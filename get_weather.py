import requests
from datetime import datetime
from database import db

def get_weather():
    API_KEY = '1f22d5aa77094be4f98e5f96bf2a008b'

    response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat=44.34&lon=10.99&appid={API_KEY}')

    now = datetime.now()

    

    if response.ok:
        data = response.json()
        city = data['name']
        min = round(data['main']['temp_min'] - 273.15 , 2)
        max = round(data['main']['temp_max'] - 273.15, 2)
        temp = data['main']['temp']
        pressure = data['main']['pressure']
        humidity = data['main']['humidity']
        temp_c = round(temp - 273.15 ,2)

        # print(f'Miejsce: {city}' + '\n')
        # print(f'Min temp: {min}' + '\n')
        # print(f'Max temp: {max}' + '\n')
        print(f'Temperatura: {temp_c}' + '\n')
        # print(f'Wilgotność: {humidity}\n')
        # print(f'Ciśnienie: {pressure}\n')

        db.weather.insert_one({
            "city" : city,
            "temperature" : temp_c,
            "temp_min" : min,
            "temp_max" : max,
            "pressure" : pressure,
            "humidity" : humidity,
            "time": now.strftime("%H:%M"),
            "date": now.strftime("%d/%m/%y")
            })
    