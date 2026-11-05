"""Capture the owner's public Google Site; never uploads or changes it."""
from pathlib import Path
from urllib.request import urlopen
from html.parser import HTMLParser
import html, json, re
BASE='https://sites.google.com/view/enricoscalashomepage/'
PAGES=[('home','Home'),('publications','Publications'),('students-projects','Students Projects'),('funded-projects','Funded Projects'),('tools-software-and-experiments','Tools, Software and Experiments'),('studies','Studies'),('things-to-do-in-milan','Things to do in Milan')]
VOID={'img','br','hr','input','meta','link','source','wbr','area','base','embed','param','col','track'}
class Node:
 def __init__(self,tag='',attrs=()): self.tag=tag;self.attrs=dict(attrs);self.children=[]
 def walk(self):
  yield self
  for c in self.children:
   if isinstance(c,Node): yield from c.walk()
 def text(self): return ''.join(c.text() if isinstance(c,Node) else c for c in self.children)
class Parser(HTMLParser):
 def __init__(self): super().__init__(); self.root=Node();self.stack=[self.root]
 def handle_starttag(self,t,a):
  n=Node(t,a);self.stack[-1].children.append(n)
  if t not in VOID:self.stack.append(n)
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==t: self.stack=self.stack[:i];break
 def handle_data(self,d):self.stack[-1].children.append(d)
def render(n):
 if isinstance(n,str):return html.escape(n)
 if n.tag in ['script','style','svg','button','iframe']:return ''
 inside=''.join(render(c) for c in n.children)
 t=n.tag
 if t=='a':
  url=n.attrs.get('href','')
  if not n.text().strip():return ''
  if not url.startswith(('https://','http://','mailto:','tel:','#','/')):return inside
  return '<a href="'+html.escape(url,quote=True)+'">'+inside+'</a>'
 if t=='span':
  style=n.attrs.get('style','')
  if 'font-weight: 700' in style:return '<strong>'+inside+'</strong>'
  if 'font-style: italic' in style:return '<em>'+inside+'</em>'
 if t in ['p','ul','ol','li','strong','em','b','i','sub','sup','blockquote','h1','h2','h3','h4','h5','h6']:
  if not n.text().strip():return ''
  if t.startswith('h'):t='h2'
  return '<'+t+'>'+inside+'</'+t+'>'
 if t=='br':return '<br>'
 return inside

def extract(root):
 blocks=[]
 def visit(n):
  if n.tag in ['p','ul','ol','h1','h2','h3','h4','h5','h6'] and n.text().strip():
   blocks.append(n);return
  for c in n.children:
   if isinstance(c,Node):visit(c)
 for section in (n for n in root.walk() if n.tag=='section'):visit(section)
 return blocks
if __name__=='__main__':
 manifest=[]
 for slug,title in PAGES:
  raw=urlopen(BASE+slug).read();Path('source-snapshot/'+slug+'.html').write_bytes(raw)
  parser=Parser();parser.feed(raw.decode())
  blocks=extract(parser.root)
  content='\n'.join(render(n) for n in blocks)
  Path('content/'+slug+'.html').write_text(content)
  images=[n.attrs['src'] for n in parser.root.walk() if n.tag=='img' and 'CENy8b' in n.attrs.get('class','')]
  saved=[]
  for i,url in enumerate(images):
   data=urlopen(url).read();filename=f'{slug}-{i}.jpg';Path('public/assets/'+filename).write_bytes(data);saved.append(filename)
  links=[{'text':n.text(),'href':n.attrs.get('href')} for b in blocks for n in b.walk() if n.tag=='a' and n.text().strip()]
  manifest.append({'slug':slug,'title':title,'source':BASE+slug,'images':saved,'blocks':len(blocks),'links':links})
  print(slug,len(blocks),'blocks',len(links),'links',len(saved),'images')
 Path('content/manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
