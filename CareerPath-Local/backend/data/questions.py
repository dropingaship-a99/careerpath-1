"""Questions and interest types (adapted from the original pathfinder.py).
OWNER: Member 3 (Quiz + scoring)."""

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
