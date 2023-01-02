import uvicorn
from src.app_server import getArgs


startArgs = getArgs()


if __name__ == "__main__":
    uvicorn.run("src.app_server:server", host=startArgs.host,
                port=startArgs.port)
