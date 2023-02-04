$(document).ready(function()
{
    $("#LoginForm").submit(function(e)
    {
        e.preventDefault(); // avoid to execute the actual submit of the form.
        var form = $(this);
        var url = form.attr('action');
        var type = form.attr('method');
        var data = form.serialize()  + "&task=user_login";

        if($("#UserNameEmail").val().length === 0 || $("#UserPassword").val().length === 0)
        {
            $('#loginResponseMsg').text("** Please insert login information.");
            hide_error("#loginResponseMsg", 2000);
           return;
        }

        $.ajax({
            type: type,
            url: url,
            data: data, // serializes the form's elements.
            success: function(response) {
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[1];
                if (responseMsg.indexOf("UserNotFound") != -1)
                    $('#loginResponseMsg').text("User not found.");
                else if (responseMsg.indexOf("WrongPassword") != -1)
                    $('#loginResponseMsg').text("Password is wrong.");
                else if (responseMsg.indexOf("LoginNow") != -1)
                    // this will be changed to window.location = "user/log_in.php" later;
                    window.location = "lara-content/contents.php";
            }
        });
    });
});

function hide_error(divID, timeout)
{
    setTimeout(function() {
        $(divID).text("");
    }, timeout);
}

function send_sign_up_form()
{
    if(validate_sign_up_form())
    {
        var data = $('#SignupForm').serialize();
        data += "&task=user_sign_up";

        $.ajax({
            url: "account/account.data.php",
            type: "post",
            data: data ,
            success: function (response) {
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[1];
                if (responseMsg.indexOf("DuplicateUsername") != -1)
                    $('#signupResponseMsg').text("This Username is taken.");
                else if (responseMsg.indexOf("DuplicateEmail") != -1)
                    $('#signupResponseMsg').text("An account exists for this Email.");
                else if (responseMsg.indexOf("NoDuplication") != -1)
                    $('#signupResponseMsg').text("You can now sign in.");
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
            }
        });

    }
}

function validate_sign_up_form()
{
    var nameReg = /^[A-Za-z]+$/;
    var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
    var passwordReg = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}/;

    var UserName = $('#UserName').val();
    var Email = $('#Email').val();
    var Password = $('#Password').val();
    var PwdRepeat = $('#PwdRepeat').val();

    $('.sign_up_error').text('');

    if(UserName == "")
    {
        $('#UserNameMsg').text('Please enter a username.');
        return false;
    }
    else if(!nameReg.test(UserName))
    {
        $('#UserNameMsg').text('Letters only.');
        return false;
    }

    if(Email == "")
    {
        $('#EmailMsg').text('Please enter an email.');
        return false;
    }
    else if(!emailReg.test(Email))
    {
        $('#EmailMsg').text('Please enter a valid email address');
        return false;
    }

    if(Password == "")
    {
        $('#PasswordMsg').text('Please enter the password');
        return false;
    }
    else if(!passwordReg.test(Password))
    {
        $('#PasswordMsg').text('Minimum eight characters, at least one letter and one number');
        return false;
    }

    if(PwdRepeat == "")
    {
        $('#PwdRepeatMsg').text('Please re-enter the password.');
        return false;
    }
    else if(Password != PwdRepeat)
    {
        $('#PwdRepeatMsg').text('Password and Repeat Password are not the same.');
        return false;
    }

    return true;
}