const imageInput = document.getElementById("imageInput");
const uploadBox = document.getElementById("uploadBox");
const previewContainer = document.getElementById("previewContainer");
const previewImage = document.getElementById("previewImage");
const fileName = document.getElementById("fileName");
const analyzeBtn = document.getElementById("analyzeBtn");

const loading = document.getElementById("loading");
const resultCard = document.getElementById("resultCard");

const category = document.getElementById("category");
const confidence = document.getElementById("confidence");
const progress = document.getElementById("progress");
const recommendation = document.getElementById("recommendation");
const tip = document.getElementById("tip");
const resultEmoji = document.getElementById("resultEmoji");

let selectedFile = null;


// When user selects an image
imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) {
        return;
    }

    selectedFile = file;

    fileName.textContent = file.name;

    const reader = new FileReader();

    reader.onload = function (event) {

        previewImage.src = event.target.result;

        uploadBox.style.display = "none";
        previewContainer.style.display = "flex";

        resultCard.style.display = "none";
    };

    reader.readAsDataURL(file);
});


// Analyze image
analyzeBtn.addEventListener("click", async function () {

    if (!selectedFile) {
        alert("Please select an image first.");
        return;
    }

    loading.style.display = "block";
    resultCard.style.display = "none";

    const formData = new FormData();

    formData.append("image", selectedFile);

    try {

        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        loading.style.display = "none";

        if (data.error) {
            alert(data.error);
            return;
        }

        // Show category
        category.textContent = data.category;

        // Show confidence
        confidence.textContent = data.confidence + "%";

        progress.style.width = data.confidence + "%";

        // Recommendation
        recommendation.textContent = data.recommendation;

        // Environmental tip
        tip.textContent = data.tip;


        // Category emoji
        if (data.category === "plastic") {
            resultEmoji.textContent = "🧴";
        }
        else if (data.category === "paper") {
            resultEmoji.textContent = "📄";
        }
        else {
            resultEmoji.textContent = "🌱";
        }

        // Show result
        resultCard.style.display = "block";

        // Scroll to result
        resultCard.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

    }
    catch (error) {

        loading.style.display = "none";

        alert(
            "Something went wrong while analyzing the image."
        );

        console.error(error);
    }

});
