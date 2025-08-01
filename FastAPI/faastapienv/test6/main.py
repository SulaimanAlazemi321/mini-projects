"""
main.py – FastAPI application with JSON-structured logging that is ready for
future Isolation-Forest training and rule matching.

• All requests are logged to logs/fastapi_security.log as one-line JSON.
• Payload & path metadata are stored, but no full PII.
• Numeric / categorical features are pre-computed for ML.
"""

import time
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles

# ── YOUR project modules ────────────────────────────────────────────────────
from Models.database import engine
from Models.model    import base
from Routes          import ecoUser, view    # add more routers as needed

from logging_config  import setup_logger, new_request_id
from feature_utils   import payload_features, temporal_features, path_features

# ── bootstrap ───────────────────────────────────────────────────────────────
security_logger = setup_logger()
app = FastAPI()

base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="Views"), name="static")

# ── middleware ──────────────────────────────────────────────────────────────
@app.middleware("http")
async def log_all_requests(request: Request, call_next):
    req_id = new_request_id()
    start  = time.time()

    # Read body once then re-inject so downstream endpoints can still read it
    raw_body = await request.body()
    request._receive = lambda: {
        "type": "http.request", "body": raw_body, "more_body": False
    }

    try:
        response: Response = await call_next(request)
        status = response.status_code
    except Exception:
        response = Response(status_code=500, content="Internal Server Error")
        status   = 500

    # ── feature extraction (lightweight, privacy-safe) ──────────────────────
    feats = {
        **payload_features(raw_body, request.headers.get("content-type", "")),
        **temporal_features(start),
        **path_features(request.url.path, str(request.url.query)),
        "duration_ms": int((time.time() - start) * 1000),
        "bytes_in": len(raw_body) or int(request.headers.get("content-length", 0) or 0),
        "bytes_out": int(response.headers.get("content-length", 0) or 0),
        "method_encoded": {
            "GET": 1, "POST": 2, "PUT": 3, "DELETE": 4,
            "PATCH": 5, "HEAD": 6, "OPTIONS": 7
        }.get(request.method, 0),
        "status": status,
    }

    log_entry = {
        "ts_iso":   time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(start)),
        "ts_epoch": int(start * 1000),
        "request_id": req_id,
        "method": request.method,
        "path":   request.url.path,
        "query":  str(request.url.query),
        "client_ip": request.client.host if request.client else "unknown",
        "ua": request.headers.get("user-agent", ""),
        "content_type": request.headers.get("content-type", ""),
        **feats,
    }

    # one-line JSON log (INFO, WARNING, or ERROR)
    (security_logger.error   if status >= 500 else
     security_logger.warning if status >= 400 else
     security_logger.info)(log_entry)

    return response

# ── API routes ──────────────────────────────────────────────────────────────
app.include_router(ecoUser.router)
app.include_router(view.router)

# ── health check ────────────────────────────────────────────────────────────
@app.get("/health")
async def health_check():
    return {"ok": True, "ts": time.time()}
