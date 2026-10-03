// Source-bound portable editions in the curriculum map.
// OpenAI Codex — GPT-6 Astra, Ultra effort: integration and checks only.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {createHash} from 'node:crypto';

const cataloguePath='docs/interface/public-course-format-editions.json';
const origin='https://kokunoyumeto.github.io/program-matematika-indonesia/';
const hash=b=>createHash('sha256').update(b).digest('hex');
const fact=(path,b)=>({path,bytes:b.length,sha256:hash(b)});
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');

export async function loadPortableCourseRoutes(root,courseIds,read=path=>readFile(resolve(root,path))){
  const raw=await read(cataloguePath),catalogue=JSON.parse(raw);
  assert.equal(catalogue.schema,'public-course-format-catalogue/1');
  const seen=new Set(),editions=[];
  for(const item of catalogue.editions){
    assert.ok(courseIds.has(item.course_id),'Portable edition needs an exact curriculum course ID');
    assert.ok(!seen.has(item.course_id),'Duplicate portable course edition');seen.add(item.course_id);
    assert.match(item.slug,/^[a-z0-9]+(?:-[a-z0-9]+)*$/);
    const base='docs/editions/'+item.slug+'/';
    assert.equal(item.edition.path,base+'EDITION.json');
    const bytes=await read(item.edition.path);
    assert.deepEqual(fact(item.edition.path,bytes),item.edition,'Changed portable edition manifest');
    const edition=JSON.parse(bytes);
    assert.equal(edition.schema,'public-course-portable-edition/1');
    assert.equal(edition.course_id,item.course_id);
    assert.equal(edition.content_language,item.content_language);
    assert.equal(edition.new_translation,false);
    assert.equal(edition.source_mathematics_changed,false);
    assert.ok(item.notes.en&&item.notes.id&&edition.coverage);
    assert.match(edition.source.commit,/^[0-9a-f]{40}$/);
    assert.equal(edition.files.length,4);
    const files=[];
    for(let i=0;i<edition.files.length;i++){
      const row=edition.files[i],suffix=['.pdf','.tex','-source.zip','.epub'][i];
      assert.match(row.path,/^files\/[a-z0-9.-]+$/);
      assert.ok(row.path.endsWith(suffix),'PDF / direct TeX / full source ZIP / EPUB order');
      const path=base+row.path,content=await read(path);
      assert.equal(content.length,row.bytes);assert.equal(hash(content),row.sha256);
      files.push({path,bytes:row.bytes,sha256:row.sha256,url:origin+path.slice(5)});
    }
    const readers={};
    for(const locale of ['id','en']){
      const path=base+'index.'+locale+'.html',content=await read(path);
      assert.ok(content.toString('utf8').includes('<html lang="'+locale+'">'));
      readers[locale]={...fact(path,content),url:origin+path.slice(5)};
    }
    editions.push({course_id:item.course_id,slug:item.slug,title:item.title,
      content_language:item.content_language,notes:item.notes,coverage:edition.coverage,
      edition:item.edition,source:edition.source,readers,files,
      lesson_count:edition.lessons,prerequisite_chapters:edition.prerequisite_chapters??0,
      supplements:edition.editorial_supplements??0,pdf_pages:edition.pdf_pages,
      native_locations:edition.native_locations,
      proof_dependency_closure:'not_established_by_format_validation',new_translation:false});
  }
  return {schema:'curriculum-portable-course-routes/1',catalogue:fact(cataloguePath,raw),editions};
}

export function renderPortableCourseRoute(route,locale){
  assert.ok(['id','en'].includes(locale));
  const heading=locale==='id'?'Baca dan unduh edisi portabel':'Read and download the portable edition';
  const read=locale==='id'?'Buka indeks pelajaran dan lokasi bacaan':'Open the lesson and reading-location index';
  const labels=locale==='id'?['PDF untuk dibaca','LaTeX kumulatif yang dapat disunting','ZIP sumber lengkap','EPUB']:['Reading PDF','Editable cumulative LaTeX','Complete source ZIP','EPUB'];
  return '<aside data-portable-course="'+esc(route.course_id)+'"><h4>'+heading+'</h4><p>'+esc(route.notes[locale])+'</p><p><a data-portable-reader="'+locale+'" href="'+esc(route.readers[locale].url)+'">'+read+'</a></p><ol>'+route.files.map((file,i)=>'<li><a data-portable-format="'+['pdf','tex','zip','epub'][i]+'" href="'+esc(file.url)+'" hreflang="'+esc(route.content_language)+'">'+labels[i]+'</a></li>').join('')+'</ol></aside>';
}
