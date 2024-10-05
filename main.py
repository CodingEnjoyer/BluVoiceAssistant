from bluos_api import *
from voice_recoginition import *

DEVICE_IP = '192.168.68.50'

def main():
    while True:
        try:
            # Wait for the wake word before getting the actual command
            if wait_for_wake_word():
                # Get the voice command from the user
                voice_command = get_voice_command()
                
                # If we have a valid command, execute it
                if voice_command:
                    speak(f"Executing command: {voice_command}")
                    execute_bluos_command(voice_command, DEVICE_IP)

        except BluOSAPIError as e:
            speak(f"An error occurred: {e}")
            
        except KeyboardInterrupt:
            speak("Stopping voice assistant...")
            break

if __name__ == '__main__':
    main()