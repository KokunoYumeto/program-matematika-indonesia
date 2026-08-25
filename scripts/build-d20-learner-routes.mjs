import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const proposalPath = resolve(project, '..', '..', '..', 'outputs', '01a01ec1-e685-70d0-b022-211396334723', 'curriculum_logbook', 'D20_LEARNER_ROUTE_WRAPPER_PROPOSAL_20260826.json');
const docs = resolve(project, 'docs');
const routeRoot = resolve(docs, 'id-ID', 'courses', 'D20');
const proposalBytes = await readFile(proposalPath);
const proposalSha = createHash('sha256').update(proposalBytes).digest('hex');
const proposal = JSON.parse(proposalBytes.toString('utf8'));

if (proposalSha !== '720f0d7501a5b5e1d53dcc2bf167168aa375100cac6cfd35ed127b60a7e68758') {
  throw new Error(`D20 route proposal changed: ${proposalSha}`);
}
if (proposal.course_id !== 'D20' || proposal.units.length !== 17) throw new Error('D20 proposal is not the frozen 17-unit route map.');
if (proposal.route_readback.all_core_unit_routes_status !== 200) throw new Error('D20 core route readback is not 200.');

const esc = (value) => String(value)
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#39;');
const write = async (path, value) => {
  await mkdir(dirname(path), { recursive: true });
  await writeFile(path, value, 'utf8');
};
const owner = proposal.wrapper_contract;
const commonStyle = `
  :root{color-scheme:light;--ink:#152522;--muted:#52635f;--paper:#fbfaf6;--accent:#176b5d;--line:#d8e1dc}
  *{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
  main{max-width:960px;margin:0 auto;padding:clamp(1.25rem,4vw,4rem) clamp(1rem,4vw,2rem)}
  nav{font-size:.95rem;margin-bottom:2rem}a{color:var(--accent)}h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.08;margin:.25rem 0 1rem}h2{margin-top:2.2rem;line-height:1.2}p{max-width:72ch}.lede{font-size:1.12rem;color:var(--muted)}
  .actions{display:flex;flex-wrap:wrap;gap:.7rem;margin:1.5rem 0 2rem}.button{display:inline-block;border:1px solid var(--accent);border-radius:999px;padding:.6rem 1rem;text-decoration:none}.button.primary{background:var(--accent);color:white}.button.secondary{background:white}
  ol{padding-left:1.5rem}li{margin:.55rem 0}.chapter{display:flex;gap:.7rem;align-items:baseline}.chapter small{color:var(--muted)}.notice{border-left:4px solid var(--accent);background:#eef5f1;padding:.8rem 1rem;margin:1.5rem 0}.meta{color:var(--muted);font-size:.92rem}
  @media(max-width:600px){.actions{display:grid}.button{text-align:center}}
`;

const unitLinks = proposal.units.map((unit) => `<li><a href="units/${esc(unit.slug)}/"><span class="chapter"><strong>Bab ${String(unit.order).padStart(2, '0')}</strong> ${esc(unit.title)}</span></a><small>${esc(unit.id)}</small></li>`).join('\n');
const courseHtml = `<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>D20 — Analisis Fungsional | Program Matematika Indonesia</title><meta name="description" content="Pintu masuk pelajar untuk 17 bab HTML Bahasa Indonesia Analisis Fungsional."><link rel="canonical" href="https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/D20/"><style>${commonStyle}</style></head>
<body><main>
<nav aria-label="Jejak navigasi"><a href="../../../">Program Matematika Indonesia</a> › <span aria-current="page">D20</span></nav>
<h1>Analisis Fungsional</h1>
<p class="lede">Edisi Bahasa Indonesia untuk fondasi pascasarjana awal: ruang bernorma, Banach dan Hilbert, operator terbatas, dualitas, teori kompak, dan teori spektral.</p>
<p>Ini adalah indeks pelajar yang mengarahkan ke pembaca HTML publik yang sebenarnya. Teks buku tidak disalin ke hub; setiap bab tetap berada di repositori pemiliknya.</p>
<div class="actions"><a class="button primary" href="${esc(owner.native_html_base)}">Buka pembaca HTML pemilik ↗</a><a class="button secondary" href="${esc(owner.pdf_fallback)}">Buka PDF lengkap ↗</a><a class="button secondary" href="${esc(owner.owner_repository)}">Sumber dan kode ↗</a><a class="button secondary" href="${esc(owner.owner_zenodo)}">Zenodo / DOI ↗</a></div>
<div class="notice"><strong>Tentang pendamping:</strong> pembaca pendamping tersedia hanya untuk bab yang benar-benar memiliki rute publik. Bab tanpa pendamping tetap memiliki pembaca utama.</div>
<h2>Bab</h2><ol>${unitLinks}</ol>
<p class="meta">Peta rute dibekukan dari proposal pusat ${esc(proposalSha)} pada 26 Agustus 2026. Hub hanya memuat identitas, judul, urutan, hak, dan tautan—bukan prosa buku.</p>
</main></body></html>\n`;
await write(resolve(routeRoot, 'index.html'), courseHtml);

for (const unit of proposal.units) {
  const companion = unit.companion_url
    ? `<a class="button secondary" href="${esc(unit.companion_url)}">Buka pendamping bab ↗</a>`
    : '<span class="meta">Pendamping publik tidak tersedia untuk bab ini.</span>';
  const unitHtml = `<!doctype html>
<html lang="id"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bab ${String(unit.order).padStart(2, '0')} — ${esc(unit.title)} | Analisis Fungsional</title><meta name="description" content="Indeks pelajar untuk ${esc(unit.title)}."><link rel="canonical" href="https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/D20/units/${esc(unit.slug)}/"><style>${commonStyle}</style></head>
<body><main><nav aria-label="Jejak navigasi"><a href="../../../../">Program Matematika Indonesia</a> › <a href="../../">D20 — Analisis Fungsional</a> › <span aria-current="page">Bab ${String(unit.order).padStart(2, '0')}</span></nav>
<p class="meta">${esc(unit.id)}</p><h1>Bab ${String(unit.order).padStart(2, '0')}: ${esc(unit.title)}</h1>
<p class="lede">Buka pembaca bab yang dipelihara oleh edisi kanonik. Halaman indeks ini tidak menggantikan pembaca dan tidak menyalin isi buku.</p>
<div class="actions"><a class="button primary" href="${esc(unit.html_url)}">Buka pembaca HTML bab ↗</a>${companion}<a class="button secondary" href="${esc(owner.pdf_fallback)}">PDF lengkap ↗</a></div>
<p><a href="../../">← Kembali ke daftar 17 bab</a> · <a href="${esc(owner.native_html_base)}">Pembaca pemilik</a> · <a href="${esc(owner.owner_repository)}">Repositori</a></p>
<p class="meta">Rute pembaca utama diverifikasi HTTP 200 pada 26 Agustus 2026. Tautan pendamping hanya ditampilkan bila rute publiknya juga terverifikasi.</p>
</main></body></html>\n`;
  await write(resolve(routeRoot, 'units', unit.slug, 'index.html'), unitHtml);
}

const routeManifest = {
  schema_id: 'program-matematika-indonesia/unit-route-v2.1/v1',
  recorded_at: '2026-08-26T00:00:00+02:00',
  source_proposal_sha256: proposalSha,
  course_id: proposal.course_id,
  central_root: proposal.central_route_root,
  learner_start: `${proposal.central_route_root}`,
  units: proposal.units.map((unit) => ({
    id: unit.id,
    order: unit.order,
    slug: unit.slug,
    title: unit.title,
    central_url: `https://kokunoyumeto.github.io/program-matematika-indonesia${proposal.central_route_root}units/${unit.slug}/`,
    native_html_url: unit.html_url,
    companion_url: unit.companion_url ?? null,
    native_route_state: 'verified_public_http_200',
    companion_route_state: unit.companion_url ? 'verified_public_http_200' : 'not_published_route_verified_404',
  })),
};
await write(resolve(docs, 'data', 'unit-route-v2.1.json'), `${JSON.stringify(routeManifest, null, 2)}\n`);
console.log(JSON.stringify({ result: 'pass', proposal_sha256: proposalSha, course: 'D20', units: proposal.units.length, companion_units: proposal.units.filter((unit) => unit.companion_url).length }));
