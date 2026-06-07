import logging
import os


os.makedirs("logs", exist_ok = True)
logger = logging.getLogger("shopping_cart")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)


file_handler = logging.FileHandler("logs/error.log")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)


logger.addHandler(console_handler)
logger.addHandler(file_handler)