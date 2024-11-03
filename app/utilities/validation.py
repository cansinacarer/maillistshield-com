import requests

from app import app


def request_validation(email):
    # TODO: Implement load balancing
    url = "https://worker1.maillistshield.com/validate"
    data = {
        "email": email,
        "api_key": app.config["MLS_WORKER_API_KEY"],  # Replace with the actual API key
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        # API request was successful
        return response.json()
    else:
        # API request failed
        print(
            f"API request failed with status code with this response: {response.json()}"
        )
