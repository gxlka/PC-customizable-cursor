# Wingline Cursor Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and package two complete, high-contrast Wingline cursor schemes for Windows.

**Architecture:** Keep the editable vector-style drawing and role definitions in a small Python package. Render at high resolution and downsample to 32, 48, 64, and 96 px CUR entries; encode Busy and Working in Background as RIFF ANI animations. A build entry point then generates role mappings, INF installers, previews, and ZIPs from the same manifest.

**Tech Stack:** Python 3.11+, Pillow for RGBA rasterization, Python standard library for CUR/ANI encoding, INF/ZIP creation, and unittest.

**Spec:** `docs/superpowers/specs/2026-10-06-wingline-cursor-pack-design.md`

## Global Constraints

- The main pointer should retain the sketch's right-facing silhouette, with smooth corners, a subtle curve at the rear, and small wing-like lines trailing from its left side.
- Each theme covers these 17 Windows roles: Normal Select (`arrow`), Help Select (`help`), Working in Background (`appstarting`), Busy (`wait`), Precision Select (`crosshair`), Text Select (`ibeam`), Handwriting (`nwpen`), Unavailable (`no`), Vertical Resize (`sizens`), Horizontal Resize (`sizewe`), Diagonal Resize 1 (`sizenwse`), Diagonal Resize 2 (`sizenesw`), Move (`sizeall`), Alternate Select (`uparrow`), Link Select (`hand`), Location Select (`pin`), and Person Select (`person`).
- Generate multi-size static `.cur` files, animated `.ani` files for Busy and Working in Background, one `.inf` installer per theme, and a preview sheet.
- The build should produce individual theme ZIPs and a combined ZIP under `dist/`.
- Include a README with build instructions and the Windows install steps.
- The pack will use Windows' built-in cursor installer and will not add a separate running application.
- The build/check command should verify that both themes contain all 17 role mappings; every INF reference resolves to a packaged cursor; static cursor hotspots are within their images; animated cursor containers are well-formed; and all ZIP archives pass an integrity check.
- A live Windows installation check is outside the available build environment and must not be claimed unless performed separately.

## Review Focus

- **Tiny-size readability:** role shape and wing marks remain visible at 32 px; pin representative preview samples in the artwork tests and inspect the final sheet.
- **Invalid canvas size:** unsupported sizes fail clearly before rendering or CUR encoding; cover in the artwork/CUR tests.
- **Hotspot outside the image:** each hotspot remains inside every CUR entry; cover in CUR tests.
- **Malformed animation sequence:** ANI frame and step counts, references, and RIFF lengths agree; cover in ANI tests.
- **Broken scheme package:** an INF cannot name a missing cursor and each ZIP contains its installer and mapped files; cover in package tests.

---

### Task 1: Define roles, themes, and cursor artwork

**Files:**
- Create: `requirements.txt`
- Create: `wingline/__init__.py`
- Create: `wingline/roles.py`
- Create: `wingline/artwork.py`
- Create: `tests/test_artwork.py`

**Interfaces:**
- `CursorRole(key: str, label: str, glyph: str)` stores a Windows role ID, display label, and artwork symbol.
- `Theme(key: str, label: str, fill: str, edge: str, wing: str)` stores a stable theme key and its three palette colors.
- `ROLE_ORDER: tuple[CursorRole, ...]` defines the 17 ordered roles in the spec.
- `THEMES: dict[str, Theme]` contains keys `Wingline-White` and `Wingline-Black`.
- `render_cursor(role: CursorRole, theme: Theme, size: int, frame: int = 0) -> tuple[Image.Image, tuple[int, int]]` returns an RGBA image and its click hotspot.
- The renderer accepts only 32, 48, 64, or 96 px. It draws at 4x resolution before downsampling. The rightmost arrow tip is the `arrow` hotspot. Animated role frames use indices 0–7.

- [ ] **Step 1: Write failing role and artwork tests.** Assert the ordered IDs are exactly the 17 in the spec; every role/theme renders a non-empty RGBA image at 32 px; images preserve transparent background; hotspots fit the canvas; unsupported sizes raise `ValueError`.
- [ ] **Step 2: Run `python -m unittest discover -s tests -p test_artwork.py -v`.** Expected: FAIL because the role manifest and renderer are not implemented.
- [ ] **Step 3: Implement role metadata and vector-style drawing.** Use shared geometry for the arrow and theme outlines; add recognizable role-specific marks for help, busy/loading, crosshair, text, pen, unavailable, resize, move, alternate select, link, location, and person.
- [ ] **Step 4: Run `python -m unittest discover -s tests -p test_artwork.py -v`.** Expected: PASS; inspect the test-generated 32 px role sheet for clipped marks and legibility.
- [ ] **Step 5: Commit the role manifest and artwork renderer.**

### Task 2: Encode multi-size CUR files

**Files:**
- Create: `wingline/cur.py`
- Create: `tests/test_cur.py`

**Interfaces:**
- `encode_cur(images: Sequence[tuple[Image.Image, tuple[int, int]]]) -> bytes` writes one CUR container from images at 32, 48, 64, and 96 px.
- Each image entry stores its own in-bounds hotspot and a 32-bit color DIB plus transparency mask.

- [ ] **Step 1: Write failing CUR tests.** Independently parse the directory and assert four sizes, correct hotspot values, valid offsets/lengths, and transparent pixels encoded in the mask; assert out-of-bounds hotspots are rejected.
- [ ] **Step 2: Run `python -m unittest discover -s tests -p test_cur.py -v`.** Expected: FAIL because `encode_cur` is missing.
- [ ] **Step 3: Implement CUR directory and DIB encoding in `wingline/cur.py`.**
- [ ] **Step 4: Run `python -m unittest discover -s tests -p test_cur.py -v`.** Expected: PASS for valid icons and rejected invalid input.
- [ ] **Step 5: Commit the CUR encoder and tests.**

### Task 3: Encode animated ANI cursors

**Files:**
- Create: `wingline/ani.py`
- Create: `tests/test_ani.py`

**Interfaces:**
- `encode_ani(frames: Sequence[bytes], frame_jiffies: int = 7) -> bytes` wraps eight single-size CUR frames in a looping RIFF ANI file.
- The Busy animation rotates a small wing accent; Working in Background sweeps the accent across the same cursor silhouette.

- [ ] **Step 1: Write failing ANI tests.** Parse the output and assert RIFF/ACON identity, declared frame and step counts of 8, ordered sequence 0–7, seven-jiffy rates, embedded CUR frames, and consistent chunk lengths. Reject an empty frame list.
- [ ] **Step 2: Run `python -m unittest discover -s tests -p test_ani.py -v`.** Expected: FAIL because `encode_ani` is missing.
- [ ] **Step 3: Implement RIFF ANI encoding in `wingline/ani.py`.**
- [ ] **Step 4: Run `python -m unittest discover -s tests -p test_ani.py -v`.** Expected: PASS, including boundary and length checks.
- [ ] **Step 5: Commit the ANI encoder and tests.**

### Task 4: Build installers, previews, and downloadable packs

**Files:**
- Create: `build.py`
- Create: `wingline/package.py`
- Create: `tests/test_package.py`
- Create: `README.md`
- Create: `.gitignore`
- Generate: `dist/Wingline-White.zip`
- Generate: `dist/Wingline-Black.zip`
- Generate: `dist/Wingline-Cursor-Pack.zip`
- Generate: `dist/preview.png`

**Interfaces:**
- `build.py` runs `python build.py` to generate outputs and `python build.py --check` to verify them without rebuilding.
- `build_theme(theme: Theme, output_dir: Path) -> list[Path]` writes the 17 role mappings, CUR/ANI assets, INF, and per-theme preview.
- The combined ZIP contains both named theme directories; the individual ZIPs each contain one theme's INF, cursor assets, and install notes.

- [ ] **Step 1: Write failing package tests.** Assert every theme's INF maps all 17 roles in Windows order, all referenced files exist, the two theme ZIPs contain their INF and assets, and all three ZIPs pass `ZipFile.testzip()`.
- [ ] **Step 2: Run `python -m unittest discover -s tests -p test_package.py -v`.** Expected: FAIL because the packager and build entry point are missing.
- [ ] **Step 3: Implement INF generation, previews, ZIP output, and build/check commands.** Use the role manifest as the single source of truth. Document right-click install steps and the Windows cursor-scheme selection step in README.
- [ ] **Step 4: Run `python build.py`, then `python build.py --check`, then `python -m unittest discover -s tests -v`.** Expected: all builds complete; every mapping, binary structure, and archive check passes.
- [ ] **Step 5: Review the generated preview sheet and both theme ZIP contents, then commit source, tests, documentation, and verified outputs.**
