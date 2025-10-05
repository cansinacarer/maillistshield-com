// File size formatter
function formatFileSize(fileSize) {
	const units = ["Bytes", "KB", "MB", "GB", "TB"];
	let index = 0;

	while (fileSize >= 1024 && index < units.length - 1) {
		fileSize /= 1024;
		index++;
	}

	return `${fileSize.toFixed(2)} ${units[index]}`;
}

document.addEventListener("DOMContentLoaded", function () {
	// Define the DOM elements
	const dropzoneElement = document.getElementById("dropzone");
	const fileInputElement = document.getElementById("csvFileInput");
	const fileDetailsElement = document.getElementById("fileDetails");
	const columnListElement = document.getElementById("columnList");
	const filePreviewElement = document.getElementById("filePreview");
	const fileNameElement = document.getElementById("fileName");
	const fileValidationCostElement =
		document.getElementById("fileValidationCost");
	const tableHeadersToggleSwitch = document.getElementById(
		"tableHeadersToggleSwitch"
	);
	const uploadButtonElement = document.getElementById(
		"submitFileForValidation"
	);
	const progressContainerElement =
		document.getElementById("progressContainer");
	const progressBarElement = document.getElementById("progressBar");

	// Initialize variables
	let rowCount = 0;
	let localFileName = "";
	let uploadedFileKey = "";
	const maxTableLength = 3;
	//
	let emailColumnName = "";

	// When the dropzone is clicked, trigger a click on the input
	dropzoneElement.addEventListener("click", () => fileInputElement.click());

	// Change the background color when file is hovered over the dropzone
	dropzoneElement.addEventListener("dragover", (e) => {
		e.preventDefault();
		dropzoneElement.classList.add("bg-body-secondary");
	});

	// Remove the background color change when hover file stops
	dropzoneElement.addEventListener("dragleave", () => {
		dropzoneElement.classList.remove("bg-body-secondary");
	});
	dropzoneElement.addEventListener("drop", (e) => {
		e.preventDefault();
		dropzoneElement.classList.remove("bg-body-secondary");
		handleFiles(e.dataTransfer.files);
	});

	// When the file input changes, call handleFiles()
	fileInputElement.addEventListener("change", () => {
		handleFiles(fileInputElement.files);
	});

	function handleFiles(files) {
		// Please only select one file
		if (files.length > 1) {
			showAlert(
				"Invalid file",
				"Please only select 1 file",
				"Back",
				"danger"
			);
			return;
		}

		// If no files are selected, hide the file details section
		if (files.length === 0) {
			fileDetailsElement.classList.add("d-none");
			return;
		}

		// Update selected file name
		const file = files[0];
		localFileName = files[0].name;
		fileNameElement.innerHTML = `<span class="fw-bold text-success"><i class="bi bi-check-circle-fill"></i> Selected file: ${localFileName}</span>`;

		// Read the size of the file, if it is too big, show error
		const fileSize = file.size;
		if (fileSize > 2147483648) {
			showAlert(
				"File error",
				`The file you selected is ${formatFileSize(
					fileSize
				)} but the maximum allowable file size is 2 GB.<br /><br /> Please try again with a smaller file.`,
				"Back",
				"danger"
			);
			return;
		}

		// Only CSV files are supported
		if (file.type !== "text/csv") {
			showAlert(
				"Invalid file",
				"Only CSV files are supported",
				"Back",
				"danger"
			);
			return;
		}

		// If all good, show the file details section
		fileDetailsElement.classList.remove("d-none");

		// Count the number of rows in the file
		const reader = new FileReader();
		reader.onload = (e) => {
			const text = e.target.result;

			// Use Papa Parse to parse the CSV file
			const parsed = Papa.parse(text, {
				header: false,
				skipEmptyLines: true,
				dynamicTyping: false,
				trimHeaders: true
			});

			const rows = parsed.data;
			rowCount = rows.length;
			fileValidationCostElement.innerText =
				rowCount.toLocaleString("en-US");
			const columns = rows[0];

			// Create a table to display the file name, row count, column names, and first 3 rows
			filePreviewElement.innerHTML = "";
			const table = document.createElement("table");
			table.classList.add("table", "table-striped", "table-hover");

			// Create table header
			const thead = document.createElement("thead");
			const headerRow = document.createElement("tr");
			columns.forEach((column) => {
				const td = document.createElement("td");
				td.textContent = column;
				headerRow.appendChild(td);
			});
			thead.appendChild(headerRow);
			table.appendChild(thead);

			// Populate the columnList element with column names
			if (columns.length > 1) {
				columnListElement.parentElement.classList.remove("d-none");
				columnListElement.innerHTML = columns
					.map(
						(column, index) => `
                    <div class="form-check">
                        <input
                            class="form-check-input"
                            type="radio"
                            name="columnWithEmails"
                            id="columnWithEmails${index}"
                            value="${column}"
                            required
                        />
                        <label
                            class="form-check-label"
                            for="columnWithEmails${index}"
                        >
                            ${column}
                        </label>
                    </div>
                `
					)
					.join("");
			} else {
				columnListElement.parentElement.classList.add("d-none");
			}

			// Create table body
			const tbody = document.createElement("tbody");
			for (let i = 1; i <= Math.min(maxTableLength, rowCount - 1); i++) {
				const row = rows[i];
				const tr = document.createElement("tr");
				row.forEach((cell) => {
					const td = document.createElement("td");
					td.textContent = cell;
					tr.appendChild(td);
				});
				tbody.appendChild(tr);
			}
			table.appendChild(tbody);

			// If rowCount > maxTableLength, show a row saying N more rows
			const hiddenRowsCount = document.createElement("p");

			// Append table to filePreviewElement
			filePreviewElement.appendChild(table);

			if (rowCount > maxTableLength) {
				hiddenRowsCount.classList.add("text-center");
				if (rowCount - maxTableLength - 1 === 1) {
					hiddenRowsCount.innerText = `${
						rowCount - maxTableLength - 1
					} more row`;
				} else {
					hiddenRowsCount.innerText = `${
						rowCount - maxTableLength - 1
					} more rows`;
				}
			}
			filePreviewElement.append(hiddenRowsCount);

			// Select the column with the emails
		};
		reader.readAsText(file);
	}

	// Toggle whether the table has headers
	tableHeadersToggleSwitch.addEventListener("change", (event) => {
		const table = filePreviewElement.querySelector("table");
		if (!table) return;

		const thead = table.querySelector("thead");
		if (!thead) return;

		const headerRow = thead.querySelector("tr");
		if (!headerRow) return;

		const headers = headerRow.children;
		for (let i = 0; i < headers.length; i++) {
			const header = headers[i];
			let newElement;
			// If first row is a label
			if (event.target.checked) {
				newElement = document.createElement("th");
				fileValidationCostElement.innerText = rowCount - 1;
			} else {
				newElement = document.createElement("td");
				fileValidationCostElement.innerText = rowCount;
			}
			newElement.textContent = header.textContent;
			headerRow.replaceChild(newElement, header);
		}
	});

	// Upload Step 0: Form submit handler
	uploadButtonElement.addEventListener("click", (event) => {
		// Update the selected column
		try {
			emailColumnName = document.querySelector(
				"input[name=columnWithEmails]:checked"
			).value;
		} catch {
			emailColumnName = "";
		}
		console.log(`emailColumnName: ${emailColumnName}`);

		// Start the loading state
		startButtonLoadingState(uploadButtonElement, "Uploading");

		// Show the progress bar, set it to 0%
		progressContainerElement.classList.remove("d-none");
		progressBarElement.style.width = "0%";

		// This is only informational, checked again in the backend, obviously
		if (user.credits > rowCount) {
			// Trigger the first step of the submission process
			getSignedRequest();
		} else {
			showAlert(
				"Error",
				`You do not have enough credits to validate this file.<br /><br /> We estimate that processing this file will cost ${rowCount.toLocaleString(
					"en-US"
				)} credits but your account only has ${user.credits.toLocaleString(
					"en-US"
				)} credits remaining.<br /><br /> Please purchase more credits to validate this file.`,
				"Back",
				"danger"
			);
			endButtonLoadingState(
				uploadButtonElement,
				"Submit File for Validation"
			);
			progressContainerElement.classList.add("d-none");
		}
	});

	// Upload Step 1: Get the signed request from the backend
	const getSignedRequest = () => {
		let xhr = new XMLHttpRequest();

		xhr.open(
			"GET",
			"/validate-file/getSignedRequest?file=" +
				fileInputElement.files[0].name +
				"&file_type=" +
				fileInputElement.files[0].type
		);

		xhr.onreadystatechange = function () {
			if (xhr.readyState === 4) {
				if (xhr.status === 200) {
					let response = JSON.parse(xhr.responseText);
					uploadFile(fileInputElement.files[0], response.data);
				} else {
					showAlert(
						"Error",
						"We were not able to upload your file. If this error persists, please contact us and let us know you received the error code VUF-1.",
						"Try again",
						"danger"
					);
					endButtonLoadingState(
						uploadButtonElement,
						"Submit File for Validation"
					);
					progressContainerElement.classList.add("d-none");
				}
			}
		};
		xhr.send();
	};

	// Upload Step 2: Upload the file to the bucket with the signed request
	const uploadFile = (file, s3Data) => {
		let xhr = new XMLHttpRequest();
		uploadedFileKey = s3Data.fields["key"];

		xhr.open("POST", s3Data.url);

		// Add the s3Data elements to the post request form data
		let postData = new FormData();
		for (key in s3Data.fields) {
			postData.append(key, s3Data.fields[key]);
		}
		postData.append("file", file);

		// Update the progress bar
		xhr.upload.addEventListener("progress", function (e) {
			if (e.lengthComputable) {
				let percentComplete = Math.round((e.loaded / e.total) * 100);
				progressBarElement.style.width = percentComplete + "%";
				progressBarElement.innerText = percentComplete + "%";
			}
		});

		xhr.onreadystatechange = function () {
			if (xhr.readyState === 4) {
				if (xhr.status === 200 || xhr.status === 204) {
					// Record the job details
					validationFileUploadedNotice();
				} else {
					showAlert(
						"Error",
						"We were not able to upload your file. If this error persists, please contact us and let us know you received the error code VUF-2.",
						"Try again",
						"danger"
					);
					endButtonLoadingState(
						uploadButtonElement,
						"Submit File for Validation"
					);
					progressContainerElement.classList.add("d-none");
				}
			}
		};
		xhr.send(postData);
	};

	// Upload Step 3: Record the job details
	const validationFileUploadedNotice = () => {
		let xhr = new XMLHttpRequest();

		xhr.open(
			"GET",
			"/validate-file/recordBatchFileDetails?file=" +
				uploadedFileKey +
				"&email-column=" +
				emailColumnName +
				"&headers=" +
				tableHeadersToggleSwitch.checked +
				"&original-file-name=" +
				localFileName
		);

		xhr.onreadystatechange = function () {
			if (xhr.readyState === 4) {
				if (xhr.status === 200) {
					let response = JSON.parse(xhr.responseText);
					// Confirm it is all good
					showAlert(
						"Success",
						"Your file has been uploaded successfully.<br />Redirecting to the job list.",
						"OK",
						"success"
					);
					setTimeout(() => {
						window.location.href = "/app";
					}, 5000);
				} else {
					showAlert(
						"Error",
						"We were not able to upload your file. If this error persists, please contact us and let us know you received the error code VUF-3.",
						"Try again",
						"danger"
					);
					endButtonLoadingState(
						uploadButtonElement,
						"Submit File for Validation"
					);
					progressContainerElement.classList.add("d-none");
				}
			}
		};
		xhr.send();
	};
});
