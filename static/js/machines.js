var machineId, machineIdToDelete, machineAddressToDelete;

var machineEditModal = document.getElementById('machineEditModal');
machineEditModal.addEventListener('hide.bs.modal', function (event) {
    CloseEditModal();
});

var machineCreateModal = document.getElementById('machineCreateModal');
machineCreateModal.addEventListener('hide.bs.modal', function (event) {
    CloseCreateModal();
});

function GetMachines() {
    $.ajax({
        url: 'getMachine',
        method: 'GET',
        success: function (machines) {
            $('#machineList').empty();
            var machineRowTemplate = $.templates('#machineTemplete');

            var machineRowHtml = machineRowTemplate.render(machines);

            $('#machineList').html(machineRowHtml);
        },
        error: function (error) {
            console.log(error);
        }

    });
}

$(function () {
    GetMachines();
});

function CloseEditModal() {
    // 
    $('#machineAddress').val('');
    $('#machineDescription').val('');
    $('#alertEditMachine').hide();
}

function EditMachine(machineRow) {
    machineId = $(machineRow).attr('machine-id');
    console.log(machineId);
    var url = 'getMachine/';
    url = url.concat(String(machineId));
    console.log(url);

    $.ajax({
        url: url,
        method: 'GET',
        success: function (machine) {
            console.log(machine)
            $('#machineAddress').val(machine.address);
            $('#machineDescription').val(machine.description);
            $('#vanNumber').val(machine.van_number);

            $('#machineEditModal').modal('show');
        },
        error: function (error) {
            console.log(error);
        }

    });
}

$(function () {
    $('#btnUpdateMachineModal').click(function () {
        console.log(machineId);
        var url = 'updateMachine/';
        url = url.concat(String(machineId));
        console.log(url);
        requestData = {
            address: $('#machineAddress').val(),
            description: $('#machineDescription').val(),
            van_number: $('#vanNumber').val()
        };

        $.ajax({
            url: url,
            method: 'PUT',
            data: requestData,
            success: function (result) {
                console.log(result)
                if (!('error' in result)) {
                    $('#machineEditModal').modal('hide');

                    GetMachines();
                } else {
                    $('#alertEditMachine').text(result.error);
                    $('#alertEditMachine').show();
                }
            },
            error: function (error) {
                console.log(error);
            }

        });
    });
});

$(function () {
    $('#btnCloseEditMachineModal').click(function () {
        CloseEditModal();
    });
});

function DeleteMachine(machineRow) {
    machineIdToDelete = $(machineRow).attr('machine-id');
    machineAddressToDelete = $(machineRow).attr('machine-address');
    // console.log(machineIdToDelete);
    // console.log(machineAddressToDelete);
    var url = 'deleteMachine/';
    url = url.concat(String(machineIdToDelete));
    // console.log(url);

    var label = 'Are you sure to delete ' + machineAddressToDelete + '?';
    // console.log(label);

    $('#deleteModalLabel').empty();
    var deleteModalLabelTemplete = $.templates('#deleteModalLableTemplete');

    var deleteModalLabelTempleteHtml = deleteModalLabelTemplete.render({ msg: label });

    $('#deleteModalLabel').html(deleteModalLabelTempleteHtml);

    $('#machineDeleteModal').modal('show');

}

$(function () {
    $('#btnDeleteMachineModal').click(function () {
        console.log(machineIdToDelete);
        var url = 'deleteMachine/';
        url = url.concat(String(machineIdToDelete));
        console.log(url);

        $.ajax({
            url: url,
            method: 'DELETE',
            success: function (result) {
                console.log(result)
                $('#machineDeleteModal').modal('hide');

                GetMachines();
            },
            error: function (error) {
                console.log(error);
            }

        });
    });
});

function CloseCreateModal() {

    $('#machineAddressNew').val('');
    $('#machineDescriptionNew').val('');
    $('#alertMachineExists').hide();
}

function AddMachine() {
    $('#machineCreateModal').modal('show');
}

$(function () {
    $('#btnAddMachineModal').click(function () {
        $('#alertMachineExists').hide();
        var url = 'addMachine';
        console.log(url);
        requestData = {
            address: $('#machineAddressNew').val(),
            description: $('#machineDescriptionNew').val(),
            van_number: $('#vanNumberNew').val()
        };

        $.ajax({
            url: url,
            method: 'POST',
            data: requestData,
            success: function (result) {
                console.log(result)
                if (!('error' in result)) {
                    $('#machineCreateModal').modal('hide');

                    GetMachines();
                } else {
                    console.log('exists')
                    $('#alertMachineExists').text(result.error);
                    $('#alertMachineExists').show();

                }
            },
            error: function (error) {
                console.log(error);
            }

        });
    });
});

$(function () {
    $('#btnCloseAddMachineModal').click(function () {
        CloseCreateModal();
    });
});