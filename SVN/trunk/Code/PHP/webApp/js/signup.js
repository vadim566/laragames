$(document).ready(function()
{
    var myInput = $('#Password')[0];
    var letter =  $('#letter')[0];
    var number =  $('#number')[0];
    var length =  $('#length')[0];

    myInput.onfocus = function() {
        document.getElementById("message").style.display = "block";
    }

    myInput.onblur = function() {
        document.getElementById("message").style.display = "none";
    }

    myInput.onkeyup = function() {
        // Validate letters
        var lowerCaseLetters = /[a-z]/g;
        var upperCaseLetters = /[A-Z]/g;

        if(myInput.value.match(lowerCaseLetters) ||myInput.value.match(upperCaseLetters) ) {
            letter.classList.remove("invalid");
            letter.classList.add("valid");
        } else {
            letter.classList.remove("valid");
            letter.classList.add("invalid");
        }

        // Validate numbers
        var numbers = /[0-9]/g;
        if(myInput.value.match(numbers)) {
            number.classList.remove("invalid");
            number.classList.add("valid");
        } else {
            number.classList.remove("valid");
            number.classList.add("invalid");
        }

        // Validate length
        if(myInput.value.length >= 8) {
            length.classList.remove("invalid");
            length.classList.add("valid");
        } else {
            length.classList.remove("valid");
            length.classList.add("invalid");
        }
    }

    $("#SignupForm").submit(function(event){
        event.preventDefault();
        submitForm();
    });


    function submitForm(){
        var data = $('#SignupForm').serialize();
        data += "&task=userSignUp";

        $.ajax({
            url: "../data/User.data.php",
            type: "post",
            data: data ,
            success: function (response) {
                if (response.indexOf("DuplicateUsername") != -1)
                {
                    $('#dangerText').text("This Username is taken.");
                    $("#dangerDiv").fadeTo(2000, 500).slideUp(500, function() {
                        $("#dangerDiv").slideUp(500);
                    });
                }
                else if (response.indexOf("DuplicateEmail") != -1)
                {
                    $('#dangerText').text("An account exists for this Email.");
                    $("#dangerDiv").fadeTo(2000, 500).slideUp(500, function() {
                        $("#dangerDiv").slideUp(500);
                    });
                }
                else if (response.indexOf("NoDuplication") != -1)
                {
                    $('#successText').text("You can now sign in.");
                    $("#successDiv").fadeTo(2000, 500).slideUp(500, function() {
                        $("#successDiv").slideUp(500);
                    });
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
            }
        });

    }

});

