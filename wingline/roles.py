from dataclasses import dataclass


@dataclass(frozen=True)
class CursorRole:
    key: str
    label: str
    glyph: str
    registry_value: str


@dataclass(frozen=True)
class Theme:
    key: str
    label: str
    fill: str
    edge: str
    style: str = "wingline"


ROLE_ORDER = (
    CursorRole("arrow", "Normal Select", "arrow", "Arrow"),
    CursorRole("help", "Help Select", "help", "Help"),
    CursorRole("appstarting", "Working in Background", "appstarting", "AppStarting"),
    CursorRole("wait", "Busy", "wait", "Wait"),
    CursorRole("crosshair", "Precision Select", "crosshair", "Crosshair"),
    CursorRole("ibeam", "Text Select", "ibeam", "IBeam"),
    CursorRole("nwpen", "Handwriting", "pen", "NWPen"),
    CursorRole("no", "Unavailable", "no", "No"),
    CursorRole("sizens", "Vertical Resize", "resize_vertical", "SizeNS"),
    CursorRole("sizewe", "Horizontal Resize", "resize_horizontal", "SizeWE"),
    CursorRole("sizenwse", "Diagonal Resize 1", "resize_nwse", "SizeNWSE"),
    CursorRole("sizenesw", "Diagonal Resize 2", "resize_nesw", "SizeNESW"),
    CursorRole("sizeall", "Move", "move", "SizeAll"),
    CursorRole("uparrow", "Alternate Select", "up", "UpArrow"),
    CursorRole("hand", "Link Select", "hand", "Hand"),
    CursorRole("pin", "Location Select", "pin", "Pin"),
    CursorRole("person", "Person Select", "person", "Person"),
)

THEMES = {
    "Wingline-White": Theme(
        "Wingline-White",
        "Wingline White",
        fill="#FCFDFF",
        edge="#151922",
    ),
    "Wingline-Black": Theme(
        "Wingline-Black",
        "Wingline Black",
        fill="#171A20",
        edge="#F8F9FC",
    ),
    "Windows-Smooth-White": Theme(
        "Windows-Smooth-White",
        "Windows Smooth White",
        fill="#FCFDFF",
        edge="#151922",
        style="windows",
    ),
    "Windows-Smooth-Black": Theme(
        "Windows-Smooth-Black",
        "Windows Smooth Black",
        fill="#171A20",
        edge="#F8F9FC",
        style="windows",
    ),
}
