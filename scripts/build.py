"""Build static HTML and a self-contained Google Sites embed. Python stdlib only."""
from pathlib import Path
import base64, html, json, re, sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from capture_source import Parser, render

ROOT=Path(__file__).resolve().parent.parent
PAGES=json.loads((ROOT/'content/manifest.json').read_text())
OUT=ROOT/'public'
def page_content(page):
    slug=page['slug']; text=(ROOT/f'content/{slug}.html').read_text()
    if slug=='home':
        # Keep the exact content, moving contact details below the biography.
        pos=text.index('<h2>About Me')
        contact=text[:pos];text=text[pos:]
        text += '<aside class="contact">'+contact+'</aside>'
    else:
        # The page title takes the place of an identical imported first heading.
        text=re.sub(r'^<h2>'+re.escape(html.escape(page['title']))+r'</h2>\s*','',text)
    if slug=='publications':
        text=text.replace('<ul>','<ul class="publication-list">',1)
        text='<div class="filters" hidden><label for="publication-search">Search publications</label><input id="publication-search" data-publication-search type="search" placeholder="Title, author, venue or year…"><div class="result-count" data-result-count role="status" aria-live="polite"></div></div>'+text
    return text
def heading(page,embedded=False):
    if page['slug']=='home':
        src='assets/home-0.jpg'
        if embedded:src='data:image/jpeg;base64,'+base64.b64encode((OUT/src).read_bytes()).decode()
        return '<header class="page-heading home-heading"><div><p class="eyebrow">Artificial intelligence · Automated planning</p><h1>Enrico Scala</h1><p class="role">Associate Professor<br>University of Brescia</p></div><img class="portrait" src="'+src+'" width="132" height="158" alt="Enrico Scala"></header>'
    return '<header class="page-heading"><p class="eyebrow">Enrico Scala</p><h1>'+html.escape(page['title'])+'</h1></header>'
def nav(current,embed=False):
    links=''
    for p in PAGES:
        href='#'+p['slug'] if embed else ('index.html' if p['slug']=='home' else p['slug']+'.html')
        active=' aria-current="page"' if p['slug']==current else ''
        links+='<a href="'+href+'"'+active+'>'+html.escape(p['title'])+'</a>'
    home='#home' if embed else 'index.html'
    return '<aside class="sidebar"><a class="brand" href="'+home+'">Enrico Scala<span aria-hidden="true">.</span></a><p class="affiliation">University of Brescia<br>Department of Information Engineering</p><nav aria-label="Main navigation">'+links+'</nav><div class="sidebar-footer">Artificial intelligence<br>Planning &amp; scheduling</div></aside>'
def shell(title,body,embedded=False):
    head='<style>'+(OUT/'styles.css').read_text()+'</style>' if embedded else '<link rel="stylesheet" href="styles.css">'
    script='<script>'+(OUT/'site.js').read_text()+'</script>' if embedded else '<script src="site.js" defer></script>'
    return '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Enrico Scala, University of Brescia. Research in artificial intelligence, automated planning and scheduling; publications, projects and software."><title>'+html.escape(title)+' | Enrico Scala</title>'+head+'</head><body><a class="skip" href="#main">Skip to content</a>'+body+script+'</body></html>\n'
def main():
    for p in PAGES:
        name='index' if p['slug']=='home' else p['slug']
        body='<div class="layout">'+nav(p['slug'])+'<main id="main"><section>'+heading(p)+'<div class="prose">'+page_content(p)+'</div></section><footer class="footer">Enrico Scala · University of Brescia</footer></main></div>'
        (OUT/f'{name}.html').write_text(shell(p['title'],body))
    panels=''.join('<section class="embed-panel" id="'+p['slug']+'">'+heading(p,True)+'<div class="prose">'+page_content(p)+'</div></section>' for p in PAGES)
    tabs='''<script>
function showPage(){const key=location.hash.slice(1)||'home';const target=document.getElementById(key);if(!target||!target.classList.contains('embed-panel'))return;document.querySelectorAll('.embed-panel').forEach(p=>p.hidden=p!==target);document.querySelectorAll('.sidebar nav a').forEach(a=>{if(a.getAttribute('href')==='#'+key)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});document.title=target.querySelector('h1').textContent+' | Enrico Scala'}
window.addEventListener('hashchange',showPage);showPage();
</script>'''
    body='<div class="layout">'+nav('home',True)+'<main id="main">'+panels+'<footer class="footer">Enrico Scala · University of Brescia</footer></main></div>'
    embed=shell('Homepage',body,True).replace('</body>',tabs+'</body>')
    # External destinations must open outside the Google Sites iframe.
    embed=re.sub(r'<a href="((?:https?://|mailto:)[^"]*)"',r'<a target="_blank" rel="noopener" href="\1"',embed)
    (ROOT/'google-sites/embed.html').write_text(embed)
    print('Built seven static pages and google-sites/embed.html')
if __name__=='__main__':main()
