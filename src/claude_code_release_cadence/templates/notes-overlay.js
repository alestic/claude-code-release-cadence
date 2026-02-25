// --- Changelog entries per release (with outlier capping + scroll-to-reveal) ---
const notesLabels = notesData.map((d) => d.version);
const notesDatasets = majorsOrder.flatMap((m) =>
  makeDatasetPair(
    m,
    notesData.map((d) => (d.major === m ? d.non_fixes : 0)),
    notesData.map((d) => (d.major === m ? d.fixes : 0)),
    ' (fixes)',
    'main',
  ),
);

// Outlier detection: find >2x gap and compute y-axis cap
function computeOutlierCap(totals, maxOutliers = 3) {
  const desc = totals.slice().sort((a, b) => b - a);
  if (desc.length === 0 || desc[0] === 0) return { threshold: 0, cap: 10 };
  let threshold = desc[0] + 1;
  for (let i = 0; i < desc.length - 1 && i < maxOutliers; i++) {
    if (desc[i] > desc[i + 1] * 2) {
      threshold = desc[i + 1] * 2;
      break;
    }
  }
  const cap =
    Math.ceil(
      Math.min(desc.find((v) => v <= threshold) || desc[0], threshold) / 5,
    ) *
      5 +
    5;
  return { threshold, cap };
}

// Helpers: compute visible totals and per-bar fix/non-fix from chart state
function getVisibleTotals(chart) {
  return chart.data.labels.map((_, i) => {
    let sum = 0;
    chart.data.datasets.forEach((ds, dsIdx) => {
      if (!chart.getDatasetMeta(dsIdx).hidden) sum += ds.data[i] || 0;
    });
    return sum;
  });
}
function getVisibleParts(chart, idx) {
  let fixes = 0,
    nonFixes = 0;
  chart.data.datasets.forEach((ds, dsIdx) => {
    if (chart.getDatasetMeta(dsIdx).hidden) return;
    const val = ds.data[idx] || 0;
    if (ds.label.includes('(fixes)')) fixes += val;
    else nonFixes += val;
  });
  return { fixes, nonFixes, total: fixes + nonFixes };
}

// DOM setup: overlay container + tooltip
const notesCanvas = document.getElementById('notesChart');
const notesWrapper = notesCanvas.parentElement;
notesWrapper.style.overflow = 'visible';
notesWrapper.parentElement.style.overflow = 'visible';
const notesOverlayContainer = document.createElement('div');
notesOverlayContainer.className = 'overlay-container';
notesWrapper.appendChild(notesOverlayContainer);
const overlayTooltip = document.createElement('div');
overlayTooltip.className = 'overlay-tooltip';
overlayTooltip.setAttribute('role', 'status');
overlayTooltip.setAttribute('aria-live', 'polite');
document.body.appendChild(overlayTooltip);
// Sentinel at bottom of chart for scroll detection
const notesSentinel = document.createElement('div');
notesSentinel.style.cssText =
  'position:absolute;bottom:0;left:0;width:1px;height:1px';
notesWrapper.appendChild(notesSentinel);

// Track focused overlay version for focus restoration after rebuild
var focusedOverlayVersion = null;

// Show ALL outlier overlays at once
function showNotesOverlays(chart) {
  const o = chart._outlier;
  const meta = chart.getDatasetMeta(0);
  const { chartArea } = chart;
  const pxPerUnit = (chartArea.bottom - chartArea.top) / o.cap;
  var restoreVersion = focusedOverlayVersion;
  while (notesOverlayContainer.firstChild)
    notesOverlayContainer.removeChild(notesOverlayContainer.firstChild);
  o.visibleTotals.forEach((total, idx) => {
    if (total <= o.threshold || !meta.data[idx]) return;
    const parts = getVisibleParts(chart, idx);
    if (parts.total <= o.cap) return;
    const overflowPx = (parts.total - o.cap) * pxPerUnit;
    const barWidth = meta.data[idx].width || 8;
    const barX = meta.data[idx].x;
    const origIdx = chart._indexMap ? chart._indexMap[idx] : idx;
    const major = notesData[origIdx].major;
    const color = COLORS[major];
    const version = notesData[origIdx].version;

    const col = document.createElement('div');
    col.className = 'overlay-col';
    col.style.left = barX - barWidth / 2 + 'px';
    col.style.top = chartArea.top - overflowPx - 20 + 'px';
    col.style.width = barWidth + 'px';
    col.setAttribute('tabindex', '0');
    col.setAttribute('role', 'img');
    col.setAttribute(
      'aria-label',
      version +
        ': ' +
        parts.nonFixes +
        ' non-fix changes, ' +
        parts.fixes +
        ' fixes, ' +
        parts.total +
        ' total',
    );
    col.addEventListener('mouseenter', () => {
      overlayTooltip.textContent =
        version +
        '\nnon-fix changes: ' +
        parts.nonFixes +
        '\nfixes: ' +
        parts.fixes +
        '\nTotal: ' +
        parts.total;
      overlayTooltip.style.display = 'block';
    });
    col.addEventListener('mousemove', (e) => {
      overlayTooltip.style.left = e.clientX + 12 + 'px';
      overlayTooltip.style.top = e.clientY + 12 + 'px';
    });
    col.addEventListener('mouseleave', () => {
      overlayTooltip.style.display = 'none';
    });
    col.addEventListener('focus', function () {
      focusedOverlayVersion = version;
      overlayTooltip.textContent =
        version +
        '\nnon-fix changes: ' +
        parts.nonFixes +
        '\nfixes: ' +
        parts.fixes +
        '\nTotal: ' +
        parts.total;
      overlayTooltip.style.display = 'block';
      var r = this.getBoundingClientRect();
      var left = r.right + 8;
      if (left + 220 > window.innerWidth) left = r.left - 228;
      overlayTooltip.style.left = Math.max(0, left) + 'px';
      overlayTooltip.style.top = r.top + 'px';
    });
    col.addEventListener('blur', function () {
      focusedOverlayVersion = null;
      overlayTooltip.style.display = 'none';
    });

    const label = document.createElement('div');
    label.className = 'overlay-label';
    label.textContent = String(parts.total);
    label.style.marginLeft = '-10px';
    label.style.width = barWidth + 20 + 'px';
    col.appendChild(label);

    if (parts.fixes > 0) {
      const el = document.createElement('div');
      el.className = 'overlay-segment';
      el.style.cssText = `width:${barWidth}px;height:${parts.fixes * pxPerUnit}px;background:${COLORS_PALE[major]};border:1px solid ${color}88;border-bottom:0`;
      col.appendChild(el);
    }
    if (parts.nonFixes > 0) {
      const el = document.createElement('div');
      el.className = 'overlay-segment';
      el.style.cssText = `width:${barWidth}px;height:${parts.nonFixes * pxPerUnit}px;background:${color}cc;border:1px solid ${color};border-top:0`;
      col.appendChild(el);
    }
    notesOverlayContainer.appendChild(col);
  });
  notesOverlayContainer.style.display = 'block';
  if (restoreVersion) {
    var el = notesOverlayContainer.querySelector(
      '[aria-label^="' + restoreVersion + ':"]',
    );
    if (el) el.focus();
  }
}
function hideNotesOverlays() {
  notesOverlayContainer.style.display = 'none';
}

// Rebuild notesChart data arrays to exclude hidden major versions
function rebuildNotesData() {
  var keepIndices = [];
  notesData.forEach(function (d, i) {
    if (isMajorVisible(d.major)) keepIndices.push(i);
  });
  notesChart.data.labels = keepIndices.map(function (i) {
    return notesData[i].version;
  });
  notesChart.data.datasets.forEach(function (ds) {
    ds.data = keepIndices.map(function (i) {
      return ds._origData[i];
    });
  });
  notesChart._indexMap = keepIndices;
  notesChart._seriesLabels = firstAppearanceLabels(
    keepIndices,
    function (origIdx) {
      return notesData[origIdx].major;
    },
    function (origIdx, chartIdx) {
      return chartIdx;
    },
  );
}

// Recompute outlier cap and overlays after visibility changes
function recomputeNotesOutlier() {
  rebuildNotesData();
  const totals = getVisibleTotals(notesChart);
  const result = computeOutlierCap(totals);
  const inView =
    notesSentinel.getBoundingClientRect().bottom <= window.innerHeight;
  notesChart._outlier = {
    threshold: result.threshold,
    cap: result.cap,
    visibleTotals: totals,
    hovered: inView,
  };
  notesChart.options.scales.y.max = result.cap;
  hideNotesOverlays();
  notesChart.update('none');
  if (inView) showNotesOverlays(notesChart);
}

// Plugin: draw static outlier labels above capped bars
const notesOutlierPlugin = {
  id: 'notesOutlierLabels',
  afterDraw(chart) {
    const o = chart._outlier;
    if (!o) return;
    const { ctx, chartArea } = chart;
    const meta = chart.getDatasetMeta(0);
    o.visibleTotals.forEach((total, i) => {
      if (total <= o.threshold || o.hovered || !meta.data[i]) return;
      const x = meta.data[i].x;
      ctx.save();
      ctx.fillStyle = THEME_CHART[getTheme()].heading;
      ctx.textAlign = 'center';
      ctx.font = 'bold 11px -apple-system, BlinkMacSystemFont, sans-serif';
      ctx.textBaseline = 'bottom';
      ctx.fillText(String(total), x, chartArea.top - 10);
      ctx.font = '10px -apple-system, BlinkMacSystemFont, sans-serif';
      ctx.textBaseline = 'top';
      ctx.fillText('\u25B4', x, chartArea.top - 10);
      ctx.restore();
    });
  },
};

// Create notes chart with outlier capping
const notesInit = computeOutlierCap(notesData.map((d) => d.total));
const notesChart = new Chart(notesCanvas, {
  type: 'bar',
  data: { labels: notesLabels, datasets: notesDatasets },
  plugins: [notesOutlierPlugin],
  options: {
    responsive: true,
    maintainAspectRatio: false,
    onResize(chart) {
      const o = chart._outlier;
      if (o && o.hovered) requestAnimationFrame(() => showNotesOverlays(chart));
    },
    layout: { padding: { top: 20 } },
    plugins: {
      legend: {
        position: 'top',
        labels: { boxWidth: 12, padding: 16 },
        onClick: function (e, legendItem) {
          syncLegendClick(legendItem.text, 'notesChart');
          recomputeNotesOutlier();
        },
      },
      tooltip: {
        mode: 'index',
        filter: (item) => item.parsed.y !== 0,
        callbacks: {
          title: (items) => {
            var di = items[0].dataIndex;
            var origIdx = notesChart._indexMap ? notesChart._indexMap[di] : di;
            return notesData[origIdx].version;
          },
          label: (item) => {
            const kind = item.dataset.label.includes('(fixes)')
              ? 'fixes'
              : 'non-fix changes';
            return kind + ': ' + item.parsed.y;
          },
          footer: (items) => {
            const parts = getVisibleParts(notesChart, items[0].dataIndex);
            return `Total: ${parts.total}`;
          },
        },
      },
    },
    scales: {
      x: {
        stacked: true,
        grid: { display: false },
        ticks: { display: false },
      },
      y: {
        stacked: true,
        title: { display: true, text: 'Bullet points' },
        beginAtZero: true,
        max: notesInit.cap,
      },
    },
  },
});
notesChart._outlier = {
  threshold: notesInit.threshold,
  cap: notesInit.cap,
  visibleTotals: notesData.map((d) => d.total),
  hovered: false,
};
// Store original data arrays for rebuilding on visibility changes
notesChart.data.datasets.forEach(function (ds) {
  ds._origData = ds.data.slice();
});
notesChart._indexMap = notesData.map(function (_, i) {
  return i;
});
// Series labels: first bar index per major (category axis)
notesChart._seriesLabels = firstAppearanceLabels(
  notesData,
  function (d) {
    return d.major;
  },
  function (d, i) {
    return i;
  },
);

// Scroll-to-reveal: show overlays when chart bottom is visible
new IntersectionObserver(
  (entries) => {
    const o = notesChart._outlier;
    const visible = entries[0].isIntersecting;
    if (visible !== o.hovered) {
      o.hovered = visible;
      if (visible) showNotesOverlays(notesChart);
      else hideNotesOverlays();
      notesChart.draw();
    }
  },
  { threshold: 1.0 },
).observe(notesSentinel);
