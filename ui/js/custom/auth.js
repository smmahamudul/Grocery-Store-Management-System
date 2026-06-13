function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

function showAuthMessage(type, message) {
    const box = $("#authMessage");
    if (!box.length) return;
    box.removeClass("error success").addClass(type).text(message);
}

$(function () {
    const error = getQueryParam("error");
    const success = getQueryParam("success");

    if (error) {
        showAuthMessage("error", error);
    } else if (success) {
        showAuthMessage("success", success);
    }

    const confirmPassword = $("#confirm_password");
    if (confirmPassword.length) {
        $("form").on("submit", function (event) {
            const password = $("#password").val().trim();
            const confirm = confirmPassword.val().trim();
            if (password !== confirm) {
                event.preventDefault();
                showAuthMessage("error", "Passwords do not match");
            }
        });
    }
});
