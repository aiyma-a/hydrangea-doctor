// Phone app: language, settings, photos (several at once), location, call the ML server, show advice.
const $ = (id) => document.getElementById(id);
const MAX_PHOTOS = 6;
const SETTINGS_KEY = "hydrangea-settings"; // {species, plants: {plantKey: {age, height}}}
const EMOJI = { hydrangea: "🌸", rose: "🌹", peony: "🌺", lilac: "💜", tulip: "🌷", iris: "🪻", apple: "🍎", pear: "🍐",
  apricot: "🍑", cherry: "🍒", plum: "🫐", grape: "🍇", raspberry: "🍓", currant: "🔴", unknown: "🌿" };
const LANG_KEY = "hydrangea-lang";

// Screen texts. The advice itself is translated on the server (hydrangea/i18n.py).
const UI = {
  en: {
    title: "Hydrangea Doctor", aboutPlant: "About your plant", plantLabel: "Plant", auto: "🔍 Recognise automatically",
    recognised: "Recognised:", notSureWhich: "I'm not sure which plant this is. Please pick it above.", change: "Not right? Change", type: "Type", age: "Age (years)", height: "Height (cm)",
    savedHint: "Saved on this phone. The app also uses your location for the weather.", save: "Save",
    lead: "Add photos of <b>one plant</b>: a <b>leaf close-up</b> (for health) and the <b>whole plant</b> (for trimming).",
    takePhoto: "Take photo", gallery: "Gallery", check: "Check my plant", looking: "Looking at your plant…",
    whatSaw: "What the model saw", again: "Check another plant", remove: "Remove",
    count: (n) => `${n} of ${MAX_PHOTOS} photos`, tooMany: `Up to ${MAX_PHOTOS} photos at a time.`,
    badge: { yes: "✂️ Yes, trim now", light: "🌿 Light touch only", no: "✋ Don't trim now" },
    howFar: "How far:", health: "Health", stage: "Stage", notSure: "not sure", photo: "Photo",
    offline: "You're offline. Connect to the internet and try again.", failed: "Sorry, something went wrong. Please try again.",
  },
  ru: {
    title: "Доктор Гортензий", aboutPlant: "О вашем растении", plantLabel: "Растение", auto: "🔍 Определить автоматически",
    recognised: "Определено:", notSureWhich: "Не уверена, что это за растение. Выберите его выше.", change: "Неверно? Изменить", type: "Вид", age: "Возраст (лет)", height: "Высота (см)",
    savedHint: "Сохраняется на этом телефоне. Для погоды приложение использует ваше местоположение.", save: "Сохранить",
    lead: "Добавьте фото <b>одного растения</b>: <b>лист крупным планом</b> (здоровье) и <b>куст целиком</b> (обрезка).",
    takePhoto: "Сфотографировать", gallery: "Галерея", check: "Проверить растение", looking: "Смотрю на ваше растение…", slow: "Первая проверка после перерыва может занять до минуты, пока приложение просыпается.",
    whatSaw: "Что увидела модель", again: "Проверить другое растение", remove: "Удалить",
    count: (n) => `${n} из ${MAX_PHOTOS} фото`, tooMany: `Не больше ${MAX_PHOTOS} фото за раз.`,
    badge: { yes: "✂️ Да, обрезайте", light: "🌿 Только слегка", no: "✋ Не обрезайте сейчас" },
    howFar: "Сколько срезать:", health: "Здоровье", stage: "Стадия", notSure: "не уверена", photo: "Фото",
    offline: "Нет интернета. Подключитесь и попробуйте снова.", failed: "Что-то пошло не так. Попробуйте ещё раз.",
  },
  ky: {
    title: "Гортензия Доктуру", aboutPlant: "Өсүмдүгүңүз жөнүндө", plantLabel: "Өсүмдүк", auto: "🔍 Автоматтык түрдө аныктоо",
    recognised: "Аныкталды:", notSureWhich: "Бул кайсы өсүмдүк экенин так биле албадым. Жогорудан тандаңыз.", change: "Туура эмеспи? Өзгөртүү", type: "Түрү", age: "Жашы (жыл)", height: "Бийиктиги (см)",
    savedHint: "Ушул телефондо сакталат. Аба ырайы үчүн колдонмо жайгашкан жериңизди колдонот.", save: "Сактоо",
    lead: "<b>Бир өсүмдүктүн</b> сүрөттөрүн кошуңуз: <b>жалбырагын жакындан</b> (ден соолугу үчүн) жана <b>бадалды толугу менен</b> (кыркуу үчүн).",
    takePhoto: "Сүрөткө тартуу", gallery: "Галерея", check: "Өсүмдүктү текшерүү", looking: "Өсүмдүгүңүздү карап жатам…", slow: "Тыныгуудан кийинки биринчи текшерүү колдонмо ойгонгуча бир мүнөткө чейин созулат.",
    whatSaw: "Модель эмнени көрдү", again: "Башка өсүмдүктү текшерүү", remove: "Өчүрүү",
    count: (n) => `${MAX_PHOTOS} сүрөттөн ${n}`, tooMany: `Бир жолу ${MAX_PHOTOS} сүрөткө чейин.`,
    badge: { yes: "✂️ Ооба, азыр кыркыңыз", light: "🌿 Жеңил гана", no: "✋ Азыр кыркпаңыз" },
    howFar: "Канча кесүү керек:", health: "Ден соолугу", stage: "Баскычы", notSure: "так эмес", photo: "Сүрөт",
    offline: "Интернет жок. Туташып, кайра аракет кылыңыз.", failed: "Бир нерсе туура эмес болду. Кайра аракет кылыңыз.",
  },
};

let plantNames = {};
let lang = localStorage.getItem(LANG_KEY) || ({ ru: "ru", ky: "ky" }[navigator.language.slice(0, 2)] ?? "en");
let photos = []; // [{file, url}]
let coords = null;
const tr = () => UI[lang];

function loadSettings() { try { return JSON.parse(localStorage.getItem(SETTINGS_KEY)) || null; } catch { return null; } }

async function setLang(l) {
  lang = l; localStorage.setItem(LANG_KEY, l); document.documentElement.lang = l;
  document.querySelectorAll("[data-i18n]").forEach((el) => (el.textContent = tr()[el.dataset.i18n]));
  document.querySelectorAll("[data-i18n-html]").forEach((el) => (el.innerHTML = tr()[el.dataset.i18nHtml]));
  document.querySelectorAll("#langs button").forEach((b) => b.classList.toggle("on", b.dataset.lang === l));
  document.title = tr().title;
  const [species, plants] = await Promise.all([
    fetch(`api/species?lang=${l}`).then((r) => r.json()), fetch(`api/plants?lang=${l}`).then((r) => r.json())]);
  plantNames = Object.fromEntries(Object.entries(plants).map(([k, v]) => [k, v.name]));
  const currentPlant = $("plant").value || "auto";
  $("plant").replaceChildren(new Option(tr().auto, "auto"),
    ...Object.entries(plants).map(([k, v]) => new Option(`${EMOJI[k] || ""} ${v.name}`, k)));
  $("plant").value = currentPlant;
  showPlantSettings();
  const current = $("species").value || loadSettings()?.species || "unknown";
  $("species").replaceChildren(...Object.entries(species).map(([v, text]) => new Option(text, v)));
  $("species").value = current;
  renderThumbs();
  if (!$("result").hidden && lastForm) submit(); // re-show the advice in the new language
}

async function init() {
  await setLang(lang);
  if (!loadSettings()) $("settings").hidden = false; // first run: ask about the plant
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
  navigator.geolocation?.getCurrentPosition(
    (p) => (coords = { lat: p.coords.latitude, lon: p.coords.longitude }),
    () => (coords = null), // refused or unavailable: advice just ignores weather
    { maximumAge: 3600e3, timeout: 10e3 });
}

document.querySelectorAll("#langs button").forEach((b) => (b.onclick = () => setLang(b.dataset.lang)));
$("settingsBtn").onclick = () => ($("settings").hidden = !$("settings").hidden);
// Age/height are remembered per plant type; the hydrangea type is only asked for hydrangeas.
function plantSettings(key) { return loadSettings()?.plants?.[key] || {}; }
function showPlantSettings() {
  const key = $("plant").value;
  const s = loadSettings() || {};
  $("settingsPlant").textContent = key === "auto" ? "" : `${EMOJI[key] || ""} ${plantNames[key] || ""}`;
  $("speciesRow").hidden = !(key === "hydrangea" || key === "auto");
  $("species").value = s.species || "unknown";
  $("age").value = plantSettings(key).age ?? ""; $("height").value = plantSettings(key).height ?? "";
}
$("plant").onchange = () => {
  showPlantSettings();
  if (!$("result").hidden && lastForm) { lastForm.set("plant", $("plant").value); applyPlantSettings(lastForm); submit(); }
};
$("saveSettings").onclick = () => {
  const s = loadSettings() || { plants: {} };
  s.plants ||= {};
  s.species = $("species").value;
  s.plants[$("plant").value] = { age: $("age").value, height: $("height").value };
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));
  $("settings").hidden = true;
  if (!$("result").hidden && lastForm) { applyPlantSettings(lastForm); submit(); }
};
function applyPlantSettings(form) {
  const p = plantSettings(form.get("plant"));
  form.delete("age_years"); form.delete("height_cm");
  if (p.age) form.append("age_years", p.age);
  if (p.height) form.append("height_cm", p.height);
  form.set("species", loadSettings()?.species || "unknown");
}

// ---- photos ----
function addPhotos(files) {
  $("error").hidden = true;
  for (const file of files) {
    if (photos.length >= MAX_PHOTOS) { showError(tr().tooMany); break; }
    photos.push({ file, url: URL.createObjectURL(file) });
  }
  $("result").hidden = true;
  renderThumbs();
}

function renderThumbs(perPhoto = null) {
  $("thumbs").replaceChildren(...photos.map((p, i) => {
    const box = document.createElement("div"); box.className = "thumb";
    const img = Object.assign(document.createElement("img"), { src: p.url, alt: `${tr().photo} ${i + 1}` });
    const x = Object.assign(document.createElement("button"), { textContent: "✕", ariaLabel: tr().remove, className: "remove" });
    x.onclick = () => { URL.revokeObjectURL(p.url); photos.splice(i, 1); $("result").hidden = true; renderThumbs(); };
    box.append(img, x);
    if (perPhoto?.[i]) {
      const cap = document.createElement("small");
      cap.textContent = `${perPhoto[i].health.text} · ${perPhoto[i].stage.text}`;
      box.append(cap);
    }
    return box;
  }));
  $("count").textContent = photos.length ? tr().count(photos.length) : "";
  $("check").disabled = photos.length === 0;
}

for (const id of ["camera", "gallery"]) $(id).onchange = (e) => { addPhotos([...e.target.files]); e.target.value = ""; };

// Shrink each photo on the phone before upload: faster on mobile data, and the model only needs ~224px anyway.
function shrink(file, maxSide = 1024) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const k = Math.min(1, maxSide / Math.max(img.width, img.height));
      const c = Object.assign(document.createElement("canvas"), { width: img.width * k, height: img.height * k });
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      c.toBlob((b) => (b ? resolve(b) : reject(new Error("read"))), "image/jpeg", 0.85);
      URL.revokeObjectURL(img.src);
    };
    img.onerror = () => reject(new Error("read"));
    img.src = URL.createObjectURL(file);
  });
}

// ---- analyse ----
let lastForm = null;
$("check").onclick = async () => {
  lastForm = new FormData();
  for (const [i, p] of photos.entries()) lastForm.append("photos", await shrink(p.file), `photo${i}.jpg`);
  lastForm.append("plant", $("plant").value);
  applyPlantSettings(lastForm);
  if (coords) { lastForm.append("lat", coords.lat); lastForm.append("lon", coords.lon); }
  submit();
};

async function submit() {
  for (const id of ["result", "error", "settings"]) $(id).hidden = true;
  $("loading").hidden = false; $("check").disabled = true;
  $("slow").hidden = true;
  const slowTimer = setTimeout(() => ($("slow").hidden = false), 8000);
  try {
    lastForm.set("lang", lang);
    const res = await fetch("api/analyze", { method: "POST", body: lastForm });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || tr().failed);
    show(data);
  } catch (e) {
    showError(navigator.onLine ? e.message || tr().failed : tr().offline);
  } finally {
    clearTimeout(slowTimer);
    $("loading").hidden = true; $("check").disabled = photos.length === 0;
  }
}

function showError(msg) { $("error").textContent = msg; $("error").hidden = false; }

function show(d) {
  const p = d.plant;
  const plantText = `${EMOJI[p.key] || "🌿"} ${p.text}`;
  $("plantLine").replaceChildren();
  if (p.method === "chosen") $("plantLine").textContent = plantText;
  else {
    $("plantLine").append(p.key === "unknown" ? tr().notSureWhich : `${tr().recognised} ${plantText} (${Math.round(p.confidence * 100)}%) `);
    const btn = Object.assign(document.createElement("button"), { className: "link-btn", textContent: tr().change });
    btn.onclick = () => { $("plant").scrollIntoView({ behavior: "smooth", block: "center" }); $("plant").focus(); };
    $("plantLine").append(" ", btn);
  }
  $("badge").textContent = tr().badge[d.trim_now];
  $("badge").className = `badge ${d.trim_now}`;
  $("headline").textContent = d.headline;
  $("howFar").textContent = d.how_far ? `${tr().howFar} ${d.how_far}` : "";
  $("notes").replaceChildren(...d.notes.map((n) => Object.assign(document.createElement("li"), { textContent: n })));
  $("weather").textContent = d.weather ? `🌦️ ${d.weather}` : "";
  const fmt = (t) => `${t.text} (${Math.round(t.confidence * 100)}%${t.unsure ? ", " + tr().notSure : ""})`;
  $("seen").textContent = `${tr().health}: ${fmt(d.health)} · ${tr().stage}: ${fmt(d.stage)} · ${d.health.method}`;
  renderThumbs(d.photos);
  $("result").hidden = false;
  $("result").scrollIntoView({ behavior: "smooth" });
}

$("again").onclick = () => {
  photos.forEach((p) => URL.revokeObjectURL(p.url)); photos = []; lastForm = null;
  $("result").hidden = true; renderThumbs(); window.scrollTo({ top: 0, behavior: "smooth" });
};

init();
