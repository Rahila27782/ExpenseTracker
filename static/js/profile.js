document.addEventListener("DOMContentLoaded", function () {
    console.log("Profile page loaded successfully.");
});

function openProfileImagePicker() {
    document.getElementById("profileImageInput").click();
}

const profileImageInput = document.getElementById("profileImageInput");

if (profileImageInput) {
    profileImageInput.addEventListener("change", function () {
        const file = this.files[0];

        if (!file) {
            return;
        }

        const allowedTypes = [
            "image/png",
            "image/jpg",
            "image/jpeg",
            "image/gif",
            "image/webp"
        ];

        if (!allowedTypes.includes(file.type)) {
            alert("Please select a valid image file.");
            this.value = "";
            return;
        }

        const preview = document.getElementById("profilePreview");

        if (preview) {
            preview.src = URL.createObjectURL(file);
        }

        document.getElementById("profileUploadForm").submit();
    });
}