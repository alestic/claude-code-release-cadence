"""Dynamic color assignment for major version series."""
# [Created with AI: Claude Code with Opus 4.6]

DARK_PALETTE: list[str] = [
    "#f97316",  # orange
    "#3b82f6",  # blue
    "#b975f9",  # purple (lightened for dark-theme AA contrast)
    "#22c55e",  # green
    "#eab308",  # yellow
    "#ec4899",  # pink
    "#14b8a6",  # teal
    "#f43f5e",  # rose
]

# Darker variants that pass WCAG AA-normal (4.5:1) on #f6f8fa
LIGHT_PALETTE: list[str] = [
    "#c05621",  # orange
    "#2563eb",  # blue
    "#7c3aed",  # purple
    "#15803d",  # green
    "#a16207",  # yellow
    "#be185d",  # pink
    "#0f766e",  # teal
    "#be123c",  # rose
]


def assign_colors(
    majors_order: list[str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Assign hex colors to major version series from both palettes.

    Cycles through each palette if there are more series than colors.

    Args:
        majors_order: Ordered list of major version labels.

    Returns:
        Tuple of (dark_colors, light_colors) dicts mapping major label
        to hex color string.
    """
    dark = {
        major: DARK_PALETTE[i % len(DARK_PALETTE)]
        for i, major in enumerate(majors_order)
    }
    light = {
        major: LIGHT_PALETTE[i % len(LIGHT_PALETTE)]
        for i, major in enumerate(majors_order)
    }
    return dark, light
