import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const read = path => readFile(resolve(root,path),'utf8');
const contract = JSON.parse(await read('backend/authority/central-reader-navigation-v1.json'));
const handoff = JSON.parse(await read('backend/authority/library-handoff-v1.json'));
const hub = contract.reciprocal_hubs.find(row=>row.id==='mathematics-library');
assert.equal(hub.public_url, handoff.public_url);
assert.deepEqual([...hub.linked_from_locales].sort(),Object.keys(contract.interfaces).sort());
for(const row of handoff.deploy_only) {
  const bytes=await readFile(resolve(root,'docs/library',row.path));
  assert.equal(bytes.length,row.bytes);
  assert.equal(createHash('sha256').update(bytes).digest('hex'),row.sha256.toLowerCase());
}
const escape = text => text.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
function check(html, locale) {
  const link = '<a data-library-link="v1" href="'+hub.public_url+'">'+escape(hub.labels[locale])+'</a>';
  const header = html.match(/<header\b[^>]*>[\s\S]*?<\/header>/)?.[0];
  const footer = html.match(/<footer\b[^>]*>[\s\S]*?<\/footer>/)?.[0];
  assert(header?.includes(link),'Missing visible localized Library link in header');
  assert(footer?.includes(link),'Missing visible localized Library link in footer');
  assert.equal(html.split(link).length-1,2,'Exactly two Library navigation links');
}
let count=0;
const css=await read('docs/interface/styles.css');
const cssRevision=createHash('sha256').update(css).digest('hex').slice(0,12);
assert(css.includes('.course-card{min-width:0;overflow-wrap:anywhere;'));
assert(css.includes('.course-grid,.filters{grid-template-columns:minmax(0,1fr)}'));
for(const locale of Object.keys(contract.interfaces)) {
  for(const file of ['index.html','learning-map.html','learning-map-paired.html']) {
    const html=await read('docs/'+locale+'/'+file);
    check(html,locale);
    if(file==='index.html') assert(html.includes('href="../interface/styles.css?v='+cssRevision+'"'));
    else assert(html.includes(css),'Offline map must contain the same mobile layout fix');
    assert.throws(()=>check(html.replace('data-library-link="v1"','data-library-link="broken"'),locale));
    assert.throws(()=>check(html.replace(hub.public_url,hub.public_url+'missing/'),locale));
    count++;
  }
}
const rootHtml=await read('docs/index.html');
const chooser=rootHtml.match(/<!-- GENERATED-INTERFACE-LOCALES-START -->[\s\S]*?<!-- GENERATED-INTERFACE-LOCALES-END -->/)?.[0];
assert(chooser?.includes('<a data-library-link="v1" href="'+hub.public_url+'">Perpustakaan / Library</a>'));
for(const locale of Object.keys(contract.interfaces)) assert(chooser.includes('data-interface-locale="'+locale+'"'));
console.log(JSON.stringify({state:'pass',localized_documents:count,root_chooser:true,negative_fixtures:count*2,library_registry_unchanged:true}));
