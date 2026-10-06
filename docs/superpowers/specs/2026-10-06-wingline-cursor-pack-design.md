# Wingline Cursor Pack Design

**Date:** 2026-10-06  
**Status:** Approved; implementation complete
**Repository:** `gxlka/PC-customizable-cursor`

## Goal

Create a polished Windows cursor pack based on the supplied sketch. The main pointer should retain the sketch's upper-pointed silhouette, with smooth corners and a subtle curve at the rear. The pack must include the other standard Windows cursor roles so it installs as a complete scheme rather than a single pointer. Each non-default role uses its own cursor shape without the normal pointer underneath; no trailing wing lines are drawn.

## Visual system

Two themes share the same shapes for each cursor role:

- **Wingline White:** white body and dark defining outline.
- **Wingline Black:** near-black body and pale defining outline.

The contrasting edge should keep each cursor legible over both light and dark backgrounds. The normal pointer should use a compact silhouette with its hotspot on the pointed tip. Other role artwork is drawn on its own, enlarged for visibility at 32 px, and centered on its hotspot.

## Cursor roles

Each theme covers these 17 Windows roles: Normal Select (`arrow`), Help Select (`help`), Working in Background (`appstarting`), Busy (`wait`), Precision Select (`crosshair`), Text Select (`ibeam`), Handwriting (`nwpen`), Unavailable (`no`), Vertical Resize (`sizens`), Horizontal Resize (`sizewe`), Diagonal Resize 1 (`sizenwse`), Diagonal Resize 2 (`sizenesw`), Move (`sizeall`), Alternate Select (`uparrow`), Link Select (`hand`), Location Select (`pin`), and Person Select (`person`).

## Build and package

Keep editable vector-style source in the repository and use a Python build script to render the cursor assets. Generate multi-size static `.cur` files, animated `.ani` files for Busy and Working in Background, one `.inf` installer per theme, and a preview sheet. The build should produce individual theme ZIPs and a combined ZIP under `dist/`. Include a README with build instructions and the Windows install steps. The pack will use Windows' built-in cursor installer and will not add a separate running application.

## Validation

The build/check command should verify that both themes contain all 17 role mappings; every INF reference resolves to a packaged cursor; static cursor hotspots are within their images; animated cursor containers are well-formed; and all ZIP archives pass an integrity check. A live Windows installation check is outside the available build environment and must not be claimed unless performed separately.
