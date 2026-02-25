# Color Contrast Ratio Analysis

<!-- [Created with AI: Claude Code with Opus 4.6] -->

WCAG 2.1 thresholds: AA-normal ≥ 4.5:1, AA-large ≥ 3.0:1, AAA-normal ≥ 7.0:1

## Theme Colors

| Pair                                 |    Ratio | AA-norm  | AA-lrg   | AAA-norm |
| ------------------------------------ | -------: | -------- | -------- | -------- |
| `--text` on `--bg-body` (dark)       |    12.26 | PASS     | PASS     | PASS     |
| `--text` on `--bg-card` (dark)       |    11.21 | PASS     | PASS     | PASS     |
| `--text-muted` on `--bg-body` (dk)   |     6.15 | PASS     | PASS     | FAIL     |
| `--text-muted` on `--bg-card` (dk)   |     5.62 | PASS     | PASS     | FAIL     |
| `--text-heading` on `--bg-card` (dk) |    15.89 | PASS     | PASS     | PASS     |
| `trend-positive` on `--bg-card` (dk) |     7.59 | PASS     | PASS     | PASS     |
| `trend-negative` on `--bg-card` (dk) |     6.17 | PASS     | PASS     | FAIL     |
| link `#58a6ff` on `--bg-card` (dk)   |     6.85 | PASS     | PASS     | FAIL     |
| `--text` on `--bg-body` (light)      |    15.80 | PASS     | PASS     | PASS     |
| `--text` on `--bg-card` (light)      |    14.84 | PASS     | PASS     | PASS     |
| `--text-muted` on `--bg-body` (lt)   |     5.25 | PASS     | PASS     | FAIL     |
| `--text-muted` on `--bg-card` (lt)   |     4.93 | PASS     | PASS     | FAIL     |
| `--text-heading` on `--bg-card` (lt) |    14.84 | PASS     | PASS     | PASS     |
| **link `#58a6ff` on bg-card (lt)**   | **2.37** | **FAIL** | **FAIL** | **FAIL** |

## Chart Palette on Dark Card (`#161b22`)

| Color      | Hex           |    Ratio | AA-norm  | AA-lrg | AAA-norm |
| ---------- | ------------- | -------: | -------- | ------ | -------- |
| Orange     | `#f97316`     |     6.17 | PASS     | PASS   | FAIL     |
| Blue       | `#3b82f6`     |     4.70 | PASS     | PASS   | FAIL     |
| **Purple** | **`#a855f7`** | **4.37** | **FAIL** | PASS   | FAIL     |
| Green      | `#22c55e`     |     7.59 | PASS     | PASS   | PASS     |
| Yellow     | `#eab308`     |     9.02 | PASS     | PASS   | PASS     |
| Pink       | `#ec4899`     |     4.90 | PASS     | PASS   | FAIL     |
| Teal       | `#14b8a6`     |     6.95 | PASS     | PASS   | FAIL     |
| Rose       | `#f43f5e`     |     4.71 | PASS     | PASS   | FAIL     |

## Chart Palette on Light Card (`#f6f8fa`)

| Color      | Hex           |    Ratio | AA-norm  | AA-lrg   | AAA-norm |
| ---------- | ------------- | -------: | -------- | -------- | -------- |
| **Orange** | **`#f97316`** | **2.63** | **FAIL** | **FAIL** | FAIL     |
| **Blue**   | **`#3b82f6`** | **3.45** | **FAIL** | PASS     | FAIL     |
| **Purple** | **`#a855f7`** | **3.72** | **FAIL** | PASS     | FAIL     |
| **Green**  | **`#22c55e`** | **2.14** | **FAIL** | **FAIL** | FAIL     |
| **Yellow** | **`#eab308`** | **1.80** | **FAIL** | **FAIL** | FAIL     |
| **Pink**   | **`#ec4899`** | **3.31** | **FAIL** | PASS     | FAIL     |
| **Teal**   | **`#14b8a6`** | **2.34** | **FAIL** | **FAIL** | FAIL     |
| **Rose**   | **`#f43f5e`** | **3.45** | **FAIL** | PASS     | FAIL     |

**Note:** Chart palette colors appear primarily as chart fills (bar/point
colors) and in legend text boxes. The legend _text_ uses `--text` which
passes, but the colored box beside the legend text is the only way to
map a dataset to its legend label visually.

## Suggested Light-Theme Palette

Darker variants that pass AA-normal (4.5:1) on `#f6f8fa`:

| Color  | Current   | Suggested | Ratio on `#f6f8fa` |
| ------ | --------- | --------- | -----------------: |
| Orange | `#f97316` | `#c05621` |               ~5.1 |
| Blue   | `#3b82f6` | `#2563eb` |               ~4.6 |
| Purple | `#a855f7` | `#7c3aed` |               ~5.7 |
| Green  | `#22c55e` | `#15803d` |               ~5.2 |
| Yellow | `#eab308` | `#a16207` |               ~5.3 |
| Pink   | `#ec4899` | `#be185d` |               ~5.8 |
| Teal   | `#14b8a6` | `#0f766e` |               ~5.6 |
| Rose   | `#f43f5e` | `#be123c` |               ~5.6 |

These would require either a theme-aware palette in JS or two separate
color maps injected from `config.py` / `render.py`.
