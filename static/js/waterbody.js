var searchText = '', prevSearchText = '';
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

function GetWaterBodies() {
    $('#waterBodyList').empty();
    $('#spinnerStatus').show();
    offSet = ((currentPage - 1) * rowsInPage);
    requestData = { search: searchText, offset: offSet, limit: rowsInPage };
    $.ajax({
        url: 'waterbody_records',
        method: 'GET',
        data: requestData,
        success: function (waterbodies) {
            $('#spinnerStatus').hide();
            // console.log(waterbodies.totalCount);
            // console.log(waterbodies.waterbodies);
            totalRows = waterbodies.totalCount;
            totalPages = Math.ceil(totalRows / rowsInPage);
            var waterBodyRowTemplate = $.templates('#waterBodyTemplete');

            var waterBodyRowHtml = waterBodyRowTemplate.render(waterbodies);

            $('#waterBodyList').html(waterBodyRowHtml);
            SetPaginationButtons(waterbodies.count);
        },
        error: function (error) {
            console.log(error);
            $('#spinnerStatus').hide();
        }

    });
}

$(function () {
    GetWaterBodies();
});

$('ul.pagination').on('click', 'li', function (e) {
    // console.log('clicked');
    // console.log($(this).hasClass('disabled'));

    if ($(this).hasClass('disabled') || $(this).hasClass('active')) {
        return false;
    }

    currentPage = Number($(this).find('a').attr('value'));
    // console.log(currentPage);
    GetWaterBodies();
});

$('#selectRowsInPage').change(function () {
    rowsInPage = $(this).val();
    currentPage = 1;
    GetWaterBodies();
});

$(function () {
    $('#searchText').keyup(function () {
        searchText = $('#searchText').val();
        if (prevSearchText == searchText) {
            return;
        }
        prevSearchText = searchText;
        // console.log(searchText);
        currentPage = 1;
        GetWaterBodies();
    });
});

function generateReport(waterBody) {
    $('#spinnerStatus').show();
    stationId = $(waterBody).attr('station-id');
    $('#btn-' + stationId).addClass('disabled');
    var url = 'waterbody_records/report/'
    url = url.concat(String(stationId));

    $.ajax({
        url: url,
        method: 'GET',
        success: function (data) {
            console.log(data);
            $('#spinnerStatus').hide();
            $('#btn-' + stationId).removeClass('disabled');
            prepareReport(data.groups, stationId);
        },
        error: function (error) {
            console.log(error);
            $('#spinnerStatus').hide();
            $('#btn-' + stationId).removeClass('disabled');
        }
    });
}

function prepareReport(groups, stationId) {
    var doc = new jspdf.jsPDF('landscape');
    var footerText = 'EXECUTIVE ENGINEER WATER RESOURCES INVESTIGATION DIVISION, AHMEDABAD-380001, GOVERNMENT OF GUJARAT';

    for (var i = 0; i < groups.length; i++) {
        var y = 7;

        doc.setFontSize(22);
        doc.text('NATIONAL HYDROLOGY PROJECT – GUJARAT', 148, y += 5, null, null, 'center');

        // doc.setFont("helvetica", "bold");
        doc.setFontSize(12);
        doc.text('Water Quality Test Results', 148, y += 9, null, null, 'center');

        doc.setFontSize(10);
        doc.text('Report ID: ' + groups[i].groupId, 282, 17, null, null, 'right');
        doc.text(groups[i].monthYear, 282, 25, null, null, 'right');

        doc.setFontSize(9);
        doc.text('1.   Location: ' + groups[i].waterbodyName, 20, y += 17);

        doc.text('2.   Station ID: ' + groups[i].stationId, 20, y += 6);
        doc.text('8.   Sampling Date: ' + groups[i].samplingDate, 80, y);

        doc.text('3.   Latitude: ' + groups[i].latitude, 20, y += 6);
        doc.text('9.   Sampling Time: ' + groups[i].samplingTime, 80, y);

        doc.text('4.   Longitude: ' + groups[i].longitude, 20, y += 6);
        doc.text('10. Result Publish Date: ' + groups[i].publishDate, 80, y);

        doc.text('5.   District: ' + groups[i].district, 20, y += 6);
        doc.text('11. Result Publish Time: ' + groups[i].publishTime, 80, y);

        doc.text('6.   Taluka: ' + groups[i].taluka, 20, y += 6);
        doc.text('12. Mobile Van Number: ' + groups[i].vanNumber, 80, y);

        doc.text('7.   Category: ' + groups[i].category, 20, y += 6);

        doc.setDrawColor(150);
        doc.setLineWidth(0.1);
        doc.rect(15, 30, 127, y - 30 + 6);

        if (groups[i].image.length > 0) {
            var imWidth = groups[i].imageWidth, imHeight = groups[i].imageHeight;
            if (imWidth > 127) {
                imHeight = imHeight * (127 / imWidth);
                imWidth = 127;
            }
            if (imHeight > 105) {
                imWidth = imWidth * (105 / imHeight);
                imHeight = 105;
            }

            doc.addImage('data:image/jpeg;base64,' + groups[i].image, 'JPEG', 15, y += 9, imWidth, imHeight)
        }

        doc.setFontSize(8);
        doc.text('* IS 10500 : 2012 | ** Research Paper | *** CPCB Norms', 15, 210 - 18);
        doc.text('**** Laboratory analysis is to be carried out separately for assessment in case of Presence.', 15, 210 - 14);

        doc.autoTable({
            margin: {
                top: 30,
                left: 147,
                right: 15
            },
            styles: {
                fontSize: 8.25,
                lineWidth: 0.1,
                lineColor: 150
            },
            body: groups[i].element_readings,
            columns: [
                { header: 'Sr No', dataKey: 'id' },
                { header: 'Parameters', dataKey: 'elementName' },
                { header: 'Threshold Limits', dataKey: 'limit' },
                { header: 'Test Results', dataKey: 'readingValue' },
                { header: 'Unit', dataKey: 'unit' }
            ],
            columnStyles: {
                limit: { halign: 'center' },
                readingValue: { halign: 'center' },
                unit: { halign: 'center' }
            },
            headStyles: {
                halign: 'center'
            },
            didParseCell: function (data) {
                if (data.column.dataKey == 'readingValue' && data.row.index > 0 && data.row.raw.valid < 2) {
                    data.cell.styles.fontStyle = 'bolditalic';
                    // console.log(data);
                }
            }
        });

        doc.setFontSize(9);
        doc.text(footerText, 148, 210 - 7, null, null, 'center');

        doc.setDrawColor(150);
        doc.setLineWidth(0.1);
        doc.rect(49, 210 - 12, 198, 7);

        if (i + 1 < groups.length) {
            doc.addPage('l');
        }
    }

    if (groups.length > 1) {
        const pageCount = doc.internal.getNumberOfPages();

        for (var i = 1; i <= pageCount; i++) {
            var pageLine = 'Page ' + String(i) + ' of ' + String(pageCount);
            doc.setPage(i);

            doc.text(pageLine, 297 - 15, 210 - 8, null, null, "right");
        }
    }

    doc.save(stationId + '_report.pdf');
}