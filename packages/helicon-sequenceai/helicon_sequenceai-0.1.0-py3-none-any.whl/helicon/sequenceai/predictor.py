"""Python interface for ONNX model.

This wraps ONNX Runtime with minimal shape handling so callers can pass
feature arrays (lists or numpy arrays) and get predictions.

Callers must provide the ONNX model path explicitly.
"""

from pathlib import Path

import numpy as np


def _prepare_input_array(X: np.ndarray | list[list[float]], input_shape) -> np.ndarray:
    # ruff: noqa: PLR2004 – allow ONNX shape ranks 2/3 as literal values
    """Normalize input shapes to what the ONNX model expects."""
    rank = len(input_shape)
    arr = np.asarray(X, dtype=np.float32)

    if arr.ndim == 0:
        raise ValueError(
            f"Expected at least 1D array, got scalar with shape {arr.shape}"
        )

    if rank == 2:
        if arr.ndim == 1:
            arr = arr[None, :]
        elif arr.ndim > 2:
            arr = arr.reshape(arr.shape[0], -1)
    elif rank == 3:
        if arr.ndim == 1:
            raise ValueError(
                f"Expected (time, features) or (batch, time, features), got shape {arr.shape}"
            )

        if arr.ndim == 2:
            arr = arr[None, :, :]  # add batch dimension
        elif arr.ndim != 3:
            raise ValueError(
                f"Expected (time, features) or (batch, time, features), got shape {arr.shape}"
            )
    else:
        raise ValueError(f"Unsupported input rank {rank} for shape {input_shape}")

    return arr


def predict(
    features: list[list[float]] | np.ndarray,
    *,
    model_path: str | Path,
    providers: list[str] | None = None,
) -> np.ndarray:
    """Run ONNX inference.

    Args:
        features: Nested lists/arrays representing model inputs.
        model_path: Path to the ONNX model on disk (required).
        providers: ONNX Runtime execution providers. Defaults to `["CPUExecutionProvider"]`.
            To use GPU, install `onnxruntime-gpu` and pass e.g.
            `["CUDAExecutionProvider", "CPUExecutionProvider"]`.
        Note: models with more than one input tensor are not supported (ValueError).
            If a model has multiple outputs, only the first output is returned.

    Returns:
        np.ndarray of model outputs (single-output models only).

    Raises:
        FileNotFoundError: If the model file is missing.
        ImportError: If onnxruntime is not installed.
        ValueError: If inputs cannot be reshaped for the model.
    """

    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    try:
        import onnxruntime as ort
    except ImportError as e:  # pragma: no cover - dependency issue
        raise ImportError("onnxruntime is required for inference") from e

    session = ort.InferenceSession(
        str(model_path), providers=providers or ["CPUExecutionProvider"]
    )
    inputs = session.get_inputs()
    if len(inputs) != 1:
        names = [inp.name for inp in inputs]
        raise ValueError(
            f"Expected a single input tensor, found {len(inputs)}: {names}"
        )

    input_meta = inputs[0]
    input_name = input_meta.name
    input_shape = input_meta.shape

    prepared = _prepare_input_array(features, input_shape)
    outputs = session.run(None, {input_name: prepared})

    return np.asarray(outputs[0])


class Predictor:
    """Reusable predictor that keeps a cached ONNX Runtime session.

    Defaults to CPU. To enable GPU, install `onnxruntime-gpu` and pass
    `providers=["CUDAExecutionProvider", "CPUExecutionProvider"]`.

    Note: models with more than one input tensor are not supported (ValueError).
    If a model has multiple outputs, only the first output is returned.
    """

    def __init__(
        self,
        model_path: str | Path,
        *,
        providers: list[str] | None = None,
    ):
        self.model_path = Path(model_path)
        self.providers = list(providers) if providers else ["CPUExecutionProvider"]
        self._session = None

    def _ensure_session(self):
        if self._session is None:
            try:
                import onnxruntime as ort
            except ImportError as e:
                raise ImportError("onnxruntime is required for inference") from e

            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found: {self.model_path}")
            self._session = ort.InferenceSession(
                str(self.model_path), providers=self.providers
            )

        return self._session

    def predict(self, features: list[list[float]] | np.ndarray) -> np.ndarray:
        session = self._ensure_session()
        inputs = session.get_inputs()
        if len(inputs) != 1:
            names = [inp.name for inp in inputs]
            raise ValueError(
                f"Expected a single input tensor, found {len(inputs)}: {names}"
            )

        input_meta = inputs[0]
        prepared = _prepare_input_array(features, input_meta.shape)
        outputs = session.run(None, {input_meta.name: prepared})

        return np.asarray(outputs[0])
