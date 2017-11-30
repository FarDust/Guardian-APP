from datetime import datetime, timedelta

import pymongo
from pymongo import MongoClient

try:
    from guardian.api_driver import *
    from config import *
except ModuleNotFoundError:
    from api_driver import *

if __name__ == '__main__':
    DB = 'face-security'
    KEYCOLLECTION = 'persistent'
    SECURITY = ['allowed', 'disallowed', 'wanted']
    SECURITY_LIST = next(open('list_id', 'r'))

conn = MongoClient()
db = conn[DB]
collection = db[KEYCOLLECTION]


def add_security_lvl(img, security_lvl, info=dict()):
    if security_lvl in SECURITY and isinstance(info, dict):
        info.update({"security_lvl": security_lvl})
        if isinstance(img, bytes):
            face = get_face_id(img)
            if isinstance(face, list) and len(face) > 0:
                image = comparison(face[0]['faceId'], SECURITY_LIST)
                if isinstance(image, list) and not len(image) > 0 or 'error' in image:
                    persisted_face_id = add_face(SECURITY_LIST, img)
                    if 'persistedFaceId' in persisted_face_id:
                        path = os.path.join(BASE_DIR, "security_check",
                                            "{}.bmp".format(persisted_face_id['persistedFaceId']))
                        with open(path, 'wb') as file:
                            file.write(img)
                            info.update({'path': path})
                        info.update(
                            {'_id': persisted_face_id['persistedFaceId']})
                    else:
                        raise type('ImageNotAllowed', (Exception,), {})()
                    collection.insert_one(info)
                    return persisted_face_id
                else:
                    if isinstance(image, list):
                        for pic in image:
                            if 'persistedFaceId' in pic:
                                collection.update(
                                    {"_id": pic["persistedFaceId"]}, {"$set": info})
                    return image
            return {"error": "image_not_found"}
        else:
            raise TypeError('"img" must be bytes object')
    else:
        raise type('SecurityFault', (Exception,), {})()


def ask_info(img):
    response = {}
    if isinstance(img, bytes) or True:
        face = get_face_id(img)
        if isinstance(face, list) and len(face) > 0 and 'faceId' in face[0]:
            face = face[0]
            persistedFaceId = comparison(face['faceId'], SECURITY_LIST)
            if isinstance(persistedFaceId, list) and len(persistedFaceId) > 0 and 'persistedFaceId' in \
                    persistedFaceId[0]:
                persistedFaceId = persistedFaceId[0]
                response = collection.find_one(
                    {'_id': persistedFaceId['persistedFaceId']}, {'_id': 0})
                collection.update({'_id': persistedFaceId['persistedFaceId']},
                                  {"$set": {"timestamp": datetime.now().isoformat()}})
                if not response:
                    response = {"error": "No record in database"}
                elif not "path" in response:
                    path = os.path.join(os.getcwd(), "security_check",
                                        "{}.bmp".format(persistedFaceId['persistedFaceId']))
                    with open(path, 'wb') as file:
                        file.write(img)
                        collection.update({'_id': persistedFaceId['persistedFaceId']},
                                          {"$set": {"path": path}})
                if "path" in response:
                    response.pop("path", 0)
                if "nombre" in response:
                    response["name"] = response.pop("nombre")
            else:
                response.update({"security_lvl": 'disallowed'})
            return response
        else:
            return {"error": "face not detected"}
    else:
        raise TypeError('"img" must be bytes object')


def ask_log():
    return collection.find(
        {"timestamp": {"$gte": (datetime.now() - timedelta(days=1)
                                ).isoformat(), "$lt": datetime.now().isoformat()}},
        {"timestamp": 1, "name": 1, "nombre": 1, "_id": 0})


if __name__ == "__main__":
    """
    print(add_security_lvl(open("./0.jpg",
                                'rb').read(), "allowed", {'age': 20}))
    """
    [print(i) for i in ask_log()]
    # print(ask_info(open("./0.jpg", 'rb').read()))
