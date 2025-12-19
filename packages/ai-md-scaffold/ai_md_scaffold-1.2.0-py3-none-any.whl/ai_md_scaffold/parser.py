import re
from pathlib import Path

# Format 1: **path/to/file**
# Relaxed regex to find the first **bold text** segment in a line.
# Allows prefixes like "# 📁 " to handle: "# 📁 **2. tailwind.config.js**"
FMT1_TITLE_RE = re.compile(r".*?\*\*(.+?)\*\*.*")

# Format 2: # path/to/file (Matches 1-6 hashes followed by text)
FMT2_TITLE_RE = re.compile(r"^#{1,6}\s+(.+?)$")

CODE_BLOCK_RE = re.compile(r"^```")

# Whitelist for files without extensions
KNOWN_FILES = {
    "dockerfile", "makefile", "jenkinsfile", "procfile", 
    "license", "readme", "changelog", ".gitignore", ".env", ".dockerignore"
}

def normalize_title(title: str) -> str:
    """
    Clean up file title.
    Removes trailing colons, extra spaces, backticks, and asterisks.
    """
    # Remove backticks and asterisks (fixes **file.js** or `file.js`)
    title = title.replace("`", "").replace("*", "")
    return title.rstrip(":").strip()


def is_likely_file(path_str: str) -> bool:
    """
    Determines if a string is likely a valid file path.
    Prevents section headers like "Backend", "Frontend", "Installation" 
    from being treated as files.
    """
    if not path_str:
        return False
        
    path = path_str.lower()
    name = path.split("/")[-1] # Get filename only

    # 1. Allow if it's in the known whitelist (e.g. Dockerfile)
    if name in KNOWN_FILES or path in KNOWN_FILES:
        return True
    
    # 2. Allow if it has a file extension (e.g. .js, .py, .md)
    # We look for a dot that isn't at the start (like .env is handled above, but checks here too)
    # and isn't at the end (like "1.")
    if "." in name and not name.endswith("."):
        return True

    # 3. Allow if it contains a directory separator (e.g. src/main)
    # This assumes "Backend" usually has no slash, but "server/app.js" does.
    if "/" in path_str or "\\" in path_str:
        return True

    return False


def get_clean_token(text: str) -> str:
    """
    Extracts the single valid filename token from a string if possible.
    Returns None if the string contains multiple words or only symbols.
    """
    if not text:
        return None
        
    # Remove backticks and asterisks immediately
    text = text.replace("`", "").replace("*", "").strip()
    
    tokens = text.split()
    
    # Filter tokens that contain at least one alphanumeric character
    valid_tokens = [t for t in tokens if any(c.isalnum() for c in t)]
    
    if len(valid_tokens) == 1:
        return valid_tokens[0]
    return None


def parse_markdown(md_text: str, fmt: int = 1):
    """
    Parse markdown into (path, content) tuples.
    
    Args:
        md_text: The markdown content
        fmt: 1 for Bold Title (**file**), 2 for Header Title (### file)
    """
    files = []
    seen_paths = set() # To track existing paths for duplicate handling
    current = None
    in_code = False
    buf = []

    # Select regex based on format argument
    title_re = FMT1_TITLE_RE if fmt == 1 else FMT2_TITLE_RE

    for line in md_text.splitlines():
        # Look for title only if NOT inside a code block
        if not in_code:
            match = title_re.match(line.strip())
            if match:
                raw_title = match.group(1)
                candidate = None
                
                if fmt == 2:
                    # --- Format 2 Logic (Headers) ---
                    
                    # 1. Cleanup numbering (e.g. "1. ")
                    raw_title = re.sub(r"^\d+\.\s+", "", raw_title)

                    # 2. Strategy: Inside Parens vs Outside Parens
                    paren_match = re.search(r"\(([^)]+)\)", raw_title)
                    inside_text = paren_match.group(1) if paren_match else ""
                    outside_text = re.sub(r"\([^)]+\)", "", raw_title)
                    
                    cand_inside = get_clean_token(inside_text)
                    cand_outside = get_clean_token(outside_text)
                    
                    # Decision logic favoring the one that looks most like a file
                    if cand_inside and cand_outside:
                        in_score = 1 if is_likely_file(cand_inside) else 0
                        out_score = 1 if is_likely_file(cand_outside) else 0
                        candidate = cand_inside if in_score > out_score else cand_outside
                    elif cand_inside:
                        candidate = cand_inside
                    elif cand_outside:
                        candidate = cand_outside

                else:
                    # --- Format 1 Logic (Bold) ---
                    
                    # 1. Cleanup numbering inside bold (e.g. "**2. file.js**")
                    raw_title = re.sub(r"^\d+\.\s+", "", raw_title)
                    
                    # Remove comments in parens
                    if "(" in raw_title:
                        raw_title = raw_title.split("(")[0]
                        
                    candidate = raw_title

                # --- Final Validation & Normalization ---
                if candidate:
                    cleaned = normalize_title(candidate)
                    # Only accept if it actually looks like a file
                    if is_likely_file(cleaned):
                        current = cleaned
                    else:
                        current = None
                else:
                    current = None

                buf = []
                continue

        # Check for code block markers
        if CODE_BLOCK_RE.match(line.strip()):
            in_code = not in_code
            if not in_code and current:
                # End of code block -> Save file
                
                # --- DUPLICATE HANDLING ---
                # If file already exists, rename it (e.g. package.json -> package_2.json)
                if current in seen_paths:
                    original_name = current
                    counter = 2
                    while current in seen_paths:
                        # Find insertion point for suffix
                        last_dot_idx = original_name.rfind(".")
                        slash_idx = original_name.rfind("/")
                        
                        # Apply suffix logic:
                        if last_dot_idx > slash_idx + 1:
                             base = original_name[:last_dot_idx]
                             ext = original_name[last_dot_idx:]
                             current = f"{base}_{counter}{ext}"
                        else:
                             current = f"{original_name}_{counter}"
                        
                        counter += 1
                
                files.append((current, "\n".join(buf)))
                seen_paths.add(current)
                
                current = None
                buf = []
            continue

        if in_code:
            buf.append(line)

    # Handle trailing file definition (Format 1 specific behavior)
    if current and fmt == 1:
        if current in seen_paths:
             original_name = current
             counter = 2
             while current in seen_paths:
                last_dot_idx = original_name.rfind(".")
                slash_idx = original_name.rfind("/")
                if last_dot_idx > slash_idx + 1:
                     base = original_name[:last_dot_idx]
                     ext = original_name[last_dot_idx:]
                     current = f"{base}_{counter}{ext}"
                else:
                     current = f"{original_name}_{counter}"
                counter += 1
        
        files.append((current, ""))
        seen_paths.add(current)

    return files