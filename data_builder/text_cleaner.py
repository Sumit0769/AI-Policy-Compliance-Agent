import re

def clean_text(text: str) -> str:
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Fix broken line breaks
    text = text.replace("\n", " ")

    # Remove page numbers (common pattern)
    text = re.sub(r"Page \d+", "", text)

    return text.strip()