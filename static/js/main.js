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
                labels: ["Январь", "Февраль", "Март", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
                datasets: [
                    {
                        label: "Образец",
                        data: [15, 30, 55, 65, 60, 80, 95, 55, 69, 80, 66, 80],
                        backgroundColor: "rgba(0, 156, 255, 0.7)"
                    },
                    {
                        label: "Экспорт",
                        data: [8, 35, 40, 60, 70, 55, 75, 65, 90, 50, 75, 55],
                        backgroundColor: "rgba(255, 99, 132, 0.7)"
                    },
                    {
                        label: "Услуга",
                        data: [12, 25, 45, 55, 65, 70, 60, 50, 75, 60, 55, 65],
                        backgroundColor: "rgba(54, 162, 235, 0.7)"
                    },
                    {
                        label: "Внутренный рынок",
                        data: [20, 30, 50, 40, 55, 75, 80, 60, 70, 65, 85, 70],
                        backgroundColor: "rgba(75, 192, 192, 0.7)"
                    }
                ]
            },
            options: {
                responsive: true
            }
        });

        // Sales & Revenue Chart
    } else {
        console.error("Chart.js не загружен");
    }

})(jQuery);
