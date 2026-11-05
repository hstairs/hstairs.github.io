"""Verify migrated text and links against the captured public source."""
from collections import Counter
from pathlib import Path
import re, sys, json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from capture_source import Parser, extract, extract_news, PAGES
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
    checked_blocks=[n for block in blocks for n in (list(n for n in block.walk() if n.tag=='li') if slug=='publications' and block.tag in ['ul','ol'] else [block])]
    for block in checked_blocks:
        if block.tag.startswith('h') and norm(block.text())==title:continue
        assert norm(block.text()) in content_text,(slug,'missing text',block.text()[:60])
    links=lambda ns:Counter((n.text(),n.attrs.get('href')) for b in ns for n in b.walk() if n.tag=='a' and n.text().strip())
    assert not (links(blocks)-links([visible])),(slug,'missing or altered original links')
    total+=sum(links(blocks).values())
    for n in output.walk():
        if n.tag not in ['a','img','script','link']:continue
        url=n.attrs.get('href',n.attrs.get('src',''))
        if url and not re.match(r'\w+:|#|//',url):
            assert (ROOT/'public'/url.split('#')[0]).exists(),('missing local target',url)
    print('PASS',slug,'text, links, local assets')
print(f'PASS: all seven pages and {total} original content links preserved.')
news=json.loads((ROOT/'content/news.json').read_text())
assert news==extract_news(parse(ROOT/'source-snapshot/home.html')),'Missing or changed original news'
homepage=parse(ROOT/'public/index.html')
for item in news:
    assert norm(item['text']) in norm(homepage.text()),('Missing news',item)
assert sum(n.tag=='time' for n in homepage.walk())==len(news)
print(f'PASS: all {len(news)} original embedded news items restored.')
additions=json.loads((ROOT/'content/publications-added.json').read_text())
publication_page=parse(ROOT/'public/publications.html')
nodes=list(publication_page.walk())
ids=[node.attrs.get('id') for node in nodes if node.attrs.get('id')]
assert len(ids)==len(set(ids)),'Duplicate publication IDs'
for record in additions:
    node=next(n for n in nodes if n.attrs.get('id')==record['id'])
    assert record['title'] in node.text(),('Missing added title',record['id'])
    for link in record['links']:
        assert any(n.tag=='a' and n.attrs.get('href')==link['url'] for n in node.walk())
coverage=json.loads((ROOT/'content/bibliography-review.json').read_text())
profile=json.loads((ROOT/'source-snapshot/scholar-profile.json').read_text())
assert len(coverage['coverage'])==len(profile['records'])==110
for item in coverage['coverage']:
    target=item['target'].split(' ')[0]
    assert target in ids,('Unaccounted Scholar record',item['title'])
assert len([n for n in nodes if n.tag=='li'])==56+len(additions)
print(f'PASS: {len(additions)} additions; all 110 Scholar records accounted for; 56 originals retained.')
