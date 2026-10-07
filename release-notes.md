# Wingline Cursor Pack — Animated States

Five distinct styles: Wingline, Windows Smooth, Hand, macOS, and I-Beam, each in light and dark themes.

All 17 cursor roles now animate at 30 fps. Normal selection, text selection, links, resizing, precision, help, and other states use a subtle moving sheen, preserving their shape, thin outlines, and click hotspots. Busy and Working keep their distinct progress animations.

Windows selects the current role in applications that use system cursors. Loops play while that role is visible; they do not react to individual clicks or keystrokes. No background app or service is needed. The installer selects smaller 64 px source animations for normal sizes, with 256 px versions for larger settings. Static CUR alternatives are included for manual selection.

Download Wingline-Cursor-Pack.zip, extract a theme, and run Install-Wingline.cmd. Re-run the installer to update an existing installation.

The release requires passing artwork and loop tests, archive integrity, installer checks, native Windows loading of every asset and frame, and a native drawing benchmark covering all 17 roles.

## Hand pointer refinement

The Hand family's main pointer has a slimmer rounded index finger, staggered folded knuckles, a curved thumb and a softer palm. It keeps its original fingertip click point, visible size, thin outline and smooth state animation. All loop continuity checks now cover both light and dark themes, alongside native loading checks of every exported frame and the all-role drawing benchmark.
