"""Page shell for the South Florida dog beaches guide.

Layout, topic menu, sticky header, search, and checks follow the sister guide
at github.com/Deon-jvn-life/sa-refugees-usa-guide, restyled for this site.
Facts, dates, sources, and page copy are supplied by tools/build.py.
"""
import os,html as H,shutil,re,sys,json,struct,zlib
D="26 Oct 2026"
ISO="2026-10-26"
DISCLAIMER=("For general information only. This independent site is not affiliated with any city, county or park authority. "
            "Rules, hours and access can change and may contain errors; always check the official park page and posted signs before you go. "
            "You are responsible for your dog and following local rules, and we accept no liability for decisions made using this site.")
UNOFFICIAL="Unofficial and independent guide. Not a government website."
HEADER_NOTE="Independent guide. Not a government website."
RELATED=(
    ("https://us-passport-walkin-finder.vercel.app/","US Passport Walk-in Finder"),
    ("https://south-florida-dmv-walkin-guide.vercel.app/","South Florida DMV Walk-in Guide"),
)
# Coastal header. White text, the foam subtitle, and the sand gold are checked
# against every sRGB and Oklab sample of this gradient in check_contrast().
HEAD_STOPS=("#0A3A48","#0E5564","#0C4A62")
INK="#1A1814"
PAPER="#F7F4EE"
LINK="#083E56"
VISITED="#3D2A6B"
GOLD="#F6E3A4"
SUB="#E6F4F1"
NOTICE_BG="#FFF6DB"
FONT="system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

def esc(s): return H.escape(s,quote=True)
def clean_url(path):
    if path.startswith(('http://','https://','mailto:','tel:','//')): return path
    frag=''
    if '#' in path:
        path,frag=path.split('#',1)
        frag='#'+frag
    p=path
    while p.startswith('../'): p=p[3:]
    if p.startswith('./'): p=p[2:]
    if p.endswith('/index.html'): p=p[:-len('index.html')]
    elif p in ('index.html','/index.html'): p='/'
    if p in ('','/'): return '/'+frag if frag else '/'
    if not p.startswith('/'): p='/'+p
    if p.endswith('.html') or p.endswith('/'): return p+frag
    return p+'/'+frag
def a(url,text='source'): return f'<a href="{esc(clean_url(url))}" rel="noopener">{esc(text)}</a>'
def slug(t):
    t=H.unescape(re.sub(r'<[^>]+>','',t))
    return re.sub(r'[^a-z0-9]+','-',t.lower()).strip('-') or 'section'
def _abs(base,path):
    c=clean_url(path)
    return base+'/' if c=='/' else base+c

def _lin(c):
    c=c/255
    return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def _lum(h):
    h=h.lstrip('#')
    r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    return 0.2126*_lin(r)+0.7152*_lin(g)+0.0722*_lin(b)
def _contrast(a,b):
    hi,lo=max(_lum(a),_lum(b)),min(_lum(a),_lum(b))
    return (hi+0.05)/(lo+0.05)
def _srgb_lin(c):
    c=c/255
    return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def _lin_srgb(c):
    v=12.92*c if c<=0.0031308 else 1.055*(max(c,0)**(1/2.4))-0.055
    return max(0,min(255,round(v*255)))
def _oklab(h):
    r,g,b=[_srgb_lin(int(h.lstrip('#')[i:i+2],16)) for i in (0,2,4)]
    l=0.4122214708*r+0.5363325363*g+0.0514459929*b
    m=0.2119034982*r+0.6806995451*g+0.1073969566*b
    s=0.0883024619*r+0.2817188376*g+0.6299787005*b
    l_,m_,s_=l**(1/3),m**(1/3),s**(1/3)
    return (0.2104542553*l_+0.7936177850*m_-0.0040720468*s_,
            1.9779984951*l_-2.4285922050*m_+0.4505937099*s_,
            0.0259040371*l_+0.7827717662*m_-0.8086757660*s_)
def _oklab_hex(L,A,B):
    l_=L+0.3963377774*A+0.2158037573*B
    m_=L-0.1055613458*A-0.0638541728*B
    s_=L-0.0894841775*A-1.2914855480*B
    l,m,s=l_**3,m_**3,s_**3
    r=4.0767416621*l-3.3077115913*m+0.2309699292*s
    g=-1.2684380046*l+2.6097574011*m-0.3413193965*s
    b=-0.0041960863*l-0.7034186147*m+1.7076147010*s
    return '#%02x%02x%02x'%(_lin_srgb(r),_lin_srgb(g),_lin_srgb(b))
def _gradient_samples(stops):
    labs=[_oklab(s) for s in stops]
    out=[]
    for i in range(41):
        t=i/40
        if t<=0.5:
            u=t/0.5; a,b=stops[0],stops[1]; la,lb=labs[0],labs[1]
        else:
            u=(t-0.5)/0.5; a,b=stops[1],stops[2]; la,lb=labs[1],labs[2]
        ar,ag,ab=[int(a.lstrip('#')[k:k+2],16) for k in (0,2,4)]
        br,bg,bb=[int(b.lstrip('#')[k:k+2],16) for k in (0,2,4)]
        srgb='#%02x%02x%02x'%tuple(round(ar+(br-ar)*u) if False else round([ar,ag,ab][k]+([br,bg,bb][k]-[ar,ag,ab][k])*u) for k in range(3))
        ok=_oklab_hex(*(la[k]+(lb[k]-la[k])*u for k in range(3)))
        out.extend((srgb,ok))
    return out
def check_contrast():
    samples=_gradient_samples(HEAD_STOPS)
    mins={}
    for fg,need,name in (('#FFFFFF',4.5,'white'),(SUB,4.5,'subtitle'),(GOLD,3.0,'gold')):
        worst=min(_contrast(fg,bg) for bg in samples)
        mins[name]=worst
        if worst<need:
            raise SystemExit(f'Header contrast for {name} is {worst:.2f}, need {need}')
    pairs=[
        (INK,PAPER,4.5,'ink on paper'),
        (INK,'#FFFFFF',4.5,'ink on white'),
        (INK,NOTICE_BG,4.5,'ink on notice'),
        (INK,GOLD,4.5,'ink on sand button'),
        (LINK,PAPER,4.5,'link on paper'),
        (LINK,'#FFFFFF',4.5,'link on white'),
        (LINK,NOTICE_BG,4.5,'link on notice'),
        (LINK,'#EEF4F1',4.5,'link on summary'),
        (LINK,'#FFF8EC',4.5,'link on note'),
        (LINK,'#F6F1FA',4.5,'link on conflict'),
        (LINK,'#FDEEEE',4.5,'link on warning'),
        (LINK,'#E5F2EA',4.5,'link on checked'),
        (LINK,'#E7EFE9',4.5,'link on table header'),
        (VISITED,PAPER,4.5,'visited on paper'),
        (VISITED,'#FFFFFF',4.5,'visited on white'),
        (VISITED,NOTICE_BG,4.5,'visited on notice'),
        (VISITED,'#EEF4F1',4.5,'visited on summary'),
        (VISITED,'#FFF8EC',4.5,'visited on note'),
        (VISITED,'#F6F1FA',4.5,'visited on conflict'),
        ('#3E3A34','#FFFFFF',4.5,'source text on white'),
        ('#143024','#E5F2EA',4.5,'checked text'),
        (INK,'#FDEBC8',4.5,'tag text'),
    ]
    for fg,bg,need,name in pairs:
        ratio=_contrast(fg,bg)
        if ratio<need:
            raise SystemExit(f'Contrast for {name} is {ratio:.2f}, need {need}')
    return mins

SEARCH_JS=r'''(function(){
  var el=document.getElementById("search-data");
  var input=document.getElementById("q");
  var box=document.getElementById("search-results");
  if(!el||!input||!box) return;
  var pages=[];
  try { pages=JSON.parse(el.textContent); } catch(e){ return; }
  function esc(s){
    return String(s).replace(/[&<>"']/g, function(c){
      return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c];
    });
  }
  function activeWords(q){
    var t=String(q||"").trim().toLowerCase();
    if(t.length<2) return [];
    return t.split(/\s+/).filter(function(w){ return w; });
  }
  function match(blob, ws){
    if(!ws.length) return true;
    blob=String(blob).toLowerCase();
    for(var i=0;i<ws.length;i++) if(blob.indexOf(ws[i])<0) return false;
    return true;
  }
  function filterIndex(q){
    var root=document.getElementById("page-index");
    if(!root) return;
    var ws=activeWords(q);
    var items=root.querySelectorAll("li");
    var shown=0;
    for(var i=0;i<items.length;i++){
      var li=items[i];
      var blob=li.textContent+" "+(li.getAttribute("data-keywords")||"");
      var ok=match(blob, ws);
      li.hidden=!ok;
      if(ok) shown++;
    }
    var sections=root.querySelectorAll("section");
    for(var s=0;s<sections.length;s++){
      var sec=sections[s];
      var lis=sec.querySelectorAll("li");
      var any=false;
      for(var k=0;k<lis.length;k++) if(!lis[k].hidden) any=true;
      sec.hidden=!any;
    }
    var status=document.getElementById("index-status");
    if(status){
      if(!ws.length) status.textContent="Showing every page.";
      else if(!shown) status.textContent="No page matches. Try a different word, or clear the search.";
      else status.textContent="Showing "+shown+" of "+items.length+" pages.";
    }
  }
  function show(q){
    var ws=activeWords(q);
    if(!ws.length){
      box.hidden=true;
      box.innerHTML="";
    } else {
      var hits=[];
      for(var i=0;i<pages.length;i++){
        var p=pages[i];
        var blob=p.t+" "+p.s+" "+p.g+" "+(p.k||"");
        if(match(blob, ws)) hits.push(p);
        if(hits.length===8) break;
      }
      if(!hits.length){
        box.innerHTML="<p class=\"search-empty\">No matching page. Open the <a href=\"/find/\">full page list</a>.</p>";
      } else {
        var html="<ul>";
        for(var j=0;j<hits.length;j++){
          var hit=hits[j];
          html+="<li><a href=\""+esc(hit.u)+"\"><strong>"+esc(hit.t)+"</strong><span>"+esc(hit.s)+"</span></a></li>";
        }
        html+="</ul>";
      }
      box.hidden=false;
    }
    filterIndex(q);
  }
  input.addEventListener("input", function(){ show(input.value); });
  input.addEventListener("keydown", function(e){
    if(e.key==="Escape"){ box.hidden=true; box.innerHTML=""; }
  });
  document.addEventListener("click", function(e){
    if(!box.contains(e.target) && e.target!==input){ box.hidden=true; }
  });
  var initial="";
  try { initial=new URLSearchParams(window.location.search).get("q")||""; } catch(err){ initial=""; }
  if(initial){ input.value=initial; show(initial); }
  else filterIndex("");
  var sums=document.querySelectorAll(".grp > summary");
  for(var n=0;n<sums.length;n++){
    sums[n].addEventListener("click", function(){
      var parent=this.parentNode;
      var open=document.querySelectorAll(".grp[open]");
      for(var i=0;i<open.length;i++) if(open[i]!==parent) open[i].removeAttribute("open");
    });
  }
})();'''
FILTER_JS=r'''(function(){
  var input=document.getElementById("place-filter");
  var status=document.getElementById("place-filter-status");
  if(!input) return;
  function apply(){
    var v=input.value.trim().toLowerCase();
    var rows=document.querySelectorAll("main table tbody tr");
    var shown=0;
    for(var i=0;i<rows.length;i++){
      var ok=!v || rows[i].textContent.toLowerCase().indexOf(v)>-1;
      rows[i].hidden=!ok;
      if(ok) shown++;
    }
    if(!status) return;
    if(!v) status.textContent="";
    else if(!shown) status.textContent="No line matches. Try a different word, or clear the filter.";
    else status.textContent="Showing "+shown+" of "+rows.length+" lines.";
  }
  input.addEventListener("input", apply);
})();'''
MAP_JS=r'''(function(){
  var frame=document.querySelector(".map-frame");
  if(!frame) return;
  var canvas=frame.querySelector(".map-canvas");
  var dataEl=frame.querySelector(".map-data");
  if(!canvas||!dataEl) return;
  var pins=[];
  try { pins=JSON.parse(dataEl.textContent); } catch(err){ return; }
  if(!pins.length) return;
  var started=false;
  var mapMade=false;
  function esc(s){
    return String(s).replace(/[&<>"']/g, function(c){
      return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c];
    });
  }
  function fail(){
    var p=canvas.querySelector(".map-pending");
    if(p) p.textContent="The map did not load. The list on this page is complete.";
  }
  function init(){
    if(mapMade) return;
    if(!window.L){ fail(); return; }
    mapMade=true;
    var reduce=false;
    try { reduce=window.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch(err){ reduce=false; }
    var style=document.createElement("style");
    style.textContent=".leaflet-container{font-family:inherit;background:#E7EFE9;z-index:0}.leaflet-container .leaflet-popup-content,.leaflet-container .leaflet-control,.leaflet-container .leaflet-control-attribution{font-family:inherit}.leaflet-popup-content{font-size:1rem;line-height:1.5;color:#1A1814;margin:12px 16px}.map-pop-name{font-weight:700;margin:0 0 8px}.leaflet-popup-content a{color:#083E56}.leaflet-popup-content a:visited{color:#3D2A6B}.leaflet-container a.leaflet-popup-close-button{width:28px;height:28px;font-size:1.25rem;line-height:28px;color:#1A1814}.leaflet-control-zoom a{width:44px;height:44px;line-height:44px;font-size:1.25rem;color:#1A1814}.leaflet-control-attribution{font-size:.875rem;line-height:1.4;color:#1A1814;background:rgba(255,255,255,.95)}.leaflet-control-attribution a{color:#083E56}.leaflet-control-attribution a:visited{color:#3D2A6B}.map-canvas.leaflet-container:focus-visible{outline:3px solid #1A1814;outline-offset:3px}";
    document.head.appendChild(style);
    var pending=canvas.querySelector(".map-pending");
    if(pending) pending.remove();
    var map=L.map(canvas, {
      scrollWheelZoom:false,
      zoomAnimation:!reduce,
      fadeAnimation:!reduce,
      markerZoomAnimation:!reduce
    });
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom:19,
      attribution:'&copy; <a href="https://www.openstreetmap.org/copyright" rel="noopener">OpenStreetMap</a> contributors'
    }).addTo(map);
    var bounds=[];
    for(var i=0;i<pins.length;i++){
      var pin=pins[i];
      var lat=Number(pin.lat), lon=Number(pin.lon);
      if(!isFinite(lat)||!isFinite(lon)) continue;
      var marker=L.marker([lat, lon], {alt:String(pin.name||"Place"), title:String(pin.name||"Place"), keyboard:true});
      var hrefAttr="href";
      var nameHtml=pin.url ? "<a "+hrefAttr+"=\""+esc(pin.url)+"\">"+esc(pin.name)+"</a>" : esc(pin.name);
      var html="<p class=\"map-pop-name\">"+nameHtml+"</p><p>"+esc(pin.address)+"</p><p><a "+hrefAttr+"=\""+esc(pin.directions)+"\" target=\"_blank\" rel=\"noopener\">Get directions<span class=\"vh\"> to "+esc(pin.name)+" (opens in a new tab)</span></a></p>";
      marker.bindPopup(html, {maxWidth:320});
      marker.addTo(map);
      bounds.push([lat, lon]);
    }
    if(!bounds.length){ fail(); return; }
    if(bounds.length===1) map.setView(bounds[0], 16);
    else map.fitBounds(bounds, {padding:[32,32], maxZoom:14});
    function arm(){ map.scrollWheelZoom.enable(); }
    canvas.addEventListener("click", arm);
    map.whenReady(function(){ map.invalidateSize(); });
  }
  function loadScript(){
    if(window.L){ init(); return; }
    var s=document.createElement("script");
    s.src="/assets/leaflet/leaflet.js";
    s.onload=init;
    s.onerror=fail;
    document.body.appendChild(s);
  }
  function start(){
    if(started) return;
    started=true;
    var link=document.createElement("link");
    link.rel="stylesheet";
    link.href="/assets/leaflet/leaflet.css";
    var cssDone=false;
    function cssReady(){
      if(cssDone) return;
      cssDone=true;
      loadScript();
    }
    link.onload=cssReady;
    link.onerror=fail;
    document.head.appendChild(link);
    setTimeout(function(){ if(link.sheet) cssReady(); }, 80);
  }
  if(!("IntersectionObserver" in window)){ start(); return; }
  var io=new IntersectionObserver(function(entries){
    for(var i=0;i<entries.length;i++){
      if(entries[i].isIntersecting){ io.disconnect(); start(); return; }
    }
  }, {rootMargin:"240px 0px"});
  io.observe(canvas);
})();'''
DOCK_JS=r'''(function(){
  var header=document.getElementById("site-header");
  var slot=document.getElementById("head-slot");
  var toggle=document.querySelector(".search-toggle");
  var search=document.getElementById("site-search");
  var nav=document.getElementById("site-nav");
  if(!header||!slot) return;
  var docked=false;
  var fullH=0;
  function pxVar(name, fallback){
    var raw=getComputedStyle(document.documentElement).getPropertyValue(name)||fallback;
    var n=parseFloat(raw);
    if(String(raw).indexOf("rem")>=0){
      n=n*parseFloat(getComputedStyle(document.documentElement).fontSize||"16");
    }
    return n||parseFloat(fallback)||0;
  }
  function placeHeader(){
    var b=header.getBoundingClientRect().bottom;
    document.documentElement.style.setProperty("--header-bottom", Math.max(0, Math.round(b))+"px");
  }
  function setSearchOpen(open){
    if(!search||!toggle) return;
    if(open && !document.body.classList.contains("is-docked")) open=false;
    search.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open?"true":"false");
    if(open) closeGroups();
    if(open){
      var input=document.getElementById("q");
      if(input) input.focus();
    }
    placeHeader();
  }
  function measure(){
    if(docked) return;
    fullH=header.offsetHeight;
  }
  function closeGroups(){
    var open=document.querySelectorAll(".grp[open]");
    for(var i=0;i<open.length;i++) open[i].removeAttribute("open");
  }
  function updateHint(){
    if(!nav) return;
    var more=nav.scrollWidth>nav.clientWidth+8;
    var atEnd=nav.scrollLeft+nav.clientWidth>=nav.scrollWidth-8;
    var atStart=nav.scrollLeft<=8;
    document.body.classList.toggle("nav-more-right", !!(more && !atEnd));
    document.body.classList.toggle("nav-more-left", !!(more && !atStart));
  }
  function revealCurrent(){
    if(!nav) return;
    var cur=nav.querySelector(".grp.has-current");
    if(!cur || nav.scrollWidth<=nav.clientWidth+8){ updateHint(); return; }
    var left=cur.offsetLeft-(nav.clientWidth-cur.offsetWidth)/2;
    nav.scrollLeft=left<0?0:left;
    updateHint();
  }
  function dock(){
    if(docked) return;
    closeGroups();
    setSearchOpen(false);
    measure();
    if(!fullH) fullH=header.offsetHeight;
    slot.style.height=fullH+"px";
    document.body.classList.add("is-docked");
    docked=true;
    revealCurrent();
    placeHeader();
  }
  function undock(){
    if(!docked) return;
    setSearchOpen(false);
    closeGroups();
    document.body.classList.remove("is-docked");
    slot.style.height="";
    docked=false;
    measure();
    updateHint();
    placeHeader();
  }
  function onScroll(){
    var y=window.scrollY||document.documentElement.scrollTop||0;
    var compact=pxVar("--header-compact","100");
    var line=fullH-compact;
    if(!fullH) measure();
    if(!docked){
      measure();
      if(fullH>compact && y>fullH-compact) dock();
    } else if(y<line-24){
      undock();
    }
    placeHeader();
  }
  if(toggle){
    toggle.addEventListener("click", function(){
      var open=toggle.getAttribute("aria-expanded")==="true";
      setSearchOpen(!open);
    });
  }
  document.addEventListener("keydown", function(e){
    if(e.key!=="Escape") return;
    setSearchOpen(false);
    closeGroups();
    var box=document.getElementById("search-results");
    if(box){ box.hidden=true; box.innerHTML=""; }
  });
  document.addEventListener("click", function(e){
    if(header.contains(e.target)) return;
    setSearchOpen(false);
    closeGroups();
  });
  if(nav){
    nav.addEventListener("scroll", updateHint, {passive:true});
    var topicSums=nav.querySelectorAll(".grp>summary");
    for(var s=0;s<topicSums.length;s++){
      topicSums[s].addEventListener("click", function(){ setSearchOpen(false); placeHeader(); });
    }
  }
  document.addEventListener("focusin", function(e){
    var t=e.target;
    if(!t) return;
    if(nav && nav.contains(t) && nav.scrollWidth>nav.clientWidth+8 && t.closest){
      var grp=t.closest(".grp");
      if(grp){
        var pad=16;
        var left=grp.offsetLeft-pad;
        var right=grp.offsetLeft+grp.offsetWidth+pad;
        if(left<nav.scrollLeft) nav.scrollLeft=Math.max(0,left);
        else if(right>nav.scrollLeft+nav.clientWidth) nav.scrollLeft=right-nav.clientWidth;
        updateHint();
      }
    }
    if(!docked) return;
    if(header.contains(t)||(t.classList&&t.classList.contains("skip"))) return;
    var edge=pxVar("--scroll-pad","116");
    var r=t.getBoundingClientRect();
    if(r.bottom>edge && r.top>=edge) return;
    var y=(window.scrollY||0)+r.top-edge;
    window.scrollTo(0, y<0?0:y);
  });
  window.addEventListener("scroll", onScroll, {passive:true});
  window.addEventListener("resize", function(){
    if(docked) undock();
    measure();
    onScroll();
    updateHint();
  });
  measure();
  onScroll();
  updateHint();
  revealCurrent();
})();'''
TOC_BOOT='<script>if(window.matchMedia("(min-width:960px)").matches){var d=document.currentScript.previousElementSibling;if(d&&d.tagName==="DETAILS")d.open=true;}</script>'
MARK='''<svg class="mark" viewBox="0 0 32 32" aria-hidden="true" focusable="false"><ellipse cx="10" cy="11" rx="2.2" ry="2.8"/><ellipse cx="15.2" cy="8.4" rx="2.2" ry="2.8"/><ellipse cx="20.2" cy="9" rx="2.2" ry="2.8"/><ellipse cx="23.6" cy="13.2" rx="2" ry="2.5"/><ellipse cx="16" cy="20.2" rx="6" ry="4.6"/></svg>'''

class Site:
    def __init__(s,root,base,brand,groups,footer,css,verification=None):
        s.out=os.path.join(root,'site'); s.base=base.rstrip('/'); s.brand=brand; s.groups=groups
        s.footer=footer; s.css=css; s.pages=[]; s.indexable=[]; s.warnings=[]
        s.verification=verification or {}
        s.titles={p:t for g,items in groups for p,t in items}
        s.titles['index.html']='Home'
        s.summaries={}; s.read_next={}; s.aliases={}; s.parents={}; s.sequences=[]; s.checked={}
        s._queue=[]; s._search_cache=None
        if os.path.exists(s.out): shutil.rmtree(s.out)
        os.makedirs(s.out)
    def _search_json(s):
        rows=[{"u":"/","t":"Home","s":s.summaries.get('index.html',''),"g":"Home","k":s.aliases.get('index.html','dog beach park guide')}]
        for g,items in s.groups:
            for p,t in items:
                rows.append({"u":clean_url(p),"t":t,"s":s.summaries.get(p,""),"g":g,"k":s.aliases.get(p,"")})
        return json.dumps(rows,ensure_ascii=False).replace("<","\\u003c")
    def _topic(s,path):
        for g,items in s.groups:
            for p,_t in items:
                if p==path: return g
        return None
    def page(s,path,title,desc,body,faq=None,crumbs=None,listed=True,checked=None,kind=None,parent=None):
        s.summaries[path]=desc
        s._queue.append(dict(path=path,title=title,desc=desc,body=body,faq=faq,crumbs=crumbs,listed=listed,checked=checked,kind=kind,parent=parent))
    def _emit(s,path,title,desc,body,faq=None,crumbs=None,listed=True,checked=None,kind=None,parent=None):
        for label,text,lo,hi in (('title',title,50,60),('description',desc,120,160)):
            if not lo<=len(text)<=hi:
                s.warnings.append(f'{path} {label} is {len(text)} characters (want {lo} to {hi}): {text}')
        show,iso=checked if checked else s.checked.get(path,(D,ISO))
        s.checked[path]=(show,iso)
        if kind is None:
            kind='home' if path=='index.html' else 'error' if path=='404.html' else 'content'
        if '<h1>' in body:
            body=body.replace('<h1>','<h1 id="page-title">',1)
        words=re.sub(r'<[^>]+>',' ',body)
        long=len(words.split())>=80 or body.count('<h2')>=2 or '<table' in body
        summary=s.summaries.get(path,'')
        if summary and kind=='content' and long and '<h1' in body:
            body=body.replace('</h1>','</h1><div class="inshort"><p><strong>In short.</strong> '+esc(summary)+'</p></div>',1)
        h2s=re.findall(r'<h2>(.*?)</h2>',body)
        ids=[]; seen=set()
        for raw in h2s:
            base=slug(raw); n=base; i=2
            while n in seen:
                n=f'{base}-{i}'; i+=1
            seen.add(n); ids.append(n)
        state={'i':0}
        def addid(m, state=state, ids=ids):
            n=ids[state['i']]; state['i']+=1
            return f'<h2 id="{n}">{m.group(1)}</h2>'
        if ids:
            body=re.sub(r'<h2>(.*?)</h2>',addid,body)
        nav_bits=[]
        for g,items in s.groups:
            links=[]; here=False
            for p,t in items:
                cur=' aria-current="page"' if p==path else ''
                cls=' class="is-current"' if p==path else ''
                if p==path: here=True
                links.append(f'<a href="{esc(clean_url(p))}"{cls}{cur}>{esc(t)}</a>')
            mark=' aria-current="true"' if here else ''
            nav_bits.append(f'<details class="grp{" has-current" if here else ""}"><summary{mark}>{esc(g)}</summary><div class="glinks">'+''.join(links)+'</div></details>')
        nav=''.join(nav_bits)
        canon=_abs(s.base,path)
        h1m=re.search(r'<h1[^>]*>(.*?)</h1>',body,re.S)
        headline=H.unescape(re.sub(r'<[^>]+>','',h1m.group(1))) if h1m else title
        plain=headline
        topic=s._topic(path)
        parent=parent or s.parents.get(path)
        if parent is None and crumbs and len(crumbs)>=3:
            parent=(clean_url(crumbs[-2][0]), crumbs[-2][1])
        if path=='index.html':
            crumbs_html='<nav class="crumbs" aria-label="Breadcrumb"><ol><li><span aria-current="page">Home</span></li></ol></nav>'
        else:
            items_html=['<li><a href="/">Home</a></li>']
            if parent:
                items_html.append(f'<li><a href="{esc(parent[0])}">{esc(parent[1])}</a></li>')
            elif topic:
                items_html.append(f'<li><a href="/#topic-{slug(topic)}">{esc(topic)}</a></li>')
            items_html.append(f'<li><span aria-current="page">{esc(plain)}</span></li>')
            crumbs_html='<nav class="crumbs" aria-label="Breadcrumb"><ol>'+''.join(items_html)+'</ol></nav>'
        topic_html=''
        if topic and kind!='home':
            topic_html=f'<a class="topic-chip" href="/#topic-{slug(topic)}"><span class="vh">Topic: </span>{esc(topic)}</a>'
        meta=f'<p class="meta"><span class="checked">Last checked: {esc(show)}</span>{topic_html}</p>'
        m=re.match(r'(?s)(.*?</h1>(?:<div class="inshort">.*?</div>)?)(.*)\Z', body)
        head,rest=(m.group(1),m.group(2)) if m else (body,'')
        toc=''
        if len(ids)>=3:
            opened=' open' if len(ids)<=8 else ''
            lis=''.join(f'<li><a href="#{n}">{esc(H.unescape(re.sub("<[^>]+>","",raw)))}</a></li>' for raw,n in zip(h2s,ids))
            toc=f'<nav class="toc" aria-label="On this page"><details class="toc-details"{opened}><summary>On this page</summary><ul>{lis}</ul></details>{TOC_BOOT}</nav>'
        seq_label=None; seq=None
        for label,paths in s.sequences:
            if path in paths:
                seq_label,seq=label,paths; break
        pn=''
        if seq:
            i=seq.index(path)
            def step(target,word,cls):
                label=s.titles.get(target) or target
                return f'<a class="{cls}" href="{esc(clean_url(target))}"><span class="pn-k">{word}</span><span class="pn-t">{esc(label)}</span></a>'
            prev=step(seq[i-1],'Previous','prev') if i>0 else ''
            nxt=step(seq[i+1],'Next','next') if i+1<len(seq) else ''
            if prev or nxt:
                pn=f'<nav class="pn" aria-label="{esc(seq_label)}">{prev}{nxt}</nav>'
        rn_items=[]
        for dest in s.read_next.get(path) or []:
            label=s.titles.get(dest)
            if not label: continue
            blurb=s.summaries.get(dest,'')
            blurb_html=f'<span class="ls">{esc(blurb)}</span>' if blurb else ''
            rn_items.append(f'<li><a class="jump" href="{esc(clean_url(dest))}"><span class="lt">{esc(label)}</span>{blurb_html}</a></li>')
        readnext='<aside class="readnext" aria-labelledby="read-next"><h2 id="read-next">Read next</h2><ul>'+''.join(rn_items)+'</ul></aside>' if rn_items else ''
        crumbs_ld=[{"@type":"ListItem","position":1,"name":"Home","item":s.base+"/"}]
        if path!='index.html':
            pos=2
            if parent:
                crumbs_ld.append({"@type":"ListItem","position":pos,"name":parent[1],"item":s.base+parent[0] if parent[0].startswith('/') else parent[0]})
                pos+=1
            elif topic:
                crumbs_ld.append({"@type":"ListItem","position":pos,"name":topic,"item":s.base+"/#topic-"+slug(topic)})
                pos+=1
            item={"@type":"ListItem","position":pos,"name":plain}
            if kind!='error': item["item"]=canon
            crumbs_ld.append(item)
        graph=[{"@type":"BreadcrumbList","itemListElement":crumbs_ld}]
        if kind=='home':
            graph=[
                {"@type":"WebSite","@id":s.base+"/#website","url":s.base+"/","name":s.brand,"description":desc,
                 "inLanguage":"en-US","publisher":{"@id":s.base+"/#organization"}},
                {"@type":"Organization","@id":s.base+"/#organization","name":s.brand,"url":s.base+"/",
                 "logo":{"@type":"ImageObject","url":s.base+"/apple-touch-icon.png"}},
                graph[0],
            ]
        elif kind=='content':
            pub={"@type":"Organization","name":s.brand,"url":s.base+"/","logo":{"@type":"ImageObject","url":s.base+"/apple-touch-icon.png"}}
            graph.insert(0,{"@type":"Article","headline":headline,"description":desc,"datePublished":iso,"dateModified":iso,
                            "inLanguage":"en-US","mainEntityOfPage":canon,"url":canon,"image":s.base+"/og.png",
                            "author":{"@type":"Organization","name":s.brand,"url":s.base+"/"},"publisher":pub})
        if faq:
            graph.append({"@type":"FAQPage","mainEntity":[
                {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":ans}} for q,ans in faq]})
        ld=json.dumps({"@context":"https://schema.org","@graph":graph},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
        robots='<meta name="robots" content="noindex">' if kind=='error' else ''
        ver=''.join(f'<meta name="{esc(n)}" content="{esc(v)}" />' for n,v in s.verification.items() if v)
        og_type='article' if kind=='content' else 'website'
        article=''
        if kind=='content':
            article=f'<meta property="article:published_time" content="{iso}"><meta property="article:modified_time" content="{iso}">'
        img=s.base+'/og.png'
        rel=''.join(f'<a href="{esc(u)}" rel="noopener">{esc(t)}</a>' for u,t in RELATED)
        if len(RELATED)==2: rel=rel.replace('</a><a ','</a> and <a ',1)
        layout_cls='layout has-toc' if toc else 'layout'
        h=f'''<!doctype html><html lang="en-US"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="{HEAD_STOPS[0]}"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{esc(canon)}">{ver}{robots}<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{esc(s.brand)}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{esc(canon)}"><meta property="og:image" content="{esc(img)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{esc(s.brand)}"><meta property="og:locale" content="en_US">{article}<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{esc(img)}"><script type="application/ld+json">{ld}</script><style>{s.css}</style><script defer src="/_vercel/insights/script.js"></script></head><body>
<a class="skip" href="#content">Skip to content</a>
<div id="head-slot"><header id="site-header"><div class="shell">
<div class="brand-block"><a class="brand" href="/">{MARK}<span class="name"><span class="name-main">{esc(s.brand)}</span><span class="name-compact">Dog beaches</span></span></a><p class="name-sub">{HEADER_NOTE}</p></div>
<button type="button" class="search-toggle" aria-expanded="false" aria-controls="site-search"><svg class="search-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="10.5" cy="10.5" r="6.5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15.5 15.5 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg><span class="search-toggle-text">Search</span></button>
<div class="search-wrap" id="site-search"><form class="sitesearch" role="search" action="/find/" method="get"><label for="q">Search this guide</label><input id="q" name="q" type="search" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false"><button type="submit">Search</button></form><div id="search-results" class="search-results" hidden role="region" aria-live="polite" aria-label="Matching pages"></div></div>
<nav id="site-nav" class="top" aria-label="Topics"><span class="vh">On a small screen, scroll this row sideways for more topics.</span>{nav}<span class="nav-fade nav-fade-left" aria-hidden="true"></span><span class="nav-fade nav-fade-right" aria-hidden="true"></span><span class="nav-hint" aria-hidden="true"></span></nav>
</div></header></div>
<main id="content" tabindex="-1"><div class="notice" role="note"><div class="shell"><p class="unofficial">{UNOFFICIAL}</p><p>{esc(DISCLAIMER)}</p></div></div><div class="shell">{crumbs_html}{meta}<article class="content" aria-labelledby="page-title"><div class="head-block">{head}</div><div class="{layout_cls}">{toc}<div class="rest">{rest}{pn}{readnext}</div></div></article></div></main>
<footer><div class="shell"><nav class="footnav" aria-label="About this guide"><a href="/find/">All pages</a><a href="/dog-beaches/">Dog beaches</a><a href="/dog-parks/">Off-leash dog parks</a><a href="/disclaimer/">Disclaimer</a></nav><p>{esc(s.footer)}</p><p>{esc(DISCLAIMER)}</p><p><strong>Related guides:</strong> {rel}.</p><p><a href="/disclaimer/">Disclaimer</a></p><p>Last checked: {esc(show)}.</p></div></footer>
<script type="application/json" id="search-data">{s._search_json()}</script><script>{SEARCH_JS}</script><script>{FILTER_JS}</script><script>{DOCK_JS}</script><script>{MAP_JS}</script></body></html>'''
        for bad in ('\u2014','\u2013','&mdash;','&ndash;'):
            assert bad not in h,(path,bad)
        p=os.path.join(s.out,path); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w',encoding='utf-8').write(h)
        s.pages.append(path)
        if listed and kind!='error': s.indexable.append((path,iso))
    def finish(s):
        ratios=check_contrast()
        if not s._queue: raise SystemExit('No pages queued')
        for item in s._queue: s._emit(**item)
        if s.warnings:
            raise SystemExit('SEO length check failed:\n'+'\n'.join(s.warnings))
        _write_assets(s.out)
        bots=['GPTBot','OAI-SearchBot','ChatGPT-User','PerplexityBot','Bingbot','Googlebot','ClaudeBot','*']
        open(os.path.join(s.out,'robots.txt'),'w').write(''.join(f'User-agent: {b}\nAllow: /\n\n' for b in bots)+f'Sitemap: {s.base}/sitemap.xml\n')
        urls=''.join(f'<url><loc>{_abs(s.base,p)}</loc><lastmod>{mod}</lastmod></url>\n' for p,mod in sorted(s.indexable))
        open(os.path.join(s.out,'sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+urls+'</urlset>\n')
        needles=(HEADER_NOTE,UNOFFICIAL,DISCLAIMER,'Last checked:','/_vercel/insights/script.js','scroll-margin-top:var(--scroll-pad)',FONT)
        gsc=s.verification.get('google-site-verification','')
        for path in s.pages:
            html=open(os.path.join(s.out,path),encoding='utf-8').read()
            for needle in needles:
                if needle not in html: raise SystemExit(f'Missing {needle!r} on {path}')
            if gsc and gsc not in html: raise SystemExit('Missing Google verification on '+path)
            if 'rel="canonical"' not in html: raise SystemExit('Missing canonical on '+path)
            if path=='404.html':
                if 'noindex' not in html: raise SystemExit('404 should be noindex')
            elif 'noindex' in html:
                raise SystemExit('Unexpected noindex on '+path)
            if html.count('id="q"')!=1: raise SystemExit('Search field id q must appear once on '+path)
            if html.count('id="place-filter"')>1: raise SystemExit('Duplicate table filter on '+path)
            if path not in s.read_next or len(s.read_next[path])<1:
                raise SystemExit('Missing Read next on '+path)
        missing=_check_links(s.out, s.pages)
        if missing: raise SystemExit('Broken internal links:\n'+'\n'.join(missing[:40]))
        grouped=[p for _g,it in s.groups for p,_t in it]
        built=set(s.pages)
        absent=[p for p in grouped if p not in built]
        if absent: raise SystemExit('Menu pages were not built: '+', '.join(absent))
        print('header contrast white {white:.2f}, subtitle {subtitle:.2f}, gold {gold:.2f}'.format(**ratios))

def _check_links(out, pages):
    missing=[]
    cache={}
    def ids_of(target):
        if target not in cache:
            dest=os.path.join(out,target)
            if not os.path.isfile(dest):
                cache[target]=None
            elif target.endswith(('.png','.jpg','.jpeg','.webp','.gif','.ico')):
                cache[target]=set()
            else:
                cache[target]=set(re.findall(r'\bid="([^"]*)"', open(dest,encoding='utf-8').read()))
        return cache[target]
    for path in pages:
        html=open(os.path.join(out,path),encoding='utf-8').read()
        ids=ids_of(path)
        for href_v in re.findall(r'\bhref="([^"]*)"', html):
            if href_v.startswith(('http://','https://','mailto:','tel:')): continue
            url,_,frag=href_v.partition('#')
            if url in ('','/'):
                target=path if url=='' else 'index.html'
            elif url.startswith('/'):
                rel=url.lstrip('/')
                target='index.html' if rel=='' else (rel+'index.html' if rel.endswith('/') else rel)
            else:
                target=os.path.normpath(os.path.join(os.path.dirname(path), url)).replace('\\','/')
            if ids_of(target) is None:
                missing.append(f'{path} -> {href_v} (missing {target})'); continue
            if frag and frag not in ids_of(target):
                missing.append(f'{path} -> {href_v} (missing #{frag})')
    return missing

def _write_assets(out):
    open(os.path.join(out,'favicon.svg'),'w').write(FAVICON)
    _write_png(os.path.join(out,'apple-touch-icon.png'),_apple_icon())
    _write_png(os.path.join(out,'og.png'),_og_image())
    vendor=os.path.join(os.path.dirname(os.path.abspath(__file__)),'vendor','leaflet')
    needed=('leaflet.js','leaflet.css','LICENSE')
    for name in needed:
        if not os.path.isfile(os.path.join(vendor,name)):
            raise SystemExit('Missing Leaflet file '+name)
    for name in ('marker-icon.png','marker-icon-2x.png','marker-shadow.png'):
        if not os.path.isfile(os.path.join(vendor,'images',name)):
            raise SystemExit('Missing Leaflet image '+name)
    dest=os.path.join(out,'assets','leaflet')
    shutil.copytree(vendor, dest)

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
    navy,sand,white=(10,58,72),(246,227,164),(255,255,255)
    im=_Img(180,180,navy); im.rect(0,146,180,34,sand); im.paw(90,78,18,white); return im
def _og_image():
    navy,sand,foam,white=(10,58,72),(246,227,164),(214,232,240),(255,255,255)
    im=_Img(1200,630,navy); im.rect(0,500,1200,130,sand); im.rect(0,486,1200,14,foam)
    im.paw(220,250,34,white)
    im.text("SOUTH FLORIDA",430,155,9,white)
    im.text("DOG BEACHES",430,255,11,white)
    im.text("HOURS, PERMITS AND RULES",430,390,5,sand)
    return im
FAVICON='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><title>South Florida Dog Beaches</title><rect width="32" height="32" rx="6" fill="#0A3A48"/><g fill="#ffffff"><ellipse cx="10" cy="11" rx="2.2" ry="2.8"/><ellipse cx="15.2" cy="8.4" rx="2.2" ry="2.8"/><ellipse cx="20.2" cy="9" rx="2.2" ry="2.8"/><ellipse cx="23.6" cy="13.2" rx="2" ry="2.5"/><ellipse cx="16" cy="20.2" rx="6" ry="4.6"/></g></svg>'''

def _css():
    stops=", ".join(f"{c} {p}" for c,p in zip(HEAD_STOPS,("0%","50%","100%")))
    return '''/* spacing scale: 12px 16px 24px 32px 40px */
:root{--s12:12px;--s16:16px;--s24:24px;--s32:32px;--s40:40px;--header-compact:100px;--scroll-pad:116px;--header-bottom:12rem;--ink:'''+INK+''';--paper:'''+PAPER+''';--link:'''+LINK+''';--visited:'''+VISITED+''';--gold:'''+GOLD+''';--line:#D9D3C7;--head-bg:linear-gradient(90deg,'''+stops+''');--font:'''+FONT+'''}
*,*::before,*::after{box-sizing:border-box}
html{scroll-padding-top:0}
body{margin:0;color:var(--ink);background:var(--paper);font-family:var(--font);font-size:1.125rem;line-height:1.6}
h1,h2,h3,h4,h5,h6,button,input,textarea,select,summary{font-family:var(--font)}
h1,h2,h3,h4,h5,h6{font-weight:700;line-height:1.25}
h1{font-size:1.7rem;margin:0 0 var(--s16)}
h2{font-size:1.5rem;margin:var(--s40) 0 var(--s12)}
h3{font-size:1.25rem;margin:var(--s24) 0 var(--s12)}
main h1,main h2,main h3,main h4,main [id]{scroll-margin-top:var(--scroll-pad)}
[hidden]{display:none!important}
img,svg{max-width:100%}
.vh{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.shell{max-width:76rem;margin:0 auto;padding:0 var(--s16);min-width:0}
.skip{position:absolute;left:var(--s16);top:0;transform:translateY(-120%);background:#fff;color:var(--ink);padding:var(--s12) var(--s16);z-index:70;font-weight:700;border-radius:12px}
.skip:focus,.skip:focus-visible{position:fixed;top:var(--s12);transform:none}
#head-slot{min-width:0}
#site-header{background:var(--head-bg);color:#fff;position:relative;z-index:30}
#site-header a,#site-header a:visited{color:#fff}
#site-header .shell{display:grid;grid-template-columns:minmax(0,1fr) auto;grid-template-areas:"brand searchbtn" "search search" "nav nav";align-items:center;column-gap:var(--s16);row-gap:var(--s12);padding:var(--s24) var(--s16) var(--s16);position:relative}
.brand-block{grid-area:brand;min-width:0}
.brand{display:flex;align-items:center;gap:var(--s12);min-width:0;min-height:44px;color:#fff;text-decoration:none;font-weight:700}
.mark{width:28px;height:28px;flex:none;display:block;fill:#fff}
.name{display:flex;flex-direction:column;min-width:0}
.name-main{font-size:1.125rem;line-height:1.3;font-weight:700}
.name-compact{display:none;font-weight:700}
.name-sub{margin:var(--s12) 0 0;font-size:.9375rem;font-weight:600;color:'''+SUB+''';line-height:1.35}
.search-toggle{grid-area:searchbtn;display:none;align-items:center;justify-content:center;gap:var(--s12);min-height:44px;min-width:44px;height:44px;padding:0 var(--s12);font:inherit;font-weight:700;line-height:1.2;color:#fff;background:transparent;border:2px solid #fff;border-radius:12px;cursor:pointer;position:relative}
.search-icon{width:1.15rem;height:1.15rem;display:block;flex:none}
.search-wrap{grid-area:search;position:relative;min-width:0}
.sitesearch{display:flex;flex-wrap:wrap;align-items:center;gap:var(--s12)}
.sitesearch label{flex:1 1 100%;color:#fff;font-weight:700}
.sitesearch input[type="search"]{flex:1 1 12rem;min-width:0;min-height:48px;font:inherit;color:var(--ink);background:#fff;border:2px solid #fff;border-radius:12px;padding:var(--s12) var(--s16)}
.sitesearch button{min-height:48px;min-width:5.5rem;padding:var(--s12) var(--s16);font:inherit;font-weight:700;color:var(--ink);background:var(--gold);border:2px solid var(--gold);border-radius:12px;cursor:pointer}
.search-results{position:absolute;z-index:50;left:0;right:0;top:100%;margin-top:var(--s12);background:#fff;color:var(--ink);border:2px solid var(--ink);border-radius:12px;max-height:70vh;overflow:auto}
.search-results ul{list-style:none;margin:0;padding:0}
#site-header .search-results a,#site-header .search-results a:visited{display:flex;flex-direction:column;gap:var(--s12);min-height:44px;justify-content:center;padding:var(--s12) var(--s16);color:var(--link);text-decoration:underline;text-underline-offset:.12em;background:#fff}
#site-header .search-results a:visited{color:var(--visited)}
#site-header .search-results a span,.search-empty{color:var(--ink);font-weight:400}
.search-empty{margin:0;padding:var(--s12)}
#site-header .search-empty a{color:var(--link)}
nav.top{grid-area:nav;display:flex;flex-wrap:nowrap;align-items:center;gap:var(--s12);min-width:0;position:relative;margin:0;padding-top:var(--s12);border-top:1px solid rgba(255,255,255,.35);overflow-x:auto;scroll-snap-type:x proximity;scrollbar-width:thin}
.grp{position:relative;flex:0 0 auto}
.grp>summary{display:flex;align-items:center;justify-content:space-between;gap:var(--s12);min-height:44px;height:44px;padding:0 var(--s16);color:#fff;font-weight:700;cursor:pointer;list-style:none;white-space:nowrap;border:2px solid #fff;border-radius:999px;background:transparent;scroll-snap-align:start}
.grp>summary::-webkit-details-marker{display:none}
.grp>summary::marker{content:""}
.grp>summary::after{content:"";border:solid #fff;border-width:0 2px 2px 0;width:.45rem;height:.45rem;transform:rotate(45deg);flex:none;margin-top:-.15rem}
.grp[open]>summary::after{transform:rotate(-135deg);margin-top:.2rem}
.grp>summary:hover,.grp.has-current>summary{background:rgba(255,255,255,.16)}
.grp.has-current>summary{box-shadow:inset 0 -3px 0 #fff}
.glinks{display:flex;flex-direction:column;min-width:16rem}
.glinks a{display:flex;align-items:center;min-height:44px;padding:var(--s12) var(--s16);color:#fff;text-decoration:underline;text-underline-offset:.15em}
.glinks a.is-current{font-weight:700;background:rgba(255,255,255,.16);border-radius:12px}
@media (max-width:959px){
.grp[open] .glinks{position:fixed;z-index:46;top:var(--header-bottom);left:0;right:0;max-width:none;max-height:min(70vh,28rem);overflow:auto;background:#0A3A48;border:2px solid #fff;border-radius:0 0 12px 12px;padding:var(--s12);box-shadow:0 12px 24px rgba(0,0,0,.28)}
}
@media (min-width:960px){
#site-header .shell{grid-template-areas:"brand searchbtn" "search search" "nav nav"}
nav.top{overflow:visible;scroll-snap-type:none;border-top:1px solid rgba(255,255,255,.35)}
.grp>summary{border:0;border-radius:12px;padding:0 var(--s12);background:transparent}
.grp[open] .glinks{position:absolute;z-index:46;top:100%;left:0;background:#0A3A48;border:2px solid #fff;border-radius:12px;padding:var(--s12);box-shadow:0 8px 24px rgba(0,0,0,.28)}
.grp:nth-last-of-type(-n+2)[open] .glinks{left:auto;right:0}
}
@media (min-width:720px){
.sitesearch{flex-wrap:nowrap}
.sitesearch label{flex:0 0 auto}
}
.nav-fade,.nav-hint{display:none}
.nav-hint::before{content:"";display:block;width:.5rem;height:.5rem;border:solid #fff;border-width:0 3px 3px 0;transform:rotate(-45deg)}
body.nav-more-right .nav-fade-right,body.nav-more-left .nav-fade-left{display:block;position:absolute;top:0;bottom:0;width:40px;pointer-events:none;z-index:4}
body.nav-more-right .nav-fade-right{right:0;background:linear-gradient(90deg,rgba(12,74,98,0),#0C4A62 72%)}
body.nav-more-left .nav-fade-left{left:0;background:linear-gradient(90deg,#0A3A48 28%,rgba(10,58,72,0))}
body.nav-more-right .nav-hint{display:flex;align-items:center;justify-content:flex-end;position:absolute;right:var(--s12);top:0;bottom:0;width:24px;pointer-events:none;z-index:5}
body.is-docked #site-header{position:fixed;top:0;left:0;right:0;height:var(--header-compact);z-index:40;box-shadow:0 2px 12px rgba(0,0,0,.28);overflow:visible}
body.is-docked #site-header .shell{height:100%;padding:0 var(--s16);column-gap:var(--s12);row-gap:var(--s12);grid-template-columns:minmax(0,1fr) auto;grid-template-rows:44px 44px;grid-template-areas:"brand searchbtn" "nav nav"}
body.is-docked .brand{min-height:44px;height:44px}
body.is-docked .name-sub{display:none}
body.is-docked .name-main{font-size:1rem;line-height:1.2;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
body.is-docked .mark{width:22px;height:22px}
body.is-docked .search-toggle{display:inline-flex}
body.is-docked .search-wrap{display:none;position:absolute;top:100%;left:0;right:0;z-index:36;background:var(--head-bg);padding:var(--s16) 0;box-shadow:0 12px 24px rgba(0,0,0,.28)}
body.is-docked .search-wrap.is-open{display:block}
body.is-docked nav.top{border:0;padding:0;margin:0;overflow-x:auto}
@media (min-width:960px){
body.is-docked nav.top{overflow:visible}
}
@media (max-width:719px){
body.is-docked .name-main{display:none}
body.is-docked .name-compact{display:block;font-size:1rem;line-height:1.2;white-space:nowrap}
body.is-docked #site-header .shell{padding-left:var(--s12);padding-right:var(--s12)}
}
.notice{background:'''+NOTICE_BG+''';color:var(--ink);border-bottom:3px solid #8A5A00}
.notice .shell{padding-top:var(--s16);padding-bottom:var(--s16)}
.notice p,.unofficial{margin:0 0 var(--s12);max-width:66ch}
.notice p:last-child{margin-bottom:0}
.unofficial{font-weight:700}
main{min-width:0}
main>.shell{padding-top:var(--s24);padding-bottom:var(--s40)}
main:focus{outline:none}
main:focus-visible{outline:3px solid var(--ink);outline-offset:3px}
.crumbs ol{display:flex;flex-wrap:wrap;list-style:none;padding:0;margin:0 0 var(--s12);gap:0}
.crumbs li{display:flex;align-items:center;min-height:44px}
.crumbs li+li::before{content:"/";margin:0 var(--s12);color:#3E3A34}
.crumbs a{display:inline-flex;align-items:center;min-height:44px}
.meta{display:flex;flex-wrap:wrap;gap:var(--s12);align-items:center;margin:0 0 var(--s24)}
.checked,.topic-chip{display:inline-flex;align-items:center;min-height:44px;border-radius:12px;padding:var(--s12) var(--s16);font-size:1rem}
.checked{background:#E5F2EA;color:#143024;border:1px solid #1D4F3E}
.topic-chip{background:#fff;border:1px solid var(--line);font-weight:700;text-decoration:none}
article.content{min-width:0}
.head-block>p,.rest>p,.inshort p{max-width:66ch}
.head-block>p,.rest>p{margin:0 0 var(--s16)}
.inshort{background:#EEF4F1;border-left:6px solid #1D4F3E;border-radius:12px;padding:var(--s16) var(--s24);margin:0 0 var(--s24)}
.inshort p{margin:0}
.layout{display:flex;flex-direction:column;gap:var(--s24);min-width:0;margin-top:var(--s32)}
.toc{order:-1}
.rest{order:0;min-width:0}
.rest>h2:first-child,.rest>h3:first-child{margin-top:0}
@media (min-width:960px){
.layout.has-toc{display:grid;grid-template-columns:minmax(0,1fr) 18rem;column-gap:var(--s32);align-items:start}
.layout.has-toc .rest{grid-column:1;grid-row:1;order:0}
.layout.has-toc .toc{grid-column:2;grid-row:1;order:0;position:sticky;top:var(--scroll-pad);max-height:calc(100vh - var(--scroll-pad) - var(--s16));overflow:auto}
}
.toc{background:#fff;border:1px solid var(--line);border-radius:12px;padding:var(--s12) var(--s24) var(--s16);margin:0}
.toc summary{min-height:44px;display:flex;align-items:center;font-weight:700;cursor:pointer}
.toc ul{list-style:none;margin:0;padding:0 0 var(--s12)}
.toc a{display:flex;align-items:center;min-height:44px;padding:var(--s12) 0}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:var(--s24);margin:0 0 var(--s16)}
.card>:first-child{margin-top:0}
.card>:last-child{margin-bottom:0}
.card p{margin:0 0 var(--s16)}
.card ul,.card ol{margin:var(--s12) 0 0;padding-left:1.25rem}
.warn{border-left:6px solid #9B2C2C;background:#FDEEEE}
.note{border-left:6px solid #8A5A00;background:#FFF8EC}
.conf{border-left:6px solid #5C3D78;background:#F6F1FA}
.tasks,.link-grid,.readnext ul,.index-list,.period-pages{list-style:none;padding:0;margin:var(--s16) 0 0;display:grid;gap:var(--s16);grid-template-columns:1fr}
ol.steps{list-style:decimal;margin:var(--s16) 0 0;padding-left:1.5rem}
ol.steps>li{margin:0 0 var(--s16)}
ol.steps>li:last-child{margin-bottom:0}
ol.steps>li::marker{font-weight:700}
@media (min-width:720px){.tasks,.link-grid,.readnext ul,.index-list{grid-template-columns:1fr 1fr}}
.topic{margin:0 0 var(--s32)}
.topic>h3{margin-top:0}
.jump{display:flex;flex-direction:column;justify-content:center;gap:var(--s12);min-height:44px;padding:var(--s16) var(--s24);background:#fff;color:var(--ink);border:1px solid var(--line);border-radius:12px;text-decoration:none}
.jump:hover{border-color:var(--link)}
.jump .lt{color:var(--link);font-weight:700;text-decoration:underline;text-underline-offset:.12em}
.jump .ls{color:var(--ink);font-weight:400;text-decoration:none}
a.jump:visited .lt{color:var(--visited)}
.src{color:#3E3A34;font-size:1rem}
.src,.card,td,th{overflow-wrap:anywhere}
.content ul,.content ol{margin:var(--s12) 0 var(--s16);padding-left:1.25rem}
.content li+li{margin-top:var(--s12)}
.place-filter{display:flex;flex-direction:column;align-items:flex-start;gap:var(--s12);margin:0 0 var(--s16)}
.place-filter label{font-weight:700}
.place-filter input{width:100%;max-width:40rem;min-height:48px;font:inherit;color:var(--ink);background:#fff;border:2px solid var(--ink);border-radius:12px;padding:var(--s12) var(--s16)}
.filter-status{margin:0;font-weight:700}
.pn{display:grid;gap:var(--s16);margin-top:var(--s40)}
.pn a{display:flex;flex-direction:column;justify-content:center;gap:var(--s12);min-height:44px;padding:var(--s16) var(--s24);background:#fff;border:1px solid var(--line);border-radius:12px;text-decoration:none}
.pn .pn-k{color:#3E3A34;font-weight:700}
.pn .pn-t{color:var(--link);font-weight:700;text-decoration:underline;text-underline-offset:.12em}
.pn a:visited .pn-t{color:var(--visited)}
@media (min-width:720px){.pn:has(.prev):has(.next){grid-template-columns:1fr 1fr}.pn a.next{align-items:flex-end;text-align:right}}
.readnext{margin-top:var(--s40)}
.readnext h2{margin-top:0}
.index-status{font-weight:700;margin:0 0 var(--s16)}
a{color:var(--link)}
a:visited{color:var(--visited)}
.content a{text-decoration:underline;text-underline-offset:.12em}
table{border-collapse:collapse;width:100%;background:#fff;font-size:1rem}
th,td{border:1px solid var(--line);padding:var(--s12) var(--s16);text-align:left;vertical-align:top}
th{background:#E7EFE9;color:var(--ink)}
.wrap{overflow-x:auto;max-width:100%;margin:var(--s16) 0;border-radius:12px}
.map-frame{position:relative;z-index:0;isolation:isolate;margin:0 0 var(--s24)}
.map-canvas{height:22rem;background:#E7EFE9;border:1px solid var(--line);border-radius:12px;overflow:hidden}
.map-pending,.map-note{max-width:66ch}
.map-pending{margin:0;padding:var(--s16)}
.map-note{margin:0 0 var(--s12)}
footer{border-top:1px solid var(--line);color:var(--ink);margin-top:var(--s32)}
footer .shell{padding-top:var(--s32);padding-bottom:var(--s40)}
footer p{max-width:66ch}
.footnav{display:flex;flex-wrap:wrap;gap:var(--s12) var(--s24);margin:0 0 var(--s16)}
.footnav a{display:inline-flex;align-items:center;min-height:44px;font-weight:700}
.tag{display:inline-block;font-size:.875rem;font-weight:700;padding:0 var(--s12);border-radius:12px;background:#FDEBC8;color:var(--ink);border:1px solid #8A5A00;margin-right:var(--s12)}
:focus{outline:3px solid var(--ink);outline-offset:3px;box-shadow:0 0 0 3px #fff}
:focus:not(:focus-visible){outline:none;box-shadow:none}
:focus-visible{outline:3px solid var(--ink);outline-offset:3px;box-shadow:0 0 0 3px #fff}
@media (max-width:359px){body{font-size:1.0625rem}.shell{padding-left:var(--s12);padding-right:var(--s12)}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media (forced-colors:active){
.card,.inshort,.notice,.jump,.toc,.pn a,.search-toggle,.grp>summary,.sitesearch button{border:1px solid CanvasText}
.sitesearch button,.search-toggle{background:ButtonFace;color:ButtonText}
}
'''
CSS=_css()
