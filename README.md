# Wingline Cursor Pack

Five complete Windows cursor styles, each with independent artwork and white and black themes.

- **Wingline:** an angled wing-shaped pointer.
- **Windows Smooth:** a familiar Windows-style arrow with smooth curves.
- **Hand:** a fingertip main pointer, with separate role icons including a chain for links.
- **macOS:** a macOS-inspired arrow and matching icons for Windows.
- **I-Beam:** a text-selection main pointer, with a separate insertion caret and unique role icons.

All ten schemes include 17 distinct roles, animated Busy and Working in Background cursors, consistent visible sizes, thin outlines, and sharp 32–256 px variants for different display scales.

## Download and install

[Download the full cursor pack](https://github.com/gxlka/PC-customizable-cursor/releases/latest/download/Wingline-Cursor-Pack.zip), extract it, open your preferred theme folder, and double-click `Install-Wingline.cmd`. It copies the files to your user profile, updates your cursor scheme, and tells Windows to reload the cursors immediately. It does not require administrator access. The `.inf` is included for manual import through Windows; Windows may require selecting Apply in Mouse Properties after an INF install.

The pack contains a preview and `INSTALL.txt` in each theme folder.

Normal-size animations use small bitmap frames; the installer chooses larger versions when your DPI or cursor size requires them. Animation remains at 30 fps. After installation, Windows handles the cursor files directly; the installer does not keep an app, service, or scheduled task running.

## Build and verify

Python 3.11 or later is required.

```powershell
python -m pip install -r requirements.txt
python build.py
python build.py --check
python -m unittest discover -s tests -v
```

The build writes theme folders, individual ZIPs, the combined ZIP, and a combined preview under `dist/`. The full ZIP is distributed through GitHub Releases because it exceeds GitHub’s repository file limit; individual theme downloads remain in the repository. Repository-only maintenance can reuse a published pack when all cursor sources match its release tag. The check command validates role mappings, installer files, CUR hotspots and bitmap data, ANI frame structure, previews, and ZIP integrity. Windows CI also loads every CUR and ANI through the Windows native cursor API at all seven included sizes, validates the dimensions and hotspots, and releases the ZIPs only after that check passes. Applying the scheme to a desktop is not automated by the build.

## Animated cursor states

Windows and the active application select Text Select over text fields, Link Select over links, Resize at supported edges, and Busy/Working during work. All 17 roles animate at 30 fps. These are state loops, not reactions to individual clicks or keystrokes. Some applications hide the pointer while typing or supply their own cursors. No companion app runs in the background. Static CUR alternatives are included for manual selection through Mouse Properties.

State motion uses a slower 2.13-second cycle with 64 frames at 30 fps, visible at normal 32 px desktop size and rests for 0.4 seconds between loops. Each theme folder contains only its named color; its preview shows that variant only. Files ending in -large.ani use the same colors at a larger resolution, and .cur files are optional static versions. Rerun Install-Wingline.cmd after every update to activate the new .ani files.

A clearer moving sheen now complements the existing shape motion and loading loops in every role. It affects only the fill, preserving the contrasting outlines and click points.
