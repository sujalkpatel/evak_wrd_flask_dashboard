var userId, userIdToDelete, userName;

var userEditModal = document.getElementById('userEditModal');
var userCreateModal = document.getElementById('userCreateModal');
var passwordResetModal = document.getElementById('passwordResetModal');

userEditModal.addEventListener('hide.bs.modal', function (event) {
    closeEditModal();
});
userCreateModal.addEventListener('hide.bs.modal', function (event) {
    closeCreateModal();
});
passwordResetModal.addEventListener('hide.bs.modal', function (event) {
    closePasswordResetModal();
});

function showSuccessAlert(message) {
    var alertHtml = "";
    alertHtml += "<div class='alert alert-success alert-dismissible fade show' role='alert'>";
    alertHtml += message;
    alertHtml += "  <button type='button' class='btn-close' data-bs-dismiss='alert' aria-label='Close'></button>";
    alertHtml += "</div>";

    // console.log(alertHtml);
    $('#alertUserMain').html(alertHtml);
    $('#alertUserMain').show();
}
function showDangerAlert(message) {
    var alertHtml = "";
    alertHtml += "<div class='alert alert-danger alert-dismissible fade show' role='alert'>";
    alertHtml += message;
    alertHtml += "  <button type='button' class='btn-close' data-bs-dismiss='alert' aria-label='Close'></button>";
    alertHtml += "</div>";

    // console.log(alertHtml);
    $('#alertUserMain').html(alertHtml);
    $('#alertUserMain').show();
}

function renderUserRows(users) {
    var resultHtml = "", bgColor = "";

    for (var i = 0; i < users.length; i++) {
        bgColor = "";
        if (users[i].admin) {
            bgColor = "class='text-danger'";
        }
        resultHtml += "<tr " + bgColor + ">";
        resultHtml += "    <th scope='row'>" + users[i].id + "</th>";
        resultHtml += "    <td>" + users[i].name + "</td>";
        resultHtml += "    <td>" + users[i].email + "</td>";
        resultHtml += "    <td class='text-center'>";
        resultHtml += "        <button type='button' class='btn btn-outline-info' user-id=" + users[i].id + " onclick='editUser(this)' ";
        resultHtml += "                data-bs-toggle='tooltip' data-bs-placement='top' title='Edit " + users[i].name + "'><i class='bi bi-pencil-square'></i>";
        resultHtml += "        </button>";
        resultHtml += "        <button type='button' class='btn btn-outline-warning' user-id=" + users[i].id + " user-name='" + users[i].name + "' ";
        resultHtml += "                onclick='resetPassword(this)' data-bs-toggle='tooltip' data-bs-placement='top' title='Reset Password for " + users[i].name + "'>";
        resultHtml += "                <i class='bi bi-arrow-clockwise'></i></button>";
        resultHtml += "        <button type='button' class='btn btn-outline-danger' user-id=" + users[i].id + " user-name='" + users[i].name + "' ";
        resultHtml += "                onclick='deleteUser(this)' data-bs-toggle='tooltip' data-bs-placement='top' title='Delete " + users[i].name + "'>";
        resultHtml += "                <i class='bi bi-trash'></i></button>";
        resultHtml += "    </td>";
        resultHtml += "</tr>";
    }

    return resultHtml;
}

function getUsers() {
    var objectConstructor = ({}).constructor;
    $.ajax({
        url: 'api/user',
        method: 'GET',
        success: function (result) {
            // console.log(result);
            if (!(result.constructor === objectConstructor)) {
                location.reload();
                return;
            }

            $('#userList').empty();

            var userRowHtml = renderUserRows(result.users);
            $('#userList').html(userRowHtml);
        },
        error: function (error) {
            console.log(error);
        }

    });
}

$(function () {
    getUsers();
});

function closeEditModal() {
    $('#userName').val('');
    $('#userEmail').val('');
    $('#checkAdmin').prop('checked', false);
    $('#alertEditUser').hide();
}

function editUser(userRow) {
    userId = $(userRow).attr('user-id');
    console.log(userId);
    var url = 'api/user/';
    url = url.concat(String(userId));
    console.log(url);

    $.ajax({
        url: url,
        method: 'GET',
        success: function (user) {
            console.log(user)
            $('#userName').val(user.name);
            $('#userEmail').val(user.email);
            if (user.admin) {
                $('#checkAdmin').prop('checked', true);
            }
            $('#userEditModal').modal('show');
        },
        error: function (error) {
            console.log(error);
        }
    });
}

$(function () {
    $('#btnUpdateUserModal').click(function () {
        console.log(userId);
        var url = 'api/user/';
        url = url.concat(String(userId));
        var adminStatus = 0;
        if ($('#checkAdmin').prop('checked')) {
            adminStatus = 1;
        }
        requestData = { name: $('#userName').val(), email: $('#userEmail').val(), admin: adminStatus };
        // console.log(requestData);

        $.ajax({
            url: url,
            method: 'PUT',
            data: requestData,
            success: function (result) {
                console.log(result)
                if (!('error' in result)) {
                    $('#userEditModal').modal('hide');
                    getUsers();
                } else {
                    $('#alertEditUser').text(result.error);
                    $('#alertEditUser').show();
                }
            },
            error: function (error) {
                console.log(error);
            }

        });
    });
});

function closePasswordResetModal() {
    $('#resetPassword').val('');
    $('#alertPasswordReset').hide();
}

function resetPassword(userRow) {
    userId = $(userRow).attr('user-id');
    userName = $(userRow).attr('user-name');

    var label = 'Reset password for ' + userName;
    $('#passwordResetModalLabel').html(label);

    $('#passwordResetModal').modal('show');
}

$(function () {
    $('#btnResetPasswordModal').click(function () {
        console.log(userId);
        var url = 'api/resetPassword/';
        url = url.concat(String(userId));

        requestData = { password: $('#resetPassword').val() };
        // console.log(requestData);

        $.ajax({
            url: url,
            method: 'POST',
            data: requestData,
            success: function (result) {
                console.log(result)
                if (!('error' in result)) {
                    $('#passwordResetModal').modal('hide');
                    var label = result.msg + ' for ' + userName + '.';
                    showSuccessAlert(label);
                    getUsers();
                } else {
                    showDangerAlert(result.error);
                }
            },
            error: function (error) {
                console.log(error);
            }

        });
    });
});

function deleteUser(userRow) {
    userIdToDelete = $(userRow).attr('user-id');
    userName = $(userRow).attr('user-name');

    $('#alertUserDelete').text('');
    $('#alertUserDelete').hide();
    $('#deleteModalLabel').empty();
    var label = 'Are you sure to delete ' + userName + '?';
    $('#deleteModalLabel').html(label);

    $('#userDeleteModal').modal('show');
}

$(function () {
    $('#btnDeleteUserModal').click(function () {
        console.log(userIdToDelete);
        var url = 'api/user/';
        url = url.concat(String(userIdToDelete));
        console.log(url);

        $.ajax({
            url: url,
            method: 'DELETE',
            success: function (result) {
                console.log(result)
                if (!('error' in result)) {
                    $('#userDeleteModal').modal('hide');
                    getUsers();
                } else {
                    $('#alertUserDelete').text(result.error);
                    $('#alertUserDelete').show();
                }
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
});

function closeCreateModal() {
    $('#userNameNew').val('');
    $('#userPasswordNew').val('');
    $('#userEmailNew').val('');
    $('#checkAdminNew').prop('checked', false);
    $('#alertUserExists').hide();
}

function addUser() {
    $('#userCreateModal').modal('show');
}

$(function () {
    $('#btnAddUserModal').click(function () {
        if ($('#userNameNew').val() == "" || $('#userPasswordNew').val() == "" || $('#userEmailNew').val() == "") {
            $('#alertUserExists').text("All fields are required.");
            $('#alertUserExists').show();

            return false;
        }

        $('#alertUserExists').hide();
        var url = 'api/user';

        var adminStatus = 0;
        if ($('#checkAdminNew').prop('checked')) {
            adminStatus = 1;
        }
        requestData = {
            name: $('#userNameNew').val(),
            password: $('#userPasswordNew').val(),
            email: $('#userEmailNew').val(),
            admin: adminStatus
        };
        console.log(requestData);

        $.ajax({
            url: url,
            method: 'POST',
            data: requestData,
            success: function (result) {
                console.log(result)
                if (!('error' in result)) {
                    $('#userCreateModal').modal('hide');
                    getUsers();
                } else {
                    console.log('exists')
                    $('#alertUserExists').text(result.error);
                    $('#alertUserExists').show();

                }
            },
            error: function (error) {
                console.log(error);
            }

        });
    });
});