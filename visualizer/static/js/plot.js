/**
 * Created by kasun on 6/4/15.
 */
var enable_comparison;
var select_first_set;
var first_set;
var second_set;
var comparisonControls = $("#comparison-controls");
var config_table;

$(document).ready(function () {
    config_table = jQuery('#configuration-table').dynatable();
    $.fn.bootstrapSwitch.defaults.size = 'normal';
    $("#enable-comparison").bootstrapSwitch();
    enableComparison();
});

setInterval(function () {
    $.ajax({
        type: "GET",
        url: '/plot/update/'
    });
}, 500000);

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
                }).on('click', 'tr', function() {
                    $.ajax({
                        type: "GET",
                        url: '/plot/highlight_flag/?flag=' + $(this).children(":first").text()
                    });
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
    var table_html_start = "<table id='configuration-table' class='table table-bordered'><thead>";
    var table_html_end = "</thead><tbody></tbody></table>";
    var table_html_body = "";

    for (var i = 0; i < columns.length; ++i) {
        table_html_body += "<th>" + columns[i] + "</th>";
    }

    jQuery("#config-table").html(table_html_start + table_html_body + table_html_end);
}

function enableComparison() {
    comparisonControls = $("#comparison-controls");
    if ($("#enable-comparison").prop('checked')) {
        enable_comparison = true;
        select_first_set = true;
        comparisonControls.html("Select first set and click next. <br> <input type='button' value='Next' style='padding-right: 20px; padding-left: 20px;' onclick='nextSet()'>");
        comparisonControls.fadeIn();
    }
    else {
        enable_comparison = false;
        select_first_set = false;
        comparisonControls.fadeOut();
    }
}

function nextSet() {
    comparisonControls = $("#comparison-controls");
    if (select_first_set && first_set != null) {
        select_first_set = false;
        comparisonControls.fadeOut(function () {
            comparisonControls.html("Select second set and click next. <br> <input type='button' value='Next' style='padding-right: 20px; padding-left: 20px;' onclick='nextSet()'>");
            comparisonControls.fadeIn();
        });
    }
    else if (first_set == null) {
        alert("First set cannot be empty!\nPlease select a region on map to proceed.");
    }
    else if (!select_first_set && second_set == null) {
        alert("Second set cannot be empty!\nPlease select a region on map to proceed.");
    }
    else if (!select_first_set && second_set != null) {
        comparisonControls.fadeOut(function () {
            showComparison();
        });
    }
}

function showComparison() {
    console.log(second_set)
    for (var i = 0; i < first_set.length; i++) {
        for (var j= 0; j < second_set.length; j++) {
            if(first_set[i].name == second_set[j].name) {
                first_set[i].second = second_set[j].second
            }
        }
    }
    update_table_structure(["Name", "First", "Second"]);
    config_table = jQuery('#configuration-table').dynatable({
        dataset: {
            records: first_set
        }
    }).on('click', 'tr', function() {
        $.ajax({
            type: "GET",
            url: '/plot/highlight_flag/?flag=' + $(this).children(":first").text()
        });
    });
    first_set = null;
    second_set = null;
    enableComparison();
}
