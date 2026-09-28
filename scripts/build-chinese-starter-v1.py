"""Build a small, static Chinese entry point; never admit forty translated roles.

Initial intake: --intake <PUBLIC_INTAKE.json>. Later builds need only the
checked-in catalogue, stylesheet and this script. No network or book copies.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'docs/zh'
ORIGIN = 'https://kokunoyumeto.github.io/program-matematika-indonesia/'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dump(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def intake(path):
    raw = path.read_bytes()
    source = json.loads(raw)
    assert source['schema'] == 'chinese-starter-intake/1' and source['anonymous']
    editorial = {
        'algebra-trigonometry': ('代数与三角学（第二版）', '基础准备',
            '从代数运算、方程和函数开始，为三角学与微积分打基础。',
            '94 / 94 个来源模块；1,932 页。', '22082180', 'CC BY-NC-SA 4.0'),
        'calculus-1': ('微积分（第一卷）', '微积分入门',
            '已有函数与三角学基础后，学习极限、导数和积分。',
            '55 / 55 个来源模块；1,037 页。', '22403537', 'CC BY-NC-SA 4.0'),
        'openlogic': ('开放逻辑文本', '逻辑与证明',
            '按专题学习集合、形式逻辑、证明系统与可计算性。可与其他课程交叉阅读，不必一次读完整本。',
            '722 / 722 个来源单元；859 页。含 642 个主读本单元和 80 个补充单元。',
            '22379030', 'CC BY 4.0'),
    }
    resources = []
    for key, (title, level, intro, extent, zenodo, license_) in editorial.items():
        row = next(r for r in source['releases'] if r['id'] == key)
        pdfs = [a for a in row['assets'] if a['name'].endswith('.pdf')]
        assert len(pdfs) == 1
        editable = [a for a in row['assets'] if a['name'].endswith('.zip') and 'Source' in a['name']]
        assert editable
        resources.append({
            'id': key, 'kind': 'released-translation', 'title': title, 'level': level,
            'intro': intro, 'extent': extent, 'author': 'Open Logic Project' if key == 'openlogic' else 'OpenStax',
            'language': 'zh-Hans-CN', 'license': license_, 'repository': row['repository'],
            'release': row['release_url'], 'release_tag': row['tag'], 'pdf': pdfs[0],
            'editable_sources': editable, 'zenodo': 'https://zenodo.org/records/' + zenodo,
            'evidence': {'inventory_url': row['inventory_url'], 'inventory_identity': row['inventory_identity']},
        })
    for row in source['originals']:
        resources.append({
            'id': row['id'], 'kind': 'chinese-original',
            'title': '代数学方法 · 卷' + ('一' if row['id'] == 'algebra-1' else '二'),
            'level': '进阶代数', 'intro': '李文威用中文写作的代数教材。适合已有证明基础、希望系统学习代数的读者。',
            'extent': '中文原作；提供 PDF、LaTeX 源码与编译说明。',
            'author': row['author'], 'language': 'zh-Hans', 'license': 'CC BY 4.0',
            'repository': row['repository'], 'release': row['tree_url'],
            'commit': row['commit'], 'pdf': row['pdf'], 'tex_master': row['tex'],
            'source_tree': row['tree_url'],
            'evidence': {'readme_url': row['readme_url'], 'readme_identity': row['readme_identity']},
        })
    return {
        'schema': 'chinese-program-starter/1', 'language': 'zh-Hans-CN', 'status': 'starter',
        'as_of': '2026-09-28', 'complete_curriculum': False, 'canonical_role_admissions': [],
        'source_intake': {'bytes': len(raw), 'sha256': digest(raw), 'observed_utc': source['observed_utc']},
        'verification_scope': '公开发行清单和作者源码库核对；未在本入口重新下载校验全部书籍，也不声称完成独立翻译审校。',
        'resources': resources,
        'in_progress': [
            {'title': '微积分（第二卷）', 'status': '翻译已报告完成；本次核对尚未确认完整公开发行版。',
             'repository': 'https://github.com/KokunoYumeto/openstax-foundational-stem-zh-hans-cn'},
            {'title': '微积分（第三卷）', 'status': '翻译与校对进行中，尚未完成。',
             'repository': 'https://github.com/KokunoYumeto/openstax-foundational-stem-zh-hans-cn'},
        ],
        'integration_provenance': {'model': 'gpt-6-astra', 'effort': 'ultra',
            'scope': '入口文案、资源编目和网页代码；不是所链接书籍的翻译署名。'},
    }


def link(url, label, **attrs):
    attr = ''.join(' ' + k.replace('_', '-') + '="' + html.escape(v, quote=True) + '"' for k, v in attrs.items())
    return '<a href="' + html.escape(url, quote=True) + '"' + attr + '>' + html.escape(label) + '</a>'


def card(row):
    translated = row['kind'] == 'released-translation'
    pdf_url = row['pdf'].get('browser_download_url') or row['pdf']['url']
    links = [link(pdf_url, '阅读 PDF', class_='button')]
    if translated:
        for i, item in enumerate(row['editable_sources']):
            label = '可编辑源码 ZIP' if len(row['editable_sources']) == 1 else ('主读本源码 ZIP' if 'Supplement' not in item['name'] else '补充读本源码 ZIP')
            links.append(link(item['browser_download_url'], label))
        links += [link(row['zenodo'], 'Zenodo 存档'), link(row['release'], '版本说明与完整文件')]
        note = '非官方 AI 译本；未声明已完成人工中文审校。模型及编辑历史以书籍自身的来源记录为准。'
        identity = row['release_tag']
    else:
        links += [link(row['tex_master']['url'], 'LaTeX 主文件'), link(row['source_tree'], '完整源码与编译说明')]
        note = '这是作者的中文原作，不是本项目的 AI 译文。LaTeX 主文件依赖完整源码库，单独下载不能重建整本书。'
        identity = row['commit'][:12]
    return f'''<article id="{row['id']}" class="book" data-resource-kind="{row['kind']}">
<div class="eyebrow">{html.escape(row['level'])} · {'已公开译本' if translated else '中文原作'}</div>
<h3>{html.escape(row['title'])}</h3><p>{html.escape(row['intro'])}</p>
<p class="extent">{html.escape(row['extent'])}</p><nav class="book-links" aria-label="{html.escape(row['title'])}的阅读与源码">{''.join(links)}</nav>
<p class="detail">{html.escape(row['author'])} · {html.escape(row['license'])} · <code>{identity}</code></p>
<p class="detail">{note}</p></article>'''.replace('class-=', 'class=')


def render(data):
    translations = '\n'.join(card(r) for r in data['resources'] if r['kind'] == 'released-translation')
    originals = '\n'.join(card(r) for r in data['resources'] if r['kind'] == 'chinese-original')
    pending = ''.join('<li><strong>' + html.escape(r['title']) + '</strong> — ' + html.escape(r['status']) + '</li>' for r in data['in_progress'])
    return f'''<!doctype html>
<html lang="zh-Hans-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>开放数学课程 · 中文起步版</title><meta name="description" content="从已公开的中文数学教材开始自主学习。逻辑、代数、三角学与微积分；附阅读、源码和来源说明。">
<meta name="theme-color" content="#15302e"><link rel="canonical" href="{ORIGIN}zh/"><link rel="stylesheet" href="styles.css"></head>
<body><a class="skip" href="#main">跳转到正文</a>
<header><div class="bar"><a class="brand" href="./">开放数学课程</a><nav aria-label="语言选择">
<a href="./" lang="zh-Hans-CN" aria-current="page">中文（起步版）</a>
<a href="../id/" lang="id" hreflang="id">Bahasa Indonesia</a><a href="../en/" lang="en" hreflang="en">English</a></nav></div></header>
<main id="main"><section class="intro"><p class="eyebrow">自主学习 · 开放教材 · 简体中文</p>
<h1>从这里，开始学数学。</h1><p class="lead">把已经能读的中文教材放在一起，让你找到下一本书，也能拿到可编辑的源码。</p>
<p class="boundary">这是中文课程的<strong>起步入口</strong>，目前收录 3 部已公开译本和 2 卷中文原作。
它不是 40 门课程已全部汉化的声明；中文课程衔接、章节对应和学习工具还将逐步补齐。</p>
<nav class="sections" aria-label="本页内容"><a href="#start">怎样开始</a><a href="#translations">已公开译本</a><a href="#originals">中文原作</a><a href="#next">接下来</a><a href="#sources">来源与维护</a></nav></section>
<section id="start"><h2>按你现在的基础来选</h2><ol class="path">
<li><strong>先补基础：</strong>从<a href="#algebra-trigonometry">代数与三角学</a>开始，熟悉函数和图像。</li>
<li><strong>接着学微积分：</strong>有了函数与三角学基础，再读<a href="#calculus-1">微积分第一卷</a>。</li>
<li><strong>学习证明与更深入的代数：</strong><a href="#openlogic">开放逻辑文本</a>可按专题阅读；有证明基础后，再考虑<a href="#originals">代数学方法</a>。</li>
</ol><p class="detail">这是选书建议，不是已验证的完整先修课程表，也不表示所有教材难度相同。读不懂某一节时，可以先返回相关基础内容。</p></section>
<section id="translations"><h2>现在可以读的中文译本</h2><div class="books">{translations}</div></section>
<section id="originals"><h2>直接使用中文原作</h2><p>不需要先翻译到另一种语言再翻回来。以下两卷直接链接作者公开的中文书与 LaTeX 源码。</p><div class="books">{originals}</div>
<p class="detail">这里只登记可用书籍，尚未把两卷书等同于整个课程中的所有代数课程或认定章节映射已经完成。</p></section>
<section id="next"><h2>接下来补齐什么</h2><p>截至 {data['as_of']} 的工作状态：</p><ul>{pending}</ul>
<p>{link(data['in_progress'][0]['repository'], '查看中文 OpenStax 项目的公开进展')}</p>
<p>后续再把现有教材接入课程图、章节导航、习题和教师材料。尚未收录的课程不显示为已完成，也不拿英文内容冒充中文教材。</p></section>
<section id="sources"><h2>来源、可编辑文件与维护</h2>
<p>本入口不重新托管或改写书籍。每部书保留自己的作者、版本、许可与修订历史；许可范围以对应来源为准。</p>
<p>{html.escape(data['verification_scope'])} 公开清单中的散列值是发行方提供的身份信息，不是本入口重新验证整本书的证明。</p>
<p>{link('catalog.json', '下载资源目录 JSON')} · {link('chinese-starter-source-v1.zip', '下载本入口完整可编辑源码 ZIP')} · {link('build-receipt.json', '查看构建记录')}</p>
<p class="detail">入口文案、资源编目和网页代码由 OpenAI Codex — gpt-6-astra，Ultra effort 生成。这不替代各书自己的翻译与审校记录。本入口是 HTML 导航页，不新制作 PDF 或书籍译文。源码包可离线重建本页；阅读所链接书籍需要联网或事先下载。</p></section>
</main><footer><a href="../id/" lang="id">Bahasa Indonesia</a> · <a href="../en/" lang="en">English</a> · <a href="#main">返回顶部</a><p>中文起步版 · 资源核对日期 {data['as_of']}</p></footer></body></html>
'''.encode('utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--intake', type=Path)
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    if args.intake:
        (DEST/'catalog.json').write_bytes(dump(intake(args.intake)))
    data = json.loads((DEST/'catalog.json').read_bytes())
    assert data['status'] == 'starter' and data['complete_curriculum'] is False
    assert data['canonical_role_admissions'] == [] and len(data['resources']) == 5
    (DEST/'index.html').write_bytes(render(data))
    members = ['LICENSE', 'scripts/build-chinese-starter-v1.py', 'scripts/test-chinese-starter-v1.py',
               'docs/zh/catalog.json', 'docs/zh/styles.css', 'docs/zh/index.html', 'docs/zh/README.txt']
    package = DEST/'chinese-starter-source-v1.zip'
    with zipfile.ZipFile(package, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 28, 0, 0, 0))
            info.external_attr = 0o100644 << 16
            z.writestr(info, (ROOT/name).read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    outputs = ['index.html', 'catalog.json', 'styles.css', 'README.txt', package.name]
    receipt = {'schema': 'chinese-starter-build/1', 'status': 'pass', 'source_members': members,
               'files': [{'path': name, 'bytes': (DEST/name).stat().st_size,
                          'sha256': digest((DEST/name).read_bytes())} for name in outputs],
               'new_translations': 0, 'new_canonical_course_admissions': 0}
    (DEST/'build-receipt.json').write_bytes(dump(receipt))
    print(json.dumps({'status': 'pass', 'resources': 5, 'source_zip_bytes': package.stat().st_size}))


if __name__ == '__main__':
    main()
