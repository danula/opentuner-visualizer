/**
 * Created by kasun on 6/4/15.
 */
var enable_comparison;
var select_first_set;
var first_set;
var second_set;
var full_set;

var config_table;
$(document).ready(function () {
    config_table = jQuery('#configuration-table').dynatable().data('dynatable');
    $.fn.bootstrapSwitch.defaults.size = 'normal';
    $("#enable-comparison").bootstrapSwitch();
    enableComparison();
});

setInterval(function () {
    $.ajax({
        type: "GET",
        url: '/plot/update/'
    });
}, 5000);

function update_conf_details(obj) {
    $.ajax({
        type: "GET",
        url: '/plot/config/' + obj.join(),
        success: function (response) {
            if (enable_comparison == false) {
                update_table_structure(response.columns);
                config_table = jQuery('#configuration-table').dynatable({
                    dataset: {
                        records: response.data
                    }
                });
            } else {
                if (select_first_set) {
                    first_set = response.data;
                    for (var i = 0; i < first_set.length; i++) {
                        first_set[i].first = first_set[i].value;
                        delete first_set[i].value;
                    }
                } else {
                    second_set = response.data;
                    for (var i = 0; i < second_set.length; i++) {
                        second_set[i].second = second_set[i].value;
                        delete second_set[i].value;
                    }
                }
            }
        }
    });
}

function update_table_structure(columns) {
    table_html_start = "<table id='configuration-table' class='table table-bordered'><thead>";
    table_html_end = "</thead><tbody></tbody></table>";
    table_html_body = "";

    for (var i = 0; i < columns.length; ++i) {
        table_html_body += "<th>" + columns[i] + "</th>";
    }

    jQuery("#config-table").html(table_html_start + table_html_body + table_html_end);
}

function enableComparison() {
    if ($("#enable-comparison").prop('checked')) {
        enable_comparison = true;
        select_first_set = true;
        $("#comparison-controls").html("Select first set and click next. <br> <input type='button' value='Next' style='padding-right: 20px; padding-left: 20px;' onclick='nextSet()'>");
        $("#comparison-controls").fadeIn();
    }
    else {
        enable_comparison = false;
        select_first_set = false;
        $("#comparison-controls").fadeOut();
    }
}

function nextSet() {
    if (select_first_set && first_set != null) {
        select_first_set = false;
        $("#comparison-controls").fadeOut(function () {
            $("#comparison-controls").html("Select second set and click next. <br> <input type='button' value='Next' style='padding-right: 20px; padding-left: 20px;' onclick='nextSet()'>");
            $("#comparison-controls").fadeIn();
        });
    }
    else if (first_set == null) {
        alert("First set cannot be empty!\nPlease select a region on map to proceed.");
    }
    else if (!select_first_set && second_set == null) {
        alert("Second set cannot be empty!\nPlease select a region on map to proceed.");
    }
    else if (!select_first_set && second_set != null) {
       $("#comparison-controls").fadeOut(function () {
           showComparison();
        });
    }
}

function showComparison() {
    full_set = $.extend(true, first_set, second_set);
    update_table_structure(["Name", "First", "Second"]);
    config_table = jQuery('#configuration-table').dynatable({
        dataset: {
            records: full_set
        }
    });
    first_set = null;
    second_set = null;
    enableComparison();
}