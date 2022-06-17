import datetime
import requests
import os.path
from typing import List
from io import BytesIO

import matplotlib.pyplot as plt
from matplotlib.pyplot import Figure
from PIL import Image, ImageFont, ImageDraw


async def get_img_to_send(img: Image) -> BytesIO:
    """Преобразование Image в BytesIO"""
    bio = BytesIO()
    img.save(bio, 'png')
    bio.seek(0)
    return bio


async def fig_to_img(fig: Figure) -> Image:
    """Преобразование Figure в Image"""
    bio = BytesIO()
    fig.savefig(bio, transparent=True, dpi=180)
    fig.clear()
    bio.seek(0)
    img = Image.open(bio)
    return img


async def create_graph(coins_data: List[dict], days: int) -> Image:
    """Создание графика на основе входных данных"""
    ax = plt.axes()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    if days == 1:
        interval = "hourly"
        num = 24
    elif days == 7:
        interval = "daily"
        num = 7
    else:
        interval = "daily"
        num = 31

    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": interval
    }

    for coin in coins_data:
        prices = requests.get(url=f"https://api.coingecko.com/api/v3/coins/{coin['id']}/market_chart", params=params)
        prices = [price for _, price in prices.json()['prices']][:num]
        plt.plot([day for day in range(1, num + 1)], prices, label=coin["name"])
    plt.legend()
    plt.grid(which="major", linewidth=0.2)

    fig = plt.gcf()
    return await fig_to_img(fig)


async def create_img(coins_data: List[dict], days: int) -> Image:
    """Созданик изображения с курсами криптовалют"""
    # Создание белого фона
    height = 128 * len(coins_data)
    background_img = Image.new('RGB', (1080, 1100 + height), color="#FFFFFF")
    # Объект для рисования
    draw = ImageDraw.Draw(background_img)
    # Основной шрифт
    main_font = ImageFont.truetype("assets/fonts/VelaSans-Medium.ttf", size=50)

    # Заголовок
    if days == 1:
        text = "24 часа"
    elif days == 7:
        text = "неделю"
    else:
        text = "месяц"

    draw.text(
        (60, 60),
        f"Изменения за {text}",
        font=ImageFont.truetype("assets/fonts/VelaSans-SemiBold.ttf", size=72),
        fill="#000000",
    )

    # Преобразование даты в нужный формат
    date_info = datetime.datetime.now().strftime('%d %m %H:%M %S').split()
    month_ru = {1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
                7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}

    # Подзаголовок с датой
    draw.text(
        (60, 156),
        f"{int(date_info[0])} {month_ru[int(date_info[1])]}, {date_info[2]}",
        font=main_font,
        fill="#676767"
    )

    y = 292
    for count, coin in enumerate(coins_data):
        # Логотип монеты
        if os.path.isfile(f"assets/images/{coin['id']}.webp"):
            icon = Image.open(f"assets/images/{coin['id']}.webp").convert("RGBA")
        else:
            icon = Image.open(f"assets/images/unknown.png")
        icon = icon.resize((80, 80), Image.ANTIALIAS)
        background_img.paste(icon, (60, y), icon)
        # Название криптовалюты
        if len(coin['name']) > 9:
            draw.text((164, y + 5), text=f"{coin['name'][:10]}.", font=main_font, fill="#000000")
        else:
            draw.text((164, y + 5), text=coin['name'], font=main_font, fill="#000000")
        # Стоимость
        draw.text(
            (743, y + 59),
            "${:,.2f}".format(coin['usd']),
            font=main_font,
            fill="#000000",
            anchor="rs"
        )
        # Изменение цены за последние 24 часа
        if coin['change'] < 0:
            draw.text((1024, y + 59), "\u2193{:,.2f}%".format(- coin['change']), font=main_font,
                      fill="#DC8E8E", anchor="rs")
        else:
            draw.text((1024, y + 59), "\u2191{:,.2f}%".format(coin['change']), font=main_font,
                      fill="#8EDCAC", anchor="rs")
        # Линия
        if count < len(coins_data) - 1:
            draw.line((164, y + 105, 1020, y + 105), fill="#CECECE", width=3)
        y += 128

    graph = await create_graph(coins_data, days=days)
    background_img.paste(graph, (-25, y - 100), graph)

    return await get_img_to_send(background_img)
