import speech_recognition as sr
import pyttsx3
import logging
import platform
from bluos_api import *

if platform.system() == "Linux":
    engine = pyttsx3.init('espeak')
else:
    engine = pyttsx3.init()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_voice_command():
    """
    Capture a voice command from the user.
    
    Returns:
        str: The recognized command in lowercase.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("Listening timeout. Please speak more quickly.")
            return ''
        
    try:
        command = recognizer.recognize_google(audio)
        logger.info(f"Recognized command: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("Sorry, I did not understand that.")
        logger.warning("Could not understand audio input.")
        return ''
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        logger.error(f"Speech recognition error: {e}")
        return ''
    
def execute_bluos_command(command, device_ip):
    """
    Execute the command on BluOS Device.

    Args:
        commands (str): The command to execute.
        device_ip (str): The IP address of the BluOS device.
    """
    command_mapping = {
        "play": lambda: play(device_ip),
        "pause": lambda: pause(device_ip),
        "stop": lambda: pause(device_ip),
        "volume up": lambda: set_volume(device_ip, level = 10),
        "volume down": lambda: set_volume(device_ip, level = -10),
        "skip": lambda: skip(device_ip),
        "next": lambda: skip(device_ip),
        "back": lambda: back(device_ip),
        "previous": lambda: back(device_ip),
        "shuffle on": lambda: shuffle(device_ip, state = 1),
        "shuffle off": lambda: shuffle(device_ip, state = 0),
        "repeat on": lambda: repeat(device_ip, state = 1),
        "repeat off": lambda: repeat(device_ip, state = 2),
    }

    for key, action in command_mapping.items():
        if key in command:
            action()
            return
        
    print("Command not recognized. Please try again.")
    logger.warning(f"Command not recognized: {command}")


def speak(text):
    """
    Make the assistant speak a given text.
    
    Args:
        text (str): The text to speak.
    """
    engine.say(text)
    engine.runAndWait()

def wait_for_wake_word(wake_word="hello"):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Waiting for wake word...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()
            if wake_word.lower() in command:
                speak("Wake word detected!")
                return True
        except sr.WaitTimeoutError:
            speak("Listening timeout. No wake word detected.")
        except sr.UnknownValueError:
            speak("Could not understand audio input.")
        except sr.RequestError as e:
            speak(f"Could not request results; {e}")
    return False