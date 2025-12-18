import os
import uuid
import boto3
import datetime
import mimetypes
import hashlib
from botocore.exceptions import ClientError
from .base_storage import BaseStorage
from .ignore import load_ignore_patterns, is_ignored


class S3Storage(BaseStorage):
    def __init__(self, bucket, region, access_key=None, secret_key=None, ignore_file=".botoeaseignore"):
        self.bucket = bucket
        self.region = region
        self.ignore_file = ignore_file

        self.s3 = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

    # -------------------------
    # Internal helpers
    # -------------------------

    def _md5_hex(self, filepath):
        h = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def _object_metadata(self, key):
        try:
            return self.s3.head_object(Bucket=self.bucket, Key=key)
        except ClientError:
            return None

    # -------------------------
    # Upload
    # -------------------------

    def upload(
        self,
        filepath,
        filename=None,
        use_uuid=False,
        use_date_structure=False,
        allowed_types=None,
        max_size=None,
        safe_upload=False,
    ):
        if not os.path.exists(filepath):
            raise FileNotFoundError(filepath)

        size = os.path.getsize(filepath)
        if max_size and size > max_size:
            raise ValueError(f"File exceeds {max_size} bytes")

        mime_type, _ = mimetypes.guess_type(filepath)
        if allowed_types and mime_type not in allowed_types:
            raise ValueError(f"File type {mime_type} not allowed")

        if not filename:
            filename = os.path.basename(filepath)

        if use_uuid:
            ext = os.path.splitext(filename)[1]
            filename = f"{uuid.uuid4()}{ext}"

        if use_date_structure:
            date_path = datetime.datetime.utcnow().strftime("%Y/%m/%d")
            filename = f"{date_path}/{os.path.basename(filename)}"

        extra_args = {}
        if mime_type:
            extra_args["ContentType"] = mime_type

        self.s3.upload_file(filepath, self.bucket, filename, ExtraArgs=extra_args)

        if safe_upload:
            meta = self._object_metadata(filename)
            if not meta:
                raise Exception("Upload verification failed")

            etag = meta["ETag"].strip('"')
            local_md5 = self._md5_hex(filepath)

            if "-" not in etag and etag != local_md5:
                raise Exception("MD5 checksum mismatch")

        return {
            "storage": "s3",
            "bucket": self.bucket,
            "filename": filename,
            "url": f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{filename}",
        }

    # -------------------------
    # Delete
    # -------------------------

    def delete(self, filename):
        self.s3.delete_object(Bucket=self.bucket, Key=filename)
        return True

    # -------------------------
    # Presigned URL
    # -------------------------

    def generate_url(self, filename, expires=3600, content_type=None):
        params = {"Bucket": self.bucket, "Key": filename}
        if content_type:
            params["ResponseContentType"] = content_type

        return self.s3.generate_presigned_url(
            "get_object",
            Params=params,
            ExpiresIn=expires,
        )

    # -------------------------
    # List files
    # -------------------------

    def list_files(self, prefix="", **kwargs):
        results = []
        paginator = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                results.append(obj["Key"])
        return results

    # -------------------------
    # Rsync-style sync (dry_run + ignore)
    # -------------------------

    def sync_folder(
        self,
        local_folder,
        mode="push",
        delete=False,
        dry_run=False,
        ignore_patterns=None,
    ):
        if mode not in ("push", "pull"):
            raise ValueError("mode must be 'push' or 'pull'")

        actions = {"copy": [], "delete": []}

        # ---------- PUSH (local → S3) ----------
        if mode == "push":
            if not os.path.exists(local_folder):
                raise FileNotFoundError(local_folder)

            ignore = load_ignore_patterns(
                local_folder,
                ignore_file=self.ignore_file,
                extra_patterns=ignore_patterns,
            )

            # Existing S3 objects
            s3_meta = {}
            paginator = self.s3.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self.bucket):
                for obj in page.get("Contents", []):
                    s3_meta[obj["Key"]] = obj["Size"]

            local_files = set()

            for root, _, files in os.walk(local_folder):
                for f in files:
                    local_path = os.path.join(root, f)
                    key = os.path.relpath(local_path, local_folder).replace("\\", "/")

                    if is_ignored(key, ignore):
                        continue

                    local_files.add(key)
                    size = os.path.getsize(local_path)

                    if key not in s3_meta or s3_meta[key] != size:
                        actions["copy"].append(key)
                        if not dry_run:
                            self.upload(local_path, filename=key)

            if delete:
                for key in s3_meta:
                    if key not in local_files and not is_ignored(key, ignore):
                        actions["delete"].append(key)
                        if not dry_run:
                            self.delete(key)

            return actions

        # ---------- PULL (S3 → local) ----------
        ignore = load_ignore_patterns(
            local_folder,
            ignore_file=self.ignore_file,
            extra_patterns=ignore_patterns,
        )

        s3_keys = set(self.list_files())
        local_keys = set()

        for key in s3_keys:
            if is_ignored(key, ignore):
                continue

            dest = os.path.join(local_folder, key)
            local_keys.add(key)

            if not os.path.exists(dest):
                actions["copy"].append(key)
                if not dry_run:
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    self.s3.download_file(self.bucket, key, dest)

        if delete:
            for root, _, files in os.walk(local_folder):
                for f in files:
                    path = os.path.join(root, f)
                    rel = os.path.relpath(path, local_folder).replace("\\", "/")
                    if rel not in local_keys and not is_ignored(rel, ignore):
                        actions["delete"].append(rel)
                        if not dry_run:
                            os.remove(path)

        return actions
