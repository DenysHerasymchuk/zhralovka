"""Cafeteria price board, typed in from the printed board; update by hand when it changes.

Prices are in cents: (student/staff card, TM intern card, Bancontact).
"""
from typing import NamedTuple


class Item(NamedTuple):
    nl: str
    en: str
    student: int
    intern: int
    bancontact: int


class Section(NamedTuple):
    emoji: str
    nl: str
    en: str
    items: tuple[Item, ...]


SECTIONS = (
    Section("🥪", "Broodjes", "Sandwiches", (
        Item("Broodje", "Bread roll", 95, 95, 120),
        Item("Baguette club", "Baguette club", 450, 450, 540),
        Item("Broodje upgrade", "Baguette snack", 545, 545, 660),
        Item("Broodje luxe", "Baguette luxe", 595, 595, 720),
        Item("Piccolo belegd", "Roll + spread", 220, 220, 270),
    )),
    Section("🍲", "Warm eten", "Hot meals", (
        Item("Kom soep", "Soup", 125, 165, 200),
        Item("Dagschotel", "Daily special", 540, 1010, 1220),
        Item("Friet + saus", "Fries + mayo", 360, 360, 440),
        Item("Snack + friet", "Snack + fries", 600, 600, 720),
        Item("Kleine snack", "Fried snack", 310, 310, 380),
        Item("Panini", "Panini", 520, 520, 630),
        Item("Worstenbroodje", "Sausage roll", 250, 250, 300),
        Item("Bladerdeeg", "Puff pastry", 250, 250, 300),
        Item("Frikandel kip", "Chicken roll", 300, 300, 360),
        Item("Pizzabaguette", "Pizzabaguette", 400, 400, 480),
        Item("Quiche", "Quiche", 355, 355, 430),
        Item("Croque + saus", "Croque + sauce", 305, 305, 370),
    )),
    Section("🥗", "Koude schotel", "Cold dishes", (
        Item("Saladbar menu", "Salad bar menu", 540, 875, 1050),
        Item("Extra potje", "Extra cup", 295, 295, 360),
        Item("Rauwkost mini", "Salad mini", 180, 180, 220),
    )),
    Section("🍰", "Desserten", "Desserts", (
        Item("Donut/muffin", "Donut/muffin", 170, 170, 210),
        Item("Gebak", "Pastry", 220, 220, 260),
        Item("Alpro pudding", "Alpro pudding", 150, 150, 180),
        Item("Danio 165 g", "Danio 165 g", 280, 280, 340),
        Item("Fruitsla", "Fruit salad", 245, 245, 300),
        Item("Snoep/candybar", "Candy bar", 160, 160, 200),
    )),
    Section("🥤", "Dranken", "Drinks", (
        Item("Warme drank", "Hot drink", 150, 150, 180),
        Item("Brik drank", "Brick drink", 170, 170, 200),
        Item("Starbucks iced", "Starbucks iced", 345, 345, 420),
        Item("Smoothie 25 cl", "Smoothie 25 cl", 300, 300, 360),
        Item("Proteïneshake", "Protein shake", 385, 385, 470),
        Item("Arizona ice tea", "Arizona ice tea", 240, 240, 290),
        Item("Water 33 cl", "Water 33 cl", 145, 145, 180),
        Item("Frisdrank blik", "Soft drink can", 160, 160, 200),
        Item("Monster", "Monster", 240, 240, 290),
    )),
)


# Ukrainian names, keyed by the English name of each section and item.
UK_NAMES = {
    "Sandwiches": "Сендвічі",
    "Bread roll": "Булочка",
    "Baguette club": "Багет клаб",
    "Baguette snack": "Багет снек",
    "Baguette luxe": "Багет люкс",
    "Roll + spread": "Булочка з начинкою",
    "Hot meals": "Гарячі страви",
    "Soup": "Суп",
    "Daily special": "Страва дня",
    "Fries + mayo": "Картопля фрі + майонез",
    "Snack + fries": "Снек + фрі",
    "Fried snack": "Смажений снек",
    "Panini": "Паніні",
    "Sausage roll": "Ковбаска в тісті",
    "Puff pastry": "Листкова випічка",
    "Chicken roll": "Курка в тісті",
    "Pizzabaguette": "Піца-багет",
    "Quiche": "Кіш",
    "Croque + sauce": "Крок + соус",
    "Cold dishes": "Холодні страви",
    "Salad bar menu": "Салат-бар меню",
    "Extra cup": "Додаткова порція",
    "Salad mini": "Міні-салат",
    "Desserts": "Десерти",
    "Donut/muffin": "Пончик/мафін",
    "Pastry": "Тістечко",
    "Alpro pudding": "Пудинг Alpro",
    "Danio 165 g": "Danio 165 г",
    "Fruit salad": "Фруктовий салат",
    "Candy bar": "Батончик",
    "Drinks": "Напої",
    "Hot drink": "Гарячий напій",
    "Brick drink": "Напій у пачці",
    "Starbucks iced": "Starbucks айс-кава",
    "Smoothie 25 cl": "Смузі 25 cl",
    "Protein shake": "Протеїновий шейк",
    "Arizona ice tea": "Arizona айс-ті",
    "Water 33 cl": "Вода 33 cl",
    "Soft drink can": "Газований напій",
    "Monster": "Monster",
}


def _item(en: str) -> Item:
    return next(item for section in SECTIONS for item in section.items if item.en == en)


# Menu API category (English, lowercase substring) -> board row; first hit wins.
CATEGORY_PRICES = (
    ("soup", _item("Soup")),
    ("lunch", _item("Daily special")),
    ("suggestion", _item("Daily special")),
    ("salad", _item("Salad bar menu")),
    ("sandwich", _item("Baguette snack")),
    ("snack", _item("Snack + fries")),
)


def category_price(category_en: str) -> Item | None:
    name = category_en.lower()
    return next((item for key, item in CATEGORY_PRICES if key in name), None)
