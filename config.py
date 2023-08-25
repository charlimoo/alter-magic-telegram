# config.py

# Importing required libraries
import os
import simplejson as json

# Load workflows from json file
with open('workflows.json') as f:
    workflows = json.load(f)

global srvadd
srvadd = "boundary-simulations-generator-tribune.trycloudflare.com"

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = '6175303837:AAGFLDzfd3gxkoxI8ZhD3BMB7G9Rotye9gY'

# Server path to store images
IMAGE_PATH = 'images'

# Check if the environment variables are set
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN provided")

if not IMAGE_PATH:
    raise ValueError("No IMAGE_PATH provided")

# Check if the image path exists
if not os.path.exists(IMAGE_PATH):
    os.makedirs(IMAGE_PATH)
