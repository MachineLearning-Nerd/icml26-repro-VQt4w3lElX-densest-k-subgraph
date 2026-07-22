#!/usr/bin/env python3
"""Source-pinned audit of the blanket Figure-4 cost-dominance wording.

Downloads the six exact ar5iv Figure 4 panels, verifies their SHA-256 hashes,
decodes their RGBA PNG pixels using only the standard library, and compares
the core Matplotlib line colors for FW and LRBO.  In image coordinates a
larger y position is a lower plotted runtime.
"""

import hashlib
import struct
import urllib.request
import zlib


BASE = "https://ar5iv.labs.arxiv.org/html/2410.07388/assets/fig/"
PANELS = (
    ("Facebook", "Facebook_time.png", "b711ecefd1229551aa82a4e75df7cb7bfd56a84822ac5cb25fac7c4baedb1d7e", 373, 299),
    ("web-Stanford", "web-Stanford_time.png", "c14b11a567bc577305e53470b225ba453bdfcc66651bb23702be7beda6f7e590", 362, 330),
    ("com-Youtube", "com-Youtube_time.png", "d667d1d1a78196843da73fbd352b2c44057ccc5190179cdc4ad907a623dc2d31", 432, 432),
    ("soc-Pokec", "soc-Pokec_time.png", "e8e02d1b4d5cbe05d90b075f1b84b80048e1ea6361252a5acb4b65dccad150f6", 354, 322),
    ("as-Skitter", "as-Skitter_time.png", "510c9517cf11db59fff6a9c447cb84155f4e57c869a596b5d75231f3d63d4ada", 431, 431),
    ("com-Orkut", "com-Orkut_time.png", "a8a312d3ac2e6144dc89f3b9f9fb2b697eac1d84ee5f5f2ee6278164364ec018", 279, 204),
)
FW = (31, 119, 180)
LRBO = (148, 103, 189)


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def paeth(a, b, c):
    estimate = a + b - c
    da, db, dc = abs(estimate - a), abs(estimate - b), abs(estimate - c)
    return a if da <= db and da <= dc else (b if db <= dc else c)


def decode_rgba_png(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    offset = 8
    compressed = bytearray()
    width = height = None
    while offset < len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        payload = data[offset + 8 : offset + 8 + length]
        offset += 12 + length
        if kind == b"IHDR":
            width, height, depth, color_type, compression, filtering, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
            if (depth, color_type, compression, filtering, interlace) != (8, 6, 0, 0, 0):
                raise ValueError("expected non-interlaced 8-bit RGBA PNG")
        elif kind == b"IDAT":
            compressed.extend(payload)
        elif kind == b"IEND":
            break
    if (width, height) != (640, 480):
        raise ValueError(f"unexpected dimensions {(width, height)}")

    raw = zlib.decompress(bytes(compressed))
    stride = width * 4
    prior = bytearray(stride)
    rows = []
    position = 0
    for _ in range(height):
        filter_type = raw[position]
        position += 1
        scan = bytearray(raw[position : position + stride])
        position += stride
        for i, value in enumerate(scan):
            left = scan[i - 4] if i >= 4 else 0
            up = prior[i]
            upper_left = prior[i - 4] if i >= 4 else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            elif filter_type == 4:
                predictor = paeth(left, up, upper_left)
            else:
                raise ValueError(f"unsupported PNG filter {filter_type}")
            scan[i] = (value + predictor) & 255
        rows.append(bytes(scan))
        prior = scan
    return width, height, rows


def rgb(rows, x, y):
    start = x * 4
    return tuple(rows[y][start : start + 3])


def line_positions(rows, color):
    positions = {}
    # This crop contains the data lines but excludes the top-left legend.
    for x in range(100, 555):
        hits = [y for y in range(250, 430) if rgb(rows, x, y) == color]
        if hits:
            positions[x] = (sum(hits), len(hits))
    return positions


def compare_panel(data):
    _, _, rows = decode_rgba_png(data)
    fw = line_positions(rows, FW)
    lrbo = line_positions(rows, LRBO)
    common = sorted(set(fw) & set(lrbo))
    lrbo_lower = 0
    for x in common:
        fw_sum, fw_n = fw[x]
        lrbo_sum, lrbo_n = lrbo[x]
        if lrbo_sum * fw_n > fw_sum * lrbo_n:
            lrbo_lower += 1
    return len(common), lrbo_lower


def main():
    rows = []
    for dataset, filename, expected_sha, expected_common, expected_lower in PANELS:
        data = fetch(BASE + filename)
        actual_sha = hashlib.sha256(data).hexdigest()
        if actual_sha != expected_sha:
            raise AssertionError(f"source hash mismatch for {filename}: {actual_sha}")
        common, lower = compare_panel(data)
        if (common, lower) != (expected_common, expected_lower):
            raise AssertionError(
                f"pixel audit drift for {filename}: {(common, lower)} != "
                f"{(expected_common, expected_lower)}"
            )
        rows.append((dataset, common, lower))

    total_common = sum(row[1] for row in rows)
    total_lower = sum(row[2] for row in rows)
    any_lower = sum(row[2] > 0 for row in rows)
    majority_lower = sum(2 * row[2] > row[1] for row in rows)
    if (total_common, total_lower, any_lower, majority_lower) != (2231, 2018, 6, 6):
        raise AssertionError("aggregate Figure 4 gate failed")

    print("claim=Figure 4 blanket computational-cost dominance over listed baselines")
    print("source=ar5iv Figure 4 exact PNG panels")
    print("image_hashes_matching=6/6")
    for dataset, common, lower in rows:
        print(
            f"dataset={dataset} matched_columns={common} "
            f"lrbo_lower_runtime_columns={lower}"
        )
    print(f"matched_columns_total={total_common}")
    print(f"lrbo_lower_runtime_columns_total={total_lower}")
    print(f"lrbo_lower_runtime_fraction={100 * total_lower / total_common:.2f}%")
    print(f"datasets_with_any_lrbo_lower_runtime={any_lower}/6")
    print(f"datasets_with_lrbo_lower_runtime_majority={majority_lower}/6")
    print("verdict=REFUTED_AS_STATED")
    print(
        "reason=Figure 4 does not show FW cheaper than every named competitor; "
        "LRBO is plotted lower in 90.45% of matched source-image columns."
    )


if __name__ == "__main__":
    main()
