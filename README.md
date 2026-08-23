# Crop Health Risk Detection — SIH26131

**Smart India Hackathon 2025 | Problem Statement SIH26131**
Early detection and management of crop diseases and pest infestations

**Theme:** Agriculture, FoodTech & Rural Development
**PS Category:** Software
**Organization:** Government of Maharashtra
**Team:** GCPC

---

## Problem Statement

Farmers often detect crop diseases and pest infestations too late, leading to avoidable
yield loss. This project builds an image-first, AI-powered decision support system that
detects early disease/pest risk from crop images and gives farmers timely, confidence-aware
advisory — not just a label, but a recommended action.

## Team Structure

| Person | Module | Branch |
|---|---|---|
| Person 1 | Crop Classification | `person1-classification` |
| Person 2 | Crop Health Risk Detection (AI/ML engine) | `person2-remote-sensing` |
| Person 3 | Water / Irrigation Advisory | `person3-water-advisory` |
| Person 4 | Backend & Schema Integration | `person4-backend` |
| Person 5 | Dashboard | `person5-dashboard` |

## Architecture Overview
Field Image + Sowing Date
│
▼
Crop Classification (Person 1) ──► Risk Detection (Person 2)
│ │
▼ ▼
Water Advisory (Person 3) Growth Stage + Risk Type
│ │
└──────────────┬───────────────────┘
▼
Backend Schema (Person 4)
│
▼
Dashboard (Person 5)