// Рендер мультика: node render.mjs <name> [preview t1 t2 ...]
// Страница <name>.html отдаёт window.META = {TOTAL, SFX} и window.frameJPEG(t)
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs'; import { spawn } from 'child_process';
const [name, mode = 'video', ...rest] = process.argv.slice(2);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' }).catch(() => chromium.launch());
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('pageerror', e => console.log('ERR', e.message)); page.on('console', m => console.log('console:', m.text()));
await page.goto('file://' + process.cwd() + `/${name}.html?render`);
await page.evaluate(() => window.READY);
const meta = await page.evaluate(() => JSON.parse(JSON.stringify(window.META)));
fs.writeFileSync(`${name}_meta.json`, JSON.stringify(meta));
console.log('TOTAL', meta.TOTAL);
const buf = d => Buffer.from(d.split(',')[1], 'base64');
if (mode === 'preview') {
  fs.mkdirSync('prev', { recursive: true });
  for (const t of rest.map(Number)) fs.writeFileSync(`prev/${name}_${t.toFixed(2)}.jpg`, buf(await page.evaluate(t => window.frameJPEG(t), t)));
} else {
  const fps = 30, n = Math.ceil(meta.TOTAL * fps);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', `${name}_video.mp4`], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    if (!ff.stdin.write(buf(await page.evaluate(t => window.frameJPEG(t), i / fps)))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log('frame', i, '/', n);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await browser.close();
