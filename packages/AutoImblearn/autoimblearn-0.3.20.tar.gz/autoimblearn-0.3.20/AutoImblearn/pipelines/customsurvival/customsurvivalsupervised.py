import importlib.util
import logging
from pathlib import Path
from typing import Dict, Callable, Any, Optional

import numpy as np
from sklearn.base import BaseEstimator
from sksurv.util import Surv
from sksurv.metrics import (
    concordance_index_censored,
    concordance_index_ipcw,
    integrated_brier_score,
    brier_score,
    cumulative_dynamic_auc,
)

from AutoImblearn.components.survival_supv import RunSkSurvivalModel
from AutoImblearn.metrics import (
    get_metrics_for_pipeline,
    get_default_metric,
    get_metric_family,
    is_metric_supported,
)

try:
    from AutoImblearn.components.model_client.base_model_client import BaseDockerModelClient
except Exception:
    BaseDockerModelClient = None

# Docker-based survival models - factory functions
survival_models: Dict[str, Callable[..., Any]] = {
    'CPH': lambda **kw: RunSkSurvivalModel(model='CPH', **kw),
    'RSF': lambda **kw: RunSkSurvivalModel(model='RSF', **kw),
    'SVM': lambda **kw: RunSkSurvivalModel(model='SVM', **kw),
    'KSVM': lambda **kw: RunSkSurvivalModel(model='KSVM', **kw),
    'LASSO': lambda **kw: RunSkSurvivalModel(model='LASSO', **kw),
    'L1': lambda **kw: RunSkSurvivalModel(model='L1', **kw),
    'L2': lambda **kw: RunSkSurvivalModel(model='L2', **kw),
    'CSA': lambda **kw: RunSkSurvivalModel(model='CSA', **kw),
    'LRSF': lambda **kw: RunSkSurvivalModel(model='LRSF', **kw),
}
_BUILTIN_SURVIVAL_MODELS = set(survival_models.keys())


def load_custom_models():
    registry_root = Path(__file__).resolve().parents[4] / "data" / "models" / "registry"
    components_root = Path(__file__).resolve().parents[1] / "components"

    def load_registry(fname):
        path = registry_root / fname
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text())
        except Exception:
            return []

    import json

    for entry in load_registry("survival_models.json"):
        mid = entry.get("id")
        if not mid or mid in survival_models:
            continue
        target = components_root / "survival_models" / mid / "run.py"
        if not target.exists():
            target = target.parent / "__init__.py"
        if not target.exists():
            continue
        spec = importlib.util.spec_from_file_location(f"AutoImblearn.components.survival_models.{mid}", target)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore

        def factory(mod=module, mid=mid, **kw):
            if hasattr(mod, "build_model"):
                return mod.build_model(**kw)
            if hasattr(mod, "get_model"):
                return mod.get_model(**kw)
            raise RuntimeError(f"Custom survival model {mid} missing build_model/get_model")

        survival_models[mid] = factory


def reload_custom_models():
    """Reload custom survival models, clearing previous custom entries first."""
    for key in [k for k in list(survival_models.keys()) if k not in _BUILTIN_SURVIVAL_MODELS]:
        survival_models.pop(key, None)
    load_custom_models()


load_custom_models()


class CustomSurvivalModel(BaseEstimator):
    """Unified survival model wrapper built on registry `survival_models`."""

    def __init__(self,
                 method: str = "CPH",
                 registry: Optional[Dict[str, Callable[..., Any]]] = None,
                 data_folder: Optional[str] = None,
                 metric: str = "c_index",
                 **model_kwargs: Any):

        self.method = method
        self.registry = survival_models if registry is None else registry
        self.data_folder = data_folder
        self.metric = metric
        self.model_kwargs = dict(model_kwargs)

        self._survival_clf = self._build_survival_clf()
        self.result = None
        self.pipeline_type = "survival_classification"

    def fit(self,
            args,
            X_train: np.ndarray,
            y_train: np.ndarray,
            X_test: Optional[np.ndarray] = None,
            y_test: Optional[np.ndarray] = None,
            ):
        """
        Train survival model.

        Args:
            args: Arguments object with .path for data_folder
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels

        Returns:
            self
        """

        self.pipeline_type = getattr(args, "pipeline_type", "survival_classification")

        if not is_metric_supported(self.pipeline_type, self.metric):
            allowed = [m["key"] for m in get_metrics_for_pipeline(self.pipeline_type)]
            raise ValueError(f"Unsupported metric '{self.metric}' for pipeline '{self.pipeline_type}'. Allowed: {allowed}")

        if hasattr(args, 'path') and args.path:
            if hasattr(self._survival_clf, 'set_params'):
                self._survival_clf.set_params(data_folder=args.path)

        self._survival_clf.fit(args, X_train, y_train, X_test, y_test)
        # if isinstance(self._survival_clf, BaseDockerModelClient):
        #     self._survival_clf.fit(args, X_train, y_train)
        # else:
        #     self._survival_clf.fit(X_train, y_train)

        return self

    def cleanup(self):
        """Release Docker resources held by the survival model implementation."""
        impl = getattr(self, "_survival_clf", None)
        if impl and hasattr(impl, "cleanup"):
            impl.cleanup()

    def predict(self, X_test: np.ndarray):
        """Make risk predictions."""
        return self._survival_clf.predict(X_test)

    def score(self, X_test: np.ndarray, y_test: np.ndarray, y_train: Optional[np.ndarray] = None):
        """Evaluate the survival model using the specified metric."""
        metric = self.metric or get_default_metric(self.pipeline_type)

        y_test_struct = self._normalize_y(y_test)
        y_train_struct = self._normalize_y(y_train) if y_train is not None else None

        predictions = self.predict(X_test)

        if metric == "c_index":
            score = concordance_index_censored(
                y_test_struct['event'],
                y_test_struct['time'],
                predictions
            )[0]
            self.result = {'c_index': score, 'n_events': int(y_test_struct['event'].sum())}
            logging.info("\t Survival Model: %s, C-index: %.4f", self.method, score)
            return score

        if metric == "c_index_ipcw":
            if y_train_struct is None:
                raise ValueError("c_index_ipcw requires training survival data")
            score = concordance_index_ipcw(y_train_struct, y_test_struct, predictions)[0]
            self.result = {'c_index_ipcw': score, 'n_events': int(y_test_struct['event'].sum())}
            logging.info("\t Survival Model: %s, C-index IPCW: %.4f", self.method, score)
            return score

        if metric == "time_dependent_auc":
            if y_train_struct is None:
                raise ValueError("time_dependent_auc requires training survival data")
            times = self._time_grid(y_train_struct, y_test_struct)
            _, aucs = cumulative_dynamic_auc(y_train_struct, y_test_struct, predictions, times)
            score = float(np.mean(aucs))
            self.result = {
                'time_dependent_auc': score,
                'times': [float(t) for t in times],
                'aucs': [float(a) for a in aucs],
            }
            logging.info("\t Survival Model: %s, Time-dependent AUC (mean): %.4f", self.method, score)
            return score

        if metric == "integrated_brier_score":
            if y_train_struct is None:
                raise ValueError("integrated_brier_score requires training survival data")
            surv_funcs = self._predict_survival_functions(X_test)
            times = self._time_grid(y_train_struct, y_test_struct)
            ibs = integrated_brier_score(y_train_struct, y_test_struct, surv_funcs, times)
            score = float(-ibs)  # negate so higher is better
            self.result = {
                'integrated_brier_score': float(ibs),
                'score': score,
                'times': [float(t) for t in times],
            }
            logging.info("\t Survival Model: %s, Integrated Brier Score: %.4f", self.method, ibs)
            return score

        if metric == "brier_score":
            if y_train_struct is None:
                raise ValueError("brier_score requires training survival data")
            surv_funcs = self._predict_survival_functions(X_test)
            times = self._time_grid(y_train_struct, y_test_struct)
            _, brier_values = brier_score(y_train_struct, y_test_struct, surv_funcs, times)
            mean_brier = float(np.mean(brier_values))
            score = float(-mean_brier)  # negate so higher is better
            self.result = {
                'mean_brier_score': mean_brier,
                'score': score,
                'times': [float(t) for t in times],
                'brier_by_time': [float(v) for v in brier_values],
            }
            logging.info("\t Survival Model: %s, Mean Brier Score: %.4f", self.method, mean_brier)
            return score

        raise ValueError(f"Metric '{metric}' is not supported for survival analysis")

    def get_params(self, deep: bool = True):
        """Get parameters for this estimator."""
        params = {
            "method": self.method,
            "registry": self.registry,
            "data_folder": self.data_folder,
            "metric": self.metric,
            **{f"impl__{k}": v for k, v in self.model_kwargs.items()},
        }
        if deep and hasattr(self._survival_clf, "get_params"):
            for k, v in self._survival_clf.get_params(deep=True).items():
                params.setdefault(f"impl__{k}", v)
        return params

    def set_params(self, **params):
        """Set parameters for this estimator."""
        if "method" in params:
            self.method = params.pop("method")
        if "registry" in params:
            self.registry = params.pop("registry")
        if "data_folder" in params:
            self.data_folder = params.pop("data_folder")
        if "metric" in params:
            self.metric = params.pop("metric")

        impl_updates = {k[len("impl__"):]: v for k, v in list(params.items()) if k.startswith("impl__")}
        for k in list(params.keys()):
            if k.startswith("impl__"):
                params.pop(k)

        self.model_kwargs.update(params)
        self._survival_clf = self._build_survival_clf()

        if impl_updates and hasattr(self._survival_clf, "set_params"):
            self._survival_clf.set_params(**impl_updates)
        return self

    def _build_survival_clf(self):
        """Instantiate the underlying survival model from the registry."""
        if self.method not in self.registry:
            raise KeyError(
                f"Unknown survival model '{self.method}'. "
                f"Known methods: {sorted(self.registry.keys())}"
            )

        # registry values are factories (lambda **kw)
        self.model_kwargs["data_folder"] = self.data_folder
        factory = self.registry[self.method]
        impl = factory(**self.model_kwargs)

        # Set data_folder if provided and supported
        if self.data_folder is not None:
            if hasattr(impl, "set_params") and hasattr(impl, "data_folder"):
                impl.set_params(data_folder=self.data_folder)

        return impl

    def _normalize_y(self, y):
        """Normalize survival labels to sksurv structured arrays."""
        if y is None:
            return None

        if isinstance(y, np.ndarray) and getattr(y, "dtype", None) is not None and y.dtype.names:
            names = {name.lower(): name for name in y.dtype.names}
            event_field = names.get("event") or names.get("status")
            time_field = names.get("time") or names.get("survival_in_days")
            if event_field and time_field:
                return Surv.from_arrays(event=y[event_field].astype(bool), time=y[time_field].astype(float))

        if hasattr(y, "columns"):
            cols = {c.lower(): c for c in y.columns}
            event_col = cols.get("event") or cols.get("status")
            time_col = cols.get("time") or cols.get("survival_in_days")
            if event_col and time_col:
                return Surv.from_arrays(
                    event=y[event_col].astype(bool).to_numpy(),
                    time=y[time_col].astype(float).to_numpy()
                )

        arr = np.asarray(y)
        if arr.ndim == 2 and arr.shape[1] >= 2:
            return Surv.from_arrays(event=arr[:, 0].astype(bool), time=arr[:, 1].astype(float))

        raise ValueError("Survival labels must include event/status and time columns")

    def _time_grid(self, y_train, y_test):
        """Build a time grid for metrics that require it."""
        combined_times = np.concatenate([y_train["time"], y_test["time"]]) if y_train is not None else y_test["time"]
        times = np.quantile(combined_times, np.linspace(0.1, 0.9, 5))
        times = np.unique(times[times > 0])
        if times.size == 0:
            times = np.array([float(np.median(combined_times))])
        return times

    def _predict_survival_functions(self, X):
        if not hasattr(self._survival_clf, "predict_survival_function"):
            raise ValueError(f"Model '{self.method}' does not expose survival functions required for Brier-based metrics")
        return list(self._survival_clf.predict_survival_function(X))
