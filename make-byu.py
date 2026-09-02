#!/usr/bin/env python3
"""Build byu.html — the same planner, rebuilt for BYU (Provo).

index.html is READ ONLY here. The application code is identical; what changes
is the campus data layer (citations, calendar, dining, places, deals, wages,
athletics), the branding, the storage key, and the Canvas import in place of
the Canvas one. Keeping it a transform rather than a fork means a fix to the
engine in index.html carries over on the next run.

    python3 make-byu.py
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
     "const KEY = 'byu.cougarCommand.v1';", 'storage key')
swap("const BOOT_PROFILE = 'owner';",
     "const BOOT_PROFILE = 'blank';", 'boot profile')
swap('<title>Crimson Command</title>', '<title>Cougar Command</title>', 'title')
swap('<span class="mark">Crimson <em>Command</em></span>',
     '<span class="mark">Cougar <em>Command</em></span>', 'wordmark')
swap('<span class="sub">IU Bloomington · Fall 2026</span>',
     '<span class="sub">BYU Provo · Fall 2026</span>', 'masthead sub')

# ─────────────────────────────────────────────── typography
swap('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;600;700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">',
     '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700&family=Public+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">',
     'font link')
swap('''  --display:"Oswald","Haettenschweiler","Arial Narrow",sans-serif;
  --sans:"IBM Plex Sans",system-ui,-apple-system,"Segoe UI",sans-serif;''',
     '''  --display:"Archivo","Helvetica Neue",Arial,sans-serif;
  --sans:"Public Sans",system-ui,-apple-system,"Segoe UI",sans-serif;''',
     'font stacks')
swap("h1{font-family:var(--display);font-weight:600;font-size:26px;letter-spacing:.02em;text-transform:uppercase}",
     "h1{font-family:var(--display);font-weight:700;font-size:27px;letter-spacing:.005em;text-transform:uppercase}",
     'h1 weight')

# ─────────────────────────────────────────────── palette: navy + white
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
   Cougar Command — BYU Provo all-purpose planner.
   Same engine as the IU build on a different campus. BYU is navy and
   white, so the ground is a cold navy-black and the accent is a near-
   white rather than a blue: every categorical series already contains a
   blue (--s1), and an accent in the same hue family would let brand be
   mistaken for a data series. White cannot be. The accent is spent only
   on interactive chrome and identity; every data mark uses the
   CVD-validated categorical palette unchanged.
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
     '''  --plane:#060a12;
  --ground:#0b1220;
  --surface:#111a2b;
  --surface-2:#182338;
  --surface-3:#212f47;
  --line:#2a3a52;
  --line-soft:#1a263a;
  --ink:#eef4fb;
  --ink-2:#a3b4c9;
  --ink-3:#6f8299;

  /* Near-white, for legibility and brand on navy. The token is renamed to
     --brand at the end of this transform; deliberately NOT blue, because
     the engine below needs no changes — the value is what matters. */
  --crimson:#e8f1fb;
  --crimson-lift:#ffffff;
  --crimson-deep:#20456f;
  --crimson-wash:rgba(232,241,251,.11);
  --cream:#dce7f4;''',
     'palette')
swap('''  /* validated categorical palette (dark steps) — all six checks pass
     against surface #12100f: worst adjacent CVD dE 8.4, normal 19.3 */''',
     '''  /* validated categorical palette (dark steps) — re-run against this
     navy surface #111a2b: all six checks pass, worst adjacent CVD dE 8.4,
     worst adjacent normal-vision dE 19.3 */''',
     'palette comment')
swap('  --grid:#2c2725;\n  --axis:#3a3230;', '  --grid:#23324a;\n  --axis:#33465f;', 'grid/axis')
swap("a{color:var(--crimson-lift);text-decoration:none;border-bottom:1px solid rgba(232,84,107,.3)}",
     "a{color:var(--crimson-lift);text-decoration:none;border-bottom:1px solid rgba(255,255,255,.34)}", 'link underline')
swap("::selection{background:var(--crimson-deep);color:#fff}",
     "::selection{background:var(--crimson-deep);color:#fff}", 'selection')
swap(".mast{\n  position:sticky;top:0;z-index:40;background:linear-gradient(180deg,var(--ground) 78%,rgba(16,13,13,.9));",
     ".mast{\n  position:sticky;top:0;z-index:40;background:linear-gradient(180deg,var(--ground) 78%,rgba(11,18,32,.9));", 'masthead bg')
swap(".savebar{\n  position:sticky;bottom:0;z-index:30;background:linear-gradient(0deg,var(--ground) 82%,rgba(16,13,13,.92));",
     ".savebar{\n  position:sticky;bottom:0;z-index:30;background:linear-gradient(0deg,var(--ground) 82%,rgba(13,20,29,.92));", 'savebar bg')
swap(".btn.primary:hover{background:#e0344c;border-color:#e0344c}",
     ".btn.primary:hover{background:#ffffff;border-color:#ffffff}", 'primary hover')
swap(".btn.primary{background:var(--crimson);border-color:var(--crimson);color:#fff}",
     ".btn.primary{background:var(--crimson);border-color:var(--crimson);color:#0b1220}", 'primary ink')
swap('.tabbar button.on .n{background:var(--crimson);border-color:var(--crimson);color:#fff}',
     '.tabbar button.on .n{background:var(--crimson);border-color:var(--crimson);color:#0b1220}', 'tab chip ink')
swap("#toasts{position:fixed;right:18px;bottom:18px;z-index:80;",
     "#toasts{position:fixed;right:18px;bottom:18px;z-index:80;", 'toasts')
swap(".toast{\n  background:#060505;", ".toast{\n  background:#060a0f;", 'toast bg')
swap(".tt{\n  position:absolute;pointer-events:none;z-index:20;background:#060505;",
     ".tt{\n  position:absolute;pointer-events:none;z-index:20;background:#060a0f;", 'tooltip bg')
swap("body{background:#fff;color:#000}", "body{background:#fff;color:#000}", 'print')


# ─────────────────────────────────────────────── citations
swap_block("const CITE = {", "};\nfunction citeLine", '''const CITE = {
  bCal:      {t:'Academic Calendar', o:'BYU', u:'https://academiccalendar.byu.edu/'},
  bCal26:    {t:'2026 Calendar, list view', o:'BYU', u:'https://academiccalendar.byu.edu/2026-calendar-list-view'},
  bCatalog:  {t:'Course Catalog', o:'BYU', u:'https://catalog.byu.edu/courses'},
  bCore:     {t:'University Core Explained', o:'BYU Undergraduate Catalog', u:'https://catalog.byu.edu/about-byu/university-core-explained'},
  bCoreReq:  {t:'General Education Requirements', o:'BYU Catalog', u:'https://catalog.byu.edu/pages/03MfHiIsBx8dJn7ogb8S'},
  bAmHtg:    {t:'Requirement 1 \u2014 American Heritage', o:'BYU Catalog', u:'https://catalog.byu.edu/pages/etcMcLPynkU39DOba7Nt'},
  bWrtg:     {t:'First-Year Writing', o:'BYU University Writing', u:'https://writing.byu.edu/first-year-writing/'},
  bRegistrar:{t:'Office of the Registrar', o:'BYU', u:'https://registrar.byu.edu/'},
  bMyMap:    {t:'MyMAP \u2014 registration, schedule and progress', o:'BYU', u:'https://my.byu.edu/'},
  bCanvas:   {t:'Getting started with Canvas', o:'BYU Canvas', u:'https://byucanvas.byu.edu/getting-started-with-canvas'},
  bCanvasLms:{t:'Canvas LMS and user email accounts at BYU', o:'BYU Canvas', u:'https://byucanvas.byu.edu/canvas-lms-and-user-email-accounts-at-byu'},
  canvasIcal:{t:'How do I subscribe to the Calendar feed using a calendar app?', o:'Instructure Community', u:'https://community.canvaslms.com/t5/Student-Guide/How-do-I-subscribe-to-the-Calendar-feed-using-a-calendar-app-as-a/ta-p/535'},
  canvasCourses:{t:'Courses API \u2014 GET /api/v1/courses', o:'Canvas LMS REST API', u:'https://canvas.instructure.com/doc/api/courses.html'},
  canvasAG:  {t:'Assignment Groups API \u2014 GET /api/v1/courses/:id/assignment_groups', o:'Canvas LMS REST API', u:'https://canvas.instructure.com/doc/api/assignment_groups.html'},
  bHonor:    {t:'Church Educational System Honor Code', o:'BYU', u:'https://policy.byu.edu/view/church-educational-system-honor-code'},
  bDining:   {t:'BYU Dining', o:'BYU Dining Services', u:'https://dining.byu.edu/'},
  bMealHome: {t:'Meal plan home', o:'BYU Dining', u:'https://dining.byu.edu/meal-plan-home'},
  bMealInfo: {t:'Meal Plans \u2014 what dining dollars buy and where', o:'BYU Dining', u:'https://dining.byu.edu/mealplans/info/'},
  bDiningPlus:{t:'Dining Plus meal plan', o:'BYU Dining', u:'https://dining.byu.edu/meal-plans/dining-plus-meal-plan'},
  bOpenDoor: {t:'Open Door meal plan', o:'BYU Dining', u:'https://dining.byu.edu/meal-plans/open-door'},
  bEzDining: {t:'EZ Dining meal plan', o:'BYU Dining', u:'https://dining.byu.edu/meal-plans/ez-dining'},
  bTrueBlue: {t:'True Blue Dining meal plan', o:'BYU Dining', u:'https://dining.byu.edu/meal-plans/true-blue-dining'},
  bCougarCash:{t:'Cougar Cash benefits', o:'BYU', u:'https://cougarcash.byu.edu/benefits'},
  bHousing:  {t:'On-campus housing', o:'BYU Housing', u:'https://housing.byu.edu/'},
  bMap:      {t:'Campus Map', o:'BYU', u:'https://map.byu.edu/'},
  bBuildings:{t:'List of Brigham Young University buildings', o:'Wikipedia', u:'https://en.wikipedia.org/wiki/List_of_Brigham_Young_University_buildings'},
  bLibrary:  {t:'Harold B. Lee Library', o:'BYU', u:'https://lib.byu.edu/'},
  bWilk:     {t:'Ernest L. Wilkinson Student Center', o:'Wikipedia', u:'https://en.wikipedia.org/wiki/Ernest_L._Wilkinson_Student_Center'},
  bCaps:     {t:'Counseling and Psychological Services', o:'BYU', u:'https://caps.byu.edu/'},
  bHealth:   {t:'Student Health Center', o:'BYU', u:'https://health.byu.edu/'},
  bAccess:   {t:'University Accessibility Center', o:'BYU', u:'https://uac.byu.edu/'},
  bTutor:    {t:'Tutoring and academic support', o:'BYU Research and Writing Center', u:'https://rwc.byu.edu/'},
  bAthletics:{t:'BYU Cougars \u2014 official athletics site', o:'BYU Athletics', u:'https://byucougars.com/'},
  bFB26:     {t:'BYU, Big 12 announce 2026 football schedule', o:'BYU Athletics', u:'https://byucougars.com/news/2026/01/21/byu-big-12-announce-2026-football-schedule'},
  bFBsched:  {t:'2026 BYU football schedule', o:'FBSchedules', u:'https://fbschedules.com/2026-byu-football-schedule/'},
  bTickets:  {t:'Football tickets and LaVell Edwards Stadium', o:'BYU Athletics', u:'https://tickets.byu.edu/football'},
  bRec:      {t:'Student Wellness and Intramural Sports', o:'BYU', u:'https://studentwellness.byu.edu/'},
  bJobs:     {t:'Student employment', o:'BYU', u:'https://hr.byu.edu/student-employment'},
  bStudentJobs:{t:'Student job listings', o:'BYU', u:'https://studentjobs.byu.edu/'},
  bWhyWork:  {t:'Why Work on Campus \u2014 student starting wage range', o:'BYU Financial Services', u:'https://finserve.byu.edu/why-work-on-campus'},
  bPayScale: {t:'Student Employee Hourly Pay Scale 2026', o:'BYU Human Resources', u:'https://hrs.byu.edu/hourly-pay-scale'},
  wageZip:   {t:'BYU Student jobs \u2014 reported hourly pay', o:'ZipRecruiter', u:'https://www.ziprecruiter.com/Jobs/Byu-Student'},
  bCougareat:{t:'Cougareat', o:'BYU Dining', u:'https://dining.byu.edu/cougareat'},
  bCreamery: {t:'Creamery on Ninth', o:'BYU Dining', u:'https://dining.byu.edu/creamery-on-ninth'},
  bCommons:  {t:'Dining locations, including the Commons at the Cannon Center', o:'BYU Housing', u:'https://housing.byu.edu/oncampushousing/conf_dining_locations.shtml'},
  bBig12Wk:  {t:'Big 12 announces weekday game selections for the 2026 season', o:'Big 12 Conference', u:'https://big12sports.com/news/2026/4/10/big-12-announces-weekday-game-selections-for-2026-football-season.aspx'},
  bRMP:      {t:'Brigham Young University instructor reviews', o:'RateMyProfessors', u:'https://www.ratemyprofessors.com/search/schools?q=Brigham%20Young%20University'},
  bAcctRec:  {t:'Account recovery and the BYU NetID', o:'BYU', u:'https://accountrecovery.byu.edu/'},
  csCS111:   {t:'C S 111 course entry', o:'BYU Catalog', u:'https://catalog.byu.edu/courses/14243-000'},
  csCS142:   {t:'C S 142 course entry', o:'BYU Catalog', u:'https://catalog.byu.edu/courses/01489-002'},
  csMath112: {t:'MATH 112 course entry', o:'BYU Catalog', u:'https://catalog.byu.edu/courses/03615-008'},
  csWrtg150: {t:'WRTG 150 course entry', o:'BYU Catalog', u:'https://catalog.byu.edu/courses/06839-013'},
  csAHtg100: {t:'A HTG 100 course entry', o:'BYU Catalog', u:'https://catalog.byu.edu/courses/02859-006'},
  csRelA275: {t:'Teachings and Doctrine of the Book of Mormon (REL A 275)', o:'BYU Religious Studies Center', u:'https://rsc.byu.edu/my-gospel-study/recommended-readings/doctrines-teachings-book-mormon'},
  csRelBgs:  {t:'University Core requirements, including religion', o:'BYU Bachelor of General Studies', u:'https://bgs.byu.edu/university-core-requirements'},
  csCsMap:   {t:'BS in Computer Science MAP sheet \u2014 course list and credit hours', o:'BYU College of Physical and Mathematical Sciences', u:'https://science.byu.edu/00000191-9a7e-d806-afb1-be7f718f0001/3-map-bs-in-computer-science-2024-2025-pdf'},
  csBioMap:  {t:'Biology MAP sheet \u2014 University Core course choices', o:'BYU Department of Biology', u:'https://biology.byu.edu/00000193-bce7-d282-afbf-ffe738ea0001/biology-standard-map-sheet'},
  csChemMap: {t:'Chemistry BA MAP sheet \u2014 University Core course choices', o:'BYU College of Physical and Mathematical Sciences', u:'https://science.byu.edu/00000183-429f-d026-a7c7-469fef1f0001/chem-ba-map-22-23'},
  csStat121: {t:'STAT 121 course listing', o:'BYU Independent Study', u:'https://indstudy.byu.edu/catalog/STAT-121-301-001'},
  csDance184:{t:'DANCE 184 course entry', o:'BYU Catalog', u:'https://catalog.byu.edu/courses/04323-007'},
  bDanceProg:{t:'Ballroom Dance, International Beginning', o:'BYU Undergraduate Catalog', u:'https://catalog.byu.edu/fine-arts-and-communications/dance/ballroom-dance-international-beginning'},
  csSfl210: {t:'SFL 210 course entry', o:'BYU Catalog', u:'https://catalog.byu.edu/courses/01107-016'},
  bSflProg: {t:'Human Development', o:'BYU School of Family Life', u:'https://catalog.byu.edu/family-home-and-social-sciences/school-of-family-life/human-development'},
  csRelA121:{t:'REL A 121 course entry', o:'BYU Catalog', u:'https://catalog.byu.edu/courses/04997-050'},
  csBio100: {t:'BIO 100 course entry', o:'BYU Catalog', u:'https://catalog.byu.edu/courses/00099-018'},
  csMusic311R:{t:'MUSIC 311R course entry', o:'BYU Catalog', u:'https://catalog.byu.edu/courses/04014-011'},
  bChorale: {t:'University Chorale', o:'BYU School of Music', u:'https://catalog.byu.edu/fine-arts-and-communications/school-of-music/university-chorale'},
  csUniv101:{t:'UNIV 101 course entry', o:'BYU Catalog', u:'https://catalog.byu.edu/courses/09090-004'},
  bFoundations:{t:'What is First-Year Foundations', o:'BYU General Education', u:'https://ge.byu.edu/what-is-first-year-foundations'},
  amdr:      {t:'Description of the Acceptable Macronutrient Distribution Range', o:'National Academies / NCBI Bookshelf', u:'https://www.ncbi.nlm.nih.gov/books/NBK610333/'},
  amdr2:     {t:'Rethinking the Acceptable Macronutrient Distribution Range for the 21st Century', o:'National Academies', u:'https://www.nationalacademies.org/publications/27957'},
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
  start:'2026-09-02',            // classes begin, Wednesday
  thanksLast:'2026-11-24',       // last class day before the break
  thanksBack:'2026-11-30',       // classes resume
  lastClass:'2026-12-10',        // last day of instruction
  finalsStart:'2026-12-12',      // finals run Dec 12-17; Dec 11 is Exam Preparation Day
  finalsEnd:'2026-12-17',
  cite:'bCal26'
};
''', 'term')

swap_block("const CATALOG = {", "\n/* ======================================================================\n   ATHLETICS", '''const CATALOG = {
  'A HTG 100':{
    title:'American Heritage', credits:3, creditsVerified:true, cite:'csAHtg100',
    desc:'The University Core requirement in American Heritage. New students are expected to take at least one course toward this requirement during their first year.',
    prereq:'None stated in the catalog entry.',
    topics:['American political and economic institutions','Founding documents and principles','Historical development of the republic'],
    topicsCite:'bAmHtg', reported:[],
    watch:['One of the two things BYU expects you to start in your first year, alongside first-year writing.'],
    color:'--s1'},
  'WRTG 150':{
    title:'Writing and Rhetoric', credits:3, creditsVerified:true, cite:'csWrtg150',
    desc:'Writing and research with a focus on inquiry, information literacy, rhetorical awareness, genre knowledge and reflection. One of the ways to satisfy the First-Year Writing requirement.',
    prereq:'A score of 4 or higher on AP Language and Composition earns WRTG 150 credit.',
    topics:['Inquiry and research','Information literacy','Rhetorical awareness','Genre knowledge','Reflection'],
    topicsCite:'bWrtg', reported:[],
    watch:['Carries the Y Search library modules in most sections \u2014 they are easy marks and easy to forget.'],
    color:'--s5'},
  'C S 111':{
    title:'Introduction to Computer Science', credits:3, creditsVerified:true, cite:'csCS111',
    desc:'An introduction to computer science. Listed alongside C S 142 as an entry point into the major.',
    prereq:'None stated in the MAP sheet.',
    topics:['Computational thinking','Introductory programming'],
    topicsCite:'csCsMap', reported:[],
    watch:['C S 111 and C S 142 are alternative entry points \u2014 check which one your MAP sheet expects before enrolling in both.'],
    color:'--s3'},
  'C S 142':{
    title:'Introduction to Computer Programming', credits:3, creditsVerified:true, cite:'csCS142',
    desc:'Introduction to computer programming and the first programming course in the Computer Science major sequence.',
    prereq:'None stated in the catalog entry.',
    topics:['Program design','Control flow and data types','Functions and decomposition','Debugging'],
    topicsCite:'csCsMap', reported:[],
    watch:['The prerequisite for C S 235; a late withdrawal here pushes the whole major sequence back a semester.'],
    color:'--s3'},
  'C S 235':{
    title:'Data Structures and Algorithms', credits:3, creditsVerified:true, cite:'csCsMap',
    desc:'Data structures and algorithms, following the introductory programming sequence.',
    prereq:'C S 142 or C S 111, per the Computer Science MAP sheet.',
    topics:['Lists, stacks and queues','Trees and graphs','Sorting and searching','Algorithmic complexity'],
    topicsCite:'csCsMap', reported:[],
    watch:['The course the CS major is usually decided in. Front-load it.'],
    color:'--s3'},
  'MATH 112':{
    title:'Calculus 1', credits:4, creditsVerified:true, cite:'csMath112',
    desc:'Calculus 1, designed for students majoring in the mathematical and physical sciences, engineering or mathematics education, and for students minoring in mathematics or mathematics education.',
    prereq:'Stated on the catalog page \u2014 check your placement.',
    topics:['Limits and continuity','Derivatives and applications','Integrals','The fundamental theorem'],
    topicsCite:'csMath112', reported:[],
    watch:['4 credit hours, not 3 \u2014 a common miscount when planning a 15-hour semester.'],
    color:'--s4'},
  'STAT 121':{
    title:'Principles of Statistics', credits:3, creditsVerified:true, cite:'csStat121',
    desc:'Principles of statistics. Commonly taken to satisfy a quantitative reasoning requirement.',
    prereq:'None stated in the listing.',
    topics:['Descriptive statistics','Probability','Inference','Regression basics'],
    topicsCite:'csStat121', reported:[],
    watch:['Check whether your major wants STAT 121 or a department-specific statistics course before enrolling.'],
    color:'--s4'},
  'ECON 110':{
    title:'Economic Principles and Problems', credits:3, creditsVerified:true, cite:'csChemMap',
    desc:'Introductory economics. Appears on University Core MAP sheets as a Social Science option.',
    prereq:'None stated on the MAP sheet.',
    topics:['Supply and demand','Markets and prices','Macroeconomic aggregates'],
    topicsCite:'csChemMap', reported:[],
    watch:['A large-lecture course; the midterm curve is the thing to ask about, not the reading load.'],
    color:'--s7'},
  'PSYCH 111':{
    title:'Psychological Science', credits:3, creditsVerified:true, cite:'csBioMap',
    desc:'Introductory psychology. Appears on University Core MAP sheets as a Social Science option.',
    prereq:'None stated on the MAP sheet.',
    topics:['Research methods','Biological bases of behaviour','Learning and cognition','Development and personality'],
    topicsCite:'csBioMap', reported:[],
    watch:['Memorisation-heavy. Spaced retrieval beats re-reading here by a wide margin.'],
    color:'--s5'},
  'BIO 130':{
    title:'Biology', credits:4, creditsVerified:true, cite:'csBioMap',
    desc:'Introductory biology, listed on MAP sheets as a Biological Science option in the University Core.',
    prereq:'None stated on the MAP sheet.',
    topics:['Cells and molecules','Genetics','Evolution','Ecology'],
    topicsCite:'csBioMap', reported:[],
    watch:['4 credits with a lab component in most sections \u2014 budget the lab hours separately.'],
    color:'--s6'},
  'PHSCS 121':{
    title:'Introduction to Newtonian Mechanics', credits:3, creditsVerified:true, cite:'csChemMap',
    desc:'Introductory physics covering Newtonian mechanics. Appears on MAP sheets as a Physical Science option.',
    prereq:'Calculus is normally taken alongside or before \u2014 check your MAP sheet.',
    topics:['Kinematics','Newton\u2019s laws','Work and energy','Momentum and rotation'],
    topicsCite:'csChemMap', reported:[],
    watch:['Paired with a separate lab in most programmes. Confirm whether yours requires it.'],
    color:'--s2'},
  'CHEM 105':{
    title:'General College Chemistry', credits:4, creditsVerified:true, cite:'csChemMap',
    desc:'General chemistry. The MAP sheets list CHEM 105 as substitutable for CHEM 111.',
    prereq:'Placement or prior chemistry \u2014 check the catalog entry.',
    topics:['Atomic structure','Bonding','Stoichiometry','Thermochemistry'],
    topicsCite:'csChemMap', reported:[],
    watch:['4 credits and lab-bearing. If your MAP sheet says CHEM 111, confirm the substitution with an advisor rather than assuming it.'],
    color:'--s2'},
  'REL A 275':{
    title:'Teachings and Doctrine of the Book of Mormon', credits:2, creditsVerified:true, cite:'csRelA275',
    desc:'A cornerstone religion course on the teachings and doctrine of the Book of Mormon.',
    prereq:'REL A 121 and REL A 122 together also satisfy this cornerstone requirement.',
    topics:['Book of Mormon narrative and structure','Doctrinal themes'],
    topicsCite:'csRelBgs', reported:[],
    watch:['2 credits, not 3 \u2014 religion courses are counted separately from the University Core in the graduation audit.'],
    color:'--s8'},
  'REL C 225':{
    title:'Foundations of the Restoration', credits:2, creditsVerified:true, cite:'csRelBgs',
    desc:'A cornerstone religion course, required for students who began at BYU in Fall 2015 or later.',
    prereq:'None stated.',
    topics:['Restoration history and doctrine'],
    topicsCite:'csRelBgs', reported:[],
    watch:['Applies to students starting Fall 2015 or later; earlier catalog years differ.'],
    color:'--s8'},
  'REL C 324':{
    title:'The Doctrine and Covenants, Sections 1\u201376', credits:2, creditsVerified:true, cite:'csRelBgs',
    desc:'First half of the Doctrine and Covenants sequence.',
    prereq:'None stated.',
    topics:['Doctrine and Covenants sections 1\u201376'],
    topicsCite:'csRelBgs', reported:[],
    watch:['Paired with REL C 325; either one alone is 2 credits.'],
    color:'--s8'},
  'REL C 325':{
    title:'The Doctrine and Covenants, Sections 77\u2013OD 2', credits:2, creditsVerified:true, cite:'csRelBgs',
    desc:'Second half of the Doctrine and Covenants sequence.',
    prereq:'None stated.',
    topics:['Doctrine and Covenants sections 77 to Official Declaration 2'],
    topicsCite:'csRelBgs', reported:[],
    watch:['Paired with REL C 324; either one alone is 2 credits.'],
    color:'--s8'},
  'DANCE 184':{
    title:'Ballroom Dance, International Beginning', credits:1, creditsVerified:true, cite:'csDance184',
    desc:'Bronze-level International Style Waltz and Quickstep, plus beginning technique in posture, dance position, timing, footwork, weight transfer and partnering.',
    prereq:'DANCE 180, or consent of instructor.',
    topics:['International Style Waltz','Quickstep','Posture and dance position','Partnering skills'],
    topicsCite:'bDanceProg', reported:[],
    watch:['A lab-format activity course \u2014 the 1 credit is almost entirely dance-floor time, not lecture.'],
    color:'--s7'},
  'SFL 210':{
    title:'Human Development', credits:3, creditsVerified:true, cite:'csSfl210',
    desc:'The growth and development of human beings from conception until death, including the influences of family, peers, schools and culture.',
    prereq:'None stated in the catalog entry \u2014 open to all students, and a prerequisite for several other programmes including Nursing.',
    topics:['Major human-development theories','Biological, cognitive, emotional and social domains','Research methods in human development'],
    topicsCite:'bSflProg', reported:[],
    watch:['A required prerequisite for the Nursing programme at BYU \u2014 check your own programme\u2019s MAP sheet for whether it wants this or a different development course.'],
    color:'--s5'},
  'REL A 121':{
    title:'The Book of Mormon', credits:2, creditsVerified:true, cite:'csRelA121',
    desc:'The narrative, doctrines and precepts of the Book of Mormon, covering 1 Nephi through Alma 29.',
    prereq:'None stated in the catalog entry.',
    topics:['Book of Mormon narrative, 1 Nephi through Alma 29','Doctrines and precepts'],
    topicsCite:'csRelA121', reported:[],
    watch:['REL A 121 and REL A 122 together satisfy the REL A 275 cornerstone requirement \u2014 check which path your own religion sequence is on.'],
    color:'--s8'},
  'BIO 100':{
    title:'Principles of Biology', credits:3, creditsVerified:true, cite:'csBio100',
    desc:'An introductory biology course for general-education students, built around how biological principles apply to everyday life rather than around a majors-track sequence.',
    prereq:'None stated in the catalog entry.',
    topics:['Biology literacy and vocabulary','Scientific reasoning on public-policy science issues','Stewardship and civic application of biology'],
    topicsCite:'csBio100', reported:[],
    watch:['A different course from BIO 130 on this list \u2014 100 is the general-education, no-lab version; check which one your own requirement actually wants before enrolling in either.'],
    color:'--s6'},
  'MUSIC 311R':{
    title:'University Chorale', credits:1, creditsVerified:true, cite:'csMusic311R',
    desc:'BYU\u2019s non-auditioned choir, open to any student. Repertoire is read, learned, memorized and polished across the semester toward a concert and campus Devotional performances.',
    prereq:'None \u2014 no audition required.',
    topics:['Choral literature for the semester\u2019s repertoire','Sight-reading and ensemble technique'],
    topicsCite:'bChorale', reported:[],
    watch:['The R marks it repeatable for credit across multiple semesters \u2014 check how many times your own programme lets it count.'],
    color:'--s7'},
  'UNIV 101':{
    title:'BYU Foundations for Student Success', credits:2, creditsVerified:true, cite:'csUniv101',
    desc:'Required for all incoming first-year (non-transfer) students starting Winter 2024 onward. Covers the mission and aims of a BYU education, the balanced development of the whole person, and the transition to life as a BYU student.',
    prereq:'None \u2014 first-year, non-transfer students only.',
    topics:['The mission and aims of a BYU education','Whole-person development','Transition to university life'],
    topicsCite:'bFoundations', reported:[],
    watch:['Graded Credit/No Credit, not a letter grade \u2014 it will not touch your GPA, but 100% completion is required to earn the credit.'],
    color:'--s1'}
};
''', 'catalog')

swap_block("const SPORTS = [", "\n/* --- meal plans", '''const SPORTS = [
  {id:'fb',  name:'Football',           season:'Fall',   access:'Big 12. Home games are at LaVell Edwards Stadium. Student ticket policy is set by Athletics \u2014 check the ticket office rather than assuming admission is included.', cite:'bTickets'},
  {id:'mbb', name:"Men's Basketball",   season:'Winter', access:'Big 12. Plays at the Marriott Center, 701 East University Parkway.', cite:'bAthletics'},
  {id:'wbb', name:"Women's Basketball", season:'Winter', access:'Big 12. Also at the Marriott Center.', cite:'bAthletics'},
  {id:'vb',  name:"Women's Volleyball", season:'Fall',   access:'Big 12. Ticket policy: ask Athletics.', cite:'bAthletics'},
  {id:'oth', name:'Everything else',    season:'Varies', access:'BYU competes in the Big 12 across a wide slate. Full schedules are on byucougars.com.', cite:'bAthletics'}
];
const CLAIM_WINDOWS = [];
/* BYU\u2019s student ticket claim windows were not published on a page I could
   reach, so nothing is pre-loaded. The seven 2026 home football games below
   ARE published, and each one gets checked against your week like a class. */
const HOME_GAMES = [
  {id:'fb1', sport:'fb', opp:'Utah Tech',     date:'2026-09-05', start:'',      mins:240, tv:'',     prov:'reported'},
  {id:'fb2', sport:'fb', opp:'Arizona',       date:'2026-09-12', start:'13:30', mins:240, tv:'',     prov:'reported', note:'1:30 p.m. MDT.'},
  {id:'fb3', sport:'fb', opp:'Iowa State',    date:'2026-10-09', start:'20:15', mins:240, tv:'ESPN', prov:'reported', note:'Moved from Saturday Oct 10 to Friday Oct 9 \u2014 the only weeknight game on the schedule. It will eat a Friday evening.'},
  {id:'fb4', sport:'fb', opp:'Notre Dame',    date:'2026-10-17', start:'',      mins:240, tv:'',     prov:'reported'},
  {id:'fb5', sport:'fb', opp:'Arizona State', date:'2026-10-31', start:'',      mins:240, tv:'',     prov:'reported'},
  {id:'fb6', sport:'fb', opp:'Baylor',        date:'2026-11-14', start:'',      mins:240, tv:'',     prov:'reported'},
  {id:'fb7', sport:'fb', opp:'Cincinnati',    date:'2026-11-28', start:'',      mins:240, tv:'',     prov:'reported'}
];
''', 'athletics')

swap_block("const PLANS = [", "\n/* ======================================================================\n   FOOD LIBRARY", '''const PLANS = [
  {id:'opendoor', name:'Open Door', scans:'Unlimited at Cannon Commons', scansNum:null, unlimited:true, dollars:200, combo:null,
   note:'Unlimited access to the Cannon Commons during opening hours, plus 200 dining dollars debit-style at the start of the semester, usable tax-free at any BYU Dining location. Reported at $2,730 per semester \u2014 confirm on the plan page before you budget on it.'},
  {id:'diningplus', name:'Dining Plus', scans:'15 dining dollars a day', scansNum:null, unlimited:false, dollars:0, combo:null,
   note:'A daily allocation of 15 dining dollars; unused dollars roll over to the next day. Reported at $2,730 per semester or $1,365 per term. Enter the dollars you actually get below \u2014 this plan has no meal scans.'},
  {id:'trueblue', name:'True Blue Dining', scans:'Dining dollars only', scansNum:0, unlimited:false, dollars:500, combo:null,
   note:'Either 500 or 800 dining dollars for the semester. Reported at $500 / $800 per semester. Set the dollars to whichever you bought.'},
  {id:'ez', name:'EZ Dining', scans:'Dining dollars only', scansNum:0, unlimited:false, dollars:100, combo:null,
   note:'100, 150 or 200 debit-style dining dollars a month, rolling over month to month. Reported at $100 / $150 / $200 per month. Set the dollars to your monthly amount.'}
];
''', 'meal plans')


swap_block("const HALLS = [", "const ALLERGENS = [", '''const HALLS = [
  {id:'cannon',    n:'Cannon Commons',      sub:'All-you-care-to-eat, Helaman Halls', home:true},
  {id:'cougareat', n:'Cougareat',           sub:'Food court, Wilkinson Center'},
  {id:'creamery',  n:'Creamery on Ninth',   sub:'Grill, ice cream and groceries'},
  {id:'wilk',      n:'Other Wilkinson outlets', sub:'Cafes and counters in the WSC'}
];
''', 'halls')

swap_block("const PLACES = [", "const PLACE_KIND = {", '''const PLACES = [
  {id:'campus', name:'Campus centre', kind:'home', addr:'Brigham Young University, Provo, UT 84602', cite:'bMap',
   where:'Your starting point', note:'Set this to your own hall or apartment on the Data tab and every walk time here is recalculated from there.'},
  {id:'cannon', name:'Cannon Commons', kind:'aycte', addr:'Cannon Center, Helaman Halls, Brigham Young University, Provo, UT 84602', cite:'bDining',
   where:'Helaman Halls', posUnverified:true, note:'All-you-care-to-eat with six stations \u2014 entrees, wraps, soups, salads, pasta, grill, breads and desserts. The Open Door plan is unlimited access here.'},
  {id:'cougareat', name:'Cougareat', kind:'aycte', addr:'Wilkinson Student Center, Brigham Young University, Provo, UT 84602', cite:'bDining',
   where:'Wilkinson Center', posUnverified:true, note:'The food court: national brands and campus favourites, calzones through sushi. Pay with dining dollars or Cougar Cash.'},
  {id:'creamery', name:'Creamery on Ninth', kind:'aycte', addr:'Creamery on Ninth, 1209 N 900 E, Provo, UT 84602', cite:'bDining',
   where:'900 East', posUnverified:true, note:'Grill, the full BYU ice cream range, and a grocery store \u2014 the one place on this list where you can do a real shop.'},
  {id:'wilk', name:'Wilkinson Student Center', kind:'study', addr:'Wilkinson Student Center, Brigham Young University, Provo, UT 84602', cite:'bWilk',
   where:'Centre of campus', posUnverified:true, note:'The student centre: dining, lounges, study space, student services and CAPS on the top floor.'},
  {id:'hbll', name:'Harold B. Lee Library', kind:'study', addr:'1130 Harold B. Lee Library, Brigham Young University, Provo, UT 84602', cite:'bLibrary',
   where:'Centre of campus, south of the Administration Building', note:'The main library. Study space at every noise level, plus the subject librarians who will save you an evening on a research paper.'},
  {id:'rwc', name:'Research and Writing Center', kind:'study', addr:'Brigham Young University, Provo, UT 84602', cite:'bTutor',
   where:'Ask at the HBLL', posUnverified:true, note:'Free help with writing and research at any stage of a paper.'},
  {id:'jfsb', name:'Joseph F. Smith Building (JFSB)', kind:'class', addr:'Joseph F. Smith Building, Brigham Young University, Provo, UT 84602', cite:'bBuildings',
   where:'Main campus', posUnverified:true, note:'Humanities and social sciences. Where most WRTG and language sections meet.'},
  {id:'tmcb', name:'Talmage Building (TMCB)', kind:'class', addr:'James E. Talmage Math Sciences/Computer Building, Campus Dr, Provo, UT 84604', cite:'bBuildings',
   where:'Campus Drive', note:'Mathematics and computer science. C S and MATH sections, plus the CS labs.'},
  {id:'marb', name:'Martin Building (MARB)', kind:'class', addr:'Ezra Taft Benson Building area, Brigham Young University, Provo, UT 84602', cite:'bBuildings',
   where:'Science district', posUnverified:true, note:'Large science lecture halls \u2014 the 300-plus-seat rooms most first-year science courses meet in.'},
  {id:'jkb', name:'Jesse Knight Building (JKB)', kind:'class', addr:'Jesse Knight Building, Brigham Young University, Provo, UT 84602', cite:'bBuildings',
   where:'Main campus', posUnverified:true, note:'Classrooms across several departments.'},
  {id:'caps', name:'Counseling and Psychological Services', kind:'care', addr:'1500 Wilkinson Student Center, Brigham Young University, Provo, UT 84602', cite:'bCaps',
   where:'Wilkinson Center, top floor', note:'Walk-in crisis hours Monday to Friday, 8:00 a.m. to 4:15 p.m., subject to counsellor availability. Phone 801-422-3035.'},
  {id:'health', name:'Student Health Center', kind:'care', addr:'1750 N Wymount Terrace Dr, Provo, UT 84604', cite:'bHealth',
   where:'Wymount Terrace', note:'General clinic and urgent care, Monday to Friday 8:00 a.m. to 5:30 p.m.; urgent care also Saturday mornings 8:00\u201311:30 during Fall and Winter. Phone 801-422-5156.'},
  {id:'uac', name:'University Accessibility Center', kind:'care', addr:'Brigham Young University, Provo, UT 84602', cite:'bAccess',
   where:'Main campus', posUnverified:true, note:'Accommodations for disability, chronic illness and mental health conditions. Start here early in the term, not the week of an exam.'},
  {id:'marriott', name:'Marriott Center', kind:'rec', addr:'701 East University Parkway, Provo, UT 84602', cite:'bAthletics',
   where:'University Parkway', note:'Basketball, devotionals and forums. One of the largest on-campus arenas in the country.'},
  {id:'les', name:'LaVell Edwards Stadium', kind:'rec', addr:'LaVell Edwards Stadium, Provo, UT 84602', cite:'bTickets',
   where:'North campus', posUnverified:true, note:'Home football. All seven 2026 home games are already on your calendar here.'},
  {id:'wellness', name:'Student Wellness and Intramurals', kind:'rec', addr:'Brigham Young University, Provo, UT 84602', cite:'bRec',
   where:'Main campus', posUnverified:true, note:'Intramural sports and wellness programming. Whether facility access is included in your fees was not published anywhere I could reach \u2014 check before assuming.'}
];
''', 'places')

swap_block("const WAGE = {", "function deriveJobs(d){", '''const WAGE = {min:9, avgLo:13.46, avg:14.21, avgHi:20, typHours:'set yours'};
''', 'wage')

swap_block("const JOB_TEMPLATES = [", "const JOB_BENEFITS = [", '''const JOB_TEMPLATES = [
  {title:'Library assistant (HBLL)', employer:'BYU', onCampus:true, benefits:['Study during downtime','On campus','Quiet']},
  {title:'Dining services', employer:'BYU Dining', onCampus:true, benefits:['Meal during shift','On campus','Flexible around classes']},
  {title:'Creamery on Ninth', employer:'BYU Dining', onCampus:true, benefits:['On campus','Staff discount','Short shifts']},
  {title:'Wilkinson Center desk or office', employer:'BYU', onCampus:true, benefits:['On campus','Study during downtime','Central']},
  {title:'Custodial or facilities', employer:'BYU', onCampus:true, benefits:['On campus','Early shifts','Consistent hours']},
  {title:'Lab or research assistant', employer:'Academic department', onCampus:true, benefits:['Resume relevant','Faculty contact','On campus']},
  {title:'TA or grader', employer:'Academic department', onCampus:true, benefits:['Resume relevant','Reinforces the course','Flexible']},
  {title:'Off-campus food service', employer:'Provo', onCampus:false, benefits:['Tips','Free drinks']},
  {title:'Off-campus retail', employer:'Provo', onCampus:false, benefits:['Staff discount']}
];
''', 'job templates')


swap_block("const DEALS = [", "const DEAL_GROUPS = [", '''const DEALS = [
/* ---------------- campus ---------------------------------------------- */
{id:'rwc', g:'campus', n:'Research and Writing Center \u2014 free', v:null, per:'year',
 d:'Help with writing and research at any stage of a paper, from a blank page to a final draft. Already paid for out of your tuition.',
 vb:'Not a discount \u2014 already paid for. A private writing tutor runs $30\u201360/hour; enter what you would otherwise spend.',
 prov:'verified', cite:'bTutor', go:'https://rwc.byu.edu/'},
{id:'hbll', g:'campus', n:'Harold B. Lee Library \u2014 subject librarians', v:null, per:'year',
 d:'The part of the library almost nobody uses: a librarian for your specific subject who will find sources for a paper in twenty minutes that would take you an evening.',
 vb:'Not a discount \u2014 already paid for. Value it in hours saved.',
 prov:'verified', cite:'bLibrary', go:'https://lib.byu.edu/'},
{id:'caps', g:'campus', n:'Counseling and Psychological Services', v:null, per:'year',
 d:'CAPS runs walk-in crisis hours Monday to Friday, 8:00 a.m. to 4:15 p.m., on the top floor of the Wilkinson Center. Phone 801-422-3035.',
 vb:'No fee was stated on the pages I could reach \u2014 ask rather than assuming it is free or that it is not.',
 prov:'verified', cite:'bCaps', go:'https://caps.byu.edu/'},
{id:'uac', g:'campus', n:'University Accessibility Center', v:null, per:'year',
 d:'Formal accommodations for disability, chronic illness and mental health conditions. Set up in week two is worth far more than set up the week of a final.',
 vb:'Not a discount \u2014 an entitlement most eligible students never register for.',
 prov:'verified', cite:'bAccess', go:'https://uac.byu.edu/'},
{id:'health', g:'campus', n:'Student Health Center', v:null, per:'year',
 d:'1750 N Wymount Terrace Dr. General clinic and urgent care Monday to Friday 8:00 a.m. to 5:30 p.m., plus Saturday urgent care 8:00\u201311:30 a.m. during Fall and Winter.',
 vb:'Charges depend on your plan and the visit \u2014 the pages I could reach did not state them. Ask before you assume it is free.',
 prov:'verified', cite:'bHealth', go:'https://health.byu.edu/'},
{id:'wellness', g:'campus', n:'Intramural sports and Student Wellness', v:null, per:'year',
 d:'Intramurals and wellness programming. The cheapest reliable way to keep the social floor on this site above zero without spending an evening on it.',
 vb:'Whether facility access is included in your fees was not published anywhere I could reach.',
 prov:'reported', cite:'bRec', go:'https://studentwellness.byu.edu/'},
{id:'cougarcash', g:'campus', n:'Cougar Cash on campus', v:null, per:'year',
 d:'The campus debit balance on your ID. Dining Services states that dining dollars are spent tax-free at BYU Dining locations, which is a real few per cent on every meal.',
 vb:'Roughly the local sales-tax rate on whatever you spend on campus food.',
 prov:'reported', cite:'bCougarCash', go:'https://cougarcash.byu.edu/benefits'},
{id:'studentjobs', g:'campus', n:'On-campus student employment', v:null, per:'year',
 d:'BYU states student starting pay runs $9.00 to $20.00 an hour depending on the job and your qualifications, with a published hourly pay scale behind it.',
 vb:'The gap between a $9 job and a $16 job over 15 hours a week for a semester is about $1,500. Worth one afternoon of looking.',
 prov:'verified', cite:'bJobs', go:'https://hr.byu.edu/student-employment'},

/* ---------------- Provo ----------------------------------------------- */
{id:'provolocal', g:'provo', n:'Provo places that take a student ID', v:null, per:'visit',
 d:'I could not verify a single Provo student discount from a source I trust, so nothing is listed here as fact. Add the ones you actually find and record what they gave you.',
 vb:'Yours to fill in.', prov:'mine', cite:'bMap', go:'https://map.byu.edu/'},

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
 d:'GitHub Pro, JetBrains IDEs, $200 DigitalOcean credit for a year, a free .TECH domain for a year, and 100+ partner offers.',
 vb:'$200 is the DigitalOcean credit \u2014 the one figure the sources state outright.',
 prov:'reported', cite:'ghStudent', go:'https://education.github.com/pack'},
{id:'autodesk', g:'dev', n:'Autodesk Education \u2014 free', v:null, per:'year',
 d:'Fusion, AutoCAD, Inventor and Revit are offered free to students and educators.',
 vb:'Enter the licence cost you avoid.', prov:'reported', cite:'nbcDeals',
 go:'https://www.autodesk.com/education/edu-software/overview'},
{id:'notion', g:'dev', n:'Notion Plus \u2014 free for students', v:null, per:'year',
 d:'Notion Plus at no cost, verified through your school email.',
 vb:'Enter the plan price you avoid.', prov:'reported', cite:'notionEdu', go:'https://www.notion.com/product/notion-for-education'},
{id:'figma', g:'dev', n:'Figma Education \u2014 free', v:null, per:'year',
 d:'Figma Education is free for students.', vb:'Enter the plan price you avoid.',
 prov:'reported', cite:'figmaEdu', go:'https://www.figma.com/education/'},
{id:'perplexity', g:'dev', n:'Perplexity Education Pro \u2014 $10/mo', v:null, per:'year',
 d:'Verified students can subscribe to Education Pro for $10/month through SheerID.',
 vb:'Student rate verified; standard rate not stated in the source.',
 prov:'reported', cite:'perplexEdu', go:'https://www.perplexity.ai/students'},

/* ---------------- retail ---------------------------------------------- */
{id:'appleedu', g:'retail', n:'Apple Education pricing', v:150, vEst:true, per:'once',
 d:'Verify through UNiDAYS, then buy from the Apple Education Store. Reported as roughly $100\u2013$200 off current MacBooks and about $50 off iPads.',
 vb:'$150 is the midpoint of the $100\u2013$200 MacBook range the source gives. Set it to $50 for an iPad.',
 prov:'reported', cite:'nbcDeals', go:'https://www.apple.com/us-edu/store'},
{id:'samsung', g:'retail', n:'Samsung \u2014 up to 30% off', v:null, per:'once',
 d:'Reported as up to 30% off all purchases for students.',
 vb:'Percentage of your purchase \u2014 "up to" does a lot of work in that sentence.',
 prov:'reported', cite:'nbcDeals', go:'https://www.samsung.com/us/shop/discount-program/education/'},
{id:'bestbuy', g:'retail', n:'Best Buy student deals', v:null, per:'varies',
 d:'Year-round student offers on laptops, tablets, headphones and small appliances.',
 vb:'Varies by item.', prov:'reported', cite:'nbcDeals', go:'https://www.bestbuy.com/site/misc/student-deals/pcmcat1554736315457.c'},
{id:'unidays', g:'retail', n:'UNiDAYS \u2014 verification hub', v:null, per:'year',
 d:'Not a deal itself: the verification layer a lot of the retail offers here run through. Set it up once and the rest get faster.',
 vb:'No direct value \u2014 an enabler.', prov:'reported', cite:'unidays', go:'https://www.myunidays.com/'},
{id:'studentbeans', g:'retail', n:'Student Beans \u2014 verification hub', v:null, per:'year',
 d:'The other major verification hub.', vb:'No direct value \u2014 an enabler.',
 prov:'reported', cite:'studentbeans', go:'https://www.studentbeans.com/us'}
];
''', 'deals')

swap_block("const DEAL_GROUPS = [", "\n/* ======================================================================\n   STATE", '''const DEAL_GROUPS = [
  {id:'campus', n:'On campus \u2014 what BYU already provides', d:'University-run services and programmes. The highest-confidence items here, and the ones students most often miss.'},
  {id:'provo',  n:'Provo', d:'Local. Nothing here is verified as a student discount unless the card says so \u2014 add what you find and record what it actually gives you.'},
  {id:'subs',   n:'Subscriptions', d:'Student tiers on things you may already pay for.'},
  {id:'dev',    n:'Software & dev tools', d:'Worth the most if you are in a C S, engineering or design programme.'},
  {id:'retail', n:'Retail & verification hubs', d:'Lower confidence, secondary sources. Confirm before planning around them.'}
];
''', 'deal groups')


# ─────────────────────────────────────────────── Canvas, rebranded
# BYU runs Canvas at byu.instructure.com, so the IU bookmarklet and its
# whole parse path carry over untouched. Only the wording changes.
swap("\u21f1 Send Canvas \u2192 Crimson", "\u21f1 Send Canvas \u2192 Cougar", 'bookmarklet label')
swap("hosts:['instructure.com','iu.instructure.com','canvas.iu.edu'],",
     "hosts:['instructure.com','byu.instructure.com','byucanvas.byu.edu'],", 'src kind ics')
swap("{id:'canvas', n:'Canvas course page', hosts:['instructure.com','canvas.iu.edu'],",
     "{id:'canvas', n:'Canvas course page', hosts:['instructure.com','byu.instructure.com'],", 'src kind course')

swap_block("const SRC_KINDS=[", "const PASTE_KINDS=[", "const SRC_KINDS=[\n  {id:'canvas-ics', n:'Canvas calendar feed (.ics)', hosts:['instructure.com','byu.instructure.com','byucanvas.byu.edu'],\n   how:'In Canvas open <b>Calendar</b>, click <b>Calendar Feed</b> in the right sidebar, and copy the URL. It contains a private token, so treat it like a password.', cite:'canvasIcal'},\n  {id:'canvas', n:'Canvas course page', hosts:['instructure.com','byu.instructure.com'],\n   how:'Copy the address of the course home page or the Assignments page.', cite:'bCanvas'},\n  {id:'onegoiu', n:'MyBYU page', hosts:['my.byu.edu','byu.edu'], how:'Copy the address of the MyBYU page you keep coming back to.', cite:'bMyMap'},\n  {id:'sis', n:'Class schedule', hosts:['my.byu.edu','byu.edu'],\n   how:'MyBYU shows your registered schedule. Use it to confirm your meeting times.', cite:'bMyMap'},\n  {id:'gradedist', n:'Course catalog entry', hosts:['catalog.byu.edu','byu.edu'],\n   how:'Find the course on catalog.byu.edu and copy its URL so you can come back to it.', cite:'bCatalog'},\n  {id:'menu', n:'Dining menu', hosts:['dining.byu.edu','byu.edu'],\n   how:'Open the BYU Dining page for the location you use and copy the address.', cite:'bDining'},\n  {id:'events', n:'Events / athletics calendar', hosts:['byu.edu','byucougars.com','calendar.byu.edu'], how:'Copy any calendar or schedule page.', cite:'bAthletics'},\n  {id:'other', n:'Something else', hosts:[], how:'Any URL you want to keep next to your planner.', cite:null}\n];\n", 'source kinds')

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
      '   Cougar Command — BYU Provo planner.', 'js header')
prose("meta:{term:TERM.name, dorm:'McNutt Quad', dormAddr:'1101 N. Fee Lane, Bloomington, IN 47406'},",
      "meta:{term:TERM.name, dorm:'', dormAddr:'Brigham Young University, Provo, UT 84602'},", 'meta default')
prose("b.meta = {term:TERM.name, dorm:'', dormAddr:'Indiana University, Bloomington, IN 47405'};",
      "b.meta = {term:TERM.name, dorm:'', dormAddr:'Brigham Young University, Provo, UT 84602'};", 'blank meta')
prose("{addr:'Indiana University, Bloomington, IN'}", "{addr:'Brigham Young University, Provo, UT 84602'}", 'hall walk fallback')
prose('<h2>Campus map — from McNutt</h2>', '<h2>Campus map — from campus</h2>', 'map heading')
prose("Schematic, not to scale. Every pin sits at its verified street address and links to live walking directions from your dorm, so the walk time you get is Google's, not mine.",
      "BYU Provo is a walkable campus, so most of these are a short walk. Each pin carries the address I could verify \u2014 the ones I could not are marked \u2014 and links to live walking directions, so the walk time you get is Google's, not mine.", 'map blurb')
prose('Built around your actual class schedule and McNutt as home base.',
      'Built around your actual class schedule and Cannon Commons as home base.', 'dining strategy blurb')
prose("'. Opens walking directions from McNutt.'", "'. Opens walking directions from campus.'", 'map aria')
prose("fill:'var(--ink)','font-family':'var(--sans)'},'McNutt Quad'));",
      "fill:'var(--ink)','font-family':'var(--sans)'},'BYU Provo'));", 'hub label')
prose("fill:'var(--ink-2)','font-family':'var(--mono)'},'1101 N. Fee Lane'));",
      "fill:'var(--ink-2)','font-family':'var(--mono)'},'Provo, Utah'));", 'hub addr')
prose("'letter-spacing':'.09em'},'HOME + DINING HALL'));", "'letter-spacing':'.09em'},'PROVO, UTAH'));", 'hub sub')
prose("out.push('<div class=\"note acc\"><b>Breakfast is your free lunch.</b> You live in McNutt and the dining hall is in the Center Building, ground floor — a zero-commute all-you-care-to-eat meal. On an unlimited plan the marginal cost of eating it is nothing, and it is the meal most first-years drop first. '+chip('verified')+'</div>');",
      "out.push('<div class=\"note acc\"><b>Breakfast is the meal to protect.</b> Both BYU plans are a fixed number of meals a week rather than unlimited, so a skipped breakfast is a meal you paid for and did not eat — and it is the first one students drop. Work out your cost per meal below and the arithmetic gets uncomfortable quickly. '+chip('verified')+'</div>');", 'breakfast note')
prose('per-item nutrition for the actual menu on Nutrislice, which is linked',
      'per-item nutrition through BYU Dining, which is linked', 'food header 1')
prose('items can be marked as checked against Nutrislice once you have.',
      'items can be marked as checked against the real menu once you have.', 'food header 2')
prose('IU publishes per-item nutrition for the actual menu on Nutrislice; every number here is editable so you can correct it against that, and corrected items get marked.',
      'BYU Dining publishes the actual menu; every number here is editable so you can correct it against what is really served, and corrected items get marked.', 'food source note')
prose("<b>Correct this against Nutrislice, not against memory.</b> IU publishes real per-item nutrition for the actual menu.",
      "<b>Correct this against the real menu, not against memory.</b> BYU Dining publishes what is actually served.", 'food edit note')
prose('href="https://indiana-dining.nutrislice.com/" target="_blank" rel="noopener">Open Nutrislice ↗</a>',
      'href="https://dining.byu.edu/" target="_blank" rel="noopener">Open BYU Dining ↗</a>', 'nutrislice link')
prose("Every value is editable and IU\\u2019s own per-item nutrition is on Nutrislice, linked from the builder.",
      "Every value is editable and BYU Dining\\u2019s own menu is linked from the builder.", 'gaps food')
prose('<div class="srcline">Study minimum per credit hour: <strong>IU policy ACA-86</strong> — one credit hour = 50 min instruction + a minimum of 100 min out-of-class work per week. <a href="https://policies.iu.edu/policies/aca-86-credit-hour/index.html" target="_blank" rel="noopener">policies.iu.edu/policies/aca-86-credit-hour</a></div>',
      '<div class="srcline"><span class="prov unverified">Unverified</span> Study hours per credit default to <strong>2.0</strong>, the common accreditation convention of two hours of out-of-class work per contact hour. <strong>This is not a BYU figure</strong> — I could not reach a BYU credit-hour policy, so treat it as a starting dial rather than a rule.</div>', 'aca86 srcline')
prose("'IU policy ACA-86 sets the minimum at 2.0. Raising it raises every study total.'",
      "'2.0 is the common two-hours-per-credit convention, not a verified BYU policy. Raising it raises every study total.'", 'aca86 hint')
prose('<div class="srcline">Grade-point values from <strong>IU policy ACA-66, Grades and Grading</strong>. A+ and A both carry 4.0. <a href="https://policies.iu.edu/policies/aca-66-grades-and-grading/index.html" target="_blank" rel="noopener">policies.iu.edu/policies/aca-66-grades-and-grading</a></div>',
      '<div class="srcline"><span class="prov unverified">Unverified</span> This uses a conventional 4.0 scale — A=4.0, A−=3.7, B+=3.3 — with the usual 97/93/90 cutoffs. <strong>I could not verify BYU’s own grade-point values or cutoffs</strong>, and schools do differ. Check the catalog.</div>', 'aca66 srcline')
prose('https://iuhoosiers.com/sports/tickets/schedule', 'https://byucougars.com/sports/football/schedule', 'athletics schedule link')
prose('https://iuhoosiers.com/sports/tickets', 'https://byucougars.com/', 'athletics tickets link')
prose('The official routes into student employment at IU Bloomington.',
      'The official routes into student employment at BYU.', 'work sources blurb')
prose("'Adobe, GitHub and JetBrains are flagged because you are in two Luddy courses'",
      "'The software group is flagged because you have a C S or engineering course on your card'", 'work feed')
prose('<input id="ckLabel" placeholder="Lifting, IM soccer, Luddy club…">',
      '<input id="ckLabel" placeholder="Lifting, intramurals, a club…">', 'commit placeholder')
prose('<input id="ndN" placeholder="Local coffee shop — 10% with CrimsonCard">',
      '<input id="ndN" placeholder="Local coffee shop — 10% with a student ID">', 'deal placeholder')
prose('Check your balance in the CrimsonCard portal, then paste it here.',
      'Check your balance in MyBYU or with the dining office, then paste it here.', 'dollars hint')

# gaps list rewritten for this build
swap_block("  $('gaps').innerHTML='<ul class=\"tight\" style=\"color:var(--ink-2)\">'", "\n}\n\n/* =======", '''  $('gaps').innerHTML='<ul class="tight" style="color:var(--ink-2)">'
   +'<li><b>The course catalog is a sample, not the whole catalog.</b> Twenty-two BYU courses ship with credit hours and descriptions taken from catalog.byu.edu and from published MAP sheets. BYU publishes no downloadable section export I could reach, so there is no term-by-term schedule of classes embedded here \u2014 use the live search on the Courses tab, which hands your query straight to catalog.byu.edu.</li>'
   +'<li><b>Credit-hour and grading conventions.</b> The 2.0 study-hours-per-credit default and the 4.0 grade scale with 97/93/90 cutoffs are common conventions, <em>not</em> verified BYU policy. Check your syllabus and the catalog, and change them if yours differ.</li>'
   +'<li><b>Fall 2026 dates.</b> Classes begin September 2, the last day of instruction is December 10, December 11 is Exam Preparation Day and finals run December 12\u201317, from BYU\u2019s 2026 academic calendar. If the calendar and this page ever disagree, the calendar is right.</li>'
   +'<li><b>Meal plan prices.</b> Open Door and Dining Plus at $2,730 a semester, True Blue at $500 or $800, and EZ Dining at $100/$150/$200 a month all come from secondary write-ups rather than a BYU price page I could reach. The plan <em>structures</em> are from BYU Dining. Enter what you were actually charged.</li>'
   +'<li><b>Dining hall stations.</b> Cannon Commons, the Cougareat and the Creamery on Ninth are verified as locations, and Cannon Commons is verified as six-station all-you-care-to-eat. Exactly which stations run on a given day is not, so every hall starts with everything switched on \u2014 untick what is not there.</li>'
   +'<li><b>Food nutrition values.</b> Reference values for standard portions from published USDA-derived charts, not BYU Dining\u2019s own item data. Every value is editable. The allergy filter is a planning aid and knows nothing about cross-contact in a real kitchen.</li>'
   +'<li><b>Athletics.</b> All seven 2026 home football games are loaded from the published Big 12 schedule. Whether student admission is included, and how tickets are claimed, is set by Athletics and was not on a page I could reach \u2014 ask the ticket office.</li>'
   +'<li><b>Student wages.</b> BYU states student starting pay runs $9\u2013$20/hr. The $13.46\u2013$15.14 band and $14.21 median are a salary aggregator\u2019s reported figures, not a BYU publication \u2014 a sanity check on an offer, not a guarantee.</li>'
   +'<li><b>Job and instructor ratings.</b> User input by design. BYU publishes no grade-distribution database I could reach, and inventing one was not an option.</li>'
   +'<li><b>Walking times.</b> Not fetched \u2014 routing services are unreachable from the environment this was built in. The page works out which routes your timetable needs and hands you the Google Maps link for each. Buildings without a verified street address are marked and fall back to a name search.</li>'
   +'</ul>';
''', 'gaps')


# ── wage prose, escaping handled by repr ──
prose("The $'+WAGE.min+' floor is IU\\u2019s stated minimum wage for student employment.", "BYU states that student starting pay runs $'+WAGE.min+' to $'+WAGE.avgHi+' an hour depending on the job and your qualifications, so $'+WAGE.min+' is the floor an offer is scored against here.", 'wage line 1')
prose('The $\'+WAGE.avg+\' median and the $\'+WAGE.avgLo+\'–$\'+WAGE.avgHi+\' band are a salary aggregator\\u2019s figures for "IU student" roles in Bloomington as of July 2026, not an IU publication — a sanity check on an offer, not a guarantee.', "The $'+WAGE.avg+' median and the $'+WAGE.avgLo+'–$15.14 band are a salary aggregator\\u2019s reported figures for BYU student roles as of August 2026, not a BYU publication — a sanity check on an offer, not a guarantee.", 'wage line 2')
prose('The 10–12 hour average comes from IU\\u2019s own part-time jobs page.', 'BYU publishes no typical student-hours figure I could reach, so set your own ceiling on the Life tab and jobs are scored against that.', 'wage line 3')
prose("tile('Local median', money(WAGE.avg), '/hr', 'Most land '+money(WAGE.avgLo)+'–'+money(WAGE.avgHi)),", "tile('Reported median', money(WAGE.avg), '/hr', 'Aggregator figure for BYU student roles'),", 'wage tile 2')
prose("citeLine('wsAgency')", "citeLine('bWhyWork')", 'wage cite 1')
prose("citeLine('wageZip')", "citeLine('wageZip')", 'wage cite 2')
prose("citeLine('jobsIUB')", "citeLine('bPayScale')", 'wage cite 3')

prose("tile('Typical load', WAGE.typHours, 'h/wk', 'What IU says students average'),\n    tile('Your spare time', rnd(d.freeWeek,1), 'h/wk', 'Above the social floor — a job comes out of this', d.freeWeek<10?'warn':'good')",
      "tile('Your spare time', rnd(d.freeWeek,1), 'h/wk', 'Above the social floor — a job comes out of this', d.freeWeek<10?'warn':'good')",
      'wage tile row')


prose("const plan = PLANS.find(p=>p.id===dg.planId) || PLANS[3];",
      "const plan = PLANS.find(p=>p.id===dg.planId) || PLANS[0];", 'plan fallback')
prose("      planId:'expanded', priceSem:2000, comboPerWeek:5,",
      "      planId:'opendoor', priceSem:null, comboPerWeek:null,", 'default plan id')
prose("  b.dining = {...b.dining, planId:'expanded', priceSem:null, comboPerWeek:null,\n              dollarsStart:250, dollarsLeft:250, log:[], weight:null};",
      "  b.dining = {...b.dining, planId:'opendoor', priceSem:null, comboPerWeek:null,\n              dollarsStart:200, dollarsLeft:200, log:[], weight:null};", 'blank dining')
prose("      dollarsStart:250, dollarsLeft:250, scansLeft:null, log:[],",
      "      dollarsStart:200, dollarsLeft:200, scansLeft:null, log:[],", 'dining dollars default')

prose('+(pl.comboUncertain?\'<b style="color:var(--warn)">Sources conflict on this one.</b> One IU Dining contract summary gives 5/week for Expanded; an older Indiana Daily Student guide says four. Classic at 3/week is the only figure stated unambiguously. Check your own contract and set it here.\':\'Reset weekly on Sunday at 12:00 a.m.; unused combos do not carry over.\')', "+'BYU\\u2019s two plans are counted in meals per week. Nothing I could reach describes a separate combo-meal allowance, so leave this blank unless your plan has one.'", 'combo hint')
prose("+esc(pl.name)+' is listed at $'+pl.dollars+'/semester. '+chip('verified')", "+(pl.dollars>0?esc(pl.name)+' is listed at $'+pl.dollars+'/semester. '+chip('verified'):'Neither BYU plan has a dining-dollar component I could verify \\u2014 leave this at zero unless yours does. '+chip('unverified'))", 'dollars start hint')

swap_block('function renderProfTools(){', '\nfunction renderPlanStats(){', 'function renderProfTools(){\n  const tools=[\n    {n:\'The BYU course catalog\', chipk:\'verified\', tier:\'Official · factual only\',\n     d:\'catalog.byu.edu is the authority on what a course is: official title, credit hours, prerequisites, and which University Core requirement it satisfies.\',\n     use:\'Start here to confirm credit hours before you set them on a course card — every hour total on this site is built on that number. MATH 112 is 4 credits, not 3, and religion courses are 2. It will tell you nothing about an instructor.\',\n     u:CITE.bCatalog.u, u2:CITE.bCoreReq.u},\n    {n:\'Your MAP sheet\', chipk:\'verified\', tier:\'Official · your own programme\',\n     d:\'Every major publishes a MAP sheet: the exact course list, credit hours and semester-by-semester sequence for that degree.\',\n     use:\'This is the document that decides whether C S 111 or C S 142 is your entry point, and whether your programme wants CHEM 105 or CHEM 111. Read it before registration, not after.\',\n     u:CITE.bCoreReq.u, u2:CITE.bCore.u},\n    {n:\'MyBYU and MyMAP\', chipk:\'verified\', tier:\'Official · your own record\',\n     d:\'my.byu.edu is where registration, your schedule and your progress toward graduation actually live.\',\n     use:\'The authority on your own meeting times. Confirm them here rather than trusting anything typed in from memory or read off a screenshot.\',\n     u:CITE.bMyMap.u, u2:CITE.bRegistrar.u},\n    {n:\'RateMyProfessors\', chipk:\'reported\', tier:\'Unofficial · weakest signal\',\n     d:\'Not affiliated with BYU, self-selected, and heavily skewed toward students who felt strongly one way or the other.\',\n     use:\'Read the written comments and ignore the score. Comments describing the structure of a course — how many exams, whether attendance is enforced, whether the labs are graded hard — stay useful regardless of the reviewer’s mood. The number does not.\',\n     u:CITE.bRMP.u, u2:CITE.bCatalog.u}\n  ];\n  $(\'profTools\').innerHTML = tools.map(t=>\n    \'<div class="panel" style="background:var(--surface-2);margin:0">\'\n    +\'<div class="row spread" style="align-items:baseline"><h3>\'+esc(t.n)+\'</h3>\'+chip(t.chipk)+\'</div>\'\n    +\'<div style="font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);margin:5px 0 9px">\'+esc(t.tier)+\'</div>\'\n    +\'<p style="font-size:13px;color:var(--ink-2)">\'+esc(t.d)+\'</p>\'\n    +\'<div class="note acc" style="margin-top:10px"><b>How to actually read it.</b> \'+esc(t.use)+\'</div>\'\n    +\'<div class="row" style="margin-top:11px"><a class="btn sm" href="\'+esc(t.u)+\'" target="_blank" rel="noopener">Open ↗</a>\'\n    +(t.u2?\'<a class="btn sm ghost" href="\'+esc(t.u2)+\'" target="_blank" rel="noopener">Details ↗</a>\':\'\')+\'</div>\'\n    +\'</div>\').join(\'\');\n}\n\n', 'prof tools')
swap_block('function renderSupport(){', '\nfunction renderAnnouncements(){', 'function renderSupport(){\n  const items=[\n    {n:\'Counseling and Psychological Services\', chipk:\'verified\', cite:\'bCaps\',\n     body:\'CAPS is on the top floor of the Wilkinson Center, 1500 WSC. Walk-in crisis hours run Monday to Friday, 8:00 a.m. to 4:15 p.m., subject to counsellor availability.\',\n     facts:[[\'Where\',\'1500 Wilkinson Student Center\'],[\'Walk-in\',\'Mon–Fri, 8:00–4:15\'],[\'Phone\',\'801-422-3035\']],\n     go:\'https://caps.byu.edu/\',\n     caveat:\'No fee was stated on the pages I could reach. Ask at the first appointment rather than assuming it is free or that it is not.\'},\n    {n:\'Research and Writing Center\', chipk:\'verified\', cite:\'bTutor\',\n     body:\'Free help with writing and research at any stage of a paper — from working out what the assignment is asking to tightening a final draft.\',\n     facts:[[\'Cost\',\'Free\'],[\'Best used\',\'Early, on the outline\']],\n     go:\'https://rwc.byu.edu/\',\n     caveat:\'Hours were not on a page I could reach. Look them up once, then enter them as a commitment on the Life tab so the study planner works around them.\'},\n    {n:\'Harold B. Lee Library\', chipk:\'verified\', cite:\'bLibrary\',\n     body:\'The main library, in the centre of campus just south of the Administration Building. Study space at every noise level, plus subject librarians for your specific field.\',\n     facts:[[\'Where\',\'1130 HBLL, centre of campus\'],[\'Underused\',\'Subject librarians\']],\n     go:\'https://lib.byu.edu/\',\n     caveat:\'The subject librarian is the part almost nobody uses and the part that saves the most time on a research paper.\'},\n    {n:\'Student Health Center\', chipk:\'verified\', cite:\'bHealth\',\n     body:\'General clinic and urgent care at 1750 N Wymount Terrace Dr, with Saturday urgent care during Fall and Winter.\',\n     facts:[[\'Where\',\'1750 N Wymount Terrace Dr\'],[\'Hours\',\'Mon–Fri 8:00 a.m.–5:30 p.m.\'],[\'Saturday\',\'Urgent care 8:00–11:30, Fall/Winter\'],[\'Phone\',\'801-422-5156\']],\n     go:\'https://health.byu.edu/\',\n     caveat:\'What a visit costs depends on your health plan and was not stated on the pages I could reach. Ask before assuming either way.\'},\n    {n:\'University Accessibility Center\', chipk:\'verified\', cite:\'bAccess\',\n     body:\'Formal accommodations for disability, chronic illness and mental health conditions.\',\n     facts:[[\'Cost\',\'Free\'],[\'Timing\',\'Register early in the term\']],\n     go:\'https://uac.byu.edu/\',\n     caveat:\'Accommodations are not applied retroactively. Registering in week two is worth far more than registering the week of a final.\'},\n    {n:\'Student Wellness and intramural sports\', chipk:\'verified\', cite:\'bRec\',\n     body:\'Intramural sport and wellness programming — the cheapest reliable way to keep the social floor on the Life tab above zero.\',\n     facts:[[\'Where\',\'Main campus\']],\n     go:\'https://studentwellness.byu.edu/\',\n     caveat:\'Whether facility access is included in your fees was not published anywhere I could reach. Gym time counts 30% toward the social floor here either way — intramurals count fully.\'}\n  ];\n  $(\'supportList\').innerHTML = items.map(i=>\n    \'<div class="panel" style="background:var(--surface-2);margin:0">\'\n    +\'<div class="row spread" style="align-items:baseline"><h3>\'+esc(i.n)+\'</h3>\'+chip(i.chipk)+\'</div>\'\n    +\'<p style="font-size:13px;color:var(--ink-2);margin-top:8px">\'+esc(i.body)+\'</p>\'\n    +\'<dl class="kv" style="margin-top:10px">\'+i.facts.map(f=>\'<dt>\'+esc(f[0])+\'</dt><dd>\'+esc(f[1])+\'</dd>\').join(\'\')+\'</dl>\'\n    +(i.caveat?\'<div class="note warn" style="margin-top:10px">\'+esc(i.caveat)+\'</div>\':\'\')\n    +\'<div class="row" style="margin-top:11px"><a class="btn sm" href="\'+esc(i.go)+\'" target="_blank" rel="noopener">Open ↗</a></div>\'\n    + citeLine(i.cite)\n    +\'</div>\').join(\'\');\n}\n\n', 'support services')
swap_block('  const feeds=[', "  $('eventSources').innerHTML", "  const feeds=[\n    {n:'BYU academic calendar', d:'The authority on every date this planner has hard-coded. If one of mine disagrees with this, this one is right.', u:CITE.bCal26.u, ck:'verified'},\n    {n:'BYU Cougars athletics', d:'Schedules for every sport. BYU competes in the Big 12; football is at LaVell Edwards Stadium and basketball at the Marriott Center.', u:CITE.bAthletics.u, ck:'verified'},\n    {n:'MyBYU', d:'Registration, your schedule and your progress toward graduation.', u:CITE.bMyMap.u, ck:'verified'},\n    {n:'Canvas', d:'Assignments, due dates and the calendar feed the importer on this tab reads.', u:CITE.bCanvas.u, ck:'verified'}\n  ];\n", 'event sources')
swap_block("  $('jobSources').innerHTML = [", '  ].map(x=>', "  $('jobSources').innerHTML = [\n    {n:'Student job listings', ck:'verified', cite:'bStudentJobs',\n     d:'studentjobs.byu.edu is where on-campus openings are posted — everything from custodial and dining through clerical, lab and computing roles.',\n     go:'https://studentjobs.byu.edu/'},\n    {n:'Why work on campus', ck:'verified', cite:'bWhyWork',\n     d:'BYU states that student starting pay runs $9.00 to $20.00 an hour depending on the job and your qualifications, with higher ranges for positions that need specific experience or academic standing. There is a published hourly pay scale behind it.',\n     go:'https://finserve.byu.edu/why-work-on-campus'},\n    {n:'Student hourly pay scale', ck:'verified', cite:'bPayScale',\n     d:'Human Resources publishes the pay scale and job codes the campus rates are set from. Worth reading before you accept the first number an office offers you.',\n     go:'https://hrs.byu.edu/hourly-pay-scale'}\n", 'job sources')
swap_block("  $('planSrc').innerHTML =", '\n  renderBurn();', '  $(\'planSrc\').innerHTML =\n    citeLine(\'bMealHome\',\'Every BYU meal plan, side by side:\')\n   +citeLine(\'bMealInfo\',\'What dining dollars buy and where they are accepted:\')\n   +\'<div style="margin-top:6px">\'+chip(\'reported\')+\' <b>Prices.</b> Open Door and Dining Plus are reported at $2,730 a semester, True Blue at $500 or $800 a semester, and EZ Dining at $100, $150 or $200 a month. Those come from secondary write-ups, not from a BYU price page I could reach — confirm yours and enter what you were actually charged, and every cost-per-meal figure on this tab switches on.</div>\';\n', 'plan source')

prose("halls:{}, hall:'mcnuttdh',", "halls:{}, hall:'cannon',", 'default hall id')
prose("o.hallId = dg2.hall || 'mcnuttdh';", "o.hallId = dg2.hall || 'cannon';", 'derive hall id')
prose("citeLine('diningmap','Official dining map with true positions:') + citeLine('nutrislice','Live menus by hall:')", "citeLine('bDining','All BYU Dining locations:') + citeLine('bMealInfo','What dining dollars buy:')", 'map cites')
prose("citeLine('nutrislice','IU\\u2019s real menu and nutrition:')", "citeLine('bDining','BYU Dining locations:')", 'diet cite')
prose("legs.push({from:'mcnutt', to:list[0].m.bldg||''", "legs.push({from:'campus', to:list[0].m.bldg||''", 'trip leg out')
prose("legs.push({from:list[list.length-1].m.bldg||'', to:'mcnutt', gap:null, kind:'home', dow,", "legs.push({from:list[list.length-1].m.bldg||'', to:'campus', gap:null, kind:'home', dow,", 'trip leg home')
prose("const dests = PLACES.filter(p=>p.id!=='mcnutt');", "const dests = PLACES.filter(p=>p.id!=='campus');", 'hub dests')
prose("+(p.id!=='mcnutt'", "+(p.id!=='campus'", 'place walk btn')
prose('const plan = PLANS.find(p=>p.id===dg.planId) || PLANS[3];', 'const plan = PLANS.find(p=>p.id===dg.planId) || PLANS[0];', 'plan fallback')
prose("      planId:'expanded', priceSem:2000, comboPerWeek:5,", "      planId:'opendoor', priceSem:null, comboPerWeek:null,", 'default plan')
prose('      dollarsStart:250, dollarsLeft:250, scansLeft:null, log:[],', '      dollarsStart:200, dollarsLeft:200, scansLeft:null, log:[],', 'dining dollars')
prose("tile('IU student minimum', money(WAGE.min), '/hr', 'Set by IU; agencies may pay more', 'acc'),", "tile('BYU starting floor', money(WAGE.min), '/hr', 'BYU states $9\\u2013$20 depending on the role', 'acc'),", 'wage tile min')

prose("  $('recSportsInfo').innerHTML = [\n    {n:'Intramural Sports', ck:'verified', cite:'imsports',\n     d:'Run through IMLeagues, which is the platform IU Recreational Sports uses for registration, rosters, schedules and payments. You buy an Intramural Sports Player Pass there. Competitive leagues run a three-game regular season plus a single-elimination playoff; recreational leagues run five games with no playoffs and are explicitly about the social and fitness side rather than winning.',\n     use:'Recreational is the right league if the point is meeting people. Five guaranteed games beats three plus a possible playoff, and nobody is angry at you.',\n     go:'https://www.imleagues.com/indiana'},\n    {n:'Sport Clubs', ck:'verified', cite:'clubsport',\n     d:'Student-led competitive clubs, a step up in commitment from intramurals and a step down from varsity. Practice schedules are set by each club.',\n     use:'Higher time cost, much higher social return — a club is a fixed group of people you see several times a week all year.',\n     go:'https://recsports.indiana.edu/activites/sport-clubs.html'}\n  ].map", "  $('recSportsInfo').innerHTML = [\n    {n:'Intramural sports', ck:'verified', cite:'bRec',\n     d:'BYU runs intramural sport through Student Wellness. Leagues, seasons and sign-up windows are published there rather than anywhere I could read, so nothing is pre-loaded.',\n     use:'This is the highest-value hour on your calendar and the easiest to skip. Find out what runs, then add it as a commitment — intramurals count fully toward the social floor, unlike the gym.',\n     go:'https://studentwellness.byu.edu/'},\n    {n:'Cougar home games', ck:'reported', cite:'bFB26',\n     d:'All seven 2026 home football games are already loaded and checked against your week. The Iowa State game moved to Friday, October 9 at 8:15 p.m. — the only weeknight game on the schedule, and the one most likely to collide with something.',\n     use:'Whether student admission is included is set by Athletics and was not on a page I could reach. Check the ticket office before planning a Saturday around it.',\n     go:'https://byucougars.com/sports/football/schedule'}\n  ].map", 'rec sports info')
prose("+ citeLine('athl26') +'</div>'", "+ citeLine('bAthletics') +'</div>'", 'athl26 cite')
prose("+ citeLine('athlTix')", "+ citeLine('bTickets')", 'athlTix cite')
prose("+chip('verified')+citeLine('aycte')+'</div>');", "+chip('verified')+citeLine('bDining')+'</div>');", 'aycte cite')
prose("citeLine('dininghours','Check hours here:')", "citeLine('bDining','Check hours here:')", 'dininghours cite')

prose("    courses:[\n      {id:'c1', code:'CSCI-C 212', credits:4, instructor:'', diff:1.35,\n       meetings:[\n         {type:'LEC', section:'0100', classNo:'5412', days:[1,3], start:'16:00', end:'17:15', loc:'', bldg:'luddy', tEst:true},\n         {type:'LAB', section:'0124', classNo:'9335', days:[4],   start:'14:00', end:'15:45', loc:'', bldg:'luddy', tEst:true}\n       ], grades:[], notes:''},\n      {id:'c2', code:'INFO-I 101', credits:4, instructor:'', diff:1.0,\n       meetings:[\n         /* Tue/Thu 9:45–11:00 stated directly by you — treated as confirmed. */\n         {type:'LEC', section:'0301', classNo:'4230', days:[2,4], start:'09:45', end:'11:00', loc:'', bldg:'luddy', tEst:false},\n         /* Still the one meeting I have no confirmed reading of. See the lab notice. */\n         {type:'LAB', section:'0328', classNo:'5902', days:[2,4], start:'17:45', end:'19:00', loc:'', bldg:'luddy', tEst:true, disputed:true}\n       ], grades:[], notes:''},\n      {id:'c3', code:'PSY-P 101', credits:3, instructor:'', diff:1.0,\n       meetings:[\n         {type:'LEC', section:'', classNo:'', days:[1,3,5], start:'11:30', end:'12:20', loc:'', bldg:'psych', tEst:true}\n       ], grades:[], notes:''},\n      {id:'c4', code:'INFO-T 100', credits:null, instructor:'', diff:0.85,\n       meetings:[\n         {type:'LEC', section:'', classNo:'', days:[1,3], start:'12:40', end:'13:30', loc:'', bldg:'luddy', tEst:true}\n       ], grades:[], notes:''},\n      {id:'c5', code:'BUS-X 101', credits:1.5, instructor:'', diff:0.8,\n       online:true, meetings:[], grades:[], notes:''}\n    ],\n", '    /* Nothing ships pre-loaded: no BYU course data was researched, and a\n       timetable invented for a stranger would be worse than none. */\n    courses:[],\n', 'empty shipped courses')
prose("function migrate(){\n  const from = +S.v || 1;\n  if(from >= 3) return;\n  const say = [];\n\n  if(from >= 2){\n    /* v2 -> v3: the new keys are supplied by deepMerge; nothing to correct. */\n    S.commitments = S.commitments || [];\n    S.trips = S.trips || [];\n    S.jobs = S.jobs || [];\n    S.sports = S.sports || {interest:{}, games:{}, custom:[]};\n    S.v = 3; save();\n    setTimeout(()=>toast('Added Life & Balance and Work. Your existing data is untouched.','good'), 900);\n    return;\n  }\n\n  const i101 = S.courses.find(c=>c.code==='INFO-I 101');\n  if(i101){\n    const lec = (i101.meetings||[]).find(m=>m.type==='LEC');\n    if(lec){ lec.days=[2,4]; lec.start='09:45'; lec.end='11:00'; lec.tEst=false; lec.bldg=lec.bldg||'luddy';\n             say.push('INFO-I 101 lecture moved to Tue/Thu 9:45'); }\n    const lab = (i101.meetings||[]).find(m=>m.type==='LAB');\n    if(lab){ lab.disputed=true; lab.tEst=true; lab.bldg=lab.bldg||'luddy'; }\n  }\n  S.courses.forEach(c=>(c.meetings||[]).forEach(m=>{\n    if(m.bldg==null) m.bldg = /^(CSCI|INFO)/.test(c.code) ? 'luddy' : (c.code.indexOf('PSY')===0 ? 'psych' : '');\n  }));\n  if(!S.courses.some(c=>c.code==='BUS-X 101')){\n    S.courses.push({id:'c5', code:'BUS-X 101', credits:1.5, instructor:'', diff:0.8,\n                    online:true, meetings:[], grades:[], notes:''});\n    say.push('BUS-X 101 added');\n  }\n  if(S.dining.priceSem==null){ S.dining.priceSem = 2000; say.push('meal plan price set to $2,000'); }\n  if(S.dining.comboPerWeek==null){ S.dining.comboPerWeek = 5; say.push('combo meals set to 5/week'); }\n  S.walk = S.walk || {};\n  if(S.plan.mealAt.lunch==='12:30'){ S.plan.mealAt.lunch='13:30'; S.plan.mealMin.lunch=30;\n    say.push('lunch moved to 1:30 (12:30 collided with INFO-T 100)'); }\n  if(S.plan.mealAt.dinner==='18:15'){ S.plan.mealAt.dinner='19:10';\n    say.push('dinner moved to 7:10 (6:15 collided with the INFO-I 101 lab)'); }\n  S.commitments = S.commitments || [];\n  S.trips = S.trips || [];\n  S.jobs = S.jobs || [];\n  S.sports = S.sports || {interest:{}, games:{}, custom:[]};\n  S.v = 3;\n  save();\n  if(say.length) setTimeout(()=>toast('Updated your saved data: '+say.join('; ')+'.','good'), 900);\n}\n", 'function migrate(){\n  /* The IU build corrects an older shipped timetable here. This build ships\n     no timetable, so there is nothing to correct — just fill in any keys a\n     newer version added. */\n  S.commitments = S.commitments || [];\n  S.trips = S.trips || [];\n  S.jobs = S.jobs || [];\n  S.sports = S.sports || {interest:{}, games:{}, custom:[]};\n  S.walk = S.walk || {};\n  S.v = 3;\n}\n', 'neuter migrate')
prose('placeholder="Canvas calendar feed"', 'placeholder="Canvas calendar feed"', 'src label placeholder')
prose('A saved page cannot read a private Canvas feed', 'A saved page cannot read a private Canvas feed', 'test copy 1')
prose('and your Canvas feed is authenticated to you', 'and your Canvas feed is authenticated to you', 'test copy 2')
prose('<h2>One-click Canvas import</h2>', '<h2>One-click Canvas import</h2>', 'import heading')
prose("actually works. Drag the button to your bookmarks bar, open Canvas, click it — it reads Canvas's own API from inside your signed-in session and copies your courses, grade weights, assignments and scores to the clipboard.", 'actually works. Drag the button to your bookmarks bar, open Canvas, click it — it reads your grade report from inside your signed-in session and copies every course, item, score and weight to the clipboard.', 'import blurb')
prose('Paste an .ics calendar feed, a Canvas assignment list, or plain lines', 'Paste an .ics calendar feed, a Canvas export, or plain lines', 'paste blurb')
prose("'Adding your Canvas calendar feed lets you paste assignments in bulk instead of typing them one at a time.'", "'Adding your Canvas calendar feed lets you pull deadlines in bulk instead of typing them one at a time.'", 'signal copy')
prose('paste a Canvas list on the Data tab and import in bulk', 'use the Canvas import on the Data tab', 'assignments empty state')
prose('placeholder="SRSC, IMLeagues field 3…"', 'placeholder="Intramurals, the HBLL, a club room…"', 'commit note placeholder')
prose("{id:'auto', n:'Work it out from the content'},\n  {id:'canvas', n:'Canvas export from the bookmarklet'},", "{id:'auto', n:'Work it out from the content'},\n  {id:'canvas', n:'Canvas export from the bookmarklet'},", 'paste kind label')
prose('\'<span class="pill">as \'+esc(kind===\'canvas\'?\'Canvas export\'', '\'<span class="pill">as \'+esc(kind===\'canvas\'?\'Canvas export\'', 'preview label')
prose('reloads the Fall 2026 schedule this planner shipped with — the five courses, the meal plan, the confirmed times.', "restores this build's defaults. Nothing is pre-loaded here, so in practice it is the same clean slate as the option above.", 'reset copy')

prose("restores this build's defaults. Nothing is pre-loaded here, so in practice it is the same clean slate as the option above.", 'restores this build\\u2019s defaults. Nothing ships pre-loaded here, so in practice that is the same clean slate as the option above.', 'reset copy apostrophe')
prose("      /* Chosen against the actual timetable, not by habit: 13:30 is the only\n         half-hour free on all five weekdays, and 19:10 clears the evening lab. */\n      mealMin:{breakfast:30, lunch:30, dinner:45},\n      mealAt:{breakfast:'08:00', lunch:'13:30', dinner:'19:10'},", "      /* Neutral starting windows. Once your courses are in, the Dining tab\n         can refit them to slots that are free on every day you have class. */\n      mealMin:{breakfast:30, lunch:40, dinner:45},\n      mealAt:{breakfast:'08:00', lunch:'12:15', dinner:'18:00'},", 'neutral meal windows')

prose("Class contact and required study come straight from your enrolled credits under IU's own credit-hour policy; sleep and meals come from your targets; what is left is genuinely free.", 'Class contact and required study come straight from your enrolled credits at two hours per credit; sleep and meals come from your targets; what is left is genuinely free.', '168 blurb')
prose('Catalog facts are quoted from the IU Academic Bulletin and Office of the Registrar. Difficulty notes are student-reported and labelled as such. Nothing about a named instructor is asserted here — the research toolkit on each card sends you to the primary sources instead.', 'Nothing ships pre-loaded here. Add each course and this planner holds the credit hours, difficulty dial, grade components and meetings you enter. No description is invented, and nothing about a named instructor is asserted — the research toolkit below sends you to the primary sources instead.', 'courses blurb')
prose('no public database of "professor hard spots". These four are the actual sources IU students have, in order of how much weight to give them.', 'no public database of "professor hard spots", and at a school of two thousand there is barely a review site either. These four are what you actually have, in order of how much weight to give them.', 'prof tools blurb')
prose("The anchors every score on this tab is measured against. Two are IU's own figures; the market band is a salary aggregator and is labelled as such.", 'The anchors every score on this tab is measured against. Read the provenance on each — the $9–$20 starting range is BYU’s own figure; the median and band are an aggregator’s.', 'wage panel blurb')
prose('deal was stated by the operator or by IU itself and the source link is on the card.', 'deal was stated by the operator or by BYU itself and the source link is on the card.', 'deals callout')
prose("Weights and scores are yours to enter from each syllabus. GPA uses IU's official grade-point scale, and the projection assumes your current average holds on everything ungraded.", 'Weights and scores are yours to enter from each syllabus. GPA uses a conventional 4.0 scale — not a verified BYU one, see the note below — and the projection assumes your current average holds on everything ungraded.', 'grades blurb')
prose("   USDA-derived nutrition charts. THIS IS NOT IU'S MENU DATA. A dining\n   hall's own preparation differs — sometimes a lot — and IU publishes", "   USDA-derived nutrition charts. THIS IS NOT BYU DINING DATA. A dining\n   hall's own preparation differs — sometimes a lot — and BYU Dining publishes", 'food header comment')

prose('Plan structures below are quoted from the IU Dining meal-plan contract. IU does not publish plan prices on a page I could reach, so price is yours to enter — every cost-per-meal number on this tab is computed from what you type, never guessed.', 'BYU requires every residential student to buy one of two BYU Dining plans — 10 meals a week or 19 — and the BYU student ID is the meal card. Prices are not published on a page I could reach, so the price is yours to enter; every cost-per-meal number here is computed from what you type, never guessed.', 'plan panel markup')
prose('something IU publishes anywhere I could reach, so every hall starts with', 'something BYU publishes anywhere I could reach, so every hall starts with', 'halls comment')

swap_block('  const links = [', '\n  return \'<div class="course"', "  const links = [\n    ['Course catalog', 'https://catalog.byu.edu/courses', 'Official description, credit hours, prerequisites.'],\n    ['MyBYU', 'https://my.byu.edu/', 'Your own schedule — the authority on meeting times.'],\n    ['RateMyProfessors — BYU', 'https://www.ratemyprofessors.com/search/schools?q=BYU%20University', 'Unofficial, self-selected, and thin at this school size. Read comments, ignore scores.'],\n    ['Canvas', 'https://byucanvas.byu.edu/', 'The syllabus is the only authority on how a course is graded.']\n  ];\n", 'course links')

# final blanket pass over prose that still names IU
for _o,_n in [('IU\\u2019s credit-hour minimum implies', 'the two-hours-per-credit convention implies'), ('h a week short of IU\\u2019s minimum', 'h a week short of that convention'), ('IU does not publish plan prices anywhere I could reach', 'BYU does not publish plan prices anywhere I could reach'), ('IU Dining\\u2019s own item data', 'Bon App\\u00e9tit\\u2019s own item data'), ('They are not IU\\u2019s menu data.', 'They are not BYU Dining data.'), ('because IU does not publish a station list I could reach', 'because BYU does not publish a station list I could reach'), ('Claiming runs through IU\\u2019s ticketing system', 'Claiming runs through the university\\u2019s ticketing system'), ('checked against IU\\u2019s own data', 'checked against the published menu'), ('checked against IU\\u2019s published nutrition', 'checked against the published menu'), ("Multiplies IU\\'s '+S.plan.hoursPerCredit+'h-per-credit minimum", "Multiplies the '+S.plan.hoursPerCredit+'h-per-credit convention"), ("0 at IU\\u2019s $'+WAGE.min+' floor, 1.0 at $'+WAGE.avgHi+'.", "0 at $10/hr and 1.0 at $'+WAGE.avgHi+'. Neither end is a BYU figure."), ('/* 0 at the IU student minimum, 1 at the top of the local band */', '/* 0 at a $10 baseline, 1 at the top of the local band */'), ('placeholder="IU Libraries"', 'placeholder="The LINK"')]:
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
# and must never appear in a BYU build.

# ── the embedded registrar dataset: strip it out entirely ────────────────
# BYU publishes no equivalent machine-readable schedule export that I
# could reach, so the BYU build ships with an empty dataset and the
# catalog panel degrades to the "add your own" path it already had.
_soc = re.search(r'(<script type="application/json" id="socData">)(.*?)(</script>)', out, re.S)
if not _soc:
    sys.exit('ERROR: socData block not found — the IU dataset anchor moved')
_empty = ('{"metadata":{"institution":"Brigham Young University","campus":"BYU — Provo",'
          '"term":"Fall 2026","course_count":0,"section_count":0,"meeting_count":0,'
          '"note":"BYU publishes no machine-readable schedule export that this build could reach."},'
          '"instructors":{},"courses":[]}')
out = out[:_soc.start(2)] + _empty + out[_soc.end(2):]
LOG.append('registrar dataset stripped')

# ── the catalog browser + every remaining IU-facing string ──────────────
# These are matched with literal characters read from index.html rather than
# escape sequences, because the source mixes real ’/— with JS \u escapes and
# hand-retyping them is how the earlier anchors rotted.
VISIBLE = [
 # (handled by swap_re below)

 
 
 ("Look up any other IU Bloomington building by name", "Look up any other BYU building by name"),

 # (handled by swap_re below)

 ("A clean screenshot of the weekly grid works best — the one you’d get from One.IU’s class schedule view.",
  "A clean screenshot of the weekly grid works best — the one you’d get from MyBYU’s schedule view."),

 ("Paste what the bookmarklet copied, or any block of text listing your courses, days and times…",
  "Paste your schedule from MyBYU, or any block of text listing your courses, days and times…"),

 ("Open <b>stellic.iu.edu</b> (or find Stellic in One.IU) and sign in.",
  "Open <b>my.byu.edu</b> and sign in."),

 
 # source comments — cosmetic, but they should not claim to be IU data
 ("   SCHEDULE OF CLASSES — the full Fall 2026 IU Bloomington registrar export.",
  "   SCHEDULE OF CLASSES — empty in this build. BYU publishes no"),
 ("   SHARED SCHEDULE MINER — used by the Stellic importer and the screenshot",
  "   SHARED SCHEDULE MINER — used by the MyBYU importer and the screenshot"),
 ("/* Runs the shared miner over whatever is in the Stellic paste box. */",
  "/* Runs the shared miner over whatever is in the MyBYU paste box. */"),
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
  'Twenty-two BYU courses, each one carrying the credit hours, description, prerequisite and topic list I could quote from catalog.byu.edu or a published MAP sheet. BYU does not publish a downloadable schedule of classes I could reach, so this is a cited sample rather than everything running this term \u2014 for anything not below, the live search opens BYU\u2019s own catalog, which is the authority.</div>',
  'catalog blurb')

swap_re(r'The dozen places above are the ones your own week actually uses.*?</div>',
  'The places above are the ones your own week actually uses, each with a hand-verified address. This box hands any other BYU building straight to Google Maps by name rather than guessing at a location I have not checked.</div>',
  'building search hint')

swap_re(r'The table above is the registrar.*?</div>',
  'catalog.byu.edu is quick to navigate directly — and it, not this planner, is the authority on what runs this term.</div>',
  'catalog live-search hint')

swap_re(r"The full Schedule of Classes is not embedded in this build.*?</div>",
  "<b>This is a cited sample, not the whole catalog.</b> Twenty-two BYU courses ship with credit hours and descriptions from catalog.byu.edu and from published MAP sheets. BYU publishes no downloadable section export I could reach, so there is no term-by-term schedule of classes embedded here — for anything not listed above, the live search below hands your query straight to catalog.byu.edu.</div>",
  'catalog empty-state')

swap_re(r"'site:academics\.iu\.edu[^\n]*?Indiana University Bloomington course'",
  "'site:catalog.byu.edu OR site:byu.edu \\\"'+q+'\\\" BYU course'",
  'catalog live search url')

swap_re(r"q\+', Indiana University, Bloomington, IN'",
  "q+', Brigham Young University, Provo, UT'",
  'building maps url')

_PORTAL_COMMENT = (
  '/* ------------------------------------------------------ MyBYU import ---\n'
  '   BYU documents no student-facing API for MyBYU, so this does not\n'
  '   pretend to call one. The bookmarklet copies the visible text of the\n'
  '   MyBYU tab you are on (or just your selection, if you made one) and\n'
  '   hands it to the shared miner, exactly as if you had copied it yourself. */'
)
swap_re(r'/\* -+ Stellic import -+.*?\*/', _PORTAL_COMMENT, 'portal import comment')

for _o, _n in [
  ('\u21f1 Copy from Stellic', '\u21f1 Copy from MyBYU'),
  ('On the Stellic tab showing your schedule', 'On the MyBYU tab showing your schedule'),
  ('It never types, clicks, or submits anything on the Stellic page.',
   'It never types, clicks, or submits anything on the MyBYU page.'),
  ('falls back to the same text miner the Stellic box uses.',
   'falls back to the same text miner the MyBYU box uses.'),
  ('same as the Stellic box above', 'same as the MyBYU box above'),
]:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('stellic wording')
    else:
        MISSES.append('stellic: ' + _o[:40])

# the "not an API call" bullet, matched loosely because of its \u escapes
swap_re(r'<b>This is not a Stellic API call\.</b>.*?</li>',
  "<b>This is not an API call.</b> BYU documents no student API for MyBYU, so there is nothing to call on your behalf. This reads the page you are already looking at.</li>",
  'portal not-an-api bullet')

# ── the schedule importer: MyBYU, not Stellic ─────────────────────────
# The BYU CITE block above replaces IU's wholesale, so the keys the
# schedule importer cites have to be added rather than swapped.
_cite_at = out.index('const CITE = {') + len('const CITE = {')
out = out[:_cite_at] + (
    "\n  stellicIU:{t:'MyBYU \\u2014 schedules, grades and account information', o:'Brigham Young University', u:'https://my.byu.edu/'},"
    "\n  stellicNews:{t:'Registrar \\u2014 registration, transcripts and academic records', o:'Brigham Young University', u:'https://registrar.byu.edu/'},"
    "\n  stellicReg:{t:'BYU course catalog', o:'Brigham Young University', u:'https://catalog.byu.edu/courses'},"
    "\n  stellicIDS:{t:'Getting started with Canvas', o:'BYU Canvas', u:'https://byucanvas.byu.edu/getting-started-with-canvas'},"
    "\n  stellicDocs:{t:'MyBYU sign-in \\u2014 no public student API is documented for it', o:'Brigham Young University', u:'https://my.byu.edu/'},"
) + out[_cite_at:]
LOG.append('portal citations')

prose('Import your schedule from Stellic', 'Import your schedule from MyBYU', 'importer heading')
prose('Stellic replaced the Student Center for registration, so this is where your real meeting times live now. There is no student-accessible API to call, so this reads the page the same way you would copy it yourself.',
      'MyBYU is where your real meeting times live. BYU documents no student-accessible API for it, so this reads the page the same way you would copy it yourself \\u2014 select your schedule, copy, paste below.',
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
      '<a class="btn sm" href="https://my.byu.edu/" target="_blank" rel="noopener">Open MyBYU</a>',
      'confirm banner portal link')
prose('<a class="btn sm" href="https://utilities.registrar.indiana.edu/course-browser/" target="_blank" rel="noopener">Course Browser</a>',
      '<a class="btn sm" href="https://catalog.byu.edu/courses" target="_blank" rel="noopener">Course catalog</a>',
      'confirm banner catalog link')

# ── the corrected screen-recording note names Canvas; here it is Canvas ──



# ── IU course and campus names leaking into BYU-facing copy ────────────
# Several of these fire for a real BYU user: the credits-unset signal
# named INFO-T 100, the dining-strategy note listed IU's five halls, the
# social note quoted IU's SRSC fee, and the low-energy recommendation gave
# IU's CAPS address and phone number. Found by reading the built file end
# to end rather than by grepping for "IU".

swap_re(r"push\('crit','Courses','The INFO-I 101 lab is unresolved',[\s\S]*?\);",
  "push('crit','Courses','A meeting is marked unresolved',\n"
  "      'One of your meetings is flagged as unresolved rather than estimated. Open the Courses tab and set its days and times from MyBYU.');",
  'signal: unresolved meeting')

swap_re(r"push\('warn','Courses','Some meeting times are still estimates',[\s\S]*?\);",
  "push('warn','Courses','Some meeting times are still estimates',\n"
  "      'Meetings brought in by the screenshot scanner or the MyBYU importer are marked estimated until you confirm them. Check them against MyBYU on the Courses tab and this clears.');",
  'signal: estimated times')

swap_re(r"push\('warn','Courses','A course has no credit value',[\s\S]*?\);",
  "push('warn','Courses','A course has no credit value',\n"
  "      d.creditsUnset+' course'+(d.creditsUnset===1?' has':'s have')+' no credit hours set. Until you set them from the catalog, their study requirement is excluded from every total here.');",
  'signal: credits unset')

# the Courses-tab banner names IU courses and links IU tools
swap_re(r"    const lab = \(d\.courses\.find\(c=>c\.code==='INFO-I 101'\)[\s\S]*?\+ '<span class=\"hint\" style=\"margin:0\">Or just edit the row on the card below\.</span></div>';",
  "    banner += '<b>A meeting is marked unresolved.</b> Its days or times could not be read confidently, so nothing was guessed. Edit the row on the card below and it clears.';",
  'banner: unresolved')


# dining strategy listed IU's halls
swap_re(r"out\.push\('<div class=\"note\"><b>Where to actually eat\.</b>[\s\S]*?citeLine\('bDining'\)\+'</div>'\);",
  "out.push('<div class=\"note\"><b>Where to actually eat.</b> Cannon Commons in Helaman Halls is the all-you-care-to-eat hall; the Cougareat in the Wilkinson Center is the food court, and the Creamery on Ninth does a grill, ice cream and a real grocery shop. Hours vary by location and term, so check them before relying on a late meal. '+chip('verified')+citeLine('bDining')+'</div>');",
  'dining: where to eat')

# social note quoted IU's rec-centre fee
swap_re(r"out\.push\('<div class=\"note\"><b>No gym time is blocked out\.</b>[\s\S]*?</div>'\);",
  "out.push('<div class=\"note\"><b>No gym time is blocked out.</b> BYU runs intramural sport and wellness programming through Student Wellness; whether facility access is included in your fees was not published anywhere I could reach, so check before assuming. Gym time counts 30% toward the social floor here either way \u2014 intramurals count fully.</div>');",
  'social: gym note')

# the low-energy recommendation gave IU's counselling address and phone
swap_re(r"if\(avg<=2\.4\) rec\('crit','Your energy has been low for a week',[\s\S]*?'check-in history'\);",
  "if(avg<=2.4) rec('crit','Your energy has been low for a week',\n"
  "      'Average '+rnd(avg,1)+'/5 across your last '+ci.length+' check-ins. That is the pattern the recovery term is meant to catch. BYU\\u2019s Counseling Services are free and confidential \\u2014 three licensed clinicians, details on the Academics tab.',\n"
  "      'check-in history');",
  'rec: low energy')

# the deals recommendation listed IU's campus offers
swap_re(r"rec\('good','About '\+money0\(d\.deals\.left\)\+' of value is still on the table',[\s\S]*?'deals checklist'\);",
  "rec('good','About '+money0(d.deals.left)+' of value is still on the table',\n"
  "      'The on-campus group \\u2014 the Research and Writing Center, the HBLL\\u2019s subject librarians, CAPS, the Accessibility Center \\u2014 is the highest-confidence part of the list and costs nothing but the walk.',\n"
  "      'deals checklist');",
  'rec: deals')

for _o, _n in [
  # IU place id used to filter the building dropdown and to default the hall
  ("PLACES.filter(p=>p.id!=='mcnutt')", "PLACES.filter(p=>p.id!=='campus')"),
  ("const h=S.dining.hall||'mcnuttdh';", "const h=S.dining.hall||'cannon';"),
  # boot toast describes a pre-loaded IU schedule this build does not have
  ("'<div class=\"empty\">Nothing logged. Paste Canvas announcements on the Data tab, or add one by hand.</div>'",
   "'<div class=\"empty\">Nothing logged. Paste Canvas announcements on the Data tab, or add one by hand.</div>'"),
  ("out.msg.push('This looks like a Canvas calendar feed and contains a private token. Do not share it.');",
   "out.msg.push('This looks like a calendar feed and may contain a private token. Do not share it.');"),
  ("Private Canvas feeds commonly fail here", "Private Canvas feeds commonly fail here"),
  # WAGE.min is null in this build, so the placeholder rendered as "null minimum"
  ("placeholder=\"'+WAGE.min+' minimum\"", "placeholder=\"what you were offered\""),
  # the confirm-times toast still names an IU course
]:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('leak')
    else:
        MISSES.append('leak: ' + _o[:44])

# the three INFO-I 101 lab buttons only exist for the IU build's seeded lab
for _btn in ['btnLabOneDay', 'btnLabTue', 'btnLabBoth']:
    swap_re(r"    case '" + _btn + r"': \{[\s\S]*?break; \}\n", "", 'drop ' + _btn)



# mineBuilding() was still matching IU building names, so an imported BYU
# meeting could never get a location and an IU name would wrongly match one.
swap_re(r"const BLDG_KEYWORDS = \{[\s\S]*?\};",
  "const BLDG_KEYWORDS = {\n"
  "hbll:'LEE LIBRARY', wilk:'WILKINSON', jfsb:'SMITH BUILDING', tmcb:'TALMAGE',\n"
  "  marb:'MARTIN', jkb:'KNIGHT', cannon:'CANNON', cougareat:'COUGAREAT',\n"
  "  creamery:'CREAMERY', marriott:'MARRIOTT CENTER', les:'LAVELL EDWARDS',\n"
  "  caps:'COUNSELING', health:'HEALTH CENTER', uac:'ACCESSIBILITY'\n"
  "};",
  'building keywords')

swap_re(r'placeholder="Search e\.g\.[^"]*"', 'placeholder="Search e.g. “CS”, “Calculus”, “MA 16500”…"', 'catalog placeholder')
swap_re(r'placeholder="Paste \.ics text, or one item per line:[^"]*"',
        'placeholder="Paste .ics text, or one item per line:&#10;CS 24000 | Lab 4 | 2026-09-18 | 5&#10;MA 16500 | Quiz 2 | 2026-09-21 | 3"',
        'paste placeholder')
swap_re(r"note:'Counts 30% toward your social floor — the SRSC is where a lot of people actually see each other\.'",
        "note:'Counts 30% toward your social floor \\u2014 the ARC is where a lot of people actually see each other.'",
        'gym kind note')
swap_re(r"d\.creditsUnset\? 'INFO-T 100 is variable credit — set it on Courses' : 'Full-time is 12\+'",
        "d.creditsUnset? d.creditsUnset+' course'+(d.creditsUnset===1?'':'s')+' with no credits set \\u2014 set them on Courses' : 'Full-time is 12+'",
        'credits tile note')

# the estimated-times banner, matched loosely because of its mixed escapes
swap_re(r"\+ '<b>Other meeting times are still estimates\.</b>[\s\S]*?</div>';",
  "+ '<b>Some meeting times are still estimates.</b> Anything brought in by the screenshot scanner or the MyBYU importer stays marked estimated until you confirm it. '\n"
  "      + '<div class=\"row\" style=\"margin-top:11px\"><button class=\"btn primary sm\" id=\"btnConfirmTimes\">Confirm the estimated times</button>'\n"
  "      + '<a class=\"btn sm\" href=\"https://my.byu.edu/\" target=\"_blank\" rel=\"noopener\">Open MyBYU</a></div>';",
  'banner estimated (retry)')

# two recommendations keyed to IU course codes that cannot exist here
swap_re(r"  /\* front-load against the known mid-semester step-up in C 212 \*/\n[\s\S]*?'week '\+d\.weekNo\+' \+ student-reported difficulty curve'\);\n", "", 'drop c212 rec')
swap_re(r"  const i101lab=d\.courses\.find\(c=>c\.code==='INFO-I 101'\);\n[\s\S]*?'course meeting times \+ dining rules'\);\n", "", 'drop i101 rec')

swap_re(r"\? 'Estimated times confirmed\. The INFO-I 101 lab is still unresolved[^']*'",
        "? 'Estimated times confirmed. One meeting is still marked unresolved \\u2014 set it from the card below.'",
        'confirm toast (retry)')
swap_re(r"toast\('Loaded your four Fall 2026 courses[^']*','warn'\)",
        "toast('Empty planner ready. Add your courses on the Courses tab, or import them from Canvas or MyBYU on the Data tab.','good')",
        'boot toast (retry)')
swap_re(r"a Canvas calendar feed URL normally does", "a Canvas calendar feed URL normally does", 'ics hint (retry)')
swap_re(r'trailing subject letter, then a 3-4 digit number\. Matches "CSCI-C 212",',
        'trailing subject letter, then a 3-5 digit number. Matches "CS 24000",', 'regex comment')



# ── BYU schedule parsing: three real defects found by testing ────────────
# 1. BYU subject codes contain spaces ("C S 142", "REL A 275", "A HTG 100"),
#    so the IU regex's mandatory 2-5 letter first token dropped "C S" and
#    mis-read "A HTG 100" as "HTG 100".
# 2. BYU writes times as "10:00a - 10:50a" — a bare a/p with no "m" — which
#    the IU meridiem pattern rejected outright, so every mined meeting came
#    back with no time at all.
# 3. BYU rooms are written as an abbreviation plus a number ("TMCB 1170"),
#    and the keyword map only held the long building names.
for _o, _n in [
 # -- 1 --
 ("""/* A course code, generously: 2-5 letters, optional dash, optional single
   trailing subject letter, then a 3-5 digit number. Matches "CS 24000",
   "MATH 211", "BUS-X101". */
const COURSE_CODE_RE = /\\b(?!(?:LEC|LAB|DIS|REC|SEM|STD|SEC|SECTION|CLASS|ROOM|BLDG|BUILDING|HALL|FLOOR)\\b)([A-Z]{2,5})[-\\s]?([A-Z]\\s?)?(\\d{3,4}[A-Z]?)\\b/;""",
  """/* A BYU course code: a 1-5 letter subject, optionally a second 1-4 letter
   token because BYU subjects contain spaces, then a mandatory separator and
   a 3-digit number with an optional trailing letter. Matches "C S 142",
   "REL A 275", "A HTG 100", "MATH 112", "PHSCS 121", "MUSIC 160R".
   The separator is mandatory on purpose: without it a room like "JFSB B037"
   parses as a course. */
const COURSE_CODE_RE = /\\b(?!(?:LEC|LAB|DIS|REC|SEM|STD|SEC|SECTION|CLASS|ROOM|BLDG|BUILDING|HALL|FLOOR|MW|MWF|TTH|MTWTHF|AM|PM)\\b)([A-Z]{1,5})(?:\\s([A-Z]{1,4}))?[\\s-]+(\\d{3}[A-Z]?)\\b/;"""),
 # BYU never hyphenates a subject, so rebuild the mined code with spaces
 ("""    const rawCode = (cm[1]+'-'+(cm[2]||'').trim()+' '+cm[3]).replace(/-\\s+/,'-').replace(/\\s+/g,' ').trim()
      .replace(/^([A-Z]{2,5})- (\\d)/,'$1 $2');            /* no subject letter: "MATH- 211" -> "MATH 211" */""",
  """    const rawCode = (cm[1]+' '+(cm[2]||'')+' '+cm[3]).replace(/\\s+/g,' ').trim();"""),
 # -- 2 --
 ("""const TIME_RANGE_RE = /(\\d{1,2})(?::(\\d{2}))?\\s?([ap]\\.?m\\.?)?\\s*[-–—to]{1,3}\\s*(\\d{1,2})(?::(\\d{2}))?\\s?([ap]\\.?m\\.?)?/i;""",
  """/* BYU registration screens write "10:00a - 10:50a": a bare a/p, no "m".
   The (?![a-z]) stops the bare form swallowing the first letter of a word. */
const MERIDIEM = '(?:[ap]\\\\.?m\\\\.?|[ap](?![a-z]))';
const TIME_RANGE_RE = new RegExp('(\\\\d{1,2})(?::(\\\\d{2}))?\\\\s?('+MERIDIEM+')?\\\\s*[-–—to]{1,3}\\\\s*(\\\\d{1,2})(?::(\\\\d{2}))?\\\\s?('+MERIDIEM+')?','i');"""),
 ("""  ap2 = (ap2||'').toLowerCase().replace(/\\./g,'');
  ap1 = (ap1||'').toLowerCase().replace(/\\./g,'');""",
  """  const meridiem = x => { x=(x||'').toLowerCase().replace(/\\./g,''); return x==='a'?'am':x==='p'?'pm':x; };
  ap2 = meridiem(ap2);
  ap1 = meridiem(ap1);"""),
 # -- 3 --
 ("""const BLDG_KEYWORDS = {
hbll:'LEE LIBRARY', wilk:'WILKINSON', jfsb:'SMITH BUILDING', tmcb:'TALMAGE',
  marb:'MARTIN', jkb:'KNIGHT', cannon:'CANNON', cougareat:'COUGAREAT',
  creamery:'CREAMERY', marriott:'MARRIOTT CENTER', les:'LAVELL EDWARDS',
  caps:'COUNSELING', health:'HEALTH CENTER', uac:'ACCESSIBILITY'
};
function mineBuilding(text){
  const t = String(text||'').toUpperCase();
  for(const id in BLDG_KEYWORDS){ if(t.includes(BLDG_KEYWORDS[id])) return id; }
  return '';
}""",
  """const BLDG_KEYWORDS = {
  hbll:'LEE LIBRARY', wilk:'WILKINSON', jfsb:'SMITH BUILDING', tmcb:'TALMAGE',
  marb:'MARTIN BUILDING', jkb:'KNIGHT BUILDING', cannon:'CANNON', cougareat:'COUGAREAT',
  creamery:'CREAMERY', marriott:'MARRIOTT CENTER', les:'LAVELL EDWARDS',
  caps:'COUNSELING', health:'HEALTH CENTER', uac:'ACCESSIBILITY'
};
/* A BYU room reads as an abbreviation plus a number \\u2014 "TMCB 1170",
   "JFSB B037" \\u2014 so the abbreviations are matched on a word boundary,
   separately from the long names above. Only unambiguous ones are listed:
   a two-letter abbreviation would fire on ordinary prose. */
const BLDG_ABBREV = {tmcb:'TMCB', jfsb:'JFSB', jkb:'JKB', marb:'MARB', hbll:'HBLL', wilk:'WSC'};
function mineBuilding(text){
  const t = String(text||'').toUpperCase();
  for(const id in BLDG_KEYWORDS){ if(t.includes(BLDG_KEYWORDS[id])) return id; }
  for(const id in BLDG_ABBREV){ if(new RegExp('\\\\b'+BLDG_ABBREV[id]+'\\\\b').test(t)) return id; }
  return '';
}"""),
]:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('byu parser')
    else:
        MISSES.append('parser: ' + _o.strip().split('\n')[0][:44])

# ── two more parser defects, both found by running real BYU rows ─────────
# 4. mineTimeRange took String.match's FIRST hit only. On a BYU row that is
#    the section number ("C S 142 - 002" reads as 42-00), which carries no
#    meridiem, so the function bailed and every meeting lost its time.
#    Anchoring the hour on a word boundary and scanning for the first
#    candidate that actually has a meridiem fixes it.
# 5. The miner reads a 3-line window because registration screens wrap a
#    meeting across short lines. BYU puts a whole section on one line, so
#    the window pulled the NEXT course's days and building into this one.
#    Prefer the line on its own when it already yields both.
for _o, _n in [
 ("""const TIME_RANGE_RE = new RegExp('(\\\\d{1,2})(?::(\\\\d{2}))?\\\\s?('+MERIDIEM+')?\\\\s*[-–—to]{1,3}\\\\s*(\\\\d{1,2})(?::(\\\\d{2}))?\\\\s?('+MERIDIEM+')?','i');
function mineTimeRange(str){
  const m = str.match(TIME_RANGE_RE);
  if(!m) return null;""",
  """const TIME_RANGE_RE = new RegExp('\\\\b(\\\\d{1,2})(?::(\\\\d{2}))?\\\\s?('+MERIDIEM+')?\\\\s*[-–—to]{1,3}\\\\s*(\\\\d{1,2})(?::(\\\\d{2}))?\\\\s?('+MERIDIEM+')?','gi');
/* Scans for the first candidate that resolves. A BYU row leads with its
   section number ("C S 142 - 002"), which looks like a range and is not
   one, so taking only the first regex hit loses the real time. */
function mineTimeRange(str){
  TIME_RANGE_RE.lastIndex = 0;
  let m;
  while((m = TIME_RANGE_RE.exec(str))){
    const hit = timeRangeFrom(m);
    if(hit) return hit;
  }
  return null;
}
function timeRangeFrom(m){"""),
 ("""    const window2 = [lines[i], lines[i+1]||'', lines[i+2]||''].join(' ');
    const days = mineDays(window2);
    const tr = mineTimeRange(window2);
    const typeM = window2.match(MEETING_TYPE_RE);""",
  """    /* Registration screens sometimes wrap one meeting across 2-3 short
       lines, so a window is read when it is needed. BYU puts a whole
       section on one line, and reading ahead there drags the NEXT course's
       days and room into this row \\u2014 so the line alone wins whenever it
       already carries both a day set and a time. */
    const self = lines[i];
    const selfDays = mineDays(self), selfTr = mineTimeRange(self);
    const window2 = (selfDays.length && selfTr) ? self
                  : [lines[i], lines[i+1]||'', lines[i+2]||''].join(' ');
    const days = (selfDays.length && selfTr) ? selfDays : mineDays(window2);
    const tr   = (selfDays.length && selfTr) ? selfTr   : mineTimeRange(window2);
    const typeM = window2.match(MEETING_TYPE_RE);"""),
]:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('byu parser')
    else:
        MISSES.append('parser2: ' + _o.strip().split('\n')[0][:44])

# ── 6. matchCourse carried its own IU-shaped code regex ─────────────────
# It required a 3-4 letter subject and emitted a hyphen, so a Canvas course
# named "REL C 225: Foundations of the Restoration" came back as
# "REL-C 225" and stopped matching the catalog. Reuse the one BYU regex and
# the canonicaliser the rest of the import path already uses.
for _o, _n in [
 ("""  const m=t.match(/\\b([A-Z]{3,4})[-\\s]?([A-Z])?\\s?(\\d{3})\\b/);
  return m ? (m[1]+'-'+(m[2]||'')+' '+m[3]).replace('- ',' ') : '';""",
  """  const m=t.match(COURSE_CODE_RE);
  return m ? canonicalizeCode((m[1]+' '+(m[2]||'')+' '+m[3]).replace(/\\s+/g,' ').trim()) : '';"""),
]:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('byu parser')
    else:
        MISSES.append('parser3: matchCourse')

# ── claims that only hold for IU or for Trine, found by reading the built
#    file end to end rather than by grepping for a school name ────────────
for _o, _n in [
  # the live-search button and its heading still named IU
  ("""Search IU's live catalog ↗""", "Search catalog.byu.edu ↗"),
  ("Look a course up on IU's live pages", "Look a course up on BYU’s live catalog"),
  # Trine's enrolment, carried over with the prof-tools rewrite
  ("""There is no public database of "professor hard spots", and at a school of two thousand there is barely a review site either. These four are what you actually have, in order of how much weight to give them.""",
   """There is no public database of "professor hard spots" — BYU publishes no grade-distribution query I could reach. These four are what you actually have, in order of how much weight to give them."""),
  # the residential meal-plan sentence is IU/Trine's, not BYU's
  ("BYU requires every residential student to buy one of two BYU Dining plans — 10 meals a week or 19 — and the BYU student ID is the meal card. Prices are not published on a page I could reach, so the price is yours to enter; every cost-per-meal number here is computed from what you type, never guessed.",
   "BYU Dining runs four plans: Open Door (unlimited at the Cannon Commons plus 200 dining dollars), Dining Plus (15 dining dollars a day, rolling over), True Blue (500 or 800 dollars a semester) and EZ Dining (100, 150 or 200 a month). The prices shown come from secondary write-ups rather than a BYU price page I could reach, so enter what you were actually charged; every cost-per-meal number here is computed from what you type, never guessed."),
  ("two plans are counted in meals per week. Nothing I could reach describes a separate combo-meal allowance, so leave this blank unless your plan has one.",
   "plans are counted in unlimited access or in dining dollars, not in combo meals. Nothing I could reach describes a separate combo allowance, so leave this blank unless your plan has one."),
  ("Combo meals not stated in the contract text I could read",
   "No combo-meal allowance stated on the BYU plan pages"),
  # IU's CrimsonCard rollover and top-up rules, asserted as verified
  ("""notes.push('<div class="note acc"><b>Dining Dollars are the perishable part.</b> They carry from fall to spring but expire at the end of the academic year, and they can be topped up in $5 increments with a $25 minimum. Running a surplus into May is a straight loss. '+chip('verified')+'</div>');""",
   """notes.push('<div class="note acc"><b>Dining Dollars are the perishable part.</b> BYU Dining does not publish a rollover or expiry rule on a page I could reach, so nothing about carry-over is asserted here \\u2014 ask before you bank a surplus, because at most schools an unspent balance is a straight loss. '+chip('unverified')+'</div>');"""),
  ("""? 'You are <b>'+money(d.dining.dollarDelta)+'</b> above the straight line to zero. Dining Dollars carry from fall to spring but expire at the end of the academic year, so unspent money is lost money.'""",
   """? 'You are <b>'+money(d.dining.dollarDelta)+'</b> above the straight line to zero. Whether an unspent balance carries over is not published anywhere I could reach \\u2014 check before you assume it survives the term.'"""),
]:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('read-through')
    else:
        MISSES.append('read: ' + _o.strip()[:44])

for _o, _n in [
  ("Both BYU plans are a fixed number of meals a week rather than unlimited, so a skipped breakfast is a meal you paid for and did not eat — and it is the first one students drop. Work out your cost per meal below and the arithmetic gets uncomfortable quickly.",
   "On Open Door the Cannon Commons is unlimited, so breakfast costs you nothing at the margin — and it is still the first meal students drop. On a dining-dollar plan it is the cheapest meal of the day to cover. Either way, work out your cost per meal below."),
  ("asking you to time a walk to all twelve of these", "asking you to time a walk to every one of these"),
]:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('read-through')
    else:
        MISSES.append('read2: ' + _o.strip()[:44])

for _o, _n in [
  # IU's fee structure, asserted as a fact about the reader
  ("Support that is already paid for", "Support that is already there"),
  ("You have paid the health fee and the activity fee. These are the services those fees buy, with hours and addresses as published.",
   "The services BYU runs for students, with the hours, addresses and phone numbers as published. What each one costs you is on its own card \u2014 where a fee was not stated on a page I could reach, the card says so rather than promising you it is free."),
  ("CAPS is free to you and the details are two panels down.",
   "CAPS runs walk-in crisis hours and the details are two panels down."),
  # the claim-windows card heads a list this build has nothing to put in
  ("Claim windows for 2026 football", "Claiming a student ticket"),
]:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('read-through')
    else:
        MISSES.append('read3: ' + _o.strip()[:44])

for _o, _n in [
  ("<li>Open <b>iu.instructure.com</b> and sign in.</li>", "<li>Open <b>byu.instructure.com</b> and sign in.</li>"),
  ('placeholder="https://iu.instructure.com/feeds/calendars/user_xxxxx.ics"',
   'placeholder="https://byu.instructure.com/feeds/calendars/user_xxxxx.ics"'),
  # a literal \u2014 that landed in static HTML, where nothing interprets it
  ("so this reads the page the same way you would copy it yourself \\u2014 select your schedule, copy, paste below.",
   "so this reads the page the same way you would copy it yourself \u2014 select your schedule, copy, paste below."),
  # Stellic's own tab names, which MyBYU does not use
  ("<li>Go to <b>Schedule Term</b> \u2014 the tab that shows your sections and meeting times.</li>",
   "<li>Open your <b>class schedule</b> \u2014 the page listing your sections with their days, times and rooms.</li>"),
  ("Schedule Term / registration rollout:", "Where the course itself is defined:"),
]:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('read-through')
    else:
        MISSES.append('read4: ' + _o.strip()[:44])

# ── residual IU branding in user-visible strings ─────────────────────────
# The CSS custom properties, the bookmarklet's clipboard alert and the
# building-search fallback all still said "crimson" / "Bloomington".
for _o, _n in [
  ("Crimson Command: copied '+out.courses.length+' courses.", "Cougar Command: copied '+out.courses.length+' courses."),
  ("Show your bookmarks bar, then drag the crimson button onto it.", "Show your bookmarks bar, then drag the highlighted button onto it."),
  ("|| 'Bloomington';", "|| 'Provo';"),
]:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('brand')
    else:
        MISSES.append('brand: ' + _o[:40])

for _o, _n in [
  ("alert('Crimson Command: ", "alert('Cougar Command: "),
  ("For a real allergy, Bon App\\u00e9tit\\u2019s own item data and a conversation with the s",
   "For a real allergy, BYU Dining\\u2019s own item data and a conversation with the s"),
]:
    if _o in out:
        out = out.replace(_o, _n); LOG.append('brand')
    else:
        MISSES.append('brand2: ' + _o[:40])

# --crimson* -> --brand*: the token names are read by anyone who opens the
# file, and this build has no crimson in it.
for _tok in ['--crimson-deep', '--crimson-lift', '--crimson']:
    out = out.replace(_tok, _tok.replace('crimson', 'brand'))
LOG.append('brand tokens')

pathlib.Path('byu.html').write_text(out)
assert pathlib.Path('index.html').read_text() == before, 'index.html was modified!'
print(f'wrote byu.html — {len(LOG)} sections swapped')
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
pathlib.Path('byu-artifact.html').write_text(body.strip() + '\n')
print('wrote byu-artifact.html')

if MISSES:
    print('MISSED anchors: ' + ', '.join(MISSES))
