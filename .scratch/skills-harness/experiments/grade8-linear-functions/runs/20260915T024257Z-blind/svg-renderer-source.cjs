// Render a supplied diagram as pixels for the student-only model read.
const sharp = require('/Users/libo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
sharp(process.argv[2], { density: 144 }).resize({ width: 1600 }).flatten({ background: '#ffffff' }).png().toFile(process.argv[3])
  .then(info => console.log(JSON.stringify({ sharp: sharp.versions.sharp, ...info })))
  .catch(error => { console.error(String(error)); process.exitCode = 1; });
