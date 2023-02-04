$(document).ready(function(){

    $("#SignUpText").click(function(){
        $("#mainContent").load("../view/Signup.html");
    });

    $("#ForgetPass").click(function(){
        $("#mainContent").load("../view/ResetPassword.html");
    });


    $("#LoginForm").submit(function(e) {

        e.preventDefault(); // avoid to execute the actual submit of the form.

        var form = $(this);
        var url = form.attr('action');
        var type = form.attr('method');
        var data = form.serialize()  + "&task=userLogin";


        if($("#UserNameEmail").val().length === 0 ||
            $("#UserPassword").val().length === 0) {
            $('#loginResponseMsg').text("Please insert your Email/Username and Password.");
            hideError("#loginResponseMsg", 2000);

           //alert("Please insert your Email/Username and Password.");
           return;
        }


        $.ajax({
            type: type,
            url: url,
            data: data, // serializes the form's elements.
            success: function(response) {
                if (response.indexOf("UserNotFound") != -1)
                {
                    $('#loginResponseMsg').text("User not found.");
                    hideError("#loginResponseMsg", 2000);

                }
                else if (response.indexOf("WrongPassword") != -1)
                {
                    $('#loginResponseMsg').text("Password is wrong.");
                    hideError("#loginResponseMsg", 2000);
                }
                else if (response.indexOf("LoginNow") != -1)
                {
                    window.location = "../view/HomePage.php";
                }
            }
        });


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

function hideError(divID, timeout) {

    setTimeout(function() {
        $(divID).text("");
    }, timeout);
}

function ResetPasswordRequest()
{
    if(validateResetPassForm())
    {
        var data = $('#ResetPassForm').serialize();
        data += "&task=ResetPasswordRequest";

        $.ajax({
            url: "../data/User.data.php",
            type: "post",
            data: data ,
            success: function (response) {
                if (response.indexOf("succeed") != -1)
                {
                    $('#rpMsg').text("Check your email.");
                }
                else if (response.indexOf("emailNotExists") != -1)
                {
                    $('#rpMsg').text("No user is registered in lara under this email");
                }
                else if (response.indexOf("failure") != -1)
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

function validateResetPassForm()
{

    var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
    var Email = $('#Email').val();

    $('.signuperror').remove();

    if(Email == "")
    {
        $('#Email').after('<p class="signuperror"> Please enter your email address</p>');
        return false;
    }
    else if(!emailReg.test(Email))
    {
        $('#Email').after('<p class="signuperror"> Please enter a valid email address</p>');
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

    if(Password == "")
    {
        $('#Password').after('<p class="signuperror"> Please enter a new password</p>');
        return false;
    }
    else if(!passwordReg.test(Password))
    {
        $('#Password').after('<p class="signuperror">Minimum eight characters,\n  at least one letter and one number</p>');
        return false;
    }

    if(PwdRepeat == "")
    {
        $('#PwdRepeat').after('<p class="signuperror"> Please fill out repeat password</p>');
        return false;
    }
    else if(Password != PwdRepeat)
    {
        $('#PwdRepeat').after('<p class="signuperror"> Password and Repeat Password are not the same </p>');
        return false;
    }

    return true;
}