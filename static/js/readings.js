var startDate = '', endDate = '', searchText = '';
var currentPage = 1, totalPages = 0, rowsInPage = 10, totalRows = 0, pageButtonWindow = 5, offSet = 0;

function SetPaginationButtons(count) {
    $('#rowCount').html('Showing ' + String(offSet + 1) + ' to ' + String(offSet + count) + ' of ' + String(totalRows) + ' Readings');

    $('#tablePagination').html = '';
    var maxLeft = currentPage - Math.floor(pageButtonWindow / 2);
    var maxRight = currentPage + Math.floor(pageButtonWindow / 2);

    if (maxLeft < 1) {
        maxLeft = 1;
        maxRight = pageButtonWindow;
        if (maxRight > totalPages) {
            maxRight = totalPages;
        }
    }

    if (maxRight > totalPages) {
        maxLeft = totalPages - pageButtonWindow + 1;
        if (maxLeft < 1) {
            maxLeft = 1;
        }
        maxRight = totalPages;
    }

    var prevDisableState = '', nextDisableState = '', prevTabIndex = '', nextTabIndex = '';

    if (currentPage == 1) {
        prevDisableState = ' disabled';
        prevTabIndex = " tabindex ='-1'";
    }

    if (currentPage == totalPages) {
        nextDisableState = ' disabled';
        nextTabIndex = " tabindex ='-1'";
    }

    var paginationHtml = "<li class='page-item" + prevDisableState + "'><a class='page-link'" + prevTabIndex + " href='javascript:void(0)' value=1>&#171;</a></li>";

    for (var page = maxLeft; page <= maxRight; page++) {
        if (page == currentPage) {
            paginationHtml += "<li class='page-item active'><span class='page-link' href='javascript:void(0)' value=" + String(page) + ">" + String(page) + "</span></li>"
        } else {
            paginationHtml += "<li class='page-item'><a class='page-link' href='javascript:void(0)' value=" + String(page) + ">" + String(page) + "</a></li>"
        }
    }

    paginationHtml += "<li class='page-item" + nextDisableState + "'><a class='page-link'" + nextTabIndex + " href='javascript:void(0)' value=" + String(totalPages) + ">&#187;</a></li>";

    $('#tablePagination').html(paginationHtml);
}



function GetElementReadings() {
    $('#elementList').empty();
    $('#spinnerStatus').show();
    offSet = ((currentPage - 1) * rowsInPage);
    requestData = { search: searchText, start: startDate, end: endDate, offset: offSet, limit: rowsInPage };
    $.ajax({
        url: 'reading_records',
        method: 'GET',
        data: requestData,
        success: function (elements) {
            $('#spinnerStatus').hide();
            // console.log(elements.totalCount);
            // console.log(elements.elements);
            totalRows = elements.totalCount;
            totalPages = Math.ceil(totalRows / rowsInPage);
            var elementRowTemplate = $.templates('#elementTemplete');

            var elementRowHtml = elementRowTemplate.render(elements);

            $('#elementList').html(elementRowHtml);
            SetPaginationButtons(elements.count);
        },
        error: function (error) {
            console.log(error);
            $('#spinnerStatus').hide();
        }

    });
}

$(function () {
    GetElementReadings();
});


$('ul.pagination').on('click', 'li', function (e) {
    // console.log('clicked');
    // console.log($(this).hasClass('disabled'));

    if ($(this).hasClass('disabled') || $(this).hasClass('active')) {
        return false;
    }

    currentPage = Number($(this).find('a').attr('value'));
    // console.log(currentPage);
    GetElementReadings();
});

$('#selectRowsInPage').change(function () {
    rowsInPage = $(this).val();
    currentPage = 1;
    GetElementReadings();
});


function setDataRangeDisplay(start, end) {
    startDate = start.format('YYYY-MM-DD HH:mm');
    endDate = end.format('YYYY-MM-DD HH:mm');
    // console.log(startDate);
    $('#reportrange span').html(start.format('M/DD hh:mm A') + ' - ' + end.format('M/DD hh:mm A'));
    currentPage = 1;
    GetElementReadings();
}

$(function () {

    var start = moment().subtract(24, 'hours');
    var end = moment();

    $('#reportrange').daterangepicker({
        timePicker: true,
        autoUpdateInput: false,
        locale: {
            cancelLabel: 'Clear'
        }

    });


    $('#reportrange').on('apply.daterangepicker', function (ev, picker) {
        // $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
        setDataRangeDisplay(picker.startDate, picker.endDate);
    });

    $('#reportrange').on('cancel.daterangepicker', function (ev, picker) {
        // $(this).val('');
        $('#reportrange span').html('');
        startDate = '';
        endDate = '';
        GetElementReadings();
    });

});

$(function () {
    $('#searchText').keyup(function () {
        searchText = $('#searchText').val();
        // console.log(searchText);
        currentPage = 1;
        GetElementReadings();
    });
});

function GetElementReadingsCSV() {
    requestData = { search: searchText, start: startDate, end: endDate };
    $.ajax({
        url: 'reading_records_csv',
        method: 'GET',
        data: requestData,
        success: function (elements) {
            rows = elements.elements;
            csvContent = '';
            rows.forEach(function (row) {
                csvContent += row.join(',');
                csvContent += '\n';
            });

            // console.log(csvContent);

            var hiddenElement = document.createElement('a');
            hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csvContent);
            hiddenElement.target = '_blank';
            hiddenElement.download = 'element_readings.csv';
            hiddenElement.click();
        },
        error: function (error) {
            console.log(error);
        }

    });
}

$(function () {
    $('#btnExportCSV').click(function () {
        GetElementReadingsCSV();
    });
});