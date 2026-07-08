// This file powers the "Try It" page. It sends content to our own REST API
// (routes/api.py) using the fetch() function, and displays the JSON result.

async function submitText() {
    const text = document.getElementById("textInput").value;
    const resultBox = document.getElementById("textResult");

    if (!text.trim()) {
        resultBox.textContent = "Please type something first.";
        return;
    }

    resultBox.textContent = "Analyzing...";

    try {
        const response = await fetch("/api/moderate/text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text, platform: "try-it-page" }),
        });
        const data = await response.json();
        resultBox.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        resultBox.textContent = "Error: " + err.message;
    }
}

async function submitImage() {
    const fileInput = document.getElementById("imageInput");
    const resultBox = document.getElementById("imageResult");

    if (!fileInput.files.length) {
        resultBox.textContent = "Please choose an image first.";
        return;
    }

    resultBox.textContent = "Analyzing...";

    const formData = new FormData();
    formData.append("image", fileInput.files[0]);
    formData.append("platform", "try-it-page");

    try {
        const response = await fetch("/api/moderate/image", {
            method: "POST",
            body: formData,
        });
        const data = await response.json();
        resultBox.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        resultBox.textContent = "Error: " + err.message;
    }
}
