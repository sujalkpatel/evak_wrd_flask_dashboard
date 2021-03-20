
var ctx = document.getElementById('myChart');
var timeFormat = 'MM/DD/YYYY HH:mm';
var lineChartWrapper, lineChartData, lineChartOptions;


var start = moment().subtract(29, 'days'), end = moment(), diffInSec = end.diff(start, 'seconds');
var startDate = start.format('YYYY-MM-DD HH:mm'), endDate = end.format('YYYY-MM-DD HH:mm');
var drPicker;
var defaultRangeLabel = 'Last 30 Days';
var customSelected = 0;

var locations, stations, elements;
var locationSelected = '', stationSelected = '', elementSelected = '', elementUnit = '';
var stationNames = new Map();

google.charts.load('current', { 'packages': ['corechart'] });
google.charts.setOnLoadCallback(initializeDataRangeDisplay);

function getLocations() {
    $.ajax({
        url: 'getLocationsFromReadings',
        method: 'GET',
        success: function (result) {
            // console.log(result)
            locations = result.locations;
            setSelectLocations();
        },
        error: function (error) {
            console.log(error);
        }

    });
}

function setSelectLocations() {
    var selectHtml = "<option selected disabled value=''>Select Location</option>";

    for (var i in locations) {
        selectHtml += "<option value='" + locations[i] + "'>" + locations[i] + "</option>";
    }

    $('#selectLocation').html(selectHtml);
}

$('#selectLocation').change(function () {
    locationSelected = $(this).val();
    stationSelected = '';
    stations = '';
    stationNames.clear();
    setSelectStations();
    getStations();
});

function getStations() {
    requestData = { location: locationSelected }
    $.ajax({
        url: 'getStationsFromReadingsByLocation',
        method: 'GET',
        data: requestData,
        success: function (result) {
            // console.log(result)
            stations = result.stations;
            stationNames = new Map(result.stationNames);

            setSelectStations();
        },
        error: function (error) {
            console.log(error);
        }

    });
}

function setSelectStations() {
    var selectHtml = "<option selected disabled value=''>Select Station</option>";

    for (var i in stations) {
        selectHtml += "<option value='" + stations[i] + "'>" + stations[i] + "</option>";
    }

    $('#selectStation').html(selectHtml);
}

$('#selectStation').change(function () {
    stationSelected = $(this).val();

    if (elementSelected != '' && locationSelected != '' && stationSelected != '') {
        getReadings();
    }
});

function getElementNames() {
    $.ajax({
        url: 'getElementNames',
        method: 'GET',
        success: function (result) {
            // console.log(result)
            elements = result.elements;
            setSelectElements();
        },
        error: function (error) {
            console.log(error);
        }

    });
}

function setSelectElements() {
    var selectHtml = "<option selected disabled value=''>Select Element</option>";

    for (var i in elements) {
        selectHtml += "<option value='" + elements[i] + "'>" + elements[i] + "</option>";
    }

    $('#selectElement').html(selectHtml);
}

$('#selectElement').change(function () {
    elementSelected = $(this).val();
    if (elementSelected != '' && locationSelected != '' && stationSelected != '') {
        getReadings();
    }
});


function drawChart(resultData) {
    // create date object
    for (var i = 0; i < resultData.data.length; i++) {
        resultData.data[i][0] = new Date(resultData.data[i][0]);
    }

    elementUnit = resultData.unit;

    lineChartData = new google.visualization.DataTable();
    lineChartData.addColumn('datetime', 'Time of Day');
    lineChartData.addColumn('number', 'Value (' + elementUnit + ')');

    lineChartData.addRows(resultData.data);

    lineChartOptions = {
        title: 'Values of ' + elementSelected + ' at ' + stationSelected + '(' + stationNames.get(stationSelected) + ') in ' + locationSelected,
        curveType: 'function',
        legend: 'none', // { position: 'bottom' },
        pointSize: 5,
        hAxis: { minValue: new Date(startDate), maxValue: new Date(endDate) },
        vAxis: { title: 'Value (' + elementUnit + ')' }
    };

    lineChartWrapper.setDataTable(lineChartData);
    lineChartWrapper.setOptions(lineChartOptions);

    lineChartWrapper.draw();
}

function initializeDataRangeDisplay() {
    $('#reportrange span').html(defaultRangeLabel);

    $('#myChart').html('Select input to display trends');
    getLocations();
    getElementNames();
    lineChartWrapper = new google.visualization.ChartWrapper();
    lineChartWrapper.setChartType('LineChart');
    lineChartWrapper.setContainerId('myChart');
}

function setDataRangeDisplay(start, end) {
    startDate = start.format('YYYY-MM-DD HH:mm');
    endDate = end.format('YYYY-MM-DD HH:mm');
    drPicker = $('#reportrange').data('daterangepicker');

    // console.log(drPicker.chosenLabel);
    // console.log(startDate + ' - ' + endDate);
    if (customSelected == 1 || drPicker.chosenLabel == 'Custom Range') {
        $('#reportrange span').html(start.format('M/DD hh:mm A') + ' - ' + end.format('M/DD hh:mm A'));
    } else {
        $('#reportrange span').html(drPicker.chosenLabel);
    }
    diffInSec = end.diff(start, 'seconds');
    if (elementSelected != '' && locationSelected != '' && stationSelected != '') {
        getReadings();
    }
}

$(function () {
    $('#reportrange').daterangepicker({
        timePicker: true,
        autoUpdateInput: false,
        startDate: start,
        endDate: end,
        opens: 'left',
        ranges: {
            'Last 5 minutes': [moment().subtract(5, 'minutes'), moment()],
            'Last 15 minutes': [moment().subtract(15, 'minutes'), moment()],
            'Last 30 minutes': [moment().subtract(30, 'minutes'), moment()],
            'Last 1 hour': [moment().subtract(1, 'hours'), moment()],
            'Last 3 hours': [moment().subtract(3, 'hours'), moment()],
            'Last 6 hours': [moment().subtract(6, 'hours'), moment()],
            'Last 12 hours': [moment().subtract(12, 'hours'), moment()],
            'Last 24 hours': [moment().subtract(24, 'hours'), moment()],
            'Last 2 Days': [moment().subtract(2, 'days'), moment()],
            'Last 7 Days': [moment().subtract(6, 'days'), moment()],
            'Last 30 Days': [moment().subtract(29, 'days'), moment()],
            'This Month': [moment().startOf('month'), moment().endOf('month')],
            'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')]
        }
    });

    $('#reportrange').on('apply.daterangepicker', function (ev, picker) {
        customSelected = 0;
        start = picker.startDate;
        end = picker.endDate;
        setDataRangeDisplay(picker.startDate, picker.endDate);
    });
});

$(function () {
    $('#btnRangePrev').click(function () {
        customSelected = 1;
        end = start;
        start = moment(end).subtract(diffInSec, 'seconds');

        drPicker = $('#reportrange').data('daterangepicker');

        drPicker.setStartDate(start);
        drPicker.setEndDate(end);

        setDataRangeDisplay(start, end);
    });
});

$(function () {
    $('#btnRangeNext').click(function () {
        customSelected = 1;
        start = end;
        end = moment(start).add(diffInSec, 'seconds');

        drPicker = $('#reportrange').data('daterangepicker');

        drPicker.setStartDate(start);
        drPicker.setEndDate(end);

        setDataRangeDisplay(start, end);
    });
});

function getReadings() {
    requestData = { start: startDate, end: endDate, location: locationSelected, station: stationSelected, elementName: elementSelected };
    $.ajax({
        url: 'getReadingTrends',
        method: 'GET',
        data: requestData,
        success: function (result) {
            drawChart(result);
        },
        error: function (error) {
            console.log(error);
        }

    });
}





