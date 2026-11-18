"""File upload helper for meeting-note attachments (lampiran).

Order of preference:
1. Vercel Blob   — when BLOB_READ_WRITE_TOKEN is set (added automatically when a Blob
                   store is connected to the Vercel project).
2. Supabase Storage — when SUPABASE_URL and SUPABASE_SERVICE_KEY are set.
3. Local UPLOAD_FOLDER (local development).
Returns the value stored in the DB (public URL or local filename).
"""
import json
import os
import time
import urllib.parse
import urllib.request
from flask import current_app


def _vercel_blob(data, object_name, content_type, token):
    req = urllib.request.Request(
        f"https://blob.vercel-storage.com/{urllib.parse.quote(object_name)}",
        data=data,
        method='PUT',
        headers={
            'authorization': f'Bearer {token}',
            'x-api-version': '7',
            'x-content-type': content_type,
            'x-add-random-suffix': '1',
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())['url']


def _supabase(data, object_name, content_type, url, key, bucket):
    quoted = urllib.parse.quote(object_name)
    req = urllib.request.Request(
        f"{url}/storage/v1/object/{bucket}/{quoted}",
        data=data,
        method='POST',
        headers={'Authorization': f'Bearer {key}', 'apikey': key,
                 'Content-Type': content_type, 'x-upsert': 'true'},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()
    return f"{url}/storage/v1/object/public/{bucket}/{quoted}"


def save_upload(file_storage, filename):
    cfg = current_app.config
    content_type = file_storage.mimetype or 'application/octet-stream'
    object_name = f"lampiran/{int(time.time())}_{filename}"

    blob_token = os.getenv('BLOB_READ_WRITE_TOKEN')
    if blob_token:
        return _vercel_blob(file_storage.read(), object_name, content_type, blob_token)

    if cfg.get('SUPABASE_URL') and cfg.get('SUPABASE_SERVICE_KEY'):
        return _supabase(file_storage.read(), object_name, content_type,
                         cfg['SUPABASE_URL'], cfg['SUPABASE_SERVICE_KEY'], cfg['SUPABASE_BUCKET'])

    os.makedirs(cfg['UPLOAD_FOLDER'], exist_ok=True)
    file_storage.save(os.path.join(cfg['UPLOAD_FOLDER'], filename))
    return filename
