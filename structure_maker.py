import os
from random import random
import string
import random

N = 8

def StructureMaker():
    directory = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
    os.system('mkdir ' + directory)
    os.system('mkdir ' + directory + '/Chunk')
    os.system('mkdir ' + directory + '/result')
    return directory