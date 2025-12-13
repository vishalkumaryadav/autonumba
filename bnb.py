import os
import shutil
import subprocess
import time
from pathlib import Path
import sys
import re

root = Path(__file__).parent.resolve()
dist = root / "dist"
example_main = root / "example/main.py"
results_file = root / "RESULTS.md"

def run_capture(cmd, desc=""):
    print(f"▶ Running: {' '.join(cmd)} {desc}")
    start = time.perf_counter()
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    output = (result.stdout or "") + ("\n" + (result.stderr or ""))
    duration = time.perf_counter() - start
    print(f"✅ Finished {desc} in {duration:.4f}s\n")
    return output, duration

def clean_folders():
    for folder in ("dist", "build", ".hatch"):
        f = root / folder
        if f.exists():
            shutil.rmtree(f)

def build_and_install():
    run_capture([sys.executable, "-m", "hatch", "build"], "Building wheel")
    wheels = list(dist.glob("*.whl"))
    if not wheels:
        raise RuntimeError("❌ No wheel found in dist folder!")
    latest_wheel = max(wheels, key=os.path.getmtime)
    run_capture([sys.executable, "-m", "pip", "install", "--upgrade", str(latest_wheel)], "Installing wheel")

def fix_boosted_file(path: Path):
    boosted = path.with_name(path.stem + "_autonumba.py")
    if not boosted.exists():
        print(f"▶ Generating boosted file {boosted.name}...")
        # disable Rich/emoji output on Windows
        run_capture([sys.executable, "-m", "autonumba", str(path), "--no-rich"], "Boosting original script")
        if not boosted.exists():
            raise FileNotFoundError(f"❌ Boosted file still missing: {boosted}")
    return boosted

def parse_activities(output):
    activities = {}
    patterns = [
        r"Matrix multiply done in ([0-9.]+) seconds",
        r"Fibonacci done in ([0-9.]+) seconds",
        r"Heavy loop done in ([0-9.]+) seconds"
    ]
    names = ["Matrix multiply", "Fibonacci", "Heavy loop"]
    for name, pat in zip(names, patterns):
        match = re.search(pat, output)
        activities[name] = float(match.group(1)) if match else None
    return activities

def write_results_md(timings, outputs):
    md = "# 🚀 autonumba Benchmark Results per Activity\n\n"
    activities = ["Matrix multiply", "Fibonacci", "Heavy loop"]

    md += "| Activity | Original 🐍 (s) | Boosted 🔥 (s) | Faster % | Speed-up | Winner |\n"
    md += "|----------|----------------|----------------|-----------|----------|--------|\n"

    for act in activities:
        orig_time = timings["Original 🐍"].get(act)
        boost_time = timings["Boosted 🔥"].get(act)

        if orig_time and boost_time:
            faster_percent = ((orig_time - boost_time) / orig_time) * 100
            speedup = orig_time / boost_time
        else:
            faster_percent, speedup = "-", "-"

        winner = "Original 🐍"
        if boost_time and orig_time and boost_time < orig_time:
            winner = "Boosted 🔥"

        orig_str = f"{orig_time:.4f}" if orig_time else "-"
        boost_str = f"{boost_time:.4f}" if boost_time else "-"
        faster_str = f"{faster_percent:.2f}%" if faster_percent != "-" else "-"
        speedup_str = f"{speedup:.2f}x" if speedup != "-" else "-"

        md += f"| {act} | {orig_str} | {boost_str} | {faster_str} | {speedup_str} | {winner} |\n"

    md += "\n"

    for name in ["Original 🐍", "Boosted 🔥"]:
        out = outputs.get(name, "")
        md += f"## 📝 {name} Output\n```\n{out}\n```\n\n"

    results_file.write_text(md, encoding="utf-8")
    print("📄 RESULTS.md written with per-activity benchmark summary.")

def main():
    clean_folders()
    build_and_install()
    boosted_main_fixed = fix_boosted_file(example_main)

    runs = [
        ("Original 🐍", [sys.executable, "-u", str(example_main)]),
        ("Boosted 🔥", [sys.executable, "-u", str(boosted_main_fixed)]),
    ]

    timings = {}
    outputs = {}

    for name, cmd in runs:
        out, _ = run_capture(cmd, desc=name)
        outputs[name] = out
        timings[name] = parse_activities(out)

    write_results_md(timings, outputs)

if __name__ == "__main__":
    main()
    