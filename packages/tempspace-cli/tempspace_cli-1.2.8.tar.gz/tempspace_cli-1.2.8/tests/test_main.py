import pytest
from fastapi.testclient import TestClient
from main import (
    app, UPLOAD_DIR, RateLimiter, RATE_LIMIT_UPLOADS, RATE_LIMIT_DOWNLOADS, 
    RATE_LIMIT_WINDOW, cleanup_expired_files, shutdown_event, 
    is_video, is_text, format_bytes
)
import os
import shutil
import asyncio
import hashlib
from datetime import datetime, timedelta, timezone

# Create a client for testing
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limiters(monkeypatch):
    """Fixture to reset rate limiters before each test to prevent test interference."""
    monkeypatch.setattr("main.upload_limiter", RateLimiter(RATE_LIMIT_UPLOADS, RATE_LIMIT_WINDOW))
    monkeypatch.setattr("main.download_limiter", RateLimiter(RATE_LIMIT_DOWNLOADS, RATE_LIMIT_WINDOW))


@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    """Fixture to set up a clean upload directory for tests and tear it down afterward."""
    # Ensure a clean state before tests run
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    UPLOAD_DIR.mkdir()

    # Yield control to the tests
    yield

    # Teardown: clean up the uploads directory after all tests in the module are done
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)

def test_upload_file():
    """Test basic file upload."""
    response = client.post(
        "/upload",
        files={"file": ("test_file.txt", b"hello world", "text/plain")},
        data={"hours": "1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["filename"] == "test_file.txt"
    assert "url" in data
    assert "file_id" in data

def test_upload_file_with_spaces_in_name():
    """Test that filenames with spaces are correctly URL-encoded."""
    response = client.post(
        "/upload",
        files={"file": ("test file with spaces.txt", b"hello spaces", "text/plain")},
        data={"hours": "1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    # The returned filename field should be the original, raw filename
    assert data["filename"] == "test file with spaces.txt"
    # The URL should contain the URL-encoded version of the filename
    assert "test%20file%20with%20spaces.txt" in data["url"]

def test_upload_with_password():
    """Test file upload with a password."""
    response = client.post(
        "/upload",
        files={"file": ("test_password.txt", b"secret content", "text/plain")},
        data={"hours": "1", "password": "testpassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["password_protected"] is True

def test_download_file_no_password():
    """Test downloading a file that doesn't require a password."""
    # First, upload a file
    upload_response = client.post(
        "/upload",
        files={"file": ("download_test.txt", b"download content", "text/plain")},
        data={"hours": "1"},
    )
    upload_data = upload_response.json()
    file_url = upload_data["url"]

    # Now, try to download it
    # The URL contains the full host, so we need to extract the path
    path = file_url.split("/", 3)[-1]
    download_response = client.get(path)

    assert download_response.status_code == 200
    assert download_response.content == b"download content"

def test_download_file_with_correct_password():
    """Test downloading a password-protected file with the correct password."""
    upload_response = client.post(
        "/upload",
        files={"file": ("protected_download.txt", b"protected", "text/plain")},
        data={"hours": "1", "password": "supersecret"},
    )
    upload_data = upload_response.json()
    path = upload_data["url"].split("/", 3)[-1]

    download_response = client.get(f"{path}?password=supersecret")
    assert download_response.status_code == 200
    assert download_response.content == b"protected"

def test_download_file_with_incorrect_password():
    """Test downloading a password-protected file with an incorrect password."""
    upload_response = client.post(
        "/upload",
        files={"file": ("protected_fail.txt", b"protected fail", "text/plain")},
        data={"hours": "1", "password": "supersecret"},
    )
    upload_data = upload_response.json()
    path = upload_data["url"].split("/", 3)[-1]

    download_response = client.get(f"{path}?password=wrongpassword")
    assert download_response.status_code == 403 # Forbidden

def test_one_time_download():
    """Test that a one-time download file is deleted after being accessed."""
    upload_response = client.post(
        "/upload",
        files={"file": ("one_time.txt", b"one time content", "text/plain")},
        data={"hours": "1", "one_time": "true"},
    )
    upload_data = upload_response.json()
    path = upload_data["url"].split("/", 3)[-1]

    # First download should succeed
    first_download_response = client.get(path)
    assert first_download_response.status_code == 200

    # Let the async deletion task run
    async def wait_for_deletion():
        await asyncio.sleep(0.1)

    asyncio.run(wait_for_deletion())

    # Second download should fail
    second_download_response = client.get(path)
    assert second_download_response.status_code == 404 # Not Found

def test_delete_file():
    """Test deleting a file using the client_id."""
    # Upload a file with a specific client_id
    client_id = "test-client-123"
    upload_response = client.post(
        "/upload",
        files={"file": ("to_be_deleted.txt", b"delete me", "text/plain")},
        data={"hours": "1", "client_id": client_id},
    )
    upload_data = upload_response.json()
    file_id = upload_data["file_id"]

    # Now, delete the file with the correct client_id
    delete_response = client.request(
        "DELETE",
        f"/delete/{file_id}",
        json={"client_id": client_id},
    )
    assert delete_response.status_code == 200
    assert delete_response.json()["success"] is True

    # Verify the file is gone
    path = upload_data["url"].split("/", 3)[-1]
    get_response = client.get(path)
    assert get_response.status_code == 404

def test_delete_file_unauthorized():
    """Test that deleting a file with the wrong client_id fails."""
    # Upload a file with a specific client_id
    owner_client_id = "owner-client"
    upload_response = client.post(
        "/upload",
        files={"file": ("unauthorized_delete.txt", b"don't delete me", "text/plain")},
        data={"hours": "1", "client_id": owner_client_id},
    )
    upload_data = upload_response.json()
    file_id = upload_data["file_id"]

    # Attempt to delete with a different client_id
    attacker_client_id = "attacker-client"
    delete_response = client.request(
        "DELETE",
        f"/delete/{file_id}",
        json={"client_id": attacker_client_id},
    )
    assert delete_response.status_code == 403 # Forbidden

def test_duplicate_file_upload():
    """Test that uploading a file with the same content hash returns the original file's URL."""
    # First upload
    response1 = client.post(
        "/upload",
        files={"file": ("duplicate_content.txt", b"this content is the same", "text/plain")},
        data={"hours": "1"},
    )
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["success"] is True

    # Second upload with the same content
    response2 = client.post(
        "/upload",
        files={"file": ("another_name.txt", b"this content is the same", "text/plain")},
        data={"hours": "1"},
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["success"] is True

    # Check that the file_id is the same for both uploads
    assert data1["file_id"] == data2["file_id"]



def calculate_hash(content: bytes) -> str:
    """Helper function to calculate SHA256 hash."""
    return hashlib.sha256(content).hexdigest()

def test_upload_with_matching_hash():
    """Test that a file upload with a matching client_hash is successful."""
    file_content = b"content for hash test"
    client_hash = calculate_hash(file_content)

    response = client.post(
        "/upload",
        files={"file": ("hash_match.txt", file_content, "text/plain")},
        data={"hours": "1", "client_hash": client_hash},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["hash_verified"] is True

def test_upload_with_mismatching_hash():
    """Test that a file upload with a mismatching client_hash is rejected."""
    file_content = b"content for hash mismatch test"
    # Provide a deliberately incorrect hash
    incorrect_hash = "thisisnotthecorrecthash" * 2

    response = client.post(
        "/upload",
        files={"file": ("hash_mismatch.txt", file_content, "text/plain")},
        data={"hours": "1", "client_hash": incorrect_hash},
    )
    assert response.status_code == 400  # Bad Request
    data = response.json()
    assert "Hash verification failed" in data["detail"]

def test_upload_rate_limiting():
    """Test that the upload rate limit is enforced."""
    # The default rate limit is 10 uploads per hour. We'll exceed this.
    for i in range(10):
        response = client.post(
            "/upload",
            files={"file": (f"rate_limit_test_{i}.txt", b"rate limit content", "text/plain")},
            data={"hours": "1"},
        )
        assert response.status_code == 200

    # The 11th request should be rate-limited
    response = client.post(
        "/upload",
        files={"file": ("rate_limit_exceeded.txt", b"this should fail", "text/plain")},
        data={"hours": "1"},
    )
    assert response.status_code == 429

def test_download_rate_limiting():
    """Test that the download rate limit is enforced."""
    # First, upload a file to download
    upload_response = client.post(
        "/upload",
        files={"file": ("download_rate_limit.txt", b"download me", "text/plain")},
        data={"hours": "1"},
    )
    upload_data = upload_response.json()
    path = upload_data["url"].split("/", 3)[-1]

    # The default download limit is 100 per hour.
    # We will hit the endpoint 100 times, expecting success.
    for _ in range(100):
        download_response = client.get(path)
        assert download_response.status_code == 200

    # The 101st request should be rate-limited
    final_download_response = client.get(path)
    assert final_download_response.status_code == 429

def test_debug_stats_unauthorized():
    """Test that the /debug/stats endpoint requires authentication."""
    response = client.get("/debug/stats")
    assert response.status_code == 401  # Unauthorized

def test_debug_stats_authorized():
    """Test that the /debug/stats endpoint returns data with correct authentication."""
    # First, upload a file to have some stats to check
    client.post(
        "/upload",
        files={"file": ("stats_test_file.txt", b"some data", "text/plain")},
        data={"hours": "1"},
    )

    response = client.get("/debug/stats", auth=("admin", "changeme123"))
    assert response.status_code == 200
    # Check for some expected keys in the HTML response content
    assert "Total Files" in response.text
    assert "Total Size" in response.text
    assert "stats_test_file.txt" in response.text

def test_debug_wipe_unauthorized():
    """Test that the /debug/wipe endpoint requires authentication."""
    response = client.post("/debug/wipe")
    assert response.status_code == 401  # Unauthorized

def test_debug_wipe_authorized():
    """Test that the /debug/wipe endpoint successfully deletes all data."""
    # First, upload a file to ensure there is data to wipe
    upload_response = client.post(
        "/upload",
        files={"file": ("wipe_test_file.txt", b"wipe me", "text/plain")},
        data={"hours": "1"},
    )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    path = upload_data["url"].split("/", 3)[-1]

    # Now, wipe the data
    wipe_response = client.post("/debug/wipe", auth=("admin", "changeme123"))
    assert wipe_response.status_code == 200
    wipe_data = wipe_response.json()
    assert wipe_data["success"] is True
    assert wipe_data["wiped_files"] > 0

    # Verify that the previously uploaded file is gone
    get_response = client.get(path)
    assert get_response.status_code == 404

# Import necessary modules for the expiration test

@pytest.mark.asyncio
async def test_file_expiration_and_cleanup(monkeypatch):
    """Test that an expired file is automatically cleaned up by the background task."""
    # Prevent the main app's cleanup task from running automatically
    async def do_nothing():
        pass
    monkeypatch.setattr("main.cleanup_expired_files", do_nothing)

    # Set a very short cleanup interval so we can trigger it manually
    monkeypatch.setattr("main.CLEANUP_INTERVAL", 0.01)

    # Upload a file with a 1-hour expiry
    upload_response = client.post(
        "/upload",
        files={"file": ("cleanup_test.txt", b"I will be cleaned up", "text/plain")},
        data={"hours": "1"},
    )
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    path = upload_data["url"].split("/", 3)[-1]
    file_id = upload_data["file_id"]

    # At this point, the file should exist in the metadata
    from main import metadata
    assert file_id in metadata

    # A mock datetime class that is always 2 hours in the future
    class MockDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime.now(timezone.utc) + timedelta(hours=2)

    # Now, patch the datetime object to simulate time passing
    monkeypatch.setattr('main.datetime', MockDateTime)

    # Manually run the cleanup task once
    # Reset the shutdown event to allow the task to run
    shutdown_event.clear()
    cleanup_task = asyncio.create_task(cleanup_expired_files())
    await asyncio.sleep(0.02) # Give it a moment to run
    shutdown_event.set() # Stop the task
    await cleanup_task # Wait for it to finish gracefully

    # After cleanup, the file should be gone from metadata and disk
    assert file_id not in metadata
    download_response = client.get(path)
    assert download_response.status_code == 404

def test_upload_with_invalid_expiry():
    """Test that uploading with an invalid expiry time fails."""
    response = client.post(
        "/upload",
        files={"file": ("invalid_expiry.txt", b"some content", "text/plain")},
        data={"hours": "999"},  # 999 is not a valid expiry option
    )
    assert response.status_code == 400
    assert "Invalid expiry time" in response.json()["detail"]

def test_upload_exceeding_max_size(monkeypatch):
    """Test that uploading a file larger than MAX_FILE_SIZE fails."""
    # Set a very small max file size for the test
    monkeypatch.setattr("main.MAX_FILE_SIZE", 10) # 10 bytes

    # Attempt to upload a file larger than the new max size
    file_content = b"this file is definitely larger than ten bytes"
    response = client.post(
        "/upload",
        files={"file": ("too_large.txt", file_content, "text/plain")},
        data={"hours": "1"},
    )
    assert response.status_code == 413 # Payload Too Large
    assert "File too large" in response.json()["detail"]

@pytest.mark.asyncio
async def test_rate_limiter_timezone_aware_expiration(monkeypatch):
    """
    Test that the RateLimiter correctly expires entries after its time window,
    using timezone-aware datetime objects to prevent DST or timezone issues.
    """


    # Use a local limiter instance for this test
    limiter = RateLimiter(max_requests=1, window_seconds=10)

    # 1. First request should be allowed. It will be timestamped with datetime.now(timezone.utc).
    allowed, _ = await limiter.check_rate_limit("test-ip-tz")
    assert allowed is True

    # 2. Immediately after, the second request should be blocked.
    allowed, _ = await limiter.check_rate_limit("test-ip-tz")
    assert allowed is False

    # 3. Simulate time passing by 11 seconds by mocking datetime.now.
    #    The mock returns a timezone-aware datetime in the future.
    future_time = datetime.now(timezone.utc) + timedelta(seconds=11)

    class MockDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            # This mock will be used by the RateLimiter on the next call.
            # It's crucial that it returns a timezone-aware object to match the fixed code.
            return future_time

    monkeypatch.setattr('main.datetime', MockDateTime)

    # 4. The third request should now be allowed, as the original request is outside the window.
    allowed, _ = await limiter.check_rate_limit("test-ip-tz")
    assert allowed is True, "Rate limiter should allow the request after the time window has passed."


def test_chunked_upload_workflow_success():
    """Test the full chunked upload workflow from initiation to finalization."""
    # 1. Initiate upload
    initiate_response = client.post("/upload/initiate")
    assert initiate_response.status_code == 200
    upload_id = initiate_response.json()["upload_id"]
    assert upload_id is not None

    # 2. Upload chunks
    file_content = b"this is the content of a chunked upload file"
    chunk1 = file_content[:20]
    chunk2 = file_content[20:]

    client.post(
        "/upload/chunk",
        data={"upload_id": upload_id, "chunk_number": "1"},
        files={"file": ("chunk1", chunk1)},
    )
    client.post(
        "/upload/chunk",
        data={"upload_id": upload_id, "chunk_number": "2"},
        files={"file": ("chunk2", chunk2)},
    )

    # 3. Finalize upload
    finalize_response = client.post(
        "/upload/finalize",
        data={
            "upload_id": upload_id,
            "filename": "chunked_file.txt",
            "hours": "1",
        },
    )
    assert finalize_response.status_code == 200
    response_json = finalize_response.json()
    assert response_json["success"] is True
    assert "chunked_file.txt" in response_json["url"]
    assert response_json["hash"] is not None

    # 4. Verify file can be downloaded
    # The URL from the response is absolute, so we parse the path
    from urllib.parse import urlparse
    download_path = urlparse(response_json["url"]).path
    download_response = client.get(download_path)
    assert download_response.status_code == 200
    assert download_response.content == file_content


def test_chunked_upload_invalid_session():
    """Test chunk upload and finalization with an invalid or non-existent upload_id."""
    # Attempt to upload a chunk with a fake upload_id
    response_chunk = client.post(
        "/upload/chunk",
        data={"upload_id": "fake-id", "chunk_number": "1"},
        files={"file": ("chunk", b"data")},
    )
    assert response_chunk.status_code == 404

    # Attempt to finalize with a fake upload_id
    response_finalize = client.post(
        "/upload/finalize",
        data={"upload_id": "fake-id", "filename": "test.txt", "hours": "1"},
    )
    assert response_finalize.status_code == 404


def test_chunked_upload_hash_mismatch():
    """Test that finalization fails if the client-side hash does not match the server-side hash."""
    # 1. Initiate
    initiate_response = client.post("/upload/initiate")
    upload_id = initiate_response.json()["upload_id"]

    # 2. Upload chunk
    client.post(
        "/upload/chunk",
        data={"upload_id": upload_id, "chunk_number": "1"},
        files={"file": ("chunk", b"some content")},
    )

    # 3. Finalize with a deliberately incorrect hash
    finalize_response = client.post(
        "/upload/finalize",
        data={
            "upload_id": upload_id,
            "filename": "hash_mismatch_chunked.txt",
            "hours": "1",
            "client_hash": "thisisobviouslywrong",
        },
    )
    assert finalize_response.status_code == 400
    assert "Hash verification failed" in finalize_response.json()["detail"]


def test_download_with_mismatched_filename():
    """Test that a 404 is returned if the filename in the URL doesn't match the record."""
    upload_response = client.post(
        "/upload",
        files={"file": ("correct_name.txt", b"content", "text/plain")},
        data={"hours": "1"},
    )
    upload_data = upload_response.json()
    file_id = upload_data["file_id"]

    # Attempt to download with the correct file_id but the wrong filename
    download_response = client.get(f"/{file_id}/wrong_name.txt")
    assert download_response.status_code == 404


def test_download_preview_image():
    """Test that the preview parameter sets Content-Disposition to inline for images."""
    upload_response = client.post(
        "/upload",
        files={"file": ("image.jpg", b"jpeg_content", "image/jpeg")},
        data={"hours": "1"},
    )
    path = upload_response.json()["url"].split("/", 3)[-1]

    # Download with the preview flag
    preview_response = client.get(f"{path}?preview=1")
    assert preview_response.status_code == 200
    assert "inline" in preview_response.headers["content-disposition"]


def test_download_head_request():
    """Test that a HEAD request returns the correct headers and no body."""
    upload_response = client.post(
        "/upload",
        files={"file": ("head_test.txt", b"some content for head", "text/plain")},
        data={"hours": "1"},
    )
    path = upload_response.json()["url"].split("/", 3)[-1]

    head_response = client.head(path)
    assert head_response.status_code == 200
    assert head_response.content == b""
    assert "content-length" in head_response.headers
    assert head_response.headers["content-length"] == str(len(b"some content for head"))


def test_download_password_required():
    """Test that a 401 is returned if a password is required but not provided."""
    upload_response = client.post(
        "/upload",
        files={"file": ("password_required.txt", b"secret", "text/plain")},
        data={"hours": "1", "password": "a-secret"},
    )
    path = upload_response.json()["url"].split("/", 3)[-1]

    # Attempt to download without a password
    download_response = client.get(path)
    assert download_response.status_code == 401


def test_health_endpoint():
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "total_files" in data


def test_rate_limit_endpoint():
    """Test the /api/rate-limit endpoint."""
    response = client.get("/api/rate-limit")
    assert response.status_code == 200
    data = response.json()
    assert "remaining" in data
    assert "max" in data


def test_max_file_size_endpoint():
    """Test the /api/max-file-size endpoint."""
    response = client.get("/api/max-file-size")
    assert response.status_code == 200
    data = response.json()
    assert "max_size_bytes" in data
    assert "max_size_formatted" in data
    # Check against the default value
    assert data["max_size_bytes"] == 4 * 1024 * 1024 * 1024
    assert data["max_size_formatted"] == "4.00 GB"


def test_get_scheme_and_host_forwarded():
    """Test that get_scheme_and_host correctly uses X-Forwarded-Proto."""
    # Simulate a request with X-Forwarded-Proto header
    response = client.post(
        "/upload",
        files={"file": ("test_scheme.txt", b"content", "text/plain")},
        data={"hours": "1"},
        headers={"X-Forwarded-Proto": "https"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["url"].startswith("https://")




def test_format_bytes():
    """Test the format_bytes helper function."""
    assert format_bytes(1023) == "1023 bytes"
    assert format_bytes(1024) == "1.00 KB"
    assert format_bytes(1536) == "1.50 KB"
    assert format_bytes(1024 * 1024) == "1.00 MB"
    assert format_bytes(1.5 * 1024 * 1024) == "1.50 MB"
    assert format_bytes(1024 * 1024 * 1024) == "1.00 GB"
    assert format_bytes(2.5 * 1024 * 1024 * 1024) == "2.50 GB"

def test_is_video():
    """Test the is_video helper function."""
    assert is_video("test.mp4") is True
    assert is_video("test.webm") is True
    assert is_video("test.txt") is False
    assert is_video("test.mov") is False


def test_is_text():
    """Test the is_text helper function."""
    assert is_text("test.txt") is True
    assert is_text("test.py") is True
    assert is_text("test.json") is True
    assert is_text("test.mp4") is False
    assert is_text("test.jpg") is False


def test_delete_file_invalid_json():
    """Test that the delete endpoint handles invalid JSON gracefully."""
    # Upload a file to get a valid file_id
    upload_response = client.post(
        "/upload",
        files={"file": ("to_delete.txt", b"content", "text/plain")},
        data={"hours": "1", "client_id": "some-client"},
    )
    file_id = upload_response.json()["file_id"]

    # Send a request with a malformed JSON body
    response = client.request(
        "DELETE",
        f"/delete/{file_id}",
        content="this is not json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400


def test_delete_file_missing_client_id():
    """Test that the delete endpoint requires a client_id."""
    # Upload a file
    upload_response = client.post(
        "/upload",
        files={"file": ("to_delete.txt", b"content", "text/plain")},
        data={"hours": "1", "client_id": "some-client"},
    )
    file_id = upload_response.json()["file_id"]

    # Send a request with a valid JSON body but no client_id
    response = client.request(
        "DELETE",
        f"/delete/{file_id}",
        json={"some_other_key": "some_value"},
    )
    assert response.status_code == 400


def test_upload_zip_file():
    """Test uploading a zip file to verify MIME type detection and handling."""
    # Create a dummy zip content (header for a zip file)
    zip_header = b"PK\x03\x04"
    response = client.post(
        "/upload",
        files={"file": ("archive.zip", zip_header + b"some content", "application/zip")},
        data={"hours": "1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["filename"] == "archive.zip"
    # Depending on filetype library, it might guess zip or octet-stream for this partial content.
    # The server logic uses filetype.guess.
    assert "url" in data
    
def test_download_content_disposition():
    """Test that the server sends the correct Content-Disposition header."""
    filename = "disposition_test.txt"
    # Use unique content to avoid deduplication returning an old filename
    content = b"unique content for disposition test " + os.urandom(8)
    upload_response = client.post(
        "/upload",
        files={"file": (filename, content, "text/plain")},
        data={"hours": "1"},
    )
    path = upload_response.json()["url"].split("/", 3)[-1]
    
    response = client.get(path)
    assert response.status_code == 200
    assert "content-disposition" in response.headers
    # Starlette/FastAPI FileResponse might use filename*=UTF-8''... for safety
    cd = response.headers["content-disposition"]
    assert filename in cd
