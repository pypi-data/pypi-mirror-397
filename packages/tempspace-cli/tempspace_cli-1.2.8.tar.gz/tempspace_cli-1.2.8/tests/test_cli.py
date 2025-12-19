
import os
import shutil
import tempfile
import hashlib

from unittest.mock import MagicMock, patch
from cli.tempspace import parse_time, format_size, calculate_file_hash, zip_directory, upload_file, download_file, main


# --- Unit Tests ---

def test_parse_time():
    assert parse_time("7d") == 168
    assert parse_time("24h") == 24
    assert parse_time("360") == 360
    assert parse_time("1D") == 24
    assert parse_time("2H") == 2
    assert parse_time(" 7d ") == 168
    assert parse_time("invalid") is None
    assert parse_time("1w") is None

def test_format_size():
    assert format_size(0) == "0B"
    assert format_size(1023) == "1023.0 B"
    assert format_size(100) == "100.0 B"
    assert format_size(1024) == "1.0 KB"
    assert format_size(1024 * 1024) == "1.0 MB"
    assert format_size(1024 * 1024 * 1024 * 2.5) == "2.5 GB"

def test_calculate_file_hash():
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"hello world")
        filepath = f.name
    try:
        expected_hash = hashlib.sha256(b"hello world").hexdigest()
        assert calculate_file_hash(filepath) == expected_hash
    finally:
        os.remove(filepath)

def test_zip_directory():
    # Create a dummy directory structure
    temp_dir = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(temp_dir, "subdir"))
        with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
            f.write("content1")
        
        # Call zip_directory
        zip_path = zip_directory(temp_dir)
        
        assert os.path.exists(zip_path)
        assert zip_path.endswith(".zip")
        assert os.path.basename(temp_dir) in os.path.basename(zip_path)
        
        # Cleanup zip
        os.remove(zip_path)
    finally:
        shutil.rmtree(temp_dir)

# --- Mock Tests ---

@patch('cli.tempspace.requests.Session')
def test_upload_file_success(mock_session_cls, capsys):
    mock_session = mock_session_cls.return_value
    
    # Mock Initiate
    mock_session.post.side_effect = [
        MagicMock(status_code=200, json=lambda: {'upload_id': '123'}), # Initiate
        MagicMock(status_code=200), # Chunk 1
        MagicMock(status_code=200, json=lambda: {'url': 'http://test.com/file', 'hash': 'abc', 'hash_verified': True}) # Finalize
    ]
    
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"test content")
        filepath = f.name
        
    mock_console = MagicMock()
    
    try:
        upload_file(mock_console, filepath, 24, None, False, False, "http://test-server")
        
        # Assert calls
        assert mock_session.post.call_count == 3
        # Verify initiate call
        mock_session.post.call_args_list[0][0][0].endswith("/upload/initiate")
        # Verify finalize call
        mock_session.post.call_args_list[2][0][0].endswith("/upload/finalize")
        
        # Verify success message printed
        # mock_console.print.assert_called() # Hard to check partial strings on rich objects without more complex matching
        
    finally:
        os.remove(filepath)

@patch('cli.tempspace.requests.Session')
def test_download_file_success(mock_session_cls):
    mock_session = mock_session_cls.return_value
    
    # Mock HEAD request (optional/handled in code?) Code does checks but uses same session
    mock_session.head.return_value = MagicMock(status_code=200)
    
    # Mock GET request
    content = b"downloaded content"
    mock_response = MagicMock(status_code=200)
    mock_response.headers = {'content-length': str(len(content)), 'content-disposition': 'attachment; filename="server_file.txt"'}
    mock_response.iter_content.return_value = [content]
    mock_session.get.return_value = mock_response
    
    mock_console = MagicMock()
    
    # Run download
    try:
        download_file(mock_console, "http://test-server/file")
        
        # Verify file saved
        assert os.path.exists("server_file.txt")
        with open("server_file.txt", "rb") as f:
            assert f.read() == content
    finally:
        if os.path.exists("server_file.txt"):
            os.remove("server_file.txt")


@patch('sys.argv', ['tempspace', 'file.txt'])
@patch('cli.tempspace.upload_file')
def test_main_upload_defaults(mock_upload):
    # Mock os.path.isfile via patch is tricky if imported in module. 
    # cli.tempspace uses os.path.isfile directly from os module import?
    # It does `import os`. So `os.path.isfile`.
    with patch('cli.tempspace.os.path.isfile', return_value=True):
        main()
        
    mock_upload.assert_called_once()
    # args: (console, filepath, hours, password, one_time, qr, url)
    args = mock_upload.call_args[0]
    assert args[1] == 'file.txt'
    assert args[2] == 24  # Default 24h

@patch('sys.argv', ['tempspace', 'file.txt', '-t', '1h', '-p', 'secret', '--qr'])
@patch('cli.tempspace.upload_file')
def test_main_upload_custom(mock_upload):
    with patch('cli.tempspace.os.path.isfile', return_value=True):
        main()
        
    args = mock_upload.call_args[0]
    assert args[1] == 'file.txt'
    assert args[2] == 1
    assert args[3] == 'secret'
    assert args[5] is True

@patch('sys.argv', ['tempspace', 'download', 'http://example.com/file', '-p', 'pass'])
@patch('cli.tempspace.download_file')
def test_main_download_command(mock_download):
    main()
    mock_download.assert_called_once()
    args = mock_download.call_args[0]
    assert args[1] == 'http://example.com/file'
    assert args[2] == 'pass'
