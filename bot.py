import os
import time
import requests
from flask import Flask, jsonify
from threading import Thread

app = Flask(__name__)

bot_token = os.getenv('BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')
retry_interval = 30

def fetch_courses():
    response = requests.get("https://www.real.discount/api-web/all-courses/?store=Udemy&page=1&per_page=10&orderby=undefined&free=0&search=&language=&cat=")
    response.raise_for_status()
    return response.json()

def process_courses():
    last_course = None

    while True:
        try:
            data = fetch_courses()
            current_course = {
                'image': data['results'][0]['image'],
                'name': data['results'][0]['name'],
                'category': data['results'][0]['category'],
                'subcategory': data['results'][0]['subcategory'],
                'url': data['results'][0]['url'],
                'description': data['results'][0]['short_description']
            }

            if current_course != last_course:
                last_course = current_course

            time.sleep(30)

        except Exception as e:
            time.sleep(retry_interval)

@app.route('/')
def index():
    try:
        return jsonify({"status": "Running the script to check for new courses."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def run_scraper():
    process_courses()

def main():
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    scraper_thread = Thread(target=run_scraper)
    scraper_thread.start()

if __name__ == "__main__":
    main()
