function showMessage(message, contentID, valType, timeout)
{
    $('#translationError').css("display", "");
    $('.ErrorMsg').html(message);
    setTimeout(function() {
        $('.ErrorMsg').html("");
        $('#translationError').css("display", "none");

    }, timeout);
}

function sendTranslation(sendMode, saveFunction)
{
    var data = $('#dataTranslationForm').serialize();
    data += "&task=" + saveFunction;

    showLoading('#dataTranslationDiv');

    $.ajax({
        url: "../data/SegmentsAndWords.data.php",
        type: "post",
        data: data ,
        success: function (response) {
            hideLoading('#dataTranslationDiv');
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
                    $("#mainContentDIV").load('NewLARAContent.php?Q0=' + $("#ContentID").val() + '&mode=' + $("#EditMode").val() + '&activeTab=1');
                else
                    reloadOnSubmitData();
            }
            else if (responseMsg.indexOf("FailedToGenerateCsv") != -1)
            {
                showMessage("Failed to generate csv file to update.", responseID, responseType, 3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('NewLARAContent.php?Q0=' + $("#ContentID").val() + '&mode=' + $("#EditMode").val() + '&activeTab=1');
            }
            else if (responseMsg.indexOf("FailedToMergeCsv") != -1)
            {
                showMessage("Failed to merge csv files together.", responseID, responseType, 3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('NewLARAContent.php?Q0=' + $("#ContentID").val() + '&mode=' + $("#EditMode").val() + '&activeTab=1');
            }
            else
            {
                showMessage("Something goes wrong!.", -1, '', 3000);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#dataTranslationDiv');
            console.log(textStatus, errorThrown);
        }
    });
}

function exitWithoutSaving()
{
    $("#mainContentDIV").load('NewLARAContent.php?Q0=' + $("#ContentID").val() + '&mode=' + $("#EditMode").val() + '&activeTab=1');
}

function goToLemmaPage(pageNo, checkOnSubmit)
{

    var mode = $("#EditMode").val();
    if(checkOnSubmit && mode != "readOnly")
    {
        if($('#l1String').val())
        {
            var l1OnLoad = $('#l1String').val();
            var l1OnSubmit = "";
            $('input[type="text"].l1Input').each(function(){
                l1OnSubmit = l1OnSubmit + $(this).val() + "**";
            });
            if(l1OnLoad != l1OnSubmit)
            {
                if(confirm("Save before proceeding?"))
                {
                    sendTranslation("JustSave", "saveLemma");
                }
            }
        }

        var noteOnLoad = $('#noteString').val();
        var noteOnSubmit = "";
        $('input[type="text"].noteInput').each(function(){
            noteOnSubmit = noteOnSubmit +  $(this).val() + "**" ;
        });
        if(noteOnLoad != noteOnSubmit)
        {
            if(confirm("Save before proceeding?"))
            {
                sendTranslation("JustSave", "saveNote");
            }
        }
    }

    var data = { task: $('#task').val(), contentID :  $('#ContentID').val(),
                 justNote : $('#JustNote').val(), pageToLoad : pageNo , mode : mode};
    $.ajax({
        url         : '../data/SegmentsAndWords.data.php',
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

function goToSegmentPage(pageNo, checkOnSubmit)
{
    var mode = $("#EditMode").val();
    if(checkOnSubmit && mode != "readOnly")
    {
        if($('#l1String').val())
        {
            var l1OnLoad = $('#l1String').val();
            var l1OnSubmit = "";
            $('input[type="text"].l1Input').each(function(){
                l1OnSubmit = l1OnSubmit + $(this).val() + "**";
            });
            if(l1OnLoad != l1OnSubmit)
            {
                if(confirm("Save before proceeding?"))
                {
                    sendTranslation("JustSave", "saveSegment");
                }
            }
        }
    }

    var data = { task: $('#task').val(), contentID :  $('#ContentID').val(),
                 pageToLoad : pageNo, mode : mode};
    $.ajax({
        url         : '../data/SegmentsAndWords.data.php',
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

function goToTypePage(pageNo, checkOnSubmit)
{
    var mode = $("#EditMode").val();
    if(checkOnSubmit && mode != "readOnly")
    {
        if($('#l1String').val())
        {
            var l1OnLoad = $('#l1String').val();
            var l1OnSubmit = "";
            $('input[type="text"].l1Input').each(function(){
                l1OnSubmit = l1OnSubmit + $(this).val() + "**";
            });
            if(l1OnLoad != l1OnSubmit)
            {
                if(confirm("Save before proceeding?"))
                {
                    sendTranslation("JustSave", "saveType");
                }
            }
        }
    }

    var data = { task: $('#task').val(), contentID :  $('#ContentID').val(),
        pageToLoad : pageNo, mode : mode};
    $.ajax({
        url         : '../data/SegmentsAndWords.data.php',
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

function goToTokenPage(pageNo, checkOnSubmit)
{
    var mode = $("#EditMode").val();
    if(checkOnSubmit && mode != "readOnly")
    {
        if($('#l1String').val())
        {
            var l1OnLoad = $('#l1String').val();
            var l1OnSubmit = "";
            $('input[type="text"].l1Input').each(function(){
                l1OnSubmit = l1OnSubmit + $(this).val() + "**";
            });
            if(l1OnLoad != l1OnSubmit)
            {
                if(confirm("Save before proceeding?"))
                {
                    sendTranslation("JustSave", "saveToken");
                }
            }
        }
    }

    var data = { task: $('#task').val(), contentID :  $('#ContentID').val(),
        pageToLoad : pageNo, mode : mode};
    $.ajax({
        url         : '../data/SegmentsAndWords.data.php',
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

function reloadOnSubmitData() {

    if($('#noteString').val())
    {
        var noteOnLoad = $('#noteString').val();
        var submittedNote = "";
        $('input[type="text"].noteInput').each(function(){
            submittedNote = submittedNote +  $(this).val() + "**" ;
        });
        $('#noteString').val(submittedNote);
    }
    if($('#l1String').val())
    {
        var l1OnLoad = $('#l1String').val();
        var submittedL1 = "";
        $('input[type="text"].l1String').each(function(){
            submittedL1 = submittedL1 +  $(this).val() + "**" ;
        });
        $('#l1String').val(submittedL1);
     }
}