#!/usr/bin/env python3
"""Entrypoint for the news-image-20261118 entry.

Validates the bundled entry.png (format magic, size cap, dimension cap),
copies it to $MAKEFUN_OUTPUT_DIR/entry.png, and verifies the copy by
sha256 read-back. Exits non-zero on any validation failure and writes
nothing in that case.
"""
import hashlib
import os
import struct
import sys

MAX_BYTES = 1024 * 1024          # 1 MiB contest cap
MAX_DIM = 1024                   # 1024 px contest cap per side
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def png_dimensions(data):
    """(width, height) from the IHDR chunk of a PNG byte string."""
    if len(data) < 24:
        raise ValueError("PNG too short for IHDR")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def jpeg_dimensions(data):
    """(width, height) from the first SOF marker of a JPEG byte string."""
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            raise ValueError("JPEG marker expected")
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg_len
    raise ValueError("no JPEG SOF marker found")


def validate(data):
    """Raise ValueError unless data is a contest-legal entry image."""
    if len(data) > MAX_BYTES:
        raise ValueError(f"entry is {len(data)} bytes, over the 1 MiB cap")
    if data.startswith(PNG_MAGIC):
        width, height = png_dimensions(data)
    elif data.startswith(JPEG_MAGIC):
        width, height = jpeg_dimensions(data)
    else:
        raise ValueError("entry is neither PNG nor JPEG (bad magic bytes)")
    if width <= 0 or height <= 0:
        raise ValueError("entry has a zero dimension")
    if width > MAX_DIM or height > MAX_DIM:
        raise ValueError(f"entry is {width}x{height}, over the 1024px cap")
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    with open(src, "rb") as fh:
        data = fh.read()
    width, height = validate(data)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    with open(dst, "wb") as fh:
        fh.write(data)

    with open(dst, "rb") as fh:
        written = fh.read()
    src_hash = hashlib.sha256(data).hexdigest()
    out_hash = hashlib.sha256(written).hexdigest()
    if written != data or src_hash != out_hash:
        raise ValueError("read-back verification failed: sha256 mismatch")
    print(f"entry.png OK: {width}x{height}, {len(data)} bytes, "
          f"sha256 {src_hash}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
