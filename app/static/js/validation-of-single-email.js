const validationForm = document.querySelector("#validationForm");
const validationInput = document.querySelector("#emailToValidate");
const validationButton = document.querySelector("#validationButton");

// Add event listener for form submit
validationForm.addEventListener("submit", (event) => {
	// Prevent the default form submission
	event.preventDefault();
	console.log("Form submitted");

	// Start the loading
	startButtonLoadingState(validationButton);

	// Wait for a second to simulate the validation process
	setTimeout(4000);

	// End the loading state
	endButtonLoadingState(validationButton);
});

const startButtonLoadingState = (button) => {
	// Disable the submit button
	button.disabled = true;

	// Display the loading spinner
	button.querySelector(".loading").classList.remove("d-none");

	// Change the text of the button
	button.querySelector(".text").textContent = "Validating";
};

const endButtonLoadingState = (button) => {
	// Disable the submit button
	button.disabled = false;

	// Display the loading spinner
	button.querySelector(".loading").classList.add("d-none");

	// Change the text of the button
	button.querySelector(".text").textContent = "Validate";
};

const requestValidation = (email) => {
	// Make a request to the server to validate the email
	const xhr = new XMLHttpRequest();
	xhr.open("POST", "https://worker1.maillistshield.com/validate");

	const postData = new FormData();
	postData.append("email", email);
	postData.append("api_key", "09n82gcyv4cf30nm9u2ladkrfjv");

	xhr.onreadystatechange = function () {
		if (xhr.readyState === 4) {
			if (xhr.status === 200 || xhr.status === 204) {
				// Show a success message
				showAlert("Success", "Email is valid.", "OK", "success");
			} else {
				// Show an error message
				showAlert(
					"Error",
					"Email is not valid.",
					"Try again",
					"danger"
				);
			}
		}
	};
	xhr.send(postData);
};
