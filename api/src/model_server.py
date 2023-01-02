import io
import torch
from .imageHandler.imageHandler import ImageHandler
from .maskRCNN.modelWrapper import MaskRCNNModelWrapper
from .maskRCNN.config.modelDefaults import getModelYamlConfig


class ModelServer(object):
    def __init__(self):
        self.detectorConfig = self.getModelConfigurations()
        self.detectorWrapper = self.initializeDetectorWrapper(
            self.detectorConfig)
        self.imageHandlerWrapper = self.initializeImageHandlerWrapper(
            self.detectorConfig)
        print('Segmentation model ready for serving!')

    def __call__(self, imageFileObject, predictorType, imageExtension="png"):
        uploadedImage = self.imageHandlerWrapper(
            dynamicImagePath=imageFileObject)
        predictionData = self.detectorWrapper(
            uploadedImage, self.detectorConfig.detectorModel.confidenceThreshold, predictorType)

        # Remove background
        originalImages, nobackgroundImages = self.removeBackgroundOnImages(
            uploadedImage, predictionData)

        originalImages = self.imageHandlerWrapper.transformTorchImageToPIL(
            originalImages)
        nobackgroundImages = self.imageHandlerWrapper.transformTorchImageToPIL(
            nobackgroundImages)

        return originalImages, self.serializeImageToResponseByteString(nobackgroundImages, imageExtension)

    def removeBackgroundOnImages(self, imageList: torch.tensor, predictionData):
        originalImages = []
        paintedImages = []
        for imageIndex, currImage in enumerate(imageList):
            originalImages.append(currImage)

            imagePredictions = predictionData[imageIndex]
            currImage = self.removeBackground(
                imagePredictions[0], imagePredictions[1], currImage)

            paintedImages.append(currImage)
        return originalImages, paintedImages

    def removeBackground(self, objectMasks, objectClasses, currImage, threshold=0.3):
        if len(objectClasses) <= 0:
            return currImage
        mergeMask = torch.zeros(torch.squeeze(
            objectMasks[0, :, :, :]).size())
        for currMaskIndex in range(objectMasks.size()[0]):
            temp = torch.squeeze(
                objectMasks[currMaskIndex, :, :, :]) > threshold
            mergeMask += temp
        mergeMask[mergeMask > 0] = 1
        resultImage = mergeMask * currImage + (1 - mergeMask)
        # Add alpha channel
        resultImage = torch.cat(
            (resultImage, torch.unsqueeze(mergeMask, dim=0)), dim=0)
        return resultImage

    def serializeImageToResponseByteString(self, uploadedImage, extension):
        # io.BytesIO() can be used to stream any non-text
        # data. The input data to BytesIO must be a byte-string.
        imageBuffer = io.BytesIO()
        uploadedImage[0].save(imageBuffer, format=extension)
        # Apparently seek(0) is needed if you are using PIL/Skimage.
        # https://stackoverflow.com/questions/55873174/how-do-i-return-an-image-in-fastapi/55905051#55905051
        imageBuffer.seek(0)
        return imageBuffer

    def getModelConfigurations(self):
        detectorConfig = getModelYamlConfig()
        return detectorConfig

    def initializeDetectorWrapper(self, detectorConfig):
        return MaskRCNNModelWrapper(
            pretrained=detectorConfig.detectorModel.pretrained,
            minSize=detectorConfig.detectorModel.minSize,
            classesPath=detectorConfig.detectorModel.predictionClassesPath)

    def initializeImageHandlerWrapper(self, detectorConfig):
        return ImageHandler(
            staticPredictions=detectorConfig.detectorModel.staticPredictions)
