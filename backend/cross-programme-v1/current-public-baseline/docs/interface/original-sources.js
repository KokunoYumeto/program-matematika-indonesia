// Presentation provenance only: live source sites are not frozen edition identities.
// English originals already have exact bindings in locales.js.
const originalSource = (label, href, contentLanguage, origin = 'upstream-original') => ({
  label, href, contentLanguage, origin,
  accessRole: 'authoritative-original',
  authorityRole: origin === 'program-original' ? 'program-authority' : 'upstream-authority',
  relationToSource: 'source',
});
export const additionalOriginalSources = {
  B80: [originalSource('Komputasi Matematis dan Eksperimen Reprodusibel', 'https://kokunoyumeto.github.io/mathematical-computing-reproducible-experiments-id/', 'id', 'program-original')],
  D50: [originalSource('Holger Brenner — Differentialgeometrie (Osnabrück 2023)', 'https://de.wikiversity.org/wiki/Kurs:Differentialgeometrie_(Osnabr%C3%BCck_2023)', 'de')],
  D70: [originalSource('Wen-Wei Li — 代数学方法：卷一', 'https://wwli.asia/zh/docs/books/', 'zh')],
  D80: [originalSource('Wen-Wei Li — 代数学方法：卷二', 'https://wwli.asia/zh/docs/books/', 'zh')],
  D100: [
    originalSource('Holger Brenner — Algebraische Kurven (Osnabrück 2025–2026)', 'https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2025-2026)', 'de'),
    originalSource('Holger Brenner — Algebraische Kurven (Osnabrück 2012)', 'https://de.wikiversity.org/wiki/Kurs:Algebraische_Kurven_(Osnabr%C3%BCck_2012)', 'de'),
    originalSource('Holger Brenner — Bündel, Garben und Kohomologie (2019–2020)', 'https://de.wikiversity.org/wiki/Kurs:B%C3%BCndel,_Garben_und_Kohomologie_(Osnabr%C3%BCck_2019-2020)', 'de'),
  ],
  D120: [originalSource('Kerja Matematis yang Dapat Ditelusuri', 'https://kokunoyumeto.github.io/kerja-matematika-yang-dapat-ditelusuri-id/', 'id', 'program-original')],
};
