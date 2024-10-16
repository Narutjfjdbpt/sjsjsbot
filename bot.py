from flask import Flask, jsonify
import requests
import time
import os

app = Flask(__name__)

bot_token = os.getenv('BOT_TOKEN')
chat_id = os.getenv('CHAT_ID')
retry_interval = 30

def fetch_courses():
    response = requests.get("https://www.real.discount/api-web/all-courses/?store=Udemy&page=1&per_page=10&orderby=undefined&free=0&search=&language=&cat=")
    response.raise_for_status()
    return response.json()

def send_telegram_message(course):
    image = course['image']
    name = course['name']
    category = course['category']
    subcategory = course['subcategory']
    url = course['url']
    description = course['description']
    
    msg = f"<b>📚 {name}\n\n💠 Category : {category} > {subcategory}\n\n🔗 Course Link : <a href='{url}'>Click Here</a>\n\n📝 Description : <i>{description}</i></b>"
    telegram_url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
    
    payload = {
        'chat_id': chat_id,
        'photo': image,
        'caption': msg,
        'parse_mode': 'HTML'
    }
    
    response = requests.post(telegram_url, data=payload)
    
    if response.status_code != 200:
        print(f"Failed to send message: {response.status_code} - {response.text}")
        return False
    
    return True

def process_courses():
    last_course = None

    print("Script is running...")  # Print message when script starts

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
                print("New course found!")
                last_course = current_course
                success = send_telegram_message(current_course)
                
                if not success:
                    print("Error sending the message to Telegram. Retrying...")
                    time.sleep(retry_interval)
                    continue

            time.sleep(30)

        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(retry_interval)

@app.route('/')
def index():
    try:
        print("Running the script to check for courses...")  # Output in console
        return jsonify({"status": "Running the script to check for new courses."})  # Response to the user
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
