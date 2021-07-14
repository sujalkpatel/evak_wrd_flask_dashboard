var elementId, groupIdToDelete, elementNameToDelete, elementList = [], groupId;
var searchText = '', prevSearchText = '';
var currentPage = 1, totalPages = 0, rowsInPage = 10, totalRows = 0, pageButtonWindow = 5, offSet = 0;

function showSuccessAlert(message) {
    var alertHtml = "";
    alertHtml += "<div class='alert alert-success alert-dismissible fade show' role='alert'>";
    alertHtml += message;
    alertHtml += "  <button type='button' class='btn-close' data-bs-dismiss='alert' aria-label='Close'></button>";
    alertHtml += "</div>";

    // console.log(alertHtml);
    $('#alertGroupMain').html(alertHtml);
    $('#alertGroupMain').show();
}

function showWarningAlert(message) {
    var alertHtml = "";
    alertHtml += "<div class='alert alert-warning alert-dismissible fade show' role='alert'>";
    alertHtml += message;
    alertHtml += "  <button type='button' class='btn-close' data-bs-dismiss='alert' aria-label='Close'></button>";
    alertHtml += "</div>";

    // console.log(alertHtml);
    $('#alertGroupMain').html(alertHtml);
    $('#alertGroupMain').show();
}

function showDangerAlert(message) {
    var alertHtml = "";
    alertHtml += "<div class='alert alert-danger alert-dismissible fade show' role='alert'>";
    alertHtml += message;
    alertHtml += "  <button type='button' class='btn-close' data-bs-dismiss='alert' aria-label='Close'></button>";
    alertHtml += "</div>";

    // console.log(alertHtml);
    $('#alertGroupMain').html(alertHtml);
    $('#alertGroupMain').show();
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

var groupEditModal = document.getElementById('groupEditModal');
groupEditModal.addEventListener('hide.bs.modal', function (event) {
    CloseEditModal();
});


function GetReadingGroups() {
    $('#groupList').empty();
    $('#alertGroupMain').hide();
    $('#spinnerStatus').show();
    offSet = ((currentPage - 1) * rowsInPage);
    requestData = { search: searchText, offset: offSet, limit: rowsInPage };
    $.ajax({
        url: 'api/reading_groups',
        method: 'GET',
        data: requestData,
        success: function (records) {
            $('#spinnerStatus').hide();
            totalRows = records.totalCount;
            totalPages = Math.ceil(totalRows / rowsInPage);
            $.views.settings.allowCode(true);

            var groupRowHtml = $('#groupTemplate').render(records);

            $('#groupList').html(groupRowHtml);
            SetPaginationButtons(records.count);
        },
        error: function (error) {
            console.log(error);
            $('#spinnerStatus').hide();
        }

    });
}

$(function () {
    GetReadingGroups();
});

$('ul.pagination').on('click', 'li', function (e) {
    // console.log('clicked');
    // console.log($(this).hasClass('disabled'));

    if ($(this).hasClass('disabled') || $(this).hasClass('active')) {
        return false;
    }

    currentPage = Number($(this).find('a').attr('value'));
    // console.log(currentPage);
    GetReadingGroups();
});

$('#selectRowsInPage').change(function () {
    rowsInPage = $(this).val();
    currentPage = 1;
    GetReadingGroups();
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
        GetReadingGroups();
    });
});

function CloseEditModal() {
    $('#readingList').empty();
    $('#alertEditGroup').hide();
}

function replaceSpaceByUnderscore(element) {
    return element.replace(/\s/g, '__');
}

function EditGroup(groupRow) {
    $('#readingList').empty();
    $('#spinnerStatus').show();
    groupId = $(groupRow).attr('group-id');
    var url = 'api/reading_groups/';
    url = url.concat(String(groupId));
    elementList = []

    $.ajax({
        url: url,
        method: 'GET',
        success: function (readings) {
            for (var i = 0; i < readings.records.length; i++) {
                elementList.push(readings.records[i][0]);
            }

            $('#spinnerStatus').hide();
            $('#editModalLabel').html('Edit Group# ' + groupId);

            var myHelper = { removeSpace: replaceSpaceByUnderscore };
            var readingRowHtml = $('#readingTemplate').render(readings, myHelper);
            $('#readingList').html(readingRowHtml);

            $('#groupEditModal').modal('show');
        },
        error: function (error) {
            console.log(error);
        }

    });
}

$(function () {
    $('#btnUpdateGroupModal').click(function () {
        var url = 'api/reading_groups/';
        url = url.concat(String(groupId));

        requestData = {
            readings: []
        };

        for (var i = 0; i < elementList.length; i++) {
            requestData.readings.push({
                element_name: elementList[i],
                reading_value: $('#' + replaceSpaceByUnderscore(elementList[i])).val()
            });
        }

        $.ajax({
            url: url,
            method: 'PUT',
            data: JSON.stringify(requestData),
            contentType: 'application/json;',
            success: function (result) {
                if (!('error' in result)) {
                    $('#groupEditModal').modal('hide');
                    GetReadingGroups();
                    showSuccessAlert(
                        String(result.rows_updated) + ' Readings updated of Group# ' + String(result.group_id) + '.'
                    );
                } else {
                    $('#alertEditGroup').text(result.error);
                    $('#alertEditGroup').show();
                }
            },
            error: function (error) {
                console.log(error);
                $('#groupEditModal').modal('hide');
                showDangerAlert(String(error));
            }

        });
    });
});

$(function () {
    $('#btnCloseEditElementModal').click(function () {
        CloseEditModal();
    });
});

function DeleteGroup(groupRow) {
    groupIdToDelete = $(groupRow).attr('group-id');

    var url = 'api/reading_groups/';
    url = url.concat(String(groupIdToDelete));
    console.log(url);

    var label = 'Are you sure to delete readings and an image of Group# ' + groupIdToDelete + '?';

    $('#deleteModalLabel').empty();
    $('#deleteModalLabel').html(label);

    $('#groupDeleteModal').modal('show');

}

$(function () {
    $('#btnDeleteGroupModal').click(function () {
        console.log(groupIdToDelete);
        var url = 'api/reading_groups/';
        url = url.concat(String(groupIdToDelete));
        console.log(url);

        $.ajax({
            url: url,
            method: 'DELETE',
            success: function (result) {
                console.log(result)
                if (!('error' in result)) {
                    $('#groupDeleteModal').modal('hide');
                    GetReadingGroups();
                    showWarningAlert(
                        String(result.rows_deleted) + ' Readings and an image deleted from Group# ' + String(result.group_id) + '.'
                    );
                } else {
                    $('#alertDeleteGroup').text(result.error);
                    $('#alertDeleteGroup').show();
                }
            },
            error: function (error) {
                console.log(error);
                $('#groupDeleteModal').modal('hide');
                showDangerAlert(String(error));
            }

        });
    });
});