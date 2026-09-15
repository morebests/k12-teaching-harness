// Organizer-only renderer. It preserves model content; it does not repair worksheets.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { marked } = require('/Users/libo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/marked');
const katex = require('katex');
const root = path.resolve(__dirname, '..');
const run = path.resolve(root, 'runs', process.argv[2]);
if (!run.startsWith(path.join(root, 'runs') + path.sep)) throw Error('Expected experiment run');
const output = path.join(run, 'review');
fs.mkdirSync(output, { recursive: true });
const shared = path.join(root, 'runs', '.render-assets');
fs.mkdirSync(shared, { recursive: true });
fs.copyFileSync(path.join(__dirname, 'node_modules/katex/dist/katex.min.css'), path.join(shared, 'katex.min.css'));
fs.cpSync(path.join(__dirname, 'node_modules/katex/dist/fonts'), path.join(shared, 'fonts'), { recursive: true });
const digest = s => crypto.createHash('sha256').update(s).digest('hex');
const records = [];
for (const name of process.argv.slice(3)) {
  if (!/^[\w.-]+\.md$/.test(name)) throw Error('Expected flat Markdown filename');
  const original = fs.readFileSync(path.join(run, 'artifacts', name), 'utf8');
  const slots = [], errors = [];
  const hold = html => { const id = slots.push(html) - 1; return `RENDERPLACEHOLDER${id}END`; };
  const math = (formula, displayMode) => {
    try { return hold(katex.renderToString(formula, { displayMode, throwOnError: true, trust: false, strict: 'ignore' })); }
    catch (e) { errors.push({ formula, error: String(e) }); return hold(`<pre>${formula.replaceAll('&','&amp;').replaceAll('<','&lt;')}</pre>`); }
  };
  let text = original.replace(/```[^\n]*\n[\s\S]*?```/g, block => hold(marked.parse(block)));
  text = text.replace(/`([^`\n]+)`/g, (_, code) => hold('<code>' + code.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;') + '</code>'));
  text = text.replace(/(?<!\\)\$\$([\s\S]*?)(?<!\\)\$\$/g, (_, m) => math(m.trim(), true));
  text = text.replace(/(?<!\\)\$((?:\\.|[^\n$\\])+?)(?<!\\)\$/g, (_, m) => math(m, false));
  text = text.replace(/\\pagebreak/g, '<div class="pagebreak"></div>');
  let body = marked.parse(text).replace(/RENDERPLACEHOLDER(\d+)END/g, (_, i) => slots[Number(i)]);
  body = body.replace(/src="([\w.-]+\.svg)"/g, 'src="../artifacts/$1"');
  const html = `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${name}</title><link rel="stylesheet" href="../../.render-assets/katex.min.css"><style>
  body{max-width:900px;margin:40px auto;padding:0 32px;font:17px/1.55 Georgia,serif;color:#171717;background:white}h1,h2,h3,h4{font-family:system-ui,sans-serif;line-height:1.25}h1{margin-top:2em}h3{margin-top:2em}table{border-collapse:collapse;margin:20px 0;width:100%;font-size:15px}th,td{border:1px solid #aaa;padding:9px;vertical-align:top}img{max-width:100%;height:auto;display:block;margin:24px auto}pre{overflow:auto;background:#f6f6f6;padding:12px;font-size:13px}blockquote{border-left:3px solid #999;padding-left:18px;margin-left:0}.pagebreak{height:24px;border-top:1px solid #bbb;margin-top:40px}.notice{font:13px system-ui;padding:12px;border:1px solid #bbb}.katex{font-size:1.05em}.katex-display{overflow-x:auto;padding:8px 0}@media print{body{margin:0;font-size:11pt;max-width:none}.notice{display:none}.pagebreak{break-before:page;border:0;height:0}h1,h2,h3,h4{break-after:avoid}img,table{break-inside:avoid}}
  </style><body><div class="notice">Research candidate · ${path.basename(run)} · Rendering preserves the original content. This preview is not classroom or print acceptance.</div>${body}</body></html>`;
  const filename = name.replace(/\.md$/, '.html');
  fs.writeFileSync(path.join(output, filename), html);
  records.push({ source: name, source_sha256: digest(original), output: filename, output_sha256: digest(html), math_errors: errors });
}
fs.writeFileSync(path.join(output, 'render-manifest.json'), JSON.stringify({ katex: katex.version, renderer_sha256: digest(fs.readFileSync(__filename)), records }, null, 2));
console.log(JSON.stringify({ run: path.basename(run), records: records.map(r => ({...r, math_errors: r.math_errors.length})) }));
