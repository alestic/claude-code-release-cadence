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
      plugins: {
        legend: {
          position: 'top',
          labels: { boxWidth: 12, padding: opts.legendPad || 16 },
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

// Plugin: label first appearance of each version series above bars
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
      var xPos = chart.scales.x.getPixelForValue(
        new Date(chart.data.labels[s.index]).getTime(),
      );
      if (xPos >= chart.chartArea.left && xPos <= chart.chartArea.right) {
        ctx.fillText(s.label, xPos, chart.chartArea.top + 4);
      }
    });
    ctx.restore();
  },
});

function findFirstAppearances(stacked, fixonly) {
  return majorsOrder
    .map(function (m) {
      for (var i = 0; i < weekLabels.length; i++) {
        if ((stacked[m][i] || 0) + (fixonly[m][i] || 0) > 0)
          return { label: m, index: i };
      }
      return null;
    })
    .filter(Boolean);
}
