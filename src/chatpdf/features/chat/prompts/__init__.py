from chatpdf.features.chat.prompts import ar, en

_PROMPTS = {"en": en, "ar": ar}


def get_prompts(language: str):
    if language not in _PROMPTS:
        raise ValueError(f"unknown language: {language!r}, valid: {list(_PROMPTS)}")
    return _PROMPTS[language]
