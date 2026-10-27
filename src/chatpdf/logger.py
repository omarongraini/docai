import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logger() -> logging.Logger:
    log = logging.getLogger("chatpdf")
    log.setLevel(logging.INFO)

    # Prevent duplicate logs if Streamlit reruns the script
    if log.hasHandlers():
        return log

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # 1. Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    # 2. File handler (Rotates at 5MB, keeps 3 backups)
    file_handler = RotatingFileHandler(
        "chatpdf.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    return log


logger = setup_logger()
