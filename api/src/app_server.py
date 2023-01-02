import argparse

from datetime import datetime
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse

# from db.models import saveImageToDB
from .model_server import ModelServer
from .utils import setupCORSMiddleware, validInput, saveImageToStatic, DEFAULT_HOST, DEFAULT_PORT


# Create the FastAPI application server.
server = FastAPI(title="Custom Mask-RCNN API",
                 description="Segmentation",
                 version="0.0.2")


@server.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Get the original 'detail' list of errors
    details = exc.errors()
    errorDetails = []

    for error in details:
        errorDetails.append(
            {
                "error": error["msg"] + " " + str(error["loc"])
            }
        )
    return JSONResponse(content={"message": errorDetails})


@server.get('/')
def root():
    return RedirectResponse('/home')

@server.get('/home')
def home():
    htmlContent = """
                <body>
                    <h2> Mask-RCNN Segmentation</h2>
                </body>
                """
    return HTMLResponse(htmlContent)

@server.get('/health', status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return JSONResponse(content={'message': 'success'})

@server.post('/segmentation')
async def runSegmentation(challenge: str = Form(min_length=3, max_length=4), input: UploadFile = File()):
    datetime_now = datetime.now()

    # Test input
    validMsg = validInput(challenge, input)
    if validMsg is not True:
        return JSONResponse(content={"message": [{"error": validMsg}]})

    # Segmentation
    try:
        saveImage, predictionsImage = model(
            input.file, 'segmentor')
    except:
        return JSONResponse(content={"message": "segmentation errors. Try another image"})

    # Save
    timePost = datetime_now.strftime("%m%d%y_%H%M%S")
    mimeType = input.content_type.split('/')[-1]
    result = await saveImageToStatic(timePost, saveImage, mimeType)
    # result = await saveImageToDB(timePost, saveImage, mimeType)
    print(result)

    return StreamingResponse(predictionsImage, media_type=input.content_type)


def getArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host", type=str, help="The URL of the application host. Defaults to localhost", default=DEFAULT_HOST)
    parser.add_argument(
        "--port", type=int, help="The host server machine port to run the application on", default=DEFAULT_PORT)
    args = parser.parse_args()
    return args


model = ModelServer()
setupCORSMiddleware(server)
startArgs = getArgs()
