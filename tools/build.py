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
NAV=[('index.html','Home'),('dog-beaches/index.html','Dog beaches'),('dog-parks/index.html','Off-leash dog parks')]+[(f'counties/{k}/index.html',v) for k,v in CO.items()]+[('are-dogs-allowed-on-beaches/index.html','Are dogs allowed on beaches?'),('license-and-rabies/index.html','License and rabies')]
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
<div class="card"><strong>License and rabies tags.</strong> Florida requires a rabies vaccination, and each county requires its own dog tag. Fees, where to buy the tag, and which of these places ask for proof are on the {a("/license-and-rabies/","license and rabies page")}.</div>
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
    s.page(f'counties/{k}/index.html',COUNTY_TITLE[k],COUNTY_DESC[k],f'<h1>Dog beaches and dog parks in {v} County</h1><p>County dog license, rabies vaccination, and which of these places ask for a tag: {a("/license-and-rabies/","license and rabies rules")}.</p><h2>Dog beaches</h2>'+table([p for p in ps if p['kind']=='beach'])+'<h2>Off-leash dog parks</h2>'+table([p for p in ps if p['kind']=='park']))
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
    b=f'''<h1>{esc(p["name"])}</h1><div class="card"><p><strong>Type:</strong> {"Dog beach" if p["kind"]=="beach" else "Off-leash dog park"}, {p["county"]} County</p><p><strong>Location:</strong> {esc(p["address"])}</p><p><strong>Days and hours:</strong> {esc(p["hours"])}</p><p><strong>Permit, fee, parking:</strong> {esc(p["fee"])}</p>{ph}<p>{srcs(p)}</p></div>{f}<h2>Rules</h2><ul>{rl}</ul><p>{a("/","All dog beaches and parks")}. {a("/license-and-rabies/","License and rabies tag rules")}.</p>'''
    title=PLACE_TITLE.get(p['id'], f"{p['name']}: hours, rules, permit")
    desc=PLACE_DESC[p['id']]
    hub=('dog-beaches/index.html','Dog beaches') if p['kind']=='beach' else ('dog-parks/index.html','Off-leash dog parks')
    s.page(f'places/{p["id"]}/index.html',title,desc,b,crumbs=[('index.html','Home'),hub,(f'places/{p["id"]}/index.html',p['name'])])
def pl(i,n): return a(f'/places/{i}/',n)
S828=a("https://www.flsenate.gov/Laws/Statutes/2026/828.30","Florida Statutes section 828.30")
MD_LIC=a("https://www.miamidade.gov/global/license.page?Mduid_license=lic1501167447237960","Miami-Dade dog license")
MD_TAGS=a("https://www.miamidade.gov/global/service.page?Mduid_service=ser1599260560190697","Miami-Dade animal licenses and tags")
MD_VAX=a("https://www.miamidade.gov/global/service.page?Mduid_service=ser1599264624594140","Miami-Dade pet vaccinations")
MD_PARKS=a("https://www.miamidade.gov/global/service.page?Mduid_service=ser1470943010772421","Miami-Dade dog parks")
MD_BEACH=a("https://www.miamidade.gov/resources/parks/documents/haulover-park-dog-beach-rules.pdf","Haulover Dog Beach rules")
MB=a("https://www.miamibeachfl.gov/city-hall/parks-and-recreation/parks-facilities-directory/north-beach-bark-beach/","Miami Beach Bark Beach")
BW=a("https://www.broward.org/animal/tagsandshots","Broward tags and shots")
BW_HOME=a("https://www.broward.org/animal","Broward Animal Care")
BW_CLINIC=a("https://www.broward.org/animal/tagsandshots/petrabiesclinics","Broward pet rabies clinic")
BW_PARKS=a("https://www.broward.org/parks/thingstodo/dogparks","Broward dog parks")
HW=a("https://hollywoodfl.org/facilities/facility/details/Dog-Beach-Hollywood-Beach-98","Hollywood Dog Beach")
FTL=a("https://www.parks.fortlauderdale.gov/parks/dog-friendly-places","Fort Lauderdale dog-friendly places")
POMP=a("https://parks.pompanobeachfl.gov/parks-beach-and-pier/canine-corner-dog-park","Canine Corner")
POMP_B=a("https://parks.pompanobeachfl.gov/dog-park-and-beach","Pompano dog park and beach")
PBC=a("https://discover.pbc.gov/publicsafety/animalcare/pages/my_pets.aspx","Palm Beach County rabies page")
PBC_HOME=a("https://discover.pbc.gov/publicsafety/animalcare/Pages/default.aspx","Palm Beach County Animal Care")
PBC_CODE=a("https://library.municode.com/fl/palm_beach_county/codes/code_of_ordinances?nodeId=PABECOCO_CH4AN","Palm Beach County Code chapter 4")
PBC_ORD=a("https://discover.pbc.gov/publicsafety/animalcare/Pages/Ordinance.aspx","county ordinance index")
PBC_PARKS=a("https://discover.pbc.gov/parks/Pages/Dog-Park-Information.aspx","Palm Beach County dog park rules")
JUP=a("https://jupiter.fl.us/2032/Beach-FAQ","Jupiter beach questions")
JUP2=a("https://jupiter.fl.us/437/Dogs-on-the-Beach","Jupiter dogs on the beach")
JUP3=a("https://discover.pbc.gov/parks/Pages/Jupiter-Dog-Beach.aspx","county Jupiter Dog Beach page")
BOCA=a("https://www.myboca.us/953/Bark-Beach-at-Spanish-River-Park","Boca Raton Bark Beach")
BOCA2=a("https://www.myboca.us/950/Annual-Permits","Boca Raton annual permits")
LIC_TITLE="Dog license and rabies tag rules by South Florida county"
LIC_DESC="Miami-Dade, Broward and Palm Beach dog license fees, rabies proof, where to get a tag, and which listed parks and beaches require it."
lic=f'''<h1>Dog license and rabies tag rules for South Florida</h1>
<p>Florida law requires a rabies vaccination for dogs. Miami-Dade, Broward and Palm Beach each add their own license or registration tag. A park can also set its own proof rule. This page separates those three layers. Fees below are the county prices published for a county tag or a county clinic, not a private veterinarian's price.</p>
<div class="card conf"><strong>Official pages that do not agree</strong>
<ul>
<li><strong>Miami-Dade, who can buy a tag.</strong> The license pages say you must be a Miami-Dade County resident. The vaccination requirements on the county pet vaccinations page say the dog must be registered in Miami-Dade, though the owner does not have to be a Miami-Dade resident. <span class="src">[{MD_LIC}, {MD_TAGS}, {MD_VAX}]</span></li>
<li><strong>Miami-Dade, one-year or three-year tag.</strong> The dog license page says the tag must be renewed every year by the anniversary of the latest rabies vaccine, whether that vaccine lasts one year or three. The same page also says a three-year tag can be purchased when a three-year vaccine is given, that the tag expires with that vaccine, and that a three-year tag is renewed every three years. If you bought only a one-year tag, that page says you still renew every year. The animal licenses page says renewal is every year whether the vaccine lasts one year or three, and also says a three-year tag must be purchased when the three-year vaccine is given. <span class="src">[{MD_LIC}, {MD_TAGS}]</span></li>
<li><strong>Miami-Dade, age wording.</strong> The license pages say a license is required for dogs over four months of age. The pet vaccinations page says dogs and cats must be four months old, that puppies need rabies vaccine when they turn 4 months old, and, in another answer on that page, that rabies vaccination is required for dogs, cats and ferrets over four months of age. <span class="src">[{MD_LIC}, {MD_TAGS}, {MD_VAX}]</span></li>
<li><strong>Broward, three-year registration.</strong> The fee list, marked updated June 30, 2026, includes a three-year tag: $65 if the pet is microchipped, or $145 if not, with a valid three-year rabies vaccine. Later on the same page, Broward says it does not offer a three-year registration renewal, and that a pet with a three-year vaccine still renews registration every year on the vaccination date. <span class="src">[{BW}]</span></li>
<li><strong>Broward, rabies shot price.</strong> The clinic page lists the rabies vaccine as free at monthly wellness clinics, and the note under that list says the fees for the rabies vaccine and the registration tag are $25 for a microchipped pet or $55 if the pet is not microchipped. The Animal Care home page says the Pet Care Clinic is closed and is not taking appointments. <span class="src">[{BW_CLINIC}, {BW_HOME}]</span></li>
<li><strong>Palm Beach County, license age.</strong> The Animal Care rabies page says county ordinance requires every dog and cat 4 months and older to be current on rabies vaccine and the county license tag. County Code section 4-11 says the owner of a dog six months or older, or a cat four months or older, must get the rabies and license tag. Section 4-10 requires rabies vaccination in accordance with Florida Statutes section 828.30, which is 4 months of age or older. The county ordinance index lists the section titles and does not print the section text. <span class="src">[{PBC}, {PBC_CODE}, {S828}, {PBC_ORD}]</span></li>
<li><strong>Palm Beach County, clinic hours.</strong> The Animal Care home page says a $15 rabies vaccine is offered with no appointment, on the hour and the half hour: Sunday 2:00 to 3:00 p.m., Monday 3:00 to 4:00 p.m., Tuesday through Friday 11:00 a.m. to 4:00 p.m., and Saturday 11:00 a.m. to 4:00 p.m. The rabies page says every Saturday and Sunday from 2 to 4 p.m., and that hours are subject to change or cancellation. <span class="src">[{PBC_HOME}, {PBC}]</span></li>
</ul></div>
<h2>Statewide rabies rule</h2>
<p>Florida Statutes section 828.30 says every dog, cat and ferret 4 months of age or older must be vaccinated against rabies with a United States Department of Agriculture licensed vaccine. The vaccination must be given by a licensed veterinarian. For an animal already in the custody of animal control or a sheriff, an employee, agent, or contractor may vaccinate under a veterinarian's indirect supervision. The owner pays. The first booster is due 12 months after the first shot. After that, the interval follows the vaccine maker's directions. A blood test for rabies antibodies does not replace a current vaccination. The veterinarian must give the owner and the animal-control authority a rabies vaccination certificate. A veterinarian can exempt an animal in writing if vaccination would endanger its health because of age, infirmity, disability, illness, or other medical reasons, and the animal must be vaccinated when its health allows. A violation is a civil infraction. The statute does not set a county license fee, and it allows counties and cities to be stricter. It also says a local government cannot order another vaccination of an animal that is already currently vaccinated, except for rabies exposure treatment. <span class="src">[{S828}]</span></p>
<h2>Miami-Dade County</h2>
<p>The county dog license page says a dog license is required for every dog in Miami-Dade County over four months of age. The animal licenses page says the dog must be registered and must wear the tag at all times. You need proof of a current rabies vaccination. The county says you cannot buy or renew the tag without that proof. The person registering the dog must be 18. The license pages also say the person must be a Miami-Dade resident, with a driver's license or passport, and the licenses page adds proof of a Miami-Dade address. See the conflict above about whether a non-resident's dog can be registered. <span class="src">[{MD_LIC}, {MD_TAGS}, {MD_VAX}]</span></p>
<p>A cat license is available and is not required. Cats still have to be vaccinated against rabies. <span class="src">[{MD_TAGS}]</span></p>
<h3>Tag cost</h3>
<ul>
<li>One-year, spayed or neutered: $30. Proof of spay or neuter is required.</li>
<li>One-year, not spayed or neutered: $60.</li>
<li>One-year, dog under 12 months: $30, listed under both altered and unaltered dogs.</li>
<li>Three-year, spayed or neutered: $90. Three-year, not spayed or neutered: $180. The three-year tag is tied to a three-year vaccine. See the renewal conflict above.</li>
<li>One-year low-income: $5 if spayed or neutered, $15 if not. The county asks for a current eligibility letter for food stamps, Medicaid, Supplemental Security Income, a Jackson Memorial Hospital clinic card, or Temporary Assistance for Needed Families (the county's spelling).</li>
<li>Replacement tag: $5. The new tag keeps the old expiration date.</li>
<li>Service-animal tag: free at the Pet Adoption and Protection Center. The county says the dog must be trained to do work or a task directly related to a person's disability, that a verbal statement of that task is enough, and that emotional support, therapy, comfort, and companion animals do not qualify. Residency and rabies proof still apply.</li>
<li>Police-dog tag: free. The handler still meets the vaccination and licensing rules, and the rabies certificate must show the police station or city government address.</li>
</ul>
<p>The pet vaccinations page says there is a 30-day grace period from the license and rabies expiration date instead of a late fee. After that, the county says it issues a civil violation notice. A veterinarian can exempt a dog from the rabies vaccine for up to one year for health reasons. The license tag is still required. The written exemption goes to Animal Services within 30 days of the vaccine expiration, by email to petacctupdates@miamidade.gov, by mail, in person at the Pet Adoption and Protection Center, or at a 311 service center. The same answer says dogs that stay in Miami-Dade for less than 30 days are exempt from that vaccination requirement. <span class="src">[{MD_VAX}]</span></p>
<h3>Where to get the tag and the shot</h3>
<p>The county says you can buy or renew a dog tag at the Pet Adoption and Protection Center, a local veterinarian, a 311 service center, or by mail. The licenses page also says tags can be purchased and renewed online, and it names the Humane Society of Greater Miami and the American Society for the Prevention of Cruelty to Animals Liberty City location. Mail payment is by check or money order only, with a copy of the rabies certificate, payable to Miami-Dade Animal Services Tag Unit, 3599 Northwest 79 Avenue, Doral, Florida 33122. The 311 service centers take a personal check, cashier's check, or money order. <span class="src">[{MD_LIC}, {MD_TAGS}]</span></p>
<p>Tag counter at the Pet Adoption and Protection Center, 3599 Northwest 79 Avenue, Doral: Monday through Friday 10:00 a.m. to 6:30 p.m., Saturday and Sunday 8:30 a.m. to 5:00 p.m. Closed county holidays. Other counters listed on the license page: South Dade Justice Center, 10710 Southwest 211 Street, Cutler Bay, Monday through Friday 9:00 a.m. to 4:00 p.m., closed one hour for lunch; Herbert S. Saffir Permitting and Inspection Center, 11805 Southwest 26 Street, Miami, second-floor kiosk, same weekday hours; North Dade Regional Library, 2455 Northwest 183rd Street, Miami Gardens, Monday through Friday 9:30 a.m. to 5:30 p.m., closed noon to 1:00 p.m. <span class="src">[{MD_LIC}]</span></p>
<p>County rabies shots are walk-in, with no appointment, at the Wellness Clinic in the same Doral building. Dogs and cats must be four months old. Clinic hours on the vaccinations page: Monday through Friday 9:00 a.m. to 6:00 p.m., Saturday and Sunday 9:00 a.m. to 4:00 p.m. Closed county holidays. An individual rabies vaccine is $25. The low-income rabies vaccine is $10 with the eligibility letter described above. Those are county clinic prices. The county also lists a mobile clinic whose location changes by month, Monday through Wednesday, 8:30 a.m. to noon and 1:00 p.m. to 4:30 p.m. <span class="src">[{MD_VAX}]</span></p>
<h3>Listed Miami-Dade places</h3>
<p>"Rabies tag" on the dog parks page is the county's phrase. That page does not say whether the metal tag from a veterinarian is enough, or whether the county license tag is the tag it means. The license page is titled "Dog License (Tag)."</p>
<div class="wrap"><table>
<tr><th>Place</th><th>What that place's page requires</th></tr>
<tr><td>{pl("miami-beach-bark-beach","North Beach Bark Beach")}</td><td>The city page does not mention a rabies tag, a license, or vaccination proof. <span class="src">[{MB}]</span></td></tr>
<tr><td>{pl("haulover-dog-beach","Haulover Park Dog Beach")}</td><td>The county rules sheet does not mention a tag or vaccination proof. It does say puppies under 6 months are not allowed. <span class="src">[{MD_BEACH}]</span></td></tr>
<tr><td>{pl("haulover-bark-park","Haulover Bark Park")}, {pl("md-west-kendall","West Kendall")}, {pl("md-amelia-earhart","Amelia Earhart")}, {pl("md-east-greynolds","East Greynolds")}, {pl("md-tropical","Tropical Park")}</td><td>The county dog park rules say vaccinations must be up to date and a current rabies tag must be displayed. <span class="src">[{MD_PARKS}]</span></td></tr>
<tr><td>{pl("md-lago-mar","Lago Mar dog run")}</td><td>Listed on the same dog parks page as a dog run. That page's dog park rules include the rabies tag line. There is no separate Lago Mar rule sheet on the page. <span class="src">[{MD_PARKS}]</span></td></tr>
</table></div>
<h2>Broward County</h2>
<p>Broward County says every dog, cat and ferret must receive a rabies vaccination, and that every dog and cat must have and wear a Broward County pet rabies registration tag. Dogs and cats four months or older must be registered. Indoor pets are not exempt. A tattoo, microchip, or name tag does not replace the county tag. The tag is a lifetime tag that you buy once. Registration still has to be renewed. A current rabies certificate from a licensed veterinarian is required at the first purchase and at renewal. If a veterinarian waives the vaccine for health reasons, the tag is still required. The tags page does not describe a short-visit exception. <span class="src">[{BW}]</span></p>
<p>Registration is valid for one year from the date of the rabies vaccination, not from the day you buy the tag. The page says to renew within 30 days of the vaccination, and that a late fee applies if the tag or renewal is bought more than 30 days after vaccination or more than 30 days after the registration expires. It says fines for no vaccination or no registration are issued after 60 days. The stated fine is $300 for no rabies vaccination and $300 for no county registration. The late fee is $10. You are not in violation if the dog has a current rabies vaccine, you have paid for the tag, and you are waiting for it in the mail. <span class="src">[{BW}]</span></p>
<h3>Tag cost</h3>
<p>The fee depends on a microchip, not on whether the dog is spayed or neutered. The fee section was marked updated June 30, 2026.</p>
<ul>
<li>Microchipped dog or cat: $25 for one year. The page also lists $65 for three years with a valid three-year rabies vaccine. See the conflict above. The county says it does not offer a three-year renewal.</li>
<li>Not microchipped: $55 for one year, and the page also lists $145 for three years with a valid three-year vaccine.</li>
<li>Replacement tag: $10, and only at the Adoption Center.</li>
<li>Online or veterinary-office purchase: a service fee of not more than $5 per tag. The tags page does not add that service fee to a tag bought at the Adoption Center.</li>
</ul>
<h3>Where to get the tag and the shot</h3>
<p>Buy the tag at the Adoption Center, at an approved veterinary office, online (upload the rabies certificate; the tag is not issued until the county receives it), or by mail. Tag sales at the Adoption Center are Monday through Sunday, 11:00 a.m. to 5:30 p.m. Bring a copy of the rabies certificate. Animal Care is at 2400 Southwest 42nd Street, Fort Lauderdale, Florida 33312. Mail a check or money order payable to the Board of County Commissioners, Animal Care Division, to Broward County Animal Licensing, in care of PetData, Post Office Box 141929, Irving, Texas 75014-1929. <span class="src">[{BW}, {BW_HOME}]</span></p>
<p>The county has not published a single rabies-shot price. See the clinic conflict above. The on-site Pet Care Clinic is temporarily closed and is not taking new appointments. The clinic page's listed mobile clinic date, Wednesday, October 14, 2026, was already past on this check. The page says to check back for the next date. Pets must be 4 months or older for a rabies vaccine at those clinics. The contact printed for clinic registration is petcareclinic@broward.org or 954-357-9567. A private veterinarian can give the vaccine. This page does not have a county price for that visit. <span class="src">[{BW_CLINIC}, {BW_HOME}]</span></p>
<h3>Listed Broward places</h3>
<div class="wrap"><table>
<tr><th>Place</th><th>What that place's page requires</th></tr>
<tr><td>{pl("hollywood-dog-beach","Dog Beach at Hollywood Beach")}</td><td>Dogs must have a current rabies tag. The city page does not say a staff member checks it at the entrance. <span class="src">[{HW}]</span></td></tr>
<tr><td>{pl("fort-lauderdale-canine-beach","Canine Beach")}</td><td>The city's park introduction says every dog must have current vaccinations and a license. Canine Beach's own numbered rules do not repeat that line. <span class="src">[{FTL}]</span></td></tr>
<tr><td>{pl("pompano-wags-and-waves","Wags and Waves Dog Beach")}</td><td>The city page names the beach and states no tag, license, or vaccination rule for it. <span class="src">[{POMP_B}]</span></td></tr>
<tr><td>{pl("barkham-markham","Barkham at Markham Park")} and {pl("woofing-waters","Woofing Waters")}</td><td>Proof of rabies vaccination is required, and the document must show the expiration date or the date the vaccine was given. The page does not say the county registration tag is inspected at the park. <span class="src">[{BW_PARKS}]</span></td></tr>
<tr><td>{pl("ftl-holiday-park","Holiday Park Dog Park")}, {pl("ftl-riverside","Riverside Neighborhood Dog Park")}, {pl("ftl-snyder","Bark Park at Snyder Park")}</td><td>Each park's rules say every dog must have a current vaccination and license. Puppies under four months are not allowed. The city says these dog parks are not staffed. <span class="src">[{FTL}]</span></td></tr>
<tr><td>{pl("pompano-canine-corner","Canine Corner")}</td><td>Members only. Registration requires a current rabies vaccination certificate. The city says the metal tag alone is not enough. Also bring proof of residency and a photo of the dog. In the park, the dog must wear a current rabies tag and a personalized identification tag. The park is self-monitored. Register at the Emma Lou Olson Civic Center, 1801 Northeast 6th Street, or the Pompano Beach Aquatic Center, 820 Northeast 18th Avenue. <span class="src">[{POMP}]</span></td></tr>
</table></div>
<h2>Palm Beach County</h2>
<p>County Code chapter 4 applies in both cities and unincorporated areas unless a municipal exemption applies. This check did not find a published exemption for Boca Raton or Jupiter. The county's ordinance index does not list exempt cities. <span class="src">[{PBC_CODE}, {PBC_ORD}]</span></p>
<p>Use the age conflict above before you rely on a single number. Section 4-10 requires rabies vaccination in line with the state statute. A visitor who is in the county for 30 days or less meets that rabies section with a current certificate from home. A dog or cat without one must be vaccinated and given a county certificate. A dog or cat that moves in for more than 30 days needs a current certificate that matches the county form, or a new county vaccination and certificate. <span class="src">[{PBC_CODE}, {S828}]</span></p>
<p>Section 4-11 says no rabies and license tag is issued until a licensed veterinarian's rabies proof is shown. The tag is valid for one year from the vaccination date, must be renewed every year, and cannot last past the vaccine expiration. Even with a three-year vaccine, the tag is never effective for more than one year. The effective dates for the later years are one year and two years after the vaccination date. Buy the tag by the schedule in the code: by the age in section 4-11, within 30 days of getting the dog, or within 30 days after the dog enters the county. Missing the renewal by more than 30 days after the old tag expires brings a late penalty. The code says the County Commission sets that penalty by resolution. The Animal Care fee list does not state the late-penalty amount. <span class="src">[{PBC_CODE}, {PBC}]</span></p>
<p>Every dog must wear a valid county license tag, fastened so it is clearly visible. A dog in a secure enclosure does not have to wear it if the tag is fastened to a collar or harness that is attached to the enclosure. Dogs do not wear it during a registered field trial, obedience trial, conformation show, or match. <span class="src">[{PBC_CODE}]</span></p>
<h3>Tag and shot cost</h3>
<p>Prices on the Animal Care rabies page:</p>
<ul>
<li>Rabies vaccination: $15.</li>
<li>License tag, sterilized pet: $15.</li>
<li>License tag, sterilized pet, senior: $11.25. The page does not say what age counts as senior.</li>
<li>License tag, pet that is not sterilized: $75.</li>
<li>Lost tag: $5.</li>
<li>Dangerous-dog tag: $150.</li>
</ul>
<p>The code says the county division and authorized veterinary clinics sell the tag. The main shelter is 7100 Belvedere Road, West Palm Beach, Florida 33411, west of Florida's Turnpike. Phone (561) 233-1200. Hours on the rabies page: Monday through Friday 11:00 a.m. to 6:00 p.m., Saturday 10:00 a.m. to 5:00 p.m., Sunday 11:00 a.m. to 4:00 p.m. Closed government holidays. For tag renewal questions, the county says to call 1-888-782-6057. Shot times are in the conflict note above. Call before you go. <span class="src">[{PBC}, {PBC_HOME}, {PBC_CODE}]</span></p>
<h3>Listed Palm Beach County places</h3>
<div class="wrap"><table>
<tr><th>Place</th><th>What that place's page requires</th></tr>
<tr><td>{pl("boca-bark-beach","Bark Beach at Spanish River Park")}</td><td>The city requires a Bark Beach permit, carried by the handler, one permit per dog. The beach rules and the annual permits page do not list a rabies certificate or a county license tag among the documents for that permit. The permits page does require residency proof for a resident rate. <span class="src">[{BOCA}, {BOCA2}]</span></td></tr>
<tr><td>{pl("jupiter-dog-beach","Jupiter Dog Beach")}</td><td>The town's beach questions page says dogs must have proper tags and licenses worn visibly and securely around the neck, and must show evidence of rabies vaccination. The town's dogs-on-the-beach page and the county Jupiter Dog Beach page do not repeat that line. None of the three says an out-of-county tag is accepted or rejected. <span class="src">[{JUP}, {JUP2}, {JUP3}]</span></td></tr>
<tr><td>{pl("pbc-canine-cove","Canine Cove")}, {pl("pbc-lake-ida","Lake Ida West")}, {pl("pbc-lake-woof","Lake Woof")}, {pl("pbc-pooch-pines","Pooch Pines")}</td><td>County dog park rules say dogs must be vaccinated and must display current licenses. The page does not say a staff member checks papers at the gate. These parks are unsupervised. <span class="src">[{PBC_PARKS}]</span></td></tr>
</table></div>
<h2>Left off this page</h2>
<ul>
<li>Private veterinarian prices, other than the county clinic prices above.</li>
<li>The dollar amount of Palm Beach County's late penalty. The code says it exists and that the commission sets it. The fee page does not give the number.</li>
<li>The age for Palm Beach County's senior tag discount. The $11.25 price is on the county page. The qualifying age is not.</li>
<li>A separate city dog-license fee for Miami Beach, Hollywood, Fort Lauderdale, Pompano Beach, Boca Raton, or Jupiter. The city pages read for this check do not publish one. That is not a finding that no city fee exists.</li>
<li>A Miami-Dade citation dollar amount. The vaccinations page says a civil violation notice follows the grace period. It does not state the fine.</li>
<li>Whether an unstaffed gate has someone looking at tags. Fort Lauderdale says its dog parks are not staffed. Pompano says Canine Corner is self-monitored and that animal control patrols. No listed page describes a booth that inspects papers for every dog.</li>
</ul>
<p>Hours, beach permits, and the rest of the park rules are on each {a("/","place page")}.</p>'''
s.page('license-and-rabies/index.html',LIC_TITLE,LIC_DESC,lic,checked=("26 Oct 2026","2026-10-26"))
FAQ_Q="Are dogs allowed on most South Florida beaches?"
FAQ_A="No. On most public beaches in Miami-Dade, Broward and Palm Beach, dogs (other than service animals) are not allowed. Use a designated dog beach."
b=f'''<h1>{esc(FAQ_Q)}</h1><div class="card"><p><strong>No.</strong> {esc(FAQ_A[4:])}</p></div>
<ul><li>Miami Beach: dogs are prohibited from city beaches except the designated Bark Beach at 80 to 81 Streets <span class="src">[{a(P[0]["src"][0])}]</span>.</li>
<li>Palm Beach County: dogs are not allowed on county beaches, with the exception of ADA service animals; Jupiter Dog Beach is the county's off-leash beach stretch <span class="src">[{a("https://discover.pbc.gov/parks/General/Dogs.aspx")}, {a("https://discover.pbc.gov/parks/Pages/Jupiter-Dog-Beach.aspx","source 2")}]</span>.</li>
<li>Fort Lauderdale: pets are not allowed on beaches or in any body of water unless permitted by law, except at Canine Beach <span class="src">[{a("https://www.parks.fortlauderdale.gov/parks/dog-friendly-places")}]</span>.</li>
<li>Jupiter calls its beach "one of the few remaining dog-friendly beaches in the state of Florida" <span class="src">[{a("https://jupiter.fl.us/437/Dogs-on-the-Beach")}]</span>.</li></ul>
<p>Where dogs are allowed, rules usually include a leash to and from the sand, a current rabies tag or vaccination proof, a limit of two or three dogs per person, and picking up waste. See the {a("/dog-beaches/","dog beach list")}. County license fees, where to get the tag, and which places ask for proof are on the {a("/license-and-rabies/","license and rabies page")}.</p>'''
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
