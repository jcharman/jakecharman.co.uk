function update_filter() {
    var project_filter = document.getElementById("filter_category");
    console.log(project_filter.value)
    if (project_filter.value == 'all') {
        window.location.href = '/projects';
    }
    else {
        window.location.href = '/projects/category/' + project_filter.value;
    }
}
