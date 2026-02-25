// --- Heatmap color helpers (shared across makeCell, theme update, legend) ---
function heatmapBg(intensity, isDark) {
  if (intensity === 0)
    return isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)';
  return isDark
    ? 'rgba(56, 189, 248, ' + (0.15 + intensity * 0.75) + ')'
    : 'rgba(14, 116, 144, ' + (0.12 + intensity * 0.7) + ')';
}
function heatmapNumColor(intensity, isDark) {
  return isDark
    ? 'rgba(255,255,255,0.85)'
    : intensity >= 0.5
      ? 'rgba(255,255,255,0.9)'
      : 'rgba(0,0,0,0.7)';
}
function heatmapNumShadow(intensity, isDark) {
  return isDark || intensity >= 0.5 ? '0 0 2px rgba(0,0,0,0.6)' : 'none';
}

// --- Heatmap (DOW x Hour, pure CSS grid — wide + narrow layouts) ---
(function () {
  const container = document.getElementById('heatmap');
  const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const maxVal = Math.max(1, ...heatmapDowHour.flat());

  // Tooltip element (shared)
  const tip = document.createElement('div');
  tip.className = 'heatmap-cell-tooltip';
  tip.setAttribute('role', 'status');
  tip.setAttribute('aria-live', 'polite');
  document.body.appendChild(tip);

  function cellTipText(cell) {
    var dn = dayNames[+cell.dataset.dow];
    var hr = +cell.dataset.hour;
    var hrLabel = (hr % 12 || 12) + (hr < 12 ? 'am' : 'pm');
    return (
      dn +
      ' ' +
      hrLabel +
      ': ' +
      cell.dataset.total +
      ' entries (' +
      cell.dataset.fixes +
      ' fixes, ' +
      cell.dataset.features +
      ' features)'
    );
  }

  function showTipAt(el) {
    tip.textContent = cellTipText(el);
    tip.style.display = 'block';
    var r = el.getBoundingClientRect();
    var left = r.right + 8;
    if (left + 220 > window.innerWidth) left = r.left - 228;
    tip.style.left = Math.max(0, left) + 'px';
    tip.style.top = r.top + 'px';
  }

  function makeCell(d, h, isFirst) {
    const total = heatmapDowHour[d][h];
    const fixes = heatmapDowHourFixes[d][h];
    const features = total - fixes;
    const intensity = total > 0 ? Math.sqrt(total / maxVal) : 0;
    const cell = document.createElement('div');
    cell.className = 'heatmap-cell';
    cell.setAttribute('role', 'gridcell');
    cell.setAttribute('tabindex', isFirst ? '0' : '-1');
    const isDark = getTheme() === 'dark';
    cell.dataset.dow = d;
    cell.dataset.hour = h;
    cell.dataset.total = total;
    cell.dataset.fixes = fixes;
    cell.dataset.features = features;
    var dn = dayNames[d];
    var hrLabel = (h % 12 || 12) + (h < 12 ? 'am' : 'pm');
    cell.setAttribute(
      'aria-label',
      dn +
        ' ' +
        hrLabel +
        ': ' +
        total +
        ' entries (' +
        fixes +
        ' fixes, ' +
        features +
        ' features)',
    );
    cell.style.background = heatmapBg(intensity, isDark);
    if (total > 0) {
      var num = document.createElement('span');
      num.className = 'heatmap-num';
      num.textContent = total;
      num.style.color = heatmapNumColor(intensity, isDark);
      num.style.textShadow = heatmapNumShadow(intensity, isDark);
      cell.appendChild(num);
    }
    cell.addEventListener('mouseenter', function (e) {
      tip.textContent = cellTipText(this);
      tip.style.display = 'block';
    });
    cell.addEventListener('mousemove', function (e) {
      tip.style.left = e.clientX + 12 + 'px';
      tip.style.top = e.clientY + 12 + 'px';
    });
    cell.addEventListener('mouseleave', function () {
      tip.style.display = 'none';
    });
    cell.addEventListener('focus', function () {
      showTipAt(this);
    });
    cell.addEventListener('blur', function () {
      tip.style.display = 'none';
    });
    return cell;
  }

  function hourLabel(h) {
    return h % 6 === 0 ? (h % 12 || 12) + (h < 12 ? 'a' : 'p') : '';
  }

  function makeHeader(text, role) {
    const hdr = document.createElement('div');
    hdr.className = 'heatmap-header';
    hdr.textContent = text || '';
    if (role) hdr.setAttribute('role', role);
    return hdr;
  }

  function makeRow() {
    const row = document.createElement('div');
    row.className = 'heatmap-row';
    row.setAttribute('role', 'row');
    return row;
  }

  // Arrow-key navigation for roving tabindex within a grid
  function addGridKeyNav(grid, rowCount, colCount) {
    grid.addEventListener('keydown', function (e) {
      var focused = document.activeElement;
      if (!focused || !focused.dataset.dow) return;
      var d = +focused.dataset.dow,
        h = +focused.dataset.hour;
      // Wide: rows=days(d), cols=hours(h); Narrow: rows=hours(h), cols=days(d)
      var isWide = grid.classList.contains('heatmap-wide');
      var row = isWide ? d : h,
        col = isWide ? h : d;
      if (e.key === 'ArrowRight') col = (col + 1) % colCount;
      else if (e.key === 'ArrowLeft') col = (col + colCount - 1) % colCount;
      else if (e.key === 'ArrowDown') row = (row + 1) % rowCount;
      else if (e.key === 'ArrowUp') row = (row + rowCount - 1) % rowCount;
      else if (e.key === 'Home') {
        row = 0;
        col = 0;
      } else if (e.key === 'End') {
        row = rowCount - 1;
        col = colCount - 1;
      } else return;
      e.preventDefault();
      var nd = isWide ? row : col,
        nh = isWide ? col : row;
      var next = grid.querySelector(
        '[data-dow="' + nd + '"][data-hour="' + nh + '"]',
      );
      if (next) {
        focused.setAttribute('tabindex', '-1');
        next.setAttribute('tabindex', '0');
        next.focus();
      }
    });
  }

  // Wide grid: rows = days, columns = hours (original layout)
  const wide = document.createElement('div');
  wide.className = 'heatmap-grid heatmap-wide';
  wide.setAttribute('role', 'grid');
  wide.setAttribute(
    'aria-label',
    'Release activity heatmap: days of week by hours',
  );
  var hdrRow = makeRow();
  hdrRow.appendChild(makeHeader('', 'columnheader'));
  for (let h = 0; h < 24; h++)
    hdrRow.appendChild(makeHeader(hourLabel(h), 'columnheader'));
  wide.appendChild(hdrRow);
  for (let d = 0; d < 7; d++) {
    var row = makeRow();
    const lbl = document.createElement('div');
    lbl.className = 'heatmap-row-label';
    lbl.setAttribute('role', 'rowheader');
    lbl.textContent = dayNames[d];
    row.appendChild(lbl);
    for (let h = 0; h < 24; h++)
      row.appendChild(makeCell(d, h, d === 0 && h === 0));
    wide.appendChild(row);
  }
  addGridKeyNav(wide, 7, 24);
  container.appendChild(wide);

  // Narrow grid: rows = hours, columns = days (transposed for mobile)
  const narrow = document.createElement('div');
  narrow.className = 'heatmap-grid heatmap-narrow';
  narrow.setAttribute('role', 'grid');
  narrow.setAttribute(
    'aria-label',
    'Release activity heatmap: hours by days of week',
  );
  hdrRow = makeRow();
  hdrRow.appendChild(makeHeader('', 'columnheader'));
  for (let d = 0; d < 7; d++)
    hdrRow.appendChild(makeHeader(dayNames[d], 'columnheader'));
  narrow.appendChild(hdrRow);
  for (let h = 0; h < 24; h++) {
    var row = makeRow();
    const lbl = document.createElement('div');
    lbl.className = 'heatmap-row-label';
    lbl.setAttribute('role', 'rowheader');
    lbl.textContent = hourLabel(h);
    row.appendChild(lbl);
    for (let d = 0; d < 7; d++)
      row.appendChild(makeCell(d, h, d === 0 && h === 0));
    narrow.appendChild(row);
  }
  addGridKeyNav(narrow, 24, 7);
  container.appendChild(narrow);

  // "Now" dot — highlight current US/Pacific day+hour in both grids
  try {
    var pacNow = new Date(
      new Date().toLocaleString('en-US', { timeZone: 'America/Los_Angeles' }),
    );
    var jsDow = pacNow.getDay(); // 0=Sun
    var nowDow = (jsDow + 6) % 7; // convert to 0=Mon
    var nowHour = pacNow.getHours();
    [wide, narrow].forEach(function (g) {
      var nowCell = g.querySelector(
        '[data-dow="' + nowDow + '"][data-hour="' + nowHour + '"]',
      );
      if (nowCell) {
        var dot = document.createElement('div');
        dot.className = 'heatmap-now';
        dot.title = 'Now (US/Pacific)';
        nowCell.appendChild(dot);
      }
    });
  } catch (e) {}

  // Legend
  const legend = document.createElement('div');
  legend.className = 'heatmap-legend';
  const lessLabel = document.createElement('span');
  lessLabel.textContent = 'Less';
  legend.appendChild(lessLabel);
  [0, 0.25, 0.5, 0.75, 1].forEach(function (intensity) {
    const swatch = document.createElement('div');
    swatch.className = 'heatmap-legend-cell';
    swatch.style.background = heatmapBg(intensity, getTheme() === 'dark');
    legend.appendChild(swatch);
  });
  const moreLabel = document.createElement('span');
  moreLabel.textContent = 'More';
  legend.appendChild(moreLabel);
  container.appendChild(legend);
})();

// Heatmap theme update helper
function updateHeatmapTheme() {
  const isDark = getTheme() === 'dark';
  const maxVal = Math.max(1, ...heatmapDowHour.flat());
  document.querySelectorAll('.heatmap-cell').forEach(function (cell) {
    const total = +cell.dataset.total;
    const intensity = total > 0 ? Math.sqrt(total / maxVal) : 0;
    cell.style.background = heatmapBg(intensity, isDark);
    var numEl = cell.querySelector('.heatmap-num');
    if (numEl) {
      numEl.style.color = heatmapNumColor(intensity, isDark);
      numEl.style.textShadow = heatmapNumShadow(intensity, isDark);
    }
  });
  document
    .querySelectorAll('.heatmap-legend-cell')
    .forEach(function (swatch, i) {
      swatch.style.background = heatmapBg([0, 0.25, 0.5, 0.75, 1][i], isDark);
    });
}
