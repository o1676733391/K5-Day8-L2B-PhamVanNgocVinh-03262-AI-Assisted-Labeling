"""Tự động tạo Project và Tasks trên CVAT thông qua CVAT SDK.
Chạy: python scripts/setup_cvat_tasks.py
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from cvat_sdk import Client

ROOT = Path(__file__).resolve().parent.parent
CVAT_URL = "http://localhost:8080"
PROJECT_NAME = "day08-03262"


def get_auth_key():
    val = os.environ.get("CVAT_TOKEN", "")
    if val:
        return val
    try:
        r = subprocess.run(
            ["docker", "exec", "cvat_server", "python3", "-c",
             "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cvat.settings.production'); "
             "django.setup(); from rest_framework.authtoken.models import Token; print(Token.objects.first().key)"],
            capture_output=True, text=True, check=True
        )
        return r.stdout.strip()
    except Exception:
        return ""


def main():
    auth_key = get_auth_key()
    print(f"[*] Kết nối tới CVAT tại {CVAT_URL}...")
    client = Client(url=CVAT_URL)
    if auth_key:
        client.api_client.default_headers["Authorization"] = f"Token {auth_key}"

    # 1. Tìm hoặc tạo Project
    existing_projects = {p.name: p for p in client.projects.list()}
    if PROJECT_NAME in existing_projects:
        project = existing_projects[PROJECT_NAME]
        print(f"[+] Project '{PROJECT_NAME}' đã tồn tại (ID: {project.id})")
    else:
        labels_path = ROOT / "cvat" / "labels_generated.json"
        if not labels_path.exists():
            print(f"[!] Không tìm thấy {labels_path}. Hãy chạy python scripts/make_cvat_labels.py trước.")
            sys.exit(1)
        labels = json.loads(labels_path.read_text(encoding="utf-8"))
        print(f"[*] Đang tạo Project '{PROJECT_NAME}' với {len(labels)} nhãn...")
        project = client.projects.create({
            "name": PROJECT_NAME,
            "labels": labels
        })
        print(f"[+] Đã tạo Project '{PROJECT_NAME}' thành công (ID: {project.id})")

    # 2. Tạo Task gold-manual
    existing_tasks = {t.name: t for t in client.tasks.list()}
    gold_dir = ROOT / "work" / "tasks" / "gold"
    gold_images = sorted(list(gold_dir.glob("*.jpg")))
    if not gold_images:
        print(f"[!] Thư mục {gold_dir} trống! Hãy chạy python scripts/prepare_workdirs.py trước.")
        sys.exit(1)

    if "gold-manual" in existing_tasks:
        gold_task = existing_tasks["gold-manual"]
        print(f"[+] Task 'gold-manual' đã tồn tại (ID: {gold_task.id}) -> {CVAT_URL}/tasks/{gold_task.id}")
    else:
        print(f"[*] Đang tạo Task 'gold-manual' ({len(gold_images)} ảnh)...")
        gold_task = client.tasks.create_from_data(
            spec={"name": "gold-manual", "project_id": project.id},
            resources=gold_images,
            data_params={"image_quality": 95}
        )
        print(f"[+] Đã tạo Task 'gold-manual' thành công (ID: {gold_task.id}) -> {CVAT_URL}/tasks/{gold_task.id}")

    # 3. Tạo Task batch-review
    review_dir = ROOT / "work" / "tasks" / "review"
    review_images = sorted(list(review_dir.glob("*.jpg")))
    if not review_images:
        print(f"[!] Thư mục {review_dir} trống! Hãy chạy python scripts/prepare_workdirs.py trước.")
        sys.exit(1)

    if "batch-review" in existing_tasks:
        review_task = existing_tasks["batch-review"]
        print(f"[+] Task 'batch-review' đã tồn tại (ID: {review_task.id}) -> {CVAT_URL}/tasks/{review_task.id}")
    else:
        print(f"[*] Đang tạo Task 'batch-review' ({len(review_images)} ảnh)...")
        review_task = client.tasks.create_from_data(
            spec={"name": "batch-review", "project_id": project.id},
            resources=review_images,
            data_params={"image_quality": 95}
        )
        print(f"[+] Đã tạo Task 'batch-review' thành công (ID: {review_task.id}) -> {CVAT_URL}/tasks/{review_task.id}")

    print("\n" + "=" * 60)
    print("HOÀN TẤT THIẾT LẬP TRÊN CVAT!")
    print(f"Project URL : {CVAT_URL}/projects/{project.id}")
    print(f"Gold Task   : {CVAT_URL}/tasks/{gold_task.id} (Dùng cho Part 1)")
    print(f"Review Task : {CVAT_URL}/tasks/{review_task.id} (Dùng cho Part 4)")
    print("=" * 60)


if __name__ == "__main__":
    main()
