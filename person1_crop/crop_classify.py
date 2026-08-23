#!/usr/bin/env python3
"""
crop_classify.py - Person 1 deliverable: crop type classification.

Two modes, ONE interface. Person 4 integrates against this CLI on Day 1 using
--mode dummy and never has to change a line when --mode baseline becomes real.

Pure standard library. No pip install, runs on any teammate's machine.

Usage
-----
  # Day 1 morning: schema-compliant dummy output, needs no data at all
  python crop_classify.py --mode dummy --fields F001 F002 F003 F004 --out crop_predictions

  # Day 1 afternoon onward: the real baseline
  python crop_classify.py --mode baseline --input field_ndvi.csv --season rabi --out crop_predictions

  # Sanity check on synthetic fields (zero dependency on Person 2)
  python crop_classify.py --selftest --season rabi

Input CSV from Person 2
-----------------------
  field_id,date,ndvi
  F001,2024-11-05,0.21
  F001,2024-11-20,0.34
  ...
One row per field per satellite acquisition date. Extra columns (ndwi, vh_db)
are read and ignored for now - the hook is there, do not block on it.

Output
------
  <out>.json and <out>.csv
  ALWAYS one record per input field_id. A field that fails to classify comes
  out as crop="unknown", confidence=0.0 - never missing. Person 4's pipeline
  should never have to handle a gap.

Method (for the methodology slide, Person 6)
--------------------------------------------
Single-date NDVI thresholds cannot separate wheat from mustard from gram -
their value ranges overlap heavily on any one date. What separates them is the
SHAPE of the NDVI curve over the season (phenology). So: each field's observed
NDVI time series is compared against a small library of reference crop
phenology curves, with a search over sowing-date offset to absorb the fact that
farmers do not all sow on the same day. Best fit wins. This is still a lookup
classifier - no training data required - but it uses the multi-temporal
signature the problem statement actually asks for.
"""

import argparse
import csv
import json
import math
import os
import random
import sys
from datetime import date, datetime, timedelta

VERSION = "0.3.0"

# ---------------------------------------------------------------------------
# Reference phenology library
#
# Anchors are (days since season start, NDVI). Linearly interpolated between.
# Season start: rabi = Oct 1, kharif = Jun 1.
#
# EDIT THIS TABLE FIRST if your pilot region grows something else. It is the
# only domain knowledge in the file and it is where accuracy comes from.
# ---------------------------------------------------------------------------

SEASON_START = {"rabi": (10, 1), "kharif": (6, 1)}

CROP_PROFILES = {
    "rabi": {
        "wheat": [
            (0, 0.15), (30, 0.15), (45, 0.20), (60, 0.32), (75, 0.48),
            (95, 0.68), (115, 0.80), (130, 0.82), (145, 0.70), (160, 0.45),
            (175, 0.25), (190, 0.16),
        ],
        "mustard": [
            (0, 0.15), (15, 0.18), (30, 0.28), (45, 0.45), (60, 0.60),
            (75, 0.66), (90, 0.62), (105, 0.55), (120, 0.38), (135, 0.22),
            (150, 0.15), (190, 0.14),
        ],
        "gram": [
            (0, 0.14), (30, 0.16), (50, 0.25), (70, 0.40), (90, 0.55),
            (105, 0.62), (120, 0.58), (135, 0.42), (150, 0.26), (165, 0.16),
            (190, 0.14),
        ],
        "sugarcane": [
            (0, 0.55), (30, 0.60), (60, 0.62), (90, 0.58), (120, 0.55),
            (150, 0.58), (175, 0.65), (190, 0.68),
        ],
        "fallow": [
            (0, 0.13), (60, 0.14), (120, 0.13), (190, 0.14),
        ],
    },
    "kharif": {
        "rice": [
            (0, 0.18), (20, 0.20), (35, 0.15), (50, 0.30), (70, 0.55),
            (90, 0.72), (105, 0.78), (120, 0.68), (135, 0.45), (150, 0.25),
            (165, 0.16), (190, 0.15),
        ],
        "cotton": [
            (0, 0.16), (20, 0.22), (40, 0.35), (60, 0.48), (85, 0.62),
            (105, 0.70), (125, 0.68), (145, 0.55), (165, 0.40), (185, 0.25),
        ],
        "maize": [
            (0, 0.16), (20, 0.25), (40, 0.45), (60, 0.65), (75, 0.72),
            (90, 0.66), (105, 0.48), (120, 0.28), (140, 0.18), (190, 0.16),
        ],
        "sugarcane": [
            (0, 0.45), (30, 0.60), (60, 0.72), (90, 0.78), (120, 0.78),
            (150, 0.75), (180, 0.70), (190, 0.68),
        ],
        "fallow": [
            (0, 0.14), (60, 0.15), (120, 0.14), (190, 0.15),
        ],
    },
}

# Matching hyperparameters. Sensible defaults; tune only if you have labels.
SHIFT_RANGE = 21        # +/- days of sowing-date search
SHIFT_STEP = 3
TAU = 0.10              # RMSE -> score temperature, controls confidence spread
MIN_OBS_FOR_TEMPORAL = 3
BAD_FIT_RMSE = 0.22     # above this, the field matches nothing well


# ---------------------------------------------------------------------------
# Team-agreed output vocabulary
#
# CONFIRM these exact strings with Person 4 before Day 2. A case mismatch
# ("wheat" vs "Wheat") will silently break their join and nobody will notice
# until the demo.
# ---------------------------------------------------------------------------

INV_CROP_DISPLAY = {}
CROP_DISPLAY = {
    "wheat": "Wheat", "mustard": "Mustard", "gram": "Gram",
    "sugarcane": "Sugarcane", "fallow": "Fallow",
    "rice": "Rice", "cotton": "Cotton", "maize": "Maize",
    "unknown": "Unknown",
}
INV_CROP_DISPLAY.update({v: k for k, v in CROP_DISPLAY.items()})

# Internal stage names -> the team's vocabulary. Their sample used "Flowering",
# which is a reproductive sub-stage; this is the mapping I assumed.
STAGE_DISPLAY = {
    "bare_or_emergence": "Emergence",
    "bare": "Pre-Sowing",
    "vegetative": "Vegetative",
    "reproductive": "Flowering",
    "maturity": "Maturity",
    "post_harvest": "Harvested",
    "standing": "Standing",
}

# Fields owned by other people. Emitted as null so the record shape is stable
# from Day 1 and Person 4 never has to construct it - they just fill these in.
DOWNSTREAM_FIELDS = [
    "stress_level", "stress_score", "water_deficit_mm",
    "irrigation_priority", "recommendation",
]


# ---------------------------------------------------------------------------
# Profile maths
# ---------------------------------------------------------------------------

def interp_profile(anchors, t):
    """NDVI of a reference profile at day t (linear, clamped at the ends)."""
    if t <= anchors[0][0]:
        return anchors[0][1]
    if t >= anchors[-1][0]:
        return anchors[-1][1]
    for i in range(len(anchors) - 1):
        t0, v0 = anchors[i]
        t1, v1 = anchors[i + 1]
        if t0 <= t <= t1:
            if t1 == t0:
                return v0
            frac = (t - t0) / (t1 - t0)
            return v0 + frac * (v1 - v0)
    return anchors[-1][1]


def days_since_season_start(d, season):
    """Convert a calendar date to days since this season's start."""
    month, day = SEASON_START[season]
    start_year = d.year if (d.month, d.day) >= (month, day) else d.year - 1
    return (d - date(start_year, month, day)).days


def profile_peak(anchors):
    """(peak_day, peak_ndvi, amplitude) sampled densely."""
    lo, hi = anchors[0][0], anchors[-1][0]
    best_t, best_v, min_v = lo, -1.0, 1.0
    t = lo
    while t <= hi:
        v = interp_profile(anchors, t)
        if v > best_v:
            best_v, best_t = v, t
        if v < min_v:
            min_v = v
        t += 1
    return best_t, best_v, best_v - min_v


def growth_stage(anchors, t):
    """
    Optional extra: rough phenological stage at day t.

    Person 3 (moisture stress) needs stage, not just crop type, and this comes
    almost free. Metadata only - do not let it eat P0 time.
    """
    peak_t, peak_v, amp = profile_peak(anchors)
    if amp < 0.15:
        # low-amplitude curve: either bare ground all season, or a standing
        # near-perennial like sugarcane. Stage is not resolvable either way.
        return "bare" if peak_v < 0.30 else "standing"
    v = interp_profile(anchors, t)
    if v < 0.40 * peak_v:
        return "bare_or_emergence" if t < peak_t else "post_harvest"
    if t < peak_t and v < 0.90 * peak_v:
        return "vegetative"
    if abs(v - peak_v) <= 0.10 * peak_v:
        return "reproductive"
    return "maturity"


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def rmse_against(anchors, obs_days, obs_ndvi, shift):
    total = 0.0
    for t, v in zip(obs_days, obs_ndvi):
        pred = interp_profile(anchors, t - shift)
        total += (v - pred) ** 2
    return math.sqrt(total / len(obs_days))


def classify_temporal(obs_days, obs_ndvi, season):
    """Nearest reference phenology curve, searching over sowing offset."""
    library = CROP_PROFILES[season]
    results = {}
    for crop, anchors in library.items():
        best_rmse, best_shift = None, 0
        shift = -SHIFT_RANGE
        while shift <= SHIFT_RANGE:
            r = rmse_against(anchors, obs_days, obs_ndvi, shift)
            if best_rmse is None or r < best_rmse:
                best_rmse, best_shift = r, shift
            shift += SHIFT_STEP
        results[crop] = (best_rmse, best_shift)

    ranked = sorted(results.items(), key=lambda kv: kv[1][0])
    top_crop, (top_rmse, top_shift) = ranked[0]
    runner_up = ranked[1][0] if len(ranked) > 1 else None

    # RMSE -> normalised score. Softmax-style, so confidence reflects the
    # MARGIN over the next-best crop, not just how good the fit was.
    scores = {c: math.exp(-r / TAU) for c, (r, _) in results.items()}
    total = sum(scores.values()) or 1.0
    confidence = scores[top_crop] / total

    # Penalise fields that fit nothing well.
    quality = max(0.20, min(1.0, 1.0 - (top_rmse - 0.06) / 0.20))
    confidence *= quality

    if top_rmse > BAD_FIT_RMSE:
        return "unknown", round(min(confidence, 0.30), 3), runner_up, top_shift

    return top_crop, round(confidence, 3), runner_up, top_shift


def classify_single_date(ndvi, season):
    """
    Fallback when a field has fewer than 3 clear observations.

    Deliberately weak and capped low, because a single NDVI value genuinely
    cannot distinguish these crops. Better to report low confidence than to
    fake a number.
    """
    if season == "rabi":
        if ndvi >= 0.55:
            guess = "sugarcane"
        elif ndvi >= 0.30:
            guess = "wheat"
        else:
            guess = "fallow"
    else:
        if ndvi >= 0.65:
            guess = "sugarcane"
        elif ndvi >= 0.35:
            guess = "rice"
        else:
            guess = "fallow"
    return guess, 0.35


def classify_field(field_id, rows, season):
    """rows: list of dicts with 'date' (date obj) and 'ndvi' (float)."""
    rows = sorted(rows, key=lambda r: r["date"])
    obs_days = [days_since_season_start(r["date"], season) for r in rows]
    obs_ndvi = [r["ndvi"] for r in rows]

    crop_key, stage_key = "unknown", None
    conf, runner_up, shift = 0.0, None, None
    method = "none"

    if rows:
        if len(rows) >= MIN_OBS_FOR_TEMPORAL:
            crop_key, conf, runner_up, shift = classify_temporal(obs_days, obs_ndvi, season)
            method = "temporal_profile_match"
            if crop_key in CROP_PROFILES[season]:
                stage_key = growth_stage(CROP_PROFILES[season][crop_key], obs_days[-1] - shift)
        else:
            crop_key, conf = classify_single_date(obs_ndvi[-1], season)
            method = "single_date_fallback"

    record = {
        # --- owned by Person 1 ---
        "field_id": field_id,
        "crop": CROP_DISPLAY.get(crop_key, crop_key.title()),
        "confidence_or_score": conf,
        "growth_stage": STAGE_DISPLAY.get(stage_key) if stage_key else None,
        # --- owned downstream, left null for Person 3 / advisory layer ---
        **{k: None for k in DOWNSTREAM_FIELDS},
        # --- diagnostics, additive, safe to ignore ---
        "method": method,
        "n_observations": len(rows),
        "runner_up": CROP_DISPLAY.get(runner_up) if runner_up else None,
        "sowing_shift_days": shift,
        "season": season,
        "version": VERSION,
    }
    if rows:
        record["date_range"] = [rows[0]["date"].isoformat(), rows[-1]["date"].isoformat()]
    return record


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

FIELDNAMES = (
    ["field_id", "crop", "confidence_or_score", "growth_stage"]
    + DOWNSTREAM_FIELDS
    + ["method", "n_observations", "runner_up", "sowing_shift_days",
       "season", "version"]
)


def load_csv(path):
    by_field = {}
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            fid = (row.get("field_id") or "").strip()
            if not fid:
                continue
            raw_ndvi = (row.get("ndvi") or "").strip()
            raw_date = (row.get("date") or "").strip()
            by_field.setdefault(fid, [])
            try:
                ndvi = float(raw_ndvi)
                d = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except (TypeError, ValueError):
                continue          # bad row, field still exists in output
            if ndvi != ndvi or ndvi < -1.0 or ndvi > 1.0:
                continue          # NaN or impossible NDVI
            by_field[fid].append({"date": d, "ndvi": ndvi})
    return by_field


def write_outputs(records, out_stem):
    parent = os.path.dirname(out_stem)
    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(out_stem + ".json", "w") as fh:
        json.dump(records, fh, indent=2)

    with open(out_stem + ".csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    print(f"wrote {len(records)} records -> {out_stem}.json and {out_stem}.csv")


# ---------------------------------------------------------------------------
# Dummy mode
# ---------------------------------------------------------------------------

def dummy_records(field_ids, season):
    """Same record shape as the real thing, so Person 4 integrates once."""
    crops = [c for c in CROP_PROFILES[season] if c != "fallow"]
    stages = ["Vegetative", "Flowering", "Maturity", "Emergence"]
    out = []
    for i, fid in enumerate(field_ids):
        crop = crops[i % len(crops)]
        out.append({
            "field_id": fid,
            "crop": CROP_DISPLAY[crop],
            "confidence_or_score": round(0.90 - 0.07 * (i % 4), 3),
            "growth_stage": stages[i % len(stages)],
            **{k: None for k in DOWNSTREAM_FIELDS},
            "method": "dummy",
            "n_observations": 0,
            "runner_up": CROP_DISPLAY[crops[(i + 1) % len(crops)]],
            "sowing_shift_days": 0,
            "season": season,
            "version": VERSION,
        })
    return out


# ---------------------------------------------------------------------------
# Self-test on synthetic fields
# ---------------------------------------------------------------------------

def synth_field(crop, season, revisit=10, noise=0.05, jitter=15, rng=random):
    anchors = CROP_PROFILES[season][crop]
    shift = rng.randint(-jitter, jitter)
    month, day = SEASON_START[season]
    start = date(2024, month, day)
    rows = []
    t = 5
    while t <= 185:
        true_v = interp_profile(anchors, t - shift)
        v = max(0.0, min(1.0, true_v + rng.gauss(0, noise)))
        if rng.random() > 0.25:                # ~25% of dates lost to cloud
            rows.append({"date": start + timedelta(days=t), "ndvi": round(v, 3)})
        t += revisit
    return rows


def selftest(season, n=300, seed=7):
    rng = random.Random(seed)
    crops = list(CROP_PROFILES[season].keys())
    correct = 0
    confusion = {a: {b: 0 for b in crops + ["unknown"]} for a in crops}
    for i in range(n):
        truth = crops[i % len(crops)]
        rows = synth_field(truth, season, rng=rng)
        rec = classify_field(f"S{i:03d}", rows, season)
        pred = INV_CROP_DISPLAY.get(rec["crop"], "unknown")
        confusion[truth][pred if pred in confusion[truth] else "unknown"] += 1
        if pred == truth:
            correct += 1

    acc = correct / n
    print(f"\nself-test  season={season}  n={n}")
    print(f"accuracy on synthetic phenology (+/-15d sowing jitter, sigma=0.05 NDVI, 25% cloud loss): {acc:.1%}\n")
    header = "truth \\ pred".ljust(14) + "".join(c[:9].rjust(11) for c in crops + ["unknown"])
    print(header)
    for a in crops:
        line = a.ljust(14) + "".join(str(confusion[a][b]).rjust(11) for b in crops + ["unknown"])
        print(line)
    print("\nNOTE: synthetic data, so this measures internal consistency of the")
    print("profile library, NOT real-world accuracy. Say that out loud on the slide.")
    return acc


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    p = argparse.ArgumentParser(description="Crop type classification (Person 1).")
    p.add_argument("--mode", choices=["dummy", "baseline"], default="baseline")
    p.add_argument("--input", help="CSV from Person 2: field_id,date,ndvi")
    p.add_argument("--fields", nargs="*", default=["F001", "F002", "F003", "F004"],
                   help="field ids for --mode dummy")
    p.add_argument("--season", choices=["rabi", "kharif"], default="rabi")
    p.add_argument("--out", default="crop_predictions", help="output path stem")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)

    if args.selftest:
        selftest(args.season)
        return 0

    if args.mode == "dummy":
        write_outputs(dummy_records(args.fields, args.season), args.out)
        return 0

    if not args.input:
        p.error("--mode baseline needs --input <csv>")
    if not os.path.exists(args.input):
        p.error(f"input not found: {args.input}")

    by_field = load_csv(args.input)
    if not by_field:
        print("no usable rows in input", file=sys.stderr)
        return 1

    records = []
    for fid in sorted(by_field):
        try:
            records.append(classify_field(fid, by_field[fid], args.season))
        except Exception as exc:                      # never drop a field
            print(f"  {fid}: failed ({exc}) -> unknown", file=sys.stderr)
            records.append({
                "field_id": fid, "crop": "Unknown", "confidence_or_score": 0.0,
                "growth_stage": None,
                **{k: None for k in DOWNSTREAM_FIELDS},
                "method": "error", "n_observations": len(by_field[fid]),
                "runner_up": None, "sowing_shift_days": None,
                "season": args.season, "version": VERSION,
            })

    write_outputs(records, args.out)
    n_unknown = sum(1 for r in records if r["crop"] == "Unknown")
    mean_conf = sum(r["confidence_or_score"] for r in records) / len(records)
    print(f"unknown: {n_unknown}/{len(records)}   mean confidence: {mean_conf:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
