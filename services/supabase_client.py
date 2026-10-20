import os
from supabase import create_client, Client
from config import Config

_supabase_client: Client | None = None

def get_supabase_client() -> Client | None:
    """Returns a singleton instance of the Supabase Client."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    url = Config.SUPABASE_URL
    key = Config.SUPABASE_SECRET_KEY or Config.SUPABASE_PUBLISHABLE_KEY

    if not url or not key:
        return None

    try:
        _supabase_client = create_client(url, key)
        return _supabase_client
    except Exception as e:
        print(f"[Supabase] Initialization error: {e}")
        return None


def test_supabase_connection() -> dict:
    """Tests connection to Supabase and returns diagnostic status."""
    client = get_supabase_client()
    if not client:
        return {
            "status": "error",
            "message": "Supabase client could not be initialized. Check SUPABASE_URL and SUPABASE_SECRET_KEY."
        }

    try:
        # Check storage buckets or basic API accessibility
        buckets = client.storage.list_buckets()
        bucket_names = [b.name for b in buckets] if buckets else []
        return {
            "status": "connected",
            "url": Config.SUPABASE_URL,
            "storage_buckets": bucket_names
        }
    except Exception as e:
        return {
            "status": "connected_with_warning",
            "url": Config.SUPABASE_URL,
            "warning": str(e)
        }


def upload_to_supabase_storage(file_bytes: bytes, destination_path: str, bucket: str = "receipts") -> str | None:
    """
    Uploads a file to Supabase Storage bucket.
    Returns the public URL or destination path if successful, None otherwise.
    """
    client = get_supabase_client()
    if not client:
        return None

    try:
        # Ensure bucket exists or attempt upload
        client.storage.from_(bucket).upload(destination_path, file_bytes, {"upsert": "true"})
        public_url = client.storage.from_(bucket).get_public_url(destination_path)
        return public_url
    except Exception as e:
        print(f"[Supabase Storage] Upload error: {e}")
        return None
