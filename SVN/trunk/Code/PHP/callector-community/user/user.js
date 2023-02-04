function save_user_setting()
{
    var responseMapping = {};
    responseMapping["Succeed"] = "The changes to your profile have been saved.";
    responseMapping["Failure"] = "The changes to your profile have NOT been saved.";

    var form = $('#UserProfileForm');
    var formdata = false;
    if (window.FormData){
        formdata = new FormData(form[0]);
    }
    var data = formdata ? formdata : form.serialize();
    $.ajax({
        url         : 'user.data.php',
        data        : data,
        cache       : false,
        contentType : false,
        processData : false,
        type        : 'POST',
        success: function (response) {
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[1];
            if (responseMsg.indexOf("Succeed") != -1)
                $("#saveSettingResponseMsg").text(responseMapping["Succeed"]);
            else if (responseMsg.indexOf("Failure") != -1)
                $("#saveSettingResponseMsg").text(responseMapping["Failure"]);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, errorThrown);
        }
    });
}

function save_picture(formName)
{
    var form = $(formName);
    var formdata = false;
    if (window.FormData){
        formdata = new FormData(form[0]);
    }
    var data = formdata ? formdata : form.serialize();

    $.ajax({
        url         : 'user.data.php',
        data        : data,
        cache       : false,
        contentType : false,
        processData : false,
        type        : 'POST',
        success: function (response) {
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[1];
            if (responseMsg.indexOf("Succeed") != -1)
                location.reload();
            else if (responseMsg.indexOf("Failure") != -1)
                alert("not done");
            },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, errorThrown);
        }
    });
}
