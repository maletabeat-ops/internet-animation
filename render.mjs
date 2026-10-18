import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs'; import { spawn } from 'child_process';
const tl = fs.readFileSync('timeline.json', 'utf8');
const html = fs.readFileSync('anim.html', 'utf8').replace('/*TIMELINE*/[]', tl);
fs.writeFileSync('build.html', html);
const mode = process.argv[2] || 'preview';
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' , args:['--disable-gpu-vsync']}).catch(()=>chromium.launch());
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('console', m => console.log('console:', m.text())); page.on('pageerror', e => console.log('ERR', e.message));
await page.goto('file://' + process.cwd() + '/build.html?render');
await page.evaluate(() => window.READY);
const meta = await page.evaluate(() => JSON.parse(JSON.stringify(window.META)));
fs.writeFileSync('meta.json', JSON.stringify(meta));
console.log('TOTAL', meta.TOTAL);
const save = (d, f) => fs.writeFileSync(f, Buffer.from(d.split(',')[1], 'base64'));
if (mode === 'preview') {
  fs.mkdirSync('prev', { recursive: true });
  const ts = process.argv.slice(3).map(Number);
  for (const t of ts) save(await page.evaluate(t => window.frameJPEG(t), t), `prev/f_${t.toFixed(2)}.jpg`);
} else {
  const fps = 30, n = Math.ceil(meta.TOTAL * fps);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', 'video.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    const d = await page.evaluate(t => window.frameJPEG(t), i / fps);
    if (!ff.stdin.write(Buffer.from(d.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 300 === 0) console.log('frame', i, '/', n);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await browser.close();
