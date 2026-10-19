// Phone app logic: settings, camera, location, call the ML server, show advice.
const $ = (id) => document.getElementById(id);
const BADGE = { yes: "✂️ Yes, trim now", light: "🌿 Light touch only", no: "✋ Don't trim now" };
const SETTINGS_KEY = "hydrangea-settings";
let coords = null;

function loadSettings() { try { return JSON.parse(localStorage.getItem(SETTINGS_KEY)) || null; } catch { return null; } }

async function init() {
  const species = await fetch("api/species").then((r) => r.json());
  for (const [value, text] of Object.entries(species)) $("species").add(new Option(text, value));
  const s = loadSettings();
  if (s) { $("species").value = s.species; $("age").value = s.age ?? ""; $("height").value = s.height ?? ""; }
  else { $("species").value = "unknown"; $("settings").hidden = false; } // first run: ask about the plant
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
  askLocation();
}

function askLocation() {
  navigator.geolocation?.getCurrentPosition(
    (p) => (coords = { lat: p.coords.latitude, lon: p.coords.longitude }),
    () => (coords = null), // refused or unavailable: advice just ignores weather
    { maximumAge: 3600e3, timeout: 10e3 });
}

$("settingsBtn").onclick = () => ($("settings").hidden = !$("settings").hidden);
$("saveSettings").onclick = () => {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify({ species: $("species").value, age: $("age").value, height: $("height").value }));
  $("settings").hidden = true;
};

// Shrink the photo on the phone before upload: faster on mobile data, and the model only needs ~224px anyway.
function shrink(file, maxSide = 1024) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const k = Math.min(1, maxSide / Math.max(img.width, img.height));
      const c = Object.assign(document.createElement("canvas"), { width: img.width * k, height: img.height * k });
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      c.toBlob((b) => (b ? resolve(b) : reject(new Error("Couldn't read photo"))), "image/jpeg", 0.85);
      URL.revokeObjectURL(img.src);
    };
    img.onerror = () => reject(new Error("Couldn't read photo"));
    img.src = URL.createObjectURL(file);
  });
}

async function analyse(file) {
  if (!file) return;
  for (const id of ["result", "error", "settings"]) $(id).hidden = true;
  $("preview").src = URL.createObjectURL(file); $("preview").hidden = false;
  $("loading").hidden = false;
  try {
    const s = loadSettings() || { species: $("species").value };
    const form = new FormData();
    form.append("photo", await shrink(file), "photo.jpg");
    form.append("species", s.species || "unknown");
    if (s.age) form.append("age_years", s.age);
    if (s.height) form.append("height_cm", s.height);
    if (coords) { form.append("lat", coords.lat); form.append("lon", coords.lon); }
    const res = await fetch("api/analyze", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Something went wrong");
    show(data);
  } catch (e) {
    $("error").textContent = navigator.onLine ? `Sorry: ${e.message}. Please try again.` : "You're offline. Connect to the internet and try again.";
    $("error").hidden = false;
  } finally {
    $("loading").hidden = true;
  }
}

function show(d) {
  $("badge").textContent = BADGE[d.trim_now];
  $("badge").className = `badge ${d.trim_now}`;
  $("headline").textContent = d.headline;
  $("howFar").textContent = d.how_far ? `How far: ${d.how_far}` : "";
  $("notes").replaceChildren(...d.notes.map((n) => Object.assign(document.createElement("li"), { textContent: n })));
  $("weather").textContent = d.weather ? `🌦️ ${d.weather}` : "";
  const fmt = (t) => `${t.label.replace("_", " ")} (${Math.round(t.confidence * 100)}%${t.unsure ? ", not sure" : ""})`;
  $("seen").textContent = `Health: ${fmt(d.health)} · Stage: ${fmt(d.stage)} · ${d.health.method} model`;
  $("result").hidden = false;
  $("result").scrollIntoView({ behavior: "smooth" });
}

for (const id of ["photo", "gallery"]) $(id).onchange = (e) => { analyse(e.target.files[0]); e.target.value = ""; };
init();
