import sys

import numpy as np
import pytest

from helicon.sequenceai import predictor


class _DummyInput:
    def __init__(self, shape):
        self.name = "input"
        self.shape = shape
        self.type = "tensor(float)"


class _DummySession:
    def __init__(self, path, providers=None, shape=None):
        self.path = path
        self.providers = providers
        self._shape = shape or [None, 3]

    def get_inputs(self):
        return [_DummyInput(self._shape)]

    def run(self, _, inputs):
        # Echo back the input for test visibility
        arr = np.asarray(list(inputs.values())[0])
        return [arr]


class _DummyORT:
    def __init__(self, shape):
        self._shape = shape

    def InferenceSession(self, path, providers=None):  # noqa: N802
        return _DummySession(path, providers=providers, shape=self._shape)


@pytest.fixture
def model_path(tmp_path):
    path = tmp_path / "model.onnx"
    path.write_text("dummy")
    return path


@pytest.fixture
def set_dummy_ort(monkeypatch):
    def _apply(shape):
        monkeypatch.setitem(sys.modules, "onnxruntime", _DummyORT(shape=shape))

    return _apply


def test_predict_rank2(set_dummy_ort, model_path):
    set_dummy_ort([None, 3])
    out = predictor.predict([[1, 2, 3], [4, 5, 6]], model_path=model_path)
    assert np.array_equal(out, np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float32))


def test_predict_rank3_invalid_shape(set_dummy_ort, model_path):
    set_dummy_ort([None, 5, 2])

    with pytest.raises(ValueError):
        predictor.predict([1.0, 2.0], model_path=model_path)


def test_missing_model_path(tmp_path):
    missing = tmp_path / "missing.onnx"
    with pytest.raises(FileNotFoundError):
        predictor.predict([[1, 2, 3]], model_path=missing)


def test_predictor_class_reuses_session(set_dummy_ort, model_path):
    set_dummy_ort([None, 3])
    p = predictor.Predictor(model_path=model_path, providers=["CPUExecutionProvider"])
    out1 = p.predict([[1, 2, 3]])
    out2 = p.predict([[4, 5, 6]])

    assert np.array_equal(out1, np.array([[1, 2, 3]], dtype=np.float32))
    assert np.array_equal(out2, np.array([[4, 5, 6]], dtype=np.float32))


def test_multiple_inputs_rejected(monkeypatch, model_path):
    class _DummySessionMulti:
        def __init__(self, path, providers=None):
            self.path = path
            self.providers = providers

        def get_inputs(self):
            return [_DummyInput([None, 3]), _DummyInput([None, 3])]

        def run(self, _, inputs):
            arr = np.asarray(list(inputs.values())[0])
            return [arr]

    class _DummyORTMulti:
        def InferenceSession(self, path, providers=None):  # noqa: N802
            return _DummySessionMulti(path, providers=providers)

    monkeypatch.setitem(sys.modules, "onnxruntime", _DummyORTMulti())

    with pytest.raises(ValueError):
        predictor.predict([[1, 2, 3]], model_path=model_path)


def test_multiple_outputs_rejected(monkeypatch, model_path):
    class _DummySessionMultiOut:
        def __init__(self, path, providers=None):
            self.path = path
            self.providers = providers

        def get_inputs(self):
            return [_DummyInput([None, 3])]

        def run(self, _, inputs):
            arr = np.asarray(list(inputs.values())[0])
            return [arr, arr]

    class _DummyORTMultiOut:
        def InferenceSession(self, path, providers=None):  # noqa: N802
            return _DummySessionMultiOut(path, providers=providers)

    monkeypatch.setitem(sys.modules, "onnxruntime", _DummyORTMultiOut())

    out = predictor.predict([[1, 2, 3]], model_path=model_path)
    assert np.array_equal(out, np.array([[1, 2, 3]], dtype=np.float32))
