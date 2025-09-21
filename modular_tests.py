from data_ingestion import LoadFromApi, logger
import time

base_url = "https://archive-api.open-meteo.com/v1/archive"
city = 'Accra'
country = 'Ghana'
start_date = '2025-08-18'
end_date = '2025-09-20'


def test_openmeteo(base_url:str, city:str, country:str, start_date:str, end_date:str):
    test_case_1 = LoadFromApi(base_url, city, country, start_date, end_date)

    return test_case_1.get_weather_data(daily = ["weather_code", "temperature_2m_mean", "temperature_2m_max",\
     "temperature_2m_min", "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours", "cloud_cover_mean",\
      "cloud_cover_max", "cloud_cover_min", "dew_point_2m_mean", "dew_point_2m_max", "dew_point_2m_min",\
       "wind_speed_10m_mean", "wind_speed_10m_max", "wind_speed_10m_min", "relative_humidity_2m_mean",\
        "relative_humidity_2m_min", "relative_humidity_2m_max"])

    
start = time.time()
print(test_openmeteo(base_url, city, country, start_date, end_date))
end = time.time()

print(f'{round(end-start, 2)}s')