import re

def preprocess_rpc(code: str) -> str:
    """
    Preprocess Red Panda Code before execution:
    - Convert shorthand math like 5x -> 5 * x
    - Convert directions up/down/left/right to strings
    - Preserve spaces inside string literals
    """

    # Split code into string literals and non-string parts
    parts = re.split(r'(\".*?\"|\'.*?\')', code)

    for i, part in enumerate(parts):
        # Skip string literals
        if part.startswith('"') or part.startswith("'"):
            continue

        # Convert shorthand math: 5x -> 5 * x
        part = re.sub(r'(\d)([a-zA-Z_]\w*)', r'\1*\2', part)

        # Convert directions to strings automatically
        part = re.sub(r'\b(up|down|left|right)\b', r'"\1"', part)

        parts[i] = part

    return ''.join(parts)
