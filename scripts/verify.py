"""Verify current content, embedded routes, and unchanged migration records."""
from collections import Counter
from pathlib import Path
import re, sys, json
from urllib.parse import unquote
sys.path.insert(0,str(Path(__file__).resolve().parent))
from capture_source import Parser, extract, extract_news, PAGES
ROOT=Path(__file__).resolve().parent.parent
def parse(path):
    p=Parser();p.feed(path.read_text());return p.root
def norm(text):return re.sub(r'\s+',' ',text).strip()
total=0
# These pages were deliberately revised after the original migration.
REVISED={'home','funded-projects','students-projects'}
embed=parse(ROOT/'google-sites/embed.html')
embed_nodes=list(embed.walk())
embed_ids=[n.attrs['id'] for n in embed_nodes if n.attrs.get('id')]
assert len(embed_ids)==len(set(embed_ids)),'Duplicate embed IDs'
for slug,title in PAGES:
    source=parse(ROOT/f'source-snapshot/{slug}.html')
    blocks=extract(source)
    captured=parse(ROOT/f'content/{slug}.html')
    expected=Counter(norm(n.text()) for n in blocks)
    actual=Counter(norm(n.text()) for n in captured.children if hasattr(n,'tag'))
    if slug not in REVISED:
        assert expected==actual,(slug,'imported content differs')
    elif slug=='students-projects':
        # Only this terminology change is intended on the thesis topics page.
        expected=Counter(norm(n.text()).replace('PDDL+ representation languages','PDDL+ representation formalisms') for n in blocks)
        assert expected==actual,(slug,'unexpected thesis topic change')
    filename='index' if slug=='home' else slug
    output=parse(ROOT/f'public/{filename}.html')
    visible=next(n for n in output.walk() if n.attrs.get('class')=='prose')
    content_text=norm(visible.text())
    current_blocks=[n for n in captured.children if hasattr(n,'tag')]
    rendered_blocks=current_blocks if slug in REVISED else blocks
    checked_blocks=[n for block in rendered_blocks for n in (list(n for n in block.walk() if n.tag=='li') if slug=='publications' and block.tag in ['ul','ol'] else [block])]
    for block in checked_blocks:
        if block.tag.startswith('h') and norm(block.text())==title:continue
        assert norm(block.text()) in content_text,(slug,'missing text',block.text()[:60])
    links=lambda ns:Counter((n.text(),n.attrs.get('href')) for b in ns for n in b.walk() if n.tag=='a' and n.text().strip())
    assert not (links(rendered_blocks)-links([visible])),(slug,'missing or altered content links')
    total+=sum(links(rendered_blocks).values())
    panel=next(n for n in embed_nodes if n.attrs.get('id')==slug)
    embedded_prose=next(n for n in panel.walk() if n.attrs.get('class')=='prose')
    assert norm(embedded_prose.text())==content_text,(slug,'embed content differs')
    for node in visible.walk():
        if node.tag!='a':continue
        href=node.attrs.get('href','')
        if re.match(r'\w+:|//',href):continue
        path,sep,anchor=href.partition('#')
        target=ROOT/'public'/path if path else ROOT/f'public/{filename}.html'
        assert target.is_file(),('missing local page',href)
        if anchor:
            assert any(n.attrs.get('id')==unquote(anchor) for n in parse(target).walk()),('missing anchor',href)
        route=next((p_slug for p_slug,_ in PAGES if path==('index' if p_slug=='home' else p_slug)+'.html'),None)
        embedded_href='#'+route+('/'+anchor if anchor else '') if route else href
        assert any(n.tag=='a' and n.attrs.get('href')==embedded_href for n in embedded_prose.walk()),('missing embed link',embedded_href)
    for n in output.walk():
        if n.tag not in ['a','img','script','link']:continue
        url=n.attrs.get('href',n.attrs.get('src',''))
        if url and not re.match(r'\w+:|#|//',url):
            assert (ROOT/'public'/url.split('#')[0]).exists(),('missing local target',url)
    print('PASS',slug,'text, links, local assets')
print(f'PASS: all seven pages, {total} content links, and static/embed content parity.')
for node in embed_nodes:
    if node.tag!='a':continue
    href=node.attrs.get('href','')
    if not href.startswith('#'):continue
    route,sep,anchor=href[1:].partition('/')
    target=next((n for n in embed_nodes if n.attrs.get('id')==route),None)
    assert target is not None,('missing embed route',href)
    if anchor:
        assert any(n.attrs.get('id')==anchor for n in target.walk()),('missing embedded anchor',href)
print('PASS: all embedded routes and citation targets resolve.')
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
