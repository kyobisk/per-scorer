"""Record one narration clip per walkthrough caption with macOS `say`.

Usage: python3 tools/narrate.py "Ava (Premium)" [words-per-minute]

Writes narration/NN.m4a, then stores each clip's length in
per-walkthrough.html (the NARRATION block) so the player can hold the frame
wherever a line needs more time than its slot.
"""
import json, re, subprocess, sys, pathlib, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGE = ROOT / "per-walkthrough.html"
OUT = ROOT / "narration"

voice = sys.argv[1] if len(sys.argv) > 1 else "Samantha"
rate = sys.argv[2] if len(sys.argv) > 2 else "180"

# `say` falls back to the default voice when the named one is missing, so check first.
listing = subprocess.run(["say", "-v", "?"], capture_output=True, text=True).stdout.splitlines()
installed = dict(m.groups() for m in (re.match(r"(.+?)\s+([a-z]{2,3}[_-]\w+)\s", line) for line in listing) if m)
if voice not in installed:
    english = sorted(n for n, loc in installed.items() if loc.startswith("en"))
    sys.exit(f'Voice "{voice}" is not installed, so nothing was recorded.\n'
             f'Installed English voices: {", ".join(english)}')

src = PAGE.read_text()
block = re.search(r"const CAPTIONS = \[(.*?)\n\];", src, re.S).group(1)
caps = [(float(t), txt) for t, txt in re.findall(r"\[([\d.]+),'([^']*)'\]", block)]
END = float(re.search(r"const END = (\d+)", src).group(1))

# Spoken wording where the caption text reads badly aloud.
SPOKEN = {
    "PER 1": "P.E.R. one",
    "PER ": "P.E.R. ",
    "fps": "F.P.S.",
    "CSV": "C.S.V.",
    " ID": " I.D.",
    "key E": "key, E",
}
def spoken(text):
    for a, b in SPOKEN.items():
        text = text.replace(a, b)
    return text

OUT.mkdir(parents=True, exist_ok=True)
clips, held = [], 0.0
for i, (t, text) in enumerate(caps):
    if not text:
        continue
    slot_end = caps[i + 1][0] if i + 1 < len(caps) else END
    name = f"{i:02d}.m4a"
    with tempfile.TemporaryDirectory() as tmp:
        aiff = pathlib.Path(tmp) / "clip.aiff"
        subprocess.run(["say", "-v", voice, "-r", rate, "-o", str(aiff), spoken(text)], check=True)
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", str(aiff), str(OUT / name)], check=True)
    info = subprocess.run(["afinfo", str(OUT / name)], capture_output=True, text=True).stdout
    dur = round(float(re.search(r"estimated duration: ([\d.]+)", info).group(1)), 2)
    clips.append({"t": t, "file": name, "dur": dur})
    extra = t + dur + 0.4 - slot_end
    if extra > 0:
        held += extra
        print(f"  hold {extra:4.1f}s after {t:6.1f}s  {text[:56]}")

data = json.dumps({"voice": voice, "clips": clips}, separators=(",", ":"))
html, n = re.subn(r"/\*NARRATION\*/.*?/\*END NARRATION\*/",
                  lambda m: "/*NARRATION*/const NARRATION = " + data + ";/*END NARRATION*/",
                  src, count=1, flags=re.S)
assert n == 1, "NARRATION block not found in per-walkthrough.html"
PAGE.write_text(html)
print(f"{len(clips)} clips with {voice}; holds add {held:.1f}s, total {END + held:.0f}s")
