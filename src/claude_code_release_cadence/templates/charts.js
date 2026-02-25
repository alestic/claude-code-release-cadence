// --- Days between releases (scatter) ---
new Chart(document.getElementById('gapChart'), {
  type: 'scatter',
  data: {
    datasets: majorsOrder.map(function (major, mi) {
      return {
        label: major,
        data: gaps
          .filter((g) => g.major === major)
          .map((g) => ({ x: g.timestamp, y: g.days })),
        backgroundColor: COLORS[major] + 'cc',
        borderColor: COLORS[major],
        pointStyle:
          mi === majorsOrder.length - 1
            ? 'circle'
            : POINT_STYLES_OTHER[mi % POINT_STYLES_OTHER.length],
        pointRadius: mi === majorsOrder.length - 1 ? 3 : 4,
        pointHoverRadius: 6,
      };
    }),
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { usePointStyle: true } },
      tooltip: {
        callbacks: {
          title: (items) => {
            const idx = gaps.findIndex((g) => g.timestamp === items[0].raw.x);
            return idx >= 0 ? gaps[idx].version : '';
          },
          label: (item) =>
            `${item.parsed.y.toFixed(1)} days since previous release`,
        },
      },
    },
    scales: {
      x: { type: 'time', time: { unit: 'month' } },
      y: {
        title: { display: true, text: 'Days since previous release' },
        min: 0,
      },
    },
  },
});

// --- Releases per week ---
var weekChart = stackedBar(
  'weekChart',
  weekLabels,
  majorsOrder.flatMap((m) =>
    makeDatasetPair(
      m,
      weekStacked[m],
      weekStackedFixonly[m],
      ' (fix-only)',
      'main',
    ),
  ),
  {
    yTitle: 'Releases',
    xScale: { type: 'time', time: { unit: 'month' } },
    tooltipTitle: (items) => `Week of ${items[0].label}`,
    tooltipFooter: totalFooter('releases'),
  },
);
weekChart._seriesLabels = findFirstAppearances(weekStacked, weekStackedFixonly);
weekChart.update('none');

// --- Changelog entries per week ---
var weekNotesChart = stackedBar(
  'weekNotesChart',
  weekLabels,
  majorsOrder.flatMap((m) =>
    makeDatasetPair(
      m,
      weekNotesStacked[m],
      weekNotesStackedFixes[m],
      ' (fixes)',
      'main',
    ),
  ),
  {
    yTitle: 'Changelog entries',
    xScale: { type: 'time', time: { unit: 'month' } },
    tooltipTitle: (items) => `Week of ${items[0].label}`,
    tooltipFooter: totalFooter('entries'),
  },
);
weekNotesChart._seriesLabels = findFirstAppearances(
  weekNotesStacked,
  weekNotesStackedFixes,
);
weekNotesChart.update('none');

// --- Day of week (% by major) ---
stackedBar(
  'dowChart',
  ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  pctDatasets(dowStacked, dowStackedFixonly, ' (fix-only)').map(
    function (ds, i) {
      var mi = Math.floor(i / 2);
      var pi = mi === majorsOrder.length - 1 ? 0 : (mi % 7) + 1;
      ds._hatchType = pi;
      ds.backgroundColor = hatchPattern(ds.backgroundColor, pi);
      return ds;
    },
  ),
  {
    legendPad: 10,
    yTicks: { callback: (v) => v + '%' },
    tooltipLabel: (i) => `${i.dataset.label}: ${i.parsed.y}%`,
    tooltipFooter: (items) => {
      const t = items.reduce((s, i) => s + i.parsed.y, 0);
      return `Total: ${t.toFixed(1)}%`;
    },
  },
);

// --- Hour of day (% by major) ---
const hourLabels = Array.from(
  { length: 24 },
  (_, i) => (i % 12 || 12) + (i < 12 ? 'a' : 'p'),
);
stackedBar(
  'hourChart',
  hourLabels,
  pctDatasets(hourStacked, hourStackedFixonly, ' (fix-only)').map(
    function (ds, i) {
      var mi = Math.floor(i / 2);
      var pi = mi === majorsOrder.length - 1 ? 0 : (mi % 7) + 1;
      ds._hatchType = pi;
      ds.backgroundColor = hatchPattern(ds.backgroundColor, pi);
      return ds;
    },
  ),
  {
    legendPad: 10,
    xScale: { ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 12 } },
    yTicks: { callback: (v) => v + '%' },
    tooltipLabel: (i) => `${i.dataset.label}: ${i.parsed.y}%`,
    tooltipFooter: (items) => {
      const t = items.reduce((s, i) => s + i.parsed.y, 0);
      return `Total: ${t.toFixed(1)}%`;
    },
  },
);
