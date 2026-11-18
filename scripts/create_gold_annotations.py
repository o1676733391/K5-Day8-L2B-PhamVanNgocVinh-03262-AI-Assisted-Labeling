"""Tạo bộ nhãn chuẩn gold_manual.json chuẩn guideline v1.0 cho 4 ảnh gold
và đồng bộ nạp thẳng vào Task 15 trên CVAT.
"""
import json
import os
import subprocess
from pathlib import Path
from cvat_sdk import Client

ROOT = Path(__file__).resolve().parent.parent
GOLD_DIR = ROOT / "work" / "tasks" / "gold"
OUT_PATH = ROOT / "submission" / "labels" / "gold_manual.json"

CATEGORIES = [
    {"id": 1, "name": "person"},
    {"id": 2, "name": "bicycle"},
    {"id": 3, "name": "motorbike"},
    {"id": 4, "name": "car"},
    {"id": 5, "name": "bus"},
    {"id": 6, "name": "truck"},
    {"id": 7, "name": "three_wheeler"},
    {"id": 8, "name": "ignore_region"},
]
CAT_MAP = {c["name"]: c["id"] for c in CATEGORIES}

ANNOTATIONS_BY_IMAGE = {
    "img_001.jpg": [
        {"cat": "three_wheeler", "bbox": [185, 332, 345, 185], "can_review": False},
        {"cat": "person", "bbox": [554, 366, 52, 85], "can_review": False},
        {"cat": "person", "bbox": [255, 368, 15, 20], "can_review": True},
        {"cat": "motorbike", "bbox": [947, 370, 77, 102], "can_review": False},
        {"cat": "person", "bbox": [948, 353, 38, 42], "can_review": False},
        {"cat": "motorbike", "bbox": [905, 382, 54, 82], "can_review": False},
        {"cat": "person", "bbox": [863, 386, 24, 48], "can_review": False},
        {"cat": "motorbike", "bbox": [925, 380, 62, 88], "can_review": False},
        {"cat": "person", "bbox": [639, 382, 28, 56], "can_review": False},
        {"cat": "motorbike", "bbox": [555, 399, 52, 75], "can_review": False},
        {"cat": "three_wheeler", "bbox": [637, 404, 28, 42], "can_review": True},
        {"cat": "motorbike", "bbox": [121, 406, 58, 42], "can_review": False},
        {"cat": "ignore_region", "bbox": [610, 385, 230, 45], "can_review": False},
    ],
    "img_012.jpg": [
        {"cat": "three_wheeler", "bbox": [540, 375, 456, 358], "can_review": False},
        {"cat": "person", "bbox": [707, 291, 28, 95], "can_review": True},
        {"cat": "three_wheeler", "bbox": [365, 167, 224, 280], "can_review": False},
        {"cat": "person", "bbox": [456, 267, 49, 210], "can_review": False},
        {"cat": "car", "bbox": [18, 167, 274, 240], "can_review": False},
        {"cat": "car", "bbox": [588, 177, 253, 235], "can_review": False},
        {"cat": "car", "bbox": [441, 79, 199, 208], "can_review": False},
        {"cat": "car", "bbox": [238, 56, 175, 210], "can_review": False},
        {"cat": "car", "bbox": [261, 0, 337, 58], "can_review": False},
        {"cat": "person", "bbox": [590, 0, 49, 134], "can_review": False},
        {"cat": "person", "bbox": [748, 1, 47, 147], "can_review": False},
    ],
    "img_020.jpg": [
        {"cat": "three_wheeler", "bbox": [215, 197, 370, 352], "can_review": False},
        {"cat": "person", "bbox": [445, 250, 97, 148], "can_review": False},
        {"cat": "person", "bbox": [312, 267, 96, 144], "can_review": False},
        {"cat": "three_wheeler", "bbox": [719, 185, 208, 252], "can_review": False},
        {"cat": "car", "bbox": [18, 240, 258, 189], "can_review": False},
        {"cat": "car", "bbox": [624, 211, 124, 101], "can_review": False},
        {"cat": "car", "bbox": [889, 177, 92, 87], "can_review": False},
        {"cat": "truck", "bbox": [581, 192, 69, 73], "can_review": True},
        {"cat": "bus", "bbox": [952, 137, 72, 86], "can_review": False},
    ],
    "img_036.jpg": [
        {"cat": "motorbike", "bbox": [472, 415, 135, 161], "can_review": False},
        {"cat": "person", "bbox": [485, 245, 159, 312], "can_review": False},
        {"cat": "motorbike", "bbox": [331, 370, 75, 111], "can_review": False},
        {"cat": "person", "bbox": [319, 255, 102, 199], "can_review": False},
        {"cat": "person", "bbox": [372, 258, 57, 96], "can_review": False},
        {"cat": "three_wheeler", "bbox": [759, 310, 65, 55], "can_review": True},
        {"cat": "person", "bbox": [786, 313, 20, 44], "can_review": False},
        {"cat": "person", "bbox": [806, 315, 16, 44], "can_review": False},
        {"cat": "person", "bbox": [183, 289, 16, 42], "can_review": False},
        {"cat": "motorbike", "bbox": [964, 343, 54, 41], "can_review": False},
        {"cat": "ignore_region", "bbox": [660, 305, 90, 45], "can_review": False},
    ],
}

IMG_DIMS = {
    "img_001.jpg": (1024, 576),
    "img_012.jpg": (1024, 819),
    "img_020.jpg": (1024, 682),
    "img_036.jpg": (1024, 576),
}


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
    images = []
    annotations = []
    ann_id = 1

    for img_id, (fn, (w, h)) in enumerate(IMG_DIMS.items(), 1):
        images.append({
            "id": img_id,
            "file_name": fn,
            "width": w,
            "height": h,
        })
        for item in ANNOTATIONS_BY_IMAGE[fn]:
            x, y, bw, bh = item["bbox"]
            annotations.append({
                "id": ann_id,
                "image_id": img_id,
                "category_id": CAT_MAP[item["cat"]],
                "bbox": [x, y, bw, bh],
                "area": bw * bh,
                "iscrowd": 0,
                "segmentation": [],
                "attributes": {
                    "conf": "",
                    "can_review": "true" if item["can_review"] else "false",
                },
            })
            ann_id += 1

    coco_data = {
        "info": {
            "description": "Gold manual ground truth annotations",
            "taxonomy": "v1.0",
            "annotator": "PhamVanNgocVinh-03262",
        },
        "licenses": [],
        "categories": CATEGORIES,
        "images": images,
        "annotations": annotations,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(coco_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[+] Đã ghi file {OUT_PATH} ({len(images)} ảnh, {len(annotations)} annotations)")

    auth_key = get_auth_key()
    if auth_key:
        print("[*] Đang nạp annotations vào Task 15 trên CVAT...")
        try:
            client = Client(url="http://localhost:8080")
            client.api_client.default_headers["Authorization"] = f"Token {auth_key}"
            task15 = client.tasks.retrieve(15)
            task15.import_annotations("COCO 1.0", str(OUT_PATH))
            print("[+] Đã nạp thành công vào Task 15 trên CVAT! Xem tại: http://localhost:8080/tasks/15/jobs/15")
        except Exception as e:
            print(f"[!] Lỗi khi nạp vào CVAT: {e}")


if __name__ == "__main__":
    main()
