import numpy as np
import pydash

biResult = [1,3,4,5]
biResult2 = [6,9,10,11]
test = pydash.map_(biResult,lambda item:item>3)
print(test)
