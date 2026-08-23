# ML Methodology — Crop Classification (Person 1)

Notes for Person 6's slide. Everything below is measured, not estimated.
Caveats are in the text on purpose — they are what makes the numbers credible.

---

## One-line summary

Crop type is identified by matching each field's **multi-temporal NDVI curve**
against reference crop phenology profiles, with a Random Forest upgrade
validated against labels derived from satellite observations the classifier
never sees.

---

## Inputs

| | |
|---|---|
| Source | Sentinel-2 L2A (harmonized), 10m, via Google Earth Engine |
| Window | 1 Nov 2024 – 15 Apr 2025 (rabi) |
| Cloud handling | Scene Classification Layer; only vegetation / bare / water / unclassified pixels retained |
| Per field | Mean NDVI per acquisition date, ~28 dates after cloud loss |
| Field size | ~130m boxes, roughly one parcel |

## Output

One record per field, merged into the team schema:

`field_id`, `crop`, `confidence_or_score`, `growth_stage`

Every input field always appears in the output. Failures return `"Unknown"`
with confidence 0.0 rather than being dropped, so the downstream pipeline never
encounters a gap.

---

## Approach 1 — Baseline: temporal profile matching (P0, shipped)

Single-date NDVI thresholds **cannot** separate these crops — wheat, mustard
and gram overlap heavily in value on any given date. What separates them is the
*shape* of the curve over the season.

Each field's observed series is fitted against a library of reference phenology
profiles, searching ±35 days of sowing-date offset to absorb the fact that
farmers in one district do not all sow on the same day. Best fit wins.

Requires no training data. Runs on the Python standard library alone.

Two byproducts that other modules consume:
- **Estimated sowing offset** — the best-fit time shift is itself a sowing-date estimate
- **Growth stage** — derived from where the latest observation sits on the matched curve, fed to the moisture-stress module

## Approach 2 — Random Forest (P1, validated)

300 trees on fixed-length features: NDVI resampled to a 10-day grid, plus
amplitude, min, max, mean, peak timing and seasonal integral.

---

## The labelling problem, and how it was solved

**There was no labelled crop data.** Training on the baseline's own predictions
would only teach the model to imitate the lookup table, and any accuracy from
that would be meaningless.

Solution: labels come from a **time window the classifier never reads**.

The classifier sees November–April only. In **May–June** the rabi crop has been
harvested and kharif has not established, so:

- annual crops (wheat, mustard, gram) → bare soil, NDVI ≈ 0.15–0.25
- sugarcane, a 12–18 month crop → still standing, NDVI ≈ 0.5–0.75

Off-season NDVI therefore gives an **independent** perennial-vs-annual label.
Fields falling between the thresholds were dropped rather than guessed at.

---

## Results (held-out test sets, 5 random splits)

| | Baseline | Random Forest |
|---|---|---|
| Mean accuracy | **76.3%** | **96.4%** |
| Range across splits | 63.6 – 90.9% | 90.9 – 100% |

The Random Forest wins or ties on every split, and is far more stable.

**The more interesting finding is the error pattern.** Every baseline error was
a perennial misclassified as annual — none in the other direction. The lookup
classifier has a systematic blind spot: it under-detects sugarcane. In
Muzaffarnagar district, India's densest sugarcane belt, that is a material
failure, and it was invisible until independent labels existed.

The model's most informative features were mid-December to January NDVI —
exactly the period when sugarcane stands green and annual crops have barely
emerged. It recovered the agronomically correct discriminator unsupervised.

---

## Limitations (state these; do not let a judge find them)

1. **n = 36 labelled fields, 11 held out per split.** A 100% score on 11 samples has a confidence interval reaching roughly 70%. The multi-split mean is the defensible number, not the best single run.
2. **Validation covers perennial vs annual only.** Wheat vs mustard vs gram has no independent label and is unvalidated. Those calls rest on the profile library alone.
3. **Profiles are anchored to western UP timing.** Punjab and Haryana run 2–3 weeks earlier. Moving region means re-anchoring the day numbers.
4. **One season, one district.** No cross-year or cross-region test.

---

## How it scales

More training data is the direct path: the RF already outperforms the lookup at
36 labelled fields, and the same off-season labelling trick generates labels
automatically anywhere sugarcane is grown — no fieldwork required.

More crop types need either reference profiles (roughly ten anchor points each,
an afternoon of agronomic reference work) or labelled examples. The rabi and
kharif libraries are separate tables, so adding a season is additive.

The single highest-value upgrade is **Sentinel-1 SAR**, which sees through
cloud. Optical NDVI already loses about a quarter of acquisitions to cloud, and
in a kharif monsoon season that fraction is far worse.
