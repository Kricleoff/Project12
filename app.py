from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = 'VWn4z2XGS65BKGxiW409goZLc8PvmgDF'

def get_weather_data(city, api_key):
    url = "http://dataservice.accuweather.com/locations/v1/cities/search"
    params = {'apikey': api_key, 'q': city}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        location_data = response.json()
        if location_data:
            location_key = location_data[0]['Key']

            f_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
            f_param = {'apikey': api_key, 'metric': 'true'}
            f_response = requests.get(f_url, params=f_param)

            url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
            param = {'apikey': api_key, 'details': 'true'}
            c_response = requests.get(url, params=param)

            if f_response.status_code == 200 and c_response.status_code == 200:
                f_data = f_response.json()
                c_data = c_response.json()

                if 'DailyForecasts' in f_data and c_data:
                    daily_forecast = f_data['DailyForecasts'][0]
                    current_conditions = c_data[0]

                    temperature = daily_forecast['Temperature']['Maximum']['Value']
                    precipitation_probability = daily_forecast['Day'].get('PrecipitationProbability', 0)
                    wind_speed = current_conditions['Wind']['Speed']['Metric']['Value']
                    humidity = current_conditions['RelativeHumidity']

                    return {
                        'city': city,
                        'temperature': temperature,
                        'wind_speed': wind_speed,
                        'precipitation_probability': precipitation_probability,
                        'humidity': humidity
                    }
    return None


def is_bad_weather(weather_data):
    if weather_data['temperature'] < -5 or weather_data['temperature'] > 35:
        return True
    if weather_data['wind_speed'] > 50:
        return True
    if weather_data['precipitation_probability'] > 70:
        return True
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_results = []
    error_message = None

    if request.method == 'POST':
        start_city = request.form.get('start_city')
        end_city = request.form.get('end_city')

        if start_city and end_city:
            for city in [start_city, end_city]:
                weather_info = get_weather_data(city, API_KEY)
                if weather_info:
                    weather_info['is_bad'] = is_bad_weather(weather_info)
                    weather_results.append(weather_info)
                else:
                    error_message = f"Упс. Неверно введён город {city}. Проверьте название!"
        else:
            error_message = 'Пожалуйста, введите начальную и конечную точки маршрута!'

    return render_template('index.html', weather_results=weather_results, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
