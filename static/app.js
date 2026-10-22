// On GitHub Pages the page is static, so the AI is called on Cloud Run. Elsewhere the server serves both.
const API = location.hostname.endsWith("github.io") ? "https://hydrangea-doctor-624126191196.us-central1.run.app/" : "";
// Phone app, designed for older users: one big photo button, the answer appears
// by itself, short text, questions only when they matter.
const $ = (id) => document.getElementById(id);
const MAX_PHOTOS = 6;
const STORE = "hydrangea-store"; // {lang, location: "yes"|"no", species, plants: {key: {age}}}
const EMOJI = {}, SPECIES_EMOJI = {}; // text only, deliberately
const AGES = [["young", 1], ["middle", 4], ["old", 10]];

// Screen texts. The advice itself is translated on the server (hydrangea/i18n.py).
const UI = {
  en: {
    eyebrow: "Plant health and pruning guidance",
    heroTitle: "Know when to prune, and when to wait.",
    heroLead: "Photograph a plant. Get a clear pruning answer based on what it looks like and the weather where you are.",
    howTitle: "How it works",
    s1t: "Photograph",
    s1d: "One leaf up close, or the whole plant. Up to six photos.",
    s2t: "Analyse",
    s2d: "An image model reads the plant's stage and health. Local weather is added.",
    s3t: "Act",
    s3d: "You get one clear answer: trim now, only a little, or wait.",
    honestTitle: "What it can and cannot do",
    honest1: "It estimates the growth stage and visible health problems from a photo, and checks frost and heat before advising a cut.",
    honest2: "It is not a diagnosis. When the photo is unclear it says it is not sure and asks for a closer one. Garden-specific accuracy improves as labelled photos are added.",
    footPrivacy: "Photos are analysed and not stored.",
    title: "Hydrangea Doctor", homeTitle: "Take a photo of your plant", takePhoto: "Take a photo",
    fromGallery: "or choose from the gallery", tip: "Tip: a close-up of one leaf, or the whole plant.",
    locQuestion: "May I use your location?", locWhy: "Only to check the weather: frost and heat change the advice.",
    yes: "Yes", noThanks: "No, thanks", looking: "Looking at your plant…",
    slow: "The first check after a break can take up to a minute. Please wait.",
    readAloud: "Read aloud", stop: "Stop", yesRight: "Yes", noChoose: "No, choose", more: "More details",
    addPhoto: "Add another photo of this plant", again: "Check a different plant", remove: "Remove photo",
    answer: { yes: "Yes, trim now", light: "Only a little", no: "Don't trim now" },
    thisIs: (p) => `This is: ${p}`, looksLike: (p) => `This looks like: ${p}. Is that right?`,
    whichPlant: "Which plant is this?", whichHydrangea: "What does your hydrangea look like?",
    howOld: "How old is this plant?", ages: { young: "Young (1–2 years)", middle: "3–5 years", old: "Older" },
    tooMany: `Up to ${MAX_PHOTOS} photos at a time.`, health: "Health", stage: "Stage",
    sure: "sure", probably: "probably", notSure: "not sure",
    offline: "No internet. Please connect and try again.", failed: "Something went wrong. Please try again.",
  },
  ru: {
    eyebrow: "Здоровье растений и обрезка",
    heroTitle: "Знайте, когда обрезать, а когда подождать.",
    heroLead: "Сфотографируйте растение. Получите понятный ответ об обрезке с учётом его вида и погоды в вашем месте.",
    howTitle: "Как это работает",
    s1t: "Сфотографируйте",
    s1d: "Один лист крупным планом или всё растение. До шести фото.",
    s2t: "Анализ",
    s2d: "Модель по фото определяет стадию и состояние растения. Добавляется местная погода.",
    s3t: "Действие",
    s3d: "Один чёткий ответ: обрезать сейчас, немного или подождать.",
    honestTitle: "Что умеет и чего не умеет",
    honest1: "Оценивает стадию роста и видимые проблемы со здоровьем по фото и проверяет заморозки и жару перед советом об обрезке.",
    honest2: "Это не диагноз. Если фото нечёткое, приложение скажет, что не уверено, и попросит снимок ближе. Точность для вашего сада растёт по мере добавления размеченных фото.",
    footPrivacy: "Фото анализируются и не сохраняются.",
    title: "Доктор Гортензий", homeTitle: "Сфотографируйте растение", takePhoto: "Сфотографировать",
    fromGallery: "или выбрать из галереи", tip: "Совет: один лист крупным планом или всё растение целиком.",
    locQuestion: "Можно узнать ваше местоположение?", locWhy: "Только чтобы проверить погоду: заморозки и жара меняют совет.",
    yes: "Да", noThanks: "Нет, спасибо", looking: "Смотрю на ваше растение…",
    slow: "Первая проверка после перерыва может занять до минуты. Пожалуйста, подождите.",
    readAloud: "Прочитать вслух", stop: "Стоп", yesRight: "Да", noChoose: "Нет, выбрать", more: "Подробнее",
    addPhoto: "Добавить ещё фото этого растения", again: "Проверить другое растение", remove: "Удалить фото",
    answer: { yes: "Да, обрезайте", light: "Только немного", no: "Не обрезайте сейчас" },
    thisIs: (p) => `Это: ${p}`, looksLike: (p) => `Похоже, это: ${p}. Верно?`,
    whichPlant: "Что это за растение?", whichHydrangea: "Как выглядит ваша гортензия?",
    howOld: "Сколько лет этому растению?", ages: { young: "Молодое (1–2 года)", middle: "3–5 лет", old: "Старше" },
    tooMany: `Не больше ${MAX_PHOTOS} фото за раз.`, health: "Здоровье", stage: "Стадия",
    sure: "уверена", probably: "скорее всего", notSure: "не уверена",
    offline: "Нет интернета. Подключитесь и попробуйте снова.", failed: "Что-то пошло не так. Попробуйте ещё раз.",
  },
  ky: {
    eyebrow: "Өсүмдүктүн ден соолугу жана кыркуу",
    heroTitle: "Качан кыркууну, качан күтүүнү билиңиз.",
    heroLead: "Өсүмдүктү сүрөткө тартыңыз. Анын көрүнүшүнө жана жериңиздеги аба ырайына жараша так жооп алыңыз.",
    howTitle: "Бул кантип иштейт",
    s1t: "Сүрөткө тартыңыз",
    s1d: "Бир жалбырак жакындан же өсүмдүк толугу менен. Алты сүрөткө чейин.",
    s2t: "Талдоо",
    s2d: "Модель сүрөттөн өсүмдүктүн баскычын жана абалын аныктайт. Жергиликтүү аба ырайы кошулат.",
    s3t: "Иш-аракет",
    s3d: "Бир так жооп: азыр кыркуу, бир аз гана же күтүү.",
    honestTitle: "Эмне кыла алат жана эмне кыла албайт",
    honest1: "Сүрөттөн өсүү баскычын жана көрүнгөн көйгөйлөрдү баалайт, кыркуудан мурун үшүк менен ысыкты текшерет.",
    honest2: "Бул диагноз эмес. Сүрөт даана эмес болсо, ишенбей турганын айтып, жакындан тартууну суранат. Бакчаңыз үчүн тактык белгиленген сүрөттөр кошулган сайын жакшырат.",
    footPrivacy: "Сүрөттөр талдоодон өтөт, сакталбайт.",
    title: "Гортензия Доктуру", homeTitle: "Өсүмдүгүңүздү сүрөткө тартыңыз", takePhoto: "Сүрөткө тартуу",
    fromGallery: "же галереядан тандаңыз", tip: "Кеңеш: бир жалбыракты жакындан же өсүмдүктү толугу менен.",
    locQuestion: "Жайгашкан жериңизди колдонсом болобу?", locWhy: "Аба ырайын текшерүү үчүн гана: үшүк жана ысык кеңешти өзгөртөт.",
    yes: "Ооба", noThanks: "Жок, рахмат", looking: "Өсүмдүгүңүздү карап жатам…",
    slow: "Тыныгуудан кийинки биринчи текшерүү бир мүнөткө чейин созулушу мүмкүн. Күтө туруңуз.",
    readAloud: "Үн менен окуу", stop: "Токтотуу", yesRight: "Ооба", noChoose: "Жок, тандоо", more: "Кененирээк",
    addPhoto: "Бул өсүмдүктүн дагы бир сүрөтүн кошуу", again: "Башка өсүмдүктү текшерүү", remove: "Сүрөттү өчүрүү",
    answer: { yes: "Ооба, кыркыңыз", light: "Бир аз гана", no: "Азыр кыркпаңыз" },
    thisIs: (p) => `Бул: ${p}`, looksLike: (p) => `Бул ${p} окшойт. Туурабы?`,
    whichPlant: "Бул кайсы өсүмдүк?", whichHydrangea: "Гортензияңыз кандай көрүнөт?",
    howOld: "Бул өсүмдүк канча жашта?", ages: { young: "Жаш (1–2 жыл)", middle: "3–5 жыл", old: "Улуураак" },
    tooMany: `Бир жолу ${MAX_PHOTOS} сүрөткө чейин.`, health: "Ден соолугу", stage: "Баскычы",
    sure: "ишенемин", probably: "балким", notSure: "так эмес",
    offline: "Интернет жок. Туташып, кайра аракет кылыңыз.", failed: "Бир нерсе туура эмес болду. Кайра аракет кылыңыз.",
  },
};
const SPEECH_LANG = { en: "en-US", ru: "ru-RU", ky: "ky-KG" };

const store = (() => { try { return JSON.parse(localStorage.getItem(STORE)) || {}; } catch { return {}; } })();
const save = () => localStorage.setItem(STORE, JSON.stringify(store));
store.plants ||= {};
let lang = store.lang || ({ ru: "ru", ky: "ky" }[navigator.language.slice(0, 2)] ?? "ru");
let photos = []; // [{file, url}]
let plant = "auto"; // what we send; becomes the confirmed/chosen plant
let coords = null;
let plantNames = {}, speciesNames = {};
let last = null; // last server answer
const tr = () => UI[lang];

// ---------- language ----------
async function setLang(l) {
  lang = l; store.lang = l; save(); document.documentElement.lang = l; document.title = tr().title;
  document.querySelectorAll("[data-i18n]").forEach((el) => (el.textContent = tr()[el.dataset.i18n]));
  document.querySelectorAll("#langs button").forEach((b) => b.classList.toggle("on", b.dataset.lang === l));
  const [plants, species] = await Promise.all([
    fetch(API + `api/plants?lang=${l}`).then((r) => r.json()), fetch(API + `api/species?lang=${l}`).then((r) => r.json())]);
  plantNames = Object.fromEntries(Object.entries(plants).map(([k, v]) => [k, v.name]));
  speciesNames = species;
  renderThumbs();
  if (photos.length && last) analyse(); // show the same answer in the new language
}
document.querySelectorAll("#langs button").forEach((b) => (b.onclick = () => setLang(b.dataset.lang)));

// ---------- location (asked once, with an explanation first) ----------
function getLocation() {
  navigator.geolocation?.getCurrentPosition(
    (p) => (coords = { lat: p.coords.latitude, lon: p.coords.longitude }),
    () => (coords = null), { maximumAge: 3600e3, timeout: 10e3 });
}
$("locYes").onclick = () => { store.location = "yes"; save(); $("locAsk").hidden = true; getLocation(); };
$("locNo").onclick = () => { store.location = "no"; save(); $("locAsk").hidden = true; };

// ---------- photos ----------
for (const id of ["camera", "gallery"]) $(id).onchange = (e) => { addPhotos([...e.target.files]); e.target.value = ""; };

function addPhotos(files) {
  if (!files.length) return;
  $("error").hidden = true;
  for (const file of files) {
    if (photos.length >= MAX_PHOTOS) { showError(tr().tooMany); break; }
    photos.push({ file, url: URL.createObjectURL(file) });
  }
  renderThumbs();
  analyse(); // no "Check" button: the answer comes by itself
}

function renderThumbs() {
  $("thumbs").replaceChildren(...photos.map((p, i) => {
    const box = Object.assign(document.createElement("div"), { className: "thumb" });
    const img = Object.assign(document.createElement("img"), { src: p.url, alt: "" });
    const x = Object.assign(document.createElement("button"), { textContent: "✕", className: "remove" });
    x.setAttribute("aria-label", tr().remove);
    x.onclick = () => {
      URL.revokeObjectURL(p.url); photos.splice(i, 1); renderThumbs();
      photos.length ? analyse() : reset();
    };
    box.append(img, x);
    return box;
  }));
  $("home").hidden = photos.length > 0;
  document.body.classList.toggle("working", photos.length > 0);
}

// Shrink each photo on the phone before upload: faster on mobile data; the model only needs ~224px.
function shrink(file, maxSide = 1024) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const k = Math.min(1, maxSide / Math.max(img.width, img.height));
      const c = Object.assign(document.createElement("canvas"), { width: img.width * k, height: img.height * k });
      c.getContext("2d").drawImage(img, 0, 0, c.width, c.height);
      c.toBlob((b) => (b ? resolve(b) : reject(new Error(tr().failed))), "image/jpeg", 0.85);
      URL.revokeObjectURL(img.src);
    };
    img.onerror = () => reject(new Error(tr().failed));
    img.src = URL.createObjectURL(file);
  });
}

// ---------- ask the server ----------
let requestId = 0;
async function analyse() {
  const id = ++requestId;
  stopSpeaking();
  for (const s of ["result", "error"]) $(s).hidden = true;
  $("loading").hidden = false; $("slow").hidden = true;
  const slowTimer = setTimeout(() => ($("slow").hidden = false), 8000);
  try {
    const form = new FormData();
    for (const [i, p] of photos.entries()) form.append("photos", await shrink(p.file), `photo${i}.jpg`);
    form.append("plant", plant);
    form.append("lang", lang);
    form.append("species", store.species || "unknown");
    form.append("ages", JSON.stringify(Object.fromEntries(
      Object.entries(store.plants).filter(([, v]) => v.age).map(([k, v]) => [k, v.age]))));
    if (coords) { form.append("lat", coords.lat); form.append("lon", coords.lon); }
    const res = await fetch(API + "api/analyze", { method: "POST", body: form });
    const data = await res.json().catch(() => ({}));
    if (id !== requestId) return; // a newer request replaced this one
    if (!res.ok) throw new Error(data.detail || tr().failed);
    last = data;
    show(data);
  } catch (e) {
    if (id === requestId) showError(navigator.onLine ? e.message || tr().failed : tr().offline);
  } finally {
    clearTimeout(slowTimer);
    if (id === requestId) $("loading").hidden = true;
  }
}

function showError(msg) { $("error").textContent = msg; $("error").hidden = false; }

const certainty = (c) => (c >= 0.85 ? tr().sure : c >= 0.6 ? tr().probably : tr().notSure);

// ---------- show the answer ----------
function show(d) {
  $("answer").textContent = tr().answer[d.trim_now];
  $("answer").className = `answer ${d.trim_now}`;
  $("headline").textContent = d.headline;
  $("howFar").textContent = d.how_far;
  $("speak").hidden = !("speechSynthesis" in window);

  // Which plant
  const p = d.plant, name = p.text;
  $("plantGrid").hidden = true;
  if (p.key === "unknown") {
    $("plantLine").textContent = tr().whichPlant; $("plantConfirm").hidden = true; showPlantGrid();
  } else if (p.method === "chosen") {
    $("plantLine").textContent = tr().thisIs(name); $("plantConfirm").hidden = true;
  } else {
    $("plantLine").textContent = tr().looksLike(name); $("plantConfirm").hidden = false;
  }

  // One question at a time, only when it changes the advice
  const key = p.key;
  if (key === "hydrangea" && !store.species) askQuestion(tr().whichHydrangea,
    Object.entries(speciesNames).map(([k, v]) => [k, `${SPECIES_EMOJI[k] || ""}`, v]),
    (k) => { store.species = k; save(); analyse(); });
  else if (key !== "unknown" && d.trim_now !== "no" && !store.plants[key]?.age) askQuestion(tr().howOld,
    AGES.map(([k, years]) => [years, "", tr().ages[k]]),
    (years) => { store.plants[key] = { ...store.plants[key], age: years }; save(); plant = key; analyse(); });
  else $("question").hidden = true;

  // Details
  $("notes").replaceChildren(...d.notes.map((n) => Object.assign(document.createElement("li"), { textContent: n })));
  $("weather").textContent = d.weather ? d.weather : "";
  $("seen").textContent = `${tr().health}: ${d.health.text} (${certainty(d.health.confidence)}) · ${tr().stage}: ${d.stage.text} (${certainty(d.stage.confidence)})`;

  $("result").hidden = false;
  $("thumbs").scrollIntoView({ behavior: "smooth" });
}

function askQuestion(text, choices, onPick) {
  $("questionText").textContent = text;
  $("questionChoices").replaceChildren(...choices.map(([value, emoji, label]) => {
    const b = document.createElement("button");
    b.innerHTML = emoji ? `<span class="e">${emoji}</span>` : "";
    b.append(label);
    b.onclick = () => onPick(value);
    return b;
  }));
  $("question").hidden = false;
}

function showPlantGrid() {
  $("plantGrid").replaceChildren(...Object.entries(plantNames).map(([k, v]) => {
    const b = document.createElement("button");
    b.innerHTML = ``;
    b.append(v);
    b.classList.toggle("on", k === last?.plant?.key);
    b.onclick = () => { plant = k; analyse(); };
    return b;
  }));
  $("plantGrid").hidden = false;
}
$("plantYes").onclick = () => { plant = last.plant.key; $("plantConfirm").hidden = true; $("plantLine").textContent = tr().thisIs(last.plant.text); };
$("plantNo").onclick = () => { $("plantConfirm").hidden = true; $("plantLine").textContent = tr().whichPlant; showPlantGrid(); };

// ---------- read aloud ----------
function stopSpeaking() { if ("speechSynthesis" in window) speechSynthesis.cancel(); }
$("speak").onclick = () => {
  if (speechSynthesis.speaking) { stopSpeaking(); return; }
  const u = new SpeechSynthesisUtterance([$("answer").textContent.replace(/^\S+\s/, ""), last.headline, last.how_far].join(". "));
  const voices = speechSynthesis.getVoices();
  const voice = voices.find((v) => v.lang.startsWith(lang)) || (lang === "ky" && voices.find((v) => v.lang.startsWith("ru")));
  if (voice) u.voice = voice;
  u.lang = voice?.lang || SPEECH_LANG[lang];
  u.rate = 0.9; // a little slower is easier to follow
  speechSynthesis.speak(u);
};

// ---------- start over ----------
function reset() {
  stopSpeaking();
  photos.forEach((p) => URL.revokeObjectURL(p.url)); photos = []; plant = "auto"; last = null; requestId++;
  for (const s of ["result", "error", "loading"]) $(s).hidden = true;
  renderThumbs(); window.scrollTo({ top: 0, behavior: "smooth" });
}
$("again").onclick = reset;

// ---------- start ----------
(async function init() {
  fetch(API + "api/warmup").catch(() => {}); // wake the AI up while she gets the camera ready
  await setLang(lang);
  if (!store.location) $("locAsk").hidden = false;
  else if (store.location === "yes") getLocation();
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
})();
