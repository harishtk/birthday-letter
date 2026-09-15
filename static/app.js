/* No external scripts, trackers, or animation dependencies. */
'use strict';
const config = JSON.parse(document.getElementById('birthday-data').dataset.config);
const target = Date.parse(config.target);
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let offset = Date.parse(config.serverNow) - Date.now();
let birthday = false;
const units = ['days', 'hours', 'minutes', 'seconds'];

function remaining(milliseconds) {
  const seconds = Math.max(0, Math.ceil(milliseconds / 1000));
  return [Math.floor(seconds / 86400), Math.floor(seconds / 3600) % 24, Math.floor(seconds / 60) % 60, seconds % 60];
}

function tick() {
  const difference = target - (Date.now() + offset);
  remaining(difference).forEach((value, index) => {
    const element = document.getElementById(units[index]);
    const text = String(value).padStart(2, '0');
    if (element.textContent !== text) {
      element.textContent = text;
      element.classList.remove('tick');
      void element.offsetWidth;
      element.classList.add('tick');
    }
  });
  if (difference <= 0 && !birthday) {
    birthday = true;
    document.getElementById('hero-title').textContent = `Happy birthday, ${config.name}!`;
    document.getElementById('hero-description').textContent = 'Today is yours, my love. May you feel as special, beautiful, and endlessly loved as you make my world feel. Here’s to you—and every wonderful chapter ahead.';
    document.querySelector('.hello').textContent = 'The world is lovelier with you in it.';
    document.querySelector('.hero-note').textContent = 'Your day is here. And my heart is yours. ♡';
    document.getElementById('countdown-title').textContent = 'THE WAIT IS OVER. TODAY, WE CELEBRATE YOU.';
    document.getElementById('countdown-note').textContent = 'A whole new chapter of beautiful things begins. ♡';
    document.getElementById('birthday-announcement').textContent = `Happy birthday, ${config.name}!`;
    document.getElementById('celebrate').hidden = false;
    document.title = `Happy birthday, ${config.name}! ♡`;
    confetti();
  }
}

async function syncClock() {
  const start = Date.now();
  try {
    const response = await fetch('/time', {cache: 'no-store'});
    if (!response.ok || !response.headers.get('content-type')?.includes('application/json')) return;
    const data = await response.json();
    const server = Date.parse(data.now);
    if (Number.isFinite(server)) offset = server - (start + Date.now()) / 2;
    tick();
  } catch { /* The countdown keeps working if the connection drops. */ }
}

let confettiFrame;
function confetti() {
  if (reducedMotion.matches) return;
  cancelAnimationFrame(confettiFrame);
  const canvas = document.getElementById('confetti');
  const context = canvas.getContext('2d');
  if (!context) return;
  const width = window.innerWidth, height = window.innerHeight;
  canvas.width = width; canvas.height = height;
  const colors = ['#b65e7b', '#e3a9b5', '#c7a164', '#f0c5cd', '#92715e'];
  const pieces = Array.from({length: 135}, () => ({x: Math.random() * width, y: -Math.random() * height, speed: 1.8 + Math.random() * 2.5, size: 4 + Math.random() * 6, angle: Math.random() * 6, color: colors[Math.floor(Math.random() * colors.length)]}));
  const start = performance.now();
  let previous = start;
  function frame(now) {
    const step = Math.min((now - previous) / 16.67, 3); previous = now;
    context.clearRect(0, 0, width, height);
    if (now - start > 6500 || reducedMotion.matches) return;
    context.globalAlpha = Math.min(1, (6500 - (now - start)) / 1000);
    pieces.forEach(piece => {
      piece.y += piece.speed * step; piece.x += Math.sin(piece.angle) * .7 * step; piece.angle += .025 * step;
      context.save(); context.translate(piece.x, piece.y); context.rotate(piece.angle);
      context.fillStyle = piece.color; context.fillRect(-piece.size / 2, -piece.size / 2, piece.size, piece.size * .6); context.restore();
    });
    confettiFrame = requestAnimationFrame(frame);
  }
  confettiFrame = requestAnimationFrame(frame);
}

let fortuneIndex = -1;
document.getElementById('fortune-button').addEventListener('click', () => {
  if (!config.fortunes.length) return;
  fortuneIndex = (fortuneIndex + 1) % config.fortunes.length;
  document.getElementById('fortune').textContent = config.fortunes[fortuneIndex];
  document.getElementById('fortune-button').textContent = 'Another little fortune ↗';
});
document.getElementById('celebrate').addEventListener('click', confetti);
document.querySelectorAll('.photo-space img').forEach(img => {
  const fallback = () => {img.hidden = true; img.nextElementSibling.hidden = false;};
  img.addEventListener('error', fallback);
  if (img.complete && !img.naturalWidth) fallback();
});
document.addEventListener('visibilitychange', () => {if (!document.hidden) {tick(); syncClock();}});
window.addEventListener('pageshow', syncClock);
tick();
setInterval(tick, 250);
setInterval(syncClock, 60000);
