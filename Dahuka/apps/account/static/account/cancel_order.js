(function () {
    const textArea = document.getElementById('id_cancel_reason');
    const choices = document.querySelectorAll('input[name="cancel_reason_choice"]');
    if (choices.length > 0) {
        choices.forEach(function (choice) {
            choice.addEventListener('change', function () {
                if (textArea) {
                    textArea.value = choice.value;
                }
            });
        });
    }
})();
