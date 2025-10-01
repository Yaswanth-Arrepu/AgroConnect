import requests
import datetime
API_KEY = 'your api key here' 

def fetch_weather(latitude, longitude, exclude=None):
    if not latitude or not longitude:
        raise ValueError("Latitude and longitude are required.")
    try:
        url = "https://api.openweathermap.org/data/3.0/onecall"
        params = {
            'lat': latitude,
            'lon': longitude,
            'exclude': exclude if exclude else '',
            'appid': API_KEY,
            'units': 'metric' 
        }
        response = requests.get(url, params=params)
        response.raise_for_status() 
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Error fetching weather data: {e}")
def process_weather_data(weather_data):
    current_weather = weather_data.get('current', {})
    current_temp = current_weather.get('temp', 'N/A')
    current_description = current_weather.get('weather', [{}])[0].get('description', 'No description available')
    current_icon = current_weather.get('weather', [{}])[0].get('icon', '01d')
    today_weather = {
        'temp': f"{current_temp}°C" if current_temp != 'N/A' else 'N/A',
        'description': current_description.capitalize(),
        'icon': f"https://openweathermap.org/img/wn/{current_icon}@2x.png"
    }
    daily_forecast = weather_data.get('daily', [])
    if not daily_forecast:
        raise ValueError("No daily forecast data available.")
    forecast_weather = []
    for day in daily_forecast:
        date_unix = day.get('dt', 'N/A')
        date = datetime.datetime.utcfromtimestamp(date_unix).strftime('%A, %B %d') if date_unix != 'N/A' else 'N/A'
        temp = day.get('temp', {})
        icon = day.get('weather', [{}])[0].get('icon', '01d')
        description = day.get('weather', [{}])[0].get('description', 'No description available')
        precipitation_chance = day.get('pop', 0) * 100  
        rainfall = day.get('rain', 0)
        avg_temp = (
            temp.get('morn', 0) + 
            temp.get('day', 0) + 
            temp.get('eve', 0) + 
            temp.get('night', 0)
        ) / 4
        forecast_weather.append({
            'date': date,
            'avg_temp': f"{avg_temp:.2f}°C",  # Average temperature
            'icon': f"https://openweathermap.org/img/wn/{icon}@2x.png",
            'description': description.capitalize(),
            'precipitation_chance': f"{precipitation_chance:.0f}%" if precipitation_chance else '0%',
            'rainfall': f"{rainfall} mm" if rainfall else '0 mm',
        })
    return today_weather, forecast_weather
def get_7_day_weather_average(latitude, longitude):
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        'lat': latitude,
        'lon': longitude,
        'exclude': 'current,minutely,hourly,alerts',
        'appid': API_KEY,
        'units': 'metric'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        forecast_data = response.json()
        
        daily_forecasts = forecast_data.get("daily", [])
        if not daily_forecasts:
            raise ValueError("No daily forecast data available.")
        
        total_temp = 0
        total_rainfall = 0
        days_with_rain = 0
        
        for day in daily_forecasts[:7]:  # take only 7 days
            day_temp = day.get("temp", {}).get("day")
            if day_temp is not None:
                total_temp += day_temp
            
            rainfall = day.get("rain", 0)
            total_rainfall += rainfall
            if rainfall > 0:
                days_with_rain += 1
        
        avg_temp = total_temp / len(daily_forecasts[:7])
        avg_rainfall = total_rainfall / days_with_rain if days_with_rain > 0 else 0
        
        return avg_temp, avg_rainfall
    
    except requests.RequestException as e:
        print(f"Error fetching forecast data: {e}")
        return None, None

def get_weather_data(lat, lon):
    URL = "https://pro.openweathermap.org/data/2.5/forecast/hourly"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(URL, params=params)
    data = response.json()
    print(data)
    current_weather = data["list"][0]  
    current_date = datetime.datetime.fromtimestamp(current_weather["dt"]).strftime("%A, %B %d, %Y")
    current_temp = round(current_weather["main"]["temp"], 1)
    current_wind_speed = current_weather["wind"]["speed"]
    current_pop = round(current_weather.get("pop", 0) * 100, 1)
    hourly_forecast = []
    for entry in data["list"][:24]:  
        dt_obj = datetime.datetime.fromtimestamp(entry["dt"])
        time = dt_obj.strftime("%I %p")
        hour = dt_obj.hour 
        temp = round(entry["main"]["temp"], 1)
        wind_speed = entry["wind"]["speed"]
        rain = entry.get("rain", {}).get("1h", 0) 
        weather_main = entry["weather"][0]["main"].lower()
        if "rain" in weather_main:
            icon = "rain.png"
        elif "cloud" in weather_main:
            icon = "cloudy.png"
        elif "clear" in weather_main:
            if hour < 6 or hour >= 18:
                icon = "moon.png"  
            else:
                icon = "sunny.png" 
        else:
            icon = "partly_sunny.png"
        hourly_forecast.append({"time": time, "temp": temp, "wind": wind_speed, "rain": rain, "icon": icon})
    return {
        "date": current_date,
        "current_temp": current_temp,
        "current_wind_speed": current_wind_speed,
        "current_pop": current_pop,
        "hourly_forecast": hourly_forecast
    }
