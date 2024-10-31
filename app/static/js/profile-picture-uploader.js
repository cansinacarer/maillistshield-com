// When the user selects a profile picture, upload it to the bucket
(function () {
	document.getElementById("profile_picture").onchange = function () {
		var files = document.getElementById("profile_picture").files;
		var file = files[0];
		if (file) {
			// If the aspect ratio is 1, then request the signed URL
			getAspectRatio(file).then((aspectRatio) => {
				if (aspectRatio === 1) {
					getSignedRequest(file);
				} else {
					showAlert(
						"Error",
						`Please select a square image.\n\nThe image you selected has an aspect ratio of ${aspectRatio.toFixed(
							2
						)}.`
					);
				}
			});
		}
	};
})();

// Build an image object to get the aspect ratio of the image
function getAspectRatio(file) {
	return new Promise((resolve, reject) => {
		const img = new Image();
		img.onload = () => {
			const aspectRatio = img.naturalWidth / img.naturalHeight;
			resolve(aspectRatio);
		};
		img.onerror = reject;
		img.src = URL.createObjectURL(file);
	});
}

// Request 1/3: Get the signed request from the backend
function getSignedRequest(file) {
	var xhr = new XMLHttpRequest();
	xhr.open("GET", "/app/account/upload-profile-pic/?file_type=" + file.type);
	xhr.onreadystatechange = function () {
		if (xhr.readyState === 4) {
			if (xhr.status === 200) {
				var response = JSON.parse(xhr.responseText);
				uploadFile(file, response.data, response.url);
			} else {
				showAlert(
					"Error",
					"We were not able to update your profile picture. If this error persists, please contact us and let us know you received the error code APPU-1."
				).then(() => {
					location.reload();
				});
			}
		}
	};
	xhr.send();
}

// Request 2/3: Upload to the bucket with the signed request
function uploadFile(file, s3Data, url) {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", s3Data.url);

	var postData = new FormData();
	for (key in s3Data.fields) {
		postData.append(key, s3Data.fields[key]);
	}
	postData.append("file", file);

	xhr.onreadystatechange = function () {
		if (xhr.readyState === 4) {
			if (xhr.status === 200 || xhr.status === 204) {
				// Tell the server we uploaded a profile picture
				profilePicUploadedNotice();

				// Optimistically update the UI with the new profile picture
				document
					.querySelectorAll('img[alt="avatar"]')
					.forEach((img) => {
						img.src = url;
					});
			} else {
				showAlert(
					"Error",
					"We were not able to update your profile picture. If this error persists, please contact us and let us know you received the error code APPU-2."
				).then(() => {
					location.reload();
				});
			}
		}
	};
	xhr.send(postData);
}

// Request 3/3: Let the backend know that user uploaded a profile picture
function profilePicUploadedNotice() {
	var xhr = new XMLHttpRequest();
	xhr.open("POST", "/app/account");

	var postData = new FormData();
	postData.append("profile-pic-updated", "yes");

	xhr.onreadystatechange = function () {
		if (xhr.readyState === 4) {
			if (xhr.status === 200 || xhr.status === 204) {
				showAlert("Success", "Profile picture is updated.");
			} else {
				showAlert(
					"Error",
					"We were not able to update your profile picture. If this error persists, please contact us and let us know you received the error code APPU-3."
				).then(() => {
					location.reload();
				});
			}
		}
	};
	xhr.send(postData);
}
