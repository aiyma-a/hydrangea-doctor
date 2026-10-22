"""Translations: English, Russian, Kyrgyz.

The rules (pruning.py) never write sentences directly. They return message
*keys* like "water_first", and this file turns a key into text in the chosen
language. To add a language: copy the "en" block, translate the values, and
keep the {placeholders} unchanged.
"""
from dataclasses import dataclass, field

LANGS = ("en", "ru", "ky")

MESSAGES: dict[str, dict[str, str]] = {
    "en": {
        # labels
        "label.healthy": "healthy", "label.leaf_spot": "leaf spot", "label.powdery_mildew": "powdery mildew",
        "label.wilting": "wilting", "label.yellowing": "yellowing leaves", "label.unknown": "not sure",
        "label.budding": "budding", "label.blooming": "blooming", "label.fading_blooms": "fading flowers",
        "label.dormant": "dormant (resting)",
        "species.bigleaf": "Bigleaf – big round blue/pink balls",
        "species.oakleaf": "Oakleaf – leaves shaped like oak leaves",
        "species.panicle": "Panicle – cone-shaped, usually white",
        "species.smooth": "Smooth – white balls, e.g. 'Annabelle'",
        "species.unknown": "I don't know",
        # sick / stressed
        "water_first": "Water first, don't prune.",
        "wilting_note": "Wilting is usually thirst or heat. Water deeply at the base and check again next morning. If it hasn't recovered by then, check the roots for rot.",
        "remove_infected": "Only remove the infected leaves ({disease}).",
        "remove_infected_how": "Pick off affected leaves; cut badly affected stems back to healthy tissue.",
        "bin_leaves": "Throw the leaves in the bin, don't compost them.",
        "water_soil": "Water at the soil, not over the leaves, and clean the pruners between cuts.",
        "hold_shaping": "Hold off on any shaping cuts until the plant is healthy.",
        "unknown_health": "Couldn't judge health from this photo; advice assumes the plant is healthy.",
        "yellowing_note": "Yellow leaves with green veins usually mean the soil is too alkaline (iron can't be absorbed); pruning won't fix it. A soil pH test is the next step.",
        # unknown species
        "tell_type": "Tell me the hydrangea type for full advice. Until then, only cut off faded flowers.",
        "deadhead_safe_how": "Snip faded flower heads just above the first pair of fat buds below the flower. That's safe for every type.",
        "wood_types": "Bigleaf/oakleaf flower on last year's stems; panicle/smooth on this year's. Cutting the wrong type at the wrong time costs you next year's flowers.",
        # new wood
        "main_prune": "Good time for the big yearly trim.",
        "panicle_how": "Cut every stem back by about one third, just above a pair of buds. Remove thin, crossing, or dead stems at the base.",
        "smooth_how": "Cut all stems down to about 30–45 cm from the ground. Shorter stems flop less under heavy flowers.",
        "optional_tidy": "Optional tidy-up only.",
        "optional_tidy_how": "Cut off faded flowers if you don't like the look; leave the big trim for late winter.",
        "dried_heads_interest": "Many people leave the dried flowers on for winter decoration.",
        "not_now_new_wood": "Not now. The main prune is in late winter / early spring.",
        # old wood
        "trim_after_flowering": "Trim now, right after flowering.",
        "after_flowering_how": "Cut each faded flower stem back to the first pair of healthy, fat buds below the flower head (usually 10–30 cm down). Remove a few of the oldest stems at the base to thin.",
        "stop_late_summer": "Stop by late summer: after that, cuts remove the buds that make next year's flowers.",
        "dead_wood_only": "Only remove dead wood.",
        "dead_wood_how": "Cut stems that show no green buds back to the first live pair of buds, or to the ground if fully dead.",
        "scratch_test": "Scratch a stem with your nail: green underneath = alive.",
        "light_deadhead": "Only cut off the faded flowers.",
        "light_deadhead_how": "Snip only the flower head itself, just above the first pair of buds. No hard cuts.",
        "buds_formed": "Next year's flower buds have already formed in these stems. Hard cuts now remove them.",
        "heads_protect": "Leaving the dried flowers on over winter also protects the buds from frost.",
        "leave_old_wood": "Leave it. This type flowers on last year's stems.",
        "right_window": "The right time is just after it finishes flowering in summer.",
        # weather
        "hot_dry_thirst": "It's been hot and dry lately, so this is almost certainly thirst.",
        "not_hot_dry": "It hasn't been hot and dry lately. If the soil is wet, suspect too much water / root rot.",
        "frost_wait": "Wait: frost is coming.",
        "frost_wait_note": "Frost expected in {days} day(s). Cutting now pushes out soft new shoots that frost will kill. Wait until late winter.",
        "frost_mild_day": "Frost is still in the forecast: pick a dry, mild day for cutting.",
        "weather_summary": "{place}: last 7 days up to {max_temp}°C, {rain} mm rain; {frost}.",
        "frost_in": "frost expected in {days} day(s)",
        "no_frost": "no frost in the next 14 days",
        "your_location": "Your location",
        "weather_failed": "Couldn't get the weather right now; advice ignores it.",
        # age
        "young_gentle": "Go gently, it's a young plant.",
        "young_how": "Young plant: cut about half as much as that.",
        "young_note": "Under {years} years old: the plant is still building roots. Remove dead wood and faded flowers, but no more than half the usual cut.",
        "renewal_note": "Older bush: each year, also cut up to 1/3 of the oldest, thickest stems right at the ground, so young stems can grow in their place.",
        "cm_estimate": "On a {height} cm plant that's about {cut} cm off the top.",
        # confidence
        "unsure_health": "I'm not confident about the plant's health from these photos. Try a close-up of one leaf in daylight.",
        "unsure_stage": "I'm not confident about the stage from these photos. Try a photo of the whole plant.",
        # server errors
        "err_type": "Unknown hydrangea type.",
        "err_too_large": "A photo is too large (max 15 MB).",
        "err_not_photo": "One of the files isn't a photo I can read.",
        "err_count": "Please send between 1 and {max} photos.",
        "err_busy": "The app is still waking up. Please try again in a moment.",
        "err_no_plant": "I don't see a plant in this photo. Please photograph a leaf, or the whole plant.",
    },
    "ru": {
        "label.healthy": "здорова", "label.leaf_spot": "пятнистость листьев", "label.powdery_mildew": "мучнистая роса",
        "label.wilting": "вянет", "label.yellowing": "желтеют листья", "label.unknown": "не уверена",
        "label.budding": "бутоны", "label.blooming": "цветёт", "label.fading_blooms": "цветы отцветают",
        "label.dormant": "в покое",
        "species.bigleaf": "Крупнолистная – большие круглые голубые/розовые шапки",
        "species.oakleaf": "Дуболистная – листья как у дуба",
        "species.panicle": "Метельчатая – соцветия-конусы, обычно белые",
        "species.smooth": "Древовидная – белые шары, напр. «Анабель»",
        "species.unknown": "Не знаю",
        "water_first": "Сначала полейте, не обрезайте.",
        "wilting_note": "Обычно растение вянет от жажды или жары. Обильно полейте под корень и проверьте утром. Если не восстановилось — проверьте корни на гниль.",
        "remove_infected": "Удалите только больные листья ({disease}).",
        "remove_infected_how": "Оборвите поражённые листья; сильно поражённые побеги обрежьте до здоровой ткани.",
        "bin_leaves": "Выбросите листья в мусор, не в компост.",
        "water_soil": "Поливайте под корень, а не по листьям, и протирайте секатор после каждого среза.",
        "hold_shaping": "Формирующую обрезку отложите, пока растение не поправится.",
        "unknown_health": "По этому фото не удалось оценить здоровье; совет исходит из того, что растение здорово.",
        "yellowing_note": "Жёлтые листья с зелёными прожилками обычно значат, что почва слишком щелочная (железо не усваивается); обрезка не поможет. Следующий шаг — проверить pH почвы.",
        "tell_type": "Укажите вид гортензии для полного совета. Пока — только удаляйте отцветшие соцветия.",
        "deadhead_safe_how": "Срежьте отцветшее соцветие чуть выше первой пары крупных почек под ним. Это безопасно для любого вида.",
        "wood_types": "Крупнолистная и дуболистная цветут на прошлогодних побегах, метельчатая и древовидная — на побегах этого года. Обрезка не в то время лишит вас цветов на следующий год.",
        "main_prune": "Хорошее время для основной обрезки.",
        "panicle_how": "Укоротите каждый побег примерно на треть, чуть выше пары почек. Тонкие, перекрещивающиеся и сухие побеги удалите у основания.",
        "smooth_how": "Обрежьте все побеги до 30–45 см от земли. Короткие побеги меньше полегают под тяжёлыми цветами.",
        "optional_tidy": "Только лёгкая уборка, по желанию.",
        "optional_tidy_how": "Можно срезать отцветшие соцветия ради красоты; основную обрезку оставьте на конец зимы.",
        "dried_heads_interest": "Многие оставляют сухие соцветия как зимнее украшение.",
        "not_now_new_wood": "Не сейчас. Основная обрезка — в конце зимы / начале весны.",
        "trim_after_flowering": "Обрезайте сейчас, сразу после цветения.",
        "after_flowering_how": "Срежьте каждый отцветший побег до первой пары здоровых крупных почек под соцветием (обычно на 10–30 см). Для прореживания удалите у основания несколько самых старых побегов.",
        "stop_late_summer": "Закончите к концу лета: позже вы срежете почки будущих цветов.",
        "dead_wood_only": "Удалите только сухие побеги.",
        "dead_wood_how": "Побеги без зелёных почек обрежьте до первой живой пары почек, а полностью сухие — до земли.",
        "scratch_test": "Поскребите побег ногтем: зелёный под корой — живой.",
        "light_deadhead": "Только аккуратно срежьте соцветия.",
        "light_deadhead_how": "Срежьте только само соцветие, чуть выше первой пары почек. Без сильной обрезки.",
        "buds_formed": "Почки цветов следующего года уже заложены в этих побегах. Сильная обрезка сейчас их удалит.",
        "heads_protect": "Сухие соцветия, оставленные на зиму, ещё и защищают почки от мороза.",
        "leave_old_wood": "Не трогайте. Этот вид цветёт на прошлогодних побегах.",
        "right_window": "Правильное время — сразу после цветения летом.",
        "hot_dry_thirst": "Последние дни было жарко и сухо, так что это почти наверняка жажда.",
        "not_hot_dry": "Жары и засухи в последние дни не было. Если земля мокрая — возможно, перелив / гниль корней.",
        "frost_wait": "Подождите: скоро заморозки.",
        "frost_wait_note": "Заморозки ожидаются через {days} дн. Обрезка сейчас вызовет рост молодых побегов, которые погибнут от мороза. Подождите до конца зимы.",
        "frost_mild_day": "В прогнозе ещё есть заморозки: выберите сухой и тёплый день для обрезки.",
        "weather_summary": "{place}: за 7 дней до {max_temp}°C, {rain} мм осадков; {frost}.",
        "frost_in": "заморозки через {days} дн.",
        "no_frost": "заморозков в ближайшие 14 дней нет",
        "your_location": "Ваше место",
        "weather_failed": "Сейчас не удалось получить погоду; совет её не учитывает.",
        "young_gentle": "Осторожно, растение молодое.",
        "young_how": "Молодое растение: режьте примерно вдвое меньше.",
        "young_note": "Младше {years} лет: растение ещё наращивает корни. Удаляйте сухие побеги и отцветшие соцветия, но не больше половины обычной обрезки.",
        "renewal_note": "Старый куст: сделайте и омолаживающую обрезку. Каждый год вырезайте у самой земли до 1/3 самых старых и толстых побегов, чтобы их заменили молодые.",
        "cm_estimate": "При высоте {height} см это примерно {cut} см сверху.",
        "unsure_health": "По этим фото я не уверена в здоровье растения. Сфотографируйте один лист крупным планом при дневном свете.",
        "unsure_stage": "По этим фото я не уверена в стадии. Сфотографируйте куст целиком.",
        "err_type": "Неизвестный вид гортензии.",
        "err_too_large": "Фото слишком большое (максимум 15 МБ).",
        "err_not_photo": "Один из файлов не удалось прочитать как фото.",
        "err_count": "Отправьте от 1 до {max} фото.",
        "err_busy": "Приложение ещё просыпается. Попробуйте ещё раз через минуту.",
        "err_no_plant": "Я не вижу на фото растения. Сфотографируйте лист или растение целиком.",
    },
    "ky": {
        "label.healthy": "дени сак", "label.leaf_spot": "жалбырактагы тактар", "label.powdery_mildew": "ак күл оорусу",
        "label.wilting": "солуп жатат", "label.yellowing": "жалбырактар саргайып жатат", "label.unknown": "так эмес",
        "label.budding": "бүчүр байлап жатат", "label.blooming": "гүлдөп жатат", "label.fading_blooms": "гүлдөрү соолуп жатат",
        "label.dormant": "тынымда",
        "species.bigleaf": "Чоң жалбырактуу – чоң тоголок көк/кызгылт гүлдөр",
        "species.oakleaf": "Эмен жалбырактуу – жалбырактары эменге окшош",
        "species.panicle": "Шыпыргы сымал – конус формасында, көбүнчө ак",
        "species.smooth": "Дарак сымал – ак тоголок гүлдөр, мис. «Аннабель»",
        "species.unknown": "Билбейм",
        "water_first": "Адегенде сугарыңыз, кыркпаңыз.",
        "wilting_note": "Өсүмдүк көбүнчө суусагандан же ысыктан солуйт. Түбүнө мол сугарып, эртең менен текшериңиз. Оңолбосо, тамырын чирикке текшериңиз.",
        "remove_infected": "Оорулуу жалбырактарды гана алып салыңыз ({disease}).",
        "remove_infected_how": "Жабыркаган жалбырактарды үзүп, катуу жабыркаган сабактарды дени сак жерине чейин кесиңиз.",
        "bin_leaves": "Жалбырактарды таштандыга салыңыз, компостко эмес.",
        "water_soil": "Жалбырагына эмес, түбүнө сугарыңыз жана ар бир кесүүдөн кийин кайчыны тазалаңыз.",
        "hold_shaping": "Өсүмдүк айыкмайынча калыптандыруучу кыркууну кийинкиге калтырыңыз.",
        "unknown_health": "Бул сүрөттөн ден соолугун аныктай алган жокмун; кеңеш өсүмдүк дени сак деп эсептейт.",
        "yellowing_note": "Жашыл тамырчалары бар сары жалбырактар көбүнчө топурак өтө щелочтуу экенин билдирет (темир сиңбейт); кыркуу жардам бербейт. Кийинки кадам — топурактын pH деңгээлин текшерүү.",
        "tell_type": "Толук кеңеш үчүн гортензиянын түрүн тандаңыз. Азырынча соолуган гүлдөрдү гана кесиңиз.",
        "deadhead_safe_how": "Соолуган гүлдү анын астындагы биринчи жуп чоң бүчүрдөн бир аз жогору кесиңиз. Бул бардык түргө коопсуз.",
        "wood_types": "Чоң жалбырактуу жана эмен жалбырактуу өткөн жылкы сабактарда гүлдөйт, шыпыргы сымал жана дарак сымал — ушул жылкы сабактарда. Туура эмес убакта кыркуу кийинки жылдын гүлдөрүнөн ажыратат.",
        "main_prune": "Негизги кыркуу үчүн ылайыктуу убак.",
        "panicle_how": "Ар бир сабакты болжол менен үчтөн бирге, бир жуп бүчүрдөн бир аз жогору кыскартыңыз. Ичке, кайчылашкан жана куураган сабактарды түбүнөн алып салыңыз.",
        "smooth_how": "Бардык сабактарды жерден 30–45 смге чейин кесиңиз. Кыска сабактар оор гүлдөрдүн астында азыраак жыгылат.",
        "optional_tidy": "Каалоо боюнча жеңил тазалоо гана.",
        "optional_tidy_how": "Көрүнүшү жакпаса соолуган гүлдөрдү кесип салсаңыз болот; негизги кыркууну кыштын аягына калтырыңыз.",
        "dried_heads_interest": "Көп адамдар кургак гүлдөрдү кышкы кооздук катары калтырышат.",
        "not_now_new_wood": "Азыр эмес. Негизги кыркуу — кыштын аягында / жаздын башында.",
        "trim_after_flowering": "Азыр, гүлдөп бүткөндөн кийин дароо кыркыңыз.",
        "after_flowering_how": "Ар бир соолуган гүл сабагын гүлдүн астындагы биринчи жуп дени сак чоң бүчүргө чейин кесиңиз (адатта 10–30 см). Сейректетүү үчүн эң эски сабактардын бир нечесин түбүнөн алып салыңыз.",
        "stop_late_summer": "Жайдын аягына чейин бүтүрүңүз: андан кийин кийинки жылдын гүл бүчүрлөрүн кесип саласыз.",
        "dead_wood_only": "Куураган сабактарды гана алып салыңыз.",
        "dead_wood_how": "Жашыл бүчүрү жок сабактарды биринчи тирүү жуп бүчүргө чейин, толук куураганын жерге чейин кесиңиз.",
        "scratch_test": "Сабакты тырмагыңыз менен кырып көрүңүз: ичи жашыл болсо — тирүү.",
        "light_deadhead": "Гүлдөрдү гана абайлап кесиңиз.",
        "light_deadhead_how": "Гүлдүн өзүн гана, биринчи жуп бүчүрдөн бир аз жогору кесиңиз. Катуу кыркпаңыз.",
        "buds_formed": "Кийинки жылдын гүл бүчүрлөрү бул сабактарда пайда болуп калган. Азыр катуу кыркуу аларды жок кылат.",
        "heads_protect": "Кышка калтырылган кургак гүлдөр бүчүрлөрдү үшүктөн да коргойт.",
        "leave_old_wood": "Тийбеңиз. Бул түр өткөн жылкы сабактарда гүлдөйт.",
        "right_window": "Туура убак — жайында гүлдөп бүткөндөн кийин дароо.",
        "hot_dry_thirst": "Акыркы күндөрү ысык жана кургак болду, демек бул дээрлик сөзсүз суусагандык.",
        "not_hot_dry": "Акыркы күндөрү ысык жана кургак болгон жок. Топурак нымдуу болсо — суу көп берилген / тамыр чириши мүмкүн.",
        "frost_wait": "Күтө туруңуз: үшүк жакындап калды.",
        "frost_wait_note": "{days} күндөн кийин үшүк күтүлөт. Азыр кыркуу жаш сабактарды өстүрөт, алар үшүктөн өлөт. Кыштын аягына чейин күтүңүз.",
        "frost_mild_day": "Божомолдо дагы эле үшүк бар: кыркуу үчүн кургак, жылуу күндү тандаңыз.",
        "weather_summary": "{place}: акыркы 7 күндө {max_temp}°C чейин, {rain} мм жаан; {frost}.",
        "frost_in": "{days} күндөн кийин үшүк",
        "no_frost": "жакынкы 14 күндө үшүк жок",
        "your_location": "Сиздин жайгашкан жериңиз",
        "weather_failed": "Азыр аба ырайын алуу мүмкүн болгон жок; кеңеш аны эске албайт.",
        "young_gentle": "Абайлаңыз, өсүмдүк жаш.",
        "young_how": "Жаш өсүмдүк: болжол менен эки эсе азыраак кесиңиз.",
        "young_note": "{years} жашка чейин: өсүмдүк дагы эле тамыр жайып жатат. Куураган сабактарды жана соолуган гүлдөрдү алыңыз, бирок адаттагы кыркуунун жарымынан ашпасын.",
        "renewal_note": "Эски бадал: жаңыртуучу кыркууну да жасаңыз. Жаш сабактар ордун алышы үчүн жыл сайын эң эски, жоон сабактардын 1/3ине чейин жерге жакын кесиңиз.",
        "cm_estimate": "{height} см бийиктикте бул үстүнөн болжол менен {cut} см.",
        "unsure_health": "Бул сүрөттөрдөн өсүмдүктүн ден соолугуна ишенимим жок. Бир жалбыракты күндүзгү жарыкта жакындан тартыңыз.",
        "unsure_stage": "Бул сүрөттөрдөн өсүү баскычына ишенимим жок. Бадалды толугу менен тартыңыз.",
        "err_type": "Белгисиз гортензия түрү.",
        "err_too_large": "Сүрөт өтө чоң (эң көп 15 МБ).",
        "err_not_photo": "Файлдардын бири сүрөт катары окулган жок.",
        "err_count": "1ден {max}ге чейин сүрөт жөнөтүңүз.",
        "err_busy": "Колдонмо дагы эле ойгонуп жатат. Бир аздан кийин кайра аракет кылыңыз.",
        "err_no_plant": "Сүрөттө өсүмдүк көрүнбөйт. Жалбырактын же өсүмдүктүн толугу менен сүрөтүн тартыңыз.",
    },
}

from .i18n_plants import PLANT_MESSAGES  # noqa: E402

for _lang, _msgs in PLANT_MESSAGES.items():
    MESSAGES[_lang].update(_msgs)


def t(key: str, lang: str = "en", **params) -> str:
    """Translate one key. Falls back to English if a translation is missing."""
    text = MESSAGES.get(lang, {}).get(key) or MESSAGES["en"][key]
    return text.format(**{k: t(v.key, lang, **v.params) if isinstance(v, Msg) else v for k, v in params.items()})


@dataclass
class Msg:
    """A sentence that hasn't been translated yet: a key plus its {placeholders}."""
    key: str
    params: dict = field(default_factory=dict)

    def render(self, lang: str = "en") -> str:
        return t(self.key, lang, **self.params)


def M(key: str, **params) -> Msg:
    return Msg(key, params)
