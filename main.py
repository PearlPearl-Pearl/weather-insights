from src.data_ingestion import *
from tests.modular_tests import *
import time

start = time.time()
data = test_openmeteo()
print(test_db_push(data, engine))
end = time.time()

print(f'{round(end-start, 2)}s')