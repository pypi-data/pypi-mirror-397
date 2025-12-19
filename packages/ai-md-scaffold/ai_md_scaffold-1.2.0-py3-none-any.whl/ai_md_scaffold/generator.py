from pathlib import Path


def generate(files, root=".", overwrite=False, dry_run=False, logger=print):
    """
    Generate files from parsed markdown output.

    Args:
        files: List of tuples (path, content)
        root: Root folder to generate into
        overwrite: Overwrite existing files
        dry_run: Only preview actions
        logger: Logging function
    """
    root_path = Path(root)

    for rel_path, content in files:
        target = root_path / rel_path

        if target.exists() and not overwrite:
            logger(f"[WARN] Skip (exists): {target}")
            continue

        if dry_run:
            logger(f"[INFO] DRY-RUN -> {target}")
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        logger(f"[INFO] Created: {target}")
