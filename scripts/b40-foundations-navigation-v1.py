"""Register the seven sealed B40 pages using their already functioning navigation."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urljoin,urlsplit

ROOT=Path(__file__).resolve().parents[1]
PREFIX='docs/en/readers/hefferon-foundations/'
ORIGIN='https://kokunoyumeto.github.io/program-matematika-indonesia/'
class Links(HTMLParser):
    def __init__(self):super().__init__();self.hrefs=[];self.locale=None
    def handle_starttag(self,tag,attrs):
        values=dict(attrs)
        if tag=='a' and 'href' in values:self.hrefs.append(values['href'])
        if tag=='html':self.locale=values.get('lang')

def validate(root=ROOT):
    manifest=json.loads((root/PREFIX/'FOUNDATIONS_MANIFEST.json').read_bytes())
    rows=[r for r in manifest['public_files'] if r['path'].endswith('.html')]
    assert len(rows)==7 and len({r['path'] for r in rows})==7
    result=[]
    for row in rows:
        path=Path(row['path']);assert not path.anchor and '..' not in path.parts and '\\' not in row['path'] and ':' not in row['path']
        raw=(root/PREFIX/path).read_bytes()
        assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],'Sealed B40 body changed'
        parser=Links();parser.feed(raw.decode('utf-8'));assert parser.locale=='en'
        public=ORIGIN+PREFIX.removeprefix('docs/')+path.as_posix()
        links={urljoin(public,href) for href in parser.hrefs}
        assert ORIGIN+'en/programme/' in links and 'https://hefferon.net/linearalgebra/' in links
        if row['path']!='index.html':assert ORIGIN+PREFIX.removeprefix('docs/')+'index.html' in links
        for href in parser.hrefs:
            # Native navigation keeps real relative source downloads and section links.
            if not urlsplit(href).scheme and not href.startswith('#'):
                local=(root/PREFIX/path).parent/urlsplit(href).path
                assert local.resolve().is_relative_to((root/PREFIX).resolve()) and local.is_file(),'Broken B40 local route'
        result.append({'document':PREFIX+row['path'],'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                       'english_programme_return':True,'original_author_link':True,'native_body_unchanged':True})
    return {'schema':'b40-native-navigation-validation/1','state':'pass','files':result,'html_documents':7,'scope':'Six selected sections and index; not the entire textbook.'}

if __name__=='__main__':
    receipt=validate()
    path=ROOT/'backend/authority/central-reader-navigation-v1.json'
    original=path.read_bytes();nav=json.loads(original)
    names={r['document'] for r in receipt['files']}
    nav['generic_surfaces']=[r for r in nav['generic_surfaces'] if r['document'] not in names]+[
        {'document':r['document'],'state':'sealed-b40-english-foundations','navigation_required':False,
         'navigation_provider':'b40-foundations-native-v1','locale':'en'} for r in receipt['files']]
    nav['summary']['generic_html_documents']=len(nav['generic_surfaces'])
    nav['summary']['classified_html_documents']=sum(nav['summary'][k] for k in
        ['reader_html_documents','gateway_html_documents','course_surface_html_documents','generic_html_documents'])
    assert path.read_bytes()==original,'Concurrent navigation edit'
    path.write_text(json.dumps(nav,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'backend/authority/b40-native-navigation-validation-v1.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'state':'pass','registered_native_html_pages':7,'reader_bytes_changed':False}))
