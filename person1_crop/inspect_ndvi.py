#!/usr/bin/env python3
"""
inspect_ndvi.py - look at your NDVI curves before trusting any classifier.

    python inspect_ndvi.py field_ndvi.csv

Prints one line per field: observation count, NDVI range, and an ASCII plot of
the time series. You are looking for a clear arc that rises and falls. If the
line is flat, jagged, or noisy with no shape, the classifier cannot help you
and the problem is upstream in the data.
"""

import csv
import sys
from datetime import datetime

BLOCKS = " .:-=+*#%@"


def load(path):
    by_field = {}
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            fid = (row.get("field_id") or "").strip()
            if not fid:
                continue
            try:
                d = datetime.strptime(row["date"].strip(), "%Y-%m-%d").date()
                v = float(row["ndvi"])
            except (KeyError, TypeError, ValueError):
                continue
            if -1.0 <= v <= 1.0:
                by_field.setdefault(fid, []).append((d, v))
    for fid in by_field:
        by_field[fid].sort()
    return by_field


def sparkline(values, lo=0.0, hi=0.9):
    out = []
    for v in values:
        frac = (v - lo) / (hi - lo)
        idx = max(0, min(len(BLOCKS) - 1, int(frac * (len(BLOCKS) - 1))))
        out.append(BLOCKS[idx])
    return "".join(out)


def main():
    if len(sys.argv) < 2:
        print("usage: python inspect_ndvi.py <csv>")
        return 1

    by_field = load(sys.argv[1])
    if not by_field:
        print("no usable rows")
        return 1

    print(f"\n{len(by_field)} fields\n")
    print("scale: ' ' = NDVI 0.0   '@' = NDVI 0.9\n")

    for fid in sorted(by_field):
        pts = by_field[fid]
        vals = [v for _, v in pts]
        lo, hi = min(vals), max(vals)
        amp = hi - lo
        print(f"{fid}  n={len(pts):3d}  min={lo:.2f}  max={hi:.2f}  amp={amp:.2f}")
        print(f"      {pts[0][0]} to {pts[-1][0]}")
        print(f"      |{sparkline(vals)}|")

        if amp < 0.20:
            print("      ^^ FLAT. Amplitude under 0.20 means no crop cycle is visible.")
            print("         Either the parcel is not cropped, or the box is averaging")
            print("         too many different fields together.")
        elif len(pts) < 5:
            print("      ^^ SPARSE. Too few clear dates to fit a curve reliably.")
        print()

    all_amp = [max(v for _, v in p) - min(v for _, v in p) for p in by_field.values()]
    mean_amp = sum(all_amp) / len(all_amp)
    print(f"mean amplitude across fields: {mean_amp:.2f}")
    if mean_amp < 0.25:
        print("\nThis is the problem. Healthy single-crop fields swing roughly 0.5 to 0.7")
        print("across a season. Shrink your field boxes or move them onto real parcels.")
    else:
        print("\nAmplitudes look healthy. If confidence is still low, the profile")
        print("library probably does not contain the crop that is actually growing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
