var map, searchManager;
var amdPushPin, brdPushPin, suratPushPin, rajkotPushPin, jmnPushPin;
var startDate = '', endDate = '', searchText = '', selectedLocation = '';
var currentPage = 1, totalPages = 0, rowsInPage = 10, totalRows = 0, pageButtonWindow = 5, offSet = 0;


var infoboxTemplate = '<div id="infoboxText" style="background-color:rgba(255,255,255,0.8); border-style:solid; border-width:1.5px; border-color: #aa2a8f; padding: 10px; border-radius: 7px; width: fit-content;">' +
    '<h5 id="infoboxTitle" style="">{title}</h5> ' +
    // '<p>{station_id}</p>' +
    '<a id="infoboxDescription" onclick=recordClicked(this) class="reading-link" value="{value}" style="">{description}</a></div>';

var locations;


function getLocations() {
    $.ajax({
        url: 'getLocationsFromReadings',
        method: 'GET',
        success: function (result) {
            // console.log(result)
            locations = result.locations;
        },
        error: function (error) {
            console.log(error);
        }

    });
}

function getLocationCoordinates(location) {
    requestData = { location: location };
    $.ajax({
        url: 'location_coordinates',
        method: 'GET',
        data: requestData,
        success: function (result) {
            // console.log(result)
            if (result.total == 0) {
                searchLocation(location);
                // console.log('search completed');

            } else {
                addPushPin(location, new Microsoft.Maps.Location(result.lat, result.lng));
            }
        },
        error: function (error) {
            console.log(error);
        }

    });
}

function setLocationCoordinates(location, lat, lng) {
    requestData = { location: location, lat: lat, lng: lng };
    $.ajax({
        url: 'location_coordinates',
        method: 'POST',
        data: requestData,
        success: function (result) {
            // console.log(result)

        },
        error: function (error) {
            console.log(error);
        }

    });
}

getLocations();

// $('#infoboxDescription').on('click', function (e) {
//     console.log('clicked');
//     // console.log($(this).hasClass('disabled'));
//     // console.log($(this).attr('value'))
//     alert($(this).val());
// });

function searchLocation(location) {
    var searchRequest = {
        where: location,
        callback: function (r) {
            if (r && r.results && r.results.length > 0) {
                // console.log('location found');
                // console.log(r.results[0].location.latitude);
                // console.log(r.results[0].location.longitude);
                setLocationCoordinates(location, r.results[0].location.latitude, r.results[0].location.longitude);
                addPushPin(location, r.results[0].location);

            }
        },
        errorCallback: function (e) {
            //If there is an error, alert the user about it.
            alert("No results found.");
        }
    };

    //Make the geocode request.
    searchManager.geocode(searchRequest);
}

function addPushPin(locationName, location) {
    var pin = new Microsoft.Maps.Pushpin(location, null);
    var infobox = new Microsoft.Maps.Infobox(location, {
        htmlContent: infoboxTemplate
            .replace('{title}', locationName)
            .replace('{description}', 'Show Readings')
            .replace('{value}', locationName),

        // {
        // title: locationName,
        // description: 'Readings',
        visible: false,
        showCloseButton: true,
        actions: [{ label: 'Show Readings 1', eventHandler: function () { alert(locationName); } }]
    }
    );
    infobox.setMap(map);
    Microsoft.Maps.Events.addHandler(pin, 'click', function () {
        infobox.setOptions({ visible: true });
    });
    Microsoft.Maps.Events.addHandler(pin, 'mouseout', function () {
        infobox.setOptions({ visible: false });
    });
    //Add the pins to the map
    map.entities.push(pin);
}

window.onload = function () {
    map = new Microsoft.Maps.Map(document.getElementById('indiaMap'), {
        zoom: 8,
        center: new Microsoft.Maps.Location(22.347354, 71.688290),
        supportedMapTypes: [Microsoft.Maps.MapTypeId.road]
    });

    Microsoft.Maps.loadModule('Microsoft.Maps.Search', function () {
        searchManager = new Microsoft.Maps.Search.SearchManager(map);

        for (var i = 0; i < locations.length; i++) {
            // console.log(locations[i]);
            var result = getLocationCoordinates(locations[i]);
        }
    });

}


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

function GetElementReadings() {
    $('#elementList').empty();
    $('#spinnerStatus').show();
    offSet = ((currentPage - 1) * rowsInPage);
    requestData = { search: searchText, location: selectedLocation, start: startDate, end: endDate, offset: offSet, limit: rowsInPage };
    $.ajax({
        url: 'reading_records_location',
        method: 'GET',
        data: requestData,
        success: function (elements) {
            $('#spinnerStatus').hide();
            // console.log(elements.totalCount);
            // console.log(elements.count);
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


function recordClicked(e) {
    selectedLocation = $(e).attr('value');
    $('#getReadingsModalLabel').html('Recent Element Readings from ' + selectedLocation);
    $('#getReadingsModal').modal('show');
    GetElementReadings();
}

var elementReadingsModal = document.getElementById('getReadingsModal');
elementReadingsModal.addEventListener('hide.bs.modal', function (event) {
    CloseReadingsModal();
});

function CloseReadingsModal() {

    startDate = '';
    endDate = '';
    searchText = '';
    currentPage = 1;
    totalPages = 0;
    totalRows = 0;
    offSet = 0;

    $('#reportrange span').html('');
    $('#searchText').val('');
}