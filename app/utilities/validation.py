import requests

from flask import current_app


# Distribute traffic to workers with round robin
def validate_email(email):
    workers = current_app.config["MLS_WORKERS"]
    first_worker_index = current_app.config["NEXT_WORKER"]
    best_result_so_far = {}

    # Until we find a server that doesn't return status = unknown
    for i, _ in enumerate(workers):
        # len(workers) = 3, first_worker_index = 2, i = 0  =>  worker_index = 2
        # len(workers) = 3, first_worker_index = 2, i = 1  =>  worker_index = 2
        worker_index = (i + first_worker_index) % len(workers)
        print(f"We are using worker #{worker_index}, which is {workers[worker_index]}")

        # Increment the next worker global variable
        current_app.config["NEXT_WORKER"] = (worker_index + 1) % len(workers)
        print(f'Next time we will use the worker #{current_app.config["NEXT_WORKER"]}')

        # Request the result from the worker
        new_result = request_validation(email, workers[worker_index])

        # If there wasn't an exception during request_validation
        # If there was, we continue looping
        if new_result:
            # If it has a status key, we know that a response was received
            # If it doesn't, we continue looping
            if "status" in new_result:
                # We can at least call this the best_result_so_far
                best_result_so_far = new_result

                # Report what it returned
                # print(f"{workers[worker_index]} returned the result as {new_result['status']}.")
                # print(new_result)

            # If the result is not unknown, it is good to return
            if new_result.get("status") != "unknown":
                return new_result

    if best_result_so_far:
        return best_result_so_far
    else:
        raise Exception(
            "We could not even get an unknown response from any of the workers."
        )


def request_validation(email, worker):
    data = {
        "email": email,
        "api_key": current_app.config["MLS_WORKER_API_KEY"],
    }

    try:
        response = requests.post(worker, json=data)

        if response.status_code == 200:
            # API request was successful
            return response.json()

        else:
            # API request failed
            print(
                f"API request failed with status code with this response: {response.json()}"
            )

    except Exception as e:
        print(f"Error occurred when contacting the worker.")
