from pathlib import Path
import fnmatch
import site

def load_excludes(base):
    p = base / "exclude.txt"
    if not p.exists():
        return []
    return [l.strip() for l in p.read_text().splitlines() if l.strip()]

def is_excluded(path, patterns):
    return any(fnmatch.fnmatch(str(path), pat) for pat in patterns)

def resolve_targets(targets):
    files = []
    roots = set()

    for t in targets:
        if t.startswith("@"):
            name = t[1:]
            for sp in site.getsitepackages():
                cand = Path(sp) / name
                if cand.exists():
                    roots.add(cand)
                    excludes = load_excludes(cand)
                    for f in cand.rglob("*.py"):
                        if "__pycache__" not in str(f) and not is_excluded(f, excludes):
                            files.append(f)
        else:
            p = Path(t)
            if p.is_file() and p.suffix == ".py":
                roots.add(p.parent)
                files.append(p)
            elif p.is_dir():
                roots.add(p)
                excludes = load_excludes(p)
                for f in p.rglob("*.py"):
                    if "__pycache__" not in str(f) and not is_excluded(f, excludes):
                        files.append(f)

    return files, roots
