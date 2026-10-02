# Sumber bacaan terkini / Current reading resources

Dalam `bridge.json`, `courses.core[].language_access` mempertahankan snapshot
sumber yang dibekukan. Gunakan `courses.core[].current_reading_resources` untuk
tambahan bacaan terkini yang telah diikat pada identitas sumber; daftar ini
bukan pengganti atau pengesahan seluruh snapshot lama. Daftar kosong tidak
berarti tidak ada bacaan pada snapshot sumber.

Setiap tambahan mencatat bahasa isi, label Indonesia dan Inggris, commit sumber,
manifest, cakupan bagian dan unit, serta identitas SHA-256 pembaca dan indeks
unit asli untuk setiap bagian. Tautan tambahan yang terlihat di kedua halaman
program berasal dari catatan yang sama. Buku yang baru tersedia sebagian tetap
ditandai `full_book: false`; tautan ini tidak mengesahkan pembuktian prasyarat.

## English

`courses.core[].language_access` is the preserved historical source snapshot.
`courses.core[].current_reading_resources` is the additive, current resource
layer. Use both; an empty addition list does not mean the snapshot has no
readings. New reader availability does not rewrite historical observations.

Each addition carries its actual content language, localized interface labels,
source commit, exact manifest and partial coverage. Every section has a
hash-bound reader and native-unit-index URL. The same records generate the
visible additional links in both programme interfaces. Partial-book and
proof-closure flags remain explicit. Foundation and expanded-reader units
overlap and their counts must not be added as distinct corpus size.

Integration: OpenAI Codex — GPT-6 Astra, Ultra effort. Native author credits,
rights, mathematical content and identifiers are preserved.
