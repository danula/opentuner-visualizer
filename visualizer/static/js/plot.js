/**
 * Created by kasun on 6/4/15.
 */
var enable_comparison;
var select_first_set;
var first_set;
var second_set;
var comparisonControls = $("#comparison-controls");
var config_table;
var token_field;
var clicked_flag;

$(document).ready(function () {
    config_table = jQuery('#configuration-table').dynatable();
    $.fn.bootstrapSwitch.defaults.size = 'normal';
    $("#enable-comparison").bootstrapSwitch();
    enableComparison();
    token_field = $('#tokenfield');

    $.ajax({
        type: "GET",
        url: '/plot/get_flags/',
        success: function (response) {
            token_field.tokenfield({
                autocomplete: {
                    source: response,
                    delay: 200
                },
                showAutocompleteOnFocus: false
            });
        }
    });

    $('.slider-input').jRange({
    from: 0,
    to: 100,
    step: 1,
    scale: [0,100],
    format: '%s',
    width: 300,
    showLabels: true,
    isRange : true
    });

});

setInterval(function () {
    $.ajax({
        type: "GET",
        url: '/plot/update/'
    });
}, 50000);

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
                }).on('click', 'tr', function () {
                    var flag = $(this).children(":first").text();
                    token_field.tokenfield('createToken', {value: flag, label: flag, status: 1});
                });
            } else {
                if (select_first_set) {
                    first_set = obj;
                    //for (var i = 0; i < first_set.length; i++) {
                    //    first_set[i].first = first_set[i].value;
                    //    delete first_set[i].value;
                    //}
                } else {
                    second_set = obj;
                    //for (var i = 0; i < second_set.length; i++) {
                    //    second_set[i].second = second_set[i].value;
                    //    delete second_set[i].value;
                    //}

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
    console.log(second_set);
    console.log(first_set)
    $.ajax({
        type: "GET",
        url: '/plot/config3/' + first_set + "/" + second_set,
        success: function (response) {
            console.log(response)
            update_table_structure(["Name", "First", "Second"]);
            config_table = jQuery('#configuration-table').dynatable({
                dataset: {
                    records: response.data
                }
            }).on('click', 'tr', function () {
                $.ajax({
                    type: "GET",
                    url: '/plot/highlight_flag/?flag=' + $(this).children(":first").text()
                });
            });
        }
    });

    console.log($(this).children(":first").text());
    first_set = null;
    second_set = null;
    enableComparison();
}

function tokenFieldChange() {
    var selected_flags = token_field.tokenfield('getTokens');
    var flag_names = "";
    var flag_status = "";
    $.each(selected_flags, function (index) {
        if (selected_flags[index].status != -1) {
            flag_names = flag_names + selected_flags[index].value + ",";
            flag_status = flag_status + selected_flags[index].status + ",";
        }
    });
    console.log(flag_names);
    console.log(flag_status);
    $.ajax({
        type: "GET",
        url: '/plot/highlight_flag/?flags=' + flag_names.substring(0, flag_names.length - 1) + '&status=' + flag_status.substring(0, flag_status.length - 1)
    });
    update_table2(selected_flags);
}

function update_table2(selected_flags){
    var table_html_start = "<table id='custom-param-table' class='table'>";
    var table_html_end = "</table>";
    var table_html_body = "";
    $.each(selected_flags, function (index) {
        table_html_body += "<tr><td><input type='checkbox' aria-label='...'></td><td>" + selected_flags[index].value + "</td><td><div class='btn-group btn-group-xs' role='group' aria-label='...' style='float: right'>";
        if(selected_flags[index].status==1){
            table_html_body += "<button type='button' class='btn btn-success'>on</button>"+
                            "<button type='button' class='btn btn-default'>off</button></tr>";
        }else if(selected_flags[index].status==0){
            table_html_body += "<button type='button' class='btn btn-default'>on</button>"+
                            "<button type='button' class='btn btn-danger'>off</button></tr>";
        }else{
            table_html_body += "<button type='button' class='btn btn-default'>on</button>"+
                            "<button type='button' class='btn btn-default'>off</button></tr>";
        }
        table_html_body += "</tr>";
    });

    jQuery("#custom-param-list").html(table_html_start + table_html_body + table_html_end);
}

document.addEventListener('DOMContentLoaded', function () {
    token_field.on('tokenfield:createtoken', function (event) {
        var existingTokens = jQuery(this).tokenfield('getTokens');
        $.each(existingTokens, function (index, token) {
            if (token.value === event.attrs.value)
                event.preventDefault();
        });
    });

    token_field.on('tokenfield:createdtoken', function (event) {
        clicked_flag = $(event.relatedTarget);
        clicked_flag.css("background-color", "#85FF85");
        var flag_status = clicked_flag.find("span").text().split("(")[0];
        flag_status = flag_status + " (On)";
        clicked_flag.find("span").text(flag_status);
    });

    token_field.on('tokenfield:edittoken', function (event) {
        event.preventDefault();
        clicked_flag = $(event.relatedTarget);

        //Green to red
        if (clicked_flag.css("background-color") == "rgb(133, 255, 133)") {
            clicked_flag.css("background-color", "rgb(255, 133, 133)");
            var flag_status = clicked_flag.find("span").text().split("(")[0];
            flag_status = flag_status + " (Off)";
            event.attrs.status = 0;
            clicked_flag.find("span").text(flag_status);
        }
        //Red to default
        else if (clicked_flag.css("background-color") == "rgb(255, 133, 133)") {
            clicked_flag.css("background-color", "rgb(237, 237, 237)");
            var flag_status = clicked_flag.find("span").text().split("(")[0];
            flag_status = flag_status + " (Ignore)";
            event.attrs.status = -1;
            clicked_flag.find("span").text(flag_status);
        }
        //Default to green
        else {
            clicked_flag.css("background-color", "rgb(133, 255, 133)");
            var flag_status = clicked_flag.find("span").text().split("(")[0];
            flag_status = flag_status + " (On)";
            event.attrs.status = 1;
            clicked_flag.find("span").text(flag_status);
        }
        tokenFieldChange();
    });
});