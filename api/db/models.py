import pickle
import numpy as np

from pydantic import BaseModel

from .database import db


class ImageModel(BaseModel):
    timePost: str = None
    mimeType: str
    data: bytes

    def toDict(self):
        return {'timePost': self.timePost, 'mimeType': self.mimeType, 'data': self.data}


class ImagePathModel(BaseModel):
    timePost: str = None
    mimeType: str
    imagePath: str

    def toDict(self):
        return {'timePost': self.timePost, 'mimeType': self.mimeType, 'imagePath': self.imagePath}


async def saveImageToDB(timePost, pilImages, mimeType='jpg'):
    created_image = []
    for i in range(len(pilImages)):
        imageArray = np.asarray(pilImages[i])
        byteData = pickle.dumps(imageArray)

        imageModel = ImageModel(timePost=timePost,
                                mimeType=mimeType, data=byteData)

        new_image = await db["images"].insert_one(imageModel.toDict())
        c = await db["images"].find_one({"_id": new_image.inserted_id})
        created_image.append(
            {'_id': c['_id'], 'timePost': c['timePost']})

        # # Load image from database
        # from PIL import Image
        # img = Image.fromarray(pickle.loads(c['data']))
        # img.save('./a.png')

    return created_image
