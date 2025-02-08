import requests
import os
DEVICE_IP = os.getenv("DEVICE_IP")

def test_bluos_api():
    try:
        # Send GET request to BluOS device
        response = requests.get(f'http://{DEVICE_IP}:11000/Status')
        response.raise_for_status()

        print("Response: ")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"An error occured: {e}")

if __name__ == '__main__':
    test_bluos_api()