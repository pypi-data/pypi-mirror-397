# helicon-sequenceai

A small inference-only Python package for running ONNX models exported from the internal `sequence-ai` training repository.

## What this package provides

- `helicon.sequenceai.predict(...)`: a simple function that loads an ONNX model and runs inference.
- `helicon.sequenceai.Predictor`: a reusable predictor that caches the ONNX Runtime session.

## What this package does NOT include

- The ONNX model file(s) themselves.
- Training pipelines (MLflow/Metaflow/Kedro), preprocessing/windowing, or the FastAPI UI.

You must provide the ONNX model path at runtime.

## Install

```bash
pip install helicon-sequenceai
```

GPU (Linux x86_64 only, CUDA-enabled):

```bash
pip install "helicon-sequenceai[gpu]"
```

Note: the default install uses CPU-only `onnxruntime`. To use GPU, install the `gpu` extra and pass providers when calling:

```python
preds = predict(features=X, model_path="model.onnx",
                providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
```

## Usage

```python
from helicon.sequenceai import predict

preds = predict(features=[[1.0, 2.0, 3.0]], model_path="/path/to/model.onnx")
```

## Development

### With uv (recommended)

Create a virtualenv and install with dev extras:

```bash
uv venv
uv sync --group dev
```

Run tests:

```bash
uv run pytest
```

Build locally:

```bash
uv build
```

### With pip

Install in editable mode with dev extras:

```bash
python -m pip install -e ".[dev]"
pytest
```
