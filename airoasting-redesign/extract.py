import json,re,sys
from bs4 import BeautifulSoup
s=BeautifulSoup(open(sys.argv[1],encoding='utf-8').read(),'html.parser')
T=lambda e:re.sub(r'\s+',' ',e.get_text(' ',strip=True)).strip() if e else ''
def ic(e):
    sv=e.find('svg') if e else None
    if not sv: return ''
    inner=''.join(str(c) for c in sv.children).strip()
    inner=re.sub(r'\s+',' ',inner)
    inner=re.sub(r' ?pathlength="1"| ?style="--d:[\d.]+s"','',inner)
    return inner
def card(a):
    h2=a.find('h2'); ti=T(h2).replace('↗','').strip()
    return dict(h=a.get('href'),n=(a.select_one('[data-no]') or {}).get('data-no') if a.select_one('[data-no]') else None,
      f='featured' in a['class'],o='card-out' in a['class'] or (a.get('href','').startswith('http')),
      ic=ic(a.select_one('.card-icon')),ti=ti,
      m=[[T(x),' '.join(x.get('class',[]))] for x in a.select('.card-meta > span')],
      d=T(a.find('p')))
out={}
# hero
hero=s.select_one('header.hero')
out['hero']=dict(
 title=T(hero.select_one('.visually-hidden')),
 sub=T(hero.select_one('.cover-sub')),sub2=T(hero.select_one('.cover-sub2')),
 steps=[dict(href=a['href'],term=a.get('data-term'),label=a.get('aria-label'),name=T(a.select_one('.cs-name')),ic=ic(a)) for a in hero.select('.cover-steps a')],
 author=T(hero.select_one('.cover-author-go')).replace('↗',''),affil=T(hero.select_one('.cover-affil')),
 band=T(hero.select_one('.band-line')),
 bandCards=[dict(href=a['href'],b=T(a.find('b')),s=T(a.find('span'))) for a in hero.select('.band-card')],
 cue=T(hero.select_one('.cover-cue')),
 flaps=[dict(tag=T(a.select_one('.flap-tag')),name=T(a.select_one('.flap-name')),desc=T(a.select_one('.flap-desc'))) for a in hero.select('.flap-item')],
 models=[dict(brand=T(x.select_one('.ce-brand')),pills=[T(p) for p in x.select('.ce-pill')]) for x in hero.select('.ce-set')],
)
secs=[]
for sec in s.select('.card-section'):
    blocks=[]
    for c in sec.find_all(recursive=False):
        cl=c.get('class',[])
        if 'section-header' in cl or 'section-subtitle' in cl: continue
        if 'track-label' in cl:
            b=c.select_one('.track-label-badge'); blocks.append(dict(k='L',b=T(b),bc=b['class'][-1],x=T(c.select_one('.track-label-text')))); continue
        if 'code-track-info' in cl:
            blocks.append(dict(k='I',items=[dict(b=T(x.select_one('.track-label-badge')),bc=x.select_one('.track-label-badge')['class'][-1],ti=T(x.select_one('.track-info-title')),d=T(x.select_one('.track-info-desc'))) for x in c.select('.track-info-card')])); continue
        if c.name=='section' and 'cards' in cl:
            blocks.append(dict(k='C',col2='col-2' in cl,cards=[card(a) for a in c.select('a.card')])); continue
        if c.select('.voice-card'):
            blocks.append(dict(k='V',v=[dict(q=T(v.find(['p','blockquote'])),tags=[T(t) for t in v.select('.voice-tag')]) for v in c.select('.voice-card')])); continue
        txt=T(c)
        if txt: blocks.append(dict(k='D',t=txt))
    secs.append(dict(id=sec.get('id'),num=T(sec.select_one('.section-num')),ti=T(sec.select_one('.section-title')),sub=T(sec.select_one('.section-subtitle')),blocks=blocks))
out['sections']=secs
# nav
out['nav']=[dict(href=a['href'],num=T(a.select_one('.guide-btn-num')),t=T(a).replace(T(a.select_one('.guide-btn-num')),'',1).strip()) for a in s.select('.guide-btn')]
# newsletter
nl=s.select_one('.newsletter-section'); cats=[]
for el in nl.select('.acc-row > .card'):
    d=dict(ic=ic(el.select_one('.card-icon')),ti=T(el.find('h2')).replace('↗','').strip(),d=T(el.find('p')),h=el.get('href'))
    if el.get('data-target'):
        p=nl.select_one('#'+el['data-target'])
        d['items']=[dict(h=a.get('href'),ic=ic(a.select_one('.card-icon')),ti=T(a.find('h2')).replace('↗','').strip(),d=T(a.find('p'))) for a in p.select('a')] if p else []
    cats.append(d)
out['more']=dict(title=T(nl.select_one('.newsletter-header-text')),sub=T(nl.select_one('.newsletter-header-sub')),cats=cats)
json.dump(out,open(sys.argv[2],'w',encoding='utf-8'),ensure_ascii=False,indent=1)
