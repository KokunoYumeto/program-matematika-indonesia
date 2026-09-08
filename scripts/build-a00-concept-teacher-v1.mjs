import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {projectA00} from './a00_concept_model_v1.mjs';

export const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
export const base='backend/course-capsule-v1/adapters/a00-concept-teacher-v1';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const json=value=>JSON.stringify(value,null,2)+'\n';
const escape=value=>String(value).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const origin='https://kokunoyumeto.github.io/program-matematika-indonesia';
const labels={
  id:{title:'Konsep dan latihan A00',teacherTitle:'Pilihan belajar A00 untuk pengajar',program:'Kembali ke program',
    learner:'Untuk pelajar',teacher:'Untuk pengajar',language:'Bahasa',skip:'Lewati ke isi',
    intro:'Pilih konsep untuk membuka definisi, prasyarat, dan modul bacaan. Buku yang ditautkan berbahasa Indonesia.',
    concepts:'konsep',modules:'modul',assessments:'latihan dan contoh',solutions:'solusi sumber',gaps:'tanpa solusi sumber',
    conceptHeading:'Konsep dan prasyarat',conceptQuery:'Cari konsep',role:'Lingkup konsep',all:'Semua',
    roles:{a00_core:'Konsep inti A00',a00_supporting:'Konsep pendukung',a10_bridge:'Pengantar A10'},
    prerequisites:'Prasyarat konsep',none:'Tidak ada prasyarat dalam peta ini.',readings:'Bacaan pendukung',
    sourceObjectives:'Nomor tujuan dalam sumber Inggris',selectConcept:'Sertakan konsep dalam pilihan',
    moduleHeading:'Pilih modul',module:'Modul bacaan',clear:'Kosongkan pilihan modul',
    addConceptModules:'Tambahkan modul konsep yang dipilih',
    exerciseHeading:'Buka latihan dan solusi',category:'Jenis',solution:'Ketersediaan solusi',
    withSolution:'Dengan solusi sumber',withoutSolution:'Tanpa solusi sumber',query:'Cari ID modul atau latihan',
    read:'Baca soal',readSolution:'Baca solusi',noSolution:'Sumber tidak menyediakan solusi',identity:'ID sumber',
    previous:'Sebelumnya',next:'Berikutnya',empty:'Tidak ada latihan untuk pilihan ini.',
    loadFailure:'Daftar interaktif tidak tersedia. Tautan konsep dan daftar modul di bawah tetap dapat digunakan.',
    loading:'Tautan konsep dan modul tersedia. Daftar latihan sedang disiapkan.',
    download:'Unduh pilihan untuk digunakan kembali',exported:'Pilihan diunduh sebagai metadata; teks buku tidak disalin.',
    unselectedPrerequisites:'Prasyarat yang belum disertakan (bukan urutan belajar)',
    noUnselectedPrerequisites:'Tidak ada prasyarat tambahan untuk konsep yang dipilih; ini bukan penilaian penguasaan.',
    boundary:'Latihan ditampilkan menurut modul, bukan sebagai bukti bahwa setiap latihan menguji konsep tertentu. Daftar prasyarat tidak menyatakan kemampuan pelajar.',
    sourceNote:'Peta mempertahankan 245 tujuan sumber dan 246 tujuan terjemahan. Satu tujuan sumber pada m81354 dipecah menjadi dua dalam terjemahan; penomoran tidak disamakan.',
    bridge:'Enam konsep pengantar A10 berasal dari buku A00 ini. Pelajari aljabar elementer selanjutnya di A10.',
    fallback:'Semua modul — tautan tetap tersedia tanpa JavaScript',provenance:'Sumber dan batas penggunaan',
    portable:'Paket halaman luring',portableNote:'Paket memuat peta, pemilih dan metadata latihan. Bacaan buku tetap menggunakan tautan publik dan memerlukan salinan buku tersendiri untuk dibaca luring.',
    selectionNote:'Pilih modul dan, bila perlu, konsep yang ingin disertakan. Pilihan menyimpan ID dan tautan yang dapat digunakan kembali; bukan buku baru atau silabus yang telah diuji.',
    planTitle:'Rencana belajar A00',planNote:'Catatan ini adalah rencana Anda, bukan isi buku atau bukti hasil belajar. Tautan bacaan tetap berbahasa Indonesia. Isian boleh dikosongkan; jangan masukkan data pribadi pelajar.',
    planFields:{title:'Judul rencana',audience:'Untuk pelajar',goal:'Tujuan belajar',period:'Waktu belajar',study:'Cara belajar',feedback:'Umpan balik dan pembahasan'},
    planHTML:'Unduh rencana yang dapat dibaca (HTML)',planJSON:'Unduh rencana dan identitas sumber (JSON)',
    planOrder:'Bacaan mengikuti urutan buku sumber. Urutan ini bukan rekomendasi otomatis untuk kebutuhan setiap pelajar.',
    planPortableNote:'Halaman rencana memuat catatan, konsep yang dipilih beserta prasyaratnya, dan tautan bacaan serta latihan. Halaman ini dapat dibaca luring, tetapi tidak memuat pemilih interaktif atau isi buku. Untuk membaca buku luring, gunakan salinan buku tersendiri.',
    planMissingModules:'Modul pendukung konsep yang belum disertakan',planExported:'Rencana diunduh. Halaman rencana dapat dibaca luring; isi buku tidak disertakan.',
    planInvalid:'Periksa isian rencana; setiap isian dibatasi 2.000 karakter.',
    categories:{'section:practice-perfect':'Latihan penguasaan','note:try':'Coba sendiri','section:review-exercises':'Latihan ulasan',example:'Contoh terpandu','section:practice-test':'Tes latihan','note:be-prepared':'Persiapan prasyarat','section:writing':'Menulis dan menjelaskan','section:everyday':'Penerapan sehari-hari','section:section-exercises':'Latihan bagian'}},
  en:{title:'A00 concepts and exercises',teacherTitle:'A00 study selections for educators',program:'Back to the program',
    learner:'For learners',teacher:'For educators',language:'Language',skip:'Skip to content',
    intro:'Choose a concept to open its definition, prerequisites and supporting reading. Linked textbook modules are in Indonesian.',
    concepts:'concepts',modules:'modules',assessments:'exercises and examples',solutions:'source solutions',gaps:'without source solutions',
    conceptHeading:'Concepts and prerequisites',conceptQuery:'Find a concept',role:'Concept scope',all:'All',
    roles:{a00_core:'A00 core',a00_supporting:'Supporting concept',a10_bridge:'Introduction to A10'},
    prerequisites:'Concept prerequisites',none:'No prerequisites declared in this map.',readings:'Supporting reading',
    sourceObjectives:'Objective numbers in the English source',selectConcept:'Include concept in selection',
    moduleHeading:'Choose modules',module:'Reading module',clear:'Clear module selection',addConceptModules:'Add modules for selected concepts',
    exerciseHeading:'Open exercises and solutions',category:'Category',solution:'Solution availability',withSolution:'With source solution',withoutSolution:'Without source solution',query:'Find a module or exercise ID',
    read:'Read problem',readSolution:'Read solution',noSolution:'No solution supplied by the source',identity:'Source ID',previous:'Previous',next:'Next',empty:'No exercises match this selection.',
    loadFailure:'The interactive list is unavailable. Concept links and the full module list below remain usable.',loading:'Concept and module links are ready. Preparing the exercise list.',
    download:'Download reusable selection',exported:'Selection downloaded as metadata; textbook text is not copied.',
    unselectedPrerequisites:'Prerequisites not selected (not a study sequence)',noUnselectedPrerequisites:'No additional prerequisites for the selected concepts; this is not a mastery assessment.',
    boundary:'Exercises are listed by module, not as evidence that each exercise tests a particular concept. Prerequisite lists do not assess the learner’s knowledge.',
    sourceNote:'The map retains 245 source objectives and 246 translated objectives. One source objective in m81354 becomes two translated objectives; their numbering is not treated as identical.',
    bridge:'Six introductory A10 concepts come from this A00 book. Continue to elementary algebra in A10.',
    fallback:'Every module — links remain available without JavaScript',provenance:'Sources and scope',portable:'Offline page package',
    portableNote:'The package includes the map, selectors and exercise metadata. Textbook reading still uses public links; offline reading requires a separate copy of the book.',
    selectionNote:'Choose modules and, optionally, concepts to include. The selection preserves reusable identities and links; it is not a new book or an evaluated syllabus.',
    planTitle:'A00 study plan',planNote:'These notes are your plan, not textbook content or evidence of learning. Linked reading remains Indonesian. Fields may be left blank; do not enter learners’ personal data.',
    planFields:{title:'Plan title',audience:'Intended learners',goal:'Learning intention',period:'Study period',study:'Study approach',feedback:'Feedback and discussion'},
    planHTML:'Download readable plan (HTML)',planJSON:'Download plan and source identities (JSON)',
    planOrder:'Reading follows the source book order. It is not an automatic recommendation for each learner’s needs.',
    planPortableNote:'This plan page contains your notes, selected concepts and their prerequisites, and reading and exercise links. The page works offline, but includes neither interactive selectors nor textbook bodies. Offline textbook reading requires a separate copy of the book.',
    planMissingModules:'Supporting concept modules not selected',planExported:'Plan downloaded. The plan page works offline; textbook bodies are not included.',
    planInvalid:'Check the plan fields; each field is limited to 2,000 characters.',
    categories:{'section:practice-perfect':'Practice','note:try':'Try it','section:review-exercises':'Review exercises',example:'Worked example','section:practice-test':'Practice test','note:be-prepared':'Prerequisite preparation','section:writing':'Writing and explanation','section:everyday':'Everyday applications','section:section-exercises':'Section exercises'}}};

export async function loadInputs(){
  const lock=JSON.parse(await readFile(resolve(root,base,'input/source-lock.json'),'utf8'));
  const snapshots={};
  for(const item of lock.snapshots){
    const bytes=await readFile(resolve(root,base,'input',item.path));
    assert.equal(bytes.length,item.bytes);assert.equal(hash(bytes),item.sha256);
    snapshots[item.path]=JSON.parse(bytes);
  }
  assert.equal(lock.sources.graph.sha256,'254f151384102f03256909bb803bf9a6611573afc4f4c1a1601545d28d8a060f');
  assert.equal(lock.sources.originalGraph.sha256,'acfddef3015112ca0b3805e8a22b782433da4d8d835d7f357fd2b223d03fbe23');
  assert.equal(hash(await readFile(resolve(root,base,'input/neutral-graph.json'))),lock.sources.graph.sha256);
  assert.equal(hash(await readFile(resolve(root,base,'input/localized-terms.json'))),lock.sources.overlay.sha256);
  const assessmentBytes=await readFile(resolve(root,lock.sources.assessments.path));
  assert.equal(hash(assessmentBytes),lock.sources.assessments.sha256);
  return {graph:snapshots['neutral-graph.json'],overlay:snapshots['localized-terms.json'],
    nativeConcepts:snapshots['concept-identities.json'],crosswalks:snapshots['module-crosswalks.json'],
    assessments:JSON.parse(assessmentBytes),sources:lock.sources,rights:snapshots['concept-rights.json']};
}

function page(model,locale,teacher){
  const L=labels[locale],suffix=locale==='en'?'-en':'',stem=teacher?'A00-pengajar':'A00';
  const title=teacher?L.teacherTitle:L.title;
  const conceptCards=model.concepts.map(c=>`<article class="concept-card" id="concept-${escape(c.key)}"><details><summary>${escape(c.labels[locale])}</summary><p>${escape(c.definitions[locale])}</p><span class="badge">${L.roles[c.role]}</span><h3>${L.prerequisites}</h3>${c.prerequisite_keys.length?`<ul>${c.prerequisite_keys.map(key=>`<li><a href="#concept-${escape(key)}">${escape(model.concepts.find(row=>row.key===key).labels[locale])}</a></li>`).join('')}</ul>`:`<p>${L.none}</p>`}<h3>${L.readings}</h3><ul>${c.modules.map(m=>`<li><a href="${escape(m.module_url)}" lang="id">${escape(model.modules.find(row=>row.module_id===m.module_id).title)} (id)</a><br><small>${L.sourceObjectives}: ${m.objective_numbers.join(', ')}</small></li>`).join('')}</ul></details>${teacher?`<label><input type="checkbox" name="concept" value="${escape(c.key)}"> ${L.selectConcept}</label>`:''}</article>`).join('\n');
  const initialModule=model.modules.find(m=>m.counts.assessments>0).module_id;
  const moduleOptions=model.modules.map(m=>`<option lang="id" value="${m.module_id}"${m.module_id===initialModule?' selected':''}>${m.ordinal}. ${escape(m.title)} (id)</option>`).join('');
  const moduleList=model.modules.map(m=>`<label><input type="checkbox" name="module" value="${m.module_id}"><span>${m.ordinal}. <span lang="id">${escape(m.title)}</span><small>${m.counts.assessments} ${L.assessments} · ${m.counts.explicit_solutions} ${L.solutions}</small><a href="${m.module_url}" lang="${locale}" hreflang="id">${L.readings} (id)</a></span></label>`).join('');
  const moduleFallback=model.modules.map(m=>`<li><a href="${m.module_url}" lang="id">${m.ordinal}. ${escape(m.title)} (id)</a></li>`).join('');
  const payload=JSON.stringify({model,locale,teacher,labels:L}).replaceAll('<','\\u003c');
  const studyPlan=teacher?`<section aria-labelledby="study-plan-heading"><h2 id="study-plan-heading">${L.planTitle}</h2><p>${L.planNote}</p><div class="study-plan-fields">${Object.entries(L.planFields).map(([key,label])=>`<label for="plan-${key}">${label}<textarea id="plan-${key}" maxlength="2000" rows="2"></textarea></label>`).join('')}</div><div class="controls"><button id="download-study-plan-html" type="button" disabled>${L.planHTML}</button><button id="download-study-plan-json" type="button" disabled>${L.planJSON}</button></div><p id="plan-export-status" role="status"></p></section>`:'';
  return `<!doctype html>
<html lang="${locale}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${title} — Program Matematika Indonesia</title><meta name="description" content="${escape(L.intro)}"><link rel="stylesheet" href="a00-concept.css"><script defer src="a00-controls.js"></script><script defer src="../data/assessment-inventory-v1.js"></script><script defer src="a00-ui.js"></script></head>
<body><a class="skip" href="#main">${L.skip}</a><header><a href="${origin}/${locale}/index.html#course-A00">${L.program}</a><nav aria-label="${L.language}"><a href="A00${suffix}.html">${L.learner}</a><a href="A00-pengajar${suffix}.html">${L.teacher}</a><a href="${stem}.html" lang="id" hreflang="id">Bahasa Indonesia</a><a href="${stem}-en.html" lang="en" hreflang="en">English</a></nav></header>
<main id="main"><p class="eyebrow">A00 · OpenStax Prealgebra 2e</p><h1>${title}</h1><p class="intro">${L.intro}</p><div class="counts"><span><strong>35</strong> ${L.concepts}</span><span><strong>75</strong> ${L.modules}</span><span><strong>${model.counts.assessments.toLocaleString(locale)}</strong> ${L.assessments}</span><span><strong>${model.counts.supplied_solutions.toLocaleString(locale)}</strong> ${L.solutions}</span><span><strong>${model.counts.explicit_solution_gaps.toLocaleString(locale)}</strong> ${L.gaps}</span></div>
<section aria-labelledby="exercise-heading"><h2 id="exercise-heading">${L.exerciseHeading}</h2>${teacher?`<p>${L.selectionNote}</p>`:''}<div class="workspace"><div>${teacher?`<fieldset><legend>${L.moduleHeading}</legend><div class="module-list">${moduleList}</div></fieldset><div class="controls"><button id="clear-modules" type="button">${L.clear}</button><button id="select-concept-modules" type="button">${L.addConceptModules}</button></div><p id="prerequisite-status" role="status"></p><button id="download-selection" type="button" disabled>${L.download}</button><p id="export-status" role="status"></p>`:`<label for="module">${L.module}</label><select id="module">${moduleOptions}</select>`}</div><div><div id="assessment-controls" class="controls" hidden><label>${L.category}<select id="category"><option value="all">${L.all}</option>${Object.entries(L.categories).map(([key,label])=>`<option value="${escape(key)}">${label}</option>`).join('')}</select></label><label>${L.solution}<select id="solution"><option value="all">${L.all}</option><option value="with">${L.withSolution}</option><option value="without">${L.withoutSolution}</option></select></label><label>${L.query}<input id="assessment-query" type="search"></label></div><p id="results-status" role="status" aria-live="polite">${L.loading}</p><ol id="results" class="result-list"></ol><div class="pagination"><button id="previous" type="button" disabled>${L.previous}</button><button id="next" type="button" disabled>${L.next}</button></div></div></div><p class="note">${L.boundary}</p></section>
<section aria-labelledby="concept-heading"><h2 id="concept-heading">${L.conceptHeading}</h2><div class="controls"><label>${L.conceptQuery}<input id="concept-query" type="search"></label><label>${L.role}<select id="concept-role"><option value="all">${L.all}</option>${Object.entries(L.roles).map(([key,label])=>`<option value="${key}">${label}</option>`).join('')}</select></label></div><div class="concept-grid">${conceptCards}</div><p>${L.bridge} <a href="${origin}/${locale}/index.html#course-A10">A10 →</a></p></section>
${studyPlan}
<section><h2>${L.fallback}</h2><ol class="fallback-list">${moduleFallback}</ol></section>
<section><h2>${L.provenance}</h2><p>${L.sourceNote}</p><p>OpenStax · Prealgebra 2e. <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>. ${locale==='id'?'Adaptasi navigasi dan metadata; bukan terbitan resmi OpenStax.':'Navigation and metadata adaptation; not an official OpenStax edition.'}</p><p><a href="https://github.com/openstax/osbooks-prealgebra-bundle/tree/${model.source_revision}">OpenStax Prealgebra 2e · ${model.source_revision.slice(0,12)}</a> · <a href="../input/source-lock.json">${locale==='id'?'Identitas sumber':'Source identities'}</a></p><p><a href="${origin}/backend/a00/A00-concept-teacher-offline.zip">${L.portable}</a></p><p>${L.portableNote}</p></section></main><footer><a href="${origin}/${locale}/index.html#course-A00">${L.program}</a></footer><script type="application/json" id="a00-page-data">${payload}</script></body></html>\n`;
}

export async function build(out=resolve(root,base)){
  const full=projectA00(await loadInputs());
  const {assessments,...model}=full;
  const files=new Map([['data/learning-map.json',json(model)],
    ['data/assessment-inventory-v1.js','globalThis.A00AssessmentInventory='+JSON.stringify(assessments).replaceAll('<','\\u003c')+';\n']]);
  for(const locale of ['id','en'])for(const teacher of [false,true])
    files.set(`views/${teacher?'A00-pengajar':'A00'}${locale==='en'?'-en':''}.html`,page(model,locale,teacher));
  for(const [source,target] of [['a00_concept_controls_v1.js','a00-controls.js'],['a00_concept_ui_v1.js','a00-ui.js'],['a00_concept_styles_v1.css','a00-concept.css']])
    files.set('views/'+target,await readFile(resolve(root,'scripts',source),'utf8'));
  const outputFacts=[];
  for(const [path,text] of files){
    assert.doesNotMatch(text,/(?:^|["'\s])[A-Za-z]:[\\/]|codex:\/\/threads\//m);
    const bytes=Buffer.from(text);await mkdir(dirname(resolve(out,path)),{recursive:true});await writeFile(resolve(out,path),bytes);
    outputFacts.push({path,bytes:bytes.length,sha256:hash(bytes)});
  }
  const generators=[];
  for(const path of ['build-a00-concept-teacher-v1.mjs','a00_concept_model_v1.mjs','a00_concept_controls_v1.js','a00_concept_ui_v1.js','a00_concept_styles_v1.css']){
    const bytes=await readFile(resolve(root,'scripts',path));generators.push({path:'scripts/'+path,bytes:bytes.length,sha256:hash(bytes)});
  }
  const sourceLock=await readFile(resolve(root,base,'input/source-lock.json'));
  const manifest={schema:'a00-concept-teacher-manifest/1',course_id:'A00',counts:model.counts,generators,
    input:{path:'input/source-lock.json',bytes:sourceLock.length,sha256:hash(sourceLock)},outputs:outputFacts,
    capabilities:['native_concept_navigation','prerequisite_lookup','module_exercise_selection','educator_metadata_export','bilingual_interface','source_bound_readable_study_plan'],
    limitations:{exercise_to_concept_alignment:false,prerequisite_mastery_assessment:false,
      new_curriculum_effect_evidence:false,full_canon_review:false,textbook_bodies_included:false,
      english_interface_reading_language:'id-ID',objective_ids_to_ordinals_positional_mapping:false}};
  await writeFile(resolve(out,'manifest.json'),json(manifest));
  return manifest;
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const args=process.argv.slice(2);assert.ok(args.length===0||(args.length===2&&args[0]==='--out'));
  const result=await build(args.length?resolve(args[1]):undefined);console.log(JSON.stringify({status:'pass',counts:result.counts,outputs:result.outputs.length}));
}
