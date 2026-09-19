# -*- coding: utf-8 -*-
"""
Slang handling around the IndicTrans2 model.

The distilled model is trained mostly on formal text, so spoken slang hurts it in two ways:
  * spoken Tamil ("இங்க வாங்க", "எங்கடா இருக்க") is mis-read ("buy it here", "Where to be")
  * English address slang ("man", "dude", "bro") is translated literally ("மனிதர்" = "human being")

prepare_source() normalizes the input before translation and finish_target() restores the
casual flavour afterwards. GENERATE_KWARGS stops the degenerate repetition the model shows
on short informal inputs ("What's what's ...", "Hey Hey Hey ...").
"""

import re
from colloquial import _wb

GENERATE_KWARGS = dict(
    num_beams=4,
    num_return_sequences=1,
)


def generate_kwargs(text: str) -> dict:
    """Plain beam search. Decoding-time repetition controls were tried and rejected on the real
    model: repetition_penalty=1.3 flipped "I have no idea" into "I know", and
    no_repeat_ngram_size works on subword pieces, which legitimately repeat in Indic scripts, so it
    derailed Tamil output and produced English artifacts ("I can'Am unable"). Repetition is instead
    cleaned up after decoding by dedupe_repeats()."""
    return dict(GENERATE_KWARGS)


# Words that are legitimately doubled and must be left alone
_KEEP_DOUBLED = {"very", "bye", "no", "so", "really", "yes", "ha", "hi", "come", "go", "more", "many", "far", "again"}


# A stutter fragment glued to the next word: "Can'Can't", "can'I can't" -> apostrophe followed by a capital
_GLUED_STUTTER = re.compile(r"\b[A-Za-z]+'(?=[A-Z])")


def _norm_token(tok: str) -> str:
    return re.sub(r"[^\w']", "", tok, flags=re.UNICODE).casefold()


def dedupe_repeats(text: str) -> str:
    """Clean up the degenerate repetition the model shows on short informal inputs:
    "What's what's ...", "Hey Hey Hey", "I can'I can't I can't help", and a whole sentence emitted
    twice. Collapses an immediately repeated run of 1-6 words; never touches a repeat that straddles
    a sentence boundary for single words ("I saw him. Him too"), and leaves natural doubles ("very very")."""
    if not text:
        return text
    text = _GLUED_STUTTER.sub("", text)
    out = []
    for tok in text.split(" "):
        out.append(tok)
        collapsed = True
        while collapsed:
            collapsed = False
            for n in range(6, 0, -1):
                if len(out) < 2 * n:
                    continue
                first = [_norm_token(t) for t in out[-2 * n:-n]]
                second = [_norm_token(t) for t in out[-n:]]
                if first != second or not any(first):
                    continue
                if n == 1 and (first[0] in _KEEP_DOUBLED or (len(first[0]) < 2 and first[0] != "i")
                               or out[-2][-1:] in ".!?।॥,;:"):
                    continue
                # Keep the first copy (it has the capitalization) but adopt the repeat's closing
                # punctuation if the first copy had none.
                tail = out[-1][-1:]
                del out[-n:]
                if tail in ".!?।॥" and out[-1][-1:] not in ".!?।॥":
                    out[-1] = out[-1].rstrip(",;:") + tail
                collapsed = True
                break
    return " ".join(out)

# --------------------------------------------------------------------------------------
# English slang address terms
# --------------------------------------------------------------------------------------
_EN_VOCATIVE = r"(?:man|dude|bro|buddy|mate|bruh|pal|fam|dawg)"
_EN_LEAD = re.compile(
    r"^\s*(?:(?:hey|hi|yo|hello|oh|ok|okay|come on)[\s,]+" + _EN_VOCATIVE + r"[\s,!]+|" + _EN_VOCATIVE + r"\s*[,!]\s*)", re.I)
_EN_TRAIL = re.compile(r"[\s,]+" + _EN_VOCATIVE + r"\s*([.!?]*)\s*$", re.I)
_EN_QUESTION = re.compile(
    r"^(?:where|what|who|whom|whose|why|how|when|which|are|is|am|do|does|did|can|could|will|would|should|have|has|was|were)(?![A-Za-z])", re.I)
_EN_LEAD_BARE = re.compile(r"^\s*(bro|dude|buddy|mate|bruh|pal|fam|dawg)\s+(\w+)", re.I)
_STARTS_CLAUSE = {
    "where", "what", "who", "why", "how", "when", "which", "are", "do", "did", "can", "could",
    "will", "would", "should", "i", "we", "you", "he", "she", "it", "they", "let", "lets", "let's", "come",
    "go", "please", "listen", "look", "wait", "stop", "help", "tell", "give", "send", "bring", "don't", "dont",
}
_EN_LEAD_INTERJ = re.compile(r"^\s*(?:hey|yo|oi|hey there)[\s,]+", re.I)

# Casual address word appended in the target language (tone == casual only)
VOCATIVE_BY_TARGET = {
    "tam_Taml": "மச்சான்",
    "hin_Deva": "यार",
    "tel_Telu": "బ్రో",
    "kan_Knda": "ಮಗಾ",
    "mal_Mlym": "മച്ചാ",
    "ben_Beng": "ভাই",
    "mar_Deva": "भावा",
    "guj_Gujr": "ભાઈ",
    "pan_Guru": "ਯਾਰ",
    "ory_Orya": "ଭାଇ",
}

# --------------------------------------------------------------------------------------
# Spoken Tamil -> standard Tamil (what the model actually understands)
# --------------------------------------------------------------------------------------
# Stems that take a fused vocative "டா"/"டி" in speech-to-text output: "எங்கடா" = "எங்க டா"
_TA_FUSABLE_STEMS = [
    "எங்க", "இங்க", "அங்க", "என்ன", "ஏன்", "எப்படி", "எதுக்கு", "யாரு", "எப்போ", "சரி",
    "வா", "போ", "சொல்லு", "பாரு", "விடு", "நில்லு", "இரு", "வாங்க", "நல்லா",
]
_TA_FUSED = re.compile(r"(?<![஀-௿])(" + "|".join(sorted(_TA_FUSABLE_STEMS, key=len, reverse=True)) + r")(டா|டி)(?![஀-௿])")

# Address particles that carry no content of their own
_TA_VOCATIVES = ["டா", "டி", "போடா", "போடி", "மச்சான்", "மச்சி", "மாப்ள", "மாப்பிள்ளை", "நண்பா", "தல", "டே"]

# (colloquial, standard) whole-word replacements
_TA_WORDS = [
    ("நீங்க", "நீங்கள்"), ("அவங்க", "அவர்கள்"), ("இவங்க", "இவர்கள்"), ("நாங்க", "நாங்கள்"),
    ("என்னோட", "என்னுடைய"), ("உங்களோட", "உங்களுடைய"), ("உங்க", "உங்கள்"), ("எங்க", "எங்கே"),
    ("இங்க", "இங்கே"), ("அங்க", "அங்கே"), ("எதுக்கு", "எதற்கு"), ("எப்போ", "எப்போது"),
    ("இப்போ", "இப்போது"), ("எவ்ளோ", "எவ்வளவு"), ("அவ்ளோ", "அவ்வளவு"), ("இல்ல", "இல்லை"),
    ("வேணும்", "வேண்டும்"), ("வேணாம்", "வேண்டாம்"), ("புரியல", "புரியவில்லை"),
    ("தெரியல", "தெரியவில்லை"), ("வீட்ல", "வீட்டில்"), ("எல்லாரும்", "அனைவரும்"),
    # second person singular spoken verb forms
    ("இருக்க", "இருக்கிறாய்"), ("போற", "போகிறாய்"), ("வர்ற", "வருகிறாய்"), ("வர்றியா", "வருகிறாயா"),
    ("பண்ற", "செய்கிறாய்"), ("சொல்ற", "சொல்கிறாய்"), ("சாப்பிட்டியா", "சாப்பிட்டாயா"),
    ("பாக்குற", "பார்க்கிறாய்"), ("தர்ற", "தருகிறாய்"),
    ("செம்ம", "மிகவும் அருமையான"),
]
# Suffix-style verb forms (formal -> spoken pairs from colloquial.py, inverted)
_TA_VERBS = [
    ("இருக்கீங்க", "இருக்கிறீர்கள்"), ("இருக்கேன்", "இருக்கிறேன்"), ("இருக்காரு", "இருக்கிறார்"),
    ("இருக்காங்க", "இருக்கிறார்கள்"), ("பண்றீங்க", "செய்கிறீர்கள்"), ("பண்றேன்", "செய்கிறேன்"),
    ("வர்றீங்க", "வருகிறீர்கள்"), ("வர்றேன்", "வருகிறேன்"), ("போறீங்க", "போகிறீர்கள்"),
    ("போறேன்", "போகிறேன்"), ("சொல்றீங்க", "சொல்கிறீர்கள்"), ("சொல்றேன்", "சொல்கிறேன்"),
]
# "வாங்க" is genuinely ambiguous ("come!" vs "buy!"). After a place word / group it means "come".
_TA_COME = re.compile(r"((?:இங்க|இங்கே|அங்க|அங்கே|சீக்கிரம்|எல்லாரும்|அனைவரும்)\s+)வாங்க(?![஀-௿])")


_TA_HAS_SUBJECT = re.compile(r"(என்னால்|உன்னால்|உங்களால்|எங்களால்|அவனால்|அவளால்|அவரால்|நம்மால்|நானு|நான்)")


def _tamil_to_standard(text: str) -> str:
    t = _TA_FUSED.sub(lambda m: m.group(1) + " " + m.group(2), text)
    t = _TA_COME.sub(lambda m: m.group(1) + "வாருங்கள்", t)
    for spoken, standard in _TA_VERBS:
        t = t.replace(spoken, standard)
    for spoken, standard in _TA_WORDS:
        t = re.sub(_wb(spoken), standard, t)
    return t


def _tamil_add_subject(text: str) -> str:
    # "உதவி செய்ய முடியாது" (no subject) is mis-translated; "என்னால் ... முடியாது" is unambiguous.
    if ("முடியாது" in text or "முடியும்" in text) and not _TA_HAS_SUBJECT.search(text):
        return "என்னால் " + text
    return text


def _strip_tamil_vocatives(text: str):
    """Remove trailing/leading address particles when real content remains. Returns (text, had_vocative)."""
    tokens = text.split()
    had = False
    while len(tokens) > 1 and tokens[-1] in _TA_VOCATIVES:
        tokens.pop()
        had = True
    while len(tokens) > 1 and tokens[0] in ("மச்சான்", "மச்சி", "மாப்ள", "நண்பா", "தல"):
        tokens.pop(0)
        had = True
    # a lone "டா"/"டி" in the middle ("எங்க டா இருக்க") is also just an address particle
    kept = []
    for i, tok in enumerate(tokens):
        if tok in ("டா", "டி") and len(tokens) > 1:
            had = True
            continue
        kept.append(tok)
    return " ".join(kept), had


# Pure address particles (no lexical content) in other source languages
_OTHER_VOCATIVES = {
    "hin_Deva": {"अबे", "ओए", "ओये", "बे"},
    "pan_Guru": {"ਓਏ", "ਓਇ", "ਯਾਰ", "ਵੀਰੇ"},
    "ben_Beng": {"রে", "ওরে"},
    "mar_Deva": {"रे", "अरे"},
    "guj_Gujr": {"અરે"},
    "tel_Telu": {"రా", "రే"},
    "kan_Knda": {"ಲೇ", "ಮಗಾ"},
    "mal_Mlym": {"ടാ", "ഡാ"},
}


def _strip_particles(text: str, particles):
    tokens = text.split()
    had = False
    while len(tokens) > 1 and tokens[-1] in particles:
        tokens.pop()
        had = True
    while len(tokens) > 1 and tokens[0] in particles:
        tokens.pop(0)
        had = True
    return " ".join(tokens), had


_NOT_BEFORE_VOCATIVE = {
    "the", "a", "an", "my", "your", "his", "her", "our", "their", "this", "that", "old", "young",
    "good", "bad", "tall", "strong", "wise", "poor", "rich", "dead", "best", "first", "last", "one", "no",
}
# "man" is also a common noun, so only treat it as an address word after a pronoun/particle
_MAN_AFTER = {"you", "me", "it", "that", "this", "him", "her", "them", "us", "now", "here", "there",
              "please", "ok", "okay", "yes", "no", "come", "go", "up", "on", "off", "up,", "sorry", "thanks", "bye"}


def _is_trailing_vocative(t: str, m) -> bool:
    lead = re.match(r"[\s,]+", m.group(0)).group(0)
    voc = m.group(0)[len(lead):].strip().rstrip(".!?").lower()
    if "," in lead:
        return True
    before = t[: m.start()].split()
    prev = before[-1].lower().strip(",") if before else ""
    if not prev:
        return False
    if voc == "man":
        return prev in _MAN_AFTER
    return prev not in _NOT_BEFORE_VOCATIVE


def prepare_source(text: str, src_code: str):
    """Normalize slang in the source. Returns (clean_text, had_vocative)."""
    t = text.strip()
    had = False
    if src_code == "tam_Taml":
        t, had_a = _strip_tamil_vocatives(t)
        t = _tamil_to_standard(t)
        t, had_b = _strip_tamil_vocatives(t)
        had = had_a or had_b
        t = _tamil_add_subject(t)
    elif src_code in _OTHER_VOCATIVES:
        t, had = _strip_particles(t, _OTHER_VOCATIVES[src_code])
    elif src_code == "eng_Latn":
        m = _EN_TRAIL.search(t)
        if m and _is_trailing_vocative(t, m):
            end = m.group(1) or ""
            t = (t[: m.start()].rstrip(" ,") + end).strip()
            had = True
        m = _EN_LEAD.match(t)
        if m and len(t[m.end():].split()) >= 1:
            t = t[m.end():].strip()
            had = True
        else:
            m = _EN_LEAD_BARE.match(t)
            if m and m.group(2).lower() in _STARTS_CLAUSE:
                t = t[m.start(2):].strip()
                had = True
        t = _EN_LEAD_INTERJ.sub("", t).strip() or text.strip()
        if had and t and t[-1] not in ".!?" and _EN_QUESTION.match(t):
            t += "?"
    return (t or text.strip()), had


def finish_target(text: str, tgt_code: str, had_vocative: bool, tone: str) -> str:
    """Re-attach a casual address word in the target language (casual tone only)."""
    if not had_vocative or tone != "casual" or not text:
        return text
    if tgt_code == "eng_Latn":
        if re.search(r"(?<![A-Za-z])(?:man|brother|bro|dude|buddy|mate|sir|sister)[.!?]*\s*$", text, re.I):
            return text
        m = re.search(r"([.!?]+)\s*$", text)
        base, end = (text[: m.start()].rstrip(" ,"), m.group(1)) if m else (text.rstrip(" ,"), "")
        return base + ", man" + end
    voc = VOCATIVE_BY_TARGET.get(tgt_code)
    if not voc:
        return text
    m = re.search(r"([.!?।॥]+)\s*$", text)
    if m:
        return text[: m.start()].rstrip(" ,") + " " + voc + m.group(1)
    return text.rstrip() + " " + voc
