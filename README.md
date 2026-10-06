# Wingline & Windows Smooth Cursor Pack

A complete Windows cursor pack in two styles: **Wingline**, with an angled wing-shaped pointer, and **Windows Smooth**, with clean rounded curves. Each style has its own matching icons and comes in white and black themes.

Includes all 17 Windows cursor roles, animated Busy and Working in Background cursors, consistent visible sizes, thin outlines, and sharp 32–256 px variants for different display scales.

## Themes

- **Wingline White** and **Wingline Black** keep the original Wingline design in light and dark palettes.
- **Windows Smooth White** and **Windows Smooth Black** use the separate familiar Windows-style arrow and a complete set of distinct role cursors in light and dark palettes.

## Download and install

[Download the full cursor pack](https://github.com/gxlka/PC-customizable-cursor/releases/latest/download/Wingline-Cursor-Pack.zip), extract it, open your preferred theme folder, and double-click `Install-Wingline.cmd`. It copies the files to your user profile, updates your cursor scheme, and tells Windows to reload the cursors immediately. It does not require administrator access. The `.inf` is included for manual import through Windows; Windows may require selecting Apply in Mouse Properties after an INF install.

The pack contains a preview and `INSTALL.txt` in each theme folder.

## Build and verify

Python 3.11 or later is required.

```powershell
python -m pip install -r requirements.txt
python build.py
python build.py --check
python -m unittest discover -s tests -v
```

The build writes theme folders, individual ZIPs, the combined ZIP, and a combined preview under `dist/`. The check command validates role mappings, installer files, CUR hotspots and bitmap data, ANI frame structure, previews, and ZIP integrity. Windows CI also loads every CUR and ANI through the Windows native cursor API at all seven included sizes, validates the dimensions and hotspots, and releases the ZIPs only after that check passes. Applying the scheme to a desktop is not automated by the build.
