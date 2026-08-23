#!/usr/bin/env python3
"""
train_rf.py - Task 3 (Random Forest) and Task 4 (validation metrics).

    pip install scikit-learn
    python train_rf.py --series field_ndvi.csv --labels field_offseason.csv

---------------------------------------------------------------------------
WHAT THIS DOES, AND WHAT IT HONESTLY CANNOT DO
---------------------------------------------------------------------------
The Random Forest in the role spec was gated on labelled data. There is none.
Training on the baseline's own predictions would only teach the model to copy
the lookup table, and any accuracy it reported would be meaningless.

So this trains on a label the baseline never sees.

Labels come from OFF-SEASON (May-June) NDVI. The classifier only reads Nov-Apr,
so off-season observations are independent evidence, not circular.

    off-season NDVI high  -> still standing in May  -> PERENNIAL (sugarcane)
    off-season NDVI low   -> bare soil in May       -> ANNUAL (wheat/mustard/gram)

Fields in the ambiguous middle are DROPPED rather than guessed at.

This is a genuine two-class problem with genuine held-out validation. It does
NOT separate wheat from mustard from gram - no independent label for that
exists here. That distinction stays baseline-only, and the slide should say so.
---------------------------------------------------------------------------
"""

import argparse
import csv
import sys
from datetime import datetime

import crop_classify as cc

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
except ImportError:
    print("needs scikit-learn:  pip install scikit-learn", file=sys.stderr)
    raise SystemExit(1)


# Label thresholds on off-season NDVI. The gap between them is deliberate -
# fields landing inside it are genuinely ambiguous and get dropped.
PERENNIAL_ABOVE = 0.45
ANNUAL_BELOW = 0.25

# Feature grid: resample each field's irregular observations onto fixed days
# so every field becomes a same-length vector.
GRID_START, GRID_END, GRID_STEP = 40, 200, 10
MIN_OBS = 6


def load_series(path, season="rabi"):
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
                t = cc.days_since_season_start(d, season)
                by_field.setdefault(fid, []).append((t, v))
    for fid in by_field:
        by_field[fid].sort()
    return by_field


def load_labels(path):
    out, dropped = {}, 0
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            fid = (row.get("field_id") or "").strip()
            try:
                v = float(row["offseason_ndvi"])
            except (KeyError, TypeError, ValueError):
                continue
            if not fid:
                continue
            if v >= PERENNIAL_ABOVE:
                out[fid] = "perennial"
            elif v <= ANNUAL_BELOW:
                out[fid] = "annual"
            else:
                dropped += 1          # ambiguous, do not guess
    return out, dropped


def interp_at(pts, t):
    """Linear interpolation over a field's own observations."""
    if t <= pts[0][0]:
        return pts[0][1]
    if t >= pts[-1][0]:
        return pts[-1][1]
    for i in range(len(pts) - 1):
        t0, v0 = pts[i]
        t1, v1 = pts[i + 1]
        if t0 <= t <= t1:
            if t1 == t0:
                return v0
            return v0 + (t - t0) / (t1 - t0) * (v1 - v0)
    return pts[-1][1]


def featurise(pts):
    """Fixed-length feature vector from an irregular time series."""
    grid = list(range(GRID_START, GRID_END + 1, GRID_STEP))
    resampled = [interp_at(pts, t) for t in grid]

    vals = [v for _, v in pts]
    lo, hi = min(vals), max(vals)
    peak_t = max(pts, key=lambda p: p[1])[0]
    mean = sum(vals) / len(vals)
    # crude integral, proxy for total season biomass
    auc = sum(resampled) * GRID_STEP / 1000.0

    return resampled + [lo, hi, hi - lo, mean, peak_t / 200.0, auc]


def feature_names():
    grid = list(range(GRID_START, GRID_END + 1, GRID_STEP))
    return ([f"ndvi_d{t}" for t in grid]
            + ["min", "max", "amplitude", "mean", "peak_day", "auc"])


def baseline_prediction(pts, season="rabi"):
    """What the P0 lookup classifier says, collapsed to the same two classes."""
    obs_days = [t for t, _ in pts]
    obs_ndvi = [v for _, v in pts]
    crop_key, _, _, _ = cc.classify_temporal(obs_days, obs_ndvi, season)
    return "perennial" if crop_key == "sugarcane" else "annual"


def print_matrix(y_true, y_pred, labels, title):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    print(f"\n{title}")
    print("truth \\ pred".ljust(16) + "".join(l[:11].rjust(13) for l in labels))
    for i, l in enumerate(labels):
        print(l.ljust(16) + "".join(str(cm[i][j]).rjust(13) for j in range(len(labels))))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--series", required=True, help="field_ndvi.csv (Nov-Apr)")
    p.add_argument("--labels", required=True, help="field_offseason.csv (May-Jun)")
    p.add_argument("--season", default="rabi", choices=["rabi", "kharif"])
    p.add_argument("--test-size", type=float, default=0.3)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    series = load_series(args.series, args.season)
    labels, ambiguous = load_labels(args.labels)

    X, y, kept = [], [], []
    for fid, pts in sorted(series.items()):
        if fid not in labels or len(pts) < MIN_OBS:
            continue
        X.append(featurise(pts))
        y.append(labels[fid])
        kept.append(fid)

    n_ann = y.count("annual")
    n_per = y.count("perennial")

    print(f"fields with time series : {len(series)}")
    print(f"dropped, ambiguous label: {ambiguous}")
    print(f"dropped, too few obs    : {len(series) - len(kept) - ambiguous}")
    print(f"usable labelled fields  : {len(kept)}  ({n_ann} annual, {n_per} perennial)")

    if len(kept) < 20 or n_ann < 5 or n_per < 5:
        print("\nNOT ENOUGH LABELLED DATA TO TRAIN HONESTLY.")
        print("You need at least ~20 fields with both classes represented.")
        print("Widen the sample grid in ndvi_export_grid.js and re-export.")
        print("Do NOT lower this bar to get a number - ship the baseline instead,")
        print("which is exactly what the role spec tells you to do.")
        return 1

    X_tr, X_te, y_tr, y_te, _, id_te = train_test_split(
        X, y, kept, test_size=args.test_size, random_state=args.seed, stratify=y
    )
    print(f"\ntrain: {len(X_tr)}   held-out test: {len(X_te)}")

    rf = RandomForestClassifier(
        n_estimators=300, min_samples_leaf=2,
        random_state=args.seed, class_weight="balanced"
    )
    rf.fit(X_tr, y_tr)
    rf_pred = rf.predict(X_te)
    rf_acc = accuracy_score(y_te, rf_pred)

    # Same held-out fields, run through the P0 lookup classifier.
    base_pred = [baseline_prediction(series[f], args.season) for f in id_te]
    base_acc = accuracy_score(y_te, base_pred)

    order = ["annual", "perennial"]
    print_matrix(y_te, base_pred, order, f"BASELINE (lookup)   accuracy {base_acc:.1%}")
    print_matrix(y_te, rf_pred, order, f"RANDOM FOREST       accuracy {rf_acc:.1%}")

    print("\nper-class detail, Random Forest:")
    print(classification_report(y_te, rf_pred, zero_division=0))

    names = feature_names()
    top = sorted(zip(names, rf.feature_importances_), key=lambda kv: -kv[1])[:8]
    print("most informative features:")
    for n, imp in top:
        print(f"  {n:<12} {imp:.3f}  {'#' * int(imp * 200)}")

    delta = rf_acc - base_acc
    print(f"\nRF vs baseline on held-out data: {delta:+.1%}")
    if delta <= 0.02:
        print("The Random Forest is not beating the lookup table. That is a real")
        print("result, not a failure - report it. With this little training data")
        print("the baseline is the honest thing to ship.")

    print("\nCAVEAT FOR THE SLIDE: labels are perennial-vs-annual, derived from")
    print("independent off-season NDVI. This does not validate wheat vs mustard")
    print("vs gram, which remains unlabelled and baseline-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
