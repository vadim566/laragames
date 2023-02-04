function send_email_to_creator()
{
    var form = $('#SendEmailToCreator');
    var formdata = false;
    if (window.FormData){
        formdata = new FormData(form[0]);
    }
    var data = formdata ? formdata : form.serialize();

    $.ajax({
        url         : 'lara_content.data.php',
        data        : data,
        cache       : false,
        contentType : false,
        processData : false,
        type        : 'POST',
        success: function (response) {
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[1];
            if (responseMsg.indexOf("succeed") != -1)
            {
                $("#email-to-creator-box").removeClass("open");
                $(".wrapper").removeClass("overlay");
            }
            else if (responseMsg.indexOf("failure") != -1)
                alert("not done");
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, errorThrown);
        }
    });
}

function open_email_to_creator_box(contentID) {
    $("#email-to-creator-box").addClass("open");
    $(".wrapper").addClass("overlay");
    $("#ContentID").val(contentID);
    return false;
}

$(".close-box").on("click", function(){
    $("#email-to-creator-box").removeClass("open");
    $(".wrapper").removeClass("overlay");
    return false;
});

function save_content_picture(formName)
{
    var form = $(formName);
    var formdata = false;
    if (window.FormData){
        formdata = new FormData(form[0]);
    }
    var data = formdata ? formdata : form.serialize();

    $.ajax({
        url         : 'lara_content.data.php',
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

function filter_data()
{
    $("#content-spinner").css("display" ,"block");

    var form = $('#ContentSearchForm');
    var formdata = false;
    if (window.FormData){
        formdata = new FormData(form[0]);
    }
    var data = formdata ? formdata : form.serialize();

    $.ajax({
        url         : 'lara_content.data.php',
        data        : data,
        cache       : false,
        contentType : false,
        processData : false,
        type        : 'POST',
        success: function (response) {
            $("#content-spinner").css("display" ,"none");
            $('.companies-list').html(response);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            $("#content-spinner").css("display" ,"none");
            console.log(textStatus, errorThrown);
        }
    });
}

function play_segment_voice(soundfile) {
    document.getElementById("audio_container").innerHTML=
        "<audio id='audioFile' src='https://regulus.unige.ch:448/LdtRecordingToolInput/" + soundfile +"'></audio>";
    var audio = document.getElementById("audioFile");
    audio.play();
}

function manage_translation(translationSpan) {
    if(document.getElementById(translationSpan).style.display == "none")
        document.getElementById(translationSpan).style.display = ""
    else
        document.getElementById(translationSpan).style.display = "none"
}

$('#FullTextVisitTag').click(function(e) {
    e.preventDefault();

    var data = { task: "content_web_page_visit", contentID : $("#ContentID").val()};

    $.ajax({
        type: "POST",
        url : 'lara_content.data.php',
        data: data,
        success: function(response) {
            var href = $('#FullTextVisitTag').attr('href');
            window.open(href, '_blank');

       //     window.location = href;
        }
    });

});

function save_comment()
{
    var form = $("#CommentForm");
    var formdata = false;
    if (window.FormData){
        formdata = new FormData(form[0]);
    }
    var data = formdata ? formdata : form.serialize();

    $.ajax({
        url         : 'lara_content.data.php',
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
