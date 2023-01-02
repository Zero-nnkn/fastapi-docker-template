import os

from typing import IO
from fastapi import UploadFile
from tempfile import NamedTemporaryFile
from fastapi.middleware.cors import CORSMiddleware

from db.database import db
from db.models import ImagePathModel

ABSPATH = os.path.abspath(os.path.dirname(__file__))


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = "8080"
SUPPORT_TYPES = ["jpg", "jpeg", "png"]


def setupCORSMiddleware(server):
    origins = [
        f"http://{DEFAULT_HOST}",
        f"http://{DEFAULT_HOST}:{DEFAULT_PORT}",
        "*"
    ]

    allowedOrigins = origins
    # Can specify certain types of HTTP methods to allow (ie: just POST/GET etc.)
    # As well as different credentials like authorization headers/cookies etc.
    # Same applies for HTTP headers.
    server.add_middleware(CORSMiddleware, allow_origins=allowedOrigins,
                          allow_credentials=True,
                          allow_methods=["*"],
                          allow_headers=["*"])
    return


def validFileSize(file: UploadFile, max_size=5_000_000):
    fileSize = 0
    temp: IO = NamedTemporaryFile(delete=True)
    for chunk in file.file:
        fileSize += len(chunk)
        if fileSize > max_size:
            return "too large file, limit is 5MB"
        temp.write(chunk)
    temp.close()
    if(fileSize <= 0):
        return "empty file, try again"
    return True


def validInput(challenge: str, input: UploadFile):
    mimeType = input.content_type.split('/')[-1]
    challenge = challenge.strip()
    validFileMsg = validFileSize(input)

    if validFileMsg is not True:
        return validFileMsg
    if challenge != "cv3":
        return "unsupported request! Please try 'cv3' for segmentation task"
    if mimeType not in SUPPORT_TYPES:
        return f"unsupported image format '{mimeType}'"

    return True


async def savePathToDB(timePost, mimeType, filePath):
    imagePathModel = ImagePathModel(timePost=timePost,
                                    mimeType=mimeType, imagePath=filePath)
    new_image_path = await db["images"].insert_one(imagePathModel.toDict())
    cip = await db["images"].find_one({"_id": new_image_path.inserted_id})
    return cip


async def saveImageToStatic(timePost, pilImages, mimeType='jpg'):
    post_image = []
    for i in range(len(pilImages)):
        generatedName = os.path.join(
            ABSPATH, os.environ["STATIC_PATH"], f"{timePost}_{i}.{mimeType}")

        pilImages[i].save(generatedName)
        c = await savePathToDB(timePost, mimeType, generatedName)
        post_image.append(c)

    return post_image
