(function ($) {
    "use strict";

    // Проверка, что jQuery загружен
    if (!$) {
        console.error("jQuery не загружен");
        return;
    }

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();

    // Sidebar Toggler
    $('.sidebar-toggler').click(function () {
        $('.sidebar, .content').toggleClass("open");
        return false;
    });

    // Progress Bar
    if ($.fn.waypoint) {
        $('.pg-bar').waypoint(function () {
            $('.progress .progress-bar').each(function () {
                $(this).css("width", $(this).attr("aria-valuenow") + '%');
            });
        }, {offset: '80%'});
    } else {
        console.error("Waypoints не загружен");
    }

    // Calender
    if ($.fn.datetimepicker) {
        $('#calender').datetimepicker({
            inline: true, format: 'L'
        });
    } else {
        console.error("datetimepicker не загружен");
    }

    // Проверка, что Chart.js загружен
    if (typeof Chart !== 'undefined') {
        // Worldwide Sales Chart
        var ctx1 = $("#worldwide-sales").get(0).getContext("2d");
        var myChart1 = new Chart(ctx1, {
            type: "bar",
            data: {
                labels: ["2016", "2017", "2018", "2019", "2020", "2021", "2022"],
                datasets: [{
                    label: "USA", data: [15, 30, 55, 65, 60, 80, 95], backgroundColor: "rgba(0, 156, 255, .7)"
                }, {
                    label: "UK", data: [8, 35, 40, 60, 70, 55, 75], backgroundColor: "rgba(0, 156, 255, .5)"
                }, {
                    label: "AU", data: [12, 25, 45, 55, 65, 70, 60], backgroundColor: "rgba(0, 156, 255, .3)"
                }]
            },
            options: {
                responsive: true
            }
        });

        // Sales & Revenue Chart
        var ctx2 = $("#salse-revenue").get(0).getContext("2d");
        var myChart2 = new Chart(ctx2, {
            type: "line",
            data: {
                labels: ["2016", "2017", "2018", "2019", "2020", "2021", "2022"],
                datasets: [{
                    label: "Salse",
                    data: [15, 30, 55, 45, 70, 65, 85],
                    backgroundColor: "rgba(0, 156, 255, .5)",
                    fill: true
                }, {
                    label: "Revenue",
                    data: [99, 135, 170, 130, 190, 180, 270],
                    backgroundColor: "rgba(0, 156, 255, .3)",
                    fill: true
                }]
            },
            options: {
                responsive: true
            }
        });
    } else {
        console.error("Chart.js не загружен");
    }

})(jQuery);
