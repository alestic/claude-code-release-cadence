# Accessibility Fixes — Code Reference

<!-- [Created with AI: Claude Code with Opus 4.6] -->

Concrete diffs / snippets for each finding in README.md, targeting
`templates/dashboard.template.html` unless noted.

All findings have been implemented. This file preserves the approach
taken for each fix as a reference.

---

## Phase 1 — Critical

### 3.1 — Canvas `role="img"` + `aria-label`

Added to each `<canvas>` element:

```
gapChart:       role="img" aria-label="Scatter chart: days between consecutive releases over time, colored by major version series"
weekChart:      role="img" aria-label="Stacked bar chart: releases published per calendar week, by major version series"
weekNotesChart: role="img" aria-label="Stacked bar chart: changelog entries per calendar week, by major version series"
notesChart:     role="img" aria-label="Stacked bar chart: changelog entries per release, split into fixes vs non-fix changes"
dowChart:       role="img" aria-label="Stacked bar chart: percentage of releases by day of week per major version"
hourChart:      role="img" aria-label="Stacked bar chart: percentage of releases by hour of day per major version"
sizeChart:      role="img" aria-label="Dual-axis line chart: npm package size in MB and file count over time"
```

### 2.1 + 3.2 — Heatmap keyboard access + ARIA grid

In `makeCell()`: roving `tabindex` (0 on first cell, -1 on others), `role="gridcell"`,
`aria-label` with tooltip content, `focus`/`blur` handlers with viewport-edge tooltip clamping.

Arrow-key navigation via `addGridKeyNav()`: ArrowUp/Down/Left/Right wrap within grid,
Home/End jump to corners. Wide grid: rows=days, cols=hours. Narrow grid: rows=hours, cols=days.

Grid containers: `role="grid"` + `aria-label`. Row wrappers: `role="row"` with `display:contents`.
Row labels: `role="rowheader"`. Hour headers: `role="columnheader"`.

### 2.2 — Outlier overlay keyboard access

In `showNotesOverlays()`: `tabindex="0"`, `role="img"`, `aria-label` with tooltip content.
`focus`/`blur` handlers with viewport-edge clamping. Focus restoration after chart rebuild
via `focusedOverlayVersion` tracking.

### 1.1 — Link color in light theme

```css
:root, [data-theme="dark"] { --link: #58a6ff; }
[data-theme="light"] { --link: #0969da; }
.footer-grid a { color: var(--link); }
/* #0969da on #f6f8fa = 7.94:1 (passes AA + AAA) */
```

---

## Phase 2 — Major

### 1.2 — Theme-aware chart palette

```js
const DARK_TO_LIGHT = {
  '#f97316':'#c05621', '#3b82f6':'#2563eb', '#b975f9':'#7c3aed',
  '#22c55e':'#15803d', '#eab308':'#a16207', '#ec4899':'#be185d',
  '#14b8a6':'#0f766e', '#f43f5e':'#be123c'
};
```

`applyPalette()` swaps `COLORS` between dark and light maps on theme toggle.
Chart datasets, table color dots, and sizeChart colors all update via the
theme toggle handler.

### 1.5 — Non-color differentiators for chart datasets

```js
var DASH_PATTERNS = [[], [8, 4], [2, 2], [12, 4, 2, 4], [8, 4, 2, 4, 2, 4], [16, 4], [4, 4], [2, 6]];
var POINT_STYLES = ['circle', 'triangle', 'rect', 'rectRot', 'star', 'cross', 'crossRot', 'dash'];
```

- **gapChart** (scatter): `pointStyle` per series + `usePointStyle: true` in legend
- **dowChart / hourChart** (stacked bar): `borderDash` + `borderWidth: 2` per series
- **sizeChart** (line): `borderDash: [6, 3]` on File Count dataset

### 1.6 — Heatmap visible count numbers

```js
// In makeCell(), after setting background color:
if (total > 0) {
  var num = document.createElement('span');
  num.className = 'heatmap-num';
  num.textContent = total;
  num.style.color = isDark ? 'rgba(255,255,255,0.85)'
    : (intensity >= 0.5 ? 'rgba(255,255,255,0.9)' : 'rgba(0,0,0,0.7)');
  num.style.textShadow = isDark || intensity >= 0.5
    ? '0 0 2px rgba(0,0,0,0.6)' : 'none';
  cell.appendChild(num);
}
```

```css
.heatmap-num { position: absolute; inset: 0; display: flex; align-items: center;
  justify-content: center; font-size: 9px; font-weight: 600; pointer-events: none;
  line-height: 1; z-index: 2; }
@media (max-width: 640px) { .heatmap-num { display: none; } }
```

Theme toggle recolors via `updateHeatmapTheme()`.

### 1.7 — "Now" indicator (non-color)

Changed from small centered red dot to red border outline:

```css
.heatmap-now { position: absolute; inset: 0; border: 2px solid #f43f5e;
  border-radius: 3px; pointer-events: none; z-index: 1; }
```

Cell count number sits on top (z-index 2 > 1). Heatmap color intensity
remains visible through the border outline.

### 4.1 — Landmark regions

```html
<header>
  <h1>Claude Code Release Cadence</h1>
  <p class="subtitle">...</p>
</header>
<main>
  <!-- stats grid + all chart sections -->
</main>
<footer class="footer-section">
  <!-- was: <div class="footer-section"> -->
</footer>
```

### 4.2 — Skip navigation

```html
<a href="#about" class="skip-link">Skip to About</a>
```

Visually hidden until focused, then appears centered at top of viewport.

### 2.3 — Focus indicators

```css
:focus-visible { outline: 2px solid var(--link); outline-offset: 2px; }
```

Theme-aware via `--link` variable (`#58a6ff` dark, `#0969da` light).

### 5.1 — Reduced motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    transition-duration: 0.01ms !important;
    animation-duration: 0.01ms !important;
  }
}
```

```js
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  Chart.defaults.animation = false;
}
```

### 3.3 — Theme toggle state

Dynamic `aria-label` set on init and in the click handler:
```js
btn.setAttribute('aria-label', 'Switch to ' + (next === 'dark' ? 'light' : 'dark') + ' theme');
```

### 3.4 — Hide decorative SVGs

`aria-hidden="true"` on sun/moon icon SVGs (in HTML) and on anchor link SVGs (in JS).

### 1.3 — Purple contrast fix

In `config.py`:
```python
"#b975f9",  # purple (lightened for dark-theme AA contrast)
```

### 3.5 — Color dots

```js
dot.setAttribute('aria-hidden', 'true');
```

### 3.6 — Stats cards semantics

```js
card.setAttribute('role', 'group');
card.setAttribute('aria-label', s.label + ': ' + s.value);
```

---

## Phase 3 — Minor

### 4.3 — Table caption

```html
<caption class="sr-only">Release cadence statistics by major version series</caption>
```

### 4.4 + 3.9 — `<th scope="col">` and `aria-label`

```html
<th scope="col">Series</th>
<th scope="col">Releases</th>
<th scope="col">Span</th>
<th scope="col" aria-label="Releases per Week">Releases/<wbr>Week</th>
<th scope="col" aria-label="Entries per Week">Entries/<wbr>Week</th>
<th scope="col">Date Range</th>
```

### 1.8 — Trend arrows

Arrow character wrapped in `aria-hidden="true"` span:
```js
if (s.trend.arrow) {
  var ar = document.createElement('span');
  ar.setAttribute('aria-hidden', 'true');
  ar.textContent = s.trend.arrow + ' ';
  tr.appendChild(ar);
}
tr.appendChild(document.createTextNode(s.trend.text));
```

### 1.9 — Tooltip border contrast

```css
:root, [data-theme="dark"] { --tooltip-border: #545d68; }
```

### 3.7 — External link indication

```html
<span class="sr-only">(opens in new tab)</span>
```

Appended to all `target="_blank"` links.

### 5.2 — Respect `prefers-color-scheme`

```js
(function(){
  var s = localStorage.getItem('theme');
  if (!s) s = window.matchMedia('(prefers-color-scheme:light)').matches ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', s);
})()
```

### 3.8 — Tooltip live regions

```js
tip.setAttribute('role', 'status');
tip.setAttribute('aria-live', 'polite');
```

Applied to heatmap tooltip, overlay tooltip, and "Copied!" notification.
