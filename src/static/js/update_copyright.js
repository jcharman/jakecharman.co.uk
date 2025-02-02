window.onload = function () {
    var current_year = new Date().getFullYear();
    var copyright = document.getElementById('cr-year');
    copyright.textContent = current_year;
}