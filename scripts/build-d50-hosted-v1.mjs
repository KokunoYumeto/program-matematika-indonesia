import assert from 'node:assert/strict';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {root,base,sha,json,build} from './build-d50-surface-v1.mjs';

export async function hosted(){
  const delivery=JSON.parse(await readFile(resolve(root,base,'delivery/reader-delivery.json'),'utf8'));
  assert.equal(delivery.state,'pass');
  const out=resolve(root,'docs/backend/d50');await mkdir(out,{recursive:true});
  for(const f of delivery.reader_members){
    // This builder precedes the shared reversible navigation shell.
    const b=await readFile(resolve(out,'reader',f.path));
    assert.equal(b.length,f.bytes,f.path);assert.equal(sha(b),f.sha256,f.path);
  }
  const map=await build();
  map.hosted_reader_url=delivery.reader_url;
  map.direct_tex=delivery.direct_tex;
  map.complete_source_archive=delivery.complete_source_archive;
  map.limitations.id[5]='Bacaan daring menyalin byte edisi HTML terverifikasi; navigasi program ditambahkan tanpa menulis ulang isi. Paket sumber asli tetap tersedia.';
  map.limitations.en[5]='The hosted reader preserves the verified HTML edition; programme navigation is added without rewriting its content. The original editable source package remains available.';
  for(const u of map.units)u.route.hosted_url=delivery.reader_url+'#'+u.route.anchor;
  const names=['index.html','index.en.html','teacher.html','teacher.en.html','style.css','study-plan.js'];
  for(const name of names){
    let b=await readFile(resolve(root,base,'portable',name));
    if(name.endsWith('.html')){
      let t=b.toString('utf8');const en=name.includes('.en.'),label=(a,c)=>en?c:a;
      t=t.replace("style-src 'self';", "style-src 'self' 'unsafe-inline';");
      t=t.replace(/<p class="notice">.*?<\/p>/,
        `<p class="notice">${label('Bacaan tersedia langsung di situs ini dalam Bahasa Indonesia. English mengubah antarmuka pemilih, bukan bahasa buku.','The complete reading is hosted here in Indonesian. English changes the selector interface, not the book language.')}</p>`);
      // Replace the old portable-only limitation explicitly, not arbitrary prose.
      t=t.replace('Alat ini menggunakan paket bacaan luring yang sudah diterbitkan. Tidak ada alamat pembaca daring baru yang dinyatakan tersedia.',map.limitations.id[5]);
      t=t.replace('The tool uses the already published offline reader package; it claims no new hosted reader address.',map.limitations.en[5]);
      const downloads=`<section><h2>${label('Bacaan dan sumber yang dapat disunting','Reader and editable source')}</h2><ol><li><a href="${delivery.pdf.url}">PDF · 712 ${label('halaman','pages')}</a></li><li><a href="${delivery.direct_tex.path}" download>${label('LaTeX lengkap · unduh langsung','Complete LaTeX · direct download')}</a></li><li><a href="${delivery.complete_source_archive.url}">${label('ZIP sumber lengkap asli beserta dependensi','Original complete source ZIP with dependencies')}</a></li></ol><p>${label('Untuk membangun LaTeX gabungan, letakkan berkas ini di build/complete-stage/build dalam ZIP sumber. Gambar dan dependensi tetap berada dalam ZIP. Ini perakitan sumber, bukan penyuntingan isi atau pembangunan ulang PDF.','To build the assembled LaTeX, place it in build/complete-stage/build in the source ZIP. Images and dependencies remain in that ZIP. This is source assembly, not content editing or a new PDF build.')}</p><p><a href="https://github.com/KokunoYumeto/program-matematika-indonesia/blob/main/backend/course-capsule-v1/adapters/d50-surface-v1/README.md">${label('Kode dan petunjuk reproduksi alat','Tool source and reproduction instructions')}</a> · <a href="LICENSE.md">${label('Lisensi komponen','Component licences')}</a></p></section>`;
      t=t.replace('</main>',downloads+'</main>');b=Buffer.from(t);
    }
    await writeFile(resolve(out,name),b);
  }
  await writeFile(resolve(out,'learning-map.json'),json(map));
  await writeFile(resolve(out,'data.js'),'globalThis.D50_DATA='+JSON.stringify(map)+';\n');
  const files=[];
  for(const name of [...names,'learning-map.json','data.js',delivery.direct_tex.path,'LICENSE.md','reader-delivery.json']){
    const b=await readFile(resolve(out,name));files.push({path:name,bytes:b.length,sha256:sha(b)});
  }
  const validation={schema:'d50-hosted-surface/1',state:'pass',counts:map.counts,files,
    reader_members:delivery.reader_members,content_locale:'id-ID',interface_locales:['id','en'],
    source_body_unchanged:true,new_translation:false,public_deployment_verified:false};
  await writeFile(resolve(out,'validation.json'),json(validation));
  return validation;
}
console.log(json({state:'built',...(await hosted()).counts}));
