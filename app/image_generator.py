import datetime
import os.path
from io import BytesIO

import matplotlib.pyplot as plt
from matplotlib.pyplot import Figure
from PIL import Image, ImageFont, ImageDraw


class ImageGenerator:
    ASSETS_PATH = "assets"

    @staticmethod
    def convert_img_to_bytesio(img: Image) -> BytesIO:
        bio = BytesIO()
        img.save(bio, 'png')
        bio.seek(0)
        return bio

    @staticmethod
    def figure_to_img(fig: Figure) -> Image:
        bio = BytesIO()
        fig.savefig(bio, transparent=True, dpi=180)
        fig.clear()
        bio.seek(0)
        img = Image.open(bio)
        return img

    def graphing(self, coins_data: list[dict], days: int) -> Image:
        ax = plt.axes()
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        if days == 1:
            num = 24
        elif days == 7:
            num = 7
        else:
            num = 31

        for coin in coins_data:
            plt.plot([day for day in range(1, num + 1)], coin["price_history"][:num], label=coin["name"])
        plt.legend()
        plt.grid(which="major", linewidth=0.2)

        fig = plt.gcf()
        return self.figure_to_img(fig)

    def create_image_with_cryptocurrency_rate(self, coins_data: list[dict], days: int) -> Image:
        height = 128 * len(coins_data)
        background_img = Image.new('RGB', (1080, 1100 + height), color="#FFFFFF")
        draw = ImageDraw.Draw(background_img)
        main_font = ImageFont.truetype(f"{self.ASSETS_PATH}/fonts/VelaSans-Medium.ttf", size=50)

        # Заголовок
        if days == 1:
            text = "24 часа"
        elif days == 7:
            text = "неделю"
        else:
            text = "месяц"
        draw.text(
            xy=(60, 60),
            text=f"Изменения за {text}",
            font=ImageFont.truetype(f"{self.ASSETS_PATH}/fonts/VelaSans-SemiBold.ttf", size=72),
            fill="#000000",
        )

        # Подзаголовок с датой
        date_info = datetime.datetime.now().strftime('%d %m %H:%M %S').split()
        month_ru = {1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня",
                    7: "июля", 8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}
        draw.text(
            xy=(60, 156),
            text=f"{int(date_info[0])} {month_ru[int(date_info[1])]}, {date_info[2]}",
            font=main_font,
            fill="#676767"
        )

        # Данные о криптовалютах
        y = 292
        for count, coin in enumerate(coins_data):
            # Лого
            if os.path.isfile(f"{self.ASSETS_PATH}/images/{coin['id']}.webp"):
                icon = Image.open(f"{self.ASSETS_PATH}/images/{coin['id']}.webp").convert("RGBA")
            else:
                icon = Image.open(f"{self.ASSETS_PATH}/images/unknown.png")
            icon = icon.resize((80, 80), Image.ANTIALIAS)
            background_img.paste(icon, (60, y), icon)

            # Название
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
                draw.text(
                    xy=(1024, y + 59),
                    text="\u2193{:,.2f}%".format(- coin['change']),
                    font=main_font,
                    fill="#DC8E8E",
                    anchor="rs"
                )
            else:
                draw.text(
                    xy=(1024, y + 59),
                    text="\u2191{:,.2f}%".format(coin['change']),
                    font=main_font,
                    fill="#8EDCAC",
                    anchor="rs"
                )

            # Линия
            if count < len(coins_data) - 1:
                draw.line((164, y + 105, 1020, y + 105), fill="#CECECE", width=3)
            y += 128

        graph = self.graphing(coins_data, days=days)
        background_img.paste(graph, (-25, y - 100), graph)

        return self.convert_img_to_bytesio(background_img)
