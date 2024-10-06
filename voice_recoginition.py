import azure.cognitiveservices.speech as speechsdk
import os
import speech_recognition as sr
import platform
from dotenv import load_dotenv
import tempfile
import time
from bluos_api import *

load_dotenv()
azure_speech_key = os.getenv("AZURE_SPEECH_KEY")
azure_region = os.getenv("AZURE_REGION")

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
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("Listening timeout. Please speak more quickly.")
            return ''
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio.get_wav_data())
        temp_audio_path = temp_audio.name

    try:
        speech_config = speechsdk.SpeechConfig(subscription=azure_speech_key, region=azure_region)
        audio_input = speechsdk.audio.AudioConfig(filename=temp_audio_path)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
        result = speech_recognizer.recognize_once()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            command = result.text
            speak(f"You said: {command}")
            if any(keyword in command.lower() for keyword in ["turn off", "shut up"]):
                speak("Turning off. Goodbye!")
                exit(0)
            return command.lower()
        elif result.reason == speechsdk.ResultReason.NoMatch:
            speak("Sorry, I did not understand that.")
            return ''
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Speech recognition canceled: {cancellation_details.reason}")
            return ''
    except Exception as e:
        print(f"Could not request results; {e}")
        return ''
    finally:
        # Clean up temporary file
        time.sleep(0.5)
        try:
            os.remove(temp_audio_path)
        except PermissionError:
            print(f"Could not delete temporary file: {temp_audio_path}")
    
def execute_bluos_command(command, device_ip):
    """
    Execute the command on BluOS Device.

    Args:
        commands (str): The command to execute.
        device_ip (str): The IP address of the BluOS device.
    """
    command_mapping = {
        "play": lambda: play(device_ip),
        "play music": lambda: play(device_ip),
        "pause": lambda: pause(device_ip),
        "pause music": lambda: pause(device_ip),
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
    Use Azure's Speech API to generate speech from text and play it.
    
    Args:
        text (str): The text to speak.
    """
    try:
        speech_config = speechsdk.SpeechConfig(subscription=azure_speech_key, region=azure_region)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        result = speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Speech synthesized for text: {text}")
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
    except Exception as e:
        print(f"Error generating speech: {e}")

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