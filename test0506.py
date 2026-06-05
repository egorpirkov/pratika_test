import requests

LASTFM_API_KEY = "ea02299f81024fec786866b33972cbfc"
LASTFM_USERNAME = "cameinwit"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"


def test_lastfm_connection():
    params = {
        "method": "user.gettopartists",
        "user": LASTFM_USERNAME,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": 10,
    }

    print(f"Отправка запроса к Last.fm для пользователя {LASTFM_USERNAME}...")

    try:
        response = requests.get(BASE_URL, params=params)
        print(f"Статус-код ответа: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if "topartists" in data:
                artists = data["topartists"]["artist"]
                print("\n Соединение успешно! Топ-артисты пользователя:")
                for index, artist in enumerate(artists, start=1):
                    print(
                        f"{index}. {artist['name']} (Прослушиваний: {artist['playcount']})"
                    )
            else:
                print(
                    "\n Запрос прошёл, но формат данных неожиданный. Возможно, у пользователя нет прослушиваний."
                )
                print(data)
        elif response.status_code == 401:
            print("\n Ошибка 401: Неверный API-ключ (Unauthorized).")
        else:
            print(f"\n Произошла ошибка. Ответ сервера: {response.text}")
    except Exception as e:
        print(f"\n Не удалось связаться с сервером. Ошибка: {e}")


if __name__ == "__main__":
    test_lastfm_connection()
