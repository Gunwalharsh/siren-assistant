import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import os
import pyautogui
import smtplib
import requests
import json
import time
from datetime import timedelta
import google.generativeai as genai

# Initialize text-to-speech engine
engine = pyttsx3.init()
# sending_to_gemini = False
voices = engine.getProperty('voices')
engine.setProperty('voice', 'com.apple.speech.synthesis.voice.Daniel')

# Set up the Google Gemini API
genai.configure(api_key="Gemini_API")

# Set up the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

convo = model.start_chat(history=[])

def get_response(user_input):
    convo.send_message(user_input)
    gemini_reply = convo.last.text
    print(gemini_reply)
    return gemini_reply


# Speak function
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

# Wish the user based on the current time
def wish_me():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak('Good Morning Sir!')
    elif hour >= 12 and hour <= 17:
        speak("Good Afternoon Sir!")
    else:
        speak("Good Evening Sir!")

# Listen and recognize speech
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.energy_threshold = 100
        r.adjust_for_ambient_noise(source, duration=0.5)  # Dynamically adjust to noise
        audio = r.listen(source, timeout=5, phrase_time_limit=5)  # Limit time for speaking
    try:
        print("Recognizing...")
        query = r.recognize_google(audio)
        print(f"User said: {query}\n")
    except Exception as e:
        print("Say that again please...")
        return "None"
    return query

# Send an email
def send_email(to, content):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login('your_mail@gmail.com', 'abcd')  # Use secure methods for credentials
        server.sendmail('your_mail@gmail.com', to, content)
        server.close()
        speak("Email has been sent successfully.")
    except Exception as e:
        speak("I am unable to send the email.")
        print(f"Error in send_email: {e}")

# Fetch weather information
def get_weather(city):
    api_key = "Weather_API"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric"
    response = requests.get(complete_url)
    data = response.json()
    if data["cod"] != "404":
        main = data["main"]
        temperature = main["temp"]
        humidity = main["humidity"]
        weather_desc = data["weather"][0]["description"]
        speak(f"The temperature in {city} is {temperature}°C with {weather_desc} and humidity of {humidity}%.")
    else:
        speak("City not found.")

# Play music
def play_music():
    music_dir = "C:\\Users\\GABBAR\\Music"  # Change to your music directory
    songs = os.listdir(music_dir)
    if songs:
        os.startfile(os.path.join(music_dir, songs[0]))
    else:
        speak("No music files found in the directory.")

# Fetch latest news
def get_news():
    api_key = "News_API"
    base_url = "https://newsapi.org/v2/top-headlines?"
    country = "us"
    complete_url = f"{base_url}country={country}&apiKey={api_key}"
    response = requests.get(complete_url)
    news_data = response.json()
    if news_data["status"] == "ok":
        speak("Here are the top 5 news headlines.")
        for i, article in enumerate(news_data["articles"][:5], start=1):
            speak(f"News {i}: {article['title']}")
    else:
        speak("I couldn't fetch the news at this time.")

# Set a reminder
def set_reminder(message, time_in_seconds):
    speak(f"Reminder set for {message} in {time_in_seconds / 60:.0f} minutes.")
    time.sleep(time_in_seconds)
    speak(f"Reminder: {message}")

# Tell a joke
def tell_joke():
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url)
    if response.status_code == 200:
        joke = response.json()
        speak(f"Here's a joke for you: {joke['setup']}")
        time.sleep(2)
        speak(joke['punchline'])
    else:
        speak("I couldn't fetch a joke at the moment.")

# Main function
if __name__ == '__main__':
    wish_me()
    
    print("I am Siren, your personal assistant. How may I help you?")
    speak("I am Siren, your personal assistant. How may I help you?")

    while True:
        query = take_command().lower()

        try:
            # Wikipedia search based on questions
            if 'ok gemini' in query:
                speak('Searching...')
                query = query.replace("ok gemini", "").strip()  # Remove keyword and strip whitespace
                if query:  # Check if there's a valid query
                    results = get_response(query)
                    speak("According to google")
                    print(results)
                    speak(results)
                else:
                    speak("You didn't specify what to search on Wikipedia.")

            # Open common websites
            elif 'open youtube' in query:
                webbrowser.open("youtube.com")
            elif 'open google' in query:
                webbrowser.open("google.com")
            elif 'open spotify' in query:
                webbrowser.open("spotify.com")
            
            # Fetch weather
            elif 'weather in' in query:
                try:
                # Extract the city name from the query
                    city = query.split('in')[-1].strip()  # Extracts everything after 'in'
                    if city:
                        get_weather(city)
                    else:
                        speak("I couldn't understand the city name. Please try again.")
                except Exception as e:
                    speak("An error occurred while fetching the weather.")
                    print(f"Error: {e}")

            # Send email
            elif 'email' in query:
                try:
                    speak("What should I say?")
                    content = take_command()
                    if content != "None":  # Check if the content is valid
                        speak("Who should I send it to?")
                        to = "recipient_email@gmail.com"  # Change to the recipient's email
                        send_email(to, content)
                    else:
                        speak("You didn't specify the email content.")
                except Exception as e:
                    speak("I am unable to send the email.")
                    print(f"Error in email: {e}")

            # Play music
            elif 'play music' in query:
                play_music()

            # Get news
            # elif 'news' in query:
            #     get_news()
            
            # Set reminder
            elif 'remind me' in query:
                speak("What should I remind you about?")
                reminder_message = take_command()
                if reminder_message != "None":  # Check if the message is valid
                    speak("In how many minutes?")
                    minutes = take_command()
                    if minutes.isdigit():  # Ensure the input is a number
                        set_reminder(reminder_message, int(minutes) * 60)
                    else:
                        speak("You didn't specify a valid number of minutes.")
                else:
                    speak("You didn't specify what to remind you about.")
            
            # Tell a joke
            elif 'joke' in query:
                tell_joke()

            # System commands
            elif 'shutdown' in query:
                os.system("shutdown /s /t 1")
            elif 'restart' in query:
                os.system("shutdown /r /t 1")
            
            # Exit the assistant
            elif 'stop listening' in query:
                speak("Goodbye!")
                break

        except Exception as e:
            print(f"An error occurred: {e}")
            speak("I'm sorry, something went wrong. Please try again.")
