from dataclasses import dataclass


@dataclass(frozen=True)
class CursorRole:
    key: str
    label: str
    glyph: str


@dataclass(frozen=True)
class Theme:
    key: str
    label: str
    fill: str
    edge: str
    wing: str


ROLE_ORDER = (
    CursorRole("arrow", "Normal Select", "arrow"),
    CursorRole("help", "Help Select", "help"),
    CursorRole("appstarting", "Working in Background", "appstarting"),
    CursorRole("wait", "Busy", "wait"),
    CursorRole("crosshair", "Precision Select", "crosshair"),
    CursorRole("ibeam", "Text Select", "ibeam"),
    CursorRole("nwpen", "Handwriting", "pen"),
    CursorRole("no", "Unavailable", "no"),
    CursorRole("sizens", "Vertical Resize", "resize_vertical"),
    CursorRole("sizewe", "Horizontal Resize", "resize_horizontal"),
    CursorRole("sizenwse", "Diagonal Resize 1", "resize_nwse"),
    CursorRole("sizenesw", "Diagonal Resize 2", "resize_nesw"),
    CursorRole("sizeall", "Move", "move"),
    CursorRole("uparrow", "Alternate Select", "up"),
    CursorRole("hand", "Link Select", "hand"),
    CursorRole("pin", "Location Select", "pin"),
    CursorRole("person", "Person Select", "person"),
)

THEMES = {
    "Wingline-White": Theme(
        "Wingline-White",
        "Wingline White",
        fill="#FCFDFF",
        edge="#151922",
        wing="#293241",
    ),
    "Wingline-Black": Theme(
        "Wingline-Black",
        "Wingline Black",
        fill="#171A20",
        edge="#F8F9FC",
        wing="#E5E9F1",
    ),
}
