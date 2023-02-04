function reset_password_request()
{
    if(validate_reset_pass_form())
    {
        var data = $('#ResetPassForm').serialize();
        data += "&task=reset_password_request";

        $.ajax({
            url: "account.data.php",
            type: "post",
            data: data ,
            success: function (response) {
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[1];
                if (responseMsg.indexOf("succeed") != -1)
                {
                    $('#rpMsg').text("Check your email.");
                }
                else if (responseMsg.indexOf("emailNotExists") != -1)
                {
                    $('#rpMsg').text("No user is registered in lara under this email");
                }
                else if (responseMsg.indexOf("failure") != -1)
                {
                    $('#rpMsg').text("Could not send email.");
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                $('#rpMsg').text("Something is wrong here.");
                console.log(textStatus, errorThrown);
            }
        });
    }
}

function validate_reset_pass_form()
{
    var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
    var Email = $('#Email').val();

    $('.sign_up_error').remove();

    if(Email == "")
    {
        $('#rpMsg').text('Please enter your email address.');
        return false;
    }
    else if(!emailReg.test(Email))
    {
        $('#rpMsg').text('Please enter a valid email address');
        return false;
    }

    return true;
}

function update_password()
{
    if(validate_new_pass_form())
    {
        var data = $('#NewPassForm').serialize();
        data += "&task=update_password";

        $.ajax({
            url: "account.data.php",
            type: "post",
            data: data ,
            success: function (response) {
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[1];
                if (responseMsg.indexOf("NoResetRequest") != -1)
                {
                    $('#rpMsg').text("The reset password link does not exist.");
                }
                else if (responseMsg.indexOf("NotValidLink") != -1)
                {
                    $('#rpMsg').text("The reset password link is not valid.");
                }
                else if (responseMsg.indexOf("LoginWithNewPass") != -1)
                {
                    $('#rpMsg').text("You can now log in with your new password.");
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                $('#rpMsg').text("Something is wrong in updating password.");
                console.log(textStatus, errorThrown);
            }
        });
    }

}

function validate_new_pass_form()
{
    var passwordReg = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}/;
    var Password = $('#Password').val();
    var PwdRepeat = $('#PwdRepeat').val();

    $('.sign_up_error').remove();

    if(Password == "")
    {
        $('#rpMsg').text('Please enter a new password');
        return false;
    }
    else if(!passwordReg.test(Password))
    {
        $('#rpMsg').text('Minimum eight characters, at least one letter and one number');
        return false;
    }

    if(PwdRepeat == "")
    {
        $('#rpMsg').text('Please fill out repeat password.');
        return false;
    }
    else if(Password != PwdRepeat)
    {
        $('#rpMsg').text('Password and Repeat Password are not the same.');
        return false;
    }
    return true;
}