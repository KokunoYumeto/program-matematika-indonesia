// Headless local-file rendering checks. No user browser, web server or network.
import {createRequire} from 'node:module';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {resolve, join} from 'node:path';
import {pathToFileURL} from 'node:url';
const [readerArg, outputArg, epubArg, locatorArg] = process.argv.slice(2);
if (!readerArg || !outputArg || (epubArg && !locatorArg)) throw Error('Usage: node check_reader.mjs READER QA_OUTPUT [EXTRACTED_EPUB FORMAT_ENTRY_LOCATORS.json]');
const require = createRequire(import.meta.url);
const {chromium} = require(process.env.COURSE_PLAYWRIGHT_MODULE || 'playwright');
const reader = resolve(readerArg), out = resolve(outputArg);
await mkdir(out, {recursive:true});
const browser = await chromium.launch({headless:true, executablePath:process.env.COURSE_CHROMIUM || undefined});
const cases = [], network = [], errors = [];
try {
  for (const language of ['en','id']) for (const width of [1280,390,320]) {
    const context = await browser.newContext({viewport:{width,height:850}});
    await context.route(/https?:\/\//, route=>{network.push(route.request().url());return route.abort();});
    const page = await context.newPage();
    page.on('pageerror', error=>errors.push(String(error)));
    await page.goto(pathToFileURL(join(reader,`index.${language}.html`)).href);
    const state = await page.evaluate(()=>({
      language:document.documentElement.lang,
      overflow:document.documentElement.scrollWidth>innerWidth+1,
      downloads:[...document.querySelectorAll('.downloads a')].map(a=>a.getAttribute('href')),
      lessonLinks:[...document.querySelectorAll('ol a')].map(a=>a.getAttribute('href')),
      scripts:document.scripts.length,
      fileLinks:[...document.querySelectorAll('a')].map(a=>a.getAttribute('href')),
    }));
    if(state.language!==language||state.overflow||state.downloads.length!==4||state.scripts)throw Error(JSON.stringify(state));
    for(const href of new Set(state.fileLinks.map(href=>href.split('#')[0]))) {
      const path=resolve(reader, decodeURIComponent(href));
      await readFile(path);
    }
    const other = language==='en'?'id':'en';
    await page.locator(`nav a[lang="${other}"]`).click();
    if(await page.locator('html').getAttribute('lang')!==other)throw Error('Language switch failed');
    await page.goto(pathToFileURL(join(reader,`index.${language}.html`)).href);
    if(width===390)await page.screenshot({path:join(out,`reader-${language}-390.png`),fullPage:true});
    if(await page.locator('ol details').count()) {
      await page.locator('ol details summary').first().click();
      if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Expanded native links overflow');
      if(width===390)await page.screenshot({path:join(out,`native-locations-${language}-390.png`)});
    }
    const {fileLinks,lessonLinks,...compact}=state;
    cases.push({kind:'offline_reader',language,width,...compact,checked_links:fileLinks.length,lesson_links:lessonLinks.length});
    await context.close();
  }
  if(epubArg) {
    const epub=resolve(epubArg);
    // Use the intake's verified native routes, never title-based inference.
    const locators=JSON.parse(await readFile(resolve(locatorArg),'utf8'));
    const unique=locators.locators.map(e=>({member:e.epub.member,id:e.lesson_id}));
    if(!unique.length||new Set(unique.map(e=>e.id)).size!==unique.length)throw Error('Missing or duplicate lesson routes');
    for(const entry of unique)for(const width of [1280,390]) {
      const context=await browser.newContext({viewport:{width,height:850}});
      await context.route(/https?:\/\//,route=>{network.push(route.request().url());return route.abort();});
      const page=await context.newPage();
      const member=resolve(epub,entry.member);
      if(!member.startsWith(epub+'/')&&!member.startsWith(epub+'\\'))throw Error('EPUB preview path outside extraction');
      await page.goto(pathToFileURL(member).href);
      await page.evaluate(()=>document.fonts.ready);
      const state=await page.evaluate(()=>({
        overflow:document.documentElement.scrollWidth>innerWidth+1,
        math:document.querySelectorAll('math').length,
        mathErrors:document.querySelectorAll('merror').length,
        brokenImages:[...document.images].filter(i=>!i.complete||i.naturalWidth===0).length,
      }));
      if(state.overflow||state.mathErrors||state.brokenImages)throw Error(JSON.stringify({entry,width,state}));
      if(width===390&&await page.locator('img').count()) {
        await page.locator('img').first().scrollIntoViewIfNeeded();
        await page.screenshot({path:join(out,`epub-figure-${entry.id.replace(/[^a-zA-Z0-9_-]/g,'_')}-390.png`)});
      }
      cases.push({kind:'epub_native_mathml',lesson:entry.id,width,...state});
      await context.close();
    }
  }
} finally {await browser.close();}
if(network.length||errors.length)throw Error(JSON.stringify({network,errors}));
const receipt={state:'pass',cases,network_requests:network.length,script_errors:errors,limits:['Geometry tests are not complete visual or assistive-technology review.','PDF visual sample recorded separately.']};
await writeFile(join(out,'browser-check.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({state:'pass',cases:cases.length,network_requests:network.length}));
