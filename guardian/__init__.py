from threading import Thread, Timer
import os
import cv2
import time

from guardian.utils import parse_info
from guardian.db_register import ask_info
from guardian.api_handler import Guardian_Handler
from config import *

current_milli_time = lambda: int(round(time.time() * 1000))

__all__ = ['Camera']

if not 'CLASIFIER' in locals():
    FACE_CLASIFIER = 'haarcascade_frontalface_default.xml'

class Camera():
    faceCascade = cv2.CascadeClassifier(os.path.join(STATIC_DIR,FACE_CLASIFIER))
    unique_instance = None

    def __init__(self, source = '0',treshold=1200):
        """
        :param string source: source of image
        :param float treshold: time in ms to wait API call
        """
        if self.unique_instance != None:
            return self.unique_instance
        self.cap = cv2.VideoCapture(self.analize_input_source(source))
        self.treshold = treshold
        self.handler_lock = Guardian_Handler.lock
        self.__set_variables()
        self.nextFrameSlot()
        self.unique_instance = self

    @staticmethod
    def analize_input_source(input):
        if isinstance(input,str):
            if input.isnumeric:
                return int(input)
            else:
                return input
        else:
            raise TypeError('Write the input as string')

    def __set_variables(self):
        self.video_frame = bytes()
        self.raw_image = bytes()
        self.faces = int()
        self.calling = bool()
        self.api_state = type('state',tuple() , {'value': int()})
        self.data = str()
        self.last_handle = int()
        self.last_call = int()

    def discurrence(self):
        return current_milli_time() - self.last_call

    def concurrence(self):
        return  current_milli_time() - self.last_handle

    def nextFrameSlot(self):
        if self.api_state.value != 0:
            self.calling = False
        _, frame = self.cap.read()
        gray = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        if len(faces) > 0:
            print('You have {} faces in the image'.format(len(faces)))
            frame = self.compute_frame(faces,frame)
        elif not self.calling:
            self.faces = 0
            self.last_handle = current_milli_time()
            if self.discurrence() > self.treshold:
                self.current = "No face found: waiting..."
            else:
                self.current = "No face found: preparig API call in {}".format(
                    self.treshold - self.discurrence())
        self.video_frame = cv2.imencode('.jpg', frame)[1].tobytes()
        return self.video_frame

    def compute_frame(self, targets, frame):
        if self.faces != len(targets) and not self.calling:
            self.last_handle = current_milli_time()
        else:
            if self.concurrence() >= self.treshold:
                self.raw_image = cv2.imencode('.bmp', frame)[1].tostring()
                th = Guardian_Handler(self.raw_image)
                self.api_state = th.state_object
                th.start()
                self.calling = True
                self.last_call = current_milli_time()
            elif self.concurrence() < self.concurrence():
                self.current = "Face found: preparing release data in {}".format(
                    self.treshold - self.concurrence())
            self.last_call = current_milli_time()
        self.faces = len(targets)
        for (x, y, w, h) in targets:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return frame

    def get_frame(self):
        ret, frame = self.cap.read()
        return cv2.imencode('.jpg', frame)[1].tobytes()

    def start(self):
        if DEBUG:
            print('starting Timer...')
        self.timer = Timer(1, function=self.nextFrameSlot)
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def release(self):
        self.cap.release()

    def __iter__(self):
        last = current_milli_time()
        frame_rate_millis =  (1/60)*1000
        while True:
            if current_milli_time()- last >= frame_rate_millis:
                yield self.nextFrameSlot()
                last = current_milli_time()

    def __next__(self):
        frame = self.__iter__()
        return next(frame)

    def __repr__(self):
        string = str()
        string += self.current
        string += "\n"
        string += self.data
        return string

    def __str__(self):
        return self.current

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


