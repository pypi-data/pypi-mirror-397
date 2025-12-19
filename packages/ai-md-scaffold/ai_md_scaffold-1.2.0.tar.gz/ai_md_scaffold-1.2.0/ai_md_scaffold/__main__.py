import argparse
from pathlib import Path
from .parser import parse_markdown
from .generator import generate
from . import __version__


def ask(question, default="y"):
    """Simple interactive yes/no prompt"""
    prompt = " [Y/n] " if default.lower() == "y" else " [y/N] "
    ans = input(question + prompt).strip().lower()
    if not ans:
        return default.lower() == "y"
    return ans in ("y", "yes")


def detect_root(md_text):
    """
    Detect root folder from first code block containing folder path ending with '/'
    """
    import re
    match = re.search(r"```([\s\S]+?)```", md_text)
    if not match:
        return None
    for line in match.group(1).splitlines():
        if line.strip().endswith("/"):
            return line.strip().rstrip("/")
    return None


def main():
    parser = argparse.ArgumentParser(
        prog="ai-md-scaffold",
        description="Generate project files from AI-generated Markdown"
    )
    parser.add_argument("markdown", nargs="+", help="Markdown file(s)")
    parser.add_argument("--format", type=int, choices=[1, 2], default=1, 
                        help="Markdown format: 1=Bold Title (**file**), 2=Header Title (### file)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--no-interactive", action="store_true", help="Disable prompts")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()
    interactive = not args.no_interactive

    combined = ""
    for md in args.markdown:
        combined += Path(md).read_text(encoding="utf-8") + "\n"

    # Pass the selected format to the parser
    files = parse_markdown(combined, fmt=args.format)

    if not files:
        print(f"[ERROR] No files detected (using Format {args.format})")
        return

    root = detect_root(combined)
    root_path = root if root else "."

    if interactive:
        if root:
            print(f"Root folder detected: {root}")
            if not ask("Use this folder?", "y"):
                root_path = "."
        else:
            print("No root folder detected, using current directory")

    generate(
        files,
        root=root_path,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        logger=print,
    )


if __name__ == "__main__":
    main()