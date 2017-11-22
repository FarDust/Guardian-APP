import sys

from threading import Thread

from PyQt5.QtMultimedia import QSound


from PyQt5 import QtGui

from PyQt5.QtCore import QTimer, QThread, Qt
from PyQt5.QtGui import QPixmap, QImage, QPainter, QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QLayout, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, \
    QPushButton, QTextEdit

from config import *
from guardian.db_register import ask_info, add_security_lvl, ask_log

import cv2
import json

with open(os.path.join(BASE_DIR, 'static', 'url.secret'), "r") as file:
    base = file.readline().strip()

BASE_URL = base.format(
    **{"user": "admin", "password": "V3Y1dWdncmZCeFdBWXNhRg=="})


def photo_id():
    i = 0
    while True:
        yield i
        i += 1


def read_styles(path: str, window):
    try:
        with open(path) as styles:
            window.setStyleSheet(styles.read())
    except FileNotFoundError as err:
        print(err)
        print("Error al leer {} , procediendo a usar estilos por defecto".format(path))


def parse_text(text):
    result = dict()
    try:
        result.update(json.loads(text))
    except json.JSONDecodeError:
        text = text.strip(" ")
        for line in text.split("\n"):
            if ":" in line and len(line.split(":")) == 2:
                result[line.split(":")[0]] = line.split(":")[1]
    return result


def parse_info(info):
    if isinstance(info, dict):
        string = str()
        for key in info.keys():
            if isinstance(info[key], dict):
                data = ["   " + i +
                        "\n" for i in parse_info(info[key]).split("\n")]
                string += "{key} = \n{data}\n".format(**
                                                      {"key": key, "data": data})
            else:
                string += "{key} = {data}\n".format(**
                                                    {"key": key, "data": info[key]})
        return string
    else:
        raise TypeError


class Main(QWidget):
    def __init__(self):
        super().__init__()
        read_styles(os.path.join(BASE_DIR, 'demo',
                                 'styles', 'master.css'), self)
        self.setWindowTitle("Guardian")
        self.setWindowIcon(QIcon('favicon.png'))
        self.setObjectName("body")
        self.main = QFormLayout(self)
        self.layout = QHBoxLayout(self)
        self.camera = VideoCapture(self)
        vertical = QFormLayout(self)
        self.info_label = QLabel(self.camera.current, self)
        self.info_label.setFixedWidth(255)
        self.responce_label = QLabel("No Info", self)
        self.responce_label.setObjectName("response")
        self.responce_label.setMinimumHeight(300)
        self.responce_label.setAlignment(Qt.AlignTop)
        vertical.setFormAlignment(Qt.AlignCenter)
        vertical.addRow(self.info_label)
        vertical.addRow(self.responce_label)
        self.layout.addLayout(vertical)
        add_form = QFormLayout(self)
        button = QPushButton("Add user")
        button.clicked.connect(self.add_user)
        button.setObjectName("Send")
        self.security = QComboBox(self)
        self.security.addItems(SECURITY)
        self.security.setObjectName("security")
        self.form = QTextEdit()
        add_form.setFormAlignment(Qt.AlignCenter)
        add_form.addRow(QLabel("Security: "), self.security)
        add_form.addRow(self.form)
        add_form.addRow(button)
        self.layout.addLayout(add_form)
        self.log = QLabel("", self)
        self.log.setObjectName("log")
        self.log.setMaximumHeight(600)
        log_tittle = QLabel("Log:", self)
        log_tittle.setFixedWidth(50)
        log_tittle.setObjectName("Tittle")
        log_layout = QFormLayout(self)
        log_layout.addRow(log_tittle)
        log_layout.addRow(self.log)
        log_layout.setFormAlignment(Qt.AlignCenter)
        self.main.addRow(self.layout)
        self.main.addRow(log_layout)
        self.show_log()
        # self.layout.addLayout(log_layout)
        self.camera.start()
        self.ask = QTimer()
        self.ask.timeout.connect(self.asking_info)
        self.ask.start(1000.0 / 30)
        self.logging = QTimer()
        self.logging.timeout.connect(self.show_log)
        self.logging.start(5000)
        # self.showFullScreen()

    def show_log(self):
        log = list(ask_log().sort("timestamp", -1))[:7]
        res = [(i.update({"name": i.pop("nombre")})
                if "nombre" in i.keys() else None) for i in log]
        self.log.setText("\n".join([parse_info(i) for i in log]))

    def asking_info(self):
        self.info_label.setText(self.camera.current)
        if self.camera.current == "Face detected":
            self.responce_label.setText(self.camera.data)
            self.show_log()
        elif self.camera.discurrence > 12:
            self.responce_label.setText("No Data")

    def add_user(self):
        new = Thread(target=add_security_lvl, args=(self.camera.raw_image,
                                                    self.security.currentText(), parse_text(self.form.toPlainText())))
        new.start()


class VideoCapture(QWidget):
    faceCascade = cv2.CascadeClassifier(os.path.join(
        BASE_DIR, 'static', 'haarcascade_frontalface_default.xml'))

    def __init__(self, parent=None):
        super(QWidget, self).__init__()
        read_styles(os.path.join(BASE_DIR, 'demo',
                                 'styles', 'master.css'), self)
        self.cap = cv2.VideoCapture(0)
        self.video_frame = QLabel()
        self.video_frame.setObjectName("camera")
        self.setObjectName("camera-container")
        self.faces = 0
        self.raw_image = b''
        self.current = "current"
        self.data = ""
        self._concurrence = 0
        self.discurrence = 0
        self.calling = False
        parent.layout.addWidget(self.video_frame)

    def minion(self, bits):
        self.current = "Face found: calling API..."
        self.calling = True
        responce = ask_info(bits)
        if not "error" in responce:
            self.current = "Face detected"
            self.data = parse_info(responce)
            if responce["security_lvl"] == 'allowed':
                self.sound = QSound('test.wav')
                self.sound.play()
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

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = QImage(frame, frame.shape[1],
                     frame.shape[0], QtGui.QImage.Format_RGB888)
        pix = QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)

    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000.0 / 30)

    def pause(self):
        self.timer.stop()

    def deleteLater(self):
        self.cap.release()
        super(QWidget, self).deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
