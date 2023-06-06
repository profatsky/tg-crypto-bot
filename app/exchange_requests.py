import datetime

import aiohttp


class ExchangeRequests:
    API_PATH = "https://api.coingecko.com/api/v3/"

    @staticmethod
    def _build_query(host: str, method: str, params: dict = None) -> str:
        url = host + method + "?"
        if params:
            url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url

    async def search_coin(self, coin_name: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self._build_query(
                        self.API_PATH,
                        "search",
                        params={"query": coin_name}
                    )
            ) as resp:
                data = await resp.json()
                return data

    async def get_coin_prices(self, coin_ids: list[str]) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self._build_query(
                        self.API_PATH,
                        "simple/price",
                        params={
                            "ids": ",".join(coin_ids),
                            "vs_currencies": "usd"
                        }
                    )
            ) as resp:
                data = await resp.json()
                return data

    async def get_coin_price_by_date(self, coin_id: int, start_date: datetime.date) -> dict:
        start_date = f"{start_date.day}-{start_date.month}-{start_date.year}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self._build_query(
                        self.API_PATH,
                        f"coins/{coin_id}/history?date={start_date}"
                    )
            ) as resp:
                data = await resp.json()
                return data

    async def get_market_chart(self, coin_id: int, days: int):
        if days == 1:
            interval = "hourly"
        elif days == 7:
            interval = "daily"
        else:
            interval = "daily"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    self._build_query(
                        self.API_PATH,
                        f"coins/{coin_id}/market_chart",
                        params={
                            "vs_currency": "usd",
                            "days": days,
                            "interval": interval
                        }
                    )
            ) as resp:
                data = await resp.json()
                return data

    async def get_coins_info(self, coin_names: list[str], days: int) -> list[dict] | None:
        coin_data = []
        for coin_name in coin_names:
            # Получаем id, токен, имя и изображение монеты
            data = await self.search_coin(coin_name)
            if data["coins"]:
                coin_data.append(data["coins"][0])

        if coin_data:
            coins_price = await self.get_coin_prices([coin["id"] for coin in coin_data])

            # Соединяем данные о монете и о ее цене
            for count, coin in enumerate(coin_data):
                # Поиск цены в дату начала указанного интервала
                start_date = datetime.date.today() - datetime.timedelta(days=days)
                old_price = await self.get_coin_price_by_date(coin["id"], start_date)
                old_price = old_price["market_data"]["current_price"]["usd"]

                # Изменение цены за указанный период
                change = (coins_price[coin["id"]]["usd"] - old_price) / (old_price / 100)
                coin["change"] = change
                coins_price[coin["id"]].update({"change": change})
                coin_data[count].update(coins_price[coin["id"]])

                # Данные об изменении цены для построения графика
                price_history = await self.get_market_chart(coin["id"], days)
                coin["price_history"] = [price for _, price in price_history["prices"]]

            return coin_data
