window.onload = function () {
    var project_filter = document.getElementById("filter_category");
    project_filter.onchange = function () {
        if (project_filter.value == 'all') {
            window.location.href = '/projects';
        }
        else {
            window.location.href = '/projects/category/' + project_filter.value;
        }
    }
}