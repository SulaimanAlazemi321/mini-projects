# Lightweight helpers to derive ML-friendly features, no PII stored.

import time, json, re, hashlib
from typing import Dict, Any, Tuple, List

SPECIAL_CHARS = rb"[<>'\"\\%;(){}]"

def payload_features(body: bytes, content_type: str) -> Dict[str, Any]:
    length = len(body)
    ratio  = round(len(re.findall(SPECIAL_CHARS, body)) / max(length, 1), 3)
    hsh    = hashlib.sha256(body).hexdigest() if length else ""
    sample = body[:256].decode("utf-8", "ignore")

    json_keys: List[str] = []
    if content_type.startswith("application/json"):
        try:
            parsed = json.loads(body)
            if isinstance(parsed, dict):
                json_keys = list(parsed.keys())[:10]
        except Exception:
            pass

    return {
        "body_len": length,
        "special_char_ratio": ratio,
        "body_sha256": hsh,
        "body_sample": sample,
        "json_keys": json_keys,
    }

def temporal_features(epoch: float) -> Dict[str, int]:
    lt = time.localtime(epoch)
    return {
        "hour_of_day": lt.tm_hour,
        "day_of_week": lt.tm_wday,          # 0=Mon
        "is_weekend": int(lt.tm_wday in (5, 6)),
        "is_business_hours": int(9 <= lt.tm_hour <= 17),
    }

def path_features(path: str, query: str) -> Dict[str, int]:
    return {
        "path_depth": len([p for p in path.strip("/").split("/") if p]),
        "query_length": len(query),
        "query_param_count": len(query.split("&")) if query else 0,
        "has_file_ext": int("." in path.split("/")[-1]),
    }
