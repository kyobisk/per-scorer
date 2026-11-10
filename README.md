# PER Scorer

Score proboscis extension responses (PER) for individual harnessed honey bees from video. Press a key when a behavior starts and again when it stops; PER Scorer turns those labels into a PER result, latency and time spent in each behavior, and exports them as CSV.

**Site:** https://kyobisk.github.io/per-scorer/

| Page | What it is |
| --- | --- |
| [`index.html`](index.html) | Landing page for students |
| [`per-scorer.html`](per-scorer.html) | The scoring tool. A single self-contained file; runs entirely in the browser and uploads nothing. |
| [`per-walkthrough.html`](per-walkthrough.html) | A narrated, video-style demo of scoring one bee |
| [`PER-Scorer-Student-Tutorial.pdf`](PER-Scorer-Student-Tutorial.pdf) | Student tutorial: behavior definitions, step-by-step use, analysis, practice questions, shortcut card. Source in `tutorial/`. |

## Scoring

Each bee's whole recording is one trial. A bee scores PER 1 if at least one full proboscis extension is labeled; latency is the time from 0:00 (the start of the video) to the first one. Which behaviors count as a PER can be changed under **Scoring rules**. For several trials per video, add a behavior that marks each trial's start and choose it as the trial onset.

Videos can be opened from a file or from a direct link to a video file. **Crop** zooms the video panel to a box drawn around the bee (saved per bee; new bees copy the previous crop). **Trim** sets a start and end per bee: the start becomes 0:00 for latency, the trimmed span is the recording length for proportions, and labels outside it are greyed out and excluded. The video file itself is never changed; exports give times from the trim start, plus `video_start_s`, `in_trim`, `trim_start_s` and `trim_end_s`. A link can also be passed in the address, so a class can open the same clip: `per-scorer.html?video=https://example.org/bee07.mp4`.

### Ethogram

PER Scorer starts with no behaviors: students build their own ethogram. The form under the behavior keys adds a behavior with a name, a key, start/stop or point, and an optional **Counts as PER** tick; PER shows as "not set" until one behavior counts. **Edit keys & behaviors** opens the editor for renaming, recoloring, changing keys or removing unused behaviors. **Export ethogram** saves the behaviors, keys and PER rule as a small JSON file that students load with **Import ethogram…**. Ticking **Lock behavior names** (saved in the exported file) limits students to changing keys and colors, so pooled data keeps the same columns. **Start new project** (under Data) clears everything.

### Analysis

The Analysis panel compares bees by Group or by any condition added under the bee list (e.g. Colony, Day):

- **Time budget**: proportion of recording (default), total time, number of bouts or mean bout length per behavior, plotted as one point per bee with a line at each group's median; the table shows median (IQR). Each bee's recording length is read from the video and can be edited.
- **PER by condition**: responders and mean latency per group.
- **Transitions**: a row-normalized matrix of which behavior follows which, pooled over the selected bees, with optional idle gaps and self-transitions.
- Exploratory tests (Mann–Whitney / Kruskal–Wallis, Fisher's exact / chi-square), not corrected for multiple comparisons. **Time budget CSV** and **Transitions CSV** export per-bee data for formal analysis.

### Saving

Work is saved automatically as students go: labels and settings in local storage, and videos opened from a file in IndexedDB, so reopening the page returns to the same bee, video and moment. If a video cannot be kept (too large, or a different computer), the scorer asks for that file again by name. A banner warns when the page is open in two tabs. Browser storage is per computer and can be cleared, so students should still use **Save project (.json)** at the end of each session.

## Embedding in Canvas

Link to the pages, or embed the walkthrough in a Canvas page with the HTML editor:

```html
<iframe src="https://kyobisk.github.io/per-scorer/per-walkthrough.html"
        width="100%" height="820" style="border:0"
        allow="fullscreen" allowfullscreen title="PER Scorer walkthrough"></iframe>
```

The scorer works best opened in its own tab.

## Re-recording the narration

The walkthrough's voice-over is a set of clips in `narration/`, recorded with [Kokoro](https://github.com/thewh1teagle/kokoro-onnx), a free neural text-to-speech model that runs offline. After editing the `CAPTIONS` in `per-walkthrough.html`, record them again:

```bash
python3 tools/narrate.py kokoro:af_heart
```

The script records one clip per caption, converts it to AAC, and writes each clip's length into the page so the player can hold the frame when a line needs more time than its slot. An optional second argument sets the speed (e.g. `1.1`). Kokoro needs a one-time setup (a Python environment in `.venv` and about 120 MB of model files in `.models`, both ignored by Git); the steps are at the top of `tools/narrate.py`. A macOS voice also works, e.g. `python3 tools/narrate.py Samantha`.

## Rebuilding the tutorial PDF

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --no-pdf-header-footer \
  --print-to-pdf=PER-Scorer-Student-Tutorial.pdf "file://$PWD/tutorial/per-scorer-tutorial.html"
```
