from BluVoiceAssistant.voice_recoginition import get_intent_from_clu

def test_get_intent_from_clu():
    test_commands = [
        "Can you play some music?",
        "Pause the playback",
        "Set volume to 30",
        "Increase volume by 10",
        "Mute the music",
        "Turn off",
        "Skip to the next song"
    ]

    for command in test_commands:
        print(f"Testing command: {command}")
        response = get_intent_from_clu(command)
        print(f"Intent: {response['intent']}")
        print(f"Entitites: {response['entities']}")
        print("-" * 40)

if __name__ == '__main__':
    test_get_intent_from_clu()