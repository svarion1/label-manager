// Fade out flash messages after a few seconds.
document.querySelectorAll('.flash').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  }, 4000);
});

// Register the service worker (scanner PWA).
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js').catch(() => {});
  });
}

// Apply category colors from data-bg attributes.
document.querySelectorAll('[data-bg]').forEach(el => {
  el.style.background = el.dataset.bg;
});