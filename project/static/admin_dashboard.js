
var file_index = 0;

$(document).ready(function (e) {
    $('#files-input').on('change', function () {
        var form_data = new FormData();
        var ins = document.getElementById('files-input').files[0];
        form_data.append("file", ins);
        console.log(ins.name);
        console.log("idhaarrrr") 
        $.ajax({
            url: 'upload-file', // point to server-side URL
            dataType: 'json', // what to expect back from server
            cache: false,
            contentType: false,
            processData: false,
            data: form_data,
            type: 'post',
            success: function (response) 
            {
                
                var row = Math.floor(file_index/3).toString();
                var col = (file_index%3).toString();
                file_index += 1;
                if (file_index%3 == 1) {
                    var tableString = "<tr>";
                    for (var i=0; i<3; i++){
                        var file_id = row + "_" + i.toString();
                        tableString += "<td id=\'" + file_id +  "\' style=\'visibility: hidden;\'>" +
                                            "<a href=\'/responses?file=" + (file_index-1) + "\'>" + 
                                                "<div class=\'filename\'>" + ins.name + "</div>" +
                                            "</a>" +
                                        "</td>";
                        console.log(tableString)
                    }
                    tableString += "</tr>";
                    $("#files").append(tableString);
                }
                var file_id =  row + "_" + col;
                $("#"+file_id).css("visibility", "");
                

            },
            error: function (response) {
                console.error(response);
            }
        });
    });
});