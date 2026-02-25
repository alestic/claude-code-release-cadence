// --- Trend computation (28-day window) ---
const statsGrid = document.getElementById('stats-grid');
const totalDays = Math.round(
  (new Date(releases[releases.length - 1].timestamp) -
    new Date(releases[0].timestamp)) /
    86400000,
);
const overallAvgGap = totalDays / (releases.length - 1);
const overallPerWeek = releases.length / (totalDays / 7);

// 28-day window from last release
const lastTs = new Date(releases[releases.length - 1].timestamp).getTime();
const cutoff28d = lastTs - 28 * 86400000;
const recentReleases = releases.filter(
  (r) => new Date(r.timestamp).getTime() >= cutoff28d,
);
const recentGaps = gaps.filter(
  (g) => new Date(g.timestamp).getTime() >= cutoff28d,
);
const recentAvgGap =
  recentGaps.length > 0
    ? recentGaps.reduce((s, g) => s + g.days, 0) / recentGaps.length
    : overallAvgGap;
const recentPerWeek = recentReleases.length / 4;

// Changelog entry totals and peak week
const totalEntries = notesData.reduce(function (s, d) {
  return s + d.total;
}, 0);
const peakWeekEntries = weekLabels.reduce(function (best, _, wi) {
  let weekTotal = 0;
  majorsOrder.forEach(function (m) {
    weekTotal +=
      (weekNotesStacked[m][wi] || 0) + (weekNotesStackedFixes[m][wi] || 0);
  });
  return Math.max(best, weekTotal);
}, 0);

// Changelog entries per week (overall vs 28d)
const overallEntriesPerWeek = totalEntries / (totalDays / 7);
const recentNotes = notesData.filter(function (d) {
  return new Date(d.timestamp).getTime() >= cutoff28d;
});
const recentEntriesTotal = recentNotes.reduce(function (s, d) {
  return s + d.total;
}, 0);
const recentEntriesPerWeek = recentEntriesTotal / 4;

function trendIndicator(recent, overall, invert) {
  // invert: true means lower is better (for gaps)
  if (overall === 0) return { text: '', cls: 'trend-neutral' };
  const pct = ((recent - overall) / overall) * 100;
  if (Math.abs(pct) < 5)
    return { text: '~ same as overall', cls: 'trend-neutral' };
  const better = invert ? pct < 0 : pct > 0;
  const arrow = pct > 0 ? '\u25B2' : '\u25BC';
  const label =
    Math.abs(pct).toFixed(0) +
    '% ' +
    (pct > 0 ? 'above' : 'below') +
    ' overall avg';
  return {
    arrow: arrow,
    text: label,
    cls: better ? 'trend-positive' : 'trend-negative',
  };
}

const gapTrend = trendIndicator(recentAvgGap, overallAvgGap, true);
const paceTrend = trendIndicator(
  recentEntriesPerWeek,
  overallEntriesPerWeek,
  false,
);

// --- Stats cards (5 cards) ---
[
  {
    label: 'Total Releases',
    value: releases.length,
    detail:
      totalEntries + ' changelog entries in ' + notesData.length + ' releases',
  },
  {
    label: 'Time Span',
    value: totalDays + ' days',
    detail: '~' + Math.round(totalDays / 30) + ' months',
  },
  {
    label: 'Avg Gap',
    value: overallAvgGap.toFixed(1) + ' days',
    detail: 'between consecutive releases',
    trend: gapTrend,
  },
  {
    label: 'Recent Pace',
    value: recentEntriesPerWeek.toFixed(1) + '/week',
    detail: 'changelog entries in last 28 days',
    trend: paceTrend,
  },
  {
    label: 'Peak Week',
    value: peakWeekEntries,
    detail: 'changelog entries in a single week',
  },
].forEach((s) => {
  const card = document.createElement('div');
  card.className = 'stat-card';
  card.setAttribute('role', 'group');
  card.setAttribute('aria-label', s.label + ': ' + s.value);
  const lbl = document.createElement('div');
  lbl.className = 'label';
  lbl.textContent = s.label;
  const val = document.createElement('div');
  val.className = 'value';
  val.textContent = s.value;
  const det = document.createElement('div');
  det.className = 'detail';
  det.textContent = s.detail;
  card.appendChild(lbl);
  card.appendChild(val);
  card.appendChild(det);
  if (s.trend && s.trend.text) {
    const tr = document.createElement('div');
    tr.className = 'trend ' + s.trend.cls;
    if (s.trend.arrow) {
      const ar = document.createElement('span');
      ar.setAttribute('aria-hidden', 'true');
      ar.textContent = s.trend.arrow + ' ';
      tr.appendChild(ar);
    }
    tr.appendChild(document.createTextNode(s.trend.text));
    card.appendChild(tr);
  }
  statsGrid.appendChild(card);
});
