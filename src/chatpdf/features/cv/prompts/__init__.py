from chatpdf.features.cv.prompts import ar, en

_CV_PROMPTS = {"en": en, "ar": ar}


def get_cv_prompts(language: str):
    if language not in _CV_PROMPTS:
        raise ValueError(f"unknown language: {language!r}, valid: {list(_CV_PROMPTS)}")
    return _CV_PROMPTS[language]
