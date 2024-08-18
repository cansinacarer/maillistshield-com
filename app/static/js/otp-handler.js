// Select the input fields for code verification
const inputElements = document.querySelectorAll("input[id^='code']");

// Listen to the paste event and fill the input fields with the pasted data
inputElements.forEach((element) => {
	element.addEventListener("paste", (event) => {
		const pastedData = event.clipboardData.getData("text/plain");

		for (
			let i = 0;
			i < pastedData.length && i < inputElements.length;
			i++
		) {
			inputElements[i].value = pastedData[i];
		}
		inputElements[inputElements.length - 1].focus();
	});
});

// Listen to the input event and move the focus to the next input field
inputElements.forEach((element, index) => {
	element.addEventListener("input", () => {
		if (element.value.length === 1 && index < inputElements.length - 1) {
			inputElements[index + 1].select();
		}
	});
});

// Listen to the keydown event and move the focus to the previous input field
inputElements.forEach((element, index) => {
	element.addEventListener("keydown", (event) => {
		if (event.key === "Backspace" && index > 0) {
			event.preventDefault();
			inputElements[index].value = "";
			inputElements[index - 1].select();
		}
	});
});
