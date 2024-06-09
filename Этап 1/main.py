import csv 
import os
import logging
import requests

from dotenv import load_dotenv


def get_weather_data(coordinates):
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    params = {
        'lat': coordinates.split(',')[0],
        'lon': coordinates.split(',')[1],
        'extra': True,
        'limit': 7
    }
    headers = {
        'X-Yandex-API-Key': API_KEY
    }
    response = requests.get(BASE_URL, params=params, headers=headers)
    logger.info('Получение данных')
    return response.json()


def process_weather_data(data):
    weather_records = []
    for day in data['forecasts']:
        date = day['date']
        for hour in day['hours']:
            if not hour:
                continue
            is_rainy = 1 if hour['condition'].lower().find("дождь") != -1 else 0
            weather_records.append([
                data['geo_object']['locality']['name'],
                date,
                hour['hour'],
                hour['temp'],
                hour['pressure_mm'],
                is_rainy
            ])
    return weather_records


def save_to_csv(weather_data):
    with open('weather_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                'city',
                'date',
                'hour',
                'temperature_c',
                'pressure_mm',
                'is_rainy'
            ]
        )
        for record in weather_data:
            writer.writerow(record)


def main():
    """
    Главная функция, где вызываются подряд все 
    описанные в задании действия
    """
    all_weather_data = []
    # Перебираем координаты
    for coordinates in CITIES.values():
        # Получаем данные по АПИ ввиде JSON
        data = get_weather_data(coordinates)
        if 'forecasts' not in data:
            continue
        city_weather_data = process_weather_data(data)
        all_weather_data.extend(city_weather_data)

    save_to_csv(all_weather_data)


if __name__ == '__main__':
    # Задаем словарь городов, для которых
    # необходимо выгрузить прогнозные данные
    # АПИ принимает координаты, можно было бы обойтись просто списком
    # Но так удобнее и нагляднее, принцип DRY
    CITIES = {
        "Moscow": "55.7558,37.6173",
        "Kazan": "55.7963,49.1088",
        "Saint_Petersburg": "59.9311,30.3609",
        "Tula": "54.1920,37.6150",
        "Novosibirsk": "55.0084,82.9357"
    }
    # Ссылка на АПИ яндекса, откуда будем получать прогноз
    BASE_URL = 'https://api.weather.yandex.ru/v2/forecast'
    # Настраиваем запись логов в файл для отладки
    logging.basicConfig(
        filename='api_weather.log',
        filemode='a',  # добавляет строки в файл, а не перезаписывает его
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    # Запуск работы
    main()
