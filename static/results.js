// Language for the Results page. Shares the choice with the app (same localStorage key).
const STORE = "hydrangea-store";
const T = {
  en: {
    back: "← Back to the app", eyebrow: "Evaluation", title: "How accurate is it?",
    intro: "We tested the photo model on a hand-checked set of freely licensed photos from Wikimedia Commons. This page shows the numbers, the size of the test, and the limits.",
    summary: "Summary", question: "Question", photos: "Photos", untrained: "Untrained model", trained: "Trained on our photos*", random: "Random guessing",
    stage4: "Growth stage (4 classes)", health5: "Health (5 classes)", range: "95% range",
    foot1: "* Cross-validated: every photo was scored by a model that never saw it, and photos were never split across training and testing. \"Random guessing\" means always answering the most common class.",
    note: "<b>The live app uses the untrained model.</b> It is the 64% and 49% column. The trained model is held back until it is tested on real garden photos, because Wikimedia photos look different from a phone photo of a garden.",
    contains: "What the test set contains", class: "Class", stage: "Stage", health: "Health",
    blooming: "Blooming", budding: "Budding", fading: "Fading blooms", dormant: "Dormant",
    leafspot: "Leaf spot", mildew: "Powdery mildew", healthy: "Healthy", yellowing: "Yellowing", wilting: "Wilting",
    curation: "We started from 225 photos found by keyword search. Many were wrong: scanned single leaves, book pages, autumn maple trees. We looked at every photo and kept only those that show what the label says. Some were moved to the class they actually show. We chose photos before seeing any model score.",
    wrong: "Where it goes wrong", cap1: "Health, trained: rows are the true class, columns are the answer.", cap2: "Stage, trained.",
    limits: "Limits you should know",
    li0: "<b>Small test.</b> 45 and 66 photos. A single photo moves the result by 1–2 points. The ranges above show the real uncertainty.",
    li1: "<b>Wilting has only 5 photos.</b> Its result is close to anecdotal.",
    li2: "<b>Not a garden test.</b> Wikimedia photos are often well framed. Phone photos in a garden are harder, so expect lower accuracy there.",
    li3: "<b>Curated by hand.</b> Removing bad photos makes the test cleaner, and also easier. The earlier unfiltered run scored 70% on health and 76% on stage.",
    li4: "<b>Advice, not diagnosis.</b> When the model is unsure the app says so and asks for another photo.",
    next: "Next", nextp: "Labelled photos from real gardens, checked by a gardener, are the next step. They will let us report a number that matches how the app is used.",
    code: "The code, the curation list and the photo credits are in the <a href=\"https://github.com/aiyma-a/hydrangea-doctor\">open repository</a>.",
    app_name: "Hydrangea Doctor", app: "App", pageTitle: "Results · Hydrangea Doctor",
  },
  ru: {
    back: "← Назад в приложение", eyebrow: "Оценка", title: "Насколько это точно?",
    intro: "Мы проверили модель на вручную отобранных свободно лицензированных фото из Wikimedia Commons. Здесь показаны цифры, размер проверки и ограничения.",
    summary: "Итоги", question: "Вопрос", photos: "Фото", untrained: "Без обучения", trained: "Обучена на наших фото*", random: "Случайный выбор",
    stage4: "Стадия роста (4 класса)", health5: "Здоровье (5 классов)", range: "Диапазон 95%",
    foot1: "* Перекрёстная проверка: каждое фото оценивала модель, которая его не видела, а фото одного растения никогда не делились между обучением и проверкой. «Случайный выбор» — всегда отвечать самым частым классом.",
    note: "<b>Сейчас в приложении работает модель без обучения.</b> Это столбец 64% и 49%. Обученная модель пока не используется: её нужно проверить на настоящих садовых фото, потому что фото из Wikimedia отличаются от снимков на телефон в саду.",
    contains: "Что входит в проверочный набор", class: "Класс", stage: "Стадия", health: "Здоровье",
    blooming: "Цветение", budding: "Бутонизация", fading: "Увядающие цветы", dormant: "Покой",
    leafspot: "Пятнистость листьев", mildew: "Мучнистая роса", healthy: "Здоровое", yellowing: "Пожелтение", wilting: "Увядание",
    curation: "Мы начали с 225 фото, найденных по ключевым словам. Многие не подходили: сканы отдельных листьев, страницы книг, осенние клёны. Мы просмотрели каждое фото и оставили только те, что показывают названное. Часть фото перенесли в тот класс, который они действительно показывают. Фото выбирались до того, как мы увидели оценки модели.",
    wrong: "Где модель ошибается", cap1: "Здоровье, обученная модель: строки — настоящий класс, столбцы — ответ.", cap2: "Стадия, обученная модель.",
    limits: "Что важно знать об ограничениях",
    li0: "<b>Маленький набор.</b> 45 и 66 фото. Одно фото меняет результат на 1–2 пункта. Диапазоны выше показывают реальную неопределённость.",
    li1: "<b>Для «увядания» всего 5 фото.</b> Результат по нему почти ничего не доказывает.",
    li2: "<b>Это не садовая проверка.</b> Фото из Wikimedia обычно хорошо скадрированы. Снимки на телефон в саду сложнее, поэтому точность там будет ниже.",
    li3: "<b>Отбор вручную.</b> Удаление плохих фото делает проверку чище, но и легче. Прежний запуск без отбора дал 70% по здоровью и 76% по стадии.",
    li4: "<b>Совет, а не диагноз.</b> Если модель не уверена, приложение говорит об этом и просит ещё одно фото.",
    next: "Дальше", nextp: "Следующий шаг — размеченные фото из настоящих садов, проверенные садоводом. Тогда мы сможем назвать цифру, которая соответствует реальному использованию.",
    code: "Код, список отбора и авторство фото находятся в <a href=\"https://github.com/aiyma-a/hydrangea-doctor\">открытом репозитории</a>.",
    app_name: "Доктор Гортензий", app: "Приложение", pageTitle: "Результаты · Доктор Гортензий",
  },
  ky: {
    back: "← Колдонмого кайтуу", eyebrow: "Баалоо", title: "Канчалык так?",
    intro: "Биз моделди Wikimedia Commons сайтындагы эркин лицензиялуу, кол менен тандалган сүрөттөрдө текшердик. Бул жерде сандар, текшерүүнүн өлчөмү жана чектөөлөр көрсөтүлгөн.",
    summary: "Жыйынтык", question: "Суроо", photos: "Сүрөт", untrained: "Окутуусуз модель", trained: "Биздин сүрөттөр менен окутулган*", random: "Кокус божомол",
    stage4: "Өсүү баскычы (4 класс)", health5: "Ден соолук (5 класс)", range: "95% диапазон",
    foot1: "* Айкаш текшерүү: ар бир сүрөттү аны көрбөгөн модель баалады, ал эми бир өсүмдүктүн сүрөттөрү окутуу менен текшерүүнүн ортосунда бөлүнгөн эмес. «Кокус божомол» — дайыма эң көп кездешкен классты айтуу.",
    note: "<b>Азыр колдонмодо окутуусуз модель иштейт.</b> Бул 64% жана 49% мамычасы. Окутулган модель чыныгы бакча сүрөттөрүндө текшерилгенге чейин колдонулбайт, анткени Wikimedia сүрөттөрү бакчада телефон менен тартылган сүрөттөрдөн айырмаланат.",
    contains: "Текшерүү топтомунда эмне бар", class: "Класс", stage: "Баскыч", health: "Ден соолук",
    blooming: "Гүлдөө", budding: "Бүчүр байлоо", fading: "Соолуп жаткан гүлдөр", dormant: "Тынымда",
    leafspot: "Жалбырак тактары", mildew: "Ун кубулуш", healthy: "Дени сак", yellowing: "Саргаюу", wilting: "Соолуу",
    curation: "Биз ачкыч сөздөр менен табылган 225 сүрөттөн баштадык. Көбү туура эмес болчу: бир жалбырактын скандары, китеп беттери, күзгү клёндор. Ар бир сүрөттү карап чыгып, аталышына дал келгендерин гана калтырдык. Айрымдарын чындап көрсөткөн классына которгонбуз. Сүрөттөрдү модель баасын көрө электе тандадык.",
    wrong: "Ката кеткен жерлер", cap1: "Ден соолук, окутулган модель: саптар — чыныгы класс, мамычалар — жооп.", cap2: "Баскыч, окутулган модель.",
    limits: "Чектөөлөр жөнүндө билүү керек",
    li0: "<b>Кичине топтом.</b> 45 жана 66 сүрөт. Бир сүрөт жыйынтыкты 1–2 пунктка өзгөртөт. Жогорудагы диапазондор чыныгы белгисиздикти көрсөтөт.",
    li1: "<b>«Соолуу» үчүн 5 гана сүрөт бар.</b> Анын жыйынтыгы дээрлик эч нерсени далилдебейт.",
    li2: "<b>Бул бакча тести эмес.</b> Wikimedia сүрөттөрү көбүнчө жакшы тартылган. Бакчада телефон менен тартылган сүрөттөр кыйыныраак, ошондуктан тактык төмөн болот.",
    li3: "<b>Кол менен тандалган.</b> Начар сүрөттөрдү алып салуу тестти тазалайт, бирок жеңилдетет да. Тандоосуз мурунку жолу ден соолук боюнча 70%, баскыч боюнча 76% болгон.",
    li4: "<b>Кеңеш, диагноз эмес.</b> Модель ишенбесе, колдонмо муну айтып, дагы бир сүрөт сурайт.",
    next: "Кийинки кадам", nextp: "Кийинки кадам — чыныгы бакчалардан бакчачы текшерген белгиленген сүрөттөр. Ошондо колдонулушуна дал келген санды айта алабыз.",
    code: "Код, тандоо тизмеси жана сүрөттөрдүн авторлору <a href=\"https://github.com/aiyma-a/hydrangea-doctor\">ачык репозиторийде</a>.",
    app_name: "Гортензия Доктуру", app: "Колдонмо", pageTitle: "Жыйынтыктар · Гортензия Доктуру",
  },
};
let store = {}; try { store = JSON.parse(localStorage.getItem(STORE)) || {}; } catch {}
let lang = store.lang || ({ ru: "ru", ky: "ky" }[navigator.language.slice(0, 2)] ?? "ru");
function setLang(l) {
  lang = l; store.lang = l; localStorage.setItem(STORE, JSON.stringify(store));
  document.documentElement.lang = l; document.title = T[l].pageTitle;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const v = T[l][el.dataset.i18n]; if (v == null) return;
    el[el.hasAttribute("data-html") ? "innerHTML" : "textContent"] = v;
  });
  document.querySelectorAll("#langs button").forEach((b) => b.classList.toggle("on", b.dataset.lang === l));
}
document.querySelectorAll("#langs button").forEach((b) => (b.onclick = () => setLang(b.dataset.lang)));
setLang(lang);
