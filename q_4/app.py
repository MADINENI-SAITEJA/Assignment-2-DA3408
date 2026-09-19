import os
import socket
import time

import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


MODEL_PATH = os.environ.get("MODEL_PATH", "model.joblib")

POD_NAME = os.environ.get(
    "POD_NAME",
    socket.gethostname()
)

NODE_NAME = os.environ.get(
    "NODE_NAME",
    "unknown"
)

APP_VERSION = "v2"


app = FastAPI(
    title="Spam Detection API",
    version=APP_VERSION
)

_model = None


@app.on_event("startup")
def load_model():
    global _model

    _model = joblib.load(MODEL_PATH)

    print(
        f"Loaded spam detection model "
        f"version={APP_VERSION} "
        f"pod={POD_NAME} "
        f"node={NODE_NAME}"
    )


class PredictRequest(BaseModel):
    text: str


@app.get("/healthz")
def healthz():
    if _model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded yet"
        )

    return {
        "status": "ok",
        "version": APP_VERSION,
        "pod": POD_NAME,
        "node": NODE_NAME
    }


@app.post("/predict")
def predict(request: PredictRequest):
    if _model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded yet"
        )

    start = time.perf_counter()

    label = _model.predict(
        [request.text]
    )[0]

    latency_ms = (
        time.perf_counter() - start
    ) * 1000

    print(
        f"prediction={label} "
        f"latency_ms={latency_ms:.4f} "
        f"version={APP_VERSION} "
        f"pod={POD_NAME} "
        f"node={NODE_NAME}"
    )

    return {
        "label": str(label)
    }