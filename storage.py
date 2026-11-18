"""File upload helper.

Uses Supabase Storage when SUPABASE_URL and SUPABASE_SERVICE_KEY are configured
(required on Vercel, whose filesystem is read-only / ephemeral). Otherwise saves to
the local UPLOAD_FOLDER. Returns the value stored in the DB (public URL or filename).
"""
import os
import time
import urllib.parse
import urllib.request
from flask import current_app


def save_upload(file_storage, filename):
    cfg = current_app.config
    url, key, bucket = cfg.get('SUPABASE_URL'), cfg.get('SUPABASE_SERVICE_KEY'), cfg.get('SUPABASE_BUCKET')
    if url and key:
        object_name = f"{int(time.time())}_{filename}"
        quoted = urllib.parse.quote(object_name)
        req = urllib.request.Request(
            f"{url}/storage/v1/object/{bucket}/{quoted}",
            data=file_storage.read(),
            method='POST',
            headers={
                'Authorization': f'Bearer {key}',
                'apikey': key,
                'Content-Type': file_storage.mimetype or 'application/octet-stream',
                'x-upsert': 'true',
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp.read()
        return f"{url}/storage/v1/object/public/{bucket}/{quoted}"

    os.makedirs(cfg['UPLOAD_FOLDER'], exist_ok=True)
    file_storage.save(os.path.join(cfg['UPLOAD_FOLDER'], filename))
    return filename
