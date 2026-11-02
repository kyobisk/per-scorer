import re, pathlib
f = pathlib.Path("per-walkthrough.html"); s = f.read_text()

caps = r"""const CAPTIONS = [
  [0,''],
  [6,'PER Scorer turns key presses into proboscis extension data. Let’s score one bee, start to finish.'],
  [9,'First, add the bee. Type its ID, holder number and treatment group.'],
  [17.5,'Click Add. The new bee is selected, and its ID appears on the video, so you always know which bee you’re scoring.'],
  [26,'Next, open that bee’s video. You can also drag the file onto the video area.'],
  [31,'Set fps to your camera’s frame rate, so each frame step is exactly one frame.'],
  [36,'No video? Press Space to run a stopwatch and score live instead.'],
  [40,'Press Space to play. Watch the antennae and the mouthparts.'],
  [43.6,'The antennae are moving. Press A.'],
  [45.8,'Press A again when they stop.'],
  [47.3,'The mandibles are opening. Pause, then step forward one frame at a time with the period key.'],
  [51.2,'The proboscis has crossed the line between the mandible tips. That’s a full extension: press P.'],
  [53.4,'Slow playback to half speed, then press Space to keep playing.'],
  [57,'While the bout runs, its key glows amber. Press P again when the proboscis folds back.'],
  [62.4,'The bout now shows on the timeline, and in the event log.'],
  [66.3,'This one never passes the mandibles. That’s a partial extension, key E.'],
  [69.4,'Wrong key? Here, G started a grooming bout by mistake.'],
  [71.6,'Press Z to undo it.'],
  [75.2,'Any time can be corrected. Click it in the event log and type the exact value.'],
  [79.6,'The arrow button jumps the video to that event, so you can check the frame.'],
  [84,'Before moving on, check the log for bouts left open, and for accidental key presses.'],
  [90,'The PER summary scores the bee for you. Any full extension counts, so this bee scores PER 1.'],
  [95,'Latency is the time from the start of the video to the first full extension.'],
  [100,'Your instructor sets the scoring rules. Leave them as they are unless told otherwise.'],
  [104,'Use N and B to move between bees. Each bee keeps its own labels.'],
  [110,'At the end of every session, click Save project. The project file keeps everything.'],
  [116,'Export Events CSV for one row per bout, or Trial summary CSV for one row per bee.'],
  [124,''],
];"""
s, n = re.subn(r"const CAPTIONS = \[.*?\n\];", lambda m: caps, s, count=1, flags=re.S); assert n == 1

player = r"""/* ---------- narration: recorded clips, with holds where a line needs more time than its slot ---------- */
/*NARRATION*/const NARRATION = {"voice":"","clips":[]};/*END NARRATION*/
const HOLDS = [];
NARRATION.clips.forEach(c=>{
  const i = CAPTIONS.findIndex(x=>x[0]===c.t); if(i<0) return;
  const slotEnd = i+1 < CAPTIONS.length ? CAPTIONS[i+1][0] : END;
  const extra = c.t + c.dur + 0.4 - slotEnd;
  if(extra > 0) HOLDS.push({at: slotEnd - 0.001, dur: extra});
});
const HELD = HOLDS.reduce((a,h)=>a+h.dur, 0), TOTAL = END + HELD;
function sOf(R){ let acc = 0; for(const h of HOLDS){ if(R < h.at+acc) return R-acc; if(R < h.at+acc+h.dur) return h.at; acc += h.dur; } return R-acc; }
function rOf(sc){ let acc = 0; for(const h of HOLDS){ if(h.at < sc) acc += h.dur; } return sc+acc; }

/* ---------- player (T is real time; the script runs on s = sOf(T)) ---------- */
let T = 0, playing = false, speed = 1, lastTs = null, lastCap = null, voice = true, captionsOn = true;
function frame(ts){
  if(playing){
    if(lastTs!=null) T += Math.min(0.1, (ts-lastTs)/1000)*speed;
    if(T >= TOTAL){ T = TOTAL; setPlaying(false); }
  }
  lastTs = ts;
  render();
  requestAnimationFrame(frame);
}
function render(){
  const sc = sOf(T);
  const s = stateAt(sc), v = s.loaded ? V(sc) : 0, b = s.bees.find(x=>x.id===s.cur);
  renderDom(s, sc, v);
  if(s.loaded) drawBee(v, T, sc>=47.3 && sc<57); else { vctx.setTransform(2,0,0,2,0,0); vctx.fillStyle = '#0b0e11'; vctx.fillRect(0,0,778,340); }
  drawTL(b, v, s.loaded);
  drawOverlays(s, sc);
  // player chrome
  const capRow = at(CAPTIONS, sc), cap = capRow[1];
  if(cap !== lastCap){ lastCap = cap; $('capText').textContent = cap; if(audioFailed) speak(cap); }
  syncAudio(capRow[0]);
  const pct = T/TOTAL*100; $('fill').style.width = pct+'%'; $('knob').style.left = pct+'%';
  $('scrub').setAttribute('aria-valuenow', Math.round(T));
  $('time').textContent = mmss(T)+' / '+mmss(TOTAL);
  const ci = CHAPTERS.findIndex((c,i)=>sc>=c[0] && (i===CHAPTERS.length-1 || sc<CHAPTERS[i+1][0]));
  $('chapNow').textContent = `Chapter ${ci+1} of ${CHAPTERS.length} · ${CHAPTERS[ci][1]}`;
  document.querySelectorAll('.chap').forEach((el,i)=>el.classList.toggle('on', i===ci));
  $('bigplay').classList.toggle('show', !playing && (sc<5 || sc>=124));
}
const mmss = t => Math.floor(t/60)+':'+String(Math.floor(t%60)).padStart(2,'0');
function setPlaying(p){
  if(p && T >= TOTAL) T = 0;
  playing = p; lastTs = null;
  $('playBtn').setAttribute('aria-label', p ? 'Pause' : 'Play');
  $('playIcon').innerHTML = p ? '<rect x="6" y="4" width="4" height="16" fill="currentColor"/><rect x="14" y="4" width="4" height="16" fill="currentColor"/>' : '<path d="M7 4l13 8-13 8z" fill="currentColor"/>';
  if(!p){ stopSpeech(); audio.pause(); } else { lastCap = null; }
}
function seek(t){ T = Math.max(0, Math.min(TOTAL, t)); lastCap = null; stopSpeech(); audio.pause(); }

/* recorded narration; falls back to the browser's voice if the clips cannot load */
const audio = new Audio(); audio.preload = 'auto';
let audioFailed = NARRATION.clips.length === 0, loadedClip = null;
audio.addEventListener('error', ()=>{ if(audio.getAttribute('src')){ audioFailed = true; lastCap = null; } });
function syncAudio(capT){
  if(audioFailed) return;
  const clip = NARRATION.clips.find(c=>c.t===capT);
  if(!voice || !playing || !clip){ if(!audio.paused) audio.pause(); return; }
  const offset = (T - rOf(clip.t)) ;
  if(offset < 0 || offset > clip.dur){ if(!audio.paused) audio.pause(); return; }
  if(loadedClip !== clip){ loadedClip = clip; audio.src = 'narration/'+clip.file; }
  audio.playbackRate = speed;
  if(Math.abs(audio.currentTime - offset) > 0.35){ try{ audio.currentTime = offset; }catch(e){} }
  if(audio.paused) audio.play().catch(()=>{});
}
let bestVoice = null;
function pickVoice(){
  try{
    const vs = speechSynthesis.getVoices().filter(v=>/^en/i.test(v.lang));
    const rank = v => /premium|natural|neural/i.test(v.name) ? 0 : /enhanced|google us english|aria|jenny|samantha/i.test(v.name) ? 1 : /en-US/i.test(v.lang) ? 2 : 3;
    bestVoice = vs.sort((a,b)=>rank(a)-rank(b))[0] || null;
  }catch(e){}
}
try{ pickVoice(); speechSynthesis.onvoiceschanged = pickVoice; }catch(e){}
function speak(text){
  if(!voice || !playing || !text) return;
  try{ speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance(text); if(bestVoice) u.voice = bestVoice; u.rate = Math.min(1.6, speed); speechSynthesis.speak(u); }catch(e){}
}
function stopSpeech(){ try{ speechSynthesis.cancel(); }catch(e){} }

$('playBtn').onclick = () => setPlaying(!playing);
$('stage').onclick = () => setPlaying(!playing);
$('speed').onchange = e => { speed = +e.target.value; };
$('ccBtn').onclick = () => { captionsOn = !captionsOn; $('ccBtn').setAttribute('aria-pressed', captionsOn); $('caption').hidden = !captionsOn; fit(); };
$('voiceBtn').onclick = () => {
  voice = !voice; $('voiceBtn').setAttribute('aria-pressed', voice);
  if(voice){ lastCap = null; } else { stopSpeech(); audio.pause(); }
};
$('fsBtn').onclick = () => { const p = $('player'); try{ document.fullscreenElement ? document.exitFullscreen() : p.requestFullscreen().catch(()=>{}); }catch(e){} };

const scrub = $('scrub');
scrub.setAttribute('aria-valuemax', Math.round(TOTAL));
CHAPTERS.slice(1).forEach(([t])=>{ const d = document.createElement('div'); d.className = 'tick'; d.style.left = (rOf(t)/TOTAL*100)+'%'; $('ticks').appendChild(d); });
let dragging = false;
const scrubTo = e => { const r = scrub.getBoundingClientRect(); seek((e.clientX - r.left)/r.width*TOTAL); };
scrub.addEventListener('pointerdown', e=>{ dragging = true; scrub.setPointerCapture(e.pointerId); scrubTo(e); });
scrub.addEventListener('pointermove', e=>{ if(dragging) scrubTo(e); });
scrub.addEventListener('pointerup', ()=>{ dragging = false; });
scrub.addEventListener('keydown', e=>{ if(e.key==='ArrowLeft'){ seek(T-5); e.preventDefault(); } if(e.key==='ArrowRight'){ seek(T+5); e.preventDefault(); } });

$('chapters').innerHTML = CHAPTERS.map(([t,name],i)=>`<button class="chap" data-t="${rOf(t)}"><span class="n">${i+1}</span><span>${name}</span><span class="t">${mmss(rOf(t))}</span></button>`).join('');
document.querySelectorAll('.chap').forEach(b=>b.onclick = () => { seek(+b.dataset.t + 0.01); if(!playing) setPlaying(true); });
$('lenText').textContent = `About ${Math.floor(TOTAL/60)} minutes ${Math.round(TOTAL%60)} seconds`;

"""
s, n = re.subn(r"/\* ---------- player ---------- \*/.*?(?=document\.addEventListener\('keydown')", lambda m: player, s, count=1, flags=re.S); assert n == 1
for a, b in [
  ('<button id="voiceBtn" aria-pressed="false" title="Read captions aloud with your browser\'s voice">Narrate</button>',
   '<button id="voiceBtn" aria-pressed="true" title="Voice-over on or off">Narrate</button>'),
  ('saving the data. About 2 minutes 20 seconds.</p>', 'saving the data. <span id="lenText">About 2 minutes 20 seconds</span>.</p>'),
  ('Click a chapter to jump to it. Turn on Narrate to hear the captions read aloud.', 'Click a chapter to jump to it. Narrate turns the voice-over on or off.'),
]:
    assert s.count(a) == 1, a[:50]; s = s.replace(a, b)
f.write_text(s)
print("patched")
