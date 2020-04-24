
$(document).ready(function (e) {
    $('#files-input').on('change', function () {
        var form_data = new FormData();
        var ins = document.getElementById('files-input').files;
        console.log(ins); 
    });
});