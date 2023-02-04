$(document).ready(function()
{
    $("#LoginForm").submit(function(e)
    {
        e.preventDefault(); // avoid to execute the actual submit of the form.

        var form = $(this);
        var url = form.attr('action');
        var type = form.attr('method');
        var data = form.serialize()  + "&task=userLogin";

        $.ajax({
            type: type,
            url: url,
            data: data, // serializes the form's elements.
            success: function(response) {
                if (response.indexOf("UserNotFound") != -1)
                {
                    $('#errorText').text("User not found.");
                    $("#errorDiv").fadeTo(2000, 500).slideUp(500, function() {
                        $("#errorDiv").slideUp(500);
                    });

                }
                else if (response.indexOf("WrongPassword") != -1)
                {
                    $('#errorText').text("Password is wrong.");
                    $("#errorDiv").fadeTo(2000, 500).slideUp(500, function() {
                        $("#errorDiv").slideUp(500);
                    });
                }
                else if (response.indexOf("LoginNow") != -1)
                {
                    window.location = "../view/HomePage.php";
                }
            }
        });
    });

    $("#ResetPassForm").submit(function(e)
    {
        e.preventDefault(); // avoid to execute the actual submit of the form.

        var form = $(this);
        var url = form.attr('action');
        var type = form.attr('method');
        var data = form.serialize()  + "&task=ResetPasswordRequest";

        $.ajax({
            type: type,
            url: url,
            data: data, // serializes the form's elements.
            success: function(response) {
                if (response.indexOf("succeed") != -1)
                {
                    $('#successText').text("Check your email.");
                    $("#successDiv").fadeTo(2000, 500).slideUp(500, function() {
                        $("#successDiv").slideUp(500);
                    });
                }
                else if (response.indexOf("emailNotExists") != -1)
                {
                    $('#dangerText').text("No user is registered in lara under this email");
                    $("#dangerDiv").fadeTo(2000, 500).slideUp(500, function() {
                        $("#dangerDiv").slideUp(500);
                    });
                }
                else if (response.indexOf("failure") != -1)
                {
                    $('#dangerText').text("Could not send email.");
                    $("#dangerDiv").fadeTo(2000, 500).slideUp(500, function() {
                        $("#dangerDiv").slideUp(500);
                    });
                }
            }
        });
    });

    $("#NewPassForm").submit(function(e)
    {
        e.preventDefault(); // avoid to execute the actual submit of the form.

        if(validateNewPassForm()) {
            var form = $(this);
            var url = form.attr('action');
            var type = form.attr('method');
            var data = form.serialize() + "&task=UpdatePassword";

            $.ajax({
                type: type,
                url: url,
                data: data, // serializes the form's elements.
                success: function (response) {
                    if (response.indexOf("LoginWithNewPass") != -1) {
                        $('#successText').text("You can now log in with your new password.");
                        $("#successDiv").fadeTo(2000, 500).slideUp(500, function () {
                            $("#successDiv").slideUp(500);
                        });

                    } else if (response.indexOf("NoResetRequest") != -1) {
                        $('#dangerText').text("The reset password link does not exist.");
                        $("#dangerDiv").fadeTo(2000, 500).slideUp(500, function () {
                            $("#dangerDiv").slideUp(500);
                        });
                    } else if (response.indexOf("NotValidLink") != -1) {
                        $('#dangerText').text("The reset password link is not valid.");
                        $("#dangerDiv").fadeTo(2000, 500).slideUp(500, function () {
                            $("#dangerDiv").slideUp(500);
                        });
                    }
                }
            });
        }
    });

});


function SendSignupForm()
{
    if(validateSignupForm())
    {
        var data = $('#SignupForm').serialize();
        data += "&task=userSignUp";

        $.ajax({
            url: "../data/User.data.php",
            type: "post",
            data: data ,
            success: function (response) {
                if (response.indexOf("DuplicateUsername") != -1)
                {
                    $('#signupResponseMsg').text("This Username is taken.");
                    hideError("#signupResponseMsg", 5000);
                }
                else if (response.indexOf("DuplicateEmail") != -1)
                {
                    $('#signupResponseMsg').text("An account exists for this Email.");
                    hideError("#signupResponseMsg", 5000);
                }
                else if (response.indexOf("NoDuplication") != -1)
                {
                    $('#signupResponseMsg').text("You can now sign in.");                                    }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
            }
        });

    }
}

function validateSignupForm()
{

    var nameReg = /^[A-Za-z]+$/;
    var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
    var passwordReg = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}/;

    var UserName = $('#UserName').val();
    var Email = $('#Email').val();
    var Password = $('#Password').val();
    var PwdRepeat = $('#PwdRepeat').val();


    var inputVal = new Array(UserName, Email, Password, PwdRepeat);

    var inputMessage = new Array("name", "email address", "password", "repeat password");

    $('.signuperror').remove();

    if(inputVal[0] == "")
    {
        $('#UserName').after('<p class="signuperror"> Please enter your ' + inputMessage[0] + '</p>');
        return false;
    }
    else if(!nameReg.test(UserName))
    {
        $('#UserName').after('<p class="signuperror"> Letters only</p>');
        return false;
    }

    if(inputVal[1] == "")
    {
        $('#Email').after('<p class="signuperror"> Please enter your ' + inputMessage[1] + '</p>');
        return false;
    }
    else if(!emailReg.test(Email))
    {
        $('#Email').after('<p class="signuperror"> Please enter a valid email address</p>');
        return false;
    }

    if(inputVal[2] == "")
    {
        $('#Password').after('<p class="signuperror"> Please enter your ' + inputMessage[2] + '</p>');
        return false;
    }
    else if(!passwordReg.test(Password))
    {
        $('#Password').after('<p class="signuperror"> Minimum eight characters,\n  at least one letter and one number</p>');
        return false;
    }

    if(inputVal[3] == "")
    {
        $('#PwdRepeat').after('<p class="signuperror"> Please enter your ' + inputMessage[3] + '</p>');
        return false;
    }
    else if(Password != PwdRepeat)
    {
        $('#PwdRepeat').after('<p class="signuperror"> Password and Repeat Password are not the same </p>');
        return false;
    }

    return true;
}

function UpdatePassword()
{
    if(validateNewPassForm())
    {
        var data = $('#NewPassForm').serialize();
        data += "&task=UpdatePassword";

        $.ajax({
            url: "../data/User.data.php",
            type: "post",
            data: data ,
            success: function (response) {
                if (response.indexOf("NoResetRequest") != -1)
                {
                    $('#rpMsg').text("The reset password link does not exist.");
                }
                else if (response.indexOf("NotValidLink") != -1)
                {
                    $('#rpMsg').text("The reset password link is not valid.");
                }
                else if (response.indexOf("LoginWithNewPass") != -1)
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

function validateNewPassForm()
{
    var passwordReg = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}/;
    var Password = $('#Password').val();
    var PwdRepeat = $('#PwdRepeat').val();

    $('.signuperror').remove();

    if(!passwordReg.test(Password))
    {
        $('#dangerText').text("Minimum eight characters,\n  at least one letter and one number");
        $("#dangerDiv").fadeTo(2000, 500).slideUp(500, function() {
            $("#dangerDiv").slideUp(500);
        });
        return false;
    }

    if(Password != PwdRepeat)
    {
        $('#dangerText').text("Password and Repeat Password are not the same.");
        $("#dangerDiv").fadeTo(2000, 500).slideUp(500, function() {
            $("#dangerDiv").slideUp(500);
        });
        return false;
    }

    return true;
}