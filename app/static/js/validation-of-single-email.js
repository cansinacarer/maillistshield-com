const validationForm = document.querySelector("#validationForm");
const validationInput = document.querySelector("#emailToValidate");
const validationButton = document.querySelector("#validationButton");

// Add event listener for form submit
validationForm.addEventListener("submit", (event) => {
	// Prevent the default form submission
	event.preventDefault();

	// Start the loading states
	startButtonLoadingState(validationButton, "Validating");
	startTableLoadingState();
	startAPIResponseBoxLoadingState();

	// Push the event to the dataLayer for tracking
	window.dataLayer.push({
		event: "click",
		event_category: "button",
		event_label: "Front Page Validation Button Click"
	});

	// Scroll down to the demo-results section
	document.querySelector("#demo-results").scrollIntoView({
		behavior: "smooth"
	});

	// Send the email to the backend
	requestValidation(validationInput.value)
		.then((response) => {
			if (response.status === 400) {
				// CSRF token expired
				showAlert(
					"Error",
					`Your session has expired.<br /><br />Please refresh the page and try again.`,
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
			} else if (response.status === 429) {
				// Show the rate limit error message
				showAlert(
					"Error",
					`You have reached the usage limit for guest users. <br /><br /> You can get <b class="text-primary">${freeCredits} free credits</b> by creating an account. <br /><br /> <a href="/login" class="btn btn-outline-primary">Login</a> <a href="/register" class="btn btn-outline-primary">Create an account</a>`,
					"OK",
					"danger"
				);
			} else if (response.status === 500) {
				// Show an error message
				showAlert(
					"Error",
					"There was an error when we tried processing your request.",
					"OK",
					"danger"
				);
			} else if (response.ok) {
				// Show a success message
				response.json().then((data) => {
					if (data.email) {
						// Update the results table
						populateResultsTable(data);

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
						// Show an error message
						showAlert(
							"Error",
							"There was an error when we tried processing your request.",
							"Try again",
							"danger"
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
			endButtonLoadingState(validationButton, "Validate");
			endTableLoadingAnimation();
			endAPIResponseBoxLoadingState();
		});
});

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
			"X-CSRFToken": csrfToken
		},
		body: postData
	});
};

// Populate the results table with the data from the API response
const populateResultsTable = (data) => {
	document.querySelectorAll("#demoResultsTable tr").forEach((tr) => {
		const td = tr.querySelector("td");
		if (tr.id === "status") {
			// Status field
			if (data[tr.id] === "valid") {
				// If we find an empty string, we set the td to False
				td.innerHTML =
					'<span class="fw-bold text-success">Valid <i class="bi bi-check-circle-fill"></i></span>';
			} else if (data[tr.id] === "invalid") {
				// If we find an empty string, we set the td to False
				td.innerHTML =
					'<span class="fw-bold text-danger">Invalid <i class="bi bi-x-circle-fill"></i></span>';
			} else if (data[tr.id] === "likely_invalid") {
				// If we find an empty string, we set the td to False
				td.innerHTML =
					'<span class="fw-bold text-danger">Likely Invalid <i class="bi bi-x-circle-fill"></i></span>';
			} else if (data[tr.id] === "disabled") {
				// If we find an empty string, we set the td to False
				td.innerHTML =
					'<span class="fw-bold text-danger">Disabled <i class="bi bi-x-circle-fill"></i></span>';
			} else if (data[tr.id] === "unknown") {
				// If we find an empty string, we set the td to False
				td.innerHTML =
					'<span class="fw-bold text-secondary">Unknown <i class="bi bi-dash-circle-fill"></i></span>';
			}
		} else if (tr.id === "email_provider") {
			// Email provider field
			if (data[tr.id] === "google") {
				// If we find an empty string, we set the td to False
				td.innerHTML =
					'<span class="text-info"><i class="me-2 bi bi-google"></i>Google</span>';
			} else if (data[tr.id] === "microsoft") {
				// If we find an empty string, we set the td to False
				td.innerHTML =
					'<span class="text-info"><i class="me-2 bi bi-microsoft"></i>Microsoft</span>';
			} else if (data[tr.id] === "apple") {
				// If we find an empty string, we set the td to False
				td.innerHTML =
					'<span class="text-info"><i class="me-2 bi bi-apple"></i>Apple</span>';
			}
		} else if (tr.id === "email_security_gateway" && data[tr.id] !== "") {
			// Security gateway field
			td.innerHTML = `<span class="text-capitalize">${
				data[tr.id]
			}</span>`;
		} else if (data[tr.id] === true) {
			// If we find a True value, we set the td to True
			td.innerHTML =
				'<span class="text-success">True <i class="bi bi-check-lg"></i></span>';
		} else if (data[tr.id] === false) {
			// If we find a False value, we set the td to True
			td.innerHTML =
				'<span class="text-danger">False <i class="bi bi-x-lg"></i></span>';
		} else if (data[tr.id] === "") {
			// If we find an empty string, we set the td to n/a
			td.innerHTML = "n/a";
		} else if (data[tr.id]) {
			// Catch-all for other rows of the table
			// If we find a data with the same key as the tr id, we update the td
			td.innerHTML = data[tr.id];
		} else {
			// Otherwise, we set the td to None
			td.innerHTML = "None";
		}
	});
};
