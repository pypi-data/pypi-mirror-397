# 🚀 Tempspace

Tempspace is a self-hostable, terminal-themed file sharing service. It allows you to quickly upload files and share them via a link, with features like password protection, one-time downloads, and automatic expiration.



## ✨ Core Features

-   **Seamless Uploading:** Drag-and-drop web interface, cURL, or a dedicated CLI tool.
-   **Chunked Uploads:** Robust support for large files (default 4GB, configurable) via chunking.
-   **Security Focused:**
    -   **Password Protection:** Secure individual files with a password.
    -   **One-Time Downloads:** Links can be configured to expire after the first download.
    -   **Rate Limiting:** Built-in protection against abuse.
-   **Efficient Storage:** Files with identical content are de-duplicated to save space.
-   **Flexible Expiration:** Set custom expiration times from hours to days.
-   **Modern UI:**
    -   **Terminal-Inspired Design:** A clean, developer-focused interface.
    -   **QR Code Generation:** Instantly generate QR codes for mobile sharing.
    -   **Local Upload History:** Your browser remembers your recent uploads.
-   **Automatic Cleanup:** The server periodically cleans up expired files automatically.

## 🚀 Getting Started

There are three primary ways to use Tempspace.

### 1. Web Interface (The Easy Way)

1.  Open the service URL (e.g., `https://tempspace.fly.dev/` or your self-hosted instance) in your browser.
2.  Drag and drop your file(s) or click to browse.
3.  Configure options like expiration time, password, or one-time download.
4.  Click "Upload" and share the generated link.

### 2. cURL (From the Terminal)

Use `cURL` to upload files directly from your command line.

```bash
# Basic upload (expires in 24 hours)
curl -F "file=@/path/to/your/file.txt" https://tempspace.fly.dev/upload

# Set a custom expiration time (e.g., 7 days) and password
curl -F "file=@/path/to/secret.txt" \
     -F "hours=168" \
     -F "password=secret123" \
     https://tempspace.fly.dev/upload

# Create a one-time download link
curl -F "file=@/path/to/onetime.zip" \
     -F "one_time=true" \
     https://tempspace.fly.dev/upload
```

### 3. Official CLI Tool

For the best terminal experience, install the official CLI tool from PyPI.

#### Installation

```bash
pip install tempspace-cli
```

#### Usage

```bash
# Interactive mode (prompts for all options)
tempspace --it

# Basic upload (expires in 24 hours)
tempspace /path/to/document.pdf

# Set expiration to 7 days and add a password
tempspace /path/to/archive.zip -t 7d -p "secure_password"

# Display a QR code in the terminal after upload
tempspace /path/to/image.png --qr

# Point to a self-hosted server
tempspace /path/to/file.txt --url http://localhost:8000
```

## 🔧 Self-Hosting

You can easily run your own instance of Tempspace using Docker or by running the source code directly.

### Method 1: Using Docker (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Bartixxx32/tempspace.git
    cd tempspace
    ```

2.  **Build the Docker image:**
    ```bash
    docker build -t tempspace-app .
    ```

3.  **Run the container:**
    Create a `.env` file to configure your admin password.
    ```bash
    cp .env.example .env
    nano .env  # Set your ADMIN_PASS
    ```
    Then, run the container, mounting the environment file and a volume for persistent storage.
    ```bash
    docker run -d \
      -p 8000:8000 \
      --name tempspace \
      --env-file .env \
      -v $(pwd)/uploads:/app/uploads \
      tempspace-app
    ```
    Your Tempspace instance will be available at `http://localhost:8000`.

### Method 2: Running from Source

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Bartixxx32/tempspace.git
    cd tempspace
    ```

2.  **Install dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configure:**
    Copy the example environment file and set your admin password.
    ```bash
    cp .env.example .env
    nano .env
    ```

4.  **Run the server:**
    ```bash
    python -m uvicorn main:app --host 0.0.0.0 --port 8000
    ```

## ⚙️ Configuration (Environment Variables)

Configure your Tempspace instance by creating a `.env` file in the project root.

| Variable             | Description                                                              | Default                  |
| -------------------- | ------------------------------------------------------------------------ | ------------------------ |
| `ADMIN_USER`         | Username for accessing debug/admin endpoints.                            | `admin`                  |
| `ADMIN_PASS`         | **Required.** Password for the admin user. The app will not start without this. | `changeme123`            |
| `MAX_FILE_SIZE`      | Maximum file size in bytes.                                              | `4294967296` (4GB)       |
| `RATE_LIMIT_UPLOADS`   | Max uploads per IP per hour.                                             | `10`                     |
| `RATE_LIMIT_DOWNLOADS` | Max downloads per IP per hour.                                           | `100`                    |
| `RATE_LIMIT_WINDOW`  | The rate limit time window in seconds.                                   | `3600` (1 hour)          |

## 🛠️ API & Admin Endpoints

-   `/upload`: The primary endpoint for `curl` and simple POST request uploads.
-   `/upload/initiate`, `/upload/chunk`, `/upload/finalize`: Endpoints for the chunked upload flow used by the web UI and CLI.
-   `/health`: A public health check endpoint.
-   `/debug/stats`: (Admin-only) View detailed statistics of all stored files.
-   `/debug/wipe`: (Admin-only) **Destructive.** Deletes all files and metadata.

Access admin endpoints by providing the admin credentials via HTTP Basic Authentication.

## 🤝 Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## 📝 License

This project is licensed under the MIT License.
