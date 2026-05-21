#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


HEADER_CODE_SIZES = {
    1: 64,
    2: 128,
    3: 512,
    4: 512,
    5: 512,
    6: 512,
    8: 512,
}


def u32le(buf: bytes, offset: int) -> int:
    if offset + 4 > len(buf):
        raise ValueError(f"firmware is too short to read u32 at offset {offset}")
    return int.from_bytes(buf[offset : offset + 4], "little")


def parse_header(data: bytes) -> dict:
    os_type = u32le(data, 0)
    if os_type not in HEADER_CODE_SIZES:
        raise ValueError(f"unsupported firmware header type {os_type}")

    code_size = HEADER_CODE_SIZES[os_type]
    header_size = code_size + 20
    if len(data) < header_size:
        raise ValueError(
            f"firmware is too short for header type {os_type}: "
            f"need {header_size} bytes, found {len(data)}"
        )

    raw_model_code = data[4 : 4 + code_size]
    ascii_model_code = raw_model_code.split(b"\x00", 1)[0].decode("ascii", "replace")
    decoded_model_code = "".join(
        chr(raw_model_code[i])
        for i in range(1, len(raw_model_code), 2)
        if raw_model_code[i] not in (0x00,)
    ).rstrip("0")

    header = {
        "type": os_type,
        "code_size": code_size,
        "header_size": header_size,
        "model_code_raw": raw_model_code,
        "model_code_ascii": ascii_model_code,
        "model_code": decoded_model_code,
        "version_major": u32le(data, 4 + code_size),
        "version_minor": u32le(data, 8 + code_size),
        "checksum": u32le(data, 12 + code_size),
        "end_marker": u32le(data, 16 + code_size),
    }
    header["version_hex"] = f"{header['version_major']:x}.{header['version_minor']:02x}"
    return header


def bitflip(buf: bytes) -> bytes:
    return bytes((~b) & 0xFF for b in buf)


def sha256(buf: bytes) -> str:
    return hashlib.sha256(buf).hexdigest()


def write_outputs(input_path: Path, out_dir: Path) -> dict:
    raw = input_path.read_bytes()
    header = parse_header(raw)
    payload_raw = raw[header["header_size"] :]
    payload = bitflip(payload_raw)

    out_dir.mkdir(parents=True, exist_ok=True)
    payload_path = out_dir / f"{input_path.stem}.bin"
    header_path = out_dir / f"{input_path.stem}.header.json"

    payload_path.write_bytes(payload)

    header_out = {
        k: (v.hex() if isinstance(v, bytes) else v)
        for k, v in header.items()
        if k != "model_code_raw"
    }
    header_out["input_file"] = input_path.name
    header_out["input_size"] = len(raw)
    header_out["payload_size"] = len(payload)
    header_out["payload_sha256"] = sha256(payload)
    header_out["header_sha256"] = sha256(raw[: header["header_size"]])
    header_path.write_text(json.dumps(header_out, indent=2) + "\n")

    return {
        "payload_path": str(payload_path),
        "header_path": str(header_path),
        "header": header_out,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Fujifilm DAT firmware payload")
    parser.add_argument("input", type=Path, help="path to Fujifilm DAT firmware")
    parser.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        default=Path("extracted"),
        help="directory for extracted output",
    )
    args = parser.parse_args()

    result = write_outputs(args.input, args.out_dir)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
