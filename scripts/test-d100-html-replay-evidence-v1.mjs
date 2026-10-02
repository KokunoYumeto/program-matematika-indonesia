import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadD100HtmlReplay,validateD100HtmlReplay} from './d100-html-replay-evidence-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const {raw}=await loadD100HtmlReplay(root);
let rejected=0;
function mutate(key,edit,rebind=false) {
  const copy={...raw},value=JSON.parse(copy[key]);edit(value);
  copy[key]=Buffer.from(JSON.stringify(value));
  if(rebind) {
    const summary=JSON.parse(copy.d100HtmlReplay), row=summary.readers.find(r=>key.toLowerCase().includes(r.lane));
    row.proof.bytes=copy[key].length;
    row.proof.sha256=createHash('sha256').update(copy[key]).digest('hex');
    copy.d100HtmlReplay=Buffer.from(JSON.stringify(summary));
  }
  assert.throws(()=>validateD100HtmlReplay(copy));rejected++;
}
for(const key of ['native_data_export_replayed','fresh_pdf_build','semantic_canon_review','whole_backend_complete'])
  mutate('d100HtmlReplay',v=>v[key]=true);
mutate('d100HtmlReplay',v=>v.source_units=92);
mutate('d100HtmlReplay',v=>v.companion_units=0);
mutate('d100HtmlReplay',v=>v.readers.pop());
mutate('d100HtmlReplay',v=>v.locale='en');
mutate('d100BgkHtmlReplay',v=>v.runs.pop(),true);
mutate('d100BgkHtmlReplay',v=>v.runs[1].html.sha256='0'.repeat(64),true);
mutate('d100BgkHtmlReplay',v=>v.runs[0].source_files=267,true);
mutate('d100BgkHtmlReplay',v=>v.runtime_producer_sources_used=true,true);
mutate('d100ClassicalHtmlReplay',v=>v.producer_writes=true,true);
mutate('d100OriginalHtmlReplay',v=>v.runs[0].html_checks.broken_internal_or_bundled_links=1,true);
mutate('d100OriginalHtmlReplay',v=>v.runs[1].html_checks.mathml_nodes=0,true);
mutate('d100OriginalHtmlReplay',v=>v.runs[0].bundled_bgk.sha256='f'.repeat(64),true);
console.log(JSON.stringify({state:'pass',rejected_mutations:rejected,scope:'native HTML proof, not native backend/PDF/canon closure'}));
