# Wingline Cursor Pack

Wingline is a complete native Windows cursor pack with two separate visual styles. Wingline keeps its own angled arrow design. Windows Smooth adds a familiar upper-left Windows arrow with a rounded, antialiased edge and the click hotspot at its tip. Both styles have white and black themes. Every role in Windows Smooth has independent vector artwork: none of its role icons reuse Wingline artwork. Within each scheme, all 17 roles have distinct silhouettes.

Every Windows cursor role has its own artwork; none reuse the main pointer. Busy and Working in Background use looping animations. Static cursors contain multiple Windows size variants from 32 px through 256 px, rendered with 8x supersampling and premultiplied alpha for clean edges at high DPI. Role artwork is fitted to a fixed visible extent of 24 px on a 32 px canvas (36 px on a 48 px canvas), with thin contrast edges. Each native size is rendered independently; the build also checks every animation frame and checks for duplicate silhouettes between schemes. The previews show larger 48 px renders.

## Themes

- **Wingline White** and **Wingline Black** keep the original Wingline design in light and dark palettes.
- **Windows Smooth White** and **Windows Smooth Black** use the separate familiar Windows-style arrow and a complete set of distinct role cursors in light and dark palettes.

## Download and install

Choose the ZIP for the theme you want in `dist/`, extract it, open the theme folder, and double-click `Install-Wingline.cmd`. It copies the files to your user profile, updates your cursor scheme, and tells Windows to reload the cursors immediately. It does not require administrator access. The `.inf` is included for manual import through Windows; Windows may require selecting Apply in Mouse Properties after an INF install.

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
