// --- Major version table ---
const notesTotalByMajor = {};
notesData.forEach((d) => {
  notesTotalByMajor[d.major] = (notesTotalByMajor[d.major] || 0) + d.total;
});
const tbody = document.getElementById('major-table-body');
majorsOrder.forEach((series) => {
  const s = majorStats[series];
  const perWeek =
    s.span_days > 0 ? (s.count / (s.span_days / 7)).toFixed(1) : '\u2014';
  const notesTotal = notesTotalByMajor[series] || 0;
  const notesPerWeek =
    s.span_days > 0 && notesTotal > 0
      ? (notesTotal / (s.span_days / 7)).toFixed(1)
      : '\u2014';
  const tr = document.createElement('tr');
  const tdSeries = document.createElement('td');
  const dot = document.createElement('span');
  dot.className = 'color-dot';
  dot.style.background = COLORS[series];
  dot.setAttribute('aria-hidden', 'true');
  tdSeries.appendChild(dot);
  tdSeries.appendChild(document.createTextNode(series));
  tr.appendChild(tdSeries);
  [
    s.count,
    s.span_days + ' days',
    perWeek,
    notesPerWeek,
    s.first + ' \u2014 ' + s.last,
  ].forEach((text) => {
    const td = document.createElement('td');
    td.textContent = String(text);
    tr.appendChild(td);
  });
  tbody.appendChild(tr);
});

// --- Package size chart (dual-axis) ---
var sizeBlue = getTheme() === 'light' ? DARK_TO_LIGHT['#3b82f6'] : '#3b82f6';
var sizeGreen = getTheme() === 'light' ? DARK_TO_LIGHT['#22c55e'] : '#22c55e';
if (sizeData.length > 0) {
  document.getElementById('sizeChartContainer').style.display = '';
  new Chart(document.getElementById('sizeChart'), {
    type: 'line',
    data: {
      labels: sizeData.map(function (d) {
        return d.timestamp;
      }),
      datasets: [
        {
          label: 'Unpacked Size (MB)',
          data: sizeData.map(function (d) {
            return +(d.unpacked_size / 1048576).toFixed(2);
          }),
          borderColor: sizeBlue,
          backgroundColor: sizeBlue + '44',
          yAxisID: 'ySize',
          tension: 0.3,
          pointRadius: 2,
          fill: true,
        },
        {
          label: 'File Count',
          data: sizeData.map(function (d) {
            return d.file_count;
          }),
          borderColor: sizeGreen,
          backgroundColor: sizeGreen + '44',
          yAxisID: 'yFiles',
          tension: 0.3,
          pointRadius: 2,
          borderDash: [6, 3],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 12, padding: 16 } },
        tooltip: {
          mode: 'index',
          callbacks: {
            title: function (items) {
              return sizeData[items[0].dataIndex].version;
            },
            label: function (item) {
              if (item.datasetIndex === 0)
                return 'Size: ' + item.parsed.y.toFixed(2) + ' MB';
              return 'Files: ' + item.parsed.y;
            },
          },
        },
      },
      scales: {
        x: { type: 'time', time: { unit: 'month' }, grid: { display: false } },
        ySize: {
          type: 'linear',
          position: 'left',
          title: { display: true, text: 'Size (MB)' },
          beginAtZero: false,
        },
        yFiles: {
          type: 'linear',
          position: 'right',
          title: { display: true, text: 'File Count' },
          beginAtZero: false,
          grid: { drawOnChartArea: false },
        },
      },
    },
  });
}

// --- Footer population ---
(function () {
  var totalNotes = notesData.reduce(function (s, d) {
    return s + d.total;
  }, 0);
  var coverageEl = document.getElementById('footer-coverage');
  if (coverageEl)
    coverageEl.textContent =
      releases.length +
      ' releases, ' +
      totalNotes +
      ' changelog entries, ' +
      majorsOrder.length +
      ' version series';
  var genEl = document.getElementById('footer-generated');
  if (genEl) genEl.textContent = 'Generated: __GENERATED_AT__';
})();

// --- Theme toggle ---
var themeBtn = document.getElementById('theme-toggle');
themeBtn.setAttribute(
  'aria-label',
  'Switch to ' + (getTheme() === 'dark' ? 'light' : 'dark') + ' theme',
);
themeBtn.addEventListener('click', function () {
  var next = getTheme() === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  themeBtn.setAttribute(
    'aria-label',
    'Switch to ' + (next === 'dark' ? 'light' : 'dark') + ' theme',
  );
  applyChartTheme();
  applyPalette();
  updateHeatmapTheme();
  var t = THEME_CHART[next];
  [
    'gapChart',
    'weekChart',
    'weekNotesChart',
    'dowChart',
    'hourChart',
    'notesChart',
  ].forEach(function (id) {
    var c = Chart.getChart(id);
    if (!c) return;
    c.data.datasets.forEach(function (ds) {
      var major = ds.label;
      var isFix = !COLORS[major];
      if (isFix) {
        Object.keys(COLORS).forEach(function (k) {
          if (ds.label.startsWith(k)) major = k;
        });
      }
      if (COLORS[major]) {
        var clr = COLORS[major];
        if (id === 'gapChart') {
          ds.backgroundColor = clr + 'cc';
          ds.borderColor = clr;
        } else if (isFix) {
          ds.backgroundColor = COLORS_PALE[major];
          ds.borderColor = clr + '88';
        } else {
          ds.backgroundColor = clr + 'cc';
          ds.borderColor = clr;
        }
        if (ds._hatchType)
          ds.backgroundColor = hatchPattern(ds.backgroundColor, ds._hatchType);
      }
    });
    Object.values(c.options.scales).forEach(function (s) {
      if (s.ticks) s.ticks.color = t.text;
      if (s.title) s.title.color = t.text;
      if (s.grid) s.grid.color = t.border;
      if (s.border) s.border.color = t.border;
    });
    if (c.options.plugins.legend && c.options.plugins.legend.labels) {
      c.options.plugins.legend.labels.color = t.text;
    }
    c.update('none');
  });
  // sizeChart: theme-aware blue/green
  var sc = Chart.getChart('sizeChart');
  if (sc) {
    var sBlue = DARK_TO_LIGHT['#3b82f6'],
      sGreen = DARK_TO_LIGHT['#22c55e'];
    var blue = next === 'light' ? sBlue : '#3b82f6',
      green = next === 'light' ? sGreen : '#22c55e';
    sc.data.datasets[0].borderColor = blue;
    sc.data.datasets[0].backgroundColor = blue + '44';
    sc.data.datasets[1].borderColor = green;
    sc.data.datasets[1].backgroundColor = green + '44';
    Object.values(sc.options.scales).forEach(function (s) {
      if (s.ticks) s.ticks.color = t.text;
      if (s.title) s.title.color = t.text;
      if (s.grid) s.grid.color = t.border;
      if (s.border) s.border.color = t.border;
    });
    if (sc.options.plugins.legend && sc.options.plugins.legend.labels)
      sc.options.plugins.legend.labels.color = t.text;
    sc.update('none');
  }
  // Update table color dots
  document.querySelectorAll('.color-dot').forEach(function (dot, i) {
    if (i < majorsOrder.length) dot.style.background = COLORS[majorsOrder[i]];
  });
});

// --- Anchor links on section headings ---
// Note: innerHTML used here with a static SVG icon string, not untrusted content
document
  .querySelectorAll('.chart-container h2[id], .footer-section h2[id]')
  .forEach((h2) => {
    const a = document.createElement('a');
    a.className = 'anchor-link';
    a.href = '#' + h2.id;
    a.innerHTML =
      '<svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z"/></svg>';
    a.title = 'Copy link to section';
    a.addEventListener('click', (e) => {
      e.preventDefault();
      const url = location.origin + location.pathname + '#' + h2.id;
      navigator.clipboard.writeText(url).then(() => {
        const tip = document.createElement('div');
        tip.className = 'anchor-copied';
        tip.setAttribute('role', 'status');
        tip.textContent = 'Copied!';
        const r = a.getBoundingClientRect();
        tip.style.left = r.right + 6 + 'px';
        tip.style.top = r.top + 'px';
        document.body.appendChild(tip);
        setTimeout(() => tip.remove(), 1200);
      });
      history.replaceState(null, '', '#' + h2.id);
    });
    h2.insertBefore(a, h2.firstChild);
  });
