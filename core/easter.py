"""The footer giraffe: animal facts on click, a promo code after EGG_CLICKS clicks, seasonal looks.

Seasons follow the Tashkent calendar and clock (settings.TIME_ZONE):
new year 20 Dec – 10 Jan (hat), March (Navruz flowers), 22:00–07:00 (asleep, «Zzz»).
"""
from django.utils import timezone

EGG_CLICKS = 7

# (ru, uz, en)
FACTS = [
    ("Жираф спит всего 30 минут — 2 часа в сутки, часто стоя.",
     "Jirafa sutkasiga atigi 30 daqiqadan 2 soatgacha uxlaydi, koʻpincha tik turib.",
     "Giraffes sleep only 30 minutes to 2 hours a day, often standing up."),
    ("В шее жирафа 7 позвонков — столько же, сколько у человека.",
     "Jirafaning boʻynida 7 ta umurtqa bor — xuddi odamnikidek.",
     "A giraffe's neck has 7 vertebrae — the same number as yours."),
    ("Язык жирафа длиной около 45 см. Считается, что тёмный цвет защищает его от солнца.",
     "Jirafaning tili 45 sm atrofida. Uning toʻq rangi tilni quyoshdan himoya qiladi, deb hisoblanadi.",
     "A giraffe's tongue is about 45 cm long; its dark colour is thought to protect it from the sun."),
    ("Сердце взрослого жирафа весит около 11 кг.",
     "Katta jirafaning yuragi taxminan 11 kg keladi.",
     "An adult giraffe's heart weighs about 11 kg."),
    ("Новорождённый жирафёнок ростом около 1,8 м и уже через час стоит на ногах.",
     "Yangi tugʻilgan jirafa bolasining boʻyi 1,8 m atrofida, bir soatdan keyin esa oyoqqa turadi.",
     "A newborn giraffe is about 1.8 m tall and stands up within an hour."),
    ("Кошки спят 12–16 часов в сутки.",
     "Mushuklar sutkasiga 12–16 soat uxlaydi.",
     "Cats sleep 12–16 hours a day."),
    ("Кошки не чувствуют сладкого вкуса.",
     "Mushuklar shirin taʼmni sezmaydi.",
     "Cats can't taste sweetness."),
    ("В каждом ухе кошки 32 мышцы — поэтому уши поворачиваются почти на 180°.",
     "Mushukning har bir qulogʻida 32 ta muskul bor — shuning uchun quloqlari deyarli 180° buriladi.",
     "Each cat ear has 32 muscles, so it can turn almost 180°."),
    ("Кошка мурлычет на частоте 25–150 Гц.",
     "Mushuk 25–150 Gs chastotada xurillaydi.",
     "A cat purrs at 25–150 Hz."),
    ("Рисунок на носу собаки уникален, как отпечаток пальца у человека.",
     "Itning burnidagi naqsh odamning barmoq izi kabi takrorlanmasdir.",
     "The pattern on a dog's nose is as unique as a human fingerprint."),
    ("Собаки потеют в основном через подушечки лап.",
     "Itlar asosan panjalarining yostiqchalari orqali terlaydi.",
     "Dogs sweat mostly through their paw pads."),
    ("Собаки различают цвета, но видят мир в основном в синих и жёлтых тонах.",
     "Itlar ranglarni ajratadi, lekin dunyoni asosan koʻk va sariq tuslarda koʻradi.",
     "Dogs see colour, mostly in shades of blue and yellow."),
    ("Средняя собака понимает около 165 слов и жестов.",
     "Oʻrtacha it 165 ga yaqin soʻz va imo-ishorani tushunadi.",
     "An average dog understands about 165 words and gestures."),
    ("Щенки рождаются слепыми и глухими: глаза открываются примерно через две недели.",
     "Kuchukchalar koʻr va kar tugʻiladi: koʻzlari taxminan ikki haftadan keyin ochiladi.",
     "Puppies are born blind and deaf; their eyes open after about two weeks."),
    ("Попугаи жако могут выучить сотни слов.",
     "Jako toʻtiqushlari yuzlab soʻzni oʻrganishi mumkin.",
     "African grey parrots can learn hundreds of words."),
    ("Волнистые попугайчики видят ультрафиолет.",
     "Toʻlqinsimon toʻtiqushlar ultrabinafsha nurni koʻradi.",
     "Budgies can see ultraviolet light."),
    ("Золотая рыбка помнит не 3 секунды, а несколько месяцев.",
     "Oltin baliq 3 soniya emas, bir necha oy eslab qoladi.",
     "A goldfish remembers things for months, not 3 seconds."),
    ("Зубы хомяков растут всю жизнь — поэтому им нужно что-то грызть.",
     "Hamsterlarning tishlari butun umr oʻsadi — shuning uchun ularga kemiradigan narsa kerak.",
     "Hamster teeth grow all their life, so they need something to chew."),
    ("Счастливая морская свинка подпрыгивает на месте — это называют «попкорнингом».",
     "Xursand dengiz choʻchqachasi joyida sakraydi — buni «popkorning» deyishadi.",
     "A happy guinea pig jumps on the spot — it's called «popcorning»."),
    ("Кролики видят почти на 360°, не поворачивая головы.",
     "Quyonlar boshini burmasdan deyarli 360° koʻradi.",
     "Rabbits can see almost 360° without turning their heads."),
]

LANG_INDEX = {"ru": 0, "uz": 1, "en": 2}


def facts(lang: str) -> list[str]:
    i = LANG_INDEX.get(lang, 0)
    return [f[i] for f in FACTS]


def moods(now=None) -> list[str]:
    """Seasonal looks for the giraffe: any of "newyear", "navruz", "night"."""
    now = timezone.localtime(now)
    found = []
    if (now.month == 12 and now.day >= 20) or (now.month == 1 and now.day <= 10):
        found.append("newyear")
    elif now.month == 3:
        found.append("navruz")
    if now.hour >= 22 or now.hour < 7:
        found.append("night")
    return found
