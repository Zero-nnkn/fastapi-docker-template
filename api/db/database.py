import os
import motor.motor_asyncio

# -------------------- Database variables (MongoDB) --------------------
# MONGODB_USERNAME = os.environ["MONGODB_INITDB_ROOT_USERNAME"]
# MONGODB_PASSWORD = os.environ["MONGODB_INITDB_ROOT_PASSWORD"]
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_NAME = os.environ["MONGO_NAME"]

mongoURI = f"mongodb://db:{MONGO_PORT}/{MONGO_NAME}"

client = motor.motor_asyncio.AsyncIOMotorClient(mongoURI)
db = client.imageDB
