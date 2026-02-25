// Create solid + pale dataset pair for a major version
function makeDatasetPair(major, solidData, paleData, suffix, stack) {
  const c = COLORS[major];
  return [
    {
      label: major,
      data: solidData,
      backgroundColor: c + 'cc',
      borderColor: c,
      borderWidth: 1,
      borderRadius: 3,
      stack,
    },
    {
      label: major + suffix,
      data: paleData,
      backgroundColor: COLORS_PALE[major],
      borderColor: c + '88',
      borderWidth: 1,
      borderRadius: 3,
      stack,
    },
  ];
}

// Convert stacked + fixonly data to percentage-based datasets
function pctDatasets(stacked, fixonly, suffix) {
  return majorsOrder.flatMap((m) => {
    const total =
      stacked[m].reduce((s, v) => s + v, 0) +
      fixonly[m].reduce((s, v) => s + v, 0);
    const toPct = (arr) =>
      arr.map((v) => (total > 0 ? +((v / total) * 100).toFixed(1) : 0));
    return makeDatasetPair(m, toPct(stacked[m]), toPct(fixonly[m]), suffix, m);
  });
}

// Factory for stacked bar charts (covers week, weekNotes, dow, hour)
function stackedBar(id, labels, datasets, opts = {}) {
  const tooltipCb = {};
  if (opts.tooltipTitle) tooltipCb.title = opts.tooltipTitle;
  if (opts.tooltipLabel) tooltipCb.label = opts.tooltipLabel;
  if (opts.tooltipFooter) tooltipCb.footer = opts.tooltipFooter;
  return new Chart(document.getElementById(id), {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      layout: { padding: { top: 16 } },
      plugins: {
        legend: {
          position: 'top',
          labels: { boxWidth: 12, padding: opts.legendPad || 16 },
          onClick:
            opts.legendClick ||
            function (e, legendItem) {
              syncLegendClick(legendItem.text, id);
            },
        },
        tooltip: {
          mode: 'index',
          filter: (i) => i.parsed.y !== 0,
          callbacks: tooltipCb,
        },
      },
      scales: {
        x: { stacked: true, grid: { display: false }, ...(opts.xScale || {}) },
        y: {
          stacked: true,
          beginAtZero: true,
          ...(opts.yTitle
            ? { title: { display: true, text: opts.yTitle } }
            : {}),
          ...(opts.yTicks ? { ticks: opts.yTicks } : {}),
          ...(opts.yExtra || {}),
        },
      },
    },
  });
}

// Tooltip footer that sums all visible items
function totalFooter(unit) {
  return (items) => {
    const t = items.reduce((s, i) => s + i.parsed.y, 0);
    return `Total: ${t} ${unit}`;
  };
}

const THEME_CHART = {
  dark: { text: '#8b949e', border: '#30363d', heading: '#f0f6fc' },
  light: { text: '#656d76', border: '#d0d7de', heading: '#1f2328' },
};
function applyChartTheme() {
  const t = THEME_CHART[getTheme()];
  Chart.defaults.color = t.text;
  Chart.defaults.borderColor = t.border;
}
applyChartTheme();
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  Chart.defaults.animation = false;
}
Chart.defaults.font.family =
  '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

// Plugin: label first appearance of each version series above charts
// Each entry in chart._seriesLabels is { label, xValue } where xValue is
// passed directly to chart.scales.x.getPixelForValue() — works for time
// axes (timestamp ms), category axes (integer index), etc.
Chart.register({
  id: 'seriesLabels',
  afterDraw: function (chart) {
    var sl = chart._seriesLabels;
    if (!sl) return;
    var ctx = chart.ctx;
    var t = THEME_CHART[getTheme()];
    ctx.save();
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.font = 'bold 10px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.fillStyle = t.heading;
    sl.forEach(function (s) {
      if (!chart._showAllSeriesLabels && !isMajorVisible(s.label)) return;
      var xPos = chart.scales.x.getPixelForValue(s.xValue);
      if (xPos >= chart.chartArea.left && xPos <= chart.chartArea.right) {
        ctx.fillText(s.label, xPos, chart.chartArea.top + 4);
      }
    });
    ctx.restore();
  },
});

// Find first week index where each major version has data, return { label, xValue }
function findFirstAppearances(labels, stacked, fixonly) {
  return majorsOrder
    .map(function (m) {
      for (var i = 0; i < labels.length; i++) {
        if ((stacked[m][i] || 0) + (fixonly[m][i] || 0) > 0)
          return { label: m, xValue: new Date(labels[i]).getTime() };
      }
      return null;
    })
    .filter(Boolean);
}

// --- Cross-chart legend sync ---
// Visibility state: { "0.2.x": { main: true, fix: true }, ... }
var versionVisibility = {};
var VERSION_CHART_IDS = [
  'gapChart',
  'weekChart',
  'weekNotesChart',
  'dowChart',
  'hourChart',
  'notesChart',
];

function initVersionVisibility() {
  majorsOrder.forEach(function (m) {
    versionVisibility[m] = { main: true, fix: true };
  });
}

// Extract major from a dataset label (e.g. "0.2.x (fix-only)" -> "0.2.x")
function getMajorFromLabel(label) {
  if (COLORS[label]) return label;
  return (
    majorsOrder.find(function (m) {
      return label.startsWith(m);
    }) || null
  );
}

// Check if a dataset label is a fix-only/fixes variant
function isFixLabel(label) {
  return !COLORS[label] && !!getMajorFromLabel(label);
}

// Check if a major version has any visible datasets (main or fix)
function isMajorVisible(major) {
  var v = versionVisibility[major];
  return v && (v.main || v.fix);
}

// Find first appearance of each major in a flat data array
// getMajor(item, i) returns major string; getXValue(item, i) returns xValue
function firstAppearanceLabels(items, getMajor, getXValue) {
  var seen = {};
  return items
    .map(function (item, i) {
      var m = getMajor(item, i);
      if (!seen[m]) {
        seen[m] = true;
        return { label: m, xValue: getXValue(item, i) };
      }
      return null;
    })
    .filter(Boolean);
}

// Adjust x-axis min/max to fit visible data on time-axis charts
function rescaleTimeAxis(chart) {
  var xOpts = chart.options.scales && chart.options.scales.x;
  if (!xOpts || xOpts.type !== 'time') return;
  var min = Infinity,
    max = -Infinity;
  var hasScatterData = false;
  chart.data.datasets.forEach(function (ds, idx) {
    if (chart.getDatasetMeta(idx).hidden) return;
    if (!Array.isArray(ds.data)) return;
    ds.data.forEach(function (pt) {
      if (typeof pt === 'object' && pt !== null && pt.x != null) {
        hasScatterData = true;
        var t = new Date(pt.x).getTime();
        if (t < min) min = t;
        if (t > max) max = t;
      }
    });
  });
  // For label-based time charts: scan labels for positions with visible data
  if (!hasScatterData && chart.data.labels && chart.data.labels.length) {
    var labels = chart.data.labels;
    var firstIdx = -1,
      lastIdx = -1;
    for (var li = 0; li < labels.length; li++) {
      var hasData = false;
      chart.data.datasets.forEach(function (ds, idx) {
        if (chart.getDatasetMeta(idx).hidden) return;
        if (ds.data[li] > 0) hasData = true;
      });
      if (hasData) {
        if (firstIdx === -1) firstIdx = li;
        lastIdx = li;
      }
    }
    if (firstIdx !== -1) {
      min = new Date(labels[firstIdx]).getTime();
      max = new Date(labels[lastIdx]).getTime();
    }
  }
  if (min !== Infinity && min !== max) {
    var pad = (max - min) * 0.02;
    xOpts.min = min - pad;
    xOpts.max = max + pad;
  } else {
    delete xOpts.min;
    delete xOpts.max;
  }
}

// Central legend click sync: propagates visibility to all version charts
function syncLegendClick(clickedLabel, sourceChartId) {
  var major = getMajorFromLabel(clickedLabel);
  if (!major) return;
  var isFix = isFixLabel(clickedLabel);
  var vis = versionVisibility[major];
  if (!vis) return;

  if (isFix) {
    vis.fix = !vis.fix;
  } else {
    // If source chart has no fix companion for this major, toggle both
    var sourceChart = Chart.getChart(sourceChartId);
    var hasFixCompanion =
      sourceChart &&
      sourceChart.data.datasets.some(function (ds) {
        return getMajorFromLabel(ds.label) === major && isFixLabel(ds.label);
      });
    vis.main = !vis.main;
    if (!hasFixCompanion) vis.fix = vis.main;
  }

  // Apply visibility to all version charts (including source for companions)
  VERSION_CHART_IDS.forEach(function (id) {
    var chart = Chart.getChart(id);
    if (!chart) return;
    chart.data.datasets.forEach(function (ds, idx) {
      var dsMajor = getMajorFromLabel(ds.label);
      if (dsMajor !== major) return;
      var dsIsFix = isFixLabel(ds.label);
      if (isFix && !dsIsFix) return; // fix click: only toggle fix datasets
      chart.getDatasetMeta(idx).hidden =
        (dsIsFix ? !vis.fix : !vis.main) || null;
    });
    if (id === 'notesChart') return; // recomputeNotesOutlier handles its update
    rescaleTimeAxis(chart);
    chart.update('none');
  });
  // Recompute notesChart outlier cap
  if (typeof recomputeNotesOutlier === 'function') {
    recomputeNotesOutlier();
  }
}
