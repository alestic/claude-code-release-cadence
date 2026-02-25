// [Created with AI: Claude Code with Opus 4.6]
(function () {
  var s = localStorage.getItem('theme');
  if (!s)
    s = window.matchMedia('(prefers-color-scheme:light)').matches
      ? 'light'
      : 'dark';
  document.documentElement.setAttribute('data-theme', s);
})();
