$(document).ready(function () {
    $("#EvaluationForm").submit(function (event) {
        var form = $('#EvaluationForm');
        var formdata = false;
        if (window.FormData){
            formdata = new FormData(form[0]);
        }
        var data = formdata ? formdata : form.serialize();
        $.ajax({
            url         : 'Questionnaire.data.php',
            data        : data,
            cache       : false,
            contentType : false,
            processData : false,
            type        : 'POST',
            success: function (response) {
                window.location.href = "ThankYou.php?q0=" + $('#UserName').val() + "&q1=" + $('#QuestionnaireID').val();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
                alert("Something is wrong here");
            }
        });

        event.preventDefault();
    });


    $("#UserCommentsForm").submit(function (event) {
        var form = $('#UserCommentsForm');
        var formdata = false;
        if (window.FormData){
            formdata = new FormData(form[0]);
        }
        var data = formdata ? formdata : form.serialize();
        $.ajax({
            url         : 'Questionnaire.data.php',
            data        : data,
            cache       : false,
            contentType : false,
            processData : false,
            type        : 'POST',
            success: function (response) {
               window.location.href = "ThankYou.php";
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.log(textStatus, errorThrown);
                alert("Something is wrong here");
            }
        });

        event.preventDefault();
    });


});

function playSound(soundfile) {
    document.getElementById("audio_container").innerHTML=
        "<embed src='" + soundfile +"' autostart='true' loop='false' />";
}
function play(soundfile) {
    var audio = new Audio(soundfile);
    audio.play();
}