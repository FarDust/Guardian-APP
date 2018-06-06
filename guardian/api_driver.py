import json
import os

from requests import Session, Request
import uuid

_KEY = '<secret>'

_URL = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0'


def comparison(face_id, face_list_id):
    s = Session()

    data = json.dumps({"faceId": face_id, "faceListId": face_list_id})
    headers = {"Content-Type": "application/json",
               "Ocp-Apim-Subscription-Key": _KEY}

    req = Request('POST', _URL + "/findsimilars", data=data, headers=headers)
    prepped = req.prepare()

    resp = s.send(prepped)
    if resp.status_code == 200:
        return resp.json()
    else:
        return resp.json()


def get_face_id(image):
    s = Session()

    headers = {"Content-Type": "application/octet-stream",
               "Ocp-Apim-Subscription-Key": _KEY}

    req = Request('POST', _URL + '/detect', data=image,
                  headers=headers, params={'returnFaceId': True})
    prepped = req.prepare()

    resp = s.send(prepped)
    if resp.status_code == 200:
        return resp.json()
    else:
        return {}


def declare_list(name):
    s = Session()
    identifier = str(uuid.uuid4())

    headers = {"Content-Type": "application/json",
               "Ocp-Apim-Subscription-Key": _KEY}

    req = Request('PUT', _URL + '/facelists/{}'.format(identifier),
                  headers=headers, data=json.dumps({"name": name}))
    prepped = req.prepare()

    resp = s.send(prepped)
    if resp.status_code == 200:
        return identifier
    else:
        return resp.status_code, resp.content


def add_face(list_id, image):
    s = Session()

    headers = {"Content-Type": "application/octet-stream",
               "Ocp-Apim-Subscription-Key": _KEY}

    req = Request('POST', _URL + '/facelists/{faceListId}/persistedFaces'.format(**{"faceListId": list_id}), data=image,
                  headers=headers)
    prepped = req.prepare()

    resp = s.send(prepped)
    if resp.status_code == 200:
        return resp.json()
    else:
        return {}


if __name__ == "__main__":
    if not 'list_id' in os.listdir(os.getcwd()):
        with open(os.path.join(os.getcwd(), 'list_id'), 'w') as file:
            file.write(declare_list("test_face"))
