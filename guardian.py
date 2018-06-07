from config import *
from guardian import Camera


render = Camera()

with render as cam:
    while True:
        next(cam)
