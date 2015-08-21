/**
 * Created by madawa on 8/20/15.
 */
function uploadFiles() {
    var formData = new FormData();
    formData.append('database', $('#database').prop('files')[0]);
    formData.append('manipulator', $('#manipulator').prop('files')[0]);
    formData.append('csrfmiddlewaretoken', csrftoken);

    $.ajax({
        type: 'POST',
        processData: false,
        contentType: false,
        url: '/upload/upload_files/',
        data: formData,
        success: function(data, textStatus, jqXHR) {
            alert("Success");
        },
        error: function(jqXHR, textStatus, errorThrown) {
            alert("error");
        }
    });
}