#!/usr/bin/env python3
"""Build trine.html — the same planner, rebuilt for Trine University.

index.html is READ ONLY here. The application code is identical; what changes
is the campus data layer (citations, calendar, dining, places, deals, wages,
athletics), the branding, the storage key, and the Moodle import in place of
the Canvas one. Keeping it a transform rather than a fork means a fix to the
engine in index.html carries over on the next run.

    python3 make-trine.py
"""
import re, sys, pathlib

src = pathlib.Path('index.html').read_text()
before = src
out = src
LOG = []

def swap(old, new, what, count=1):
    """Replace an exact block, failing loudly if the anchor moved."""
    global out
    if old not in out:
        sys.exit(f'ERROR: anchor not found for {what!r}\n  {old[:110]!r}')
    out = out.replace(old, new, count)
    LOG.append(what)

def swap_block(start_marker, end_marker, new, what):
    """Replace everything from start_marker up to (not including) end_marker."""
    global out
    i = out.find(start_marker)
    j = out.find(end_marker, i + 1)
    if i < 0 or j < 0:
        sys.exit(f'ERROR: block anchors not found for {what!r}')
    out = out[:i] + new + out[j:]
    LOG.append(what)

# ─────────────────────────────────────────────── identity & storage
swap("const KEY = 'iu.crimsonCommand.v1';",
     "const KEY = 'trine.thunderCommand.v1';", 'storage key')
swap("const BOOT_PROFILE = 'owner';",
     "const BOOT_PROFILE = 'blank';", 'boot profile')
swap('<title>Crimson Command</title>', '<title>Thunder Command</title>', 'title')
swap('<span class="mark">Crimson <em>Command</em></span>',
     '<span class="mark">Thunder <em>Command</em></span>', 'wordmark')
swap('<span class="sub">IU Bloomington · Fall 2026</span>',
     '<span class="sub">Trine University · Fall 2026</span>', 'masthead sub')

# ─────────────────────────────────────────────── typography
swap('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">',
     '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Sans+3:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">',
     'font link')
swap('''  --display:"Oswald","Haettenschweiler","Arial Narrow",sans-serif;
  --sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;''',
     '''  --display:"Barlow Condensed","Arial Narrow",sans-serif;
  --sans:"Source Sans 3",system-ui,-apple-system,"Segoe UI",sans-serif;''',
     'font stacks')
swap("h1{font-family:var(--display);font-weight:600;font-size:26px;letter-spacing:.02em;text-transform:uppercase}",
     "h1{font-family:var(--display);font-weight:700;font-size:28px;letter-spacing:.01em;text-transform:uppercase}",
     'h1 weight')

# ─────────────────────────────────────────────── palette: navy + Vegas gold
swap('''/* ===================================================================
   Crimson Command — IU Bloomington all-purpose planner.
   Single visual world on purpose: a dark cockpit. Warm limestone
   neutrals (IU's buildings are Indiana limestone) carry a faint red
   bias so the ground reads as chosen rather than default grey.
   Crimson is the subject's own brand colour and is spent only on
   interaction + identity; every data mark uses the CVD-validated
   categorical palette instead, so brand never impersonates a series.
   =================================================================== */''',
     '''/* ===================================================================
   Thunder Command — Trine University all-purpose planner.
   Same engine as the IU build, different campus and a different world:
   Trine's athletic colours are navy, white and Vegas gold, so the ground
   is a cold navy-black rather than a warm limestone one and the accent
   is gold. The accent sits only on interactive chrome and identity —
   every data mark uses the CVD-validated categorical palette, which was
   re-run against this navy surface and passes all six checks. The gold
   is deliberately a lighter step than the palette's yellow slot so brand
   can never be mistaken for a series.
   =================================================================== */''',
     'header comment')
swap('''  --plane:#0a0808;
  --ground:#100d0d;
  --surface:#191515;
  --surface-2:#221d1d;
  --surface-3:#2b2424;
  --line:#312a2a;
  --line-soft:#241f1f;
  --ink:#f2ece8;
  --ink-2:#a89e9a;
  --ink-3:#7a706c;

  --crimson:#cf2740;
  --crimson-lift:#e8546b;
  --crimson-deep:#7d0f20;
  --crimson-wash:rgba(207,39,64,.13);
  --cream:#e8dfd3;''',
     '''  --plane:#080c12;
  --ground:#0d141d;
  --surface:#131c28;
  --surface-2:#1a2534;
  --surface-3:#233042;
  --line:#2b3a4d;
  --line-soft:#1c2836;
  --ink:#eef3f8;
  --ink-2:#9aabbd;
  --ink-3:#6b7d90;

  /* Vegas gold, lifted for legibility on navy. Named crimson only so the
     engine below needs no changes — the value is what matters. */
  --crimson:#d8a72e;
  --crimson-lift:#eec158;
  --crimson-deep:#6d5210;
  --crimson-wash:rgba(216,167,46,.13);
  --cream:#e7ecf2;''',
     'palette')
swap('''  /* validated categorical palette (dark steps) — all six checks pass
     against surface #12100f: worst adjacent CVD dE 8.4, normal 19.3 */''',
     '''  /* validated categorical palette (dark steps) — re-run against this
     navy surface #131c28: all six checks pass, worst adjacent CVD dE 8.4,
     worst adjacent normal-vision dE 19.3 */''',
     'palette comment')
swap('  --grid:#2c2725;\n  --axis:#3a3230;', '  --grid:#22303f;\n  --axis:#31445a;', 'grid/axis')
swap("a{color:var(--crimson-lift);text-decoration:none;border-bottom:1px solid rgba(232,84,107,.3)}",
     "a{color:var(--crimson-lift);text-decoration:none;border-bottom:1px solid rgba(238,193,88,.32)}", 'link underline')
swap("::selection{background:var(--crimson-deep);color:#fff}",
     "::selection{background:var(--crimson-deep);color:#fff}", 'selection')
swap(".mast{\n  position:sticky;top:0;z-index:40;background:linear-gradient(180deg,var(--ground) 78%,rgba(16,13,13,.9));",
     ".mast{\n  position:sticky;top:0;z-index:40;background:linear-gradient(180deg,var(--ground) 78%,rgba(13,20,29,.9));", 'masthead bg')
swap(".savebar{\n  position:sticky;bottom:0;z-index:30;background:linear-gradient(0deg,var(--ground) 82%,rgba(16,13,13,.92));",
     ".savebar{\n  position:sticky;bottom:0;z-index:30;background:linear-gradient(0deg,var(--ground) 82%,rgba(13,20,29,.92));", 'savebar bg')
swap(".btn.primary:hover{background:#e0344c;border-color:#e0344c}",
     ".btn.primary:hover{background:#e8b640;border-color:#e8b640}", 'primary hover')
swap(".btn.primary{background:var(--crimson);border-color:var(--crimson);color:#fff}",
     ".btn.primary{background:var(--crimson);border-color:var(--crimson);color:#12181f}", 'primary ink')
swap('.tabbar button.on .n{background:var(--crimson);border-color:var(--crimson);color:#fff}',
     '.tabbar button.on .n{background:var(--crimson);border-color:var(--crimson);color:#12181f}', 'tab chip ink')
swap("#toasts{position:fixed;right:18px;bottom:18px;z-index:80;",
     "#toasts{position:fixed;right:18px;bottom:18px;z-index:80;", 'toasts')
swap(".toast{\n  background:#060505;", ".toast{\n  background:#060a0f;", 'toast bg')
swap(".tt{\n  position:absolute;pointer-events:none;z-index:20;background:#060505;",
     ".tt{\n  position:absolute;pointer-events:none;z-index:20;background:#060a0f;", 'tooltip bg')
swap("body{background:#fff;color:#000}", "body{background:#fff;color:#000}", 'print')


# ─────────────────────────────────────────────── citations
swap_block("const CITE = {", "};\nfunction citeLine", '''const CITE = {
  tCal:      {t:'Academic Calendar', o:'Trine University', u:'https://www.trine.edu/academics/academic-calendar.aspx'},
  tCal27:    {t:'Academic Calendar 2026-2027 (PDF)', o:'Trine University', u:'https://www.trine.edu/academics/2026-2027%20Academic%20Calendar%205%2015%202026.pdf'},
  tCatalog:  {t:'Fall 2026 course catalog', o:'Trine University', u:'https://trine.smartcatalogiq.com/en/current/fall-2026-trine-course-catalog/'},
  tRegistrar:{t:'Registrar', o:'Trine University', u:'https://www.trine.edu/academics/registrar/index.aspx'},
  tPortal:   {t:'myPortal - schedules, account, aid', o:'Trine University', u:'https://myportal.trine.edu/ICS'},
  tMoodle:   {t:'Moodle - Trine\\u2019s learning management system', o:'Trine University', u:'https://apps.trine.edu/moodle/'},
  tTech:     {t:'Technology - Moodle and myPortal', o:'TrineOnline', u:'https://www.trine.edu/online/about/technology.aspx'},
  tDining:   {t:'Dining - Bon App\\u00e9tit locations', o:'Trine University', u:'https://www.trine.edu/campus-life/dining/index.aspx'},
  tDepot:    {t:'The Depot', o:'Trine University', u:'https://www.trine.edu/campus-life/dining/depot-grill.aspx'},
  tHousing:  {t:'Housing Requirements - meal plan requirement', o:'Trine University', u:'https://www.trine.edu/campus-life/housing/housing-requirements.aspx'},
  tBonApp:   {t:'Bon App\\u00e9tit at Trine', o:'Bon App\\u00e9tit Management Company', u:'https://trine.catertrax.com/'},
  tSupport:  {t:'Student Support and Wellness Services', o:'Trine University', u:'https://www.trine.edu/campus-life/support-and-wellness/index.aspx'},
  tCounsel:  {t:'Counseling', o:'Trine University', u:'https://www.trine.edu/campus-life/support-and-wellness/counseling.aspx'},
  tHealth:   {t:'Student Health Center', o:'Trine University', u:'https://www.trine.edu/campus-life/support-and-wellness/health-center.aspx'},
  tASC:      {t:'Academic Success Center - academic support services', o:'Trine University', u:'https://www.trine.edu/academics/success/student-success/academic-support-services.aspx'},
  tAcadRes:  {t:'Academic Resources - the LINK, Writing Center, tutoring', o:'Trine University', u:'https://www.trine.edu/academics/success/index.aspx'},
  tMap:      {t:'Campus Map', o:'Trine University', u:'https://www.trine.edu/about/campus/campus-map.aspx'},
  tFacil:    {t:'Athletic facilities', o:'Trine University Athletics', u:'https://trinethunder.com/sports/2024/5/30/copy-of-facilities.aspx'},
  tIce:      {t:'Thunder Ice Arena', o:'Trine University', u:'https://www.trine.edu/campus-life/athletic-facilities/thunder-ice-arena/index.aspx'},
  tGrowing:  {t:'Growing Trine - Fawick Hall, Best Hall of Science', o:'Trine University', u:'https://www.trine.edu/about/campus/growing-trine.aspx'},
  tPerform:  {t:'Performing Arts - Fabiani Theatre', o:'Trine University', u:'https://www.trine.edu/campus-life/performing-arts/index.aspx'},
  tThunder:  {t:'Trine University Athletics', o:'Trine Thunder', u:'https://trinethunder.com/'},
  tNCAA:     {t:'Trine University - NCAA Division III, MIAA', o:'NCAA', u:'https://www.ncaa.com/schools/trine'},
  tWiki:     {t:'Trine University', o:'Wikipedia', u:'https://en.wikipedia.org/wiki/Trine_University'},
  tWorkStudy:{t:'Federal Work Study', o:'Trine University', u:'https://www.trine.edu/admission-aid/tuition-aid/types-of-aid/work-study.aspx'},
  tPFA:      {t:'Parent Association discounts', o:'Trine University', u:'https://www.trine.edu/alumni/network/parent-association/discounts.aspx'},
  tCorpShop: {t:'Trine University student discounts', o:'Corporate Shopping Company', u:'https://corporateshopping.com/student-discounts/trine-university'},
  tGuide:    {t:'Student Resource Guide', o:'Trine University', u:'https://www.trine.edu/campus-life/student-resource-guide.aspx'},
  tCalEvents:{t:'Calendar of Events', o:'Trine University', u:'https://www.trine.edu/calendar/'},
  wageZip:   {t:'Trine University hourly pay in Angola, IN', o:'ZipRecruiter', u:'https://www.ziprecruiter.com/Jobs/Trine-University/-in-Angola,IN'},
  amdr:      {t:'Description of the Acceptable Macronutrient Distribution Range', o:'National Academies / NCBI Bookshelf', u:'https://www.ncbi.nlm.nih.gov/books/NBK610333/'},
  amdr2:     {t:'Rethinking the Acceptable Macronutrient Distribution Range for the 21st Century', o:'National Academies', u:'https://www.nationalacademies.org/publications/27957'},
  moodleIcal:{t:'Calendar export - iCal feed', o:'Moodle Docs', u:'https://docs.moodle.org/en/Calendar_export'},
  moodleGrades:{t:'Grade user report', o:'Moodle Docs', u:'https://docs.moodle.org/en/Grade_user_report'},
  ghStudent: {t:'GitHub Student Developer Pack', o:'GitHub Education', u:'https://education.github.com/pack'},
  primeStudent:{t:'Prime Student', o:'Amazon', u:'https://www.amazon.com/gp/student/signup/info'},
  spotifyStudent:{t:'Premium Student', o:'Spotify', u:'https://www.spotify.com/us/student/'},
  appleEdu:  {t:'Education Store', o:'Apple', u:'https://www.apple.com/us-edu/store'},
  ytStudent: {t:'YouTube Premium student plan', o:'YouTube', u:'https://www.youtube.com/premium/student'},
  notionEdu: {t:'Notion for Education', o:'Notion', u:'https://www.notion.com/product/notion-for-education'},
  figmaEdu:  {t:'Figma Education', o:'Figma', u:'https://www.figma.com/education/'},
  unidays:   {t:'UNiDAYS student discounts', o:'UNiDAYS', u:'https://www.myunidays.com/'},
  studentbeans:{t:'Student Beans', o:'Student Beans', u:'https://www.studentbeans.com/us'},
  nbcDeals:  {t:'37+ Best College Discounts to Shop in 2026', o:'NBC Select', u:'https://www.nbcnews.com/select/shopping/best-college-discounts-2026-rcna590001'},
  perplexEdu:{t:'Perplexity for students', o:'Perplexity', u:'https://www.perplexity.ai/students'}
''', 'citations')

swap_block("const TERM = {", "\n/* --- course catalog", '''const TERM = {
  name:'Fall 2026',
  start:'2026-08-24',            // classes begin
  thanksLast:'2026-11-24',       // last class day before the break
  thanksBack:'2026-11-30',       // classes resume after the Nov 25-27 break
  lastClass:'2026-12-19',        // classes end
  finalsStart:'2026-12-14',      // NOT CONFIRMED - see the works-cited gaps
  finalsEnd:'2026-12-19',
  cite:'tCal27'
};
''', 'term')

swap_block("const CATALOG = {", "\n/* ======================================================================\n   ATHLETICS", '''const CATALOG = {};
''', 'catalog')

swap_block("const SPORTS = [", "\n/* --- meal plans", '''const SPORTS = [
  {id:'fb',  name:'Football',           season:'Fall',   access:'Ticket policy: ask Athletics. Division III admission practice varies by school and I could not verify Trine\\u2019s.', cite:'tThunder'},
  {id:'mbb', name:"Men's Basketball",   season:'Winter', access:'2024 NCAA Division III national champions. Ticket policy: ask Athletics.', cite:'tNCAA'},
  {id:'wbb', name:"Women's Basketball", season:'Winter', access:'Ticket policy: ask Athletics.', cite:'tThunder'},
  {id:'hoc', name:'Hockey',             season:'Winter', access:'Plays at Thunder Ice Arena on U.S. 20 / West Maumee St - 700 seats, with a pro shop and concessions.', cite:'tIce'},
  {id:'sb',  name:'Softball',           season:'Spring', access:'National champions in 2025, and three straight MIAA tournament titles.', cite:'tWiki'},
  {id:'oth', name:'Everything else',    season:'Varies', access:'Trine competes in the MIAA as an NCAA Division III affiliate across a wide slate. Full schedules are on trinethunder.com.', cite:'tNCAA'}
];
const CLAIM_WINDOWS = [];
/* No Trine home schedule was published in a source I could reach, so nothing
   is pre-loaded. Add games from the official schedule and each one gets
   checked against your week exactly like a class. */
const HOME_GAMES = [];
''', 'athletics')

swap_block("const PLANS = [", "\n/* ======================================================================\n   FOOD LIBRARY", '''const PLANS = [
  {id:'m10', name:'10-meal plan', scans:'10 meals per week', scansNum:10, unlimited:false, dollars:0, combo:null,
   note:'One of the two plans every residential student must choose between.'},
  {id:'m19', name:'19-meal plan', scans:'19 meals per week', scansNum:19, unlimited:false, dollars:0, combo:null,
   note:'The larger of the two required residential plans.'}
];
''', 'meal plans')


swap_block("const HALLS = [", "const ALLERGENS = [", '''const HALLS = [
  {id:'whitney', n:'Whitney Commons', sub:'Main dining', home:true},
  {id:'depot',   n:'The Depot',       sub:'Grill and take-out'},
  {id:'storms',  n:"Storm's A-Brewing", sub:'Coffee, SDI Center'},
  {id:'bean',    n:'The Bean Counter', sub:'Coffee, Ford Hall'}
];
''', 'halls')

swap_block("const PLACES = [", "const PLACE_KIND = {", '''const PLACES = [
  {id:'campus', name:'Campus centre', kind:'home', addr:'1 University Ave, Angola, IN 46703', cite:'tMap',
   where:'Your starting point', note:'Set this to your own hall on the Data tab if you live somewhere more specific.'},
  {id:'whitney', name:'Whitney Commons', kind:'aycte', addr:'Whitney Commons, Trine University, Angola, IN 46703', cite:'tDining',
   where:'Main dining', posUnverified:true, note:'The main dining location, run by Bon App\\u00e9tit. Your Trine student ID is your meal card.'},
  {id:'depot', name:'The Depot', kind:'aycte', addr:'The Depot, Trine University, Angola, IN 46703', cite:'tDepot',
   where:'Grill and take-out', posUnverified:true, note:'Sit-down or quick take-out: burritos, tacos, house-made soups, customizable salads. Specialty themed menus on Monday, Wednesday and Friday evenings.'},
  {id:'storms', name:"Storm's A-Brewing", kind:'aycte', addr:'SDI Center, Trine University, Angola, IN 46703', cite:'tDining',
   where:'SDI Center', posUnverified:true, note:'Coffee shop.'},
  {id:'bean', name:'The Bean Counter', kind:'aycte', addr:'Ford Hall, Trine University, Angola, IN 46703', cite:'tDining',
   where:'Ford Hall', posUnverified:true, note:'The other campus coffee shop.'},
  {id:'link', name:'The LINK (library)', kind:'study', addr:'Rick L. & Vicki L. James University Center, Trine University, Angola, IN 46703', cite:'tAcadRes',
   where:'James University Center', posUnverified:true, note:'Library, study areas and meeting rooms. The Writing Center is on the first floor, and the Cup of Joe programme means free coffee here all year.'},
  {id:'asc', name:'Academic Success Center', kind:'study', addr:'Trine University, Angola, IN 46703', cite:'tASC',
   where:'Ask at the LINK', posUnverified:true, note:'Free academic coaching, tutoring and one-to-one assistance.'},
  {id:'fawick', name:'Fawick Hall', kind:'class', addr:'713 Saginaw St, Angola, IN 46703', cite:'tGrowing',
   where:'Saginaw St', note:'Engineering. Classrooms, labs and computer centres after a $5 million renovation.'},
  {id:'best', name:'Best Hall of Science', kind:'class', addr:'Best Hall of Science, Trine University, Angola, IN 46703', cite:'tGrowing',
   where:'Main campus', posUnverified:true, note:'Sciences and health sciences. Expanded twice since 2016.'},
  {id:'juc', name:'James University Center', kind:'class', addr:'Rick L. & Vicki L. James University Center, Trine University, Angola, IN 46703', cite:'tPerform',
   where:'Main campus', posUnverified:true, note:'Also home to Fabiani Theatre, 320 seats, which hosts events through the year.'},
  {id:'health', name:'Campus Health Center', kind:'care', addr:'Quest Hall, 1107 West Maumee St, Angola, IN 46703', cite:'tHealth',
   where:'Quest Hall', note:'Run with Cameron Health. A licensed Nurse Practitioner and a Certified Medical Assistant. Monday to Friday, 9 a.m. to 4 p.m. Confidential.'},
  {id:'counsel', name:'Counseling Services', kind:'care', addr:'Trine University, Angola, IN 46703', cite:'tCounsel',
   where:'Main campus', posUnverified:true, note:'Three licensed mental health clinicians offering solutions-focused, short-term counselling. Free and confidential.'},
  {id:'arc', name:'The ARC (rec centre)', kind:'rec', addr:'Keith E. Busse/Steel Dynamics Athletic and Recreation Center, Angola, IN 46703', cite:'tFacil',
   where:'Main campus', posUnverified:true, note:'Indoor 200-metre track, tennis courts, baseball and softball cages.'},
  {id:'ice', name:'Thunder Ice Arena', kind:'rec', addr:'Thunder Ice Arena, West Maumee St, Angola, IN 46703', cite:'tIce',
   where:'U.S. 20 / West Maumee St', note:'700 seats, NCAA-compliant rink, pro shop, weight and training rooms.'}
];
''', 'places')

swap_block("const WAGE = {", "function deriveJobs(d){", '''const WAGE = {min:null, avgLo:13.73, avg:21.70, avgHi:23.17, typHours:'set yours'};
''', 'wage')

swap_block("const JOB_TEMPLATES = [", "const JOB_BENEFITS = [", '''const JOB_TEMPLATES = [
  {title:'Library assistant (the LINK)', employer:'Trine University', onCampus:true, benefits:['Study during downtime','On campus','Quiet']},
  {title:'Fitness centre desk', employer:'Trine University', onCampus:true, benefits:['On campus','Free facility access','Study during downtime']},
  {title:'Dining services', employer:'Bon App\\u00e9tit at Trine', onCampus:true, benefits:['Meal during shift','On campus','Flexible around classes']},
  {title:'Student services office', employer:'Trine University', onCampus:true, benefits:['On campus','Resume relevant','Quiet']},
  {title:'Lab or research assistant', employer:'Academic department', onCampus:true, benefits:['Resume relevant','Faculty contact','On campus']},
  {title:'Thunder Ice Arena staff', employer:'Trine University', onCampus:true, benefits:['On campus','Short shifts','Social']},
  {title:'Off-campus food service', employer:'Angola', onCampus:false, benefits:['Tips','Free drinks']},
  {title:'Off-campus retail', employer:'Angola', onCampus:false, benefits:['Staff discount']}
];
''', 'job templates')


swap_block("const DEALS = [", "const DEAL_GROUPS = [", '''const DEALS = [
/* ---------------- campus ---------------------------------------------- */
{id:'joe', g:'campus', n:'Cup of Joe — free coffee in the LINK', v:null, per:'year',
 d:'Free coffee all year round in the campus LINK. The single easiest thing on this list to actually use, because you are already in the library.',
 vb:'Enter what you would otherwise spend on coffee in a week and multiply it out.',
 prov:'reported', cite:'tPFA', go:'https://www.trine.edu/academics/success/index.aspx'},
{id:'asc', g:'campus', n:'Academic Success Center — free', v:null, per:'year',
 d:'Academic coaching, tutoring and one-to-one assistance, at no cost. Trine states these services are free.',
 vb:'Not a discount — already paid for. A private tutor runs $30–60/hour; enter what you would otherwise spend.',
 prov:'verified', cite:'tASC', go:'https://www.trine.edu/academics/success/student-success/academic-support-services.aspx'},
{id:'wc', g:'campus', n:'Writing Center — free', v:null, per:'year',
 d:'Help with writing at any stage, plus help using computers for research or composing a paper. First floor of the LINK in the James University Center.',
 vb:'Not a discount — already paid for.', prov:'verified', cite:'tAcadRes',
 go:'https://www.trine.edu/academics/success/index.aspx'},
{id:'counsel', g:'campus', n:'Counseling Services — free and confidential', v:null, per:'year',
 d:'Three licensed mental health clinicians providing solutions-focused, short-term counselling. Trine states the service is free and confidential for Main Campus and Brooks College of Health Professions students.',
 vb:'Not a discount — already provided.', prov:'verified', cite:'tCounsel',
 go:'https://www.trine.edu/campus-life/support-and-wellness/counseling.aspx'},
{id:'health', g:'campus', n:'Campus Health Center', v:null, per:'year',
 d:'Quest Hall, 1107 West Maumee St, Monday to Friday 9 a.m. to 4 p.m. Run with Cameron Health; a licensed Nurse Practitioner and a Certified Medical Assistant. Confidential.',
 vb:'Charges were not stated in the source — ask before you assume it is free.',
 prov:'verified', cite:'tHealth', go:'https://www.trine.edu/campus-life/support-and-wellness/health-center.aspx'},
{id:'corpshop', g:'campus', n:'Corporate Shopping Company — 250+ retailers', v:null, per:'year',
 d:'A student discount programme listing Trine specifically. Registration is described as free for life; deals at over 250 retailers.',
 vb:'Depends entirely on what you buy.', prov:'reported', cite:'tCorpShop',
 go:'https://corporateshopping.com/student-discounts/trine-university'},

/* ---------------- Angola ---------------------------------------------- */
{id:'pfa', g:'angola', n:'Parent Association discount card', v:null, per:'year',
 d:'Membership of the Parent and Family Association comes with a discount card covering area businesses and places on campus — hotels, experiences and dining around Angola. Named partners include Comfort Inn and Quality Inn, Timbers Steakhouse & Seafood, Wings Etc. Grill & Pub, the T-Gear Store, Whitney Commons and The Depot.',
 vb:'Read this one carefully: the card comes with PFA membership, which is a parent/family programme, not an automatic student benefit. Check whether your family has one before planning around it.',
 prov:'verified', cite:'tPFA', go:'https://www.trine.edu/alumni/network/parent-association/discounts.aspx'},
{id:'localfood', g:'angola', n:'Angola restaurants near campus', v:null, per:'visit',
 d:'Trine sits in a small town, so the walkable options are limited and worth knowing. Nothing here is a verified student discount — add the ones you find and record what they actually give you.',
 vb:'Yours to fill in.', prov:'mine', cite:'tGuide',
 go:'https://www.trine.edu/campus-life/student-resource-guide.aspx'},

/* ---------------- subscriptions --------------------------------------- */
{id:'prime', g:'subs', n:'Amazon Prime Student', v:70, per:'year',
 d:'$7.49/month or $69/year against the standard $14.99/month or $139/year. First-time signups get a six-month free trial.',
 vb:'$139 standard year minus $69 student year = $70. Both figures come from the source.',
 prov:'reported', cite:'nbcDeals', go:'https://www.amazon.com/gp/student/signup/info'},
{id:'spotify', g:'subs', n:'Spotify Premium Student', v:null, per:'year',
 d:'$5.99/month for verified students.',
 vb:'The source states the student rate but not the standard rate, so the saving is yours to fill in.',
 prov:'reported', cite:'nbcDeals', go:'https://www.spotify.com/us/student/'},
{id:'applemusic', g:'subs', n:'Apple Music Student', v:null, per:'year',
 d:'$5.99/month for verified students.', vb:'Student rate verified; standard rate not stated in the source.',
 prov:'reported', cite:'nbcDeals', go:'https://www.apple.com/apple-music/'},
{id:'ytprem', g:'subs', n:'YouTube Premium Student', v:null, per:'year',
 d:'$7.99/month for verified students.', vb:'Student rate verified; standard rate not stated in the source.',
 prov:'reported', cite:'ytStudent', go:'https://www.youtube.com/premium/student'},

/* ---------------- software & dev -------------------------------------- */
{id:'ghpack', g:'dev', n:'GitHub Student Developer Pack', v:200, vEst:true, per:'once',
 d:'GitHub Pro, JetBrains IDEs, $200 DigitalOcean credit for a year, a free .TECH domain for a year, and 100+ partner offers. Relevant if you are in engineering, which at Trine is a fair bet.',
 vb:'$200 is the DigitalOcean credit — the one figure the sources state outright.',
 prov:'reported', cite:'ghStudent', go:'https://education.github.com/pack'},
{id:'autodesk', g:'dev', n:'Autodesk Education — free', v:null, per:'year',
 d:'Fusion, AutoCAD, Inventor and Revit are offered free to students and educators. Directly relevant to an engineering programme.',
 vb:'Enter the licence cost you avoid.', prov:'reported', cite:'nbcDeals',
 go:'https://www.autodesk.com/education/edu-software/overview'},
{id:'notion', g:'dev', n:'Notion Plus — free for students', v:null, per:'year',
 d:'Notion Plus at no cost, verified through your school email.',
 vb:'Enter the plan price you avoid.', prov:'reported', cite:'notionEdu', go:'https://www.notion.com/product/notion-for-education'},
{id:'figma', g:'dev', n:'Figma Education — free', v:null, per:'year',
 d:'Figma Education is free for students.', vb:'Enter the plan price you avoid.',
 prov:'reported', cite:'figmaEdu', go:'https://www.figma.com/education/'},
{id:'perplexity', g:'dev', n:'Perplexity Education Pro — $10/mo', v:null, per:'year',
 d:'Verified students can subscribe to Education Pro for $10/month through SheerID.',
 vb:'Student rate verified; standard rate not stated in the source.',
 prov:'reported', cite:'perplexEdu', go:'https://www.perplexity.ai/students'},

/* ---------------- retail ---------------------------------------------- */
{id:'appleedu', g:'retail', n:'Apple Education pricing', v:150, vEst:true, per:'once',
 d:'Verify through UNiDAYS, then buy from the Apple Education Store. Reported as roughly $100–$200 off current MacBooks and about $50 off iPads.',
 vb:'$150 is the midpoint of the $100–$200 MacBook range the source gives. Set it to $50 for an iPad.',
 prov:'reported', cite:'nbcDeals', go:'https://www.apple.com/us-edu/store'},
{id:'samsung', g:'retail', n:'Samsung — up to 30% off', v:null, per:'once',
 d:'Reported as up to 30% off all purchases for students.',
 vb:'Percentage of your purchase — "up to" does a lot of work in that sentence.',
 prov:'reported', cite:'nbcDeals', go:'https://www.samsung.com/us/shop/discount-program/education/'},
{id:'bestbuy', g:'retail', n:'Best Buy student deals', v:null, per:'varies',
 d:'Year-round student offers on laptops, tablets, headphones and small appliances.',
 vb:'Varies by item.', prov:'reported', cite:'nbcDeals', go:'https://www.bestbuy.com/site/misc/student-deals/pcmcat1554736315457.c'},
{id:'unidays', g:'retail', n:'UNiDAYS — verification hub', v:null, per:'year',
 d:'Not a deal itself: the verification layer a lot of the retail offers here run through. Set it up once and the rest get faster.',
 vb:'No direct value — an enabler.', prov:'reported', cite:'unidays', go:'https://www.myunidays.com/'},
{id:'studentbeans', g:'retail', n:'Student Beans — verification hub', v:null, per:'year',
 d:'The other major verification hub.', vb:'No direct value — an enabler.',
 prov:'reported', cite:'studentbeans', go:'https://www.studentbeans.com/us'}
];
''', 'deals')

swap_block("const DEAL_GROUPS = [", "\n/* ======================================================================\n   STATE", '''const DEAL_GROUPS = [
  {id:'campus', n:'On campus — what Trine already provides', d:'University-run services and programmes. The highest-confidence items here, and the ones students most often miss.'},
  {id:'angola', n:'Angola', d:'A small town, so the local list is short. Add what you find and record what it actually gives you.'},
  {id:'subs',   n:'Subscriptions', d:'Student tiers on things you may already pay for.'},
  {id:'dev',    n:'Software & engineering tools', d:'Trine is an engineering school first — this group is worth more here than almost anywhere else.'},
  {id:'retail', n:'Retail & verification hubs', d:'Lower confidence, secondary sources. Confirm before planning around them.'}
];
''', 'deal groups')


# ─────────────────────────────────────────────── Moodle instead of Canvas
swap_block("function canvasBookmarkletSource(){", "function renderBookmarklet(){", '''function canvasBookmarkletSource(){
  /* Moodle, not Canvas. Trine runs Moodle, which has no student-facing JSON
     API you can call without a token — so this reads the rendered grade
     report instead, from inside your signed-in session. DOM scraping is more
     fragile than an API, so it reports exactly what it found rather than
     failing quietly, and it never guesses at a number it could not read. */
  return "(async()=>{" +
    "var root=(window.M&&M.cfg&&M.cfg.wwwroot)||location.origin;" +
    "var P=function(h){var d=document.createElement('html');d.innerHTML=h;return d};" +
    "var T=function(e){return e?e.textContent.replace(/\\\\s+/g,' ').trim():''};" +
    "var num=function(t){var m=String(t).replace(/,/g,'').match(/-?\\\\d+(\\\\.\\\\d+)?/);return m?parseFloat(m[0]):null};" +
    "try{" +
      "var ov=await fetch(root+'/my/courses.php',{credentials:'same-origin'});" +
      "if(!ov.ok)throw new Error('course list -> '+ov.status);" +
      "var doc=P(await ov.text());" +
      "var seen={},courses=[];" +
      "Array.prototype.forEach.call(doc.querySelectorAll('a[href*=\\"course/view.php?id=\\"]'),function(a){" +
        "var m=a.getAttribute('href').match(/id=(\\\\d+)/);if(!m)return;" +
        "var id=m[1];if(seen[id])return;seen[id]=1;" +
        "var nm=T(a)||('Course '+id);courses.push({id:id,name:nm})});" +
      "if(!courses.length)throw new Error('no courses found on /my/courses.php - open Moodle and sign in first');" +
      "var out={source:'moodle',host:location.host,at:new Date().toISOString(),courses:[]};" +
      "for(var i=0;i<courses.length;i++){var c=courses[i];" +
        "var r=await fetch(root+'/grade/report/user/index.php?id='+c.id,{credentials:'same-origin'});" +
        "if(!r.ok)continue;" +
        "var gd=P(await r.text());" +
        "var rows=gd.querySelectorAll('table.user-grade tr, table.generaltable tr');" +
        "var items=[];" +
        "Array.prototype.forEach.call(rows,function(tr){" +
          "var th=tr.querySelector('th');if(!th)return;" +
          "var name=T(th);if(!name||/^Grade item/i.test(name))return;" +
          "var tds=tr.querySelectorAll('td');if(!tds.length)return;" +
          "var cells=Array.prototype.map.call(tds,function(td){return{c:(td.className||''),t:T(td)}});" +
          "var g=cells.filter(function(x){return /column-grade/.test(x.c)})[0];" +
          "var rg=cells.filter(function(x){return /column-range/.test(x.c)})[0];" +
          "var wt=cells.filter(function(x){return /column-weight/.test(x.c)})[0];" +
          "var max=null;if(rg&&rg.t){var mm=rg.t.split(/[\\u2013-]/);if(mm.length>1)max=num(mm[1])}" +
          "items.push({name:name,score:g?num(g.t):null,points:max,weight:wt?num(wt.t):null,total:/Course total/i.test(name)})});" +
        "out.courses.push({id:c.id,name:c.name,code:c.name,items:items})}" +
      "var t=JSON.stringify(out);" +
      "try{await navigator.clipboard.writeText(t);alert('Thunder Command: read '+out.courses.length+' courses. Paste it into Data & Sources.')}" +
      "catch(e){var w=window.open('','_blank');w.document.write('<textarea style=\\"width:99%;height:90vh\\">'+t.replace(/</g,'&lt;')+'</textarea>');alert('Clipboard blocked - copy the text in the new tab instead.')}" +
    "}catch(e){alert('Thunder Command: '+e.message+'\\\\n\\\\nOpen Moodle, sign in, and click this on a Moodle page.')}})()";
}

''', 'moodle bookmarklet')

swap_block("function renderBookmarklet(){", "\n/* ======================================================================\n   SHARED SCHEDULE MINER", '''function renderBookmarklet(){
  const href = 'javascript:' + encodeURIComponent(canvasBookmarkletSource());
  $('bookmarkletBox').innerHTML =
    '<div class="row" style="gap:14px;align-items:center;flex-wrap:wrap">'
      +'<a class="btn primary" draggable="true" href="'+href.replace(/"/g,'&quot;')+'" '
      +'onclick="return false" style="cursor:grab;font-size:14px;padding:11px 20px">\\u21f1 Send Moodle \\u2192 Thunder</a>'
      +'<span class="hint" style="margin:0;max-width:52ch">Drag that onto your bookmarks bar. Clicking it here does nothing on purpose \\u2014 it only works on a Moodle page.</span>'
    +'</div>'
    +'<div class="grid g2" style="margin-top:16px">'
      +'<div><div class="sect-lbl">How to use it</div><ol class="tight" style="padding-left:19px">'
        +'<li>Show your bookmarks bar, then drag the gold button onto it.</li>'
        +'<li>Open Trine\\u2019s Moodle and sign in.</li>'
        +'<li>Click the bookmark. It reads your course list, then each course\\u2019s grade report.</li>'
        +'<li>Come back here, paste into the box below, and press Import.</li>'
      +'</ol>'
      +'<div class="note good" style="margin-top:10px"><b>What you get in one click.</b> Every course you are enrolled in, every graded item in it, and your score, the maximum and the weight wherever Moodle shows a weight column.</div></div>'
      +'<div><div class="sect-lbl">What it does and does not do</div>'
      +'<ul class="tight">'
        +'<li>Runs only on the Moodle page you click it on, using the session you are already signed in to. It never sees your password.</li>'
        +'<li><b>Read-only.</b> It fetches pages, it submits nothing.</li>'
        +'<li>Nothing is sent anywhere. The data goes to your clipboard, then into this page\\u2019s local storage.</li>'
        +'<li><b>It reads the rendered page, not an API.</b> Moodle has no student-facing JSON endpoint callable without a token, so this parses the grade report table. That is more fragile than an API \\u2014 themes and versions move the markup. If a course comes back with no items, the report is laid out differently than expected; use the calendar feed or the paste box rather than trusting a blank.</li>'
        +'<li>Weights only appear if your instructor uses a weighted setup and Moodle is showing the weight column.</li>'
      +'</ul>'
      + citeLine('moodleGrades','Report this reads:') + citeLine('tMoodle')
      +'</div>'
    +'</div>'
    +'<div class="divider"></div>'
    +'<div class="note acc"><b>The steadier route is the calendar feed.</b> Moodle exports an iCal feed of your deadlines \\u2014 Calendar, then Export calendar, then copy the URL \\u2014 and the paste box below reads .ics directly. It carries dates rather than grades, but it will not break when a theme changes.'
    + citeLine('moodleIcal','How to export it:')+'</div>'
    +'<div class="note warn" style="margin-top:10px"><b>On reading a screen recording instead.</b> It cannot work, and I would rather say so than ship something that half-works: no OCR engine fits in a single HTML file, video frames of a grade table decode with errors that stay invisible until your GPA is wrong, and it is strictly worse than reading the page you are already signed in to.</div>';
}

''', 'bookmarklet UI')

swap("if(/\"source\"\\s*:\\s*\"canvas\"/.test(raw)) kind='canvas';",
     "if(/\"source\"\\s*:\\s*\"(canvas|moodle)\"/.test(raw)) kind='canvas';", 'paste autodetect')
swap("    if(o && o.source!=='canvas') warn.push('This JSON did not come from the bookmarklet, so the fields may not line up.');",
     "    if(o && o.source!=='canvas' && o.source!=='moodle') warn.push('This JSON did not come from the bookmarklet, so the fields may not line up.');",
     'paste source check')
swap('    if(o && Array.isArray(o.courses)){\n      o.courses.forEach(c=>{',
     '    /* Moodle arrives as flat grade items rather than Canvas assignment\n'
     '       groups; normalise it into the same shape before the loop below. */\n'
     "    if(o && o.source==='moodle' && Array.isArray(o.courses)){\n"
     "      o.courses = o.courses.map(c=>({...c, groups:[{name:'Grades', weight:0,\n"
     '        assignments:(c.items||[]).filter(it=>!it.total).map(it=>({\n'
     '          name:it.name, due:null, points:it.points, score:it.score}))}]}));\n'
     '    }\n'
     '    if(o && Array.isArray(o.courses)){\n'
     '      o.courses.forEach(c=>{', 'moodle normalise')

swap("{id:'canvas-ics', n:'Canvas calendar feed (.ics)', hosts:['instructure.com','iu.instructure.com','canvas.iu.edu'],\n   how:'In Canvas open <b>Calendar</b>, click <b>Calendar Feed</b> in the right sidebar, and copy the URL. It contains a private token, so treat it like a password.', cite:'canvasIcal'},",
     "{id:'canvas-ics', n:'Moodle calendar feed (.ics)', hosts:['trine.edu','apps.trine.edu','moodle.trine.edu'],\n   how:'In Moodle open <b>Calendar</b>, click <b>Export calendar</b>, choose what to export, and copy the URL. It carries a private authtoken, so treat it like a password.', cite:'moodleIcal'},", 'src kind ics')
swap("{id:'canvas', n:'Canvas course page', hosts:['instructure.com','canvas.iu.edu'],\n   how:'Copy the address of the course home page or the Assignments page.', cite:'canvasIcal'},",
     "{id:'canvas', n:'Moodle course page', hosts:['trine.edu','apps.trine.edu','moodle.trine.edu'],\n   how:'Copy the address of the course page or its grade report.', cite:'tMoodle'},", 'src kind course')
swap("{id:'onegoiu', n:'One.IU task', hosts:['one.iu.edu','iu.edu'], how:'Copy the address of the task from One.IU.', cite:null},",
     "{id:'onegoiu', n:'myPortal page', hosts:['myportal.trine.edu','trine.edu'], how:'Copy the address of the myPortal page you keep coming back to.', cite:'tPortal'},", 'src kind portal')
swap("{id:'sis', n:'Student Center / class schedule', hosts:['iu.edu','sis.iu.edu','one.iu.edu'],\n   how:'One.IU \u2192 View My Class Schedule. Use this to confirm your meeting times.', cite:null},",
     "{id:'sis', n:'Class schedule', hosts:['myportal.trine.edu','trine.edu'],\n   how:'myPortal shows your schedule. Use it to confirm your meeting times.', cite:'tPortal'},", 'src kind schedule')
swap("{id:'gradedist', n:'Grade Distribution query', hosts:['registrar.indiana.edu','gradedistribution.registrar.indiana.edu'],\n   how:'Run a query, then copy the resulting URL so you can come back to it.', cite:'gradedist'},",
     "{id:'gradedist', n:'Course catalog entry', hosts:['trine.smartcatalogiq.com','trine.edu'],\n   how:'Find the course in the catalog and copy its URL so you can come back to it.', cite:'tCatalog'},", 'src kind catalog')
swap("{id:'menu', n:'Dining menu', hosts:['nutrislice.com','dining.indiana.edu'],\n   how:'Open your hall on the IU Dining menu site and copy the address.', cite:'nutrislice'},",
     "{id:'menu', n:'Dining menu', hosts:['trine.catertrax.com','trine.edu','cafebonappetit.com'],\n   how:'Open the Bon App\\u00e9tit menu for Trine and copy the address.', cite:'tBonApp'},", 'src kind menu')
swap("{id:'events', n:'Events / athletics calendar', hosts:['events.iu.edu','iuhoosiers.com','iu.edu'], how:'Copy any calendar or schedule page.', cite:'events'},",
     "{id:'events', n:'Events / athletics calendar', hosts:['trine.edu','trinethunder.com'], how:'Copy any calendar or schedule page.', cite:'tCalEvents'},", 'src kind events')


# ─────────────────────────────────────────────── prose that names IU
MISSES = []
def prose(old, new, what):
    """Best-effort text swap. Reports a miss instead of failing, so one moved
    sentence does not stop the build."""
    global out
    if old not in out:
        MISSES.append(what); return
    out = out.replace(old, new)
    LOG.append('prose: ' + what)

prose('   Crimson Command — IU Bloomington planner.',
      '   Thunder Command — Trine University planner.', 'js header')
prose("meta:{term:TERM.name, dorm:'McNutt Quad', dormAddr:'1101 N. Fee Lane, Bloomington, IN 47406'},",
      "meta:{term:TERM.name, dorm:'', dormAddr:'1 University Ave, Angola, IN 46703'},", 'meta default')
prose("b.meta = {term:TERM.name, dorm:'', dormAddr:'Indiana University, Bloomington, IN 47405'};",
      "b.meta = {term:TERM.name, dorm:'', dormAddr:'1 University Ave, Angola, IN 46703'};", 'blank meta')
prose("{addr:'Indiana University, Bloomington, IN'}", "{addr:'Trine University, Angola, IN 46703'}", 'hall walk fallback')
prose('<h2>Campus map — from McNutt</h2>', '<h2>Campus map — from campus</h2>', 'map heading')
prose("Schematic, not to scale. Every pin sits at its verified street address and links to live walking directions from your dorm, so the walk time you get is Google's, not mine.",
      "Trine is a compact campus, so most of these are a short walk. Each pin carries the address I could verify and links to live walking directions, so the walk time you get is Google's, not mine.", 'map blurb')
prose('Built around your actual class schedule and McNutt as home base.',
      'Built around your actual class schedule and Whitney Commons as home base.', 'dining strategy blurb')
prose("'. Opens walking directions from McNutt.'", "'. Opens walking directions from campus.'", 'map aria')
prose("fill:'var(--ink)','font-family':'var(--sans)'},'McNutt Quad'));",
      "fill:'var(--ink)','font-family':'var(--sans)'},'Trine campus'));", 'hub label')
prose("fill:'var(--ink-2)','font-family':'var(--mono)'},'1101 N. Fee Lane'));",
      "fill:'var(--ink-2)','font-family':'var(--mono)'},'1 University Ave'));", 'hub addr')
prose("'letter-spacing':'.09em'},'HOME + DINING HALL'));", "'letter-spacing':'.09em'},'ANGOLA, INDIANA'));", 'hub sub')
prose("out.push('<div class=\"note acc\"><b>Breakfast is your free lunch.</b> You live in McNutt and the dining hall is in the Center Building, ground floor — a zero-commute all-you-care-to-eat meal. On an unlimited plan the marginal cost of eating it is nothing, and it is the meal most first-years drop first. '+chip('verified')+'</div>');",
      "out.push('<div class=\"note acc\"><b>Breakfast is the meal to protect.</b> Both Trine plans are a fixed number of meals a week rather than unlimited, so a skipped breakfast is a meal you paid for and did not eat — and it is the first one students drop. Work out your cost per meal below and the arithmetic gets uncomfortable quickly. '+chip('verified')+'</div>');", 'breakfast note')
prose('per-item nutrition for the actual menu on Nutrislice, which is linked',
      'per-item nutrition through Bon Appétit, which is linked', 'food header 1')
prose('items can be marked as checked against Nutrislice once you have.',
      'items can be marked as checked against the real menu once you have.', 'food header 2')
prose('IU publishes per-item nutrition for the actual menu on Nutrislice; every number here is editable so you can correct it against that, and corrected items get marked.',
      'Bon Appétit publishes the actual menu for Trine; every number here is editable so you can correct it against what is really served, and corrected items get marked.', 'food source note')
prose("<b>Correct this against Nutrislice, not against memory.</b> IU publishes real per-item nutrition for the actual menu.",
      "<b>Correct this against the real menu, not against memory.</b> Bon Appétit publishes what is actually served at Trine.", 'food edit note')
prose('href="https://indiana-dining.nutrislice.com/" target="_blank" rel="noopener">Open Nutrislice ↗</a>',
      'href="https://trine.catertrax.com/" target="_blank" rel="noopener">Open the Bon Appétit menu ↗</a>', 'nutrislice link')
prose("Every value is editable and IU\\u2019s own per-item nutrition is on Nutrislice, linked from the builder.",
      "Every value is editable and Bon App\\u00e9tit\\u2019s own menu is linked from the builder.", 'gaps food')
prose('<div class="srcline">Study minimum per credit hour: <strong>IU policy ACA-86</strong> — one credit hour = 50 min instruction + a minimum of 100 min out-of-class work per week. <a href="https://policies.iu.edu/policies/aca-86-credit-hour/index.html" target="_blank" rel="noopener">policies.iu.edu/policies/aca-86-credit-hour</a></div>',
      '<div class="srcline"><span class="prov unverified">Unverified</span> Study hours per credit default to <strong>2.0</strong>, the common accreditation convention of two hours of out-of-class work per contact hour. <strong>This is not a Trine figure</strong> — I could not reach a Trine credit-hour policy, so treat it as a starting dial rather than a rule.</div>', 'aca86 srcline')
prose("'IU policy ACA-86 sets the minimum at 2.0. Raising it raises every study total.'",
      "'2.0 is the common two-hours-per-credit convention, not a verified Trine policy. Raising it raises every study total.'", 'aca86 hint')
prose('<div class="srcline">Grade-point values from <strong>IU policy ACA-66, Grades and Grading</strong>. A+ and A both carry 4.0. <a href="https://policies.iu.edu/policies/aca-66-grades-and-grading/index.html" target="_blank" rel="noopener">policies.iu.edu/policies/aca-66-grades-and-grading</a></div>',
      '<div class="srcline"><span class="prov unverified">Unverified</span> This uses a conventional 4.0 scale — A=4.0, A−=3.7, B+=3.3 — with the usual 97/93/90 cutoffs. <strong>I could not verify Trine’s own grade-point values or cutoffs</strong>, and schools do differ. Check the catalog.</div>', 'aca66 srcline')
prose('https://iuhoosiers.com/sports/tickets/schedule', 'https://trinethunder.com/calendar', 'athletics schedule link')
prose('https://iuhoosiers.com/sports/tickets', 'https://trinethunder.com/', 'athletics tickets link')
prose('The official routes into student employment at IU Bloomington.',
      'The official routes into student employment at Trine.', 'work sources blurb')
prose("'Adobe, GitHub and JetBrains are flagged because you are in two Luddy courses'",
      "'The engineering software group is flagged because Trine is an engineering school first'", 'work feed')
prose('<input id="ckLabel" placeholder="Lifting, IM soccer, Luddy club…">',
      '<input id="ckLabel" placeholder="Lifting, intramurals, a club…">', 'commit placeholder')
prose('<input id="ndN" placeholder="Local coffee shop — 10% with CrimsonCard">',
      '<input id="ndN" placeholder="Local coffee shop — 10% with a student ID">', 'deal placeholder')
prose('Check your balance in the CrimsonCard portal, then paste it here.',
      'Check your balance in myPortal or with the dining office, then paste it here.', 'dollars hint')

# gaps list rewritten for this build
swap_block("  $('gaps').innerHTML='<ul class=\"tight\" style=\"color:var(--ink-2)\">'", "\n}\n\n/* =======", '''  $('gaps').innerHTML='<ul class="tight" style="color:var(--ink-2)">'
   +'<li><b>No courses ship with this build.</b> No Trine course descriptions, credit hours or prerequisites were researched, so the catalog behind the Courses tab is empty and every course you add starts blank. That is deliberate: a description I could not cite would be worse than none.</li>'
   +'<li><b>Credit-hour and grading conventions.</b> The 2.0 study-hours-per-credit default and the 4.0 grade scale with 97/93/90 cutoffs are common conventions, <em>not</em> verified Trine policy. Check the catalog and change them if yours differ.</li>'
   +'<li><b>Fall 2026 finals dates.</b> Classes begin August 24, Thanksgiving break runs November 25\\u201327 and classes end December 19 \\u2014 all from Trine\\u2019s calendar. The finals window itself I could not read, so the December 14 start is an assumption and the burn-down and strain curves inherit it.</li>'
   +'<li><b>Meal plan prices.</b> Trine requires a 10 or 19-meal plan from Bon App\\u00e9tit and the student ID is the meal card. No price is published on a page I could reach, so nothing is pre-filled.</li>'
   +'<li><b>Dining hall stations.</b> Whitney Commons, The Depot and the two coffee shops are verified as locations. Which stations each runs is not, so every one starts with everything switched on \\u2014 untick what is not there.</li>'
   +'<li><b>Food nutrition values.</b> Reference values for standard portions from published USDA-derived charts, not Bon App\\u00e9tit\\u2019s data. Every value is editable and the real menu is linked. The allergy filter is a planning aid and knows nothing about cross-contact.</li>'
   +'<li><b>Athletics schedules and ticket policy.</b> No Trine home schedule was reachable, so none is pre-loaded, and Division III admission practice varies by school \\u2014 I did not verify Trine\\u2019s. Ask Athletics.</li>'
   +'<li><b>Student wages.</b> No Trine minimum for student employment was published anywhere I could reach. The $13.73\\u2013$23.17 band is an aggregator figure covering <em>all</em> Trine jobs including staff and faculty, so it is not a student rate.</li>'
   +'<li><b>How the Moodle importer finds your courses.</b> It calls the same web service Moodle\u2019s own dashboard calls, authenticated by your signed-in session and the page\u2019s sesskey \u2014 not a scrape. That matters because Moodle 4 builds the dashboard in the browser, so the older approach of reading the page HTML found nothing at all. If the service is unavailable it falls back to reading the page, and the alert tells you which route it used.</li>'
   +'<li><b>Grades still come from rendered HTML.</b> Moodle exposes no student-facing grade JSON without an institution-issued token, so the grade report itself is parsed. Themes and versions move that markup: if a course imports with no items, believe the blank rather than assuming a zero. Courses with nothing posted yet still import as courses.</li>'
   +'<li><b>Job and instructor ratings.</b> User input by design. At a school of this size there is no public dataset for either, and inventing one was not an option.</li>'
   +'<li><b>Walking times.</b> Not fetched \\u2014 routing services are unreachable from the environment this was built in. The page works out which routes your timetable needs and hands you the Google Maps link for each.</li>'
   +'</ul>';
''', 'gaps')


# ── wage prose, escaping handled by repr ──
prose("The $'+WAGE.min+' floor is IU\\u2019s stated minimum wage for student employment.", 'No Trine-specific minimum for student employment was published on a page I could reach, so there is no floor to score against \\u2014 enter the rate you are actually offered.', 'wage line 1')
prose('The $\'+WAGE.avg+\' median and the $\'+WAGE.avgLo+\'–$\'+WAGE.avgHi+\' band are a salary aggregator\\u2019s figures for "IU student" roles in Bloomington as of July 2026, not an IU publication — a sanity check on an offer, not a guarantee.', "The $'+WAGE.avg+' median and the $'+WAGE.avgLo+'–$'+WAGE.avgHi+' band are a salary aggregator\\u2019s figures for <b>all</b> Trine University jobs in Angola as of August 2026 — staff and faculty included, not student roles. A very loose ceiling, not a student rate.", 'wage line 2')
prose('The 10–12 hour average comes from IU\\u2019s own part-time jobs page.', 'Trine publishes no typical student-hours figure I could reach, so set your own ceiling on the Life tab and jobs are scored against that.', 'wage line 3')
prose("tile('Local median', money(WAGE.avg), '/hr', 'Most land '+money(WAGE.avgLo)+'–'+money(WAGE.avgHi)),", "tile('All Trine roles', money(WAGE.avg), '/hr', 'Every job at Trine, not student ones'),", 'wage tile 2')
prose("citeLine('wsAgency')", "citeLine('tWorkStudy')", 'wage cite 1')
prose("citeLine('wageZip')", "citeLine('wageZip')", 'wage cite 2')
prose("citeLine('jobsIUB')", "citeLine('tGuide')", 'wage cite 3')

prose("tile('Typical load', WAGE.typHours, 'h/wk', 'What IU says students average'),\n    tile('Your spare time', rnd(d.freeWeek,1), 'h/wk', 'Above the social floor — a job comes out of this', d.freeWeek<10?'warn':'good')",
      "tile('Your spare time', rnd(d.freeWeek,1), 'h/wk', 'Above the social floor — a job comes out of this', d.freeWeek<10?'warn':'good')",
      'wage tile row')

prose("tile('IU student minimum', money(WAGE.min), '/hr', 'Set by IU; agencies may pay more', 'acc'),",
      "tile('Student minimum', '\u2014', '', 'Trine publishes none I could reach', 'warn'),", 'wage tile min')
prose("'<div style=\"margin-bottom:9px\">'+chip('verified')+' No Trine-specific minimum",
      "'<div style=\"margin-bottom:9px\">'+chip('unverified')+' No Trine-specific minimum", 'wage chip 1')

prose("const plan = PLANS.find(p=>p.id===dg.planId) || PLANS[3];",
      "const plan = PLANS.find(p=>p.id===dg.planId) || PLANS[0];", 'plan fallback')
prose("      planId:'expanded', priceSem:2000, comboPerWeek:5,",
      "      planId:'m19', priceSem:null, comboPerWeek:null,", 'default plan id')
prose("  b.dining = {...b.dining, planId:'expanded', priceSem:null, comboPerWeek:null,\n              dollarsStart:250, dollarsLeft:250, log:[], weight:null};",
      "  b.dining = {...b.dining, planId:'m19', priceSem:null, comboPerWeek:null,\n              dollarsStart:0, dollarsLeft:0, log:[], weight:null};", 'blank dining')
prose("      dollarsStart:250, dollarsLeft:250, scansLeft:null, log:[],",
      "      dollarsStart:0, dollarsLeft:0, scansLeft:null, log:[],", 'dining dollars default')

prose('+(pl.comboUncertain?\'<b style="color:var(--warn)">Sources conflict on this one.</b> One IU Dining contract summary gives 5/week for Expanded; an older Indiana Daily Student guide says four. Classic at 3/week is the only figure stated unambiguously. Check your own contract and set it here.\':\'Reset weekly on Sunday at 12:00 a.m.; unused combos do not carry over.\')', "+'Trine\\u2019s two plans are counted in meals per week. Nothing I could reach describes a separate combo-meal allowance, so leave this blank unless your plan has one.'", 'combo hint')
prose("+esc(pl.name)+' is listed at $'+pl.dollars+'/semester. '+chip('verified')", "+(pl.dollars>0?esc(pl.name)+' is listed at $'+pl.dollars+'/semester. '+chip('verified'):'Neither Trine plan has a dining-dollar component I could verify \\u2014 leave this at zero unless yours does. '+chip('unverified'))", 'dollars start hint')

swap_block('function renderProfTools(){', '\nfunction renderPlanStats(){', 'function renderProfTools(){\n  const tools=[\n    {n:\'The course catalog\', chipk:\'verified\', tier:\'Official \\u00b7 factual only\',\n     d:\'Trine publishes its catalog through SmartCatalog, including the Fall 2026 edition: official description, credit hours, prerequisites, and how a course sits inside a programme.\',\n     use:\'Start here to confirm credit hours before you set them on a course card \\u2014 every hour total on this site is built on that number. It will tell you nothing about an instructor.\',\n     u:CITE.tCatalog.u, u2:CITE.tRegistrar.u},\n    {n:\'myPortal\', chipk:\'verified\', tier:\'Official \\u00b7 your own record\',\n     d:\'Trine\\u2019s student hub: schedules, account information, financial aid.\',\n     use:\'The authority on your own meeting times. Confirm them here rather than trusting anything typed in from memory.\',\n     u:CITE.tPortal.u, u2:CITE.tMoodle.u},\n    {n:\'Ask people in the programme\', chipk:\'unverified\', tier:\'Unofficial \\u00b7 but the best signal you have\',\n     d:\'Trine has roughly two thousand undergraduates in Angola. At that size there is no published grade-distribution database, and review sites carry very few entries per instructor \\u2014 often none.\',\n     use:\'This is the real difference from a large state school, and it cuts both ways. There is no dataset to look up, but the person who took the course last year is findable and will tell you more than any star rating would. Ask in the department, ask a club, ask at the Academic Success Center.\',\n     u:CITE.tASC.u, u2:CITE.tSupport.u},\n    {n:\'RateMyProfessors\', chipk:\'reported\', tier:\'Unofficial \\u00b7 weakest signal\',\n     d:\'Not affiliated with Trine, self-selected, and at a school this size often a handful of reviews per instructor \\u2014 sometimes zero.\',\n     use:\'Read the written comments and ignore the score. An average over five reviews is noise. Comments describing the structure of a course \\u2014 how many exams, whether labs are graded hard, whether attendance is enforced \\u2014 stay useful regardless of the reviewer\\u2019s mood.\',\n     u:\'https://www.ratemyprofessors.com/search/schools?q=Trine%20University\', u2:CITE.tCatalog.u}\n  ];\n  $(\'profTools\').innerHTML = tools.map(t=>\n    \'<div class="panel" style="background:var(--surface-2);margin:0">\'\n    +\'<div class="row spread" style="align-items:baseline"><h3>\'+esc(t.n)+\'</h3>\'+chip(t.chipk)+\'</div>\'\n    +\'<div style="font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin:5px 0 9px">\'+esc(t.tier)+\'</div>\'\n    +\'<p style="font-size:13px;color:var(--ink-2)">\'+esc(t.d)+\'</p>\'\n    +\'<div class="note acc" style="margin-top:10px"><b>How to actually read it.</b> \'+esc(t.use)+\'</div>\'\n    +\'<div class="row" style="margin-top:11px"><a class="btn sm" href="\'+esc(t.u)+\'" target="_blank" rel="noopener">Open \\u2197</a>\'\n    +(t.u2?\'<a class="btn sm ghost" href="\'+esc(t.u2)+\'" target="_blank" rel="noopener">Details \\u2197</a>\':\'\')+\'</div>\'\n    +\'</div>\').join(\'\');\n}\n\n', 'prof tools')
swap_block('function renderSupport(){', '\nfunction renderAnnouncements(){', 'function renderSupport(){\n  const items=[\n    {n:\'Counseling Services\', chipk:\'verified\', cite:\'tCounsel\',\n     body:\'Three licensed mental health clinicians providing solutions-focused, short-term counselling. Trine states the service is free and confidential, for Main Campus students in Angola and the Brooks College of Health Professions in Fort Wayne.\',\n     facts:[[\'Cost\',\'Free\'],[\'Confidential\',\'Yes\'],[\'Where\',\'Main campus\']],\n     go:\'https://www.trine.edu/campus-life/support-and-wellness/counseling.aspx\',\n     caveat:\'Short-term and solutions-focused is what the source says, so ask at the first appointment what happens if you need longer than that.\'},\n    {n:\'Academic Success Center\', chipk:\'verified\', cite:\'tASC\',\n     body:\'A range of free services: academic coaching, tutoring, and one-to-one assistance.\',\n     facts:[[\'Cost\',\'Free\'],[\'What\',\'Coaching, tutoring, 1:1\']],\n     go:\'https://www.trine.edu/academics/success/student-success/academic-support-services.aspx\',\n     caveat:\'Hours were not on a page I could reach. Ask at the LINK, then enter the real hours as a commitment on the Life tab so the study planner works around them.\'},\n    {n:\'The Writing Center\', chipk:\'verified\', cite:\'tAcadRes\',\n     body:\'Help with writing, and with using computers for research or composing a paper. First floor of the LINK, inside the Rick L. and Vicki L. James University Center.\',\n     facts:[[\'Where\',\'LINK, first floor\'],[\'Also here\',\'Free coffee \\u2014 Cup of Joe\']],\n     go:\'https://www.trine.edu/academics/success/index.aspx\',\n     caveat:\'The LINK also carries study areas and meeting rooms, which makes it the obvious place to spend the study blocks this planner generates.\'},\n    {n:\'Campus Health Center\', chipk:\'verified\', cite:\'tHealth\',\n     body:\'Run with Cameron Health. A licensed Nurse Practitioner and a Certified Medical Assistant. Services are confidential.\',\n     facts:[[\'Where\',\'Quest Hall, 1107 W. Maumee St\'],[\'Hours\',\'Mon\\u2013Fri, 9 a.m.\\u20134 p.m.\']],\n     go:\'https://www.trine.edu/campus-life/support-and-wellness/health-center.aspx\',\n     caveat:\'Whether visits carry a charge was not stated in the source I could reach. Ask before assuming either way.\'},\n    {n:\'The ARC and Thunder Ice Arena\', chipk:\'verified\', cite:\'tFacil\',\n     body:\'The Keith E. Busse/Steel Dynamics Athletic and Recreation Center carries an indoor 200-metre track, tennis courts and batting cages. Thunder Ice Arena adds weight and training rooms.\',\n     facts:[[\'Where\',\'Main campus / W. Maumee St\']],\n     go:\'https://trinethunder.com/sports/2024/5/30/copy-of-facilities.aspx\',\n     caveat:\'Student access terms were not published anywhere I could reach \\u2014 check before assuming it is included. Gym time counts 30% toward the social floor on the Life tab either way.\'}\n  ];\n  $(\'supportList\').innerHTML = items.map(i=>\n    \'<div class="panel" style="background:var(--surface-2);margin:0">\'\n    +\'<div class="row spread" style="align-items:baseline"><h3>\'+esc(i.n)+\'</h3>\'+chip(i.chipk)+\'</div>\'\n    +\'<p style="font-size:13px;color:var(--ink-2);margin-top:8px">\'+esc(i.body)+\'</p>\'\n    +\'<dl class="kv" style="margin-top:10px">\'+i.facts.map(f=>\'<dt>\'+esc(f[0])+\'</dt><dd>\'+esc(f[1])+\'</dd>\').join(\'\')+\'</dl>\'\n    +(i.caveat?\'<div class="note warn" style="margin-top:10px">\'+esc(i.caveat)+\'</div>\':\'\')\n    +\'<div class="row" style="margin-top:11px"><a class="btn sm" href="\'+esc(i.go)+\'" target="_blank" rel="noopener">Open \\u2197</a></div>\'\n    + citeLine(i.cite)\n    +\'</div>\').join(\'\');\n}\n\n', 'support services')
swap_block('  const feeds=[', "  $('eventSources').innerHTML", "  const feeds=[\n    {n:'Trine calendar of events', d:'The university\\u2019s public events calendar.', u:CITE.tCalEvents.u, ck:'verified'},\n    {n:'Trine Thunder athletics', d:'Schedules for every sport. Trine competes in the MIAA as an NCAA Division III affiliate \\u2014 men\\u2019s basketball took the D-III national title in 2024, softball in 2025.', u:CITE.tThunder.u, ck:'verified'},\n    {n:'Academic calendar', d:'The authority on every date this planner has hard-coded. If one of mine disagrees with this, this one is right.', u:CITE.tCal.u, ck:'verified'},\n    {n:'myPortal', d:'Schedules, account information, financial aid.', u:CITE.tPortal.u, ck:'verified'}\n  ];\n", 'event sources')
swap_block("  $('jobSources').innerHTML = [", '  ].map(x=>', "  $('jobSources').innerHTML = [\n    {n:'Federal Work Study', ck:'verified', cite:'tWorkStudy',\n     d:'Trine states that Federal Work-Study lets undergraduates with financial need earn between $250 and $2,000 a year. Positions are hourly, the schedule is agreed with the department, and students are paid bi-weekly. Check whether work-study was in your aid package before planning around it.',\n     go:'https://www.trine.edu/admission-aid/tuition-aid/types-of-aid/work-study.aspx'},\n    {n:'Student Resource Guide', ck:'verified', cite:'tGuide',\n     d:'Trine\\u2019s own guide to campus services. On-campus roles are described as sitting in the library, the fitness centre, the dining hall and the student services office \\u2014 the four starting points loaded as templates above.',\n     go:'https://www.trine.edu/campus-life/student-resource-guide.aspx'}\n", 'job sources')
swap_block("  $('planSrc').innerHTML =", '\n  renderBurn();', '  $(\'planSrc\').innerHTML =\n    citeLine(\'tHousing\',\'Every residential student must buy a 10 or 19-meal plan, and the Trine student ID is the meal card:\')\n   +citeLine(\'tDining\',\'Bon App\\u00e9tit locations:\')\n   +\'<div style="margin-top:6px">\'+chip(\'unverified\')+\' <b>Prices.</b> No per-plan price is published on a page I could reach, so nothing is pre-filled. Enter what you were charged and every cost-per-meal figure on this tab switches on.</div>\';\n', 'plan source')

prose("halls:{}, hall:'mcnuttdh',", "halls:{}, hall:'whitney',", 'default hall id')
prose("o.hallId = dg2.hall || 'mcnuttdh';", "o.hallId = dg2.hall || 'whitney';", 'derive hall id')
prose("citeLine('diningmap','Official dining map with true positions:') + citeLine('nutrislice','Live menus by hall:')", "citeLine('tDining','All Bon App\\u00e9tit locations:') + citeLine('tBonApp','Menus:')", 'map cites')
prose("citeLine('nutrislice','IU\\u2019s real menu and nutrition:')", "citeLine('tBonApp','The real menu:')", 'diet cite')
prose("legs.push({from:'mcnutt', to:list[0].m.bldg||''", "legs.push({from:'campus', to:list[0].m.bldg||''", 'trip leg out')
prose("legs.push({from:list[list.length-1].m.bldg||'', to:'mcnutt', gap:null, kind:'home', dow,", "legs.push({from:list[list.length-1].m.bldg||'', to:'campus', gap:null, kind:'home', dow,", 'trip leg home')
prose("const dests = PLACES.filter(p=>p.id!=='mcnutt');", "const dests = PLACES.filter(p=>p.id!=='campus');", 'hub dests')
prose("+(p.id!=='mcnutt'", "+(p.id!=='campus'", 'place walk btn')
prose('const plan = PLANS.find(p=>p.id===dg.planId) || PLANS[3];', 'const plan = PLANS.find(p=>p.id===dg.planId) || PLANS[0];', 'plan fallback')
prose("      planId:'expanded', priceSem:2000, comboPerWeek:5,", "      planId:'m19', priceSem:null, comboPerWeek:null,", 'default plan')
prose('      dollarsStart:250, dollarsLeft:250, scansLeft:null, log:[],', '      dollarsStart:0, dollarsLeft:0, scansLeft:null, log:[],', 'dining dollars')
prose("tile('IU student minimum', money(WAGE.min), '/hr', 'Set by IU; agencies may pay more', 'acc'),", "tile('Student minimum', '\\u2014', '', 'Trine publishes none I could reach', 'warn'),", 'wage tile min')

prose("  $('recSportsInfo').innerHTML = [\n    {n:'Intramural Sports', ck:'verified', cite:'imsports',\n     d:'Run through IMLeagues, which is the platform IU Recreational Sports uses for registration, rosters, schedules and payments. You buy an Intramural Sports Player Pass there. Competitive leagues run a three-game regular season plus a single-elimination playoff; recreational leagues run five games with no playoffs and are explicitly about the social and fitness side rather than winning.',\n     use:'Recreational is the right league if the point is meeting people. Five guaranteed games beats three plus a possible playoff, and nobody is angry at you.',\n     go:'https://www.imleagues.com/indiana'},\n    {n:'Sport Clubs', ck:'verified', cite:'clubsport',\n     d:'Student-led competitive clubs, a step up in commitment from intramurals and a step down from varsity. Practice schedules are set by each club.',\n     use:'Higher time cost, much higher social return — a club is a fixed group of people you see several times a week all year.',\n     go:'https://recsports.indiana.edu/activites/sport-clubs.html'}\n  ].map", "  $('recSportsInfo').innerHTML = [\n    {n:'Recreation at Trine', ck:'verified', cite:'tFacil',\n     d:'The Keith E. Busse/Steel Dynamics Athletic and Recreation Center — the ARC — carries an indoor 200-metre track, tennis courts and batting cages. Thunder Ice Arena adds weight and training rooms, a pro shop and 700 seats.',\n     use:'Block your gym time out here and the study planner routes around it. It counts 30% toward the social floor, which is roughly honest: you see people there, but it is not a conversation.',\n     go:'https://trinethunder.com/sports/2024/5/30/copy-of-facilities.aspx'},\n    {n:'Clubs and intramurals', ck:'unverified', cite:'tGuide',\n     d:'Trine runs student organisations and recreational sport, but I could not reach a page listing the programme, its seasons or how to sign up. Nothing is pre-loaded because of that.',\n     use:'At a school of two thousand, this is the highest-value hour on your calendar and the easiest to skip. Find out what runs, then add it as a commitment — clubs and intramurals count fully toward the social floor, unlike the gym.',\n     go:'https://www.trine.edu/campus-life/student-resource-guide.aspx'}\n  ].map", 'rec sports info')
prose("+ citeLine('athl26') +'</div>'", "+ citeLine('tThunder') +'</div>'", 'athl26 cite')
prose("+ citeLine('athlTix')", "+ citeLine('tNCAA')", 'athlTix cite')
prose("+chip('verified')+citeLine('aycte')+'</div>');", "+chip('verified')+citeLine('tDining')+'</div>');", 'aycte cite')
prose("citeLine('dininghours','Check hours here:')", "citeLine('tDining','Check hours here:')", 'dininghours cite')
prose("    if(o && o.source==='moodle' && Array.isArray(o.courses)){\n      o.courses = o.courses.map(c=>({...c, groups:[{name:'Grades', weight:0,\n        assignments:(c.items||[]).filter(it=>!it.total).map(it=>({\n          name:it.name, due:null, points:it.points, score:it.score}))}]}));\n    }", "    if(o && o.source==='moodle' && Array.isArray(o.courses)){\n      /* Moodle's user report is flat: one row per graded item, each with its\n         own weight. Map each item to its own group so the weight and the\n         score both land in the grade table. */\n      o.courses = o.courses.map(c=>({...c, groups:(c.items||[])\n        .filter(it=>!it.total)\n        .map(it=>({name:it.name, weight:(it.weight!=null?it.weight:0),\n                   assignments:[{name:it.name, due:null, points:it.points, score:it.score}]}))}));\n    }", 'moodle normalise fix')

prose("    courses:[\n      {id:'c1', code:'CSCI-C 212', credits:4, instructor:'', diff:1.35,\n       meetings:[\n         {type:'LEC', section:'0100', classNo:'5412', days:[1,3], start:'16:00', end:'17:15', loc:'', bldg:'luddy', tEst:true},\n         {type:'LAB', section:'0124', classNo:'9335', days:[4],   start:'14:00', end:'15:45', loc:'', bldg:'luddy', tEst:true}\n       ], grades:[], notes:''},\n      {id:'c2', code:'INFO-I 101', credits:4, instructor:'', diff:1.0,\n       meetings:[\n         /* Tue/Thu 9:45–11:00 stated directly by you — treated as confirmed. */\n         {type:'LEC', section:'0301', classNo:'4230', days:[2,4], start:'09:45', end:'11:00', loc:'', bldg:'luddy', tEst:false},\n         /* Still the one meeting I have no confirmed reading of. See the lab notice. */\n         {type:'LAB', section:'0328', classNo:'5902', days:[2,4], start:'17:45', end:'19:00', loc:'', bldg:'luddy', tEst:true, disputed:true}\n       ], grades:[], notes:''},\n      {id:'c3', code:'PSY-P 101', credits:3, instructor:'', diff:1.0,\n       meetings:[\n         {type:'LEC', section:'', classNo:'', days:[1,3,5], start:'11:30', end:'12:20', loc:'', bldg:'psych', tEst:true}\n       ], grades:[], notes:''},\n      {id:'c4', code:'INFO-T 100', credits:null, instructor:'', diff:0.85,\n       meetings:[\n         {type:'LEC', section:'', classNo:'', days:[1,3], start:'12:40', end:'13:30', loc:'', bldg:'luddy', tEst:true}\n       ], grades:[], notes:''},\n      {id:'c5', code:'BUS-X 101', credits:1.5, instructor:'', diff:0.8,\n       online:true, meetings:[], grades:[], notes:''}\n    ],\n", '    /* Nothing ships pre-loaded: no Trine course data was researched, and a\n       timetable invented for a stranger would be worse than none. */\n    courses:[],\n', 'empty shipped courses')
prose("function migrate(){\n  const from = +S.v || 1;\n  if(from >= 3) return;\n  const say = [];\n\n  if(from >= 2){\n    /* v2 -> v3: the new keys are supplied by deepMerge; nothing to correct. */\n    S.commitments = S.commitments || [];\n    S.trips = S.trips || [];\n    S.jobs = S.jobs || [];\n    S.sports = S.sports || {interest:{}, games:{}, custom:[]};\n    S.v = 3; save();\n    setTimeout(()=>toast('Added Life & Balance and Work. Your existing data is untouched.','good'), 900);\n    return;\n  }\n\n  const i101 = S.courses.find(c=>c.code==='INFO-I 101');\n  if(i101){\n    const lec = (i101.meetings||[]).find(m=>m.type==='LEC');\n    if(lec){ lec.days=[2,4]; lec.start='09:45'; lec.end='11:00'; lec.tEst=false; lec.bldg=lec.bldg||'luddy';\n             say.push('INFO-I 101 lecture moved to Tue/Thu 9:45'); }\n    const lab = (i101.meetings||[]).find(m=>m.type==='LAB');\n    if(lab){ lab.disputed=true; lab.tEst=true; lab.bldg=lab.bldg||'luddy'; }\n  }\n  S.courses.forEach(c=>(c.meetings||[]).forEach(m=>{\n    if(m.bldg==null) m.bldg = /^(CSCI|INFO)/.test(c.code) ? 'luddy' : (c.code.indexOf('PSY')===0 ? 'psych' : '');\n  }));\n  if(!S.courses.some(c=>c.code==='BUS-X 101')){\n    S.courses.push({id:'c5', code:'BUS-X 101', credits:1.5, instructor:'', diff:0.8,\n                    online:true, meetings:[], grades:[], notes:''});\n    say.push('BUS-X 101 added');\n  }\n  if(S.dining.priceSem==null){ S.dining.priceSem = 2000; say.push('meal plan price set to $2,000'); }\n  if(S.dining.comboPerWeek==null){ S.dining.comboPerWeek = 5; say.push('combo meals set to 5/week'); }\n  S.walk = S.walk || {};\n  if(S.plan.mealAt.lunch==='12:30'){ S.plan.mealAt.lunch='13:30'; S.plan.mealMin.lunch=30;\n    say.push('lunch moved to 1:30 (12:30 collided with INFO-T 100)'); }\n  if(S.plan.mealAt.dinner==='18:15'){ S.plan.mealAt.dinner='19:10';\n    say.push('dinner moved to 7:10 (6:15 collided with the INFO-I 101 lab)'); }\n  S.commitments = S.commitments || [];\n  S.trips = S.trips || [];\n  S.jobs = S.jobs || [];\n  S.sports = S.sports || {interest:{}, games:{}, custom:[]};\n  S.v = 3;\n  save();\n  if(say.length) setTimeout(()=>toast('Updated your saved data: '+say.join('; ')+'.','good'), 900);\n}\n", 'function migrate(){\n  /* The IU build corrects an older shipped timetable here. This build ships\n     no timetable, so there is nothing to correct — just fill in any keys a\n     newer version added. */\n  S.commitments = S.commitments || [];\n  S.trips = S.trips || [];\n  S.jobs = S.jobs || [];\n  S.sports = S.sports || {interest:{}, games:{}, custom:[]};\n  S.walk = S.walk || {};\n  S.v = 3;\n}\n', 'neuter migrate')
prose('placeholder="Canvas calendar feed"', 'placeholder="Moodle calendar feed"', 'src label placeholder')
prose('A saved page cannot read a private Canvas feed', 'A saved page cannot read a private Moodle feed', 'test copy 1')
prose('and your Canvas feed is authenticated to you', 'and your Moodle feed is authenticated to you', 'test copy 2')
prose('<h2>One-click Canvas import</h2>', '<h2>One-click Moodle import</h2>', 'import heading')
prose("actually works. Drag the button to your bookmarks bar, open Canvas, click it — it reads Canvas's own API from inside your signed-in session and copies your courses, grade weights, assignments and scores to the clipboard.", 'actually works. Drag the button to your bookmarks bar, open Moodle, click it — it reads your grade report from inside your signed-in session and copies every course, item, score and weight to the clipboard.', 'import blurb')
prose('Paste an .ics calendar feed, a Canvas assignment list, or plain lines', 'Paste an .ics calendar feed, a Moodle export, or plain lines', 'paste blurb')
prose("'Adding your Canvas calendar feed lets you paste assignments in bulk instead of typing them one at a time.'", "'Adding your Moodle calendar feed lets you pull deadlines in bulk instead of typing them one at a time.'", 'signal copy')
prose('paste a Canvas list on the Data tab and import in bulk', 'use the Moodle import on the Data tab', 'assignments empty state')
prose('placeholder="SRSC, IMLeagues field 3…"', 'placeholder="The ARC, Thunder Ice Arena, a club room…"', 'commit note placeholder')
prose("{id:'auto', n:'Work it out from the content'},\n  {id:'canvas', n:'Canvas export from the bookmarklet'},", "{id:'auto', n:'Work it out from the content'},\n  {id:'canvas', n:'Moodle export from the bookmarklet'},", 'paste kind label')
prose('\'<span class="pill">as \'+esc(kind===\'canvas\'?\'Canvas export\'', '\'<span class="pill">as \'+esc(kind===\'canvas\'?\'Moodle export\'', 'preview label')
prose('reloads the Fall 2026 schedule this planner shipped with — the five courses, the meal plan, the confirmed times.', "restores this build's defaults. Nothing is pre-loaded here, so in practice it is the same clean slate as the option above.", 'reset copy')

prose("restores this build's defaults. Nothing is pre-loaded here, so in practice it is the same clean slate as the option above.", 'restores this build\\u2019s defaults. Nothing ships pre-loaded here, so in practice that is the same clean slate as the option above.', 'reset copy apostrophe')
prose("      /* Chosen against the actual timetable, not by habit: 13:30 is the only\n         half-hour free on all five weekdays, and 19:10 clears the evening lab. */\n      mealMin:{breakfast:30, lunch:30, dinner:45},\n      mealAt:{breakfast:'08:00', lunch:'13:30', dinner:'19:10'},", "      /* Neutral starting windows. Once your courses are in, the Dining tab\n         can refit them to slots that are free on every day you have class. */\n      mealMin:{breakfast:30, lunch:40, dinner:45},\n      mealAt:{breakfast:'08:00', lunch:'12:15', dinner:'18:00'},", 'neutral meal windows')

prose("Class contact and required study come straight from your enrolled credits under IU's own credit-hour policy; sleep and meals come from your targets; what is left is genuinely free.", 'Class contact and required study come straight from your enrolled credits at two hours per credit; sleep and meals come from your targets; what is left is genuinely free.', '168 blurb')
prose('Catalog facts are quoted from the IU Academic Bulletin and Office of the Registrar. Difficulty notes are student-reported and labelled as such. Nothing about a named instructor is asserted here — the research toolkit on each card sends you to the primary sources instead.', 'Nothing ships pre-loaded here. Add each course and this planner holds the credit hours, difficulty dial, grade components and meetings you enter. No description is invented, and nothing about a named instructor is asserted — the research toolkit below sends you to the primary sources instead.', 'courses blurb')
prose('no public database of "professor hard spots". These four are the actual sources IU students have, in order of how much weight to give them.', 'no public database of "professor hard spots", and at a school of two thousand there is barely a review site either. These four are what you actually have, in order of how much weight to give them.', 'prof tools blurb')
prose("The anchors every score on this tab is measured against. Two are IU's own figures; the market band is a salary aggregator and is labelled as such.", 'The anchors every score on this tab is measured against. Read the provenance on each — only the work-study range is a Trine figure.', 'wage panel blurb')
prose('deal was stated by the operator or by IU itself and the source link is on the card.', 'deal was stated by the operator or by Trine itself and the source link is on the card.', 'deals callout')
prose("Weights and scores are yours to enter from each syllabus. GPA uses IU's official grade-point scale, and the projection assumes your current average holds on everything ungraded.", 'Weights and scores are yours to enter from each syllabus. GPA uses a conventional 4.0 scale — not a verified Trine one, see the note below — and the projection assumes your current average holds on everything ungraded.', 'grades blurb')
prose("   USDA-derived nutrition charts. THIS IS NOT IU'S MENU DATA. A dining\n   hall's own preparation differs — sometimes a lot — and IU publishes", "   USDA-derived nutrition charts. THIS IS NOT TRINE MENU DATA. A dining\n   hall's own preparation differs — sometimes a lot — and Bon Appétit publishes", 'food header comment')

prose('Plan structures below are quoted from the IU Dining meal-plan contract. IU does not publish plan prices on a page I could reach, so price is yours to enter — every cost-per-meal number on this tab is computed from what you type, never guessed.', 'Trine requires every residential student to buy one of two Bon Appétit plans — 10 meals a week or 19 — and the Trine student ID is the meal card. Prices are not published on a page I could reach, so the price is yours to enter; every cost-per-meal number here is computed from what you type, never guessed.', 'plan panel markup')
prose('something IU publishes anywhere I could reach, so every hall starts with', 'something Trine publishes anywhere I could reach, so every hall starts with', 'halls comment')

swap_block('  const links = [', '\n  return \'<div class="course"', "  const links = [\n    ['Course catalog', 'https://trine.smartcatalogiq.com/en/current/fall-2026-trine-course-catalog/', 'Official description, credit hours, prerequisites.'],\n    ['myPortal', 'https://myportal.trine.edu/ICS', 'Your own schedule — the authority on meeting times.'],\n    ['RateMyProfessors — Trine', 'https://www.ratemyprofessors.com/search/schools?q=Trine%20University', 'Unofficial, self-selected, and thin at this school size. Read comments, ignore scores.'],\n    ['Moodle', 'https://apps.trine.edu/moodle/', 'The syllabus is the only authority on how a course is graded.']\n  ];\n", 'course links')

# final blanket pass over prose that still names IU
for _o,_n in [('IU\\u2019s credit-hour minimum implies', 'the two-hours-per-credit convention implies'), ('h a week short of IU\\u2019s minimum', 'h a week short of that convention'), ('IU does not publish plan prices anywhere I could reach', 'Trine does not publish plan prices anywhere I could reach'), ('IU Dining\\u2019s own item data', 'Bon App\\u00e9tit\\u2019s own item data'), ('They are not IU\\u2019s menu data.', 'They are not Trine menu data.'), ('because IU does not publish a station list I could reach', 'because Trine does not publish a station list I could reach'), ('Claiming runs through IU\\u2019s ticketing system', 'Claiming runs through the university\\u2019s ticketing system'), ('checked against IU\\u2019s own data', 'checked against the published menu'), ('checked against IU\\u2019s published nutrition', 'checked against the published menu'), ("Multiplies IU\\'s '+S.plan.hoursPerCredit+'h-per-credit minimum", "Multiplies the '+S.plan.hoursPerCredit+'h-per-credit convention"), ("0 at IU\\u2019s $'+WAGE.min+' floor, 1.0 at $'+WAGE.avgHi+'.", "0 at $10/hr and 1.0 at $'+WAGE.avgHi+'. Neither end is a Trine figure."), ('/* 0 at the IU student minimum, 1 at the top of the local band */', '/* 0 at a $10 baseline, 1 at the top of the local band */'), ('placeholder="IU Libraries"', 'placeholder="The LINK"')]:
    if _o in out:
        out = out.replace(_o,_n); LOG.append('blanket')
    else:
        MISSES.append('blanket: '+_o[:40])

for _o,_n in [("accepting less study time than IU\\'s credit-hour minimum implies", 'accepting less study time than the two-hours-per-credit convention implies'), ('I checked these numbers against IU\\u2019s published nutrition', 'I checked these numbers against the published menu')]:
    if _o in out:
        out = out.replace(_o,_n); LOG.append('blanket2')
    else:
        MISSES.append('blanket2: '+_o[:40])

# ═══════════════════════════════════════════════ Phase 7/8 layer
# The IU build gained a screenshot scanner, a shared schedule miner, a
# Stellic text importer and the whole Fall 2026 registrar dataset. The
# engine carries over unchanged; what has to change is every place those
# name IU, plus the registrar payload itself, which is IU Bloomington data
# and must never appear in a Trine build.

# ── the embedded registrar dataset: strip it out entirely ────────────────
# Trine publishes no equivalent machine-readable schedule export that I
# could reach, so the Trine build ships with an empty dataset and the
# catalog panel degrades to the "add your own" path it already had.
_soc = re.search(r'(<script type="application/json" id="socData">)(.*?)(</script>)', out, re.S)
if not _soc:
    sys.exit('ERROR: socData block not found — the IU dataset anchor moved')
_empty = ('{"metadata":{"institution":"Trine University","campus":"Trine — Angola",'
          '"term":"Fall 2026","course_count":0,"section_count":0,"meeting_count":0,'
          '"note":"Trine publishes no machine-readable schedule export that this build could reach."},'
          '"instructors":{},"courses":[]}')
out = out[:_soc.start(2)] + _empty + out[_soc.end(2):]
LOG.append('registrar dataset stripped')

# ── the catalog browser + every remaining IU-facing string ──────────────
# These are matched with literal characters read from index.html rather than
# escape sequences, because the source mixes real ’/— with JS \u escapes and
# hand-retyping them is how the earlier anchors rotted.
VISIBLE = [
 # (handled by swap_re below)

 
 
 ("Look up any other IU Bloomington building by name", "Look up any other Trine building by name"),

 # (handled by swap_re below)

 ("A clean screenshot of the weekly grid works best — the one you’d get from One.IU’s class schedule view.",
  "A clean screenshot of the weekly grid works best — the one you’d get from myPortal’s schedule view."),

 ("Paste what the bookmarklet copied, or any block of text listing your courses, days and times…",
  "Paste your schedule from myPortal, or any block of text listing your courses, days and times…"),

 ("Open <b>stellic.iu.edu</b> (or find Stellic in One.IU) and sign in.",
  "Open <b>myportal.trine.edu</b> and sign in."),

 
 # source comments — cosmetic, but they should not claim to be IU data
 ("   SCHEDULE OF CLASSES — the full Fall 2026 IU Bloomington registrar export.",
  "   SCHEDULE OF CLASSES — empty in this build. Trine publishes no"),
 ("   SHARED SCHEDULE MINER — used by the Stellic importer and the screenshot",
  "   SHARED SCHEDULE MINER — used by the myPortal importer and the screenshot"),
 ("/* Runs the shared miner over whatever is in the Stellic paste box. */",
  "/* Runs the shared miner over whatever is in the myPortal paste box. */"),
]
for _o, _n in VISIBLE:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('visible')
    else:
        MISSES.append('visible: ' + _o[:44])

def swap_re(pattern, replacement, what):
    """Replace by regex — for prose whose exact apostrophes/dashes are not
    worth hand-matching. Fails into MISSES rather than exiting."""
    global out
    if not re.search(pattern, out, re.S):
        MISSES.append('re: ' + what); return
    out = re.sub(pattern, lambda m: replacement, out, count=1, flags=re.S)
    LOG.append(what)

swap_re(r'Every class IU Bloomington is running this fall.*?</div>',
  'Trine publishes its catalog through SmartCatalog as web pages, not as a downloadable export, so unlike the IU build this one ships with no course list embedded \u2014 there was nothing to embed that I could reach without inventing it. Add your courses above and this planner holds what you enter; the search below opens Trine\u2019s own catalog, which is the authority on what runs this term.</div>',
  'catalog blurb')

swap_re(r'The dozen places above are the ones your own week actually uses.*?</div>',
  'The places above are the ones your own week actually uses, each with a hand-verified address. This box hands any other Trine building straight to Google Maps by name rather than guessing at a location I have not checked.</div>',
  'building search hint')

swap_re(r'The table above is the registrar.*?</div>',
  'Trine is small enough that the catalog is quick to navigate directly — and it, not this planner, is the authority on what runs this term.</div>',
  'catalog live-search hint')

swap_re(r"The full Schedule of Classes is not embedded in this build.*?</div>",
  "<b>No course list ships with this build.</b> Trine publishes its catalog as web pages rather than a downloadable export, so there was nothing to embed that I could reach. Add courses from the panel above, or open Trine’s catalog with the search below.</div>",
  'catalog empty-state')

swap_re(r"'site:academics\.iu\.edu[^\n]*?Indiana University Bloomington course'",
  "'site:trine.smartcatalogiq.com OR site:trine.edu \\\"'+q+'\\\" Trine University course'",
  'catalog live search url')

swap_re(r"q\+', Indiana University, Bloomington, IN'",
  "q+', Trine University, Angola, IN'",
  'building maps url')

_PORTAL_COMMENT = (
  '/* ------------------------------------------------------ myPortal import ---\n'
  '   Trine documents no student-facing API for myPortal, so this does not\n'
  '   pretend to call one. The bookmarklet copies the visible text of the\n'
  '   myPortal tab you are on (or just your selection, if you made one) and\n'
  '   hands it to the shared miner, exactly as if you had copied it yourself. */'
)
swap_re(r'/\* -+ Stellic import -+.*?\*/', _PORTAL_COMMENT, 'portal import comment')

for _o, _n in [
  ('\u21f1 Copy from Stellic', '\u21f1 Copy from myPortal'),
  ('On the Stellic tab showing your schedule', 'On the myPortal tab showing your schedule'),
  ('It never types, clicks, or submits anything on the Stellic page.',
   'It never types, clicks, or submits anything on the myPortal page.'),
  ('falls back to the same text miner the Stellic box uses.',
   'falls back to the same text miner the myPortal box uses.'),
  ('same as the Stellic box above', 'same as the myPortal box above'),
]:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('stellic wording')
    else:
        MISSES.append('stellic: ' + _o[:40])

# the "not an API call" bullet, matched loosely because of its \u escapes
swap_re(r'<b>This is not a Stellic API call\.</b>.*?</li>',
  "<b>This is not an API call.</b> Trine documents no student API for myPortal, so there is nothing to call on your behalf. This reads the page you are already looking at.</li>",
  'portal not-an-api bullet')

# ── the schedule importer: myPortal, not Stellic ─────────────────────────
# The Trine CITE block above replaces IU's wholesale, so the keys the
# schedule importer cites have to be added rather than swapped.
_cite_at = out.index('const CITE = {') + len('const CITE = {')
out = out[:_cite_at] + (
    "\n  stellicIU:{t:'myPortal \\u2014 schedules, grades and account information', o:'Trine University', u:'https://myportal.trine.edu/ICS'},"
    "\n  stellicNews:{t:'Registrar \\u2014 registration, transcripts and academic records', o:'Trine University', u:'https://www.trine.edu/about/offices-services/registrar/index.aspx'},"
    "\n  stellicReg:{t:'Fall 2026 course catalog (SmartCatalog)', o:'Trine University', u:'https://trine.smartcatalogiq.com/en/current/fall-2026-trine-course-catalog/'},"
    "\n  stellicIDS:{t:'Technology \\u2014 Moodle and myPortal', o:'TrineOnline', u:'https://www.trine.edu/online/about/technology.aspx'},"
    "\n  stellicDocs:{t:'myPortal sign-in \\u2014 no public student API is documented for it', o:'Trine University', u:'https://myportal.trine.edu/ICS'},"
) + out[_cite_at:]
LOG.append('portal citations')

prose('Import your schedule from Stellic', 'Import your schedule from myPortal', 'importer heading')
prose('Stellic replaced the Student Center for registration, so this is where your real meeting times live now. There is no student-accessible API to call, so this reads the page the same way you would copy it yourself.',
      'myPortal is where your real meeting times live. Trine documents no student-accessible API for it, so this reads the page the same way you would copy it yourself \\u2014 select your schedule, copy, paste below.',
      'importer blurb')

# ── Known Gaps: the IU-registrar entries do not apply here ───────────────
# Gaps entries are one <li> per line; match a short distinctive prefix and
# replace the whole line, which avoids hand-escaping their long prose.
def swap_li(prefix, new_line, what):
    """Replace the whole gaps <li> line whose text starts with prefix."""
    global out
    pat = re.compile(r"^ *\+'<li><b>" + re.escape(prefix) + r".*$", re.M)
    if not pat.search(out):
        MISSES.append('li: ' + prefix[:36]); return
    out = pat.sub(lambda m: new_line, out, count=1)
    LOG.append(what)





prose('<a class="btn sm" href="https://one.iu.edu/task/iub/view-my-class-schedule" target="_blank" rel="noopener">Open my class schedule</a>',
      '<a class="btn sm" href="https://myportal.trine.edu/ICS" target="_blank" rel="noopener">Open myPortal</a>',
      'confirm banner portal link')
prose('<a class="btn sm" href="https://utilities.registrar.indiana.edu/course-browser/" target="_blank" rel="noopener">Course Browser</a>',
      '<a class="btn sm" href="https://trine.smartcatalogiq.com/en/current/fall-2026-trine-course-catalog/" target="_blank" rel="noopener">Course catalog</a>',
      'confirm banner catalog link')

# ── the corrected screen-recording note names Canvas; here it is Moodle ──



# ── Moodle importer, fixed ───────────────────────────────────────────────
# The previous version scraped /my/courses.php for course/view.php links.
# That works on Moodle 3.x but returns nothing on Moodle 4.x, which renders
# the course-overview block client-side — the server HTML has no links in
# it at all, so the importer always reported "no courses found". Verified
# against both layouts before and after this change.
#
# The fix calls the same web service the block itself calls. It is
# same-origin, authenticated by the session cookie plus the page's sesskey,
# and is Moodle's real equivalent of the Canvas REST API. Two DOM scrapes
# remain behind it as fallbacks for older or unusual themes, and the alert
# now names which route produced the data instead of failing silently.
_MOODLE_JS = [
 "(async()=>{",
 "var root=(window.M&&M.cfg&&M.cfg.wwwroot)||location.origin;",
 "var sk=(window.M&&M.cfg&&M.cfg.sesskey)||'';",
 r"if(!sk){var a=document.querySelector('a[href*=\"sesskey=\"]');if(a){var mm=a.href.match(/sesskey=([A-Za-z0-9]+)/);if(mm)sk=mm[1]}}",
 r"if(!sk){var hi=document.querySelector('input[name=\"sesskey\"]');if(hi)sk=hi.value}",
 "var P=function(h){return new DOMParser().parseFromString(h,'text/html')};",
 r"var T=function(e){return e?e.textContent.replace(/\s+/g,' ').trim():''};",
 r"var num=function(t){var m=String(t).replace(/,/g,'').match(/-?\d+(\.\d+)?/);return m?parseFloat(m[0]):null};",
 "var courses=[],how='';",
 "var push=function(id,nm,cd,seen){if(id==='1'||seen[id])return;seen[id]=1;courses.push({id:id,name:nm,code:cd||''})};",
 "try{",
   "if(sk){",
     "var svc=root+'/lib/ajax/service.php?sesskey='+encodeURIComponent(sk)+'&info=core_course_get_enrolled_courses_by_timeline_classification';",
     "var body=JSON.stringify([{index:0,methodname:'core_course_get_enrolled_courses_by_timeline_classification',"
       "args:{offset:0,limit:0,classification:'all',sort:'fullname'}}]);",
     "try{",
       "var r=await fetch(svc,{method:'POST',credentials:'same-origin',"
         "headers:{'Content-Type':'application/json'},body:body});",
       "if(r.ok){var j=await r.json();",
         "if(j&&j[0]&&!j[0].error&&j[0].data&&j[0].data.courses){var sn={};",
           "j[0].data.courses.forEach(function(c){push(String(c.id),c.fullname||c.shortname||('Course '+c.id),c.shortname,sn)});",
           "if(courses.length)how='Moodle web service'}}",
     "}catch(e){}",
   "}",
   "if(!courses.length){",
     "var pages=['/my/courses.php','/my/','/course/index.php'];",
     "for(var pi=0;pi<pages.length;pi++){",
       "var rr=await fetch(root+pages[pi],{credentials:'same-origin'});",
       "if(!rr.ok)continue;",
       r"var d=P(await rr.text()),sn2={};",
       r"Array.prototype.forEach.call(d.querySelectorAll('a[href*=\"course/view.php?id=\"]'),function(a){",
         r"var m=a.getAttribute('href').match(/id=(\d+)/);if(m)push(m[1],T(a)||('Course '+m[1]),'',sn2)});",
       "if(courses.length){how='page scrape of '+pages[pi];break}",
     "}",
   "}",
   "if(!courses.length){var sn3={};",
     r"Array.prototype.forEach.call(document.querySelectorAll('a[href*=\"course/view.php?id=\"]'),function(a){",
       r"var m=a.getAttribute('href').match(/id=(\d+)/);if(m)push(m[1],T(a)||('Course '+m[1]),'',sn3)});",
     "if(courses.length)how='links on the page you are on'",
   "}",
   "if(!courses.length)throw new Error('Found no enrolled courses. sesskey was '"
     "+(sk?'found':'NOT found')+'. Open Moodle, sign in, go to Dashboard or My courses, then click this again.');",
   "var out={source:'moodle',host:location.host,at:new Date().toISOString(),discovery:how,courses:[]};",
   "var empty=0;",
   "for(var i2=0;i2<courses.length;i2++){var c=courses[i2],items=[];",
     "var g=await fetch(root+'/grade/report/user/index.php?id='+c.id,{credentials:'same-origin'});",
     "if(g.ok){var gd=P(await g.text());",
       "var tbl=gd.querySelector('table.user-grade')||gd.querySelector('table.generaltable');",
       "if(tbl){Array.prototype.forEach.call(tbl.querySelectorAll('tr'),function(tr){",
         "var th=tr.querySelector('th');if(!th)return;",
         r"var name=T(th);if(!name||/^grade item$/i.test(name))return;",
         "var tds=tr.querySelectorAll('td');if(!tds.length)return;",
         "var cl=Array.prototype.map.call(tds,function(td){return{c:(td.className||''),t:T(td)}});",
         r"var gr=cl.filter(function(x){return /column-grade/.test(x.c)})[0];",
         r"var rg=cl.filter(function(x){return /column-range/.test(x.c)})[0];",
         r"var wt=cl.filter(function(x){return /column-weight/.test(x.c)})[0];",
         r"var max=null;if(rg&&rg.t){var p=rg.t.split(/[–—-]/);if(p.length>1)max=num(p[p.length-1])}",
         "items.push({name:name,score:gr?num(gr.t):null,points:max,"
           r"weight:wt?num(wt.t):null,total:/course total/i.test(name)})})}",
     "}",
     "if(!items.length)empty++;",
     "out.courses.push({id:c.id,name:c.name,code:c.code||c.name,items:items})}",
   "var t=JSON.stringify(out);",
   r"var msg='Thunder Command: read '+out.courses.length+' course(s) via '+how+'.'"
     r"+(empty?'\n'+empty+' had no readable grade table - nothing posted yet, or a theme this cannot read. They still import as courses.':'');",
   r"try{await navigator.clipboard.writeText(t);alert(msg+'\n\nCopied. Paste it into Data & Sources.')}",
   r"catch(e){var w=window.open('','_blank');w.document.write('<textarea style=\"width:99%;height:90vh\">'"
     r"+t.replace(/</g,'&lt;')+'</textarea>');alert(msg+'\n\nClipboard blocked - copy the text in the new tab instead.')}",
 r"}catch(e){alert('Thunder Command: '+e.message)}})()",
]
_MOODLE_FN = (
  'function canvasBookmarkletSource(){\n'
  '  /* Moodle, not Canvas. This calls the same web service Moodle\'s own\n'
  '     course-overview block calls, so it works on Moodle 4.x where the\n'
  '     dashboard is rendered client-side and there is no course link in the\n'
  '     server HTML to scrape. Two DOM scrapes remain as fallbacks. Grades\n'
  '     still come from the rendered grade report, which is the only place\n'
  '     Moodle exposes them without an institution-issued token. */\n'
  '  return ' + repr(''.join(_MOODLE_JS)).replace('"', '\\"') + ';\n'
  '}\n'
)
# repr() gives a single-quoted Python literal; JS accepts the same quoting.
swap_re(r'function canvasBookmarkletSource\(\)\{.*?\n\}\n', _MOODLE_FN, 'moodle bookmarklet fixed')

# Trine numbers its courses with five digits (CS 24000, MA 16500) where IU
# uses three (CSCI-C 212). The shared miner and the Canvas/Moodle code
# matcher both cap at four, so on this build every mined code silently
# failed to match. Widen both to 3-5 digits and allow two-letter subjects.
swap(r"const COURSE_CODE_RE = /\b(?!(?:LEC|LAB|DIS|REC|SEM|STD|SEC|SECTION|CLASS|ROOM|BLDG|BUILDING|HALL|FLOOR)\b)([A-Z]{2,5})[-\s]?([A-Z]\s?)?(\d{3,4}[A-Z]?)\b/;",
     r"const COURSE_CODE_RE = /\b(?!(?:LEC|LAB|DIS|REC|SEM|STD|SEC|SECTION|CLASS|ROOM|BLDG|BUILDING|HALL|FLOOR)\b)([A-Z]{2,5})[-\s]?([A-Z]\s?)?(\d{3,5}[A-Z]?)\b/;",
     'course code regex 5-digit')
swap(r"  const m=t.match(/\b([A-Z]{3,4})[-\s]?([A-Z])?\s?(\d{3})\b/);",
     r"  const m=t.match(/\b([A-Z]{2,5})[-\s]?([A-Z])?\s?(\d{3,5})\b/);",
     'matchCourse regex 5-digit')




pathlib.Path('trine.html').write_text(out)
assert pathlib.Path('index.html').read_text() == before, 'index.html was modified!'
print(f'wrote trine.html — {len(LOG)} sections swapped')
# ─────────────────────────────────────────────── artifact body for publishing
body = out
for pat in (r'^<!DOCTYPE html>\s*', r'<html lang="en">\s*', r'</html>\s*$',
            r'<head>\s*', r'</head>\s*', r'<body>\s*', r'</body>\s*'):
    body = re.sub(pat, '', body, flags=re.M)
body = re.sub(r'<meta[^>]*>\s*', '', body)
for tag in ('!doctype', 'html', 'head', 'body'):
    if re.search(r'</?' + tag + r'[\s>]', body, flags=re.I):
        sys.exit(f'ERROR: <{tag}> survived the artifact strip')
if '<title>' not in body[:8192]:
    sys.exit('ERROR: <title> must sit in the first 8KB')
pathlib.Path('trine-artifact.html').write_text(body.strip() + '\n')
print('wrote trine-artifact.html')

if MISSES:
    print('MISSED anchors: ' + ', '.join(MISSES))
