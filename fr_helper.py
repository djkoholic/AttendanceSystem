import face_recognition as fr
import numpy as np

def recognize():
    pass

def get_face_encodings(image):
    image = fr.load_image_file(image)
    fe = fr.face_encodings(image)
    face_encoding = ""
    for encoding in fe[0]:
        face_encoding = face_encoding + str(encoding) + ','
    return face_encoding

def convert(encoding):
    encoding = encoding.split(',')
    encoding = encoding[:-1]
    codes = []
    for item in encoding:
        codes.append(float(item))
    converted = np.array(codes)
    return np.reshape(converted, (1,128))

def compare(known, unknown):
    known = convert(known)
    unknown = convert(unknown)
    return fr.compare_faces(known, unknown)