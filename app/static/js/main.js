// Launch tooltips
const tooltipTriggerList = document.querySelectorAll(
	'[data-bs-toggle="tooltip"]'
);
const tooltipList = [...tooltipTriggerList].map(
	(tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl)
);

const startButtonLoadingState = (button, loadingText) => {
	// Disable the submit button
	button.disabled = true;

	// Display the loading spinner
	button.querySelector(".loading").classList.remove("d-none");

	// Change the text of the button
	button.querySelector(".text").textContent = loadingText;
};

const endButtonLoadingState = (button, loadedText) => {
	// Disable the submit button
	button.disabled = false;

	// Display the loading spinner
	button.querySelector(".loading").classList.add("d-none");

	// Change the text of the button
	button.querySelector(".text").textContent = loadedText;
};
