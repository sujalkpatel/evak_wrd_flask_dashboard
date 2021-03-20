var dateSelected = '', dateToPrint = '', readingTime = '', searchText = '';
var locationSelected = '', stationSelected = '';
var stationNames = new Map();
var elementReadings;
var waterBody = '', subdivisionName = '';
var subdivisionMap = new Map();
var logoImage = '', reportImage = '', reportImageFileName = '';
var imageWidth = 0, imageHeight = 0;

subdivisionMap.set('Ahmedabad', 'Water Resources Investigaton Sub Division Ahmedabad');
subdivisionMap.set('VADODARA- NAVSARI', 'River Gauging Sub Division Vadodara/Navsari');
subdivisionMap.set('Rajkot', 'River Gauging Sub Division Rajkot');
subdivisionMap.set('Bhavnagar', 'River Gauging Sub Division Bhavnagar');
subdivisionMap.set('Bhuj', 'River Gauging Sub Division Bhuj');

getLocations();
getLogoImage();

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

    if (dateSelected != '' && locationSelected != '' && stationSelected != '') {
        GetElementReadings();
    }
});

function resetSiteLabels() {
    $('#locationName').html('Name of Subdivision:______');
    $('#stationName').html('Site Location: ______');
    $('#dateSelected').html('Date: ______ ');
}

function setSiteLabels() {
    $('#locationName').html('Name of Subdivision: ' + subdivisionName);
    $('#stationName').html('Site Location: ' + waterBody + ' (' + stationSelected + ')');
    $('#dateSelected').html('Date: ' + dateToPrint + ' ' + readingTime);
}

function GetElementReadings() {
    $('#elementList').empty();
    $('#spinnerStatus').show();
    resetSiteLabels();
    requestData = { location: locationSelected, station: stationSelected, date: dateSelected };
    $.ajax({
        url: 'reading_records_report',
        method: 'GET',
        data: requestData,
        success: function (elements) {
            $('#spinnerStatus').hide();
            // console.log(elements.totalCount);
            // console.log(elements.elements);
            var elementRowTemplate = $.templates('#elementTemplete');

            var elementRowHtml = elementRowTemplate.render(elements);
            elementReadings = elements.elements;
            waterBody = elements.water_body;
            subdivisionName = locationSelected;
            readingTime = '';
            reportImage = '';
            reportImageFileName = '';
            imageWidth = 0;
            imageHeight = 0;

            if (elementReadings.length > 0) {
                if (subdivisionMap.has(locationSelected)) {
                    subdivisionName = subdivisionMap.get(locationSelected);
                }
                readingTime = elements.reading_time;
                reportImage = elements.image;
                reportImageFileName = elements.image_file_name;
                imageWidth = elements.imageWidth;
                imageHeight = elements.imageHeight;
                // console.log(imageHeight);
                // console.log(imageWidth);
                setSiteLabels();
            }
            $('#elementList').html(elementRowHtml);

        },
        error: function (error) {
            console.log(error);
            $('#spinnerStatus').hide();
        }

    });
}


$('#selectRowsInPage').change(function () {
    rowsInPage = $(this).val();
    currentPage = 1;
    GetElementReadings();
});


function setDataRangeDisplay(start) {
    dateSelected = start.format('YYYY-MM-DD');
    dateToPrint = start.format('DD/MM/YYYY');
    // console.log(dateSelected);
    $('#reportrange span').html(start.format('YYYY-MM-DD'));
    currentPage = 1;
    GetElementReadings();
}

$(function () {
    var start = moment();

    $('#reportrange').daterangepicker({
        singleDatePicker: true,
        // autoUpdateInput: false,
        opens: 'left'
    });

    setDataRangeDisplay(start);


    $('#reportrange').on('apply.daterangepicker', function (ev, picker) {
        // $(this).val(picker.startDate.format('MM/DD/YYYY') + ' - ' + picker.endDate.format('MM/DD/YYYY'));
        setDataRangeDisplay(picker.startDate);
    });

});

function getLogoImage() {
    $.ajax({
        url: 'logoImage',
        method: 'GET',
        success: function (result) {
            // console.log(result)
            logoImage = result.image;
        },
        error: function (error) {
            console.log(error);
        }

    });
}

function prepareReport() {
    var doc = new jspdf.jsPDF();
    var y = 8, y1 = 14;

    doc.addImage('data:image/jpeg;base64,' + logoImage, 'JPEG', 30, y += 5, 50, 36);
    doc.line(15, y += 37, 195, y);

    doc.setFontSize(8);
    doc.text('Address:', 100, y1 += 5);
    doc.text('GOVERNMENT OF GUJARAT', 100, y1 += 5);
    doc.text('OFFICE OF THE EXECUTIVE ENGINEER', 100, y1 += 5);
    doc.text('WATER RESOURCES INVESTIGATION DIVISION,', 100, y1 += 5);
    doc.text('C-9, MULTISTORYED BUILDING, LAL DARWAJA, AHMEDABAD-380001', 100, y1 += 5);
    doc.text('WRD PHONE (0): 25507098,(P) 25507094, (FAX) 25507098', 100, y1 += 5);

    doc.setFontSize(10);
    doc.text('Name of Subdivision:', 15, y += 7);
    doc.text(subdivisionName, 50, y);

    doc.text('Date:', 165, y);
    doc.text(dateToPrint, 177, y);

    doc.text('Site Location:', 15, y += 6);
    doc.text(waterBody + ' (' + stationSelected + ')', 38, y);

    doc.text('Time:', 165, y);
    doc.text(readingTime, 175, y);

    doc.autoTable({
        html: '#reportTable',
        startY: y += 4
    });

    // Put image if present
    if (reportImageFileName.length > 0) {
        var imWidth = imageWidth, imHeight = imageHeight;
        if (imWidth > 160) {
            imHeight = imHeight * (160 / imWidth);
            imWidth = 160;
        }
        if (imHeight > 160) {
            imWidth = imWidth * (160 / imHeight);
            imHeight = 160;
        }

        // console.log(imWidth);
        // console.log(imHeight);
        y = doc.lastAutoTable.finalY;

        if (y + 10 + imHeight + 10 > 280) {
            doc.addPage();
            y = 10;
        }

        doc.addImage('data:image/jpeg;base64,' + reportImage, 'JPEG', 25, y += 10, imWidth, imHeight)
        doc.text('File Name: ' + reportImageFileName, 25, y += imHeight + 7);
    }

    const pageCount = doc.internal.getNumberOfPages();
    var pgX = 14;

    for (var i = 1; i <= pageCount; i++) {
        var pageLine = 'Page ' + String(i) + ' of ' + String(pageCount);
        doc.setPage(i);
        if (i > 9) {
            pgX = 16;
        }
        doc.text(pageLine, 210 - pgX, 297 - 12, null, null, "right");
    }

    doc.save(stationSelected + '_' + dateSelected + '.pdf');
}
