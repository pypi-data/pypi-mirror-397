import os
import shutil
import uuid
import datetime
import mimetypes
from .base_storage import BaseStorage
from .ignore import load_ignore_patterns, is_ignored


class LocalStorage(BaseStorage):
    def __init__(self, folder="uploads", ignore_file=".botoeaseignore"):
        self.folder = folder
        self.ignore_file = ignore_file
        os.makedirs(folder, exist_ok=True)

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
            filename = os.path.join(date_path, os.path.basename(filename))

        dest = os.path.join(self.folder, filename)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(filepath, dest)

        return {
            "storage": "local",
            "filename": filename.replace("\\", "/"),
            "path": dest,
        }

    # -------------------------
    # Delete
    # -------------------------

    def delete(self, filename):
        path = os.path.join(self.folder, filename)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    # -------------------------
    # URL
    # -------------------------

    def generate_url(self, filename, expires=3600):
        return os.path.abspath(os.path.join(self.folder, filename))

    # -------------------------
    # List
    # -------------------------

    def list_files(self, prefix="", **kwargs):
        results = []
        for root, _, files in os.walk(self.folder):
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, self.folder).replace("\\", "/")
                if prefix and not rel.startswith(prefix):
                    continue
                results.append(rel)
        return results

    # -------------------------
    # Rsync-style sync
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

        src = local_folder if mode == "push" else self.folder
        dst = self.folder if mode == "push" else local_folder

        if not os.path.exists(src):
            raise FileNotFoundError(src)

        ignore = load_ignore_patterns(
            src,
            ignore_file=self.ignore_file,
            extra_patterns=ignore_patterns,
        )

        actions = {
            "copy": [],
            "delete": [],
        }

        # Destination metadata
        dst_meta = {}
        for root, _, files in os.walk(dst):
            for f in files:
                p = os.path.join(root, f)
                rel = os.path.relpath(p, dst).replace("\\", "/")
                stat = os.stat(p)
                dst_meta[rel] = (stat.st_size, stat.st_mtime)

        src_files = set()

        for root, _, files in os.walk(src):
            for f in files:
                src_path = os.path.join(root, f)
                rel = os.path.relpath(src_path, src).replace("\\", "/")

                if is_ignored(rel, ignore):
                    continue

                src_files.add(rel)
                stat = os.stat(src_path)

                if rel not in dst_meta or dst_meta[rel][0] != stat.st_size:
                    actions["copy"].append(rel)
                    if not dry_run:
                        dst_path = os.path.join(dst, rel)
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        shutil.copy2(src_path, dst_path)

        if delete:
            for rel in dst_meta:
                if rel not in src_files and not is_ignored(rel, ignore):
                    actions["delete"].append(rel)
                    if not dry_run:
                        os.remove(os.path.join(dst, rel))

        return actions
