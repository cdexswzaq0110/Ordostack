from __future__ import annotations

import argparse
import shutil
import struct
import sys
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def read_png_pixels(path: Path) -> tuple[tuple[int, int], bytes]:
    payload = path.read_bytes()
    if not payload.startswith(PNG_SIGNATURE):
        raise ValueError(f"{path} is not a PNG file")

    offset = len(PNG_SIGNATURE)
    width = 0
    height = 0
    image_data = bytearray()
    while offset < len(payload):
        chunk_length = struct.unpack(">I", payload[offset : offset + 4])[0]
        chunk_type = payload[offset + 4 : offset + 8]
        chunk_data = payload[offset + 8 : offset + 8 + chunk_length]
        offset += 12 + chunk_length

        if chunk_type == b"IHDR":
            width, height = struct.unpack(">II", chunk_data[:8])
        elif chunk_type == b"IDAT":
            image_data.extend(chunk_data)
        elif chunk_type == b"IEND":
            break

    if width <= 0 or height <= 0 or not image_data:
        raise ValueError(f"{path} does not contain readable PNG image data")

    return (width, height), zlib.decompress(bytes(image_data))


def diff_ratio(left: bytes, right: bytes) -> float:
    compared_length = min(len(left), len(right))
    if compared_length == 0:
        return 1.0

    changed_bytes = abs(len(left) - len(right))
    changed_bytes += sum(1 for index in range(compared_length) if left[index] != right[index])
    return changed_bytes / max(len(left), len(right))


def compare_pngs(baseline_path: Path, candidate_path: Path, threshold: float) -> dict[str, object]:
    baseline_size, baseline_pixels = read_png_pixels(baseline_path)
    candidate_size, candidate_pixels = read_png_pixels(candidate_path)
    if baseline_size != candidate_size:
        return {
            "status": "failed",
            "reason": "image dimensions differ",
            "baseline_size": baseline_size,
            "candidate_size": candidate_size,
            "diff_ratio": 1.0,
            "threshold": threshold,
        }

    ratio = diff_ratio(baseline_pixels, candidate_pixels)
    return {
        "status": "ok" if ratio <= threshold else "failed",
        "reason": "within threshold" if ratio <= threshold else "pixel difference exceeds threshold",
        "baseline_size": baseline_size,
        "candidate_size": candidate_size,
        "diff_ratio": round(ratio, 6),
        "threshold": threshold,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two PNG screenshots with a simple pixel threshold.")
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--threshold", type=float, default=0.01)
    parser.add_argument("--update", action="store_true", help="Copy candidate to baseline before comparing.")
    args = parser.parse_args()

    if args.update:
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.candidate, args.baseline)
        print(f"updated baseline: {args.baseline}")
        return 0

    result = compare_pngs(args.baseline, args.candidate, args.threshold)
    print(result)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
