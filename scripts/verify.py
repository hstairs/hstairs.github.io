"""Verify migrated text and links against the captured public source."""
from collections import Counter
from pathlib import Path
import re, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from capture_source import Parser, extract, PAGES
ROOT=Path(__file__).resolve().parent.parent
def parse(path):
    p=Parser();p.feed(path.read_text());return p.root
def norm(text):return re.sub(r'\s+',' ',text).strip()
total=0
for slug,title in PAGES:
    source=parse(ROOT/f'source-snapshot/{slug}.html')
    blocks=extract(source)
    captured=parse(ROOT/f'content/{slug}.html')
    expected=Counter(norm(n.text()) for n in blocks)
    actual=Counter(norm(n.text()) for n in captured.children if hasattr(n,'tag'))
    assert expected==actual,(slug,'imported content differs')
    filename='index' if slug=='home' else slug
    output=parse(ROOT/f'public/{filename}.html')
    visible=next(n for n in output.walk() if n.attrs.get('class')=='prose')
    content_text=norm(visible.text())
    for block in blocks:
        if block.tag.startswith('h') and norm(block.text())==title:continue
        assert norm(block.text()) in content_text,(slug,'missing text',block.text()[:60])
    links=lambda ns:Counter((n.text(),n.attrs.get('href')) for b in ns for n in b.walk() if n.tag=='a' and n.text().strip())
    assert links(blocks)==links([visible]),(slug,'missing or altered links')
    total+=sum(links(blocks).values())
    for n in output.walk():
        if n.tag not in ['a','img','script','link']:continue
        url=n.attrs.get('href',n.attrs.get('src',''))
        if url and not re.match(r'\w+:|#|//',url):
            assert (ROOT/'public'/url.split('#')[0]).exists(),('missing local target',url)
    print('PASS',slug,'text, links, local assets')
print(f'PASS: all seven pages and {total} original content links preserved.')
