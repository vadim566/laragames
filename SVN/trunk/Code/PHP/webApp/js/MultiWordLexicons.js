function onLoadLexicons()
{
    $('#TableOfLexicons').DataTable();
}

function loadLexiconData(lexiconPart, languageID)
{
    switch(lexiconPart) {
        case "classes":
            $("#mainContentDIV").load('LexiconClasses.php?languageID=' + languageID);
            break;
        case "mwes":
            $("#mainContentDIV").load('LexiconMWEs.php?languageID=' + languageID);
            break;
        case "transforms":
            $("#mainContentDIV").load('LexiconTransforms.php?languageID=' + languageID);
            break;
    }
}

function showMessage(message, timeout)
{
    $('#lexiconError').css("display", "");
    $('.ErrorMsg').html(message);
    setTimeout(function() {
        $('.ErrorMsg').html("");
        $('#lexiconError').css("display", "none");

    }, timeout);
}

function goToClassPage(pageNo, checkOnSubmit)
{
    if(checkOnSubmit)
    {
        if($('#memberString').val())
        {
            var memberOnLoad = $('#memberString').val();
            var memberOnSubmit = "";
            $('input[type="text"].memberInput').each(function(){
                memberOnSubmit = memberOnSubmit + $(this).val() + "**";
            });
            if(memberOnLoad != memberOnSubmit)
            {
                if(confirm("Save before proceeding?"))
                {
                    saveLexiconClass("JustSave");
                }
            }
        }
    }

    var data = { task: "loadLexiconClassesPage", languageID :  $('#LanguageID').val(), pageToLoad : pageNo};
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

function saveLexiconClass(sendMode)
{
    var data = $('#MultiWordLexiconForm').serialize();
    data += "&task=saveLexiconClasses";
    if(sendMode == "SaveAndExit")
        data += "&updateRep=yes";

    showLoading('#multiWordLexiconDiv');

    $.ajax({
        url: "../data/MultiWordExpressions.data.php",
        type: "post",
        data: data ,
        success: function (response) {
            hideLoading('#multiWordLexiconDiv');
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[0].resultMsg;
            var responseID =  reqResponse[0].id;

            if (responseMsg.indexOf("DataIsNOTSavedForItems") != -1)
            {
                showMessage("Not saved",3000);
            }
            if (responseMsg.indexOf("FinalCopyFailed") != -1)
            {
                showMessage("Not copied to final destination!", 3000);
            }
            else if (responseMsg.indexOf("DataIsSavedForItems") != -1)
            {
                showMessage("Saved successfully", 3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('MultiWordLexicons.php');
                else
                    reloadOnSubmitData();
            }
            else if (responseMsg.indexOf("FailedToGenerateCsv") != -1)
            {
                showMessage("Failed to generate csv file to update.",  3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('MultiWordLexicons.php');
            }
            else if (responseMsg.indexOf("FailedConvertingToTxtDefinition") != -1)
            {
                showMessage("Failed to generate the definition file.", 3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('MultiWordLexicons.php');
            }
            else
            {
                showMessage("Something goes wrong!.", 3000);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#multiWordLexiconDiv');
            console.log(textStatus, errorThrown);
        }
    });
}

function goToMwePage(pageNo, checkOnSubmit)
{
    if(checkOnSubmit)
    {
        var nameOnLoad = $('#nameString').val();
        var posOnLoad = $('#posString').val();
        var posOnSubmit = "";
        var nameOnSubmit = "";

        $('input[type="text"].nameInput').each(function(){
            nameOnSubmit = nameOnSubmit + $(this).val() + "**";
        });
        $('input[type="text"].posInput').each(function(){
            posOnSubmit = posOnSubmit + $(this).val() + "**";
        });
        if(nameOnLoad != nameOnSubmit || posOnLoad != posOnSubmit)
        {
            if(confirm("Save before proceeding?"))
            {
                saveLexiconMWE("JustSave");
            }
        }
    }

    var data = { task: "loadLexiconMWEsPage" , languageID :  $('#LanguageID').val(), pageToLoad : pageNo};
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

function saveLexiconMWE(sendMode)
{
    var data = $('#MultiWordLexiconForm').serialize();
    data += "&task=saveLexiconMWEs";
    if(sendMode == "SaveAndExit")
        data += "&updateRep=yes";

    showLoading('#multiWordLexiconDiv');

    $.ajax({
        url: "../data/MultiWordExpressions.data.php",
        type: "post",
        data: data ,
        success: function (response) {
            hideLoading('#multiWordLexiconDiv');
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[0].resultMsg;
            var responseID =  reqResponse[0].id;

            if (responseMsg.indexOf("DataIsNOTSavedForItems") != -1)
            {
                showMessage("Not saved",3000);
            }
            if (responseMsg.indexOf("FinalCopyFailed") != -1)
            {
                showMessage("Not copied to final destination!", 3000);
            }
            else if (responseMsg.indexOf("DataIsSavedForItems") != -1)
            {
                showMessage("Saved successfully", 3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('MultiWordLexicons.php');
                else
                    reloadOnSubmitData();
            }
            else if (responseMsg.indexOf("FailedToGenerateCsv") != -1)
            {
                showMessage("Failed to generate csv file to update.",  3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('MultiWordLexicons.php');
            }
            else if (responseMsg.indexOf("FailedConvertingToTxtDefinition") != -1)
            {
                showMessage("Failed to generate the definition file.", 3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('MultiWordLexicons.php');
            }
            else
            {
                showMessage("Something goes wrong!.", 3000);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#multiWordLexiconDiv');
            console.log(textStatus, errorThrown);
        }
    });
}

function goToTransformPage(pageNo, checkOnSubmit)
{
    if(checkOnSubmit)
    {
        if($('#memberString').val())
        {
            var memberOnLoad = $('#memberString').val();
            var memberOnSubmit = "";
            $('input[type="text"].transformInput').each(function(){
                memberOnSubmit = memberOnSubmit + $(this).val() + "**";
            });
            if(memberOnLoad != memberOnSubmit)
            {
                if(confirm("Save before proceeding?"))
                {
                    saveLexiconTransform("JustSave");
                }
            }
        }
    }

    var data = { task: "loadLexiconTransformsPage", languageID :  $('#LanguageID').val(), pageToLoad : pageNo};
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

function saveLexiconTransform(sendMode)
{
    var data = $('#MultiWordLexiconForm').serialize();
    data += "&task=saveLexiconTransforms";
    if(sendMode == "SaveAndExit")
        data += "&updateRep=yes";

    showLoading('#multiWordLexiconDiv');

    $.ajax({
        url: "../data/MultiWordExpressions.data.php",
        type: "post",
        data: data ,
        success: function (response) {
            hideLoading('#multiWordLexiconDiv');
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[0].resultMsg;
            var responseID =  reqResponse[0].id;

            if (responseMsg.indexOf("DataIsNOTSavedForItems") != -1)
            {
                showMessage("Not saved",3000);
            }
            if (responseMsg.indexOf("FinalCopyFailed") != -1)
            {
                showMessage("Not copied to final destination!", 3000);
            }
            else if (responseMsg.indexOf("DataIsSavedForItems") != -1)
            {
                showMessage("Saved successfully", 3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('MultiWordLexicons.php');
                else
                    reloadOnSubmitData();
            }
            else if (responseMsg.indexOf("FailedToGenerateCsv") != -1)
            {
                showMessage("Failed to generate csv file to update.",  3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('MultiWordLexicons.php');
            }
            else if (responseMsg.indexOf("FailedConvertingToTxtDefinition") != -1)
            {
                showMessage("Failed to generate the definition file.", 3000);
                if(sendMode == "SaveAndExit")
                    $("#mainContentDIV").load('MultiWordLexicons.php');
            }
            else
            {
                showMessage("Something goes wrong!.", 3000);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#multiWordLexiconDiv');
            console.log(textStatus, errorThrown);
        }
    });
}

function beforeAddNewMWE()
{
    $('#newLexiconMWEDiv').dialog({
        autoOpen: true,
        width: 550,
        height: 250,
        closeOnEscape: true,
        draggable: true,
        title: 'Add new MWE',
        buttons: {
            'Add': function () {
                if($('#MweHeader').val() == "")
                {
                    alert("Please fill out all data.");
                    return;
                }
                addNewLexicon();
            },
            'Cancel': function () {
                $('#MweHeader').val("");
                $('#MweName').val("");
                $('#MwePos').val("");
                $('#newLexiconMWEDiv').dialog('destroy');
            }
        }
    });
}

function addNewLexicon()
{
    showLoading('#multiWordLexiconDiv');
    var data = $('#NewMultiWordLexiconForm').serialize();

    $.ajax({
        url: "../data/MultiWordExpressions.data.php",
        type: "post",
        data: data ,
        success: function (response) {
            hideLoading('#multiWordLexiconDiv');
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[0].resultMsg;
            var responseID =  reqResponse[0].id;

            if (responseMsg.indexOf("FailedConvertingToTxtDefinition") != -1)
            {
                alert("Failed to generate the definition file.");
            }
            else if (responseMsg.indexOf("NewMWEFailed") != -1)
            {
                alert("Failed to save the new entry.");
            }
            else if (responseMsg.indexOf("NewMWESaved") != -1)
            {
                $('#MweHeader').val("");
                $('#MweName').val("");
                $('#MwePos').val("");
                if(confirm("Successfully saved. Do you want to reload the MWEs?"))
                {
                    $('#newLexiconMWEDiv').dialog('destroy');
                    goToMwePage($('#CurrentPage').val(),false);
                }
            }
            else
            {
                alert("Something goes wrong!.");
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#multiWordLexiconDiv');
            console.log(textStatus, errorThrown);
        }
    });
}

function deleteLexiconMWE(MultiWordLexiconMWEID)
{
    var confMsg = "Are you sure you want to delete it?";
    var LanguageID = $('#LanguageID').val();
    if(confirm(confMsg))
    {
        showLoading('#multiWordLexiconDiv');
        var data = { task: "deleteMWE", MultiWordLexiconMWEID :  MultiWordLexiconMWEID, LanguageID: LanguageID};
        $.ajax({
            url         : '../data/MultiWordExpressions.data.php',
            data        : data,
            type        : 'GET',
            contentType : 'application/json; charset=utf-8',

            success: function (response) {
                hideLoading('#multiWordLexiconDiv');
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[0].resultMsg;
                var responseID =  reqResponse[0].id;

                if (responseMsg.indexOf("FailedConvertingToTxtDefinition") != -1)
                {
                    alert("Failed to generate the definition file.");
                }
                else if (responseMsg.indexOf("DeleteMWEFailed") != -1)
                {
                    alert("Failed to delete the entry.");
                }
                else if (responseMsg.indexOf("MWEDeleted") != -1)
                {
                  goToMwePage($('#CurrentPage').val(),false);
                }
                else
                {
                    alert("Something goes wrong!.");
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                hideLoading('#mainContentDIV');
                console.log(textStatus, errorThrown);
                alert("Something is wrong here.");
            }
        });
    }
}