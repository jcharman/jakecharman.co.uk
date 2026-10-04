function update_filter() {
    var section = window.location.pathname.split('/')[1]
    var project_filter = document.getElementById("filter_category");
    console.log(project_filter.value)
    if (project_filter.value == 'all') {
        window.location.href = '/'+section;
    }
    else {
        window.location.href = '/'+section+'/category/' + project_filter.value;
    }
}
