---
title: Contributing
summary: Issues, pull requests, and what a good contribution looks like for a project that mixes chemistry, CAD and code.
---

## Repository layout

```
openreef/
├── firmware/openreef_analyzer/   Python service: openreef/ package, tests/, deploy/, config.example.yaml
├── hardware/analyzer/cad/        OpenSCAD parts, panels.svg, wiring.svg, bom.csv, make_drawings.py
├── _docs/ _layouts/ _includes/   this website (Jekyll, GitHub Pages)
└── legacy/                       the 2025 colorimeter, unchanged
```

## Before you open a PR

- **Code**: `pytest` passes; new procedures run in the simulator; type hints and docstrings on public functions.
- **Chemistry**: cite the method (APHA number, paper) and include the standards you validated against with the raw curves attached.
- **CAD**: keep parts parametric; export STLs are not committed (they are built from the SCAD files).
- **Docs**: one page per subject under `_docs/`, front matter with `title` and `summary`; preview with `bundle exec jekyll serve`.

## Good first contributions

- Validation data: your calibration curves and side-by-side comparisons with hand kits or ICP.
- A second reagent profile (e.g. the lab-mixed VCl₃ nitrate) characterised end to end.
- A Pi 5 backend (needs a non-pigpio step generator — `rpi-lgpio` or a Pico as a step controller).
- Localised docs.

## Licences

Hardware: CERN-OHL-P v2. Software: MIT. Documentation: CC BY 4.0. Product names (Trident, Hydros, Hanna Checker) belong to their owners; OpenReef is not affiliated with them.
