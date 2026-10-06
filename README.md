# Wingline Cursor Pack

Wingline is a complete native Windows cursor scheme built from the supplied
sketch. Its right-facing pointer keeps the curved rear, with rounded
antialiased edges and a contrasting outline. Other roles use their own shapes
without the normal pointer underneath.

The main pointer uses a compact silhouette with its hotspot on the pointed tip.
The other role shapes are enlarged for visibility at 32 px and use centered
hotspots.

## Themes

- **Wingline White** uses a white body with dark details.
- **Wingline Black** uses a near-black body with a pale outline so it stays
  visible on dark surfaces.

Each theme includes all 17 standard Windows cursor roles: Normal Select, Help
Select, Working in Background, Busy, Precision Select, Text Select,
Handwriting, Unavailable, Vertical Resize, Horizontal Resize, both Diagonal
Resize roles, Move, Alternate Select, Link Select, Location Select, and Person
Select. Busy and Working in Background use looping animations. Static cursors
include 32, 48, 64, and 96 px images with their own hotspots.

## Download and install

Choose one of the ZIPs in `dist/`:

- `Wingline-White.zip` for the light theme.
- `Wingline-Black.zip` for the dark theme.
- `Wingline-Cursor-Pack.zip` for both themes.

Extract the ZIP, open the theme folder, then right-click its `.inf` file and
select **Install**. Windows copies the cursor files into its Cursors folder,
registers the scheme, and sets it as the current scheme for your account.
Approve the Windows permission prompt if one appears.

If Windows does not refresh the pointer immediately, open **Settings →
Bluetooth & devices → Mouse → Additional mouse settings → Pointers**. Choose
**Wingline White** or **Wingline Black** from the Scheme list, then select
**Apply** and **OK**.

The `preview.png` file shows the 32 px designs against light and dark
backgrounds. Each theme ZIP also includes its own preview and `INSTALL.txt`.

## Build and verify

Python 3.11 or later is required.

```powershell
python -m pip install -r requirements.txt
python build.py
python build.py --check
python -m unittest discover -s tests -v
```

The build writes both theme folders, individual ZIPs, the combined ZIP, and a
combined preview under `dist/`. The check command validates the 17 role
mappings and installer paths, referenced files, CUR hotspots and complete
bitmap data, ANI frame structure, preview images, and that every ZIP member
matches its built file.

The pack uses Windows cursor files and an INF installer; it does not install a
separate application. Binary structure and packaging are tested in the build
environment. A live Windows installation is not run by this project build.
