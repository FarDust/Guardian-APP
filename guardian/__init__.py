from threading import Thread, Timer
import cv2
import os


if __name__ != "__main__":
    from guardian.utils import parse_info
    from guardian.db_register import ask_info
    from config import *
else:
    from utils import parse_info
#    from db_register import ask_info
    BASE_DIR = ".."


__all__ = ['Camera']


class Camera():
    faceCascade = cv2.CascadeClassifier(os.path.join(
        BASE_DIR, 'static', 'haarcascade_frontalface_default.xml'))

    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        self.video_frame = b''
        self.faces = 0
        self.raw_image = b''
        self.current = "current"
        self.data = "No data"
        self._concurrence = 0
        self.discurrence = 0
        self.calling = False
        self.started = False
        self.timer = None
        self.nextFrameSlot()

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
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
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
        if DEBUG:
            print("frame...")

    def get_frame(self):
        ret, frame = self.cap.read()
        return cv2.imencode('.jpg', frame)[1].tobytes()

    def start(self):
        if DEBUG:
            print('starting Timer...')
        self.timer = Timer(interval=1.0 / 30, function=self.nextFrameSlot)
        self.timer.daemon = True
        self.timer.start()

    def stop(self):
        self.timer.cancel()

    def release():
        self.cap.release()

    def __iter__(self):
        while True:
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


if __name__ == "__main__":
    with render:
        while True:
            print(next(render))
