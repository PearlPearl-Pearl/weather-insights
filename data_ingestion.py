import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime
from geopy.geocoders import Nominatim
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(filename='data_load.log', 
                    filemode='w',
                    encoding='utf-8',
                    level = logging.DEBUG)

class LoadFromApi:
    """This class contains functionality to load data from the open-meteo api. For now it only loads daily data"""

    @staticmethod
    def get_geo_loc(city:str, country:str) -> tuple[float, float]:
        """Returns (latitude, longitude) for a specified city"""

        city = city.capitalize()
        country = country.capitalize()
        
        geolocator = Nominatim(user_agent='geoapi')
        location = geolocator.geocode(f'{city}, {country}') if city and country else None
        if not location:
            logger.error(f"Could not geocode empty location: {city}, {country}")
            raise LookupError(f"Could not geocode location: {city}, {country}")
        
        return location.latitude, location.longitude
        
    
    @staticmethod
    def create_openmeteo_client(expire_after:int=-1, num_retries:int=5, backoff_factor:float=0.2) -> openmeteo_requests.Client:
        """Return an OpenMeteo Client with retry and cache"""
        try:
            cache_session = requests_cache.CachedSession('.cache', expire_after = expire_after)
            retry_session = retry(cache_session, retries = num_retries, backoff_factor = backoff_factor)
            openmeteo = openmeteo_requests.Client(session = retry_session)
            logger.info('Successfully connected to API')
            return openmeteo

        except Exception as e:
            logger.error('There was an error connection to the API')
            raise ConnectionError(f"Unable to connect to OpenMeteo API: {e}")


    def __init__(self, base_url:str, city:str, country:str, start_date:str, end_date:str):
        self.base_url = base_url
        self.latitude, self.longitude = LoadFromApi.get_geo_loc(city, country)
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d")
        self.client = self.create_openmeteo_client()

        if self.end_date < self.start_date:
            raise ValueError("End date must be after start date")

        self.start_date_str = self.start_date.strftime("%Y-%m-%d")
        self.end_date_str = self.end_date.strftime("%Y-%m-%d")


    def get_openmeteo_client(self, **kwargs) -> openmeteo_requests.Response:
        """Returns the OpenMeteo Response object"""
        params = {'latitude':self.latitude, 
                  'longitude':self.longitude, 
                  'start_date':self.start_date_str, 
                  'end_date': self.end_date_str}
        
        params.update(kwargs)

        try:
            responses = self.client.weather_api(self.base_url, params=params)
            logger.info('Successfully generated variable information')
            
            return responses[0]
        except Exception as e:
            raise RuntimeError(f"Error fetching data from OpenMeteo: {e}")


    def get_weather_data(self, **kwargs) -> pd.DataFrame:
        try:
            response = self.get_openmeteo_client(**kwargs)
        except Exception as e:
            raise ConnectionError(f"API call failed: {e}")

        daily = response.Daily()
        
        daily_data = {"date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left")}

        for i, key in enumerate(kwargs.get("daily", [])):
            daily_data[key] = daily.Variables(i).ValuesAsNumpy()

        daily_dataframe = pd.DataFrame(data = daily_data)

        logger.info('Successfully generated dataframe')

        return daily_dataframe

