import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {interfaceCourses,coursePresentation,escapeMarkup as esc} from '../docs/interface/view.js';
import {siteOrigin} from '../docs/interface/locales.js';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const input='docs/interface/learner-access-manifest.json';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const order={pdf:0,tex:1,zip:2,epub:3};
export function downloadFormat(resource){
  const url=new URL(resource.url);
  assert.equal(url.protocol,'https:','Download must use HTTPS');
  assert.ok(!url.username&&!url.password,'Credentials in download URL');
  const pathname=decodeURIComponent(url.pathname).toLowerCase();
  const extension=pathname.match(/\.(pdf|tex|zip|epub)$/)?.[1];
  if(extension)return extension;
  const declared=String(resource.media_type??'').toLowerCase();
  return ['pdf','tex','epub'].includes(declared)?declared:null;
}
export function collectDownloads(manifest){
  assert.equal(manifest.schema_name,'learner-access-presentation');
  assert.equal(manifest.schema_version,'1.0.0');
  assert.deepEqual(Object.keys(manifest.courses).sort(),interfaceCourses.map(c=>c.id).sort());
  const resources=new Map(),courses=[];
  for(const course of interfaceCourses){
    const row={course_id:course.id,locales:{}};
    for(const locale of ['id','en']){
      const view=manifest.courses[course.id][locale];
      assert.equal(view.course_id,course.id);assert.equal(view.interface_locale,locale);
      assert.equal(view.locale_route,siteOrigin+locale+'/#course-'+course.id);
      const entries=[...view.program_hosted_reader.resources,...view.authoritative_original.resources,
        ...view.offline_copies,...view.alternatives];
      const selections=new Map();
      for(const resource of entries){
        if(resource.content_language!==locale)continue;
        const format=downloadFormat(resource);if(!format)continue;
        const key=locale+'\0'+resource.url;
        const fileId='file-'+hash(Buffer.from(key)).slice(0,20);
        const fact={id:fileId,url:resource.url,content_language:locale,format,
          bytes:resource.bytes??null,sha256:resource.sha256??null,
          verification:'catalogue_binding_not_fresh_file_or_edition_validation'};
        if(fact.bytes!==null)assert.ok(Number.isSafeInteger(fact.bytes)&&fact.bytes>0);
        if(fact.sha256!==null)assert.match(fact.sha256,/^[0-9a-f]{64}$/i);
        const previous=resources.get(key);
        if(previous){
          assert.equal(previous.format,fact.format,'Conflicting format for one URL');
          for(const field of ['bytes','sha256']){
            if(previous[field]!==null&&fact[field]!==null)assert.equal(previous[field],fact[field],'Conflicting declared file identity');
            if(previous[field]===null)previous[field]=fact[field];
          }
        }else resources.set(key,fact);
        if(!selections.has(fileId))selections.set(fileId,{resource_id:fileId,label:resource.label,
          label_language:resource.label_language,authority_roles:[],access_roles:[]});
        const selection=selections.get(fileId);
        for(const [field,value] of [['authority_roles',resource.authority_role],['access_roles',resource.access_role]]){
          assert.equal(typeof value,'string');if(!selection[field].includes(value))selection[field].push(value);
        }
      }
      const byId=new Map([...resources.values()].map(r=>[r.id,r]));
      row.locales[locale]={title:coursePresentation(course,locale).title,course_url:view.locale_route,
        downloads:[...selections.values()].sort((a,b)=>order[byId.get(a.resource_id).format]-order[byId.get(b.resource_id).format]||a.resource_id.localeCompare(b.resource_id,'en'))};
    }
    courses.push(row);
  }
  const files=[...resources.values()].sort((a,b)=>a.id.localeCompare(b.id,'en'));
  const byId=new Map(files.map(r=>[r.id,r]));
  const counts=Object.fromEntries(['id','en'].map(locale=>[locale,{
    courses:courses.length,unique_files:files.filter(r=>r.content_language===locale).length,
    roles_by_format:Object.fromEntries(Object.keys(order).map(format=>[format,courses.filter(c=>c.locales[locale].downloads.some(d=>byId.get(d.resource_id).format===format)).length]))
  }]));
  return {schema:'course-download-catalogue/1',scope:'Existing indexed downloads for the forty core course roles; actual content language, not interface language.',
    counts,resources:files,courses,edition_policy:'Never infer that adjacent formats are the same edition or pair a PDF with an unverified source ZIP. Preserve each exact source link and use the edition record for version, rights and provenance.',
    absence_policy:'No indexed download is not a claim that a format does not exist.',
    advanced_courses:'Separate current-edition export intake; private source snapshots are not exposed by this catalogue.',
    new_translation:false,new_mathematical_review:false,new_format_exports:false};
}
const copy={
  id:{title:'Unduhan buku dan sumber',brand:'Program Matematika',notes:'Format dan keterangan edisi',intro:'Pilih mata kuliah dan format untuk belajar atau menyimpan bahan secara luring.',
    home:'Peta belajar',language:'Bahasa',search:'Cari judul atau kode',filter:'Format',all:'Semua format',reset:'Atur ulang',
    count:'mata kuliah ditampilkan',open:'Buka mata kuliah, edisi dan asal-usul sumber',none:'Belum ada unduhan langsung yang terindeks untuk bahasa ini. Periksa halaman mata kuliah; ini bukan pernyataan bahwa berkasnya tidak ada.',
    empty:'Tidak ada mata kuliah yang cocok.',note:'Daftar ini memakai tautan edisi yang sudah terindeks. Berkas yang berdekatan belum tentu berasal dari edisi yang sama. Periksa versi, cakupan, lisensi dan sumber pada halaman edisi sebelum menggabungkannya.',
    offline:'Halaman katalog dapat dibaca tanpa JavaScript. Mengunduh berkas memerlukan internet; ZIP dapat berisi HTML, sumber atau bahan lain sesuai labelnya. Katalog ini tidak membuat EPUB atau PDF baru.',
    original:'Sumber asli',edition:'Bahan edisi',details:'Identitas berkas yang tercatat',unverified:'Identitas unduhan belum dicatat; tidak diverifikasi ulang oleh katalog ini.',
    evidence:'Data katalog dan ikatan sumber',summary:'Cakupan tautan menurut format, bukan persentase penyelesaian buku',
    provenance:'Katalog ini diproyeksikan secara deterministik dari metadata edisi yang sudah ada. Tidak ada penerjemahan, koreksi matematika atau peninjauan buku baru; atribusi manusia dan model AI tetap mengikuti setiap edisi.',
    formats:{pdf:'PDF',tex:'LaTeX langsung',zip:'Arsip ZIP',epub:'EPUB'}},
  en:{title:'Book and source downloads',brand:'Mathematics Program',notes:'Formats and edition notes',intro:'Choose a course and format for reading or keeping materials offline.',
    home:'Learning map',language:'Language',search:'Search title or code',filter:'Format',all:'All formats',reset:'Reset',
    count:'courses shown',open:'Open course, editions and provenance',none:'No direct download is indexed for this language yet. Check the course page; this does not mean the files do not exist.',
    empty:'No matching courses.',note:'These are existing indexed edition links. Adjacent formats are not necessarily the same edition. Check version, scope, licence and source on the edition page before combining them.',
    offline:'All catalogue links work without JavaScript. Downloads need an internet connection; a ZIP may contain HTML, source or other material as its label describes. This catalogue does not create new EPUBs or PDFs.',
    original:'Original source',edition:'Edition material',details:'Recorded file identity',unverified:'No download identity recorded; not reverified by this catalogue.',
    evidence:'Catalogue data and source binding',summary:'Course coverage by indexed format, not book-completion percentages',
    provenance:'This catalogue is a deterministic projection of existing edition metadata. It adds no book translation, mathematical corrections or review; human and AI-model attribution remains with each edition.',
    formats:{pdf:'PDF',tex:'Direct LaTeX',zip:'ZIP archive',epub:'EPUB'}}
};
export function renderDownloadPage(model,locale){
  assert.ok(copy[locale]);const t=copy[locale],byId=new Map(model.resources.map(r=>[r.id,r]));
  const tool=locale==='id'?{
    title:'Siapkan edisi luring dari ekspor yang sudah ada',
    text:'Untuk pengajar dan pengelola bahan: alat ini memeriksa ikatan sumber PDF, LaTeX, ZIP dan EPUB, lalu membuat direktori bacaan luring dengan pilihan bahasa antarmuka dan tautan pelajaran. Berkas sumber tidak diubah. Ini bukan konverter PDF/EPUB dan tidak berarti semua mata kuliah telah memiliki semua format.',
    download:'Unduh alat dan kode sumber lengkap',
    note:'Baca README.id.txt dalam arsip. Jalankan alat pada paket lokal yang sesuai; tidak ada unggahan otomatis. Bahasa antarmuka tidak mengubah bahasa isi. Mata kuliah privat tidak disertakan.',
    credit:'Alat dan integrasi format: OpenAI Codex - GPT-6 Astra, upaya Ultra. Atribusi dan lisensi setiap mata kuliah tetap mengikuti sumber aslinya.'
  }:{
    title:'Prepare an offline edition from existing exports',
    text:'For educators and maintainers: this tool verifies the source bindings of PDF, LaTeX, ZIP and EPUB files, then creates an offline reading directory with language controls and lesson links. Source files are unchanged. It is not a PDF/EPUB converter and does not mean every course has every format.',
    download:'Download the toolkit and complete source',
    note:'Read README.txt in the archive. Run it against a compatible local package; nothing is uploaded automatically. Interface language does not change content language. No private courses are included.',
    credit:'Format tools and integration: OpenAI Codex - GPT-6 Astra, Ultra effort. Each course retains its original attribution and licences.'
  };
  const cards=`<aside id="format-tools"><details><summary>${tool.title}</summary><p>${tool.text}</p><p><a href="../../downloads/course-format-tools-v1.zip">${tool.download}</a></p><p>${tool.note}</p><small>${tool.credit}</small></details></aside>`+model.courses.map(course=>{
    const row=course.locales[locale];const formats=[...new Set(row.downloads.map(r=>byId.get(r.resource_id).format))];
    const links=row.downloads.map(binding=>{
      const resource=byId.get(binding.resource_id);assert.equal(resource.content_language,locale);
      const original=binding.authority_roles.includes('upstream-authority');
      const identity=resource.sha256?`<details><summary>${t.details}</summary><p>${resource.bytes??'?'} bytes · SHA-256 <code>${resource.sha256}</code></p></details>`:`<small>${t.unverified}</small>`;
      return `<li data-file-id="${resource.id}" data-format="${resource.format}"><a href="${esc(resource.url)}" hreflang="${locale}"><strong>${t.formats[resource.format]}</strong> · <span lang="${esc(binding.label_language)}">${esc(binding.label)}</span></a><small>${original?t.original:t.edition}</small>${identity}</li>`;
    }).join('\n');
    return `<article id="course-${course.course_id}" data-course="${course.course_id}" data-formats="${formats.join(' ')}"><h2>${course.course_id} · ${esc(row.title)}</h2>${links?`<ul>${links}</ul>`:`<p>${t.none}</p>`}<p><a href="${esc(row.course_url)}">${t.open}</a></p></article>`;
  }).join('\n');
  return `<!doctype html>
<html lang="${locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${t.title} · ${t.brand}</title><link rel="canonical" href="${siteOrigin+locale+'/downloads/'}"><style>
.filters label{min-width:0;max-width:100%}.filters label:first-child{flex:1 1 18rem}input#search{width:100%}
*{box-sizing:border-box}body{margin:0;color:#18302e;background:#f5f3ed;font:17px/1.6 system-ui,sans-serif}header,main,footer{max-width:1100px;margin:auto;padding:1.3rem}header{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap}nav{display:flex;gap:1rem;flex-wrap:wrap}a{color:#075e64;text-underline-offset:3px;overflow-wrap:anywhere}a:focus-visible,input:focus-visible,select:focus-visible,button:focus-visible{outline:3px solid #ba6900;outline-offset:3px}h1{font-size:clamp(1.8rem,5vw,3rem);line-height:1.15}h2{font-size:1.35rem}.note{border-left:4px solid #ae6a1c;padding:.4rem 1rem;background:#fff8e8}.filters{display:flex;gap:1rem;flex-wrap:wrap;align-items:end}label{display:grid;gap:.3rem}input,select,button{font:inherit;max-width:100%;padding:.55rem;border:1px solid #607875;border-radius:5px}input{width:21rem}button{cursor:pointer}.counts{display:flex;gap:.6rem;flex-wrap:wrap}.counts span{padding:.35rem .75rem;background:#dfece7;border-radius:6px}article{background:white;border:1px solid #d2dcd6;border-radius:10px;padding:1rem 1.3rem;margin:1rem 0;scroll-margin-top:1rem}ul{padding-left:1.3rem}li{margin:1rem 0}small{display:block;color:#4d625f}code{overflow-wrap:anywhere;font-size:.8rem}details{font-size:.9rem}footer{font-size:.9rem}.skip{position:absolute;left:-10000px}.skip:focus{position:static}body:not(.enhanced) .filters{display:none}[hidden]{display:none!important}
</style></head><body><a class="skip" href="#catalogue">${t.title}</a><header><a href="../">← ${t.home}</a><nav aria-label="${t.language}"><a data-language="id" href="../../id/downloads/" lang="id"${locale==='id'?' aria-current="page"':''}>Bahasa Indonesia</a><a data-language="en" href="../../en/downloads/" lang="en"${locale==='en'?' aria-current="page"':''}>English</a></nav></header><main><h1>${t.title}</h1><p>${t.intro}</p><section class="filters"><label>${t.search}<input id="search" type="search" autocomplete="off"></label><label>${t.filter}<select id="format"><option value="">${t.all}</option>${Object.keys(order).map(f=>`<option value="${f}">${t.formats[f]}</option>`).join('')}</select></label><button id="reset" type="button">${t.reset}</button></section><p id="count" role="status">${model.courses.length}/${model.courses.length} ${t.count}</p><p id="empty" hidden>${t.empty}</p><details class="edition-notes"><summary>${t.notes}</summary><p>${t.summary}</p><div class="counts">${Object.keys(order).map(f=>`<span>${t.formats[f]}: ${model.counts[locale].roles_by_format[f]}/${model.courses.length}</span>`).join('')}</div><p class="note">${t.note}</p><p>${t.offline}</p></details><section id="catalogue">${cards}</section></main><footer><p>${t.provenance}</p><a href="../../interface/course-downloads-v1.json">${t.evidence}</a></footer><script>
document.body.classList.add('enhanced');const cards=[...document.querySelectorAll('[data-course]')],search=document.querySelector('#search'),format=document.querySelector('#format');function filter(){const query=search.value.trim().toLocaleLowerCase(),exactCode=cards.some(card=>card.dataset.course.toLowerCase()===query);let shown=0;for(const card of cards){const matches=exactCode?card.dataset.course.toLowerCase()===query:card.querySelector('h2').textContent.toLocaleLowerCase().includes(query);const visible=matches&&(!format.value||card.dataset.formats.split(' ').includes(format.value));card.hidden=!visible;if(visible)shown++;}document.querySelector('#count').textContent=shown+'/'+cards.length+' ${t.count}';document.querySelector('#empty').hidden=shown!==0;}search.addEventListener('input',filter);format.addEventListener('change',filter);document.querySelector('#reset').addEventListener('click',()=>{search.value='';format.value='';filter();});function languages(){for(const a of document.querySelectorAll('[data-language]')){const u=new URL(a.href);u.hash=location.hash;a.href=u.href;}}languages();addEventListener('hashchange',languages);
</script></body></html>\n`;
}
export async function buildDownloads(){
  const bytes=await readFile(resolve(root,input));const model=collectDownloads(JSON.parse(bytes));
  model.source={path:'interface/learner-access-manifest.json',bytes:bytes.length,sha256:hash(bytes)};
  const outputs=[];
  for(const locale of ['id','en']){
    const path=`docs/${locale}/downloads/index.html`,data=Buffer.from(renderDownloadPage(model,locale));
    await mkdir(dirname(resolve(root,path)),{recursive:true});await writeFile(resolve(root,path),data);outputs.push({path,bytes:data.length,sha256:hash(data)});
  }
  const path='docs/interface/course-downloads-v1.json',data=Buffer.from(JSON.stringify(model,null,2)+'\n');
  await writeFile(resolve(root,path),data);outputs.push({path,bytes:data.length,sha256:hash(data)});
  console.log(JSON.stringify({state:'pass',counts:model.counts,outputs}));return {model,outputs};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)await buildDownloads();
