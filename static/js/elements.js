var elementId, elementIdToDelete, elementNameToDelete;

var elementEditModal = document.getElementById('elementEditModal');
elementEditModal.addEventListener('hide.bs.modal', function (event) {
    CloseEditModal();
});

var elementCreateModal = document.getElementById('elementCreateModal');
elementCreateModal.addEventListener('hide.bs.modal', function (event) {
    CloseCreateModal();
});

function GetElements() {
    $.ajax({
        url: 'getElement',
        method: 'GET',
        success: function (elements) {
            $('#elementList').empty();
            var elementRowTemplate = $.templates('#elementTemplete');

            var elementRowHtml = elementRowTemplate.render(elements);

            $('#elementList').html(elementRowHtml);
        },
        error: function (error) {
            console.log(error);
        }

    });
}

$(function () {
    GetElements();
});

function CloseEditModal() {
    // 
    $('#elementName').val('');
    $('#elementUnit').val('');
    $('#elementMin').val('');
    $('#elementMax').val('');
    $('#alertEditElement').hide();
}

function EditElement(elementRow) {
    elementId = $(elementRow).attr('element-id');
    console.log(elementId);
    var url = 'getElement/';
    url = url.concat(String(elementId));
    console.log(url);

    $.ajax({
        url: url,
        method: 'GET',
        success: function (element) {
            console.log(element)
            $('#elementName').val(element.name);
            $('#elementUnit').val(element.unit);
            $('#elementMin').val(element.min);
            $('#elementMax').val(element.max);

            $('#elementEditModal').modal('show');
        },
        error: function (error) {
            console.log(error);
        }

    });
}

$(function () {
    $('#btnUpdateElementModal').click(function () {
        console.log(elementId);
        var url = 'updateElement/';
        url = url.concat(String(elementId));
        console.log(url);
        requestData = {
            name: $('#elementName').val(),
            unit: $('#elementUnit').val(),
            min: $('#elementMin').val(),
            max: $('#elementMax').val()
        };

        $.ajax({
            url: url,
            method: 'PUT',
            data: requestData,
            success: function (result) {
                console.log(result)
                if (!('error' in result)) {
                    $('#elementEditModal').modal('hide');

                    GetElements();
                } else {
                    $('#alertEditElement').text(result.error);
                    $('#alertEditElement').show();
                }
            },
            error: function (error) {
                console.log(error);
            }

        });
    });
});

$(function () {
    $('#btnCloseEditElementModal').click(function () {
        CloseEditModal();
    });
});

function DeleteElement(elementRow) {
    elementIdToDelete = $(elementRow).attr('element-id');
    elementNameToDelete = $(elementRow).attr('element-name');
    console.log(elementIdToDelete);
    var url = 'deleteElement/';
    url = url.concat(String(elementId));
    console.log(url);

    var label = 'Are you sure to delete ' + elementNameToDelete + '?';
    console.log(label);

    $('#deleteModalLabel').empty();
    var deleteModalLabelTemplete = $.templates('#deleteModalLableTemplete');

    var deleteModalLabelTempleteHtml = deleteModalLabelTemplete.render({ msg: label });

    $('#deleteModalLabel').html(deleteModalLabelTempleteHtml);

    $('#elementDeleteModal').modal('show');

}

$(function () {
    $('#btnDeleteElementModal').click(function () {
        console.log(elementIdToDelete);
        var url = 'deleteElement/';
        url = url.concat(String(elementIdToDelete));
        console.log(url);

        $.ajax({
            url: url,
            method: 'DELETE',
            success: function (result) {
                console.log(result)
                $('#elementDeleteModal').modal('hide');

                GetElements();
            },
            error: function (error) {
                console.log(error);
            }

        });
    });
});

function CloseCreateModal() {

    $('#elementNameNew').val('');
    $('#elementUnitNew').val('');
    $('#elementMinNew').val('');
    $('#elementMaxNew').val('')
    $('#alertElementExists').hide();
}

function AddElement() {
    $('#elementCreateModal').modal('show');
}

$(function () {
    $('#btnAddElementModal').click(function () {
        $('#alertElementExists').hide();
        var url = 'addElement';
        console.log(url);
        requestData = { name: $('#elementNameNew').val(), unit: $('#elementUnitNew').val(), min: $('#elementMinNew').val(), max: $('#elementMaxNew').val() };

        $.ajax({
            url: url,
            method: 'POST',
            data: requestData,
            success: function (result) {
                console.log(result)
                if (!('error' in result)) {
                    $('#elementCreateModal').modal('hide');

                    GetElements();
                } else {
                    console.log('exists')
                    $('#alertElementExists').text(result.error);
                    $('#alertElementExists').show();

                }
            },
            error: function (error) {
                console.log(error);
            }

        });
    });
});

$(function () {
    $('#btnCloseAddElementModal').click(function () {
        CloseCreateModal();
    });
});