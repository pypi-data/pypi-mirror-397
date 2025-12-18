# BotoEase 🚀

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/botoease?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/botoease)

**UPDATED — v0.2.0 (Production-Ready Sync, Safety & Ignore Support)**

BotoEase is a smart, lightweight file storage library for Python that provides a **unified, predictable API** for working with **Local Storage** and **AWS S3**.

It removes the repetitive, error-prone boilerplate around `boto3` and local filesystem handling, while adding real-world features developers usually have to implement themselves.

**Designed for backend services, automation scripts, and production systems.**

---

## 🚀 What BotoEase Actually Solves

Most storage code fails in production because it:
* ❌ uploads the same files again and again
* ❌ deletes files without preview
* ❌ breaks when directories grow
* ❌ ignores `.gitignore`-style rules
* ❌ behaves differently for local vs S3

**BotoEase v0.2.0 fixes this.**

---

## 📦 Installation

```bash
pip install botoease
```

---

## 🔧 Basic Usage

```python
from botoease import Storage
```

### 🗂️ 1. Local Storage

```python
storage = Storage(backend="local", folder="uploads")
storage.upload("example.png")
```

**What happens:**
* Folder is auto-created
* File is copied safely
* No overwrites unless needed

### ☁️ 2. AWS S3 Storage

```python
storage = Storage(
    backend="s3",
    bucket="my-bucket",
    region="us-east-1",
    access_key="YOUR_KEY",      # Optional if using env vars
    secret_key="YOUR_SECRET"    # Optional if using env vars
)

storage.upload("image.jpg")
```

**Note:** IAM roles, environment variables, or explicit keys are all supported.

---

## 🛡️ 3. Advanced Uploads (v0.1.0+)

**Auto-rename + Date folders:**

```python
storage.upload(
    "report.pdf",
    use_uuid=True,              # Rename to UUID
    use_date_structure=True,    # Save to YYYY/MM/DD/
    allowed_types=["application/pdf"], 
    max_size=5 * 1024 * 1024    # Max 5MB
)
```

**Why this helps:**
* ✅ Prevents filename collisions
* ✅ Organizes uploads automatically
* ✅ Blocks invalid or oversized files early

### Safe Uploads (S3 only) - v0.2.0+

```python
storage.upload("critical.csv", safe_upload=True)
```

**What “safe” actually means:**
* Uses `boto3` multipart + retries
* Verifies object exists after upload
* Verifies MD5 checksum for single-part uploads

> This prevents silent corruption, which is common in naïve S3 code.

---

## 📋 4. Listing Files (v0.2.0+)

```python
files = storage.list_files(prefix="images/")
print(files)
```

**Example output:**
```json
[
  "images/logo.png",
  "images/banner.jpg"
]
```

---

### 🆕 What’s New in v0.2.1

This is a stabilization and usability release focused on safer sync operations.

**Highlights**
- Dry-run mode for folder sync (`dry_run=True`)
- Shared ignore rules via `.botoeaseignore`
- Fully aligned Local ↔ S3 sync behavior
- Predictable sync output (`copy` / `delete` summary)

No breaking changes. Upgrade is recommended.

---

## 🔄 5. Folder Sync (Core Feature – v0.2.0)

This is the most important feature in BotoEase.

**Key properties:**
* Rsync-style behavior
* Uploads only changed files
* Optional safe delete
* Same behavior for Local & S3

### Push: Local → Storage

```python
result = storage.sync_folder(
    "project_files",
    mode="push",
    delete=True
)
```

**Returned output:**
```json
{
  "copy": ["src/app.py", "README.md"],
  "delete": ["old/data.json"]
}
```

### Pull: Storage → Local

```python
storage.sync_folder(
    "downloads",
    mode="pull",
    delete=False
)
```

---

### 🔄 Dry-Run & Ignore Support (v0.2.1+)

Preview sync operations safely before applying changes:

```python
result = storage.sync_folder(
    "project",
    mode="push",
    delete=True,
    dry_run=True
)

print(result)

```

**Returned output:**
```json
{
  "copy": ["src/app.py", "README.md"],
  "delete": ["old/data.json"]
}
```
---

## 📈 Upcoming Features (Future Releases)

### 🟦 **v0.1.0 – Core Usability Boost** (Released)
* [x] Automatic UUID renaming
* [x] Automatic folder structure (`YYYY/MM/DD/filename`)
* [x] File type (MIME) validation
* [x] File size validation

### 🟩 **v0.2.0 – High-Demand S3 Utilities** (Released)
* [x] **Safe Uploads** (MD5 checksums)
* [x] **Local ↔ S3 Sync**
* [x] **Advanced File Listing**
* [x] **Improved Pre-signed URL Helpers**

### 🟧 **v0.3.0 – Backup, Compression & Secure Uploads**
* [ ] **Bucket Backup & Restore**
  Copy bucket → backup bucket, and restore on demand. 
* [ ] **Optional Compression** 
  (gzip / zip / brotli) before upload 
* [ ] **Client-side Encrypted Uploads** 
  AES encryption before sending the file. 

### 🟥 **v0.4.0 – Storage Backend Plugins** 
  **Introduce a clean storage backend architecture:** 
* [ ] FileSystem backend (local)
* [ ] S3 backend 
* [ ] Custom backend (user supplies save/load functions) 
* [ ] Ready for future Azure/GCP integration 

### 🟪 **v0.5.0 – Erasure Coding (Advanced Feature)**
 **For users needing redundancy, multi-cloud durability, or distributed storage.**
* [ ] Erasure Coding support (XOR or Reed–Solomon)
* [ ] Encode file → return shards 
* [ ] Optional: store shards using any backend 
* [ ] Pluggable backends (S3, local, DB, multi-cloud) 
* [ ] Metadata generation + reconstruction helpers
> This is a **unique**, specialized feature no other boto3 wrapper provides.
  
### 🟨 **v1.0.0 – Async + Performance** 
**Perfect for FastAPI and modern async Python.** 
* [ ] Fully async API (upload, delete, sync, list) 
* [ ] Background uploads 
* [ ] High-performance multipart upload engine

---

## 📜 License

MIT License.
