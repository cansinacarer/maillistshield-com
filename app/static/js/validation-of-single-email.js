const validationForm = document.querySelector("#validationForm");
const validationInput = document.querySelector("#emailToValidate");
const validationButton = document.querySelector("#validationButton");

// Add event listener for form submit
validationForm.addEventListener("submit", (event) => {
	// Prevent the default form submission
	event.preventDefault();

	// Start the loading states
	startButtonLoadingState(validationButton);
	startTableLoadingState();
	startAPIResponseBoxLoadingState();

	// Scroll down to the demo-results section
	document.querySelector("#demo-results").scrollIntoView({
		behavior: "smooth",
	});

	// Send the email to the backend
	requestValidation(validationInput.value)
		.then((response) => {
			if (response.status === 429) {
				// Show the rate limit error message
				showAlert(
					"Error",
					`You have reached the usage limit for guest users. <br /><br /> You can get <b class="text-primary">${freeCredits} free credits</b> by creating an account. <br /><br /> <a href="/login" class="btn btn-outline-primary">Login</a> <a href="/register" class="btn btn-outline-primary">Create an account</a>`,
					"OK",
					"danger"
				);
			} else if (response.status === 402) {
				// Show an error message
				showAlert(
					"Error",
					"Your account does not have sufficient credits for this validation request.<br /><br />Please purchase more credits to continue.",
					"OK",
					"danger"
				);
			} else if (response.status === 403) {
				// Show an error message
				showAlert(
					"Error",
					"Please verify your email address to continue using the service.<br /><br />Check your email for the verification link.",
					"OK",
					"danger"
				);
			} else if (response.status === 500) {
				// Show an error message
				showAlert(
					"Error",
					"There was an error when we tried processing your request.",
					"Try again",
					"danger"
				);
			} else if (response.ok) {
				// Show a success message
				response.json().then((data) => {
					if (data.email) {
						// Update the results table
						document
							.querySelectorAll("#demoResultsTable tr")
							.forEach((tr) => {
								const td = tr.querySelector("td");
								if (data[tr.id]) {
									// If we find a data with the same key as the tr id, we update the td
									td.innerHTML = data[tr.id];
								} else {
									// Otherwise, we set the td to None
									td.innerHTML = "None";
								}
							});

						// Show the API response
						document.querySelector(
							"#demoAPIResponse pre code"
						).innerHTML = JSON.stringify(data, null, 2);

						// Re-highlight the code block
						document
							.querySelector("#demoAPIResponse pre code")
							.removeAttribute("data-highlighted");
						hljs.highlightAll();
					} else {
						showAlert(
							"Success",
							`Request successful:<br /><br />${data.email}`,
							"OK",
							"success"
						);
					}
				});
			} else {
				// Show an error message
				showAlert(
					"Error",
					"There was an error when we tried processing your request.",
					"Try again",
					"danger"
				);
			}
		})
		.catch((error) => {
			// Show an error message in case of network failure
			showAlert(
				"Error",
				"There was an error when we tried processing your request.",
				"Try again",
				"danger"
			);
		})
		.then(() => {
			// End the loading states
			endButtonLoadingState(validationButton);
			endTableLoadingAnimation();
			endAPIResponseBoxLoadingState();
		});
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

const startTableLoadingState = () => {
	// Add placeholders to the table cells
	document.querySelectorAll("#demoResultsTable td").forEach((td) => {
		td.innerHTML = '<span class="placeholder col-12"></span>';
	});

	// Start animating the placeholders
	document
		.querySelector("#demoResultsTable table")
		.classList.add("placeholder-glow");
};

const endTableLoadingAnimation = () => {
	// Stop animating the placeholders
	document
		.querySelector("#demoResultsTable table")
		.classList.remove("placeholder-glow");
};

const startAPIResponseBoxLoadingState = () => {
	// Add placeholder class to the pre tag
	document
		.querySelector("#demoAPIResponse pre")
		.classList.add("placeholder", "col-12");

	// Start animating the placeholders
	document
		.querySelector("#demoAPIResponse")
		.classList.add("placeholder-glow");
};

const endAPIResponseBoxLoadingState = () => {
	// Remove placeholder class to the pre tag
	document
		.querySelector("#demoAPIResponse pre")
		.classList.remove("placeholder", "col-12");

	// Stop animating the placeholders
	document
		.querySelector("#demoAPIResponse")
		.classList.remove("placeholder-glow");
};

const requestValidation = (email) => {
	// Read the CSRF token from the meta tag
	const csrfToken = document
		.querySelector('meta[name="csrf-token"]')
		.getAttribute("content");

	// Prepare the data to be sent
	const postData = new FormData();
	postData.append("email", email);

	// Make a request to the server to validate the email using fetch
	return fetch("/validate", {
		method: "POST",
		headers: {
			"X-CSRFToken": csrfToken,
		},
		body: postData,
	});
};

// TODO:
const populateResultsTable = (data) => {};
