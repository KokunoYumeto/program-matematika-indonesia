"""Bounded PDF geometry checks and Poppler contact sheets; no source-code execution."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import fitz
from PIL import Image, ImageDraw


def inspect(root, language, poppler):
    work = root / language
    pdf = work / f'00-b80-{language}.pdf'
    build = json.loads((work / 'PDF_BUILD_RECEIPT.json').read_text(encoding='utf-8-sig'))
    assert build['status'] == 'compiled_pending_visual_review'
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == build['pdf']['sha256']
    assert hashlib.sha256((work / f'01-b80-{language}.tex').read_bytes()).hexdigest() == build['source_sha256']
    out = work / 'qa'
    out.mkdir(exist_ok=True)
    document = fitz.open(pdf)
    bounds, bad_links, replacement_chars, blank = [], [], [], []
    selected = {1, 2, 8, len(document)}
    needles = ['test_scipy_special_exprel_is_stable_near_zero',
               'Measured distance', 'Jarak terukur', 'Listing 7.1',
               'test_positive_math.py', 'ketidakpastian', 'uncertainty']
    needle_pages = {}
    for index, page in enumerate(document):
        text = page.get_text()
        if page.get_images(full=True):
            selected.add(index + 1)
        if not text.strip(): blank.append(index + 1)
        if '\ufffd' in text: replacement_chars.append(index + 1)
        for needle in needles:
            if needle not in needle_pages and needle in text:
                needle_pages[needle] = index + 1
                selected.add(index + 1)
        for word in page.get_text('words'):
            if word[0] < 10 or word[1] < 10 or word[2] > page.rect.width - 10 or word[3] > page.rect.height - 10:
                bounds.append({'page': index + 1, 'box': word[:4]})
        for link in page.get_links():
            if link['kind'] == fitz.LINK_GOTO and not 0 <= link.get('page', -1) < len(document):
                bad_links.append({'page': index + 1, 'link': link})
    receipt = {'schema': 'b80-pdf-geometry/1', 'language': language,
               'pdf_sha256': build['pdf']['sha256'], 'pages': len(document),
               'bookmarks': len(document.get_toc()), 'text_outside_page_safety_margin': bounds,
               'bad_internal_links': bad_links, 'replacement_character_pages': replacement_chars,
               'blank_pages': blank, 'sample_pages': sorted(selected), 'located_samples': needle_pages,
               'visual_review': 'pending; geometry tests are not visual review'}
    assert not bounds and not bad_links and not replacement_chars
    subprocess.run([str(poppler), '-r', '25', '-png', str(pdf), str(out / 'page')],
                   check=True, capture_output=True, timeout=120)
    pages = sorted((p for p in out.glob('page-*.png') if int(p.stem.split('-')[-1]) <= len(document)),
                   key=lambda p: int(p.stem.split('-')[-1]))
    assert len(pages) == len(document)
    for start in range(0, len(pages), 20):
        group = pages[start:start + 20]
        sheet = Image.new('RGB', (5 * 218, 4 * 328), '#d8d8d8')
        draw = ImageDraw.Draw(sheet)
        for offset, path in enumerate(group):
            with Image.open(path) as pic:
                pic.thumbnail((208, 296))
                x, y = (offset % 5) * 218 + 5, (offset // 5) * 328 + 22
                sheet.paste(pic, (x, y))
                draw.text((x, y - 17), f'{language.upper()} p.{start + offset + 1}', fill='black')
        sheet.save(out / f'contact-{start // 20 + 1:02}.png')
    for page in sorted(selected):
        subprocess.run([str(poppler), '-f', str(page), '-l', str(page), '-r', '110', '-singlefile',
                        '-png', str(pdf), str(out / f'sample-{page:03}')],
                       check=True, capture_output=True, timeout=30)
    (out / 'GEOMETRY.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--poppler', required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2] / 'outputs/b80-format-repair-v1'
    for language in ('id', 'en'):
        inspect(root, language, args.poppler)
