import re


def extract_yt_term(command):
    youtube_alias = r'(?:youtube|you\s*tube|youtub|yutub|yutib|yutuq)'
    patterns = (
        rf'\bplay\s+(.+?)\s+(?:on\s+)?{youtube_alias}\b',
        rf'\b{youtube_alias}\s+(.+)$',
        r'\bplay\s+(.+)$',
    )
    for pattern in patterns:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            search_term = match.group(1).strip()
            if search_term:
                return search_term
    if re.search(r'\b(?:music|muzik|muzika|musiqa)\b', command, re.IGNORECASE):
        return command.strip()
    return None


def remove_words(input_string, words_to_remove):
    # Split the input string into words
    words = input_string.split()

    # Remove unwanted words
    filtered_words = [word for word in words if word.lower() not in words_to_remove]

    # Join the remaining words back into a string
    result_string = ' '.join(filtered_words)

    return result_string

