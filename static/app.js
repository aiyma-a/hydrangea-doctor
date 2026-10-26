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
    chatTitle: "Ask about this plant", chatPlaceholder: "For example: can I cut it now?", chatSend: "Ask", chatThinking: "Thinking…", chatNote: "An AI answers. It can be wrong; ask a garden shop before using any spray.",
    edition: "Fall edition", winterTitle: "Before winter", winterTips: ["Stop feeding: fertiliser now pushes soft new growth that frost kills.", "Leave dried hydrangea flower heads on for winter. They protect the buds.", "Mulch: spread 5–8 cm of dry leaves or compost over the roots.", "Young plants (under 3 years): cover them on freezing nights.", "Rake up leaves with spots or mould and put them in the bin, not the compost."],
    kh_title: "Let's find out which kind it is", kh_q1: "What do the flower heads look like?", kh_cone: "Cone-shaped, pointed", kh_round: "Round balls", kh_unsure: "Not sure", kh_q2cone: "Are the leaves lobed, shaped like oak leaves?", kh_lobed: "Yes, like oak leaves", kh_notlobed: "No, plain oval leaves", kh_q2round: "What colour are the flowers?", kh_colour: "Blue, pink or purple", kh_white: "White or pale green", kh_msg: "No problem. Take a close photo of one flower head and one leaf, or ask at a garden shop. Until then the app gives only safe advice.", kh_close: "OK", kh_back: "Back",
    bcTitle: "Before you cut", bcText: "This big trim is only for panicle and smooth hydrangeas, which flower on this year's stems. If your plant had round blue or pink balls last summer, do not cut it back now.", bcBtn: "I'm not sure of the kind",
    plantOther: "Other / not in the list",
    idBtn: "Not sure? Identify the plant with AI", idNote: "Your photos are sent to Google's AI for this. The answer can be wrong.", idLoading: "Looking at your photos…", idGuess: "The AI thinks this is:", idSure_high: "fairly sure", idSure_medium: "not very sure", idSure_low: "a weak guess", idYes: "Yes, that is right", idNo: "No, I'll choose myself", idNone: "The AI could not tell what this plant is. Try a close photo of a leaf or flower, or pick from the list.", idFail: "The AI could not look at the photos now. Please pick from the list.", idNotInList: "This plant is not in the list, so the app will give only safe advice. You can ask the chat below about it.",
    idAsk: "Ask the chat about it", idAskText: "What should I do with my {name}?",
    why: "Why this answer", rowPlant: "Plant", rowKind: "Kind", rowAge: "Age", change: "Change",
    tooDark: "This photo is too dark. Try again near a window or in daylight.",
    tooBlurry: "This photo is blurry. Hold the phone steady and tap the plant on the screen to focus.",
    useAnyway: "Use it anyway",
    takeAnother: "Take another photo",
    resultsLink: "Results",
    eyebrow: "Fall garden check",
    heroTitle: "What to do with your plants before winter.",
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
    footPrivacy: "Photos are analysed and not stored. If you tap \"Identify with AI\", they are also sent to Google's AI service.",
    title: "Hydrangea Doctor", homeTitle: "Take a photo of your plant", takePhoto: "Take a photo",
    fromGallery: "or choose from the gallery", tip: "Tip: a close-up of one leaf, or the whole plant.",
    locQuestion: "May I use your location?", locWhy: "Only to check the weather: frost and heat change the advice.",
    yes: "Yes", noThanks: "No, thanks", looking: "Looking at your plant…",
    slow: "The first check after a break can take up to a minute. Please wait.",
    readAloud: "Read aloud", stop: "Stop", yesRight: "Yes", noChoose: "No, choose", more: "More details",
    addPhoto: "Add another photo of this plant", again: "Check a different plant", remove: "Remove photo",
    answer: { yes: "Yes, trim now", light: "Only a little", no: "Don't trim now" },
    thisIs: (p) => `This is: ${p}`, looksLike: (p) => `This looks like: ${p}. Is that right?`,
    whichPlant: "Which plant is this?", whichHydrangea: "What does your hydrangea look like?", pickSpecies: "If it is a hydrangea: which kind?",
    howOld: "How old is this plant?", ages: { young: "Young (1–2 years)", middle: "3–5 years", old: "Older" },
    tooMany: `Up to ${MAX_PHOTOS} photos at a time.`, health: "Health", stage: "Stage",
    sure: "sure", probably: "probably", notSure: "not sure",
    offline: "No internet. Please connect and try again.", failed: "Something went wrong. Please try again.",
  },
  ru: {
    chatTitle: "Спросить про это растение", chatPlaceholder: "Например: можно ли обрезать сейчас?", chatSend: "Спросить", chatThinking: "Думаю…", chatNote: "Отвечает ИИ. Он может ошибаться; перед любым опрыскиванием спросите в садовом магазине.",
    edition: "Осеннее издание", winterTitle: "Перед зимой", winterTips: ["Не подкармливайте: удобрения сейчас вызывают нежный рост, который убьёт мороз.", "Сухие соцветия гортензии оставьте на зиму: они защищают почки.", "Замульчируйте: насыпьте на корни 5–8 см сухих листьев или компоста.", "Молодые растения (младше 3 лет): укрывайте на морозные ночи.", "Листья с пятнами или плесенью соберите и выбросьте, а не в компост."],
    kh_title: "Давайте определим вид", kh_q1: "Как выглядят соцветия?", kh_cone: "Конусом, заострённые", kh_round: "Круглые шары", kh_unsure: "Не уверена", kh_q2cone: "Листья лопастные, как у дуба?", kh_lobed: "Да, как дубовые", kh_notlobed: "Нет, простые овальные", kh_q2round: "Какого цвета цветы?", kh_colour: "Голубые, розовые или фиолетовые", kh_white: "Белые или светло-зелёные", kh_msg: "Ничего страшного. Сфотографируйте крупно одно соцветие и один лист или спросите в садовом магазине. Пока приложение даёт только безопасные советы.", kh_close: "Понятно", kh_back: "Назад",
    bcTitle: "Прежде чем резать", bcText: "Такая сильная обрезка подходит только метельчатой и древовидной гортензии: они цветут на побегах этого года. Если летом у вас были круглые голубые или розовые шары, сейчас не обрезайте.", bcBtn: "Я не уверена в виде",
    plantOther: "Другое / нет в списке",
    idBtn: "Не знаете, что за растение? Определить с помощью ИИ", idNote: "Для этого фото отправляются в ИИ Google. Ответ может быть неверным.", idLoading: "Смотрю на фото…", idGuess: "ИИ думает, что это:", idSure_high: "довольно уверен", idSure_medium: "не очень уверен", idSure_low: "слабое предположение", idYes: "Да, верно", idNo: "Нет, выберу сама", idNone: "ИИ не смог определить растение. Сфотографируйте крупно лист или цветок или выберите из списка.", idFail: "ИИ сейчас не смог посмотреть фото. Выберите из списка.", idNotInList: "Этого растения нет в списке, поэтому приложение даст только безопасный совет. Можно спросить о нём в чате ниже.", why: "Почему такой ответ", rowPlant: "Растение", rowKind: "Вид", rowAge: "Возраст", change: "Изменить",
    tooDark: "Фото слишком тёмное. Попробуйте у окна или при дневном свете.",
    tooBlurry: "Фото размытое. Держите телефон ровно и коснитесь растения на экране, чтобы навести резкость.",
    useAnyway: "Всё равно использовать",
    takeAnother: "Сфотографировать ещё раз",
    resultsLink: "Результаты",
    eyebrow: "Осенняя проверка сада",
    heroTitle: "Что сделать с растениями до зимы.",
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
    footPrivacy: "Фото анализируются и не сохраняются. Если нажать «Определить с помощью ИИ», они также отправляются в ИИ-сервис Google.",
    title: "Доктор Гортензий", homeTitle: "Сфотографируйте растение", takePhoto: "Сфотографировать",
    fromGallery: "или выбрать из галереи", tip: "Совет: один лист крупным планом или всё растение целиком.",
    locQuestion: "Можно узнать ваше местоположение?", locWhy: "Только чтобы проверить погоду: заморозки и жара меняют совет.",
    yes: "Да", noThanks: "Нет, спасибо", looking: "Смотрю на ваше растение…",
    slow: "Первая проверка после перерыва может занять до минуты. Пожалуйста, подождите.",
    readAloud: "Прочитать вслух", stop: "Стоп", yesRight: "Да", noChoose: "Нет, выбрать", more: "Подробнее",
    addPhoto: "Добавить ещё фото этого растения", again: "Проверить другое растение", remove: "Удалить фото",
    answer: { yes: "Да, обрезайте", light: "Только немного", no: "Не обрезайте сейчас" },
    thisIs: (p) => `Это: ${p}`, looksLike: (p) => `Похоже, это: ${p}. Верно?`,
    whichPlant: "Что это за растение?", whichHydrangea: "Как выглядит ваша гортензия?", pickSpecies: "Если это гортензия: какая?",
    howOld: "Сколько лет этому растению?", ages: { young: "Молодое (1–2 года)", middle: "3–5 лет", old: "Старше" },
    tooMany: `Не больше ${MAX_PHOTOS} фото за раз.`, health: "Здоровье", stage: "Стадия",
    sure: "уверена", probably: "скорее всего", notSure: "не уверена",
    offline: "Нет интернета. Подключитесь и попробуйте снова.", failed: "Что-то пошло не так. Попробуйте ещё раз.",
  },
  ky: {
    chatTitle: "Бул өсүмдүк жөнүндө суроо", chatPlaceholder: "Мисалы: азыр кесип койсом болобу?", chatSend: "Суроо", chatThinking: "Ойлонуп жатам…", chatNote: "ЖИ жооп берет. Ал жаңылышы мүмкүн; чачуудан мурун бакча дүкөнүнөн сураңыз.",
    edition: "Күзгү басылыш", winterTitle: "Кышка чейин", winterTips: ["Азыктандырбаңыз: азыр жер семирткич жумшак жаңы өсүндү чыгарат, аны үшүк өлтүрөт.", "Гортензиянын соолуган гүлдөрүн кышка калтырыңыз: алар бүчүрлөрдү коргойт.", "Мульча салыңыз: тамырдын үстүнө 5–8 см кургак жалбырак же компост төгүңүз.", "Жаш өсүмдүктөр (3 жашка чейин): үшүк түндөрдө жаап коюңуз.", "Тактуу же көгөргөн жалбырактарды жыйнап, компостко эмес, таштандыга ыргытыңыз."],
    kh_title: "Кайсы түр экенин аныктайлы", kh_q1: "Гүл топтомдору кандай көрүнөт?", kh_cone: "Конус сымал, учтуу", kh_round: "Тегерек шар сымал", kh_unsure: "Так билбейм", kh_q2cone: "Жалбырактары эмендин жалбырагындай бөлүктүүбү?", kh_lobed: "Ооба, эмен сыяктуу", kh_notlobed: "Жок, жөнөкөй сүйрү", kh_q2round: "Гүлдөрү кандай түстө?", kh_colour: "Көк, кызгылт же кызыл-көк", kh_white: "Ак же ачык жашыл", kh_msg: "Эч нерсе эмес. Бир гүл топтомун жана бир жалбырагын жакындан сүрөткө тартыңыз же бакча дүкөнүнөн сураңыз. Ага чейин колдонмо коопсуз кеңештерди гана берет.", kh_close: "Түшүнүктүү", kh_back: "Артка",
    bcTitle: "Кесүүдөн мурун", bcText: "Мындай катуу кесүү метелка жана жылмакай гортензияга гана туура келет: алар быйылкы бутактарда гүлдөйт. Жайында тегерек көк же кызгылт шарлар болсо, азыр кеспеңиз.", bcBtn: "Түрүн так билбейм",
    plantOther: "Башка / тизмеде жок",
    idBtn: "Кайсы өсүмдүк экенин билбейсизби? ЖИ менен аныктаңыз", idNote: "Ал үчүн сүрөттөр Google ЖИсине жөнөтүлөт. Жооп туура эмес болушу мүмкүн.", idLoading: "Сүрөттөрдү карап жатам…", idGuess: "ЖИ муну деп ойлойт:", idSure_high: "анчалык ишенимдүү", idSure_medium: "анча ишенимдүү эмес", idSure_low: "начар божомол", idYes: "Ооба, туура", idNo: "Жок, өзүм тандайм", idNone: "ЖИ өсүмдүктү аныктай алган жок. Жалбырагын же гүлүн жакындан тартыңыз же тизмеден тандаңыз.", idFail: "ЖИ азыр сүрөттөрдү көрө алган жок. Тизмеден тандаңыз.", idNotInList: "Бул өсүмдүк тизмеде жок, ошондуктан колдонмо коопсуз кеңеш гана берет. Төмөнкү чаттан сурасаңыз болот.", why: "Эмне үчүн мындай жооп", rowPlant: "Өсүмдүк", rowKind: "Түрү", rowAge: "Жашы", change: "Өзгөртүү",
    tooDark: "Сүрөт өтө караңгы. Терезенин жанында же күндүзгү жарыкта кайра тартып көрүңүз.",
    tooBlurry: "Сүрөт даана эмес. Телефонду кыймылдатпай кармап, фокус алуу үчүн экрандагы өсүмдүккө тийиңиз.",
    useAnyway: "Баары бир колдонуу",
    takeAnother: "Дагы бир сүрөт тартуу",
    resultsLink: "Жыйынтыктар",
    eyebrow: "Күзгү бак текшерүү",
    heroTitle: "Кышка чейин өсүмдүктөр менен эмне кылуу керек.",
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
    footPrivacy: "Сүрөттөр талдоодон өтөт, сакталбайт. «ЖИ менен аныктоо» басылса, алар Google ЖИ кызматына да жөнөтүлөт.",
    title: "Гортензия Доктуру", homeTitle: "Өсүмдүгүңүздү сүрөткө тартыңыз", takePhoto: "Сүрөткө тартуу",
    fromGallery: "же галереядан тандаңыз", tip: "Кеңеш: бир жалбыракты жакындан же өсүмдүктү толугу менен.",
    locQuestion: "Жайгашкан жериңизди колдонсом болобу?", locWhy: "Аба ырайын текшерүү үчүн гана: үшүк жана ысык кеңешти өзгөртөт.",
    yes: "Ооба", noThanks: "Жок, рахмат", looking: "Өсүмдүгүңүздү карап жатам…",
    slow: "Тыныгуудан кийинки биринчи текшерүү бир мүнөткө чейин созулушу мүмкүн. Күтө туруңуз.",
    readAloud: "Үн менен окуу", stop: "Токтотуу", yesRight: "Ооба", noChoose: "Жок, тандоо", more: "Кененирээк",
    addPhoto: "Бул өсүмдүктүн дагы бир сүрөтүн кошуу", again: "Башка өсүмдүктү текшерүү", remove: "Сүрөттү өчүрүү",
    answer: { yes: "Ооба, кыркыңыз", light: "Бир аз гана", no: "Азыр кыркпаңыз" },
    thisIs: (p) => `Бул: ${p}`, looksLike: (p) => `Бул ${p} окшойт. Туурабы?`,
    whichPlant: "Бул кайсы өсүмдүк?", whichHydrangea: "Гортензияңыз кандай көрүнөт?", pickSpecies: "Эгер бул гортензия болсо: кайсы түрү?",
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
// Nothing is picked for the user: every answer below comes from a tap in THIS check (not from the photo, not remembered).
const blankChoice = () => ({ plant: null, species: null, age: null });
let choice = blankChoice();
let analysing = false;
let coords = null;
let plantNames = {}, speciesNames = {};
let last = null; // last server answer
const tr = () => UI[lang];

// ---------- language ----------
async function setLang(l) {
  lang = l; store.lang = l; save(); document.documentElement.lang = l; document.title = tr().title;
  document.querySelectorAll("[data-i18n]").forEach((el) => (el.textContent = tr()[el.dataset.i18n]));
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => (el.placeholder = tr()[el.dataset.i18nPlaceholder]));
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

// ---------- live camera ----------
// A file input with capture="environment" often opens a menu or the gallery (especially from the home-screen icon).
// So open the camera ourselves; if that is not possible (no permission, old browser) fall back to the file input.
let camStream = null;
function closeCam() {
  if (camStream) camStream.getTracks().forEach((t) => t.stop());
  camStream = null; $("camVideo").srcObject = null; $("cam").hidden = true;
}
async function openCam() {
  try {
    camStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" }, width: { ideal: 1920 }, height: { ideal: 1440 } }, audio: false });
  } catch { $("camera").click(); return; }
  $("camVideo").srcObject = camStream; $("cam").hidden = false;
  $("camVideo").play().catch(() => {});
}
document.querySelectorAll('label[for="camera"]').forEach((l) => l.addEventListener("click", (e) => {
  if (!navigator.mediaDevices?.getUserMedia) return; // the label opens the file input as before
  e.preventDefault(); openCam();
}));
$("camClose").onclick = closeCam;
$("camShoot").onclick = () => {
  const v = $("camVideo");
  if (!v.videoWidth) return;
  const c = Object.assign(document.createElement("canvas"), { width: v.videoWidth, height: v.videoHeight });
  c.getContext("2d").drawImage(v, 0, 0);
  c.toBlob((blob) => { closeCam(); if (blob) addPhotos([new File([blob], `photo-${Date.now()}.jpg`, { type: "image/jpeg" })]); }, "image/jpeg", 0.92);
};

// A quick look at brightness and sharpness on a small copy, so a bad photo gets a friendly hint
// before it is sent. Thresholds were checked on 111 real plant photos (none flagged).
const DARK_BELOW = 40, BLUR_BELOW = 100;
// Decode a phone photo (12 MP+) directly at a small size: much faster than loading it in full.
async function decodeSmall(file, maxSide) {
  try {
    const full = await createImageBitmap(file, { imageOrientation: "from-image" }); // cheap: only reads the size lazily in most browsers
    const k = Math.min(1, maxSide / Math.max(full.width, full.height));
    if (k === 1) return full;
    const small = await createImageBitmap(file, { imageOrientation: "from-image", resizeWidth: Math.round(full.width * k), resizeHeight: Math.round(full.height * k), resizeQuality: "medium" });
    full.close(); return small;
  } catch {
    return new Promise((ok, no) => { const i = new Image(); i.onload = () => { i.close = () => URL.revokeObjectURL(i.src); ok(i); }; i.onerror = no; i.src = URL.createObjectURL(file); });
  }
}
async function photoProblem(file) {
  try {
    const img = await decodeSmall(file, 256);
    const k = 256 / Math.max(img.width, img.height), w = Math.max(3, Math.round(img.width * k)), h = Math.max(3, Math.round(img.height * k));
    const c = Object.assign(document.createElement("canvas"), { width: w, height: h });
    const ctx = c.getContext("2d", { willReadFrequently: true }); ctx.drawImage(img, 0, 0, w, h); img.close?.();
    const d = ctx.getImageData(0, 0, w, h).data, g = new Float32Array(w * h);
    let sum = 0;
    for (let i = 0; i < g.length; i++) { g[i] = 0.299 * d[4 * i] + 0.587 * d[4 * i + 1] + 0.114 * d[4 * i + 2]; sum += g[i]; }
    if (sum / g.length < DARK_BELOW) return "tooDark";
    let n = 0, s = 0, s2 = 0; // variance of the Laplacian: low means no sharp edges
    for (let y = 1; y < h - 1; y++) for (let x = 1; x < w - 1; x++) {
      const i = y * w + x, v = 4 * g[i] - g[i - 1] - g[i + 1] - g[i - w] - g[i + w];
      n++; s += v; s2 += v * v;
    }
    return s2 / n - (s / n) ** 2 < BLUR_BELOW ? "tooBlurry" : null;
  } catch { return null; } // if we cannot check, just carry on
}

function showNotice(text, canUseAnyway, onUse) {
  $("noticeText").textContent = text; $("noticeUse").hidden = !canUseAnyway; $("noticeUse").onclick = onUse;
  $("notice").hidden = false; $("notice").scrollIntoView({ behavior: "smooth" });
}

async function addPhotos(files) {
  if (!files.length) return;
  $("error").hidden = true; $("notice").hidden = true;
  const problems = await Promise.all(files.map(photoProblem));
  const bad = problems.find(Boolean);
  if (bad) { showNotice(tr()[bad], true, () => { $("notice").hidden = true; acceptPhotos(files); }); return; }
  acceptPhotos(files);
}

function acceptPhotos(files) {
  for (const file of files) {
    if (photos.length >= MAX_PHOTOS) { showError(tr().tooMany); break; }
    const added = { file, url: URL.createObjectURL(file) }; smallOf(added).catch(() => {}); photos.push(added); // start shrinking right away
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
  renderAbout();
}

// One compact card right under the photos: plant, kind, age. A row with an answer shows as
// "Label: value  Change"; a row still open shows big choice buttons. Only open rows take space.
// "I don't know" is an answer too: it is remembered and not asked again.
let editing = null;
function aboutRow(id, label, value, choices) {
  const row = Object.assign(document.createElement("div"), { className: "arow" });
  const head = Object.assign(document.createElement("div"), { className: "ahead" });
  head.append(Object.assign(document.createElement("span"), { className: "alabel", textContent: label }));
  const open = value == null || editing === id;
  if (!open) {
    head.append(Object.assign(document.createElement("b"), { className: "avalue", textContent: value }));
    const c = Object.assign(document.createElement("button"), { className: "textbtn change", textContent: tr().change });
    c.onclick = () => { editing = id; renderAbout(); };
    head.append(c);
  }
  row.append(head);
  if (editing === id) row.dataset.editing = "1";
  if (open) {
    const g = Object.assign(document.createElement("div"), { className: "grid" });
    g.append(...choices.map(([v, text, on]) => {
      const [name, hint] = text.split(" – "); // "Panicle – cone-shaped": name big, hint small
      const b = Object.assign(document.createElement("button"), { textContent: name });
      if (hint) b.append(Object.assign(document.createElement("small"), { textContent: hint }));
      b.classList.toggle("on", on);
      b.onclick = () => { editing = null; pick(id, v); };
      return b;
    }));
    row.append(g);
  }
  return row;
}
// "I don't know" the kind: two plain questions instead of a dead end. (A photo-based guess was tested and was
// right on only 10 of 41 garden photos, so it is not used.)
let kindStep = null; // null = not helping | "q1" | "cone" | "round" | "unsure"
function kindHelper() {
  const row = Object.assign(document.createElement("div"), { className: "arow helper" });
  const t = tr();
  const ask = (q, options) => {
    row.append(Object.assign(document.createElement("p"), { className: "kh-q", textContent: q }));
    const g = Object.assign(document.createElement("div"), { className: "grid" });
    g.append(...options.map(([text, go]) => {
      const b = Object.assign(document.createElement("button"), { textContent: text });
      b.onclick = () => { if (typeof go === "string" && ["bigleaf", "oakleaf", "panicle", "smooth"].includes(go)) { kindStep = null; pick("species", go); } else { kindStep = go; renderAbout(); } };
      return b;
    }));
    row.append(g);
  };
  row.append(Object.assign(document.createElement("b"), { className: "kh-title", textContent: t.kh_title }));
  if (kindStep === "q1") ask(t.kh_q1, [[t.kh_cone, "cone"], [t.kh_round, "round"], [t.kh_unsure, "unsure"]]);
  else if (kindStep === "cone") ask(t.kh_q2cone, [[t.kh_lobed, "oakleaf"], [t.kh_notlobed, "panicle"], [t.kh_back, "q1"]]);
  else if (kindStep === "round") ask(t.kh_q2round, [[t.kh_colour, "bigleaf"], [t.kh_white, "smooth"], [t.kh_back, "q1"]]);
  else {
    row.append(Object.assign(document.createElement("p"), { textContent: t.kh_msg }));
    const b = Object.assign(document.createElement("button"), { className: "secondary", textContent: t.kh_close });
    b.onclick = () => { kindStep = null; renderAbout(); };
    row.append(b);
  }
  return row;
}
function pick(id, v) {
  if (id === "plant") { if (choice.plant !== v) choice = { plant: v, species: null, age: null }; kindStep = null; ident = null; if (v !== "unknown") aiName = ""; }
  else if (id === "species") { choice.species = v; kindStep = v === "unknown" ? "q1" : null; }
  else choice.age = v;
  analyse(); renderAbout();
}
// Sick or wilting plants get the same answer for every kind, so the kind is not asked then.
const needsTreatment = () => last && !last.health.unsure && ["wilting", "leaf_spot", "powdery_mildew"].includes(last.health.label);
const stepsDone = () => !!choice.plant && (choice.plant !== "hydrangea" || !!choice.species || needsTreatment());
// "Identify with AI": the photos go to the server, which asks Gemini. The user must confirm the guess.
let ident = null; // null | "loading" | "none" | "fail" | {name, key, confidence}
let aiName = ""; // the AI's name for the plant when it is not in our list (passed to the chat)
async function identifyPlant() {
  ident = "loading"; renderAbout();
  const mine = ident;
  try {
    const form = new FormData();
    for (const [i, p] of photos.slice(0, 3).entries()) form.append("photos", await smallOf(p), `photo${i}.jpg`);
    form.append("lang", lang);
    const res = await fetch(API + "api/identify", { method: "POST", body: form });
    const data = await res.json().catch(() => ({}));
    if (ident !== mine) return; // the user moved on
    ident = res.ok ? (data.name ? data : "none") : "fail";
  } catch { if (ident === mine) ident = "fail"; }
  renderAbout();
}
function identifyBlock(other = false) {
  const box = Object.assign(document.createElement("div"), { className: "ident" });
  const t = tr();
  const text = (cls, str) => Object.assign(document.createElement("p"), { className: cls, textContent: str });
  if (ident === null) {
    const b = Object.assign(document.createElement("button"), { className: "secondary", type: "button", textContent: t.idBtn });
    b.onclick = identifyPlant;
    box.append(b, text("hint", t.idNote));
  } else if (ident === "loading") {
    box.append(text("hint", t.idLoading));
  } else if (ident === "none" || ident === "fail") {
    box.append(text("hint", ident === "none" ? t.idNone : t.idFail));
  } else {
    const label = ident.key ? plantNames[ident.key] : ident.name;
    box.append(text("hint", `${t.idGuess} (${t["idSure_" + ident.confidence]})`), text("idname", label));
    if (!ident.key) box.append(text("hint", t.idNotInList));
    if (other && !ident.key) { // "Other" is already chosen: remember the name for the chat and offer to ask about it
      aiName = ident.name;
      const ask = Object.assign(document.createElement("button"), { className: "primary", type: "button", textContent: t.idAsk });
      ask.onclick = () => { $("chatInput").value = t.idAskText.replace("{name}", ident.name); $("chat").scrollIntoView({ behavior: "smooth", block: "start" }); $("chatInput").focus(); };
      box.append(ask);
      return box;
    }
    const yes = Object.assign(document.createElement("button"), { className: "primary", type: "button", textContent: t.idYes });
    yes.onclick = () => { const g = ident; aiName = g.key ? "" : g.name; ident = null; pick("plant", g.key || "unknown"); };
    const no = Object.assign(document.createElement("button"), { className: "secondary", type: "button", textContent: t.idNo });
    no.onclick = () => { ident = "none"; renderAbout(); };
    box.append(Object.assign(document.createElement("div"), { className: "row" }), yes, no);
    box.querySelector(".row").remove();
    yes.style.marginBottom = "10px";
  }
  return box;
}
function renderAbout() {
  const rows = [];
  if (photos.length) rows.push(aboutRow("plant", tr().rowPlant, choice.plant ? (choice.plant === "unknown" ? tr().plantOther : plantNames[choice.plant]) : null,
    [...Object.entries(plantNames), ["unknown", tr().plantOther]].map(([k, v]) => [k, v, choice.plant === k])));
  if (rows.length && !choice.plant && !rows[0].dataset.editing) rows[0].insertBefore(identifyBlock(), rows[0].querySelector(".grid"));
  else if (rows.length && choice.plant === "unknown" && !rows[0].dataset.editing) rows[0].append(identifyBlock(true));
  if (choice.plant === "hydrangea" && !needsTreatment()) {
    rows.push(aboutRow("species", tr().rowKind, choice.species ? speciesNames[choice.species].split(" – ")[0] : null,
      Object.entries(speciesNames).map(([k, v]) => [k, v, choice.species === k])));
    if (choice.species === "unknown" && kindStep) rows.push(kindHelper());
  }
  // Age only changes a "yes" (younger plants get a lighter cut), so ask it once the answer is a "yes".
  if (last && stepsDone() && (last.trim_now === "yes" || choice.age))
    rows.push(aboutRow("age", tr().rowAge, choice.age ? tr().ages[AGES.find(([, y]) => y === choice.age)?.[0]] : null,
      AGES.map(([k, y]) => [y, tr().ages[k], choice.age === y])));
  // One open question at a time: the first row without an answer; later ones wait their turn.
  const firstOpen = rows.findIndex((r) => r.querySelector(".grid") && !r.dataset.editing);
  const shown = rows.filter((r, i) => !r.querySelector(".grid") || r.dataset.editing || i === firstOpen);
  $("about-plant").hidden = photos.length === 0 || shown.length === 0;
  $("about-plant").replaceChildren(...shown);
  // The answer appears only after the steps are done.
  $("result").hidden = !(last && !analysing && stepsDone());
  if (analysing && stepsDone()) $("loading").hidden = false;
}

// Shrink each photo on the phone before upload: faster on mobile data; the model only needs ~224px.
async function shrink(file, maxSide = 1024) {
  const img = await decodeSmall(file, maxSide).catch(() => { throw new Error(tr().failed); });
  const k = Math.min(1, maxSide / Math.max(img.width, img.height));
  const c = Object.assign(document.createElement("canvas"), { width: Math.round(img.width * k), height: Math.round(img.height * k) });
  c.getContext("2d").drawImage(img, 0, 0, c.width, c.height); img.close?.();
  return new Promise((resolve, reject) => c.toBlob((b) => (b ? resolve(b) : reject(new Error(tr().failed))), "image/jpeg", 0.85));
}
// Each photo is shrunk once and reused for every check, identify call and re-check.
const smallOf = (p) => (p.small ||= shrink(p.file));

// ---------- ask the server ----------
let requestId = 0;
async function analyse() {
  const id = ++requestId;
  analysing = true;
  stopSpeaking();
  for (const s of ["result", "error", "notice"]) $(s).hidden = true;
  $("loading").hidden = !stepsDone(); $("slow").hidden = true; // no spinner while the user still has questions to tap
  const slowTimer = setTimeout(() => ($("slow").hidden = false), 8000);
  try {
    const form = new FormData();
    for (const [i, p] of photos.entries()) form.append("photos", await smallOf(p), `photo${i}.jpg`);
    form.append("plant", choice.plant || "unknown");
    form.append("lang", lang);
    form.append("species", choice.species || "unknown");
    form.append("ages", JSON.stringify(choice.plant && choice.age ? { [choice.plant]: choice.age } : {}));
    if (coords) { form.append("lat", coords.lat); form.append("lon", coords.lon); }
    const res = await fetch(API + "api/analyze", { method: "POST", body: form });
    const data = await res.json().catch(() => ({}));
    if (id !== requestId) return; // a newer request replaced this one
    if (res.status === 422 && data.code === "not_plant") { showNotice(data.detail, false); return; }
    if (!res.ok) throw new Error(data.detail || tr().failed);
    last = data;
    show(data);
  } catch (e) {
    if (id === requestId) showError(navigator.onLine ? e.message || tr().failed : tr().offline);
  } finally {
    clearTimeout(slowTimer);
    if (id === requestId) { $("loading").hidden = true; analysing = false; renderAbout(); }
  }
}

function showError(msg) { $("error").textContent = msg; $("error").hidden = false; }

const certainty = (c) => (c >= 0.85 ? tr().sure : c >= 0.6 ? tr().probably : tr().notSure);

// ---------- show the answer ----------
function show(d) {
  $("answer").textContent = tr().answer[d.trim_now];
  $("answerCard").className = `answer ${d.trim_now}`;
  $("verdictIcon").textContent = { yes: "✓", light: "~", no: "✕" }[d.trim_now];
  $("headline").textContent = d.headline;
  $("howFar").textContent = d.how_far;
  // Before winter: only in autumn, and the dried-heads tip only for hydrangeas.
  const tips = tr().winterTips.filter((_, i) => i !== 1 || d.plant.key === "hydrangea");
  $("winterList").replaceChildren(...tips.map((t) => Object.assign(document.createElement("li"), { textContent: t })));
  $("winterCard").hidden = d.season !== "autumn";
  $("chatLog").replaceChildren(); chatLog.length = 0; // a new answer starts a new conversation
  $("cutPic").hidden = !d.diagram;
  if (d.diagram) $("cutPic").src = d.diagram;
  $("speak").hidden = !("speechSynthesis" in window);

  // Details, folded away
  $("notes").replaceChildren(...d.notes.map((n) => Object.assign(document.createElement("li"), { textContent: n })));
  $("weather").textContent = d.weather ? d.weather : "";
  $("seen").textContent = `${tr().health}: ${d.health.text} (${certainty(d.health.confidence)}) · ${tr().stage}: ${d.stage.text} (${certainty(d.stage.confidence)})`;

  // "Before you cut": the big trim is only right for panicle and smooth hydrangeas.
  $("bcTitle").textContent = tr().bcTitle; $("bcText").textContent = tr().bcText; $("bcBtn").textContent = tr().bcBtn;
  $("beforeCut").hidden = !(d.diagram && /cut_(third|low)/.test(d.diagram));
  analysing = false; renderAbout();
  if (!$("result").hidden) $("answerCard").scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// ---------- read aloud ----------
function stopSpeaking() { if ("speechSynthesis" in window) speechSynthesis.cancel(); }
$("speak").onclick = () => {
  if (speechSynthesis.speaking) { stopSpeaking(); return; }
  const u = new SpeechSynthesisUtterance([$("answer").textContent, last.headline, last.how_far].join(". "));
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
  photos.forEach((p) => URL.revokeObjectURL(p.url)); photos = []; choice = blankChoice(); kindStep = null; ident = null; aiName = ""; analysing = false; last = null; editing = null; requestId++;
  for (const s of ["result", "error", "loading", "notice"]) $(s).hidden = true;
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


// ---------- chat: ask the AI about the plant just checked ----------
const chatLog = []; // {role: "user" | "model", text}
function chatContext() {
  if (!last) return {};
  return { plant: aiName ? `${last.plant.text} (the AI guessed: ${aiName})` : last.plant.text, kind: choice.species && speciesNames[choice.species] ? speciesNames[choice.species].split(" – ")[0] : "",
    health: last.health.text, stage: last.stage.text, answer: tr().answer[last.trim_now], headline: last.headline, how_far: last.how_far,
    weather: last.weather || "", month: new Date().toLocaleString("en", { month: "long" }) };
}
function addChatBubble(role, text) {
  const li = Object.assign(document.createElement("li"), { textContent: text, className: role === "user" ? "me" : "ai" });
  $("chatLog").append(li); li.scrollIntoView({ behavior: "smooth", block: "nearest" }); return li;
}
$("bcBtn").onclick = () => { choice.species = "unknown"; kindStep = "q1"; analyse(); renderAbout(); $("about-plant").scrollIntoView({ behavior: "smooth", block: "start" }); };
$("chatForm").onsubmit = async (e) => {
  e.preventDefault();
  const q = $("chatInput").value.trim();
  if (!q || $("chatSend").disabled) return;
  $("chatInput").value = ""; $("chatSend").disabled = true;
  addChatBubble("user", q);
  const wait = addChatBubble("model", tr().chatThinking);
  try {
    const res = await fetch(API + "api/chat", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q, context: chatContext(), history: chatLog.slice(-6), lang }) });
    const data = await res.json();
    const text = res.ok ? data.reply : data.detail || tr().failed;
    wait.textContent = text;
    if (res.ok) chatLog.push({ role: "user", text: q }, { role: "model", text });
  } catch { wait.textContent = navigator.onLine ? tr().failed : tr().offline; }
  $("chatSend").disabled = false;
};
