import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from datetime import datetime, date
from geopy.geocoders import Nominatim
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError
from constants.constants import * 


logger = logging.getLogger(__name__)
logging.basicConfig(level = logging.DEBUG)

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
            logger.error('There was an error connecting to the API')
            raise ConnectionError(f"Unable to connect to OpenMeteo API: {e}")


    def __init__(self, base_url:str, city:str, country:str, start_date:str, end_date:str):
        self.base_url = base_url
        self.latitude, self.longitude = LoadFromApi.get_geo_loc(city, country)
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        self.client = self.create_openmeteo_client()
        self.engine = create_engine(DB_CON_STR)
        today = date.today()

        if self.end_date < self.start_date:
            raise ValueError("End date must be after start date")
        elif self.end_date > today or self.start_date > today:
            raise ValueError("dates cannot be in the future")

        self.start_date_str = self.start_date.strftime("%Y-%m-%d")
        self.end_date_str = self.end_date.strftime("%Y-%m-%d")


    def get_openmeteo_client(self, **kwargs):
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
        """Return weather data with defined variables in DataFrame"""

        try:
            response = self.get_openmeteo_client(**kwargs)
        except Exception as e:
            logger.error('There was an error connecting to the API')
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
    
    def table_exists(self, table_name:str, db_connection:Engine=None) -> bool:
        """Checks if the table already exists in the db. 
        Returns the number of rows if it does and None if it does not."""

        if db_connection is None:
            db_connection = self.engine

        query_str = fr"""select count(*) from information_schema.tables where table_name = '{table_name}';"""
        query = text(query_str)

        try:
            with db_connection.begin() as connection:
                results = connection.execute(query).scalar()
            
            if results > 0:
                return True
            else:
                return False
        
        except ConnectionError as e:
            raise ConnectionError(f'Cannot connect to the datbase {e}.')
        

    def table_len(self, table_name:str, db_connection:Engine=None) -> int:
        """Returns the number of rows in table_name"""

        query_str = fr"""select count(*) from {table_name};"""
        query = text(query_str)

        if db_connection is None:
            db_connection = self.engine

        try:
            with db_connection.begin() as connection:
                results = connection.execute(query).scalar()
            return results
        except ConnectionError as e:
            raise ConnectionError(f"Cannot connect to the database with error: {e}.")    


    def check_primary_key(self, table_name:str, db_connection:Engine=None) -> bool: 
        """Check if PRIMARY KEY constraints exist for table_name"""

        query_str = fr"""select count(*) from information_schema.table_constraints where table_name = '{table_name}' and constraint_type = 'PRIMARY KEY';"""
        query = text(query_str)

        if db_connection is None:
            db_connection = self.engine

        try:
            with db_connection.begin() as connection:
                results = connection.execute(query).scalar()

            if results>0:
                return True
            else:
                return False 
        
        except ConnectionError as e:
            raise ConnectionError(f"Cannot connect to the database with error: {e}.")    


    def push_to_db(self, dataframe:pd.DataFrame, db_connection:Engine=None):
        """Push dataframe to a temporary database table"""

        if db_connection is None:
            db_connection = self.engine

        table_name = 'raw_weather_data'
        if self.table_exists(table_name, db_connection):
            table_len = self.table_len(table_name, db_connection)
        else:
            table_len = 0
        
        primary_key = self.check_primary_key(table_name, db_connection)

        dataframe = dataframe.reset_index(drop=True)
        if table_len == 0:
            dataframe['id'] = dataframe.index + 1
        else:
            dataframe['id'] = dataframe.index + 1 + table_len

        try:
            dataframe.to_sql(table_name, db_connection, if_exists="append", index=False)

            if not primary_key:
                query = text(f'alter table "{table_name}" add constraint "{table_name}_pk" primary key (id);')
                with db_connection.connect() as conn:
                    conn.execute(query)
                    conn.commit()

            logger.info(f"Successfully pushed {len(dataframe)} rows to {table_name}.")
            return len(dataframe)

        except Exception as e:
            raise ConnectionError(f"Cannot connect to the database with error {e}.")  
        
