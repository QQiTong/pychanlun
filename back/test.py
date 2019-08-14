import numpy as np
import pydash
from datetime import datetime

time_array = ['11' for i in range(3)]

time_array[-1]=str(datetime.now())
# print(len(time_array))
for i in range(len(time_array)):
    print(time_array[i])

