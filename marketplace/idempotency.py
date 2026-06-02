import hashlib


def get_request_id(request, fallback='request'):
    body_value = getattr(request, 'data', {}) or {}
    if isinstance(body_value, dict):
        request_id = body_value.get('request_id')
    else:
        request_id = None

    if not request_id:
        request_id = getattr(request, 'headers', {}).get('X-Idempotency-Key')

    return str(request_id or fallback).strip()


def build_reference(prefix, *parts, max_length=64):
    digest = hashlib.sha256(':'.join(str(part) for part in parts).encode('utf-8')).hexdigest().upper()
    reference = f'{prefix}_{digest[:24]}'
    return reference[:max_length]
