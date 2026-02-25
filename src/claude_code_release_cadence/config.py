"""Dynamic color assignment for major version series."""
# [Created with AI: Claude Code with Opus 4.6]

DEFAULT_PALETTE: list[str] = [
    "#f97316",  # orange
    "#3b82f6",  # blue
    "#b975f9",  # purple (lightened for dark-theme AA contrast)
    "#22c55e",  # green
    "#eab308",  # yellow
    "#ec4899",  # pink
    "#14b8a6",  # teal
    "#f43f5e",  # rose
]


def assign_colors(majors_order: list[str]) -> dict[str, str]:
    """Assign hex colors to major version series from the palette.

    Cycles through DEFAULT_PALETTE if there are more series than colors.

    Args:
        majors_order: Ordered list of major version labels.

    Returns:
        Dict mapping major label to hex color string.
    """
    return {
        major: DEFAULT_PALETTE[i % len(DEFAULT_PALETTE)]
        for i, major in enumerate(majors_order)
    }
