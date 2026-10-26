"""Shared helpers: page shell, robots.txt, sitemap.xml, checks. Copied per site so each folder is self-contained."""
import os,html as H,shutil,re,sys,json,struct,zlib
D="26 Oct 2026"
ISO="2026-10-26"
DISCLAIMER="For general information only. This independent site is not affiliated with any city, county or park authority. Rules, hours and access can change and may contain errors; always check the official park page and posted signs before you go. You are responsible for your dog and following local rules, and we accept no liability for decisions made using this site."
RELATED=(
    ("https://us-passport-walkin-finder.vercel.app/","US Passport Walk-in Finder"),
    ("https://south-florida-dmv-walkin-guide.vercel.app/","South Florida DMV Walk-in Guide"),
)
def esc(s): return H.escape(s,quote=True)
def clean_url(path):
    if path.startswith(('http://','https://','mailto:','tel:','//')): return path
    p=path
    while p.startswith('../'): p=p[3:]
    if p.startswith('./'): p=p[2:]
    if p.endswith('/index.html'): p=p[:-len('index.html')]
    elif p in ('index.html','/index.html'): p='/'
    if p in ('','/'): return '/'
    if not p.startswith('/'): p='/'+p
    if p.endswith('.html') or p.endswith('/'): return p
    return p+'/'
def a(url,text='source'): return f'<a href="{esc(clean_url(url))}" rel="noopener">{esc(text)}</a>'
def _abs(base,path):
    c=clean_url(path)
    return base+'/' if c=='/' else base+c
def _crumbs(path,title,nav,crumbs):
    if crumbs: return crumbs
    if path=='index.html': return [('index.html','Home')]
    if path=='disclaimer/index.html': return [('index.html','Home'),(path,'Disclaimer')]
    if path=='404.html': return [('index.html','Home'),(path,'Page not found')]
    for p,t in nav:
        if p==path: return [('index.html','Home'),(p,t)]
    return [('index.html','Home'),(path,title)]
def _breadcrumb(base,crumbs):
    return {"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i,"name":name,"item":_abs(base,path)}
        for i,(path,name) in enumerate(crumbs,1)]}
def _article(base,canon,title,desc,brand,iso):
    pub={"@type":"Organization","name":brand,"url":base+"/","logo":{"@type":"ImageObject","url":base+"/apple-touch-icon.png"}}
    return {"@type":"Article","headline":title,"description":desc,"datePublished":iso,"dateModified":iso,
        "inLanguage":"en-US","mainEntityOfPage":canon,"url":canon,"image":base+"/og.png",
        "author":{"@type":"Organization","name":brand,"url":base+"/"},"publisher":pub}
def _graph(s,path,title,desc,canon,crumbs,faq,kind,iso):
    g=[_breadcrumb(s.base,crumbs)]
    if kind=='home':
        g=[
            {"@type":"WebSite","@id":s.base+"/#website","url":s.base+"/","name":s.brand,"description":desc,
             "inLanguage":"en-US","publisher":{"@id":s.base+"/#organization"}},
            {"@type":"Organization","@id":s.base+"/#organization","name":s.brand,"url":s.base+"/",
             "logo":{"@type":"ImageObject","url":s.base+"/apple-touch-icon.png"}},
            g[0],
        ]
    elif kind=='content':
        g.append(_article(s.base,canon,title,desc,s.brand,iso))
        if faq:
            g.append({"@type":"FAQPage","mainEntity":[
                {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":ans}} for q,ans in faq]})
    return {"@context":"https://schema.org","@graph":g}
def _warn(s,path,title,desc):
    if not 50<=len(title)<=60:
        s.warnings+=1
        print(f"WARNING: title length {len(title)} outside 50-60: {path}: {title}",file=sys.stderr)
    if not 120<=len(desc)<=160:
        s.warnings+=1
        print(f"WARNING: description length {len(desc)} outside 120-160: {path}: {desc}",file=sys.stderr)
class Site:
    def __init__(s,root,base,brand,nav,footer,css,verification=None):
        s.out=os.path.join(root,'site'); s.base=base.rstrip('/'); s.brand=brand; s.nav=nav; s.footer=footer; s.css=css
        s.verification=verification or {}; s.pages=[]; s.warnings=0
        if os.path.exists(s.out): shutil.rmtree(s.out)
        os.makedirs(s.out)
    def page(s,path,title,desc,body,faq=None,crumbs=None,listed=True,checked=None):
        _warn(s,path,title,desc)
        show,iso=checked if checked else (D,ISO)
        kind='home' if path=='index.html' else 'error' if path=='404.html' else 'content'
        canon=s.base+'/'+path.replace('index.html','')
        crumbs=_crumbs(path,title,s.nav,crumbs)
        nav=''.join(f'<a href="{esc(clean_url(p))}">{esc(t)}</a>' for p,t in s.nav)
        ver=''.join(f'<meta name="{esc(n)}" content="{esc(v)}" />' for n,v in s.verification.items() if v)
        robots='<meta name="robots" content="noindex">' if kind=='error' else ''
        og_type='article' if kind=='content' else 'website'
        article=''
        if kind=='content':
            article=f'<meta property="article:published_time" content="{iso}"><meta property="article:modified_time" content="{iso}">'
        ld=json.dumps(_graph(s,path,title,desc,canon,crumbs,faq,kind,iso),ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
        img=s.base+'/og.png'
        rel=''.join(f'<a href="{esc(u)}" rel="noopener">{esc(t)}</a>' for u,t in RELATED)
        if len(RELATED)==2: rel=rel.replace('</a><a ','</a> and <a ',1)
        h=f'''<!doctype html><html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{esc(canon)}">{ver}{robots}<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{esc(s.brand)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{esc(canon)}"><meta property="og:image" content="{esc(img)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{esc(s.brand)}"><meta property="og:locale" content="en_US">{article}<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{esc(img)}"><script type="application/ld+json">{ld}</script><style>{s.css}</style><script defer src="/_vercel/insights/script.js"></script></head><body>
<header><a class="brand" href="/">{esc(s.brand)}</a><nav>{nav}</nav></header>
<div class="unofficial">Unofficial and independent guide. Not a government website.</div>
<p class="top-disclaimer">{esc(DISCLAIMER)}</p>
<main><p class="checked">Last checked: {show}</p>
{body}
</main><footer><p>{s.footer}</p><p>{esc(DISCLAIMER)}</p><p><strong>Related guides:</strong> {rel}.</p><p><a href="/disclaimer/">Disclaimer</a></p><p>Last checked: {show}.</p></footer></body></html>'''
        for bad in ('\u2014','\u2013','&mdash;','&ndash;'): assert bad not in h,(path,bad)
        p=os.path.join(s.out,path); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w').write(h)
        if listed: s.pages.append((path,iso))
    def finish(s):
        bots=['GPTBot','OAI-SearchBot','ChatGPT-User','PerplexityBot','Bingbot','Googlebot','ClaudeBot','*']
        open(os.path.join(s.out,'robots.txt'),'w').write(''.join(f'User-agent: {b}\nAllow: /\n\n' for b in bots)+f'Sitemap: {s.base}/sitemap.xml\n')
        open(os.path.join(s.out,'sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{s.base}/{p.replace("index.html","")}</loc><lastmod>{mod}</lastmod></url>\n' for p,mod in sorted(s.pages))+'</urlset>\n')
        open(os.path.join(s.out,'favicon.svg'),'w').write(FAVICON)
        _write_png(os.path.join(s.out,'apple-touch-icon.png'),_apple_icon())
        _write_png(os.path.join(s.out,'og.png'),_og_image())
        print('meta warnings:',s.warnings)
# 5x7 glyphs, top row first, bit 4 is the left pixel.
_FONT={
"A":[0b01110,0b10001,0b10001,0b11111,0b10001,0b10001,0b10001],
"B":[0b11110,0b10001,0b10001,0b11110,0b10001,0b10001,0b11110],
"C":[0b01111,0b10000,0b10000,0b10000,0b10000,0b10000,0b01111],
"D":[0b11110,0b10001,0b10001,0b10001,0b10001,0b10001,0b11110],
"E":[0b11111,0b10000,0b10000,0b11110,0b10000,0b10000,0b11111],
"F":[0b11111,0b10000,0b10000,0b11110,0b10000,0b10000,0b10000],
"G":[0b01111,0b10000,0b10000,0b10111,0b10001,0b10001,0b01111],
"H":[0b10001,0b10001,0b10001,0b11111,0b10001,0b10001,0b10001],
"I":[0b01110,0b00100,0b00100,0b00100,0b00100,0b00100,0b01110],
"L":[0b10000,0b10000,0b10000,0b10000,0b10000,0b10000,0b11111],
"M":[0b10001,0b11011,0b10101,0b10101,0b10001,0b10001,0b10001],
"N":[0b10001,0b11001,0b10101,0b10011,0b10001,0b10001,0b10001],
"O":[0b01110,0b10001,0b10001,0b10001,0b10001,0b10001,0b01110],
"P":[0b11110,0b10001,0b10001,0b11110,0b10000,0b10000,0b10000],
"R":[0b11110,0b10001,0b10001,0b11110,0b10100,0b10010,0b10001],
"S":[0b01111,0b10000,0b10000,0b01110,0b00001,0b00001,0b11110],
"T":[0b11111,0b00100,0b00100,0b00100,0b00100,0b00100,0b00100],
"U":[0b10001,0b10001,0b10001,0b10001,0b10001,0b10001,0b01110],
"W":[0b10001,0b10001,0b10001,0b10101,0b10101,0b11011,0b10001],
",":[0b00000,0b00000,0b00000,0b00000,0b00110,0b00110,0b01100],
" ": [0,0,0,0,0,0,0],
}
class _Img:
    def __init__(s,w,h,color):
        s.w,s.h=w,h; s.buf=bytearray(bytes(color)*w*h)
    def rect(s,x,y,w,h,color):
        c=bytes(color); x0,y0,x1,y1=int(x),int(y),int(x+w),int(y+h)
        for yy in range(max(0,y0),min(s.h,y1)):
            row=yy*s.w
            for xx in range(max(0,x0),min(s.w,x1)):
                i=(row+xx)*3; s.buf[i:i+3]=c
    def ellipse(s,cx,cy,rx,ry,color):
        c=bytes(color)
        if rx<=0 or ry<=0: return
        for y in range(int(cy-ry)-1,int(cy+ry)+2):
            if y<0 or y>=s.h: continue
            for x in range(int(cx-rx)-1,int(cx+rx)+2):
                if x<0 or x>=s.w: continue
                if ((x+0.5-cx)/rx)**2+((y+0.5-cy)/ry)**2<=1:
                    i=(y*s.w+x)*3; s.buf[i:i+3]=c
    def paw(s,cx,cy,sc,color):
        for dx,dy,r in ((-2.15,-2.35,0.92),(-0.75,-3.25,0.95),(0.75,-3.15,0.95),(2.2,-2.15,0.82)):
            s.ellipse(cx+dx*sc,cy+dy*sc,r*sc,r*sc*1.15,color)
        s.ellipse(cx,cy+sc*0.85,sc*2.15,sc*1.7,color)
    def text(s,msg,x,y,sc,color):
        for ch in msg:
            glyph=_FONT.get(ch)
            if glyph:
                for ry,bits in enumerate(glyph):
                    for rx in range(5):
                        if bits&(1<<(4-rx)): s.rect(x+rx*sc,y+ry*sc,sc,sc,color)
            x+=6*sc
def _write_png(path,img):
    raw=b''.join(b'\x00'+bytes(img.buf[y*img.w*3:(y+1)*img.w*3]) for y in range(img.h))
    def chunk(tag,data):
        return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
    png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',img.w,img.h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
    open(path,'wb').write(png)
def _apple_icon():
    navy,sand,white=(18,59,92),(244,209,148),(255,255,255)
    im=_Img(180,180,navy); im.rect(0,146,180,34,sand); im.paw(90,78,18,white); return im
def _og_image():
    navy,sand,foam,white=(18,59,92),(244,209,148),(214,232,240),(255,255,255)
    im=_Img(1200,630,navy); im.rect(0,500,1200,130,sand); im.rect(0,486,1200,14,foam)
    im.paw(220,250,34,white)
    im.text("SOUTH FLORIDA",430,155,9,white)
    im.text("DOG BEACHES",430,255,11,white)
    im.text("HOURS, PERMITS AND RULES",430,390,5,sand)
    return im
FAVICON='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><title>South Florida Dog Beaches</title><rect width="32" height="32" rx="6" fill="#123b5c"/><g fill="#ffffff"><ellipse cx="10" cy="11" rx="2.2" ry="2.8"/><ellipse cx="15.2" cy="8.4" rx="2.2" ry="2.8"/><ellipse cx="20.2" cy="9" rx="2.2" ry="2.8"/><ellipse cx="23.6" cy="13.2" rx="2" ry="2.5"/><ellipse cx="16" cy="20.2" rx="6" ry="4.6"/></g></svg>'''
CSS='''body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#1a1a1a;line-height:1.55;background:#fafaf7}header{background:#123b5c;color:#fff;padding:.7rem 1rem;display:flex;flex-wrap:wrap;gap:.6rem 1.2rem;align-items:center}header a{color:#fff;text-decoration:none}.brand{font-weight:700}nav{display:flex;flex-wrap:wrap;gap:.3rem .9rem;font-size:.95rem}nav a:hover{text-decoration:underline}.unofficial{background:#fff4d6;border-bottom:1px solid #e6cf8a;padding:.4rem 1rem;font-size:.9rem}.top-disclaimer{background:#f3efe4;border-bottom:1px solid #e0d8c4;margin:0;padding:.45rem 1rem;font-size:.86rem;line-height:1.45}main{max-width:1100px;margin:0 auto;padding:1rem}h1{font-size:1.7rem;line-height:1.25}h2{margin-top:1.8rem}.checked{display:inline-block;background:#e6f2ea;border:1px solid #a9d1b5;border-radius:4px;padding:.15rem .5rem;font-size:.9rem}.card{background:#fff;border:1px solid #ddd;border-radius:6px;padding:.8rem 1rem;margin:.8rem 0}.warn{border-left:6px solid #c0392b;background:#fdeeee}.note{border-left:6px solid #d68910;background:#fff8ec}.conf{border-left:6px solid #8e44ad;background:#f6effa}.wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;background:#fff;font-size:.93rem}th,td{border:1px solid #ddd;padding:.45rem;vertical-align:top;text-align:left}th{background:#eef3f7}.src{font-size:.85rem;color:#555}.tag{display:inline-block;font-size:.78rem;padding:0 .35rem;border-radius:3px;background:#eee;margin-right:.2rem}.tag.ok{background:#d8f0de}.tag.no{background:#f8d7d7}.tag.mix{background:#fdebc8}footer{max-width:1100px;margin:2rem auto;padding:1rem;font-size:.88rem;color:#444;border-top:1px solid #ddd}footer p{margin:.4rem 0}a{color:#0b5394}input#q{width:100%;max-width:420px;padding:.45rem;margin:.5rem 0;font-size:1rem}'''
