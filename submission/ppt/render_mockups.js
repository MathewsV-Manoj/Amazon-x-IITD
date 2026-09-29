const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ deviceScaleFactor: 3 });
  const fonts = path.resolve(__dirname, '../fonts');
  for (const name of ['mockup_tier3', 'mockup_agent', 'mockup_tier2']) {
    const svg = fs.readFileSync(path.resolve(__dirname, `../assets/${name}.svg`), 'utf8');
    await p.setContent(`<html><head><style>
      @font-face{font-family:"IBM Plex Sans";src:url("file://${fonts}/IBMPlexSans-Regular.ttf");font-weight:400}
      @font-face{font-family:"IBM Plex Sans";src:url("file://${fonts}/IBMPlexSans-SemiBold.ttf");font-weight:600 900}
      body{margin:0;background:transparent} svg{display:block;width:${name==='mockup_agent'?960:450}px;height:auto}</style></head>
      <body>${svg.slice(svg.indexOf('<svg'))}</body></html>`);
    await p.evaluate(() => document.fonts.ready);
    await p.locator('svg').screenshot({ path: `${name}.png`, omitBackground: true });
    console.log('wrote', name);
  }
  await b.close();
})();
