import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime
from geopy.geocoders import Nominatim

class LoadFromApi:
    """This class contains functionality to load data from the open-meteo api. For now it only loads daily data"""

    @staticmethod
    def get_geo_loc(city:str, country:str) -> tuple[float]:
        """get_geo_loc returns a tuple with the first element being the latitude and the second element being the longitude"""

        city = city.capitalize()
        country = country.capitalize()
        
        geolocator = Nominatim(user_agent='geoapi')
        location = geolocator.geocode(f'{city}, {country}')
        latitude, longitude = location.latitude, location.longitude

        return latitude, longitude
    
    @staticmethod
    def create_openmeteo_client(expire_after:int=-1, num_retries:int=5, backoff_factor:float=0.2):
        cache_session = requests_cache.CachedSession('.cache', expire_after = expire_after)
        retry_session = retry(cache_session, retries = num_retries, backoff_factor = backoff_factor)
        openmeteo = openmeteo_requests.Client(session = retry_session)
        
        return openmeteo

    def __init__(self, base_url:str, city:str, country:str, start_date:str, end_date:str):
        self.base_url = base_url
        self.latitude, self.longitude = LoadFromApi.get_geo_loc(city, country)
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if self.end_date < self.start_date:
            raise ValueError("End date must be after start date")

        self.start_date_str = self.start_date.strftime("%Y-%m-%d")
        self.end_date_str = self.end_date.strftime("%Y-%m-%d")


    def get_openmeteo_client(self, **kwargs):
        params = {'latitude':self.latitude, 
                  'longitude':self.longitude, 
                  'start_date':self.start_date, 
                  'end_date': self.end_date}
        
        params.update(kwargs)

        try:
            responses = LoadFromApi.openmeteo.weather_api(self.base_url, params=params)
            return responses[0]
        except Exception as e:
            raise


    


# cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
# retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
# openmeteo = openmeteo_requests.Client(session = retry_session)

# url = "https://archive-api.open-meteo.com/v1/archive"
# params = {
# 	"latitude": 52.52,
# 	"longitude": 13.41,
# 	"start_date": "2025-08-13",
# 	"end_date": "2025-08-27",
# 	"daily": ["weather_code", "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "precipitation_sum",\
#             "rain_sum", "snowfall_sum", "precipitation_hours", "cloud_cover_mean", "cloud_cover_max", "cloud_cover_min",\
#             "dew_point_2m_mean", "dew_point_2m_max", "dew_point_2m_min", "wind_speed_10m_mean", "wind_speed_10m_max",\
#             "wind_speed_10m_min", "relative_humidity_2m_mean", "relative_humidity_2m_min", "relative_humidity_2m_max"]
# }
# responses = openmeteo.weather_api(url, params=params)

# response = responses[0]
# print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
# print(f"Elevation: {response.Elevation()} m asl")
# print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
# print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# daily = response.Daily()
# daily_weather_code = daily.Variables(0).ValuesAsNumpy()
# daily_temperature_2m_mean = daily.Variables(1).ValuesAsNumpy()
# daily_temperature_2m_max = daily.Variables(2).ValuesAsNumpy()
# daily_temperature_2m_min = daily.Variables(3).ValuesAsNumpy()
# daily_precipitation_sum = daily.Variables(4).ValuesAsNumpy()
# daily_rain_sum = daily.Variables(5).ValuesAsNumpy()
# daily_snowfall_sum = daily.Variables(6).ValuesAsNumpy()
# daily_precipitation_hours = daily.Variables(7).ValuesAsNumpy()
# daily_cloud_cover_mean = daily.Variables(8).ValuesAsNumpy()
# daily_cloud_cover_max = daily.Variables(9).ValuesAsNumpy()
# daily_cloud_cover_min = daily.Variables(10).ValuesAsNumpy()
# daily_dew_point_2m_mean = daily.Variables(11).ValuesAsNumpy()
# daily_dew_point_2m_max = daily.Variables(12).ValuesAsNumpy()
# daily_dew_point_2m_min = daily.Variables(13).ValuesAsNumpy()
# daily_wind_speed_10m_mean = daily.Variables(14).ValuesAsNumpy()
# daily_wind_speed_10m_max = daily.Variables(15).ValuesAsNumpy()
# daily_wind_speed_10m_min = daily.Variables(16).ValuesAsNumpy()
# daily_relative_humidity_2m_mean = daily.Variables(17).ValuesAsNumpy()
# daily_relative_humidity_2m_min = daily.Variables(18).ValuesAsNumpy()
# daily_relative_humidity_2m_max = daily.Variables(19).ValuesAsNumpy()

# daily_data = {"date": pd.date_range(
# 	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
# 	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
# 	freq = pd.Timedelta(seconds = daily.Interval()),
# 	inclusive = "left"
# )}

# daily_data["weather_code"] = daily_weather_code
# daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
# daily_data["temperature_2m_max"] = daily_temperature_2m_max
# daily_data["temperature_2m_min"] = daily_temperature_2m_min
# daily_data["precipitation_sum"] = daily_precipitation_sum
# daily_data["rain_sum"] = daily_rain_sum
# daily_data["snowfall_sum"] = daily_snowfall_sum
# daily_data["precipitation_hours"] = daily_precipitation_hours
# daily_data["cloud_cover_mean"] = daily_cloud_cover_mean
# daily_data["cloud_cover_max"] = daily_cloud_cover_max
# daily_data["cloud_cover_min"] = daily_cloud_cover_min
# daily_data["dew_point_2m_mean"] = daily_dew_point_2m_mean
# daily_data["dew_point_2m_max"] = daily_dew_point_2m_max
# daily_data["dew_point_2m_min"] = daily_dew_point_2m_min
# daily_data["wind_speed_10m_mean"] = daily_wind_speed_10m_mean
# daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
# daily_data["wind_speed_10m_min"] = daily_wind_speed_10m_min
# daily_data["relative_humidity_2m_mean"] = daily_relative_humidity_2m_mean
# daily_data["relative_humidity_2m_min"] = daily_relative_humidity_2m_min
# daily_data["relative_humidity_2m_max"] = daily_relative_humidity_2m_max

# daily_dataframe = pd.DataFrame(data = daily_data)
# print("\nDaily data\n", daily_dataframe)