import posixpath
import threading
import time
import uuid
from urllib.parse import unquote, urlparse

import httpx
from fastapi import UploadFile

from core.config import settings


ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_IMAGE_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

_SIGNED_IMAGE_URL_CACHE: dict[tuple[str, int], tuple[str, float]] = {}
_SIGNED_IMAGE_URL_CACHE_LOCK = threading.Lock()


def _supabase_error_message(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = response.text

    if isinstance(payload, dict):
        message = payload.get("message") or payload.get("error") or payload.get("msg")
        if message:
            return str(message)
        return str(payload)
    return str(payload or response.reason_phrase)


def _clean_supabase_url() -> str:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise Exception("Supabase Storage is not configured")
    url = settings.SUPABASE_URL.rstrip("/")

    # Accept either the canonical project URL
    #   https://<project-ref>.supabase.co
    # or common dashboard-copied storage endpoints such as
    #   https://<project-ref>.storage.supabase.co/storage/v1/s3
    # and normalize them to the REST Storage API host.
    if ".storage.supabase.co" in url:
        project_ref = url.split("://", 1)[-1].split(".storage.supabase.co", 1)[0]
        return f"https://{project_ref}.supabase.co"
    if "/storage/v1" in url:
        return url.split("/storage/v1", 1)[0]
    return url


def _file_extension(filename: str | None) -> str:
    if not filename or "." not in filename:
        raise Exception("Image file must have an extension")
    extension = filename.rsplit(".", 1)[-1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise Exception("Only jpg, jpeg, png, and webp images are allowed")
    return extension


async def validate_image_upload(file: UploadFile) -> tuple[bytes, str]:
    extension = _file_extension(file.filename)
    if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise Exception("Only jpg, jpeg, png, and webp images are allowed")

    content = await file.read()
    if not content:
        raise Exception("Image file is required")
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise Exception("Image file must be 5 MB or smaller")
    return content, extension


async def upload_cleaner_image(file: UploadFile, cleaner_id, document_type: str) -> str:
    content, extension = await validate_image_upload(file)
    supabase_url = _clean_supabase_url()
    bucket = settings.SUPABASE_STORAGE_BUCKET
    object_path = posixpath.join(
        "cleaners",
        str(cleaner_id),
        document_type,
        f"{uuid.uuid4()}.{extension}",
    )
    upload_url = f"{supabase_url}/storage/v1/object/{bucket}/{object_path}"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Content-Type": file.content_type or "application/octet-stream",
        "x-upsert": "false",
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(upload_url, headers=headers, content=content)

    if response.status_code not in {200, 201}:
        raise Exception(
            f"Unable to upload image to Supabase Storage: "
            f"{response.status_code} {_supabase_error_message(response)}"
        )

    return f"{supabase_url}/storage/v1/object/public/{bucket}/{object_path}"


def _object_path_from_storage_url(file_url: str) -> str | None:
    bucket = settings.SUPABASE_STORAGE_BUCKET
    parsed = urlparse(file_url)
    path = parsed.path.lstrip("/")
    public_prefix = f"storage/v1/object/public/{bucket}/"
    sign_prefix = f"storage/v1/object/sign/{bucket}/"
    short_sign_prefix = f"object/sign/{bucket}/"
    private_prefix = f"storage/v1/object/{bucket}/"

    if path.startswith(public_prefix):
        return unquote(path[len(public_prefix):])
    if path.startswith(sign_prefix):
        return unquote(path[len(sign_prefix):])
    if path.startswith(short_sign_prefix):
        return unquote(path[len(short_sign_prefix):])
    if path.startswith(private_prefix):
        return unquote(path[len(private_prefix):])
    return None


def _absolute_supabase_storage_url(supabase_url: str, signed_url: str) -> str:
    if signed_url.startswith("http"):
        return signed_url
    if signed_url.startswith("/storage/v1/"):
        return f"{supabase_url}{signed_url}"
    if signed_url.startswith("/object/"):
        return f"{supabase_url}/storage/v1{signed_url}"
    if signed_url.startswith("storage/v1/"):
        return f"{supabase_url}/{signed_url}"
    if signed_url.startswith("object/"):
        return f"{supabase_url}/storage/v1/{signed_url}"
    return f"{supabase_url}/{signed_url.lstrip('/')}"


def _get_cached_signed_image_url(file_url: str, expires_in: int) -> str | None:
    object_path = _object_path_from_storage_url(file_url)
    if not object_path:
        return None

    cache_key = (object_path, expires_in)
    current_time = time.time()

    with _SIGNED_IMAGE_URL_CACHE_LOCK:
        cached_value = _SIGNED_IMAGE_URL_CACHE.get(cache_key)
        if cached_value is not None:
            signed_url, expires_at = cached_value
            if expires_at > current_time:
                return signed_url
            _SIGNED_IMAGE_URL_CACHE.pop(cache_key, None)

    return None


def _store_signed_image_url_cache(file_url: str, signed_url: str, expires_in: int) -> None:
    object_path = _object_path_from_storage_url(file_url)
    if not object_path:
        return

    cache_key = (object_path, expires_in)
    expires_at = time.time() + max(expires_in, 1)

    with _SIGNED_IMAGE_URL_CACHE_LOCK:
        _SIGNED_IMAGE_URL_CACHE[cache_key] = (signed_url, expires_at)


def create_signed_cleaner_image_url(file_url: str | None, expires_in: int = 3600) -> str | None:
    if not file_url:
        return None

    cached_signed_url = _get_cached_signed_image_url(file_url, expires_in)
    if cached_signed_url:
        return cached_signed_url

    object_path = _object_path_from_storage_url(file_url)
    if not object_path:
        return file_url

    try:
        supabase_url = _clean_supabase_url()
    except Exception:
        return file_url

    sign_url = (
        f"{supabase_url}/storage/v1/object/sign/"
        f"{settings.SUPABASE_STORAGE_BUCKET}/{object_path}"
    )
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Content-Type": "application/json",
    }

    try:
        with httpx.Client(timeout=5) as client:
            response = client.post(
                sign_url,
                headers=headers,
                json={"expiresIn": expires_in},
            )
        if response.status_code not in {200, 201}:
            return file_url
        payload = response.json()
    except Exception:
        return file_url

    signed_url = payload.get("signedURL") or payload.get("signedUrl")
    if not signed_url:
        return file_url

    absolute_signed_url = _absolute_supabase_storage_url(supabase_url, str(signed_url))
    _store_signed_image_url_cache(file_url, absolute_signed_url, expires_in)
    return absolute_signed_url
