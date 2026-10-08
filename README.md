# curs0r pack

Six cursor styles for Windows, each in white and black. Every set includes 17 animated cursors, clear outlines, and sizes for different display scales.

**[Download curs0r pack](https://github.com/gxlka/PC-customizable-cursor/releases/latest/download/curs0r-pack.zip)**

## Find your style

Sharp Head adds a gentle wiggle and a slow yellow sweep. Click any preview for a closer look.

| White | Black |
| --- | --- |
| **Sharp Head**<br><img src="dist/Sharp-Head-White/preview.png" alt="Sharp Head white cursor set" width="380"> | **Sharp Head**<br><img src="dist/Sharp-Head-Black/preview.png" alt="Sharp Head black cursor set" width="380"> |
| **macOS**<br><img src="dist/macOS-White/preview.png" alt="macOS white cursor set" width="380"> | **macOS**<br><img src="dist/macOS-Black/preview.png" alt="macOS black cursor set" width="380"> |
| **Windows Smooth**<br><img src="dist/Windows-Smooth-White/preview.png" alt="Windows Smooth white cursor set" width="380"> | **Windows Smooth**<br><img src="dist/Windows-Smooth-Black/preview.png" alt="Windows Smooth black cursor set" width="380"> |
| **Hand**<br><img src="dist/Hand-White/preview.png" alt="Hand white cursor set" width="380"> | **Hand**<br><img src="dist/Hand-Black/preview.png" alt="Hand black cursor set" width="380"> |
| **Wingline**<br><img src="dist/Wingline-White/preview.png" alt="Wingline white cursor set" width="380"> | **Wingline**<br><img src="dist/Wingline-Black/preview.png" alt="Wingline black cursor set" width="380"> |
| **I-Beam**<br><img src="dist/I-Beam-White/preview.png" alt="I-Beam white cursor set" width="380"> | **I-Beam**<br><img src="dist/I-Beam-Black/preview.png" alt="I-Beam black cursor set" width="380"> |

## Install

1. Extract the ZIP.
2. Open the folder for your preferred style and color.
3. Double-click `Install-Wingline.cmd`.

Run the installer again after updating. No administrator access or background app is needed. Static `.cur` files are included if you prefer no animation.

<details>
<summary>Build it yourself</summary>

Requires Python 3.11 or later.

```powershell
python -m pip install -r requirements.txt
python build.py
python build.py --check
```

</details>
