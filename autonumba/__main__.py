import argparse
import sys
from pathlib import Path
from .walker import resolve_targets
from .injector import boost_file
from .installer import compile_all, aot_compile_folder
import subprocess

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
except ImportError:
    Console = None
    Progress = None

def main():
    p = argparse.ArgumentParser(
        prog="autonumba",
        description="⚡ Aggressively auto-inject Numba @njit into Python codebases with AOT compilation",
        formatter_class=argparse.RawTextHelpFormatter
    )

    p.add_argument("targets", nargs="+", help="📂 Folders, .py files, or @libname")
    p.add_argument("-i", "--inplace", action="store_true", help="✏️ Modify files in place")
    p.add_argument("-c", "--cache", action="store_true", help="💾 Enable njit cache")
    p.add_argument("-f", "--fastmath", action="store_true", help="⚡ Enable fastmath")
    p.add_argument("-p", "--parallel", action="store_true", help="🔀 Enable parallel loops")
    p.add_argument("-n", "--nogil", action="store_true", help="🛠 Release GIL")
    p.add_argument("-b", "--boundscheck", action="store_true", help="📏 Enable bounds checking")
    p.add_argument("--aot", action="store_true", help="🚀 Force ahead-of-time compilation into binaries")
    p.add_argument("-cm", "--compile", action="store_true", help="🖥 Nuitka compile to EXE after boost")
    p.add_argument("-nr", "--no-rich", action="store_true", help="❌ Disable rich output / emojis")

    args = p.parse_args()

    opts = {
        "cache": args.cache or True,
        "fastmath": args.fastmath or True,
        "parallel": args.parallel or True,
        "nogil": args.nogil or True,
        "boundscheck": args.boundscheck or True
    }

    console = Console() if Console and not args.no_rich else None
    use_progress = Progress if Progress and console else None

    if console:
        console.print("🚀 [bold cyan]autonumba[/bold cyan] starting...")
    else:
        print("autonumba starting...")

    files, roots = resolve_targets(args.targets)

    if use_progress:
        with Progress(
            SpinnerColumn(),
            TextColumn("{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeElapsedColumn(),
            console=console
        ) as progress: # pyright: ignore[reportOptionalCall]
            task = progress.add_task("📝 Boosting files", total=len(files))
            for f in files:
                boost_file(f, opts, args.inplace)
                progress.advance(task)
    else:
        for f in files:
            print(f"Boosting {f}...")
            boost_file(f, opts, args.inplace)

    if args.aot:
        if use_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("{task.description}"),
                TimeElapsedColumn(),
                console=console
            ) as progress: # pyright: ignore[reportOptionalCall]
                task = progress.add_task("💿 AOT compiling to binaries", total=len(roots))
                for r in roots:
                    aot_compile_folder(r)
                    progress.advance(task)
        else:
            for r in roots:
                print(f"AOT compiling folder {r}...")
                aot_compile_folder(r)
    else:
        for r in roots:
            compile_all(r)

    # ===== Nuitka compile to EXE =====
    if args.compile:
        if console:
            console.print("🖥 Compiling boosted files to EXE via Nuitka...")
        for f in files:
            boosted_file = f.with_name(f.stem + "_autonumba.py")
            if boosted_file.exists():
                exe_name = f.stem + "_autonumba.exe"
                out_dir = boosted_file.parent
                # All settings for raw maxxed out speed!
                subprocess.run([
                    sys.executable, "-m", "nuitka",
                    "--onefile",
                    "--nofollow-import-to=numba",
                    "--nowarn-mnemonic=unwanted-module",
                    boosted_file.name
                ], check=True, cwd=out_dir)
                exe_file = out_dir / exe_name
                if exe_file.exists():
                    if console:
                        console.print(f"✅ {boosted_file.name} → {exe_name}")
                    else:
                        print(f"{boosted_file.name} → {exe_name}")
                else:
                    print(f"❌ EXE not created for {boosted_file}")
            else:
                print(f"⚠️ Boosted file not found: {boosted_file}")
        if console:
            console.print("✅ [bold green]Done![/bold green] All targets boosted successfully.")
        else:
            print("Done! All targets boosted successfully.")
            
if __name__ == "__main__":
    main()
    