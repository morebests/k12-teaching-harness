// 有界输入由调用方检查；只排版公式，不启用可信 HTML 或外部资源。
const katex = require('katex');
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const formulas = JSON.parse(input);
    const errors = [];
    const html = formulas.map(([text, display], index) => {
      try {
        return katex.renderToString(text, {
          output: 'mathml', displayMode: display, throwOnError: true, trust: false,
          strict: 'error', maxExpand: 100, maxSize: 20
        });
      } catch (error) {
        if (!(error instanceof katex.ParseError)) throw error;
        errors.push({index, message: error.message.slice(0, 500)});
        return null;
      }
    });
    process.stdout.write(JSON.stringify({html, errors}));
  } catch (error) {
    process.stderr.write('公式排版失败，请核对 LaTeX 语法。');
    process.exitCode = 1;
  }
});
