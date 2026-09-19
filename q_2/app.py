import os
import socket
import time

import joblib
import redis

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

REDIS_HOST = os.environ.get(
    "REDIS_HOST",
    "cache"
)

REDIS_PORT = int(
    os.environ.get("REDIS_PORT", "6379")
)

REDIS_TTL = int(
    os.environ.get("REDIS_TTL", "300")
)


app = FastAPI(title="Spam Detection API with Redis Cache")

_model = None
_redis = None


@app.on_event("startup")
def startup():
    global _model
    global _redis

    _model = joblib.load(MODEL_PATH)

    print(
        f"Loaded spam detection model "
        f"on pod={POD_NAME} node={NODE_NAME}"
    )

    _redis = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )

    _redis.ping()

    print(
        f"Connected to Redis "
        f"at {REDIS_HOST}:{REDIS_PORT}"
    )


class PredictRequest(BaseModel):
    text: str


@app.get("/healthz")
def healthz():
    if _model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
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
            detail="Model not loaded"
        )

    cache_key = f"prediction:{request.text}"

    start = time.perf_counter()

    cached_label = _redis.get(cache_key)

    if cached_label is not None:
        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        print(
            f"CACHE HIT "
            f"latency_ms={latency_ms:.4f} "
            f"text={request.text!r}"
        )

        return {
            "label": cached_label
        }

    label = str(
        _model.predict([request.text])[0]
    )

    _redis.setex(
        cache_key,
        REDIS_TTL,
        label
    )

    latency_ms = (
        time.perf_counter() - start
    ) * 1000

    print(
        f"CACHE MISS "
        f"latency_ms={latency_ms:.4f} "
        f"text={request.text!r}"
    )

    return {
        "label": label
    }