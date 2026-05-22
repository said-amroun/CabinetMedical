document.addEventListener('DOMContentLoaded', function () {
    var input = document.getElementById('appointment_date');
    if (input) {
        var now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        input.min = now.toISOString().slice(0, 16);
    }
});