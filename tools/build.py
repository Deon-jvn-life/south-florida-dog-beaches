#!/usr/bin/env python3
"""Build the South Florida dog beaches and off-leash dog parks guide into site/. Run: python3 tools/build.py"""
import json,os,sys
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE); sys.path.insert(0,HERE)
from sitelib import Site,CSS,D,DISCLAIMER,esc,a,clean_url
BASE="https://south-florida-dog-beaches.vercel.app"
# Optional search-engine verification. Leave a value empty to omit that meta tag.
VERIFY={"google-site-verification":"","msvalidate.01":""}
P=json.load(open(os.path.join(HERE,'places.json')))
BCL="https://www.broward.org/parks/thingstodo/dogparks"
CITYPARKS=[("Dog Park at Emerald Hills Park (City of Hollywood)","3901 N. 30th Terrace, Hollywood 33021","954-921-3404"),("Dog Park at John Williams Park (City of Hollywood)","6101 Sheridan St., Hollywood 33021","954-921-3404"),("Dog Park at Oakridge Park (City of Hollywood)","5200 S.W. 35th Ave., Hollywood 33021","954-921-3404"),("Dog Park at Poinciana Park (City of Hollywood)","1301 S. 21st Ave., Hollywood 33020","954-921-3404"),("Dr. Steven G. Paul Dog Park (City of Coral Springs)","2575 Sportsplex Dr., Coral Springs 33067","954-346-4428"),("Gary B. Jones Park for People and Pups (City of Tamarac)","8101 Southgate Blvd., Tamarac 33321","954-597-3620"),("Happy Tails Dog Park (City of Plantation)","6500 S.W. 16th St., Plantation 33317","954-452-2510"),("Joseph Scavo Park (City of Hallandale Beach)","900 Three Islands Blvd., Hallandale Beach 33009","954-457-1452"),("Oakland Bark Park (City of Oakland Park)","971 N.W. 38th St., Oakland Park 33309","954-630-4352"),("Precious Paws Dog Park at Patrick J. Meli Park (City of Dania Beach)","2901 S.W. 52nd St., Dania Beach 33312","954-985-4400"),("Windmill Park (City of Coconut Creek)","700 Lyons Rd., Coconut Creek 33063","954-545-6670"),("Woodville Dog Park (City of North Lauderdale)","1500 S.W. 83rd Ave., North Lauderdale 33068","954-724-7061")]
CO={'miami-dade':'Miami-Dade','broward':'Broward','palm-beach':'Palm Beach'}
NAV=[('index.html','Home'),('dog-beaches/index.html','Dog beaches'),('dog-parks/index.html','Off-leash dog parks')]+[(f'counties/{k}/index.html',v) for k,v in CO.items()]+[('are-dogs-allowed-on-beaches/index.html','Are dogs allowed on beaches?')]
FOOT='Unofficial, independent guide. Not affiliated with any city, county or park agency. Hours, fees and rules are copied from the official city and county pages linked on each entry; they change, especially seasonally, so check the official page or call before you go.'
s=Site(ROOT,BASE,"South Florida Dog Beaches",NAV,FOOT,CSS,VERIFY)
def srcs(p): return ' <span class="src">['+', '.join(a(u,'official page' if i==0 else f'source {i+1}') for i,u in enumerate(p['src']))+']</span>'
def row(p):
    f=f'<br><span class="tag mix">Check</span> <span class="src">{esc(p["flag"])}</span>' if p['flag'] else ''
    return f'<tr><td><strong><a href="/places/{p["id"]}/">{esc(p["name"])}</a></strong><br><span class="src">{p["county"]}</span></td><td>{esc(p["address"])}</td><td>{esc(p["hours"])}</td><td>{esc(p["fee"])}</td><td>{srcs(p)}{f}</td></tr>'
def table(ps):
    return '<input id="q" placeholder="Filter by city or name" oninput="var v=this.value.toLowerCase();document.querySelectorAll(\'table tr\').forEach(function(x){if(x.querySelector(\'td\'))x.style.display=x.textContent.toLowerCase().indexOf(v)>-1?\'\':\'none\'})"><div class="wrap"><table><tr><th>Place</th><th>Location</th><th>Days and hours</th><th>Permit, fee, parking</th><th>Source and notes</th></tr>'+''.join(row(p) for p in ps)+'</table></div>'
B=[p for p in P if p['kind']=='beach']; K=[p for p in P if p['kind']=='park']; FL=[p for p in P if p['flag']]
CONF='<div class="card conf"><strong>Conflicts and gaps found on '+D+'</strong><ul>'+''.join(f'<li><strong>{esc(p["name"])}:</strong> {esc(p["flag"])}</li>' for p in FL)+'</ul></div>'
b=f'''<h1>South Florida dog beaches and off-leash dog parks</h1><p>{len(B)} dog beaches and {len(K)} off-leash dog parks in Miami-Dade, Broward and Palm Beach counties, each with days, hours (including seasonal hours), permits or fees, and rules from the official city or county page.</p>
<div class="card note"><strong>Most South Florida beaches do not allow dogs.</strong> Use only the designated dog beaches below. {a("/are-dogs-allowed-on-beaches/","Read the rules")}.</div>
<h2>Dog beaches</h2>{table(B)}
<h2>Seasonal and day-limited at a glance</h2><ul><li>Miami Beach Bark Beach: Friday to Sunday only; 3 p.m. to 7 p.m. March to October, 1:30 p.m. to 5:30 p.m. November to February.</li><li>Boca Raton Bark Beach: 3 p.m. to sunset in standard time, 5 p.m. to sunset in daylight saving time; permit required.</li><li>Broward County Barkham and Woofing Waters: closed third week of January through second week of April.</li></ul>
<h2>Off-leash dog parks</h2><p>See {a("/dog-parks/","all off-leash dog parks")} or browse by county: {", ".join(a(f"/counties/{k}/",v) for k,v in CO.items())}.</p>{CONF}'''
s.page('index.html',"South Florida dog beaches and parks: hours and rules","Dog beaches and off-leash dog parks in Miami-Dade, Broward and Palm Beach with seasonal hours, days, permits, fees and rules from official pages.",b)
s.page('dog-beaches/index.html',"South Florida dog beaches: days, hours and permits","7 designated dog beaches in Miami-Dade, Broward and Palm Beach, with days, seasonal hours, permits, fees and rules from official pages.",f'<h1>Dog beaches in South Florida</h1><p>{len(B)} designated dog beaches.</p>'+table(B)+CONF)
s.page('dog-parks/index.html',"Off-leash dog parks in South Florida: hours and fees","Off-leash dog parks run by Miami-Dade, Broward, Palm Beach counties and cities, with hours, maintenance closures, fees and rules.",f'<h1>Off-leash dog parks in South Florida</h1><p>{len(K)} off-leash parks with details below, plus other city dog parks listed by Broward County.</p>'+table(K)+'<h2>Other city dog parks listed by Broward County</h2><p>Broward County says usage fees may apply and to contact the park before arriving'+f' <span class="src">[{a(BCL)}]</span>.</p><div class="wrap"><table><tr><th>Park</th><th>Address</th><th>Phone</th></tr>'+''.join(f'<tr><td>{esc(n)}</td><td>{esc(x)}</td><td>{p}</td></tr>' for n,x,p in CITYPARKS)+'</table></div>')
COUNTY_TITLE={
 'miami-dade':"Dog beaches and off-leash parks in Miami-Dade County",
 'broward':"Broward County dog beaches and off-leash dog parks",
 'palm-beach':"Dog beaches and off-leash parks in Palm Beach County",
}
COUNTY_DESC={
 'miami-dade':"Miami-Dade beaches and parks: North Beach Bark Beach, Haulover Dog Beach, Haulover Bark Park, West Kendall, Amelia Earhart, Greynolds, Tropical and Lago Mar.",
 'broward':"Broward beaches and parks: Hollywood Dog Beach, Canine Beach, Wags and Waves, Barkham, Woofing Waters, Holiday Park, Riverside, Snyder and Canine Corner.",
 'palm-beach':"Palm Beach County dog beaches and parks, including Jupiter Dog Beach, Boca Raton Bark Beach, Canine Cove, Lake Ida, Lake Woof and Pooch Pines, with hours.",
}
for k,v in CO.items():
    ps=[p for p in P if p['county']==v]
    s.page(f'counties/{k}/index.html',COUNTY_TITLE[k],COUNTY_DESC[k],f'<h1>Dog beaches and dog parks in {v} County</h1><h2>Dog beaches</h2>'+table([p for p in ps if p['kind']=='beach'])+'<h2>Off-leash dog parks</h2>'+table([p for p in ps if p['kind']=='park']))
PLACE_TITLE={
 'haulover-dog-beach':"Haulover Park Dog Beach (Miami-Dade County): hours and rules",
 'pompano-wags-and-waves':"Wags and Waves Dog Beach, Pompano: hours and rules",
 'boca-bark-beach':"Bark Beach at Spanish River Park: hours and permit",
 'jupiter-dog-beach':"Jupiter Dog Beach: sunrise to sunset, free parking",
 'haulover-bark-park':"Haulover Park Bark Park: sunrise to sunset, fee, rules",
 'md-tropical':"Tropical Park dog park in Miami-Dade: hours and rules",
 'md-lago-mar':"Lago Mar Park dog run in Miami-Dade: hours and rules",
 'barkham-markham':"Barkham at Markham Park (Sunrise): hours and rules",
 'woofing-waters':"Woofing Waters at Quiet Waters Park: hours and rules",
 'ftl-holiday-park':"Holiday Park Dog Park (Fort Lauderdale): hours and rules",
 'ftl-riverside':"Riverside Dog Park, Fort Lauderdale: hours and rules",
 'ftl-snyder':"Bark Park at Snyder Park, Fort Lauderdale: hours and rules",
 'pbc-canine-cove':"Canine Cove dog park: hours, rules and small dog area",
}
PLACE_DESC={
 'miami-beach-bark-beach':"North Beach Bark Beach, Miami Beach: Friday to Sunday, 3 p.m. to 7 p.m. March to October and 1:30 p.m. to 5:30 p.m. November to February. No permit stated.",
 'haulover-dog-beach':"Haulover Park Dog Beach: daily sunrise to sunset between lifeguard towers 2 and 3. Parking is $7 Monday to Thursday and $10 on weekends and holidays.",
 'hollywood-dog-beach':"Dog Beach at Hollywood Beach: sunrise to sunset, no passes required, between Pershing and Custer Street lifeguard stands. Dogs need a current rabies tag.",
 'fort-lauderdale-canine-beach':"Canine Beach in Fort Lauderdale: 6 a.m. to 9 a.m. and 5 p.m. to 7 p.m. North of Sunrise Boulevard on A1A. No permit stated on the official page.",
 'pompano-wags-and-waves':"Wags and Waves Dog Beach at the SE 2nd Street Beach Access in Pompano Beach. Hours and fees were not stated on the official pages we could read.",
 'boca-bark-beach':"Bark Beach at Spanish River Park: 7 days a week. 3 p.m. to sunset in Eastern Standard Time, 5 p.m. to sunset in Daylight Saving Time. Permit required.",
 'jupiter-dog-beach':"Jupiter Dog Beach, Palm Beach County: sunrise to sunset, no permit stated, and parking is free. Leash dogs from the car to the beach.",
 'haulover-bark-park':"Haulover Park Bark Park: sunrise to sunset, seven days a week. Parking is $5.47 per vehicle with the dog in the car. Separate small and large dog areas.",
 'md-west-kendall':"West Kendall District Park dog park, 11255 SW 157 Ave, Miami. Hours and fees are not stated on the county dog parks page. County dog park rules apply.",
 'md-amelia-earhart':"Amelia Earhart Park dog park at 401 E 65 St., Hialeah. Hours and fees are not stated on the county dog parks page. County dog park rules apply.",
 'md-east-greynolds':"East Greynolds Park dog park, 16700 Biscayne Blvd., North Miami Beach. Hours and fees are not stated on the county dog parks page. County dog park rules apply.",
 'md-tropical':"Tropical Park dog park at 7900 SW 40 St., Miami. Hours and fees are not stated on the county dog parks page. County dog park rules apply.",
 'md-lago-mar':"Lago Mar Park dog run, 8165 SW 162 Ave., Miami. Hours and fees are not stated. No water, bag dispensers or waste baskets; bring your own.",
 'barkham-markham':"Barkham at Markham Park, Sunrise: closed Tuesday mornings until 10 a.m. Annual membership $25 or $5 daily, up to three dogs. Small and large dog areas.",
 'woofing-waters':"Woofing Waters at Quiet Waters Park: 8 a.m. to 6 p.m. daily. Annual fee $25 or $5 daily. Closed third week of January through second week of April.",
 'ftl-holiday-park':"Holiday Park Dog Park in Fort Lauderdale: 7:30 a.m. to 7 p.m., closed Monday and Wednesday 8 a.m. to 11 a.m. for maintenance. Up to three dogs per person.",
 'ftl-riverside':"Riverside Neighborhood Dog Park in Fort Lauderdale: 6 a.m. to 9 p.m. Fee not stated. Rules include a license, three dogs max and no puppies under four months.",
 'ftl-snyder':"Bark Park at Snyder Park, 3299 S.W. Fourth Ave., Fort Lauderdale. Hours not stated on the pages we could read. Broward County says usage fees may apply.",
 'pompano-canine-corner':"Canine Corner Dog Park in Pompano Beach: daily 6:30 a.m. to 8:30 p.m., closed Tuesdays. Members only. Separate areas under and over 25 pounds.",
 'pbc-canine-cove':"Canine Cove at Burt Aaronson South County Regional Park: sunrise to sunset, closed Wednesday 12 p.m. to 3 p.m. for maintenance. No fee stated.",
 'pbc-lake-ida':"Dog Park at Lake Ida West Park, 1455 Lake Ida Road, Delray Beach: sunrise to sunset, closed Thursday 12 p.m. to 3 p.m. No fee stated on the county page.",
 'pbc-lake-woof':"Lake Woof at John Prince Memorial Park, 2520 Lake Worth Road: sunrise to sunset, closed Thursday 12 p.m. to 3 p.m. No entry fee stated.",
 'pbc-pooch-pines':"Pooch Pines at Okeeheelee Park, 7715 Forest Hill Boulevard: sunrise to sunset, closed Wednesday 12 p.m. to 3 p.m. No fee stated on the county page.",
}
for p in P:
    rl=''.join(f'<li>{esc(x)}</li>' for x in p['rules']) or '<li>Not stated on the official page we could read.</li>'
    f=f'<div class="card conf">{esc(p["flag"])}</div>' if p['flag'] else ''
    ph=f'<p><strong>Phone:</strong> {esc(p["phone"])}</p>' if p['phone'] else ''
    b=f'''<h1>{esc(p["name"])}</h1><div class="card"><p><strong>Type:</strong> {"Dog beach" if p["kind"]=="beach" else "Off-leash dog park"}, {p["county"]} County</p><p><strong>Location:</strong> {esc(p["address"])}</p><p><strong>Days and hours:</strong> {esc(p["hours"])}</p><p><strong>Permit, fee, parking:</strong> {esc(p["fee"])}</p>{ph}<p>{srcs(p)}</p></div>{f}<h2>Rules</h2><ul>{rl}</ul><p>{a("/","All dog beaches and parks")}</p>'''
    title=PLACE_TITLE.get(p['id'], f"{p['name']}: hours, rules, permit")
    desc=PLACE_DESC[p['id']]
    hub=('dog-beaches/index.html','Dog beaches') if p['kind']=='beach' else ('dog-parks/index.html','Off-leash dog parks')
    s.page(f'places/{p["id"]}/index.html',title,desc,b,crumbs=[('index.html','Home'),hub,(f'places/{p["id"]}/index.html',p['name'])])
FAQ_Q="Are dogs allowed on most South Florida beaches?"
FAQ_A="No. On most public beaches in Miami-Dade, Broward and Palm Beach, dogs (other than service animals) are not allowed. Use a designated dog beach."
b=f'''<h1>{esc(FAQ_Q)}</h1><div class="card"><p><strong>No.</strong> {esc(FAQ_A[4:])}</p></div>
<ul><li>Miami Beach: dogs are prohibited from city beaches except the designated Bark Beach at 80 to 81 Streets <span class="src">[{a(P[0]["src"][0])}]</span>.</li>
<li>Palm Beach County: dogs are not allowed on county beaches, with the exception of ADA service animals; Jupiter Dog Beach is the county's off-leash beach stretch <span class="src">[{a("https://discover.pbc.gov/parks/General/Dogs.aspx")}, {a("https://discover.pbc.gov/parks/Pages/Jupiter-Dog-Beach.aspx","source 2")}]</span>.</li>
<li>Fort Lauderdale: pets are not allowed on beaches or in any body of water unless permitted by law, except at Canine Beach <span class="src">[{a("https://www.parks.fortlauderdale.gov/parks/dog-friendly-places")}]</span>.</li>
<li>Jupiter calls its beach "one of the few remaining dog-friendly beaches in the state of Florida" <span class="src">[{a("https://jupiter.fl.us/437/Dogs-on-the-Beach")}]</span>.</li></ul>
<p>Where dogs are allowed, rules usually include a leash to and from the sand, a current rabies tag or vaccination proof, a limit of two or three dogs per person, and picking up waste. See the {a("/dog-beaches/","dog beach list")}.</p>'''
s.page('are-dogs-allowed-on-beaches/index.html',"Are dogs allowed on South Florida beaches? The rules","Short answer with official sources: dogs are not allowed on most Miami-Dade, Broward and Palm Beach beaches; here is where they are.",b,faq=[(FAQ_Q,FAQ_A)])
b=f'''<h1>Disclaimer</h1>
<p>{esc(DISCLAIMER)}</p>
<h2>Accuracy</h2>
<p>Hours, fees, permits and rules on this site are copied from the official city and county pages linked on each entry. They were last checked on {D}. Listings can be incomplete or wrong, and rules, hours and access can change.</p>
<h2>No warranty</h2>
<p>This site is for general information only. It is provided without any warranty, express or implied, including any warranty of accuracy, completeness, or fitness for a particular purpose.</p>
<h2>Limitation of liability</h2>
<p>You are responsible for your dog and for following local rules. We accept no liability for decisions made using this site, including injury, fines, denied entry, or any other loss.</p>
<h2>External links are not endorsements</h2>
<p>Links to city, county, and other websites are there so you can read the source. We do not control those sites, and a link is not an endorsement of the site or of what it says.</p>
<h2>Not affiliated</h2>
<p>This independent site is not affiliated with any city, county or park authority. It is not a government website.</p>
<h2>Check official sources</h2>
<p>Always check the official park page and the signs posted at the park before you go.</p>
<h2>Contact and corrections</h2>
<p>This site does not publish an email address or a contact form. If an entry looks wrong, compare it with the official page linked on that entry and with the signs posted at the park.</p>'''
s.page('disclaimer/index.html',"Disclaimer: South Florida dog beaches and parks guide","General information only. No warranty and no liability. This independent site is not a city, county or park authority. Check the official park page.",b)
hubs=''.join(f'<li><a href="{esc(clean_url(p))}">{esc(t)}</a></li>' for p,t in NAV+[('disclaimer/index.html','Disclaimer')])
s.page('404.html',"Page not found on the South Florida dog beach guide","That page is not in this South Florida dog beach and off-leash dog park guide. Try the home page, dog beaches, dog parks or a county page.",f'<h1>Page not found</h1><p>That page is not on this guide.</p><ul>{hubs}</ul>',listed=False)
s.finish(); print(len(s.pages),'pages',len(B),'beaches',len(K),'parks',len(CITYPARKS),'listed city parks')
