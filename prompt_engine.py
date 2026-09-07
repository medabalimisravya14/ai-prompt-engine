import re

TEMPLATES = {
    "General": "Answer this clearly and helpfully: {user_input}",
    "Creative": "You are a creative writer. Write in an imaginative, engaging way: {user_input}",
    "Code Expert": "You are a senior python developer. Give clean code with explanation: {user_input}",
    "Simple Explain": "Explain this like I am 12 years old, very simple: {user_input}",
    "Summarize": "Summarize this in short bullet points: {user_input}"
}

def get_available_styles():
    return list(TEMPLATES.keys())

def engineer_prompt(user_input: str, style: str) -> str:
    template = TEMPLATES.get(style, TEMPLATES["General"])
    return template.format(user_input=user_input.strip())

def detect_prompt_issues(text: str):
    issues = []
    if len(text.strip()) < 5:
        issues.append("Too short")
    if len(text.split()) < 3:
        issues.append("Too vague - add more details")
    # check for obvious typos - repeated letters or no capital at start
    if re.search(r'(.)\1{2,}', text):
        issues.append("Spelling issue - repeated letters")
    # check if all lowercase and no punctuation for long text
    if len(text) > 10 and text.islower() and "?" not in text and "." not in text:
        issues.append("Grammar - try proper sentence")
    # common typos
    common_typos = ["writ", "abot", "teh", "becuase", "robo", "stroy"]
    for typo in common_typos:
        if typo in text.lower():
            issues.append(f"Possible typo: '{typo}'")
            break
    return issues

def get_corrected_prompt_suggestion(text: str) -> str:
    # Simple auto-correction for common mistakes
    corrections = {
        "writ": "write", "wriet": "write", "abot": "about", "abuot": "about",
        "teh": "the", "robo": "robot", "stroy": "story", "becuase": "because",
        "plz": "please", "u": "you"
    }
    corrected = text
    for wrong, right in corrections.items():
        corrected = re.sub(rf'\b{wrong}\b', right, corrected, flags=re.IGNORECASE)

    # Capitalize first letter and add question mark if needed
    corrected = corrected.strip()
    if corrected:
        corrected = corrected[0].upper() + corrected[1:]
    return corrected