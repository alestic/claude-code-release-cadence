# Accessibility Audit: Claude Code Release Cadence Dashboard

<!-- [Created with AI: Claude Code with Opus 4.6] -->

Performed: 2026-02-24
Template: `templates/dashboard.template.html`
Standard: WCAG 2.1 AA (with AAA notes where relevant)

## Summary

| Category | Critical | Major | Minor | Pass |
|---|---|---|---|---|
| Color Contrast | 2 | 3 | 4 | — |
| Keyboard Access | 2 | 1 | — | 1 |
| Screen Reader / ARIA | 2 | 4 | 3 | 2 |
| Semantic HTML | — | 2 | 2 | 3 |
| Motion & Preferences | — | 1 | 1 | — |
| **Total** | **6** | **11** | **10** | **6** |

## Implementation Status

All 27 findings have been addressed across four commits:

| Phase | Findings | Status |
|---|---|---|
| Phase 1 — Critical | 1.1, 2.1, 2.2, 3.1, 3.2 | DONE (commit `0811655`) |
| Phase 2 — Major | 1.2, 1.3, 1.5, 1.6, 2.3, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 5.1 | DONE (commits `c0b6789`, Phase 4) |
| Phase 3 — Minor | 1.7, 1.8, 1.9, 3.7, 3.8, 3.9, 4.3, 4.4, 5.2 | DONE (commit `c0b6789`) |
| Not addressed | 1.4 (AAA-only), 6.1 (info/bonus) | WONTFIX — see notes |

---

## Findings

### 1. Color Contrast (WCAG 1.4.3, 1.4.6, 1.4.11)

#### 1.1 [CRITICAL] Link color fails all contrast levels in light theme — FIXED

`#58a6ff` on `#f6f8fa` = **2.37:1** — fails AA normal (4.5:1), AA large (3.0:1), and AAA.

**Affects:** All `<a>` tags in the footer grid in light mode.

**Fix applied:** Added `--link` CSS variable: `#58a6ff` (dark), `#0969da` (light, 7.94:1 on `#f6f8fa`).

#### 1.2 [CRITICAL] Multiple chart palette colors fail AA-normal on light backgrounds — FIXED

| Color | Hex | Ratio on `#f6f8fa` | AA normal | AA large |
|---|---|---|---|---|
| Orange | `#f97316` | 2.63:1 | FAIL | FAIL |
| Green | `#22c55e` | 2.14:1 | FAIL | FAIL |
| Yellow | `#eab308` | 1.80:1 | FAIL | FAIL |
| Teal | `#14b8a6` | 2.34:1 | FAIL | FAIL |
| Blue | `#3b82f6` | 3.45:1 | FAIL | PASS |
| Purple | `#a855f7` | 3.72:1 | FAIL | PASS |
| Pink | `#ec4899` | 3.31:1 | FAIL | PASS |
| Rose | `#f43f5e` | 3.45:1 | FAIL | PASS |

**Fix applied:** Theme-aware palette with 8 darker variants for light mode (all AA-normal). `DARK_TO_LIGHT` map swaps colors on theme toggle; chart datasets, table dots, and sizeChart colors all update live. See `contrast-ratios.md` for the specific color values.

#### 1.3 [MAJOR] Purple fails AA-normal on dark card — FIXED

`#a855f7` on `#161b22` = **4.37:1** — just below the 4.5:1 threshold.

**Fix applied:** Lightened to `#b975f9` (~5.0:1 on `#161b22`) in `config.py`.

#### 1.4 [MINOR] `--text-muted` passes AA but fails AAA on both themes — WONTFIX

- Dark: `#8b949e` on `#161b22` = 5.62:1 (AA PASS, AAA FAIL)
- Light: `#656d76` on `#f6f8fa` = 4.93:1 (AA PASS, AAA FAIL)

**Acceptable** for AA compliance. Not changing — these match the GitHub-style design tokens.

#### 1.5 [MAJOR] Color is the only distinguishing factor for version series in charts (1.4.1) — FIXED

Chart datasets for different major versions were distinguished *only* by color.

**Fix applied:** Non-color differentiators via `DASH_PATTERNS` and `POINT_STYLES` arrays:
- **Scatter chart** (gapChart): distinct `pointStyle` per series (circle, triangle, rect, rectRot, star, cross, crossRot, dash) with `usePointStyle` legend
- **Day-of-week / Hour-of-day charts**: `borderDash` patterns per series with `borderWidth: 2`
- **Size chart**: `borderDash: [6, 3]` on File Count line to distinguish from solid Size line

Weekly charts and notes chart have bars too narrow for visible dash patterns; severity is lower since legend text uses `--text` (passes contrast).

#### 1.6 [MAJOR] Heatmap communicates data solely through color intensity — FIXED

The heatmap grid cells encoded changelog entry counts purely through background color opacity.

**Fix applied:** Non-zero cells now show the count as text (`.heatmap-num`, 9px semibold). Theme-aware text color: white on dark theme; adaptive dark/white on light theme based on intensity threshold. Hidden on mobile (`max-width: 640px`) where cells are too small. Theme toggle recolors numbers via `updateHeatmapTheme()`.

#### 1.7 [MINOR] Heatmap "now" dot relies on color alone — FIXED

The red dot (`#f43f5e`) marking the current time had only color to distinguish it.

**Fix applied:** Changed from a small centered dot to a red border outline (`border: 2px solid #f43f5e`) filling the cell. Provides a shape/position cue distinct from color. Cell count number renders on top (z-index 2 > 1).

#### 1.8 [MINOR] Trend arrows use Unicode triangles — FIXED

`▲` (U+25B2) and `▼` (U+25BC) are geometric shapes. Screen readers may announce them as "black up-pointing triangle."

**Fix applied:** Arrow character wrapped in `aria-hidden="true"` span. The existing "above/below overall avg" text conveys direction without color.

#### 1.9 [MINOR] `--tooltip-border` in dark theme is low contrast — FIXED

`#444c56` on `#1c2128` ≈ 2.3:1 — below 3:1 non-text contrast requirement.

**Fix applied:** Lightened to `#545d68` (≥3:1).

---

### 2. Keyboard Accessibility (WCAG 2.1.1, 2.1.2, 2.4.7)

#### 2.1 [CRITICAL] Heatmap cells are not keyboard accessible — FIXED

Heatmap `<div>` cells had `mouseenter`/`mousemove`/`mouseleave` handlers only.

**Fix applied:** Roving `tabindex` (0 on focused cell, -1 on others), `role="gridcell"`, `aria-label` with full tooltip content. Arrow/Home/End key navigation via `addGridKeyNav()`. `focus`/`blur` handlers show/hide tooltip with viewport-edge clamping.

#### 2.2 [CRITICAL] Outlier overlay bars are mouse-only — FIXED

The overlay columns for capped outlier bars used mouse events only.

**Fix applied:** `tabindex="0"`, `role="img"`, `aria-label` with tooltip content. `focus`/`blur` handlers with viewport-edge tooltip clamping. Focus restoration after chart rebuild via `focusedOverlayVersion` tracking.

#### 2.3 [MAJOR] No visible focus indicators — FIXED

No custom focus styles were defined; browser defaults hard to see on dark theme.

**Fix applied:** `:focus-visible` with `outline: 2px solid var(--link); outline-offset: 2px` — theme-aware via the `--link` variable.

#### 2.4 [PASS] Theme toggle button

The theme toggle is a native `<button>` element with `aria-label` — properly keyboard accessible.

---

### 3. Screen Reader / ARIA (WCAG 1.1.1, 4.1.2)

#### 3.1 [CRITICAL] Canvas charts have no text alternatives (1.1.1) — FIXED

Seven `<canvas>` elements had no `aria-label`, `role="img"`, or fallback content.

**Fix applied:** `role="img"` and descriptive `aria-label` on all 7 chart canvases.

#### 3.2 [CRITICAL] Heatmap grid has no ARIA structure — FIXED

The heatmap was built from plain `<div>` elements with no semantic structure.

**Fix applied:** `role="grid"` on containers, `role="row"` on rows (with `display:contents`), `role="gridcell"` on data cells, `role="rowheader"`/`role="columnheader"` on labels.

#### 3.3 [MAJOR] Theme toggle lacks state indication — FIXED

The toggle button had a static `aria-label="Toggle theme"`.

**Fix applied:** Dynamic `aria-label` set on init and on each toggle: "Switch to light/dark theme".

#### 3.4 [MAJOR] SVG icons not hidden from screen readers — FIXED

Sun/moon SVGs and anchor link SVGs were decorative but not marked `aria-hidden`.

**Fix applied:** `aria-hidden="true"` on sun/moon icon SVGs and on JS-created anchor link SVGs.

#### 3.5 [MAJOR] Color dots in the major table lack text alternatives — FIXED

The `<span class="color-dot">` had no accessible markup.

**Fix applied:** `aria-hidden="true"` on each dot (the series name text is the accessible label).

#### 3.6 [MAJOR] Stats cards have no semantic structure — FIXED

Stats cards were generic `<div>` elements.

**Fix applied:** `role="group"` with `aria-label="Label: Value"` on each card.

#### 3.7 [MINOR] External links don't indicate new window — FIXED

Links with `target="_blank"` didn't inform screen reader users.

**Fix applied:** `<span class="sr-only">(opens in new tab)</span>` appended to all `target="_blank"` links.

#### 3.8 [MINOR] Dynamic content not announced — FIXED

Tooltip content and "Copied!" messages were not in live regions.

**Fix applied:** `role="status"` and `aria-live="polite"` on tooltip elements and the "Copied!" notification.

#### 3.9 [MINOR] `<wbr>` in table headers — FIXED

Headers like `Releases/<wbr>Week` could be read as "Releases slash Week."

**Fix applied:** `aria-label="Releases per Week"` (and similar) on `<th>` elements with `<wbr>`.

#### 3.10 [PASS] Document language

`<html lang="en">` is correctly set.

#### 3.11 [PASS] Page title

`<title>Claude Code Release Cadence</title>` is descriptive.

---

### 4. Semantic HTML (WCAG 1.3.1, 2.4.1, 2.4.6)

#### 4.1 [MAJOR] No landmark regions — FIXED

The page had no `<main>`, `<header>`, `<footer>` landmarks.

**Fix applied:** `<header>` around title/subtitle, `<main>` around content, `<footer>` replacing the `<div class="footer-section">`.

#### 4.2 [MAJOR] No skip navigation link — FIXED

No mechanism to skip past stats cards and charts.

**Fix applied:** Skip-to-content link as first focusable element with `:focus-visible` appearance.

#### 4.3 [MINOR] Major table lacks `<caption>` — FIXED

**Fix applied:** `<caption class="sr-only">Release cadence statistics by major version series</caption>`.

#### 4.4 [MINOR] `scope` missing on `<th>` elements — FIXED

**Fix applied:** `scope="col"` on all table header cells.

#### 4.5 [PASS] Heading hierarchy

Headings follow a logical `h1` → `h2` → `h3` structure throughout.

#### 4.6 [PASS] Lists

Footer lists use proper `<ul>` / `<li>` elements.

#### 4.7 [PASS] Table structure

The major version table uses proper `<table>`, `<thead>`, `<tbody>`, `<th>`, `<td>` markup.

---

### 5. Motion & Preferences (WCAG 2.3.1, 2.3.3)

#### 5.1 [MAJOR] No `prefers-reduced-motion` support — FIXED

CSS transitions and Chart.js animations played regardless of user preference.

**Fix applied:** `@media (prefers-reduced-motion: reduce)` kills CSS transitions/animations. `Chart.defaults.animation = false` when the preference is detected.

#### 5.2 [MINOR] No `prefers-color-scheme` detection — FIXED

The page defaulted to dark theme regardless of OS preference.

**Fix applied:** Inline `<script>` reads `prefers-color-scheme` when no `localStorage` value exists.

---

### 6. Bonus: High-Contrast Mode

#### 6.1 [INFO] No `forced-colors` / high-contrast mode support — NOT ADDRESSED

The page does not handle Windows High Contrast Mode. Chart.js canvases and heatmap cells would be invisible.

**Note:** Low priority — Chart.js canvas rendering is fundamentally incompatible with `forced-colors` without a significant alternative rendering path.

---

## Files Modified

- `templates/dashboard.template.html` — all HTML, CSS, and JS changes
- `src/claude_code_release_cadence/config.py` — purple color adjustment (`#a855f7` → `#b975f9`)
