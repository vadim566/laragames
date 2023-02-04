function showMessage(message, contentID, valType, timeout)
{
    $('#annotationError').css("display", "");
    $('.ErrorMsg').html(message);
    setTimeout(function() {
        $('.ErrorMsg').html("");
        $('#annotationError').css("display", "none");

    }, timeout);
}

function saveMultiWordAnnotation(sendMode)
{
    $("#task").val("saveMultiWordAnnotation");
    var data = $('#MultiWordAnnotationForm').serialize();

    showLoading('#dataAnnotationDiv');

    $.ajax({
        url: "../data/MultiWordExpressions.data.php",
        type: "post",
        data: data ,
        success: function (response) {
            hideLoading('#dataAnnotationDiv');
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[0].resultMsg;
            var responseID =  reqResponse[0].id;
            var responseType =  reqResponse[0].type;

            if (responseMsg.indexOf("DataIsNOTSavedForItems") != -1)
            {
                showMessage("Not saved", responseID, responseType, 3000);
            }
            if (responseMsg.indexOf("FinalCopyFailed") != -1)
            {
                showMessage("Not copied to final destination!", responseID, responseType, 3000);
            }
            else if (responseMsg.indexOf("DataIsSavedForItems") != -1)
            {
                showMessage("Saved successfully", responseID, responseType, 3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('NewLARAContent.php?Q0=' + $("#ContentID").val() + '&activeTab=1');
                else
                    reloadOnSubmitData();
            }
            else if (responseMsg.indexOf("FailedToGenerateCsv") != -1)
            {
                showMessage("Failed to generate csv file to update.", responseID, responseType, 3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('NewLARAContent.php?Q0=' + $("#ContentID").val() + '&activeTab=1');
            }
            else if (responseMsg.indexOf("FailedToMergeCsv") != -1)
            {
                showMessage("Failed to merge csv files together.", responseID, responseType, 3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('NewLARAContent.php?Q0=' + $("#ContentID").val() + '&activeTab=1');
            }
            else
            {
                showMessage("Something goes wrong!.", -1, '', 3000);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#dataAnnotationDiv');
            console.log(textStatus, errorThrown);
        }
    });
}

function goToMultiWordPage(pageNo, checkOnSubmit)
{
    if(checkOnSubmit)
    {
        if($('#mweStatusString').val())
        {
            var mweOnLoad = $('#mweStatusString').val();
            var mweOnSubmit = "";
            $('input[type="radio"]:checked').each(function(){
                if($(this).val() == 'mwe_not_okay')
                    mweOnSubmit = mweOnSubmit + "1**";
                else if($(this).val() == 'mwe_okay')
                    mweOnSubmit = mweOnSubmit + "2**";
                else if($(this).val() == 'mwe_status_unknown')
                    mweOnSubmit = mweOnSubmit + "3**";
            });
            if(mweOnLoad != mweOnSubmit)
            {
                if(confirm("Save before proceeding?"))
                {
                    saveMultiWordAnnotation("JustSave");
                }
            }
        }
    }

    $("#task").val("loadMultiWordPage");
    var data = { task: $('#task').val(), contentID :  $('#ContentID').val(),
                 justNote : $('#JustNote').val(), pageToLoad : pageNo};
    $.ajax({
        url         : '../data/MultiWordExpressions.data.php',
        data        : data,
        type        : 'GET',
        contentType : 'application/json; charset=utf-8',

        success: function (response) {
            $("#tableInfo").html( response);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(textStatus, errorThrown);
            alert("Something is wrong here.");
        }
    });
}

function reloadOnSubmitData()
{
    if($('#mweStatusString').val())
    {
        var mweOnLoad = $('#mweStatusString').val();
        var submittedStatus = "";
        $('input[type="text"].mweStatusString').each(function(){
            submittedStatus = submittedStatus +  $(this).val() + "**" ;
        });
        $('#mweStatusString').val(submittedStatus);
     }
}