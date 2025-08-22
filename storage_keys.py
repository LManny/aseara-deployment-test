from uuid import uuid4
from werkzeug.utils import secure_filename
import os

def _ext(name): 
    return (os.path.splitext(name)[1] or ".bin").lower()

def supplier_doc_key(supplier_id: int, kind: str, filename: str) -> str:
    return f"suppliers/{supplier_id}/documents/{kind}/{uuid4().hex}{_ext(filename)}"

def product_media_key(supplier_id: int, product_id: int, filename: str, variant: str = "original") -> str:
    safe_ext = _ext(filename)
    return f"suppliers/{supplier_id}/products/{product_id}/{variant}/{uuid4().hex}{safe_ext}"

# def product_thumb_key(supplier_id: int, product_id: int, source_key: str) -> str:
#     # same uuid as original if you want to match; simplest: new uuid
#     return f"suppliers/{supplier_id}/products/{product_id}/thumb/{uuid4().hex}.jpg"
