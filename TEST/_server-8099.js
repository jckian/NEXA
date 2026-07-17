// minimal static server for the repo root on :8099 (python unavailable on this machine)
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = 'C:/SCI-Arc/SP26-RESEARCH/programAgent';
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg', '.json': 'application/json', '.txt': 'text/plain', '.mp4': 'video/mp4' };
http.createServer((req, res) => {
  const urlPath = decodeURIComponent(req.url.split('?')[0]);
  let fp = path.join(ROOT, urlPath);
  if (fp.endsWith('\\') || fp.endsWith('/')) fp += 'index.html';
  fs.readFile(fp, (err, data) => {
    if (err) { console.log('404', req.url); res.writeHead(404); res.end('404'); return; }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(fp).toLowerCase()] || 'application/octet-stream' });
    res.end(data);
  });
}).listen(8099, () => console.log('serving', ROOT, 'on :8099'));
