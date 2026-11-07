"""Build static HTML and a self-contained Google Sites embed. Python stdlib only."""
from pathlib import Path
import base64, html, json, re, sys
from datetime import datetime
sys.path.insert(0,str(Path(__file__).resolve().parent))
from capture_source import Parser

ROOT=Path(__file__).resolve().parent.parent
PAGES=json.loads((ROOT/'content/manifest.json').read_text())
OUT=ROOT/'public'
def news_content():
    items=json.loads((ROOT/'content/news.json').read_text())
    items=sorted(items,key=lambda item:datetime.strptime(item['date'],'%B %Y'),reverse=True)
    def listing(entries):
        return '<ul class="news-list">'+''.join('<li><time datetime="'+datetime.strptime(item['date'],'%B %Y').strftime('%Y-%m')+'">'+html.escape(item['date'])+'</time><span>'+html.escape(item['text'])+'</span></li>' for item in entries)+'</ul>'
    return '<section class="news-panel" aria-labelledby="news-title"><h2 id="news-title">News</h2>'+listing(items[:6])+'<details><summary>Earlier news ('+str(len(items[6:]))+')</summary>'+listing(items[6:])+'</details></section>'
def bibliography_content():
    parser=Parser()
    original_html=(ROOT/'content/publications.html').read_text()
    parser.feed(original_html)
    original=[node for node in parser.root.walk() if node.tag=='li']
    original_markup=re.findall(r'<li>.*?</li>',original_html,flags=re.S)
    assert len(original_markup)==len(original)
    entries=[]
    for index,node in enumerate(original,1):
        year=re.search(r'\b(20\d{2})\b',node.text())
        entries.append((int(year[1]) if year else 0,original_markup[index-1].replace('<li>',f'<li id="original-{index}">',1)))
    additions=json.loads((ROOT/'content/publications-added.json').read_text())
    related=[]
    for record in additions:
        esc=html.escape
        venue=esc(record['venue'])
        if record.get('volume'):venue+=' '+esc(record['volume'])
        if record.get('issue'):venue+='('+esc(record['issue'])+')'
        if record.get('pages'):venue+=', '+esc(record['pages'])
        kind='<span class="publication-type">'+esc(record['type'])+'</span> ' if record.get('type') else ''
        links=' · '.join('<a href="'+esc(link['url'],quote=True)+'">'+esc(link['label'])+'</a>' for link in record['links'])
        citation='<li id="'+esc(record['id'],quote=True)+'"><p>'+kind+esc(record['authors'])+' ('+esc(record['year'] or 'n.d.')+'). <strong>'+esc(record['title'])+'</strong>. <em>'+venue+'</em>. '+links+'</p></li>'
        target=related if record['category']=='related' else entries
        target.append((int(record['year']) if record['year'].isdigit() else 0,citation))
    listing=lambda items:'<ul class="publication-list">'+''.join(citation for year,citation in sorted(items,key=lambda row:row[0],reverse=True))+'</ul>'
    reviewed=json.loads((ROOT/'content/bibliography-review.json').read_text())['accessed']
    date=datetime.strptime(reviewed,'%Y-%m-%d').strftime('%d %B %Y').lstrip('0')
    intro='<p class="bibliography-intro"><a href="https://scholar.google.com/citations?user=lgfpklAAAAAJ&amp;hl=en">Google Scholar</a> · <a href="https://dblp.org/pid/79/10105.html">DBLP</a><br><span>Updated '+date+'</span></p>'
    return intro+'<h2>Publications and preprints</h2>'+listing(entries)+'<h2>Other research outputs</h2>'+listing(related)
def page_content(page):
    slug=page['slug']; text=(ROOT/f'content/{slug}.html').read_text()
    if slug=='home':
        # Move contact details below the biography and research sections.
        pos=text.index('<h2>About Me')
        contact=text[:pos];text=text[pos:]
        text = news_content()+text+'<aside class="contact">'+contact+'</aside>'
    else:
        # The page title takes the place of an identical imported first heading.
        text=re.sub(r'^<h2>'+re.escape(html.escape(page['title']))+r'</h2>\s*','',text)
    if slug=='publications':
        text=bibliography_content()
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
    # Route local page links inside the self-contained embed, including citations.
    routes={('index' if p['slug']=='home' else p['slug'])+'.html':p['slug'] for p in PAGES}
    def embed_links(markup):
        def replace(match):
            path,sep,anchor=match[1].partition('#')
            if path not in routes:return match[0]
            return 'href="#'+routes[path]+('/'+anchor if anchor else '')+'"'
        return re.sub(r'href="([^"]+)"',replace,markup)
    panels=''.join('<section class="embed-panel" id="'+p['slug']+'">'+heading(p,True)+'<div class="prose">'+embed_links(page_content(p))+'</div></section>' for p in PAGES)
    tabs='''<script>
function showPage(){
  const [key, anchor] = (location.hash.slice(1)||'home').split('/');
  const target=document.getElementById(key);
  if(!target||!target.classList.contains('embed-panel'))return;
  const changed=target.hidden;
  document.querySelectorAll('.embed-panel').forEach(p=>p.hidden=p!==target);
  document.querySelectorAll('.sidebar nav a').forEach(a=>{
    if(a.getAttribute('href')==='#'+key)a.setAttribute('aria-current','page');
    else a.removeAttribute('aria-current');
  });
  document.title=target.querySelector('h1').textContent+' | Enrico Scala';
  const entry=anchor?document.getElementById(anchor):null;
  if(entry&&target.contains(entry)){
    if(entry.hidden){
      const search=target.querySelector('[data-publication-search]');
      if(search){search.value='';search.dispatchEvent(new Event('input'));}
    }
    entry.scrollIntoView();
  }else if(changed){window.scrollTo(0,0);}
}
window.addEventListener('hashchange',showPage);showPage();
</script>'''
    body='<div class="layout">'+nav('home',True)+'<main id="main">'+panels+'<footer class="footer">Enrico Scala · University of Brescia</footer></main></div>'
    embed=shell('Homepage',body,True).replace('</body>',tabs+'</body>')
    # External destinations must open outside the Google Sites iframe.
    embed=re.sub(r'<a href="((?:https?://|mailto:)[^"]*)"',r'<a target="_blank" rel="noopener" href="\1"',embed)
    (ROOT/'google-sites/embed.html').write_text(embed)
    print('Built seven static pages and google-sites/embed.html')
if __name__=='__main__':main()
