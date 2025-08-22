# app/logger.py
import logging

logger = logging.getLogger("bufferzero")
logging.basicConfig(level=logging.INFO)
file_handler = logging.FileHandler("bufferzero.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)