import re

FILE_TITLE_RE = re.compile(r"^\*\*(.+?)\*\*$")
CODE_BLOCK_RE = re.compile(r"^```")


def normalize_title(title: str) -> str:
    """Remove trailing colon and extra spaces."""
    return title.rstrip(":").strip()


def parse_markdown(md_text: str):
    """
    Parse markdown into (path, content) tuples.
    Supports files without code blocks.
    """
    files = []
    current = None
    in_code = False
    buf = []

    for line in md_text.splitlines():
        title = FILE_TITLE_RE.match(line.strip())
        if title:
            current = normalize_title(title.group(1))
            buf = []
            continue

        if CODE_BLOCK_RE.match(line.strip()):
            in_code = not in_code
            if not in_code and current:
                files.append((current, "\n".join(buf)))
                current = None
                buf = []
            continue

        if in_code:
            buf.append(line)

    if current:
        files.append((current, ""))

    return files
