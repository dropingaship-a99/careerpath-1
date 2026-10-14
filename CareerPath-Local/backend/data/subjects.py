"""Niche subjects with codes. No streams: every subject stands alone and can
be combined with any other (NEP 2020 idea). OWNER: Member 2 (Data)."""

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
