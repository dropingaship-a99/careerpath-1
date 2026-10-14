"""PathFinder: Interactive Career Explorer (desktop app, single file).

Run:  python pathfinder_desktop.py
Needs only Python 3.8+ with tkinter (included with Python on Windows and macOS;
on Ubuntu/Debian: sudo apt install python3-tk). No internet, no API, no server.
"""
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk


# ===== 1. QUESTIONS =====
TYPES = ["R", "I", "A", "S", "E", "C"]
NAMES = {"R": "Builder", "I": "Thinker", "A": "Creator",
         "S": "Helper", "E": "Leader", "C": "Organiser"}
DESC = {
    "R": "You like hands-on work: tools, machines, nature and making things work.",
    "I": "You like asking why and working things out with logic and evidence.",
    "A": "You like making original things: designs, stories, images and ideas.",
    "S": "You like helping, teaching and working closely with people.",
    "E": "You like leading, persuading and turning ideas into action.",
    "C": "You like order, accuracy and getting the details right.",
}
QUESTIONS = {
    "R": ["Fixing a bike, a gadget or something broken at home",
          "Building things with tools, wood or electronics",
          "Working outdoors with plants, animals or machines"],
    "I": ["Working out why an experiment or puzzle behaves the way it does",
          "Reading about science, space or how the body works",
          "Writing a small program or solving a tough maths problem"],
    "A": ["Drawing, designing or making digital art",
          "Writing stories, scripts or songs",
          "Filming and editing videos or taking photos"],
    "S": ["Helping a classmate understand something difficult",
          "Volunteering for a community cause",
          "Listening to a friend and helping them through a problem"],
    "E": ["Leading a team or organising a school event",
          "Persuading people or debating an idea",
          "Starting a small business or selling something"],
    "C": ["Keeping notes, schedules and files neat",
          "Working with numbers, budgets or spreadsheets",
          "Following clear steps to get a task exactly right"],
}

# Skills and values students can pick (key -> label)
SKILLS = {
    "coding": "Coding", "maths": "Maths", "writing": "Writing",
    "drawing": "Drawing / design", "speaking": "Speaking",
    "problem": "Problem solving", "empathy": "Empathy",
    "organising": "Organising", "leadership": "Leadership",
    "research": "Research", "hands": "Working with hands",
    "teamwork": "Teamwork",
}
VALUES = {
    "creativity": "Creativity", "stability": "Stability",
    "helping": "Helping people", "income": "Good income",
    "nature": "Nature", "technology": "Technology",
    "independence": "Independence",
}


def question_list():
    """Mix types so questions on the same theme are not back to back."""
    out = []
    for k in range(3):
        for t in TYPES:
            out.append({"id": f"{t}{k}", "type": t, "text": QUESTIONS[t][k]})
    return out

# ===== 2. SUBJECTS =====
# code: (name, description, skills, resource keys, extra search words)
SUBJECTS = {
    "CS-101":   ("Computer Science", "How computers work, coding and building apps.", "Logic, coding, debugging", ["cs50", "fcc", "kh"], "programming python software ai"),
    "BIO-101":  ("Biology", "Living things, the human body and ecosystems.", "Observation, research, care", ["kh", "oer", "yt"], "life science body plants animals"),
    "DES-101":  ("Design", "Making products and screens easy and nice to use.", "Sketching, empathy, design tools", ["can", "ted", "cou"], "ux ui graphic product"),
    "PSY-101":  ("Psychology", "How people think, feel and behave.", "Listening, research, empathy", ["cou", "kh", "ted"], "mind behaviour mental"),
    "GEO-101":  ("Geography", "Maps, climate, land and how people use places.", "Map reading, data, observation", ["bbc", "kh", "yt"], "maps climate earth gis"),
    "ECO-101":  ("Economics", "How money, markets and choices shape society.", "Analysis, numbers, reasoning", ["inv", "kh", "cou"], "money markets trade finance"),
    "STAT-101": ("Statistics", "Collecting data and finding patterns in it.", "Data handling, maths, clear reporting", ["kag", "kh", "cou"], "data probability analytics"),
    "MATH-101": ("Mathematics", "Numbers, patterns and logical proof.", "Reasoning, accuracy, problem solving", ["kh", "mit", "nptel"], "maths algebra geometry"),
    "PHY-101":  ("Physics", "Matter, energy, motion, light and electricity.", "Modelling, measuring, problem solving", ["kh", "mit", "nptel"], "energy motion electricity"),
    "CHM-101":  ("Chemistry", "What things are made of and how they change.", "Lab care, patience, analysis", ["kh", "oer", "yt"], "chemicals reactions lab"),
    "ENG-101":  ("English and Communication", "Reading, writing and speaking clearly.", "Writing, speaking, listening", ["ted", "bbc", "cou"], "language writing speaking hindi"),
    "ENV-101":  ("Environmental Studies", "Nature, pollution, climate and sustainability.", "Fieldwork, research, awareness", ["bbc", "ted", "swayam"], "ecology climate green"),
    "AGR-101":  ("Agriculture and Food", "Crops, soil, water and food systems.", "Observation, planning, tech use", ["swayam", "nptel", "yt"], "farming crops soil"),
    "SPT-101":  ("Physical Education and Sports", "Fitness, training, games and sports science.", "Stamina, teamwork, leadership", ["kh", "yt", "ted"], "fitness games coaching"),
    "MED-101":  ("Media Studies", "News, film, social media and storytelling.", "Storytelling, editing, fact-checking", ["ted", "can", "cou"], "journalism film video"),
    "BUS-101":  ("Business Studies", "Starting, running and growing organisations.", "Planning, selling, teamwork", ["kh", "cou", "ted"], "startup management marketing"),
    "SOC-101":  ("Social Science", "Society, history, civics and communities.", "Research, empathy, debate", ["bbc", "ted", "swayam"], "history civics politics"),
    "ELE-101":  ("Electronics and Robotics", "Circuits, sensors, drones and smart machines.", "Building, troubleshooting, safety", ["tink", "kh", "yt"], "circuits arduino drone robot"),
    "HSC-101":  ("Home Science and Nutrition", "Food, health, family and daily living science.", "Planning, care, awareness", ["med", "ted", "yt"], "diet food health"),
    "ART-101":  ("Visual Arts", "Drawing, painting, animation and visual storytelling.", "Drawing, imagination, patience", ["can", "bl", "yt"], "drawing painting animation"),
}

# Ideas for mixing subjects. Examples only, students can invent their own.
COMBOS = {
    "CS-101": ["Computer Science + Statistics + Psychology", "Computer Science + Design + Communication"],
    "BIO-101": ["Biology + Mathematics + Design", "Biology + Environmental Studies + Geography"],
    "DES-101": ["Design + Psychology + Computer Science", "Design + Visual Arts + Business Studies"],
    "PSY-101": ["Psychology + Statistics + Biology", "Psychology + Social Science + Communication"],
    "GEO-101": ["Geography + Computer Science + Environmental Studies", "Geography + Economics + Statistics"],
    "ECO-101": ["Economics + Coding + Psychology", "Economics + Statistics + Social Science"],
    "STAT-101": ["Statistics + Computer Science + Economics", "Statistics + Biology + Geography"],
    "MATH-101": ["Mathematics + Biology + Design + Communication", "Mathematics + Physics + Electronics"],
    "PHY-101": ["Physics + Electronics + Environmental Studies", "Physics + Mathematics + Design"],
    "CHM-101": ["Chemistry + Biology + Home Science", "Chemistry + Environmental Studies + Agriculture"],
    "ENG-101": ["English + Media Studies + Social Science", "English + Business Studies + Psychology"],
    "ENV-101": ["Environmental Studies + Geography + Statistics", "Environmental Studies + Physics + Electronics"],
    "AGR-101": ["Agriculture + Electronics + Geography", "Agriculture + Biology + Business Studies"],
    "SPT-101": ["Sports + Biology + Psychology", "Sports + Business Studies + Media Studies"],
    "MED-101": ["Media Studies + Design + English", "Media Studies + Social Science + Computer Science"],
    "BUS-101": ["Business Studies + Design + Coding", "Business Studies + Economics + Communication"],
    "SOC-101": ["Social Science + Psychology + Statistics", "Social Science + English + Media Studies"],
    "ELE-101": ["Electronics + Computer Science + Physics", "Electronics + Agriculture + Geography"],
    "HSC-101": ["Home Science + Biology + Psychology", "Home Science + Business Studies + Design"],
    "ART-101": ["Visual Arts + Computer Science + Media Studies", "Visual Arts + Design + Psychology"],
}

# ===== 3. CAREERS (data) =====
RESOURCES = {
    "kh": ("Khan Academy", "https://www.khanacademy.org"),
    "fcc": ("freeCodeCamp", "https://www.freecodecamp.org"),
    "cs50": ("Harvard CS50", "https://cs50.harvard.edu/x"),
    "mit": ("MIT OpenCourseWare", "https://ocw.mit.edu"),
    "cou": ("Coursera (many free courses)", "https://www.coursera.org"),
    "edx": ("edX", "https://www.edx.org"),
    "can": ("Canva Design School", "https://www.canva.com/designschool"),
    "ted": ("TED-Ed", "https://ed.ted.com"),
    "yt": ("Crash Course on YouTube", "https://www.youtube.com/@crashcourse"),
    "oer": ("OpenStax free textbooks", "https://openstax.org"),
    "tink": ("Tinkercad", "https://www.tinkercad.com"),
    "kag": ("Kaggle Learn", "https://www.kaggle.com/learn"),
    "bbc": ("BBC Bitesize", "https://www.bbc.co.uk/bitesize"),
    "inv": ("Investopedia", "https://www.investopedia.com"),
    "bl": ("Blender tutorials", "https://www.blender.org/support/tutorials/"),
    "med": ("Khan Academy Health and Medicine", "https://www.khanacademy.org/science/health-and-medicine"),
    "mnm": ("My Next Move (job profiles)", "https://www.mynextmove.org"),
    "swayam": ("SWAYAM (free Indian courses)", "https://swayam.gov.in"),
    "nptel": ("NPTEL", "https://nptel.ac.in"),
    "ncs": ("National Career Service", "https://www.ncs.gov.in/"),
}

CATEGORIES = ["Technology", "Health", "Design", "Environment", "Business", "Sports",
              "Public Service", "Agriculture", "Skilled Trades", "Arts and Media"]


def _c(id, title, cat, desc, interests, skills, subs, values, adv, chal, steps, res):
    return {
        "id": id, "title": title, "category": cat, "description": desc,
        "interests": list(interests),           # RIASEC letters, strongest first
        "skills": skills.split(),
        "subject_codes": [s + "-101" for s in subs.split()],
        "work_values": values.split(),
        "advantages": [x.strip() for x in adv.split(";")],
        "challenges": [x.strip() for x in chal.split(";")],
        "next_steps": [x.strip() for x in steps.split(";")],
        "resources": res.split(),
    }


CAREERS = [
    _c("ux-ui-designer", "UX/UI Designer", "Design",
       "Designs how apps and websites look and feel so people can use them easily.",
       "AI", "drawing empathy problem", "DES CS PSY ART", "creativity technology independence",
       "Creative work with real users; Can work remotely or freelance",
       "Needs a strong portfolio; Feedback and changes are constant",
       "Redesign an app you use daily; Learn Figma or Canva basics; Share work in a simple portfolio",
       "can ted cou"),
    _c("data-analyst", "Data Analyst", "Technology",
       "Turns numbers into answers that help people make better decisions.",
       "IC", "maths coding research", "MATH STAT CS ECO", "technology income stability",
       "Needed in almost every field; Clear skills path with free courses",
       "Can be repetitive at times; Needs patience with messy data",
       "Practise spreadsheets; Try Kaggle Learn Python and Pandas; Analyse a small dataset about your school",
       "kag kh cou"),
    _c("environmental-scientist", "Environmental Scientist", "Environment",
       "Studies pollution, climate and nature and suggests ways to protect them.",
       "IR", "research hands problem", "ENV BIO GEO CHM", "nature helping stability",
       "Work that protects people and nature; Mix of fieldwork and lab work",
       "Fieldwork can be tiring; Results can take years to show",
       "Do a school water or waste audit; Join a local clean-up or eco club; Learn basic mapping and data skills",
       "bbc ted swayam"),
    _c("physiotherapist", "Physiotherapist", "Health",
       "Helps people recover movement and strength after injury or illness.",
       "SR", "empathy hands teamwork", "BIO SPT PSY", "helping stability",
       "Direct, visible help to people; Demand in hospitals, sports and clinics",
       "Physically tiring; Emotional when recovery is slow",
       "Learn basic anatomy; Talk to a physiotherapist about a normal day; Explore sports science topics",
       "med oer yt"),
    _c("graphic-designer", "Graphic Designer", "Design",
       "Creates logos, posters, social media and brand visuals.",
       "AE", "drawing writing teamwork", "DES ART MED", "creativity independence",
       "Very creative; Many freelance and studio options",
       "Tight deadlines; Clients may change their minds often",
       "Design a poster for a school event; Learn Canva design school lessons; Build a small portfolio",
       "can ted cou"),
    _c("agricultural-technologist", "Agricultural Technologist", "Agriculture",
       "Uses sensors, drones and data to help farms grow more with less water and cost.",
       "RI", "hands research problem", "AGR BIO ELE GEO", "nature technology helping",
       "Mixes technology with nature; Helps food security",
       "Work is often outdoors and seasonal; May need to live near farming areas",
       "Grow a small plant experiment; Try Tinkercad or sensor kits; Read about smart farming",
       "swayam nptel tink"),
    _c("cybersecurity-analyst", "Cybersecurity Analyst", "Technology",
       "Protects computers, apps and data from attacks.",
       "IC", "coding problem research", "CS MATH ELE", "technology income stability",
       "Growing need for skilled people; Puzzle-like, interesting problems",
       "Needs constant learning; Can be stressful during incidents",
       "Learn how the internet works; Practise coding basics; Use only legal, safe practice sites",
       "cs50 fcc kh"),
    _c("journalist", "Journalist", "Arts and Media",
       "Finds facts and tells true, clear stories in print, video or online.",
       "AS", "writing speaking research", "ENG MED SOC", "independence helping creativity",
       "Learn about many topics; Gives voice to communities",
       "Irregular hours; Needs thick skin and careful fact-checking",
       "Start a school newsletter; Practise interviewing; Check every fact with two sources",
       "ted cou bbc"),
    _c("animator", "Animator", "Arts and Media",
       "Brings drawings and 3D models to life for films, games and ads.",
       "AR", "drawing teamwork coding", "ART DES MED CS", "creativity technology",
       "Turns imagination into moving pictures; Growing games and OTT demand",
       "Detailed work takes long hours; Needs steady practice",
       "Draw a short flipbook; Try free Blender tutorials; Make a 10-second animation",
       "bl can cou"),
    _c("sports-coach", "Sports Coach", "Sports",
       "Trains players, builds fitness and teaches game skills.",
       "SE", "leadership speaking empathy", "SPT PSY BIO", "helping independence",
       "Keeps you active; Helps others grow",
       "Often weekend and evening work; Income can vary at first",
       "Volunteer to help a junior team; Learn basic fitness and first aid; Study how athletes train",
       "kh yt ted"),
    _c("social-worker", "Social Worker", "Public Service",
       "Supports families and communities and helps them reach services.",
       "SE", "empathy organising speaking", "SOC PSY ENG", "helping stability",
       "Meaningful, people-first work; Roles in NGOs, schools and government",
       "Emotionally demanding; Resources can be limited",
       "Volunteer with a local NGO; Practise listening skills; Learn about community schemes",
       "cou ted edx"),
    _c("nutritionist", "Nutritionist", "Health",
       "Plans healthy eating for individuals, schools and sports teams.",
       "IS", "research empathy organising", "HSC BIO CHM", "helping stability",
       "Helps people live healthier; Options in clinics, sports and food companies",
       "Needs trusted science, not food fads; Habits change slowly",
       "Track a balanced week of meals; Learn basic nutrition science; Talk to a registered dietitian",
       "med ted yt"),
    _c("drone-technician", "Drone Technician", "Skilled Trades",
       "Builds, repairs and flies drones for mapping, farming and film.",
       "RC", "hands problem coding", "ELE PHY CS", "technology independence",
       "Hands-on and modern; Useful in farming, surveying and media",
       "Rules and licences apply; Needs safety discipline",
       "Learn circuit basics in Tinkercad; Read the drone rules for India; Start with a small kit under adult guidance",
       "tink kh yt"),
    _c("renewable-energy-technician", "Renewable Energy Technician", "Skilled Trades",
       "Installs and maintains solar and wind systems.",
       "RC", "hands problem organising", "PHY ELE ENV", "nature stability technology",
       "Growing green sector; Can start through diploma or ITI-style courses",
       "Outdoor and height work; Strict safety rules",
       "Learn simple circuits; Explore a solar kit; Check approved skill courses on NCS",
       "tink kh ncs"),
    _c("entrepreneur", "Entrepreneur", "Business",
       "Starts and grows a business around a useful idea.",
       "EA", "leadership speaking organising", "BUS ECO ENG", "independence income creativity",
       "Be your own boss; Build something of your own",
       "Income is uncertain at first; Many ideas fail before one works",
       "Run a small school project sale; Learn basic money skills; Talk to a local business owner",
       "kh cou ted"),
    _c("doctor", "Doctor", "Health",
       "Finds out what is wrong and treats patients.",
       "IS", "research empathy problem", "BIO CHM PHY", "helping stability income",
       "High trust and respect; Many specialities to choose from",
       "Long training and long hours; Entrance exams are competitive",
       "Learn how the body works; Shadow or interview a doctor; Build good study habits",
       "med oer yt"),
    _c("teacher", "Teacher", "Public Service",
       "Helps people learn and grow in school, college or online.",
       "SA", "speaking empathy organising", "ENG PSY SOC", "helping stability",
       "Shapes young lives; Stable hours and holidays in many roles",
       "Large classes can be tiring; Paperwork and planning take time",
       "Tutor a younger student; Practise explaining one topic simply; Try making a short lesson video",
       "kh ted bbc"),
    _c("accountant", "Accountant", "Business",
       "Keeps money records correct and helps people and firms plan finances.",
       "CE", "maths organising research", "ECO BUS MATH", "stability income",
       "Needed by every business; Clear qualification routes",
       "Busy around tax deadlines; Detail-heavy work",
       "Track your own pocket money in a sheet; Learn basic accounting ideas; Learn spreadsheet formulas",
       "inv kh cou"),
]

# ===== 4. SCORING =====
WEIGHTS = {"interests": 0.4, "skills": 0.3, "subjects": 0.2, "values": 0.1}


def overlap(chosen, wanted):
    """Share of the career's wanted items the student picked (0 to 1).
    If the student picked nothing, stay neutral (0.5) instead of punishing."""
    if not chosen:
        return 0.5
    return len(set(chosen) & set(wanted)) / len(wanted)


def interest_totals(interests):
    """interests = {"R": [2,1,0], ...} -> {"R": 3, ...}. Raises ValueError."""
    if not isinstance(interests, dict):
        raise ValueError("'interests' must be an object like {\"R\": [2,1,0], ...}")
    totals = {}
    for t in TYPES:
        vals = interests.get(t)
        if not isinstance(vals, list) or len(vals) != 3 or any(v not in (0, 1, 2) for v in vals):
            raise ValueError(f"Please answer all 3 questions for type {t} (each answer must be 0, 1 or 2).")
        totals[t] = sum(vals)
    return totals


def format_career(c, picks=None):
    """Career as the website needs it (names instead of codes, resolved links)."""
    skills = [SKILLS[s] for s in c["skills"]]
    chosen = set((picks or {}).get("skills", []))
    return {
        "id": c["id"], "title": c["title"], "category": c["category"],
        "description": c["description"],
        "interest_names": [NAMES[t] for t in c["interests"]],
        "interest_codes": c["interests"],
        "skills": skills, "skill_keys": c["skills"],
        "subjects": [SUBJECTS[s][0] for s in c["subject_codes"]],
        "subject_codes": c["subject_codes"],
        "subject_combo": " + ".join(SUBJECTS[s][0] for s in c["subject_codes"]),
        "work_values": [VALUES[v] for v in c["work_values"]], "value_keys": c["work_values"],
        "advantages": c["advantages"], "challenges": c["challenges"],
        "next_steps": c["next_steps"],
        "skills_to_improve": [SKILLS[s] for s in c["skills"] if s not in chosen] or skills,
        "resources": [{"label": RESOURCES[k][0], "url": RESOURCES[k][1]} for k in c["resources"]],
    }


def recommend(interests, picks, top=5):
    totals = interest_totals(interests)
    ranked = []
    for c in CAREERS:
        first, second = c["interests"]
        parts = {
            "interests": (2 * totals[first] + totals[second]) / 18,
            "skills": overlap(picks["skills"], c["skills"]),
            "subjects": overlap(picks["subjects"], c["subject_codes"]),
            "values": overlap(picks["values"], c["work_values"]),
        }
        score = sum(WEIGHTS[k] * parts[k] for k in WEIGHTS)
        ranked.append((score, parts, c))
    ranked.sort(key=lambda r: -r[0])

    results = []
    for score, parts, c in ranked[:top]:
        out = format_career(c, picks)
        out["match"] = round(score * 100)
        out["breakdown"] = {k: round(v * 100) for k, v in parts.items()}
        out["why"] = why_text(c, totals, picks)
        results.append(out)
    top_types = sorted(TYPES, key=lambda t: (-totals[t], TYPES.index(t)))[:3]
    return {"profile": [{"type": t, "name": NAMES[t], "score": totals[t]} for t in top_types],
            "careers": results}


def why_text(c, totals, picks):
    bits = []
    t = c["interests"][0]
    if totals[t] >= 3:
        bits.append(f"you scored well on the {NAMES[t]} interest")
    sk = [SKILLS[s] for s in c["skills"] if s in picks["skills"]]
    if sk:
        bits.append("you already have " + ", ".join(sk).lower())
    sb = [SUBJECTS[s][0] for s in c["subject_codes"] if s in picks["subjects"]]
    if sb:
        bits.append("you like " + ", ".join(sb))
    vl = [VALUES[v] for v in c["work_values"] if v in picks["values"]]
    if vl:
        bits.append("it fits what you value: " + ", ".join(vl).lower())
    if not bits:
        return "This is a broad idea worth a quick look. Your answers match it only a little."
    return "This may suit you because " + "; ".join(bits) + "."

# ===== 5. COUNSELLORS (no API: edit this list) =====
# Add ONLY people you verified who agreed to be listed. Never invent numbers.
# Example: {"name": "...", "organisation": "...", "city": "Pune", "state": "Maharashtra",
#           "phone": "...", "verified": True, "consent": True}
COUNSELLORS = []

NATIONAL = {
    "name": "National Career Service (Government of India)",
    "website": "https://www.ncs.gov.in/",
    "toll_free": "1800-425-1514",
    "note": "Free career counselling and Model Career Centres.",
}


def counsellors_near(city, state):
    """Only verified AND consented people from COUNSELLORS are shown."""
    return [p for p in COUNSELLORS if p.get("verified") and p.get("consent")
            and p["city"].lower() == city.lower()
            and (not state or p["state"].lower() == state.lower())]


# ===== 6. SEARCH HELPERS =====
def filter_careers(word="", cat="", interest="", skill="", subject="", value=""):
    out = []
    for c in CAREERS:
        text = " ".join([c["title"], c["description"], c["category"]] +
                        [SUBJECTS[s][0] for s in c["subject_codes"]] +
                        [SKILLS[s] for s in c["skills"]]).lower()
        if word and word.lower() not in text:
            continue
        if cat and c["category"] != cat:
            continue
        if interest and interest not in c["interests"]:
            continue
        if skill and skill not in c["skills"]:
            continue
        if subject and subject not in c["subject_codes"]:
            continue
        if value and value not in c["work_values"]:
            continue
        out.append(format_career(c))
    return out


def search_subjects(term):
    term = term.strip().lower().replace(" ", "")
    out = []
    for code, (name, desc, skills, res, words) in SUBJECTS.items():
        if term and term not in (code + name + words).lower().replace(" ", ""):
            continue
        out.append({
            "code": code, "name": name, "description": desc, "skills": skills,
            "careers": [(c["id"], c["title"]) for c in CAREERS if code in c["subject_codes"]],
            "resources": [RESOURCES[k] for k in res], "combos": COMBOS.get(code, []),
        })
    return out


# ===== 7. THE APP (tkinter window) =====
LIGHT = dict(bg="#fafbfd", card="#ffffff", text="#1f2937", muted="#6b7280", line="#e5e7eb",
             blue="#4f7cff", green="#2f9e6f", red="#d9534f", purple="#8b5cf6",
             sgreen="#e8f6ef", sred="#fdf0ee", spurple="#f1ecff", sblue="#e8eefe")
DARK = dict(bg="#12151c", card="#1b1f29", text="#e8eaf0", muted="#9aa3b2", line="#2b3140",
            blue="#6b93ff", green="#4cc38a", red="#ef7b76", purple="#a78bfa",
            sgreen="#173026", sred="#33201d", spurple="#272140", sblue="#1d2745")
FONT = "Helvetica"
WRAP = 780
PICKS = [("subjects", "Which subjects do you enjoy?", "Pick up to 4. Mix any you like.", 4),
         ("skills", "What are you already good at?", "Pick up to 4.", 4),
         ("values", "What matters most in your future work?", "Pick up to 3.", 3)]
CHOICES = [(2, "I would love this"), (1, "It's okay"), (0, "Not for me")]
DISCLAIMER = "These suggestions are for exploration and do not decide a student's future."


class Scroll(tk.Frame):
    """A frame that scrolls vertically and keeps its content centred."""
    def __init__(self, parent, bg):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        bar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.win = self.canvas.create_window((0, 0), window=self.inner, anchor="n")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.resize)
        self.canvas.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

    def resize(self, e):
        self.canvas.itemconfigure(self.win, width=min(e.width - 20, 860))
        self.canvas.coords(self.win, e.width // 2, 0)

    def top(self):
        self.canvas.yview_moveto(0)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PathFinder: Interactive Career Explorer")
        self.geometry("980x720")
        self.minsize(640, 520)
        self.dark = False
        self.page, self.arg = "home", None
        self.questions = question_list()
        self.answers, self.step, self.results, self.compare = {}, 0, None, []
        self.picks = {"subjects": [], "skills": [], "values": []}
        self.f = {k: tk.StringVar() for k in ("q", "category", "interest", "skill", "subject", "value", "sq", "city", "state")}
        self.consent = tk.BooleanVar(value=False)
        self.bind_all("<MouseWheel>", self.wheel)
        self.bind_all("<Button-4>", lambda e: self.sc.canvas.yview_scroll(-2, "units"))
        self.bind_all("<Button-5>", lambda e: self.sc.canvas.yview_scroll(2, "units"))
        self.shell()
        self.go("home")

    # ---------- window shell ----------
    @property
    def t(self):
        return DARK if self.dark else LIGHT

    def wheel(self, e):
        self.sc.canvas.yview_scroll(-2 if e.delta > 0 else 2, "units")

    def shell(self):
        t = self.t
        for w in self.winfo_children():
            w.destroy()
        self.configure(bg=t["bg"])
        st = ttk.Style()
        st.theme_use("clam")
        st.configure("TCombobox", fieldbackground=t["card"], background=t["card"], foreground=t["text"], arrowcolor=t["text"])
        st.configure("Horizontal.TProgressbar", troughcolor=t["line"], background=t["blue"], thickness=8)
        st.configure("Vertical.TScrollbar", background=t["line"], troughcolor=t["bg"], arrowcolor=t["muted"])
        head = tk.Frame(self, bg=t["bg"], padx=16, pady=10)
        head.pack(fill="x")
        tk.Label(head, text="PathFinder", font=(FONT, 16, "bold"), fg=t["blue"], bg=t["bg"]).pack(side="left", padx=(0, 18))
        for name, label in (("home", "Home"), ("quiz", "Quiz"), ("explore", "Careers"),
                            ("subjects", "Subjects"), ("counsellors", "Counsellor")):
            self.B(head, label, lambda n=name: self.go(n), "ghost").pack(side="left", padx=2)
        self.B(head, "◐", self.toggle_theme, "ghost").pack(side="right", padx=2)
        self.B(head, "EN | हिन्दी", lambda: messagebox.showinfo("Language", "Hindi version coming soon / हिन्दी जल्द आ रही है"), "ghost").pack(side="right", padx=2)
        tk.Frame(self, bg=t["line"], height=1).pack(fill="x")
        tk.Label(self, text=DISCLAIMER, font=(FONT, 9), fg=t["muted"], bg=t["bg"], pady=6).pack(side="bottom", fill="x")
        self.sc = Scroll(self, t["bg"])
        self.sc.pack(fill="both", expand=True)

    def toggle_theme(self):
        self.dark = not self.dark
        self.shell()
        self.go(self.page, self.arg, keep=True)

    def go(self, page, arg=None, keep=False):
        self.page, self.arg = page, arg
        for w in self.sc.inner.winfo_children():
            w.destroy()
        if page == "quiz" and not keep:
            self.step = 0
        getattr(self, "p_" + page)()
        self.sc.top()

    # ---------- small widget helpers ----------
    def L(self, parent, text, size=10, bold=False, color=None, wrap=WRAP, bg=None, pady=2, anchor="w", **kw):
        t = self.t
        lab = tk.Label(parent, text=text, font=(FONT, size, "bold" if bold else "normal"),
                       fg=t[color or "text"], bg=bg or parent["bg"], wraplength=wrap, justify="left", **kw)
        lab.pack(anchor=anchor, pady=pady)
        return lab

    def B(self, parent, text, cmd, kind="primary", **kw):
        t = self.t
        look = {"primary": (t["blue"], "#ffffff", t["blue"]), "alt": (t["card"], t["blue"], t["blue"]),
                "ghost": (t["bg"], t["text"], t["bg"]), "opt": (t["card"], t["text"], t["line"]),
                "on": (t["blue"], "#ffffff", t["blue"])}[kind]
        return tk.Button(parent, text=text, command=cmd, bg=look[0], fg=look[1], activebackground=look[0],
                         activeforeground=look[1], relief="flat", cursor="hand2", font=(FONT, 10),
                         highlightthickness=1, highlightbackground=look[2], bd=0, padx=14, pady=6, **kw)

    def card(self, parent, bg=None, pady=6):
        t = self.t
        f = tk.Frame(parent, bg=bg or t["card"], highlightbackground=t["line"], highlightthickness=1, padx=16, pady=12)
        f.pack(fill="x", pady=pady)
        return f

    def row(self, parent):
        r = tk.Frame(parent, bg=parent["bg"])
        r.pack(anchor="w", pady=4)
        return r

    def chips(self, parent, items, kind="spurple"):
        t = self.t
        fg = t["purple"] if kind == "spurple" else t["blue"]
        r = tk.Frame(parent, bg=parent["bg"])
        r.pack(anchor="w", pady=2)
        for i in items:
            tk.Label(r, text=i, font=(FONT, 9), fg=fg, bg=t[kind], padx=8, pady=1).pack(side="left", padx=(0, 4))

    def link(self, parent, text, url, **kw):
        lab = tk.Label(parent, text=text, font=(FONT, 10, "underline"), fg=self.t["blue"], bg=parent["bg"], cursor="hand2", **kw)
        lab.bind("<Button-1>", lambda e: webbrowser.open(url))
        return lab

    def links_row(self, parent, pairs):
        r = tk.Frame(parent, bg=parent["bg"])
        r.pack(anchor="w", pady=2)
        for label, url in pairs:
            self.link(r, label, url).pack(side="left", padx=(0, 12))

    def bullets(self, parent, items, wrap, bg):
        for i in items:
            tk.Label(parent, text="•  " + i, font=(FONT, 10), fg=self.t["text"], bg=bg, wraplength=wrap,
                     justify="left").pack(anchor="w", pady=1)

    def career_block(self, parent, c, full, wrap=720):
        t = self.t
        bg = parent["bg"]
        self.L(parent, c["description"], wrap=wrap)
        if c.get("why"):
            self.L(parent, "Why this matches you: " + c["why"], wrap=wrap, pady=4)
        self.L(parent, "Interests", 9, True, "muted", pady=0)
        self.chips(parent, c["interest_names"])
        self.L(parent, "Skills", 9, True, "muted", pady=0)
        self.chips(parent, c["skills"], "sblue")
        self.L(parent, f"Subjects to mix (no streams): {c['subject_combo']}  ({', '.join(c['subject_codes'])})", 9, wrap=wrap, pady=4)
        two = tk.Frame(parent, bg=bg)
        two.pack(fill="x", pady=6)
        half = (wrap - 20) // 2
        for col, (title, items, tint, ink) in enumerate((("Advantages", c["advantages"], "sgreen", "green"),
                                                         ("Challenges", c["challenges"], "sred", "red"))):
            box = tk.Frame(two, bg=t[tint], padx=10, pady=8)
            box.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 8, 0))
            two.columnconfigure(col, weight=1, uniform="x")
            tk.Label(box, text=title, font=(FONT, 10, "bold"), fg=t[ink], bg=t[tint]).pack(anchor="w")
            self.bullets(box, items, half - 10, t[tint])
        self.L(parent, "Skills to improve: " + ", ".join(c["skills_to_improve"]), 9, wrap=wrap, pady=3)
        if full:
            self.L(parent, "Next steps", 10, True, pady=0)
            self.bullets(parent, c["next_steps"], wrap, bg)
        self.L(parent, "Learn free:", 9, True, "muted", pady=0)
        self.links_row(parent, [(r["label"], r["url"]) for r in c["resources"]])

    # ---------- pages ----------
    def p_home(self):
        t, b = self.t, self.sc.inner
        self.L(b, "Discover careers through your interests and skills", 24, True, pady=(30, 6))
        self.L(b, "Answer a few easy questions. See careers to explore, what is good and hard about each, and free ways to start.", 12, color="muted")
        r = self.row(b)
        self.B(r, "Start Career Quiz", lambda: self.go("quiz")).pack(side="left", padx=(0, 8))
        self.B(r, "Browse careers", lambda: self.go("explore"), "alt").pack(side="left")
        self.L(b, "How it works", 14, True, pady=(20, 4))
        g = tk.Frame(b, bg=t["bg"])
        g.pack(fill="x")
        for i, (h, d) in enumerate((("1. Answer", "18 quick questions, then pick your subjects, skills and values."),
                                    ("2. Explore", "Get 5 careers with honest advantages and challenges."),
                                    ("3. Learn", "Use free resources and talk to a real counsellor."))):
            c = tk.Frame(g, bg=t["card"], highlightbackground=t["line"], highlightthickness=1, padx=14, pady=10)
            c.grid(row=0, column=i, sticky="nsew", padx=4)
            g.columnconfigure(i, weight=1, uniform="h")
            tk.Label(c, text=h, font=(FONT, 11, "bold"), fg=t["purple"], bg=t["card"]).pack(anchor="w")
            tk.Label(c, text=d, font=(FONT, 10), fg=t["muted"], bg=t["card"], wraplength=210, justify="left").pack(anchor="w")
        self.L(b, "No streams, just choices", 14, True, pady=(20, 4))
        self.L(b, "Inspired by NEP 2020, PathFinder does not sort you into Science, Commerce or Arts. Mix subjects your own way, like "
                  "Economics + Coding + Psychology or Maths + Biology + Design. Academic, creative, sports, skilled-trade and service careers all count equally.", color="muted")

    def p_quiz(self):
        t, b = self.t, self.sc.inner
        total, n = len(self.questions) + len(PICKS), len(self.questions)
        s = self.step
        bar = ttk.Progressbar(b, maximum=total, value=s, length=500)
        bar.pack(fill="x", pady=(20, 4))
        self.L(b, f"Step {s + 1} of {total}", 9, color="muted")
        c = self.card(b)
        if s < n:
            q = self.questions[s]
            self.L(c, "How would you feel about this?", 14, True, wrap=720)
            self.L(c, q["text"], 13, wrap=720, pady=8)
            for v, label in CHOICES:
                on = self.answers.get(q["id"]) == v
                self.B(c, label, lambda v=v, i=q["id"]: self.answer(i, v), "on" if on else "opt").pack(fill="x", pady=3)
        else:
            key, title, hint, mx = PICKS[s - n]
            self.L(c, title, 14, True, wrap=720)
            self.L(c, hint + " You can also skip.", 9, color="muted", wrap=720)
            opts = ([(o_code, o_name) for o_code, o_name in ((k, v[0]) for k, v in SUBJECTS.items())] if key == "subjects"
                    else list((SKILLS if key == "skills" else VALUES).items()))
            grid = tk.Frame(c, bg=t["card"])
            grid.pack(anchor="w", pady=10)
            for i, (val, name) in enumerate(opts):
                on = val in self.picks[key]
                self.B(grid, name, lambda k=key, v=val, m=mx: self.pick(k, v, m), "on" if on else "opt").grid(row=i // 4, column=i % 4, padx=3, pady=3, sticky="ew")
            self.B(c, "See my careers" if s == total - 1 else "Next", self.next_step).pack(anchor="w", pady=(6, 0))
        if s > 0:
            self.B(c, "Back", self.back, "alt").pack(anchor="w", pady=(8, 0))

    def answer(self, qid, v):
        self.answers[qid] = v
        self.next_step()

    def pick(self, key, val, mx):
        a = self.picks[key]
        if val in a:
            a.remove(val)
        elif len(a) < mx:
            a.append(val)
        else:
            messagebox.showinfo("PathFinder", f"You can pick up to {mx}.")
        self.go("quiz", keep=True)

    def back(self):
        self.step = max(0, self.step - 1)
        self.go("quiz", keep=True)

    def next_step(self):
        if self.step < len(self.questions) + len(PICKS) - 1:
            self.step += 1
            return self.go("quiz", keep=True)
        interests = {t: [] for t in TYPES}
        for q in self.questions:
            interests[q["type"]].append(self.answers.get(q["id"], 1))
        self.results = recommend(interests, self.picks)
        self.go("results")

    def p_results(self):
        t, b = self.t, self.sc.inner
        if not self.results:
            self.L(b, "No results yet. Take the quiz first.", 12, pady=30)
            self.B(b, "Start Career Quiz", lambda: self.go("quiz")).pack(anchor="w")
            return
        self.L(b, "Careers to explore", 22, True, pady=(20, 4))
        box = tk.Frame(b, bg=t["spurple"], padx=12, pady=8)
        box.pack(fill="x", pady=6)
        tk.Label(box, text=DISCLAIMER, font=(FONT, 10), fg=t["text"], bg=t["spurple"]).pack(anchor="w")
        self.L(b, "Your top interests: " + ", ".join(p["name"] for p in self.results["profile"]), color="muted")
        for c in self.results["careers"]:
            card = self.card(b, pady=8)
            top = tk.Frame(card, bg=t["card"])
            top.pack(fill="x")
            tk.Label(top, text=c["title"], font=(FONT, 14, "bold"), fg=t["text"], bg=t["card"]).pack(side="left")
            tk.Label(top, text=f"{c['match']}% match", font=(FONT, 11, "bold"), fg=t["blue"], bg=t["card"]).pack(side="right")
            cv = tk.Canvas(card, height=8, bg=t["line"], highlightthickness=0)
            cv.pack(fill="x", pady=4)
            cv.bind("<Configure>", lambda e, cv=cv, m=c["match"]: (cv.delete("all"), cv.create_rectangle(0, 0, e.width * m / 100, 8, fill=self.t["green"], width=0)))
            self.career_block(card, c, False)
            r = self.row(card)
            self.B(r, "Explore Career", lambda i=c["id"]: self.go("career", i)).pack(side="left", padx=(0, 8))
            self.B(r, "Find a Counsellor Near Me", lambda: self.go("counsellors"), "alt").pack(side="left")
        self.B(b, "Retake the quiz", lambda: self.restart(), "alt").pack(anchor="w", pady=10)

    def restart(self):
        self.answers, self.step = {}, 0
        self.picks = {"subjects": [], "skills": [], "values": []}
        self.go("quiz")

    def p_career(self):
        b = self.sc.inner
        c = format_career(next(x for x in CAREERS if x["id"] == self.arg))
        self.B(b, "← All careers", lambda: self.go("explore"), "ghost").pack(anchor="w", pady=(12, 0))
        self.chips(b, [c["category"]], "sblue")
        self.L(b, c["title"], 22, True)
        card = self.card(b)
        self.career_block(card, c, True)
        self.B(card, "Find a Counsellor Near Me", lambda: self.go("counsellors")).pack(anchor="w", pady=6)

    def p_explore(self):
        t, b, f = self.t, self.sc.inner, self.f
        self.L(b, "Career Explorer", 22, True, pady=(20, 4))
        e = tk.Entry(b, textvariable=f["q"], font=(FONT, 11), bg=t["card"], fg=t["text"], insertbackground=t["text"], relief="flat",
                     highlightthickness=1, highlightbackground=t["line"], highlightcolor=t["blue"])
        e.pack(fill="x", ipady=6, pady=4)
        e.bind("<KeyRelease>", lambda ev: self.refresh_list())
        self.maps = {}
        r = tk.Frame(b, bg=t["bg"])
        r.pack(fill="x", pady=4)
        specs = [("category", "All categories", [(c, c) for c in CATEGORIES]),
                 ("interest", "Any interest", [(k, v) for k, v in NAMES.items()]),
                 ("skill", "Any skill", list(SKILLS.items())),
                 ("subject", "Any subject", [(k, v[0]) for k, v in SUBJECTS.items()]),
                 ("value", "Any value", list(VALUES.items()))]
        for i, (key, anyl, opts) in enumerate(specs):
            self.maps[key] = dict([(anyl, "")] + [(lab, k) for k, lab in opts])
            if not f[key].get():
                f[key].set(anyl)
            cb = ttk.Combobox(r, textvariable=f[key], values=[anyl] + [lab for _, lab in opts], state="readonly", width=17)
            cb.grid(row=0, column=i, padx=(0, 6), sticky="w")
            cb.bind("<<ComboboxSelected>>", lambda ev: self.refresh_list())
        self.listf = tk.Frame(b, bg=t["bg"])
        self.listf.pack(fill="x")
        self.cmpf = tk.Frame(b, bg=t["bg"])
        self.cmpf.pack(fill="x", pady=10)
        self.refresh_list()

    def refresh_list(self):
        t, f = self.t, self.f
        for w in self.listf.winfo_children():
            w.destroy()
        key = lambda k: self.maps[k].get(f[k].get(), "")
        found = filter_careers(f["q"].get(), key("category"), key("interest"), key("skill"), key("subject"), key("value"))
        if not found:
            self.L(self.listf, "No careers match. Try fewer filters or a different word.", pady=16)
        for c in found:
            card = self.card(self.listf, pady=4)
            self.chips(card, [c["category"]], "sblue")
            self.L(card, c["title"], 13, True, wrap=720)
            self.L(card, c["description"], 10, color="muted", wrap=720)
            r = self.row(card)
            self.B(r, "Details", lambda i=c["id"]: self.go("career", i), "alt").pack(side="left", padx=(0, 10))
            var = tk.BooleanVar(value=c["id"] in self.compare)
            tk.Checkbutton(r, text="Compare", variable=var, bg=t["card"], fg=t["text"], selectcolor=t["card"], activebackground=t["card"],
                           activeforeground=t["text"], command=lambda i=c["id"], v=var: self.toggle_compare(i, v)).pack(side="left")
        self.draw_compare()

    def toggle_compare(self, cid, var):
        if cid in self.compare:
            self.compare.remove(cid)
        elif len(self.compare) < 3:
            self.compare.append(cid)
        else:
            var.set(False)
            messagebox.showinfo("PathFinder", "You can compare up to 3 careers.")
        self.draw_compare()

    def draw_compare(self):
        t = self.t
        for w in self.cmpf.winfo_children():
            w.destroy()
        if len(self.compare) < 2:
            if self.compare:
                self.L(self.cmpf, "Pick one more career to compare.", 9, color="muted")
            return
        cs = [format_career(next(x for x in CAREERS if x["id"] == i)) for i in self.compare]
        self.L(self.cmpf, "Compare", 14, True)
        tbl = tk.Frame(self.cmpf, bg=t["line"])
        tbl.pack(fill="x")
        rows = [("", [c["title"] for c in cs]), ("Category", [c["category"] for c in cs]),
                ("Subjects", [", ".join(c["subjects"]) for c in cs]), ("Skills", [", ".join(c["skills"]) for c in cs]),
                ("Values", [", ".join(c["work_values"]) for c in cs]),
                ("Advantages", ["\n".join("• " + x for x in c["advantages"]) for c in cs]),
                ("Challenges", ["\n".join("• " + x for x in c["challenges"]) for c in cs])]
        w = (WRAP - 90) // len(cs)
        for ri, (lab, cells) in enumerate(rows):
            tk.Label(tbl, text=lab, font=(FONT, 9, "bold"), bg=t["card"], fg=t["muted"], anchor="nw", width=10).grid(row=ri, column=0, sticky="nsew", padx=1, pady=1)
            for ci, cell in enumerate(cells):
                tk.Label(tbl, text=cell, font=(FONT, 9, "bold" if ri == 0 else "normal"), bg=t["card"], fg=t["text"], wraplength=w,
                         justify="left", anchor="nw", padx=6, pady=4).grid(row=ri, column=ci + 1, sticky="nsew", padx=1, pady=1)
        for ci in range(len(cs)):
            tbl.columnconfigure(ci + 1, weight=1, uniform="c")

    def p_subjects(self):
        t, b = self.t, self.sc.inner
        self.L(b, "Subject Explorer", 22, True, pady=(20, 4))
        self.L(b, "Search by subject name or code, like CS-101 or psychology. Subjects are not grouped into streams. Mix any you like.", color="muted")
        e = tk.Entry(b, textvariable=self.f["sq"], font=(FONT, 11), bg=t["card"], fg=t["text"], insertbackground=t["text"], relief="flat",
                     highlightthickness=1, highlightbackground=t["line"], highlightcolor=t["blue"])
        e.pack(fill="x", ipady=6, pady=8)
        e.bind("<KeyRelease>", lambda ev: self.refresh_subjects())
        self.slist = tk.Frame(b, bg=t["bg"])
        self.slist.pack(fill="x")
        self.refresh_subjects()

    def refresh_subjects(self):
        for w in self.slist.winfo_children():
            w.destroy()
        found = search_subjects(self.f["sq"].get())
        if not found:
            self.L(self.slist, "No subject found. Check the code (for example CS-101) or try another word.", pady=16)
        for s in found:
            card = self.card(self.slist, pady=4)
            self.L(card, f"{s['name']}   [{s['code']}]", 13, True, wrap=720)
            self.L(card, s["description"], color="muted", wrap=720)
            self.L(card, "Useful skills: " + s["skills"], 9, wrap=720)
            self.L(card, "Related careers:", 9, True, pady=0)
            r = tk.Frame(card, bg=card["bg"])
            r.pack(anchor="w")
            for cid, title in s["careers"] or []:
                lab = tk.Label(r, text=title, font=(FONT, 10, "underline"), fg=self.t["blue"], bg=card["bg"], cursor="hand2")
                lab.bind("<Button-1>", lambda ev, i=cid: self.go("career", i))
                lab.pack(side="left", padx=(0, 10))
            self.L(card, "Mix it with:", 9, True, pady=0)
            self.bullets(card, s["combos"], 720, card["bg"])
            self.L(card, "Learn free:", 9, True, "muted", pady=0)
            self.links_row(card, s["resources"])

    def p_counsellors(self):
        t, b = self.t, self.sc.inner
        self.L(b, "Find a Career Counsellor", 22, True, pady=(20, 4))
        self.L(b, "Talking to a real person helps. Enter your city and state.", color="muted")
        c = self.card(b)
        tk.Checkbutton(c, text="I allow PathFinder to use the city and state I type to look for counsellors.\n(It never reads your device location.)",
                       variable=self.consent, bg=t["card"], fg=t["text"], selectcolor=t["card"], activebackground=t["card"],
                       activeforeground=t["text"], justify="left").pack(anchor="w")
        r = tk.Frame(c, bg=t["card"])
        r.pack(anchor="w", pady=8)
        for key, ph in (("city", "City"), ("state", "State")):
            tk.Label(r, text=ph, bg=t["card"], fg=t["muted"], font=(FONT, 9)).pack(side="left")
            tk.Entry(r, textvariable=self.f[key], width=18, bg=t["card"], fg=t["text"], insertbackground=t["text"], relief="flat",
                     highlightthickness=1, highlightbackground=t["line"]).pack(side="left", padx=(4, 12), ipady=4)
        self.B(r, "Search", self.search_counsellors).pack(side="left")
        self.cres = tk.Frame(b, bg=t["bg"])
        self.cres.pack(fill="x")

    def search_counsellors(self):
        t = self.t
        for w in self.cres.winfo_children():
            w.destroy()
        if not self.consent.get():
            return self.L(self.cres, "Please tick the permission box first.", color="red", pady=10)
        city, state = self.f["city"].get().strip(), self.f["state"].get().strip()
        if not city:
            return self.L(self.cres, "Please enter a city.", color="red", pady=10)
        hits = counsellors_near(city, state)
        for p in hits:
            card = self.card(self.cres)
            self.L(card, p["name"], 12, True)
            self.L(card, f"{p.get('organisation', '')} {p['city']}, {p['state']}", 9, color="muted")
            self.L(card, "Phone: " + p.get("phone", "Not shared"), 10, True)
            self.chips(card, ["Verified"])
        if not hits:
            box = tk.Frame(self.cres, bg=t["spurple"], padx=12, pady=8)
            box.pack(fill="x", pady=8)
            tk.Label(box, text="We do not have verified, consent-based counsellor details for this place yet. We only show contact "
                               "details that are verified and shared with permission. Please use the National Career Service below.",
                     font=(FONT, 10), fg=t["text"], bg=t["spurple"], wraplength=WRAP - 30, justify="left").pack(anchor="w")
        n = self.card(self.cres)
        self.L(n, NATIONAL["name"], 12, True)
        self.L(n, "Toll-free: " + NATIONAL["toll_free"], 11, True)
        self.L(n, NATIONAL["note"], 9, color="muted")
        self.link(n, NATIONAL["website"], NATIONAL["website"]).pack(anchor="w")
        self.L(self.cres, "Only verified, consent-based contact details are shown here.", 9, color="muted")


if __name__ == "__main__":
    App().mainloop()
