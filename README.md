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

Videos can be opened from a file or from a direct link to a video file. A link can also be passed in the address, so a class can open the same clip: `per-scorer.html?video=https://example.org/bee07.mp4`.

### Ethogram

By default students can change each behavior's key and color, but not its name, so everyone's exports have the same columns. **Edit keys & behaviors → Allow renaming, adding and removing behaviors** unlocks full editing. **Export ethogram** saves the behaviors, keys and PER rules as a small JSON file that students load with **Import ethogram…**; **Reset to defaults** restores the standard keys.

### Analysis

The Analysis panel compares bees by Group or by any condition added under the bee list (e.g. Colony, Day):

- **Time budget**: proportion of recording (default), total time, number of bouts or mean bout length per behavior, plotted as one point per bee with a line at each group's median; the table shows median (IQR). Each bee's recording length is read from the video and can be edited.
- **PER by condition**: responders and mean latency per group.
- **Transitions**: a row-normalized matrix of which behavior follows which, pooled over the selected bees, with optional idle gaps and self-transitions.
- Exploratory tests (Mann–Whitney / Kruskal–Wallis, Fisher's exact / chi-square), not corrected for multiple comparisons. **Time budget CSV** and **Transitions CSV** export per-bee data for formal analysis.

Labels are kept in the browser's local storage. Students should use **Save project (.json)** at the end of each session.

## Embedding in Canvas

Link to the pages, or embed the walkthrough in a Canvas page with the HTML editor:

```html
<iframe src="https://kyobisk.github.io/per-scorer/per-walkthrough.html"
        width="100%" height="820" style="border:0"
        allow="fullscreen" allowfullscreen title="PER Scorer walkthrough"></iframe>
```

The scorer works best opened in its own tab.

## Re-recording the narration

The walkthrough's voice-over is a set of clips in `narration/`, recorded with macOS text-to-speech. After editing the `CAPTIONS` in `per-walkthrough.html`, record them again:

```bash
python3 tools/narrate.py "Ava (Premium)"
```

The script records one clip per caption, converts it to AAC, and writes each clip's length into the page so the player can hold the frame when a line needs more time than its slot. Premium voices are a free download in System Settings → Accessibility → Spoken Content → System voice → Manage Voices.

## Rebuilding the tutorial PDF

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --no-pdf-header-footer \
  --print-to-pdf=PER-Scorer-Student-Tutorial.pdf "file://$PWD/tutorial/per-scorer-tutorial.html"
```
