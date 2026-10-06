# Wingline Cursor Pack

Wingline is a complete native Windows cursor scheme built from the supplied sketch. The main pointer uses its upper corner as the click hotspot. The white theme has rounded corners and a curved rear; the black theme uses a pale outline for visibility on dark surfaces. Other roles use their own shapes without the normal pointer underneath.

Both themes include all 17 standard Windows cursor roles. Busy and Working in Background use looping animations. Static cursors contain multiple Windows size variants from 32 px through 256 px, rendered with 8x supersampling and premultiplied alpha for clean edges at high DPI. The preview uses larger 48 px renderings so the role artwork is easier to inspect.

## Themes

- **Wingline White** uses a white body with dark details.
- **Wingline Black** uses a near-black body with a pale outline.

## Download and install

Choose a ZIP in `dist/`, extract it, open the theme folder, and double-click `Install-Wingline.cmd`. It copies the files to your user profile, updates your cursor scheme, and tells Windows to reload the cursors immediately. It does not require administrator access. The `.inf` is included for manual import through Windows; Windows may require selecting Apply in Mouse Properties after an INF install.

The pack contains a larger preview and `INSTALL.txt` in each theme folder.

## Build and verify

Python 3.11 or later is required.

```powershell
python -m pip install -r requirements.txt
python build.py
python build.py --check
python -m unittest discover -s tests -v
```

The build writes theme folders, individual ZIPs, the combined ZIP, and a combined preview under `dist/`. The check command validates role mappings, installer files, CUR hotspots and bitmap data, ANI frame structure, previews, and ZIP integrity. A live Windows installation is not run by the project build.
