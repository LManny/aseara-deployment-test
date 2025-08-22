# storage_local.py
from pathlib import Path
from flask import current_app
# from PIL import Image

def key_to_local_path(key: str) -> Path:
    root = Path(current_app.instance_path) / "uploads"
    return root / key

def save_local(file_storage, key: str):
    path = key_to_local_path(key)
    path.parent.mkdir(parents=True, exist_ok=True)
    file_storage.save(path)
    return str(key)  # return the key you’ll store in DB

# def make_thumbnail_local(src_key: str, dst_key: str, size=(800, 800)):
#     src = key_to_local_path(src_key)
#     dst = key_to_local_path(dst_key)
#     dst.parent.mkdir(parents=True, exist_ok=True)
#     with Image.open(src) as im:
#         im.thumbnail(size)
#         im.convert("RGB").save(dst, "JPEG", quality=85)
