"""Dependency-free editorial publishing. Drafts never enter the production build."""
import argparse, html, json, math, re, shutil
from datetime import date
from email.utils import formatdate
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://vanshxrastogi.github.io'
CATEGORIES = {'workflows':'Filmmaking workflows','camera':'Camera & visual direction','postproduction':'Audio & post-production','tools':'Tool decisions','commercial':'Commercial production'}
BIO = 'Vansh Rastogi is an AI filmmaker based in Prayagraj, India, and an employee at StoryLab by Devansh. This is his personal portfolio and educational blog; it is not a StoryLab company website.'
E = html.escape

def inline(text):
    text = E(text)
    def link(m):
        label, url = m.groups()
        if not (url.startswith('/') or url.startswith('#') or url.startswith('https://')):
            raise ValueError('Unsafe Markdown URL')
        return f'<a href="{url}">{label}</a>'
    text = re.sub(r'\[([^\]]+)\]\(([^ )]+)\)', link, text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)

def markdown(text):
    out, toc, para, items = [], [], [], []
    def flush():
        if para: out.append('<p>'+inline(' '.join(para))+'</p>'); para.clear()
        if items: out.append('<ul>'+''.join('<li>'+inline(x)+'</li>' for x in items)+'</ul>'); items.clear()
    seen = set()
    for line in text.splitlines():
        if line.startswith('## '):
            flush(); title=line[3:]; anchor=re.sub('[^a-z0-9]+','-',title.lower()).strip('-')
            if anchor in seen: raise ValueError('Duplicate heading')
            seen.add(anchor); toc.append((anchor,title)); out.append(f'<h2 id="{anchor}">{inline(title)}</h2>')
        elif line.startswith('- '):
            if para: flush()
            items.append(line[2:])
        elif not line.strip(): flush()
        else:
            if items: flush()
            para.append(line)
    flush(); return ''.join(out), toc

def load_posts(include_drafts=False):
    posts=[]; slugs=set()
    for path in sorted((ROOT/'content/blog').glob('*.md')):
        meta, body=path.read_text(encoding='utf-8').split('\n---\n',1); p=json.loads(meta)
        for key in ('slug','title','description','category','status','updated','sources'): assert p.get(key), (path,key)
        assert re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',p['slug']) and p['slug'] not in slugs
        assert p['category'] in CATEGORIES and p['status'] in ('draft','published')
        slugs.add(p['slug']); date.fromisoformat(p['updated'])
        if p['status']=='published':
            assert p.get('reviewed') is True and p.get('published'), 'Publication needs editorial approval/date'
            assert date.fromisoformat(p['published']) <= date.today()
        elif not include_drafts: continue
        p['body'],p['toc']=markdown(body); p['minutes']=max(1,math.ceil(len(body.split())/200)); posts.append(p)
    return sorted(posts,key=lambda p:p.get('published',p['updated']),reverse=True)

def page(title,description,path,body,kind='CollectionPage',extra=None,noindex=False):
    schema={'@context':'https://schema.org','@type':kind,'name':title,'url':ORIGIN+path}
    if extra: schema.update(extra)
    crumbs=[{'@type':'ListItem','position':1,'name':'Portfolio','item':ORIGIN+'/'}, {'@type':'ListItem','position':2,'name':'Blog','item':ORIGIN+'/blog/'}]
    if path != '/blog/': crumbs.append({'@type':'ListItem','position':3,'name':title,'item':ORIGIN+path})
    social_image=(extra or {}).get('image',ORIGIN+'/media/hero-poster.jpg')
    encoded=json.dumps([schema,{'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':crumbs}],ensure_ascii=False).replace('<','\\u003c')
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} | Vansh Rastogi</title><meta name="description" content="{E(description,quote=True)}"><meta name="robots" content="{'noindex,follow' if noindex else 'index,follow'}"><link rel="canonical" href="{ORIGIN+path}"><meta property="og:title" content="{E(title,quote=True)}"><meta property="og:description" content="{E(description,quote=True)}"><meta property="og:url" content="{ORIGIN+path}"><meta property="og:type" content="{'article' if kind=='Article' else 'website'}"><meta property="og:image" content="{E(social_image,quote=True)}"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{E(social_image,quote=True)}"><link rel="icon" href="/favicon-vr.png?v=4"><link rel="stylesheet" href="/blog/blog.css"><link rel="alternate" type="application/rss+xml" title="Vansh Rastogi filmmaking notes" href="/blog/feed.xml"><script type="application/ld+json">{encoded}</script></head><body><a class="skip" href="#main">Skip to content</a><header class="blog-header"><a class="wordmark" href="/">VANSH RASTOGI<span>FILMMAKING NOTES</span></a><nav aria-label="Main navigation"><a href="/#home">Home</a><a href="/#work">Work</a><a href="/#about">About</a><a href="/#contact">Contact ↗</a><a href="/blog/" aria-current="page">Blog</a></nav></header><main id="main">{body}</main><footer><p>Personal notes on making better films.</p><nav aria-label="Blog footer"><a href="/blog/author/">About the author</a><a href="/blog/editorial-policy/">Editorial policy</a><a href="/blog/archive/">Archive</a><a href="/blog/feed.xml">RSS</a><a href="/privacy.html">Privacy</a><a href="/terms.html">Terms</a></nav><p>© {date.today().year} Vansh Rastogi</p></footer><script src="/blog/search.js" defer></script></body></html>'''

def cover(p, lazy=False):
    name=p.get('cover','frame-plan.svg')
    assert re.fullmatch(r'[a-z0-9-]+\.(?:png|jpg|webp|svg)',name), 'Invalid cover path'
    alt=p.get('coverAlt','Three storyboard frames connected from intention to shot to edit')
    width=int(p.get('coverWidth',1200)); height=int(p.get('coverHeight',600))
    loading='lazy' if lazy else 'eager'
    return f'<img src="/blog/{name}" width="{width}" height="{height}" alt="{E(alt,quote=True)}" loading="{loading}" decoding="async">'

def card(p,featured=False):
    return f'''<article class="article-card {'featured' if featured else ''}" data-search="{E((p['title']+' '+p['description']+' '+CATEGORIES[p['category']]).lower(),quote=True)}"><div class="card-cover">{cover(p,True)}</div><p class="eyebrow">{E(CATEGORIES[p['category']])} / {p['minutes']} MIN READ</p><h2><a href="/blog/{p['slug']}/">{E(p['title'])}</a></h2><p>{E(p['description'])}</p><span class="read">Read the guide ↗</span></article>'''

def build_blog(destination,include_drafts=False):
    destination=Path(destination); target=destination/'blog'; target.mkdir(parents=True,exist_ok=True)
    for asset in (ROOT/'blog-assets').glob('*'): shutil.copy2(asset,target/asset.name)
    posts=load_posts(include_drafts); paths=[]
    def write(path,content):
        f=destination/path.lstrip('/'); f.parent.mkdir(parents=True,exist_ok=True); f.write_text(content,encoding='utf-8')
        url='/'+str(f.relative_to(destination)).replace('\\','/'); paths.append(url.removesuffix('index.html'))
    cats='<nav class="category-nav" aria-label="Blog categories">'+''.join(f'<a href="/blog/category/{slug}/">{E(label)}</a>' for slug,label in CATEGORIES.items())+'</nav>'
    notice='<p class="draft-banner">EDITORIAL PREVIEW — unpublished drafts; not indexed or included in RSS.</p>' if include_drafts else ''
    intro=f'''{notice}<section class="blog-hero"><p class="eyebrow">THE CRAFT BEHIND THE FRAME</p><h1>Make the next<br><em>frame matter.</em></h1><p>Practical guides to AI filmmaking, camera decisions and careful finishing. Written for creators who want a useful process, not another list of promises.</p></section>{cats}<label class="search-label" for="article-search">Find a guide<input id="article-search" type="search" placeholder="Search topics, techniques or workflows" autocomplete="off"></label><p id="search-status" role="status" aria-live="polite"></p>'''
    listing=''.join(card(p,i==0) for i,p in enumerate(posts)) or '<p class="empty">The first guides are in editorial review. Explore the <a href="/guides/ai-film-brief.html">film briefing guide</a> or <a href="/guides/character-continuity.html">character continuity notes</a> meanwhile.</p>'
    write('/blog/index.html',page('AI filmmaking notes','Practical AI filmmaking guides, camera decisions and post-production workflows.','/blog/',intro+'<section class="article-grid">'+listing+'</section>',noindex=include_drafts))
    for cat,label in CATEGORIES.items():
        matching=[p for p in posts if p['category']==cat]
        body=f'<p class="eyebrow"><a href="/blog/">BLOG</a> / CATEGORY</p><h1>{E(label)}</h1><section class="article-grid">'+(''.join(card(p) for p in matching) or '<p>Guides for this category are in preparation. <a href="/blog/">Browse available guides</a>.</p>')+'</section>'
        write(f'/blog/category/{cat}/index.html',page(label,'Guides to '+label.lower()+'.',f'/blog/category/{cat}/',body,noindex=include_drafts or not matching))
    for p in posts:
        path=f"/blog/{p['slug']}/"; isdraft=p['status']=='draft'
        toc='<nav class="toc" aria-label="Table of contents"><strong>In this guide</strong>'+''.join(f'<a href="#{a}">{E(t)}</a>' for a,t in p['toc'])+'</nav>'
        sources='<section class="sources"><h2>Sources & further reading</h2><ul>'+''.join(f'<li><a href="{E(s[1],quote=True)}">{E(s[0])}</a></li>' for s in p['sources'])+'</ul></section>'
        related=[x for x in posts if x['slug']!=p['slug']][:2]
        body=f'''{notice}<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Portfolio</a> / <a href="/blog/">Blog</a> / <a href="/blog/category/{p['category']}/">{E(CATEGORIES[p['category']])}</a></nav><article class="reading"><p class="eyebrow">{E(CATEGORIES[p['category']])}</p><h1>{E(p['title'])}</h1><p class="dek">{E(p['description'])}</p><p class="byline"><a href="/blog/author/">Vansh Rastogi</a> · {p['minutes']} min read · {'Draft updated' if isdraft else 'Published'} <time datetime="{p.get('published',p['updated'])}">{p.get('published',p['updated'])}</time></p><figure>{cover(p)}<figcaption>{E(p.get("coverCaption","Original planning diagram: intention → shot → edit."))}</figcaption></figure>{toc}<div class="prose">{p['body']}</div>{sources}<aside class="author"><h2>About the author</h2><p>{E(BIO)}</p></aside><div class="ad-region" hidden data-ad-placement="after-article"></div></article><section><h2>Continue reading</h2><div class="article-grid">{''.join(card(x) for x in related)}</div></section>'''
        extra={'headline':p['title'],'description':p['description'],'author':{'@type':'Person','name':'Vansh Rastogi','url':ORIGIN+'/blog/author/'},'dateModified':p['updated'],'mainEntityOfPage':ORIGIN+path,'image':ORIGIN+'/blog/'+p.get('cover','frame-plan.svg')}
        if not isdraft: extra['datePublished']=p['published']
        write(path+'index.html',page(p['title'],p['description'],path,body,'Article',extra,include_drafts or isdraft))
    write('/blog/author/index.html',page('About Vansh Rastogi','Personal author biography and editorial responsibility.','/blog/author/',f'<p class="eyebrow">AUTHOR</p><h1>Vansh Rastogi</h1><div class="reading prose"><p>{E(BIO)}</p><p>These guides explain production choices and practical planning exercises. They do not claim that every listed tool has been personally tested. Tool-specific facts link to primary sources; demonstrations and hypothetical examples are labelled.</p><p><a href="/#work">Explore the portfolio</a> · <a href="/#contact">Contact Vansh</a></p></div>','ProfilePage',noindex=include_drafts))
    write('/blog/editorial-policy/index.html',page('Editorial policy','How articles are researched, reviewed and corrected.','/blog/editorial-policy/','<p class="eyebrow">TRUST & TRANSPARENCY</p><h1>Useful before frequent.</h1><div class="reading prose"><h2>Research and review</h2><p>Use primary documentation for tool capabilities, prices and policies. Dates identify when claims were checked. AI may assist drafting; publication requires human editorial review. A draft is not evidence of firsthand testing.</p><h2>Original examples</h2><p>Exercises are illustrative unless a documented production test is supplied. Do not invent clients, outcomes, credentials or performance numbers.</p><h2>Corrections</h2><p>Send corrections through the <a href="/#contact">contact page</a>. Substantive changes receive an updated date; cosmetic edits do not.</p><h2>Commercial disclosures</h2><p>There are currently no affiliate links in these guides. Any future sponsorship or affiliate relationship must be disclosed beside the relevant recommendation. Ads remain disabled until site approval and required consent setup are complete.</p></div>',noindex=include_drafts))
    for n in range(max(1,math.ceil(len(posts)/9))):
        path='/blog/archive/' if n==0 else f'/blog/archive/page/{n+1}/'
        nav='<nav aria-label="Archive pages">'+''.join(f'<a href="{"/blog/archive/" if k==0 else f"/blog/archive/page/{k+1}/"}">Page {k+1}</a> ' for k in range(max(1,math.ceil(len(posts)/9))))+'</nav>'
        write(path+'index.html',page(f'Article archive — page {n+1}','Browse filmmaking articles. ',path,'<h1>Article archive</h1><div class="article-grid">'+''.join(card(p) for p in posts[n*9:n*9+9])+'</div>'+nav,noindex=include_drafts or not posts))
    rss=ET.Element('rss',version='2.0'); channel=ET.SubElement(rss,'channel')
    for k,v in [('title','Vansh Rastogi — Filmmaking Notes'),('link',ORIGIN+'/blog/'),('description','Practical filmmaking guides')]: ET.SubElement(channel,k).text=v
    for p in posts:
        if p['status']!='published': continue
        item=ET.SubElement(channel,'item')
        for k,v in [('title',p['title']),('link',ORIGIN+'/blog/'+p['slug']+'/'),('guid',ORIGIN+'/blog/'+p['slug']+'/'),('description',p['description'])]: ET.SubElement(item,k).text=v
    (target/'feed.xml').write_bytes(ET.tostring(rss,encoding='utf-8',xml_declaration=True))
    # Rebuild discovery from real indexable HTML; drafts and empty categories stay out.
    ns='http://www.sitemaps.org/schemas/sitemap/0.9'; ET.register_namespace('',ns); sitemap=ET.Element('{'+ns+'}urlset')
    for f in sorted(destination.rglob('*.html')):
        text=f.read_text(encoding='utf-8')
        if re.search(r'<meta[^>]+name="robots"[^>]+content="[^"]*noindex',text): continue
        rel='/'+f.relative_to(destination).as_posix(); rel=rel.removesuffix('index.html')
        ET.SubElement(ET.SubElement(sitemap,'{'+ns+'}url'),'{'+ns+'}loc').text=ORIGIN+rel
    (destination/'sitemap.xml').write_bytes(ET.tostring(sitemap,encoding='utf-8',xml_declaration=True))
    return posts

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--destination',default='dist'); parser.add_argument('--include-drafts',action='store_true'); args=parser.parse_args()
    build_blog(args.destination,args.include_drafts)
