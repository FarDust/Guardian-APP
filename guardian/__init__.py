from threading import Thread, Timer
import os
import cv2
import time

from guardian.utils import parse_info
from guardian.db_register import ask_info
from config import *


__all__ = ['Camera']

if not 'CLASIFIER' in locals():
    FACE_CLASIFIER = 'haarcascade_frontalface_default.xml'

class Camera():
    faceCascade = cv2.CascadeClassifier(os.path.join(STATIC_DIR,FACE_CLASIFIER))
    unique_instance = None

    def __init__(self, source= 0):
        if self.unique_instance != None:
            return self.unique_instance
        self.cap = cv2.VideoCapture(source)
        self.video_frame = b''
        self.faces = 0
        self.raw_image = b''
        self.current = "current"
        self.data = "No data"
        self._concurrence = 0
        self.discurrence = 0
        self.calling = False
        self.nextFrameSlot()
        self.unique_instance = self

    def minion(self, bits):
        self.current = "Face found: calling API..."
        self.calling = True
        responce = ask_info(bits)
        if not "error" in responce:
            self.current = "Face detected"
            self.data = parse_info(responce)
            if responce["security_lvl"] == 'allowed':
                pass
        else:
            self.current = "Error: {}".format(responce)
        self.calling = False

    def nextFrameSlot(self):
        _, frame = self.cap.read()
        gray = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2GRAY)
        faces = self.faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        if len(faces) > 0:
            if self.faces != len(faces) and not self.calling:
                self.discurrence += 1
                self._concurrence = 0
            else:
                if self._concurrence == 12:
                    self.raw_image = cv2.imencode('.bmp', frame)[1].tostring()
                    th = Thread(target=self.minion, args=(self.raw_image,))
                    th.start()
                    self.discurrence = 0
                elif self._concurrence < 12:
                    self.current = "Face found: preparing release data in {}".format(
                        12 - self._concurrence)
                self._concurrence += 1
                self.discurrence = 0
            self.faces = len(faces)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        elif not self.calling:
            self.discurrence += 1
            self.faces = 0
            self._concurrence = 0
            if self.discurrence > 12:
                self.current = "No face found: waiting..."
            else:
                self.current = "No face found: preparig API call in {}".format(
                    12 - self.discurrence)
        self.video_frame = cv2.imencode('.jpg', frame)[1].tobytes()

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
        last = time.time()
        while True:
            if time.time() - last >= 1/60:
                yield self.video_frame

    def __next__(self):
        frame = self.__iter__()
        while True:
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


