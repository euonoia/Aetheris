/* ============================================================
   ROADWATCH frontend — captures frames and draws server results.
   All detection/tracking/violation logic now lives in the FastAPI
   backend; this file just streams frames over a WebSocket and
   renders whatever comes back.
   ============================================================ */

const video = document.getElementById('video');
const overlay = document.getElementById('overlay');
const ctx = overlay.getContext('2d');
const stageEmpty = document.getElementById('stageEmpty');
const captureCanvas = document.createElement('canvas'); // off-screen, for JPEG capture

let ws = null;
let wsReady = false;
let sending = false; // avoid overlapping frame sends

// zones — every kind is an array so multiple can coexist (same shape as before)
let zones = { stoplines: [], directions: [], noparkings: [], gatePairs: [] };
let zoneMode = '';
let zoneClickBuffer = [];
let pendingGateA = null;
let zoneHistory = [];

let lastTracks = [];
let violationCards = new Set();

// ---------- server AI status ----------
fetch('/api/config').then(r => r.json()).then(cfg => {
  const el = document.getElementById('aiStatus');
  el.className = 'ai-status ' + (cfg.ai_enabled ? 'on' : 'off');
  el.textContent = cfg.ai_enabled
    ? 'AI review is ON (server has GROQ_API_KEY configured) — violations are auto-verified, motorcycles checked for helmets/overload.'
    : 'AI review is OFF — set GROQ_API_KEY on the server to enable it.';
}).catch(() => {});

// ---------- WebSocket ----------
function connectWs() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/ws/track`);
  ws.onopen = () => { wsReady = true; setWsBadge('connected'); };
  ws.onclose = () => { wsReady = false; setWsBadge('disconnected'); setTimeout(connectWs, 1500); };
  ws.onerror = () => { setWsBadge('error'); };
  ws.onmessage = (evt) => {
    sending = false;
    let msg;
    try { msg = JSON.parse(evt.data); } catch (e) { return; }
    if (msg.type === 'result') handleResult(msg);
    else if (msg.type === 'error') console.warn('server error:', msg.error);
  };
}
function setWsBadge(state) {
  const dot = document.getElementById('wsDot');
  const label = document.getElementById('wsLabel');
  dot.className = 'dot ' + (state === 'connected' ? 'green' : state === 'error' ? 'red' : '');
  label.textContent = 'SERVER: ' + state.toUpperCase();
}
connectWs();

// ---------- zone status ----------
function updateZoneStatus() {
  document.getElementById('zoneStatus').textContent =
    pendingGateA ? 'Gate A set — click 2 points for Gate B' :
    zoneClickBuffer.length === 1 ? 'One point placed — click one more' : '';
}
function pushZone(arrName, item) { zones[arrName].push(item); zoneHistory.push({ arrName, item }); }

// ---------- video input ----------
document.getElementById('videoFile').addEventListener('change', e => {
  const f = e.target.files[0];
  if (!f) return;
  video.srcObject = null;
  video.src = URL.createObjectURL(f);
  video.loop = true;
  prepareVideo();
});
document.getElementById('webcamBtn').addEventListener('click', async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.src = '';
    video.srcObject = stream;
    prepareVideo();
  } catch (e) { alert('Could not access webcam: ' + e.message); }
});
function prepareVideo() {
  stageEmpty.style.display = 'none';
  video.addEventListener('loadedmetadata', () => {
    overlay.width = video.videoWidth;
    overlay.height = video.videoHeight;
    captureCanvas.width = video.videoWidth;
    captureCanvas.height = video.videoHeight;
    video.play();
    document.getElementById('playBtn').disabled = false;
    document.getElementById('pauseBtn').disabled = false;
    document.getElementById('modelStatus').textContent = 'streaming to server…';
    startLoop();
  }, { once: true });
}
document.getElementById('playBtn').addEventListener('click', () => video.play());
document.getElementById('pauseBtn').addEventListener('click', () => video.pause());

// ---------- zone drawing (identical UX to the original) ----------
document.getElementById('zoneMode').addEventListener('change', e => {
  zoneMode = e.target.value; zoneClickBuffer = []; pendingGateA = null; updateZoneStatus();
});
overlay.addEventListener('click', e => {
  if (!zoneMode) return;
  const rect = overlay.getBoundingClientRect();
  const scaleX = overlay.width / rect.width, scaleY = overlay.height / rect.height;
  const x = (e.clientX - rect.left) * scaleX, y = (e.clientY - rect.top) * scaleY;
  zoneClickBuffer.push({ x, y });
  if (zoneClickBuffer.length === 2) {
    const line = [zoneClickBuffer[0], zoneClickBuffer[1]];
    zoneClickBuffer = [];
    if (zoneMode === 'stopline') pushZone('stoplines', line);
    else if (zoneMode === 'direction') pushZone('directions', line);
    else if (zoneMode === 'noparking') pushZone('noparkings', line);
    else if (zoneMode === 'gate') {
      if (!pendingGateA) { pendingGateA = line; }
      else {
        const distStr = prompt('Real-world distance between Gate A and Gate B, in meters:', '15');
        const distance = parseFloat(distStr) || 15;
        pushZone('gatePairs', { a: pendingGateA, b: line, distance_m: distance });
        pendingGateA = null;
      }
    }
  }
  updateZoneStatus();
});
document.getElementById('undoZone').addEventListener('click', () => {
  const last = zoneHistory.pop();
  if (!last) return;
  const arr = zones[last.arrName];
  const idx = arr.indexOf(last.item);
  if (idx > -1) arr.splice(idx, 1);
});
document.getElementById('clearZones').addEventListener('click', () => {
  zones = { stoplines: [], directions: [], noparkings: [], gatePairs: [] };
  zoneHistory = []; pendingGateA = null; zoneClickBuffer = []; updateZoneStatus();
});

// ---------- settings ----------
function currentSettings() {
  return {
    speed_limit_kmh: parseFloat(document.getElementById('speedLimit').value) || 40,
    meters_per_100px: parseFloat(document.getElementById('pxScale').value) || 5,
    dwell_seconds: parseFloat(document.getElementById('dwellSeconds').value) || 6,
    max_riders: parseInt(document.getElementById('maxRiders').value) || 2,
    detect_interval_ms: parseInt(document.getElementById('detectInterval').value) || 250,
  };
}

// ---------- main capture/send loop ----------
let lastSendTime = 0;
function startLoop() {
  function loop(ts) {
    requestAnimationFrame(loop);
    if (!wsReady || video.paused || video.ended || sending) return;
    const settings = currentSettings();
    if (ts - lastSendTime < settings.detect_interval_ms) return;
    lastSendTime = ts;
    sendFrame(settings);
  }
  requestAnimationFrame(loop);
}
function sendFrame(settings) {
  const cctx = captureCanvas.getContext('2d');
  cctx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);
  const dataUrl = captureCanvas.toDataURL('image/jpeg', 0.7);
  sending = true;
  ws.send(JSON.stringify({ type: 'frame', image: dataUrl, zones, settings }));
}

// ---------- render server results ----------
function handleResult(msg) {
  document.getElementById('modelStatus').textContent = 'live';
  setSignal(msg.signal);
  lastTracks = msg.tracks;

  document.getElementById('statTracked').textContent = msg.stats.tracked;
  document.getElementById('statFlagged').textContent = msg.stats.flagged;
  document.getElementById('statConfirmed').textContent = msg.stats.confirmed;
  document.getElementById('statDismissed').textContent = msg.stats.dismissed;

  (msg.new_violations || []).forEach(renderViolation);
  (msg.violation_updates || []).forEach(v => {
    if (!violationCards.has(v.local_id)) renderViolation(v); // AI-only detections (helmet/overload) arrive as updates
    updateViolationUI(v);
  });

  drawOverlay();
  updateTelemetry();
  updateVehiclesTab();
}

function setSignal(s) {
  document.getElementById('signalDot').className = 'dot ' + (s === 'unknown' ? '' : s);
  document.getElementById('signalLabel').textContent = 'SIGNAL: ' + s.toUpperCase();
}

// ---------- violations list ----------
function renderViolation(v) {
  const list = document.getElementById('violationsList');
  const empty = list.querySelector('.empty-note'); if (empty) empty.remove();
  const div = document.createElement('div');
  div.className = 'vlog-item';
  div.id = v.local_id;
  div.innerHTML = `
    <img src="${v.snapshot}" alt="violation snapshot">
    <div class="vlog-meta">
      <div class="vlog-top">
        <span class="vtype ${v.violation_type}">${v.violation_type.replace('_', ' ')}</span>
        <span class="status pending" data-role="status">reviewing…</span>
      </div>
      <p>Track #${v.track_id} · ${v.vehicle_type} · ${v.zone_name}${v.detected_speed ? ' · ' + v.detected_speed.toFixed(1) + ' km/h' : ''}</p>
      <p>${new Date(v.occurred_at).toLocaleTimeString()}</p>
      <div class="reasoning" data-role="reasoning"></div>
    </div>`;
  list.prepend(div);
  violationCards.add(v.local_id);
}
function updateViolationUI(v) {
  const el = document.getElementById(v.local_id);
  if (!el) return;
  const statusEl = el.querySelector('[data-role="status"]');
  statusEl.textContent = v.verdict;
  statusEl.className = 'status ' + v.verdict;
  el.querySelector('[data-role="reasoning"]').textContent = v.reasoning || '';
}

// ---------- tracked vehicles tab ----------
function updateVehiclesTab() {
  const list = document.getElementById('vehiclesList');
  list.innerHTML = '';
  if (lastTracks.length === 0) { list.innerHTML = '<div class="empty-note">No vehicles tracked yet.</div>'; return; }
  lastTracks.forEach(t => {
    const div = document.createElement('div');
    div.className = 'vlog-item';
    div.innerHTML = `<div class="vlog-meta">
      <div class="vlog-top"><span class="vtype" style="background:rgba(242,201,76,.12);color:var(--lane-yellow);">#${t.id}</span><span style="font-family:var(--font-mono);font-size:11px;color:var(--text-mid);">${t.type}</span></div>
      <p>${t.speed_kmh != null ? t.speed_kmh.toFixed(1) + ' km/h (' + t.speed_source + ')' : 'measuring speed…'}${t.type === 'motorcycle' ? ' · ' + t.rider_estimate + ' rider(s) est.' : ''}</p>
    </div>`;
    list.appendChild(div);
  });
}

// ---------- telemetry strip ----------
function updateTelemetry() {
  const strip = document.getElementById('telemetry');
  strip.innerHTML = '';
  lastTracks.slice(-14).forEach(t => {
    const chip = document.createElement('div');
    chip.className = 'chip';
    chip.innerHTML = `<span class="id">#${t.id}</span><span class="type">${t.type}</span>` +
      (t.speed_kmh != null ? `<span class="spd ${t.speed_source === 'est' ? 'est' : ''}">${t.speed_kmh.toFixed(0)} km/h</span>` : '') +
      (t.flagged ? `<span class="flag">⚑</span>` : '');
    strip.appendChild(chip);
  });
}

// ---------- overlay drawing ----------
function drawOverlay() {
  ctx.clearRect(0, 0, overlay.width, overlay.height);
  ctx.lineWidth = 2; ctx.font = '13px "JetBrains Mono", monospace';

  zones.stoplines.forEach((l, i) => drawLine(l, '#e5484d', 'STOP ' + i));
  zones.directions.forEach((l, i) => drawArrow(l, '#3ddc8c', 'DIR ' + i));
  zones.noparkings.forEach((r, i) => drawRect(r, '#f2c94c', 'NO PARK ' + i));
  zones.gatePairs.forEach((p, i) => { drawLine(p.a, '#5aa9ff', 'GATE ' + i + 'A'); drawLine(p.b, '#5aa9ff', 'GATE ' + i + 'B'); });
  if (pendingGateA) drawLine(pendingGateA, '#5aa9ff', 'GATE A (pending)');

  lastTracks.forEach(t => {
    const [x, y, w, h] = t.bbox;
    ctx.strokeStyle = t.flagged ? '#e5484d' : '#f2c94c';
    ctx.strokeRect(x, y, w, h);
    ctx.fillStyle = t.flagged ? '#e5484d' : '#f2c94c';
    let label = `#${t.id} ${t.type}`;
    if (t.speed_kmh != null) label += ' ' + t.speed_kmh.toFixed(0) + 'km/h';
    if (t.type === 'motorcycle') label += ' ' + t.rider_estimate + 'p';
    ctx.fillText(label, x, y > 16 ? y - 6 : y + h + 16);
  });
}
function drawLine(pts, color, label) {
  ctx.strokeStyle = color; ctx.beginPath();
  ctx.moveTo(pts[0].x, pts[0].y); ctx.lineTo(pts[1].x, pts[1].y); ctx.stroke();
  ctx.fillStyle = color; ctx.fillText(label, (pts[0].x + pts[1].x) / 2, (pts[0].y + pts[1].y) / 2 - 6);
}
function drawArrow(pts, color, label) {
  drawLine(pts, color, label);
  const angle = Math.atan2(pts[1].y - pts[0].y, pts[1].x - pts[0].x);
  ctx.beginPath();
  ctx.moveTo(pts[1].x, pts[1].y);
  ctx.lineTo(pts[1].x - 12 * Math.cos(angle - 0.4), pts[1].y - 12 * Math.sin(angle - 0.4));
  ctx.moveTo(pts[1].x, pts[1].y);
  ctx.lineTo(pts[1].x - 12 * Math.cos(angle + 0.4), pts[1].y - 12 * Math.sin(angle + 0.4));
  ctx.stroke();
}
function drawRect(pts, color, label) {
  ctx.strokeStyle = color;
  const x = Math.min(pts[0].x, pts[1].x), y = Math.min(pts[0].y, pts[1].y);
  const w = Math.abs(pts[1].x - pts[0].x), h = Math.abs(pts[1].y - pts[0].y);
  ctx.strokeRect(x, y, w, h);
  ctx.fillStyle = color; ctx.fillText(label, x + 4, y + 14);
}

// ---------- tabs ----------
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
  });
});
