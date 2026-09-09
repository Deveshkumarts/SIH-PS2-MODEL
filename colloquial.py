# -*- coding: utf-8 -*-
"""
Colloquial and conversational language post-processor for IndicTrans2.
Converts formal, bookish, literary translations into natural, everyday spoken language / slang.
"""

import re

def to_colloquial(text: str, target_lang: str, src_text: str = "") -> str:
    """
    Transforms formal translations into everyday conversational human speech.
    """
    if not text:
        return text

    is_casual_src = any(w in src_text.lower() for w in ["hi", "hey", "hello", "bro", "buddy", "dude", "yaar", "machan"])

    if target_lang == "tam_Taml":
        return _colloquial_tamil(text, is_casual_src)
    elif target_lang == "hin_Deva":
        return _colloquial_hindi(text, is_casual_src)
    elif target_lang == "tel_Telu":
        return _colloquial_telugu(text, is_casual_src)
    elif target_lang == "mal_Mlym":
        return _colloquial_malayalam(text, is_casual_src)
    elif target_lang == "kan_Knda":
        return _colloquial_kannada(text, is_casual_src)
    elif target_lang == "ben_Beng":
        return _colloquial_bengali(text, is_casual_src)
    elif target_lang == "mar_Deva":
        return _colloquial_marathi(text, is_casual_src)
    elif target_lang == "guj_Gujr":
        return _colloquial_gujarati(text, is_casual_src)
    elif target_lang == "pan_Guru":
        return _colloquial_punjabi(text, is_casual_src)

    return text


def _colloquial_tamil(text: str, is_casual_src: bool) -> str:
    t = text

    # Common full phrase replacements
    phrase_map = [
        (r"வணக்கம்,\s*நீங்கள் எப்படி இருக்கிறீர்கள்\?", "ஹாய், எப்படி இருக்கீங்க?"),
        (r"நீங்கள் எப்படி இருக்கிறீர்கள்\?", "எப்படி இருக்கீங்க?"),
        (r"நீங்கள் என்ன செய்கிறீர்கள்\?", "என்ன பண்றீங்க?"),
        (r"நீ என்ன செய்கிறாய்\?", "என்ன பண்ற?"),
        (r"நீங்கள் எங்கே போகிறீர்கள்\?", "எங்க போறீங்க?"),
        (r"நீ எங்கே போகிறாய்\?", "எங்க போற?"),
        (r"சாப்பிட்டீர்களா\?", "சாப்பிட்டீங்களா?"),
        (r"சாப்பிட்டாயா\?", "சாப்பிட்டியா?"),
        (r"உங்களுக்கு என்ன வேண்டும்\?", "உங்களுக்கு என்ன வேணும்?"),
        (r"உனக்கு என்ன வேண்டும்\?", "உனக்கு என்ன வேணும்?"),
        (r"எனக்கு புரியவில்லை", "எனக்கு புரியல"),
        (r"எனக்கு தெரியாது", "எனக்கு தெரியாது"),
        (r"பரவாயில்லை", "பரவால்ல"),
        (r"கவலைப்படாதீர்கள்", "கவலைப்படாதீங்க"),
        (r"கவலைப்படாதே", "கவலைப்படாத"),
    ]
    for p, r in phrase_map:
        t = re.sub(p, r, t)

    # Greeting adaptation
    if is_casual_src:
        t = re.sub(r"^வணக்கம்\b", "ஹாய்", t)

    # Word-level spoken transformations (Senthamizh -> Pechu Thamizh)
    word_map = [
        # Pronouns
        (r"\bநீங்கள்\b", "நீங்க"),
        (r"\bஅவர்கள்\b", "அவங்க"),
        (r"\bஇவர்கள்\b", "இவங்க"),
        (r"\bநாங்கள்\b", "நாங்க"),
        (r"\bஎன்னுடைய\b", "என்னோட"),
        (r"\bஉங்களுடைய\b", "உங்களோட"),
        (r"\bஅவருடைய\b", "அவரோட"),
        (r"\bஅவர்களுடைய\b", "அவங்களோட"),
        (r"\bஅவள்\b", "அவ"),

        # Question & direction words
        (r"\bஎங்கே\b", "எங்க"),
        (r"\bஇங்கே\b", "இங்க"),
        (r"\bஅங்கே\b", "அங்க"),
        (r"\bஎதற்கு\b", "எதுக்கு"),
        (r"\bஎப்பொழுது\b", "எப்போ"),
        (r"\bஎப்போது\b", "எப்போ"),
        (r"\bஇப்பொழுது\b", "இப்போ"),
        (r"\bஇப்போது\b", "இப்போ"),
        (r"\bஅப்பொழுது\b", "அப்போ"),
        (r"\bஅப்போது\b", "அப்போ"),
        (r"\bஎவ்வளவு\b", "எவ்ளோ"),
        (r"\bஅவ்வளவு\b", "அவ்ளோ"),
        (r"\bஇவ்வளவு\b", "இவ்ளோ"),
        (r"\bஇல்லை\b", "இல்ல"),
        (r"\bவேண்டும்\b", "வேணும்"),

        # Verb conjugations (Formal written -> Spoken colloquial)
        (r"இருக்கிறீர்கள்", "இருக்கீங்க"),
        (r"இருக்கிறேன்", "இருக்கேன்"),
        (r"இருக்கிறார்", "இருக்காரு"),
        (r"இருக்கிறார்கள்", "இருக்காங்க"),
        (r"செய்கிறீர்கள்", "பண்றீங்க"),
        (r"செய்கிறேன்", "பண்றேன்"),
        (r"செய்கிறார்", "பண்றாரு"),
        (r"செய்கிறார்கள்", "பண்றாங்க"),
        (r"வருகிறீர்கள்", "வர்றீங்க"),
        (r"வருகிறேன்", "வர்றேன்"),
        (r"வருகிறார்", "வர்றாரு"),
        (r"போகிறீர்கள்", "போறீங்க"),
        (r"போகிறேன்", "போறேன்"),
        (r"போகிறார்", "போறாரு"),
        (r"பார்க்கிறேன்", "பாக்குறேன்"),
        (r"பார்க்கிறீர்கள்", "பாக்குறீங்க"),
        (r"சொல்கிறேன்", "சொல்றேன்"),
        (r"சொல்கிறீர்கள்", "சொல்றீங்க"),
        (r"கொடுக்கிறேன்", "தர்றேன்"),
    ]

    for p, r in word_map:
        t = re.sub(p, r, t)

    return t


def _colloquial_hindi(text: str, is_casual_src: bool) -> str:
    t = text

    # Common full phrase replacements
    phrase_map = [
        (r"नमस्ते,\s*आप कैसे हैं\?", "हाय, क्या हाल है?"),
        (r"आप कैसे हैं\?", "कैसे हो भाई?"),
        (r"तुम कैसे हो\?", "क्या हाल चाल?"),
        (r"आप क्या कर रहे हैं\?", "क्या कर रहे हो?"),
        (r"आप कहाँ जा रहे हैं\?", "कहाँ जा रहे हो?"),
        (r"मुझे ज्ञात नहीं है", "मुझे नहीं पता"),
        (r"मुझे मालूम नहीं है", "मुझे नहीं पता"),
        (r"चिंता मत करो", "टेंशन मत लो"),
        (r"चिंता न करें", "टेंशन मत लो"),
        (r"धन्यवाद", "थैंक्स यार"),
        (r"बहुत धन्यवाद", "बहुत बहुत शुक्रिया"),
        (r"कृपया", "प्लीज़"),
    ]
    for p, r in phrase_map:
        t = re.sub(p, r, t)

    if is_casual_src:
        t = re.sub(r"^नमस्ते\b", "हाय", t)

    return t


def _colloquial_telugu(text: str, is_casual_src: bool) -> str:
    t = text

    phrase_map = [
        (r"నమస్కారం,\s*మీరు ఎలా ఉన్నారు\?", "హాయ్, ఎలా ఉన్నారు?"),
        (r"మీరు ఎలా ఉన్నారు\?", "ఎలా ఉన్నారు? ఏంటి సంగతులు?"),
        (r"నువ్వు ఎలా ఉన్నావు\?", "ఎలా ఉన్నావ్?"),
        (r"ఏమి చేస్తున్నారు\?", "ఏం చేస్తున్నావ్?"),
        (r"మీరు ఏమి చేస్తున్నారు\?", "ఏం చేస్తున్నారు?"),
        (r"ఎక్కడికి వెళ్తున్నారు\?", "ఎక్కడికి వెళ్తున్నారు?"),
        (r"నాకు తెలియదు", "నాకు తెలీదు"),
        (r"చింతించకండి", "టెన్షన్ పడకండి"),
        (r"ధన్యవాదాలు", "థాంక్స్"),
    ]
    for p, r in phrase_map:
        t = re.sub(p, r, t)

    t = re.sub(r"\bఏమిటి\b", "ఏంటి", t)
    t = re.sub(r"\bనమస్కారం\b", "హాయ్" if is_casual_src else "నమస్తే", t)
    return t


def _colloquial_malayalam(text: str, is_casual_src: bool) -> str:
    t = text

    phrase_map = [
        (r"നമസ്കാരം,\s*നിങ്ങൾ എങ്ങനെയിരിക്കുന്നു\?", "ഹായ്, സുഖമാണോ?"),
        (r"നിങ്ങൾ എങ്ങനെയിരിക്കുന്നു\?", "എങ്ങനെയുണ്ട്? സുഖമാണോ?"),
        (r"എന്തുചെയ്യുന്നു\?", "എന്തൊക്കെയുണ്ട് വിശേഷം?"),
        (r"എനിക്ക് അറിയില്ല", "എനിക്കറിയില്ല"),
        (r"വിഷമിക്കേണ്ട", "ടെൻഷൻ അടിക്കണ്ട"),
        (r"നന്ദി", "താങ്ക്സ്"),
    ]
    for p, r in phrase_map:
        t = re.sub(p, r, t)

    if is_casual_src:
        t = re.sub(r"^നമസ്കാരം\b", "ഹായ്", t)

    return t


def _colloquial_kannada(text: str, is_casual_src: bool) -> str:
    t = text

    phrase_map = [
        (r"ನಮಸ್ಕಾರ,\s*ನೀವು ಹೇಗಿದ್ದೀರಿ\?", "ಹಾಯ್, ಹೇಗಿದ್ದೀರಾ?"),
        (r"ನೀವು ಹೇಗಿದ್ದೀರಿ\?", "ಹೇಗಿದ್ದೀರಾ? ಏನ್ ಸಮಾಚಾರ?"),
        (r"ನೀನು ಹೇಗಿದ್ದೀಯಾ\?", "ಹೇಗಿದ್ದೀಯಾ?"),
        (r"ಏನು ಮಾಡುತ್ತಿದ್ದೀರಿ\?", "ಏನ್ ಮಾಡ್ತಿದ್ದೀರಾ?"),
        (r"ನೀವು ಏನು ಮಾಡುತ್ತಿದ್ದೀರಿ\?", "ಏನ್ ಮಾಡ್ತಿದ್ದೀರಿ?"),
        (r"ನನಗೆ ಗೊತ್ತಿಲ್ಲ", "ನನಗೆ ಗೊತ್ತಿಲ್ಲಪ್ಪ"),
        (r"ಚಿಂತಿಸಬೇಡಿ", "ಟೆನ್ಷನ್ ತಗೋಬೇಡಿ"),
        (r"ಧನ್ಯವಾದಗಳು", "ಥ್ಯಾಂಕ್ಸ್"),
    ]
    for p, r in phrase_map:
        t = re.sub(p, r, t)

    t = re.sub(r"\bಏನು\b", "ಏನ್", t)
    if is_casual_src:
        t = re.sub(r"^ನಮಸ್ಕಾರ\b", "ಹಾಯ್", t)

    return t


def _colloquial_bengali(text: str, is_casual_src: bool) -> str:
    t = text

    phrase_map = [
        (r"নমস্কার,\s*আপনি কেমন আছেন\?", "হাই, কেমন আছ?"),
        (r"আপনি কেমন আছেন\?", "কী খবর? কেমন আছো?"),
        (r"তুমি কেমন আছো\?", "কী খবর? কেমন আছিস?"),
        (r"আপনি কী করছেন\?", "কী করছ?"),
        (r"তুমি কী করছো\?", "কী করছিস?"),
        (r"আমি জানি না", "আমার জানা নেই রে"),
        (r"চিন্তা করবেন না", "টেনশন নিও না"),
        (r"ধন্যবাদ", "থ্যাঙ্কস"),
    ]
    for p, r in phrase_map:
        t = re.sub(p, r, t)

    if is_casual_src:
        t = re.sub(r"^নমস্কার\b", "হাই", t)

    return t


def _colloquial_marathi(text: str, is_casual_src: bool) -> str:
    t = text
    phrase_map = [
        (r"नमस्कार,\s*तुम्ही कसे आहात\?", "हाय, काय चाललंय?"),
        (r"तुम्ही कसे आहात\?", "काय मग, कसं काय?"),
        (r"तू कसा आहेस\?", "काय चाललंय भावा?"),
        (r"तुम्ही काय करत आहात\?", "काय करताय?"),
        (r"तू काय करत आहेस\?", "काय करतोयस?"),
        (r"मला माहित नाही", "मला काय माहीत नाही"),
        (r"काळजी करू नका", "टेन्शन घेऊ नका"),
        (r"धन्यवाद", "थँक्स"),
    ]
    for p, r in phrase_map:
        t = re.sub(p, r, t)
    if is_casual_src:
        t = re.sub(r"^नमस्कार\b", "हाय", t)
    return t


def _colloquial_gujarati(text: str, is_casual_src: bool) -> str:
    t = text
    phrase_map = [
        (r"નમસ્તે,\s*તમે કેમ છો\?", "હાય, કેમ છો? શું હાલે?"),
        (r"તમે કેમ છો\?", "શું હાલે ભાઈ? કેમ છો?"),
        (r"તું કેમ છે\?", "શું ચાલે છે?"),
        (r"તમે શું કરી રહ્યા છો\?", "શું કરો છો?"),
        (r"મને ખબર નથી", "મને નથી ખબર"),
        (r"ચિંતા કરશો નહીં", "ટેન્શન ના લો"),
        (r"આભાર", "થેંક્સ"),
    ]
    for p, r in phrase_map:
        t = re.sub(p, r, t)
    if is_casual_src:
        t = re.sub(r"^નમસ્તે\b", "હાય", t)
    return t


def _colloquial_punjabi(text: str, is_casual_src: bool) -> str:
    t = text
    phrase_map = [
        (r"ਸਤ ਸ੍ਰੀ ਅਕਾਲ,\s*ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ\?", "ਹੈਲੋ, ਕੀ ਹਾਲ ਹੈ 22 ਜੀ?"),
        (r"ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ\?", "ਕੀ ਹਾਲ ਚਾਲ ਹੈ?"),
        (r"ਤੂੰ ਕਿਵੇਂ ਹੈਂ\?", "ਸਭ ਠੀਕ ਠਾਕ?"),
        (r"ਤੁਸੀਂ ਕੀ ਕਰ ਰਹੇ ਹੋ\?", "ਕੀ ਚੱਲ ਰਿਹਾ ਹੈ?"),
        (r"ਮੈਨੂੰ ਨਹੀਂ ਪਤਾ", "ਮੈਨੂੰ ਨੀ ਪਤਾ"),
        (r"ਚਿੰਤਾ ਨਾ ਕਰੋ", "ਟੈਂਸ਼ਨ ਨਾ ਲੈ"),
        (r"ਧੰਨਵਾਦ", "ਥੈਂਕਸ ਵੀਰੇ"),
    ]
    for p, r in phrase_map:
        t = re.sub(p, r, t)
    if is_casual_src:
        t = re.sub(r"^ਸਤ ਸ੍ਰੀ ਅਕਾਲ\b", "ਹੈਲੋ", t)
    return t
