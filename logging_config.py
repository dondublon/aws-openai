from loguru import logger
from dotenv import load_dotenv
from sys import stderr
from os import getenv
load_dotenv()
logger.remove()
fileName = getenv("LOG_FILE_NAME", None)
dist = fileName if fileName else stderr 
logger.add(dist, level=getenv("LOG_LEVEL", "INFO"))
    