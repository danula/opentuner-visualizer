/**
 * Created by kasun on 6/4/15.
 */
var selected_points;

var config_table;
$(document).ready(function () {
    config_table = jQuery('#configuration-table').dynatable().data('dynatable');
});

setInterval(function () {
    $.ajax({
        type: "GET",
        url: '/plot/update/'
    });
}, 5000);

function update_conf_details(obj) {
    console.log(obj.join());
    $.ajax({
        type: "GET",
        url: '/plot/config/' + obj.join(),
        success: function (response) {
            console.log(response);
            update_table_structure(response.columns);
            config_table = jQuery('#configuration-table').dynatable({
                dataset: {
                    records: response.data
                }
            });
        }
    });
}

function update_table_structure(columns) {
    table_html_start = "<table id='configuration-table' class='table table-bordered'><thead>";
    table_html_end = "</thead><tbody></tbody></table>";
    table_html_body = "";

    for (var i = 0; i < columns.length; ++i) {
        table_html_body += "<th>"+columns[i]+"</th>";
    }

    jQuery("#config-table").html(table_html_start+table_html_body+table_html_end);
}