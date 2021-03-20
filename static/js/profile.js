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

function clearFields() {
    // 
    $('#currentPassword').val('');
    $('#newPassword').val('');
    $('#confirmPassword').val('');
}

function clearAlert() {
    $('#alertUserMain').hide();
}

function updatePassword(password, newPassword) {
    clearAlert();
    requestData = { password: password, newPassword: newPassword };
    var objectConstructor = ({}).constructor;

    $.ajax({
        url: 'api/updatePassword',
        method: 'POST',
        data: requestData,
        success: function (result) {
            console.log(result)
            if (!(result.constructor === objectConstructor)) {
                location.reload();
                return;
            }

            if (!('error' in result)) {
                showSuccessAlert(result.msg);
                location.reload();
                return;
            } else {
                showDangerAlert(result.error);
            }
            clearFields();
        },
        error: function (error) {
            console.log(error);
            showDangerAlert(error.error);
            clearFields();
        }

    });
}

$(function () {
    $('#btnUpdatePassword').click(function () {
        var password = $('#currentPassword').val();
        var newPassword = $('#newPassword').val();
        var confirmPassword = $('#confirmPassword').val();

        if (password == '' || newPassword == '' || confirmPassword == '') {
            showDangerAlert('All fields are required');
            clearFields();
        } else if (newPassword != confirmPassword) {
            showDangerAlert('New passwords don\'t match');
            clearFields();
        } else {
            updatePassword(password, newPassword);
        }
    });
});