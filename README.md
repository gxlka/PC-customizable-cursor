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

## Build and verify

Python 3.11 or later is required.

```powershell
python -m pip install -r requirements.txt
python build.py
python build.py --check
python -m unittest discover -s tests -v
```

The build writes theme folders, individual ZIPs, the combined ZIP, and a combined preview under `dist/`. The check command validates role mappings, installer files, CUR hotspots and bitmap data, ANI frame structure, previews, and ZIP integrity. Windows CI also loads every CUR and ANI through the Windows native cursor API at all seven included sizes, validates the dimensions and hotspots, and releases the ZIPs only after that check passes. Applying the scheme to a desktop is not automated by the build.
