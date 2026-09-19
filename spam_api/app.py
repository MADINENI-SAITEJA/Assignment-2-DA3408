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


app = FastAPI(title="Spam Detection API")

_model = None


@app.on_event("startup")
def load_model():
    global _model

    _model = joblib.load(MODEL_PATH)

    print(
        f"Loaded spam detection model "
        f"on pod={POD_NAME} node={NODE_NAME}"
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

    t0 = time.time()

    label = _model.predict(
        [request.text]
    )[0]

    latency_ms = round(
        (time.time() - t0) * 1000,
        2
    )

    print(
        f"prediction={label} "
        f"latency_ms={latency_ms} "
        f"pod={POD_NAME} "
        f"node={NODE_NAME}"
    )

    # Keep the assignment-required API response exact.
    return {
        "label": str(label)
    }