function onLoad(activeTab, msgToShow )
{
    var inputNames = Object.keys(R_H_Val);

    var inputName;
    var inputID;

    for (i = 0; i < inputNames.length; i++) {
        inputName = inputNames[i];
        inputID = "#" + inputName;
        if($('input:radio[name="' + inputName + '"]').length)
        {
            $('input:radio[name="' + inputName + '"]').val([R_H_Val[inputName]]);
        }
        else
        {
            $(inputID).val(R_H_Val[inputName]);
        }
    }

    var form = $('#readingHistoryForm');
    $( "#tabs" ).tabs();
    $( "#tabs" ).tabs( "option", "active", activeTab);

    if(msgToShow != "notSetYet")
    {
        showMessageOnload(msgToShow);
    }
}

function addReadingHistory() {

    var activeTab = 0;
    if(validateReadingHistoryForm())
    {
        showLoading('#mainContentDIV');
        var form = $('#readingHistoryForm');

        var data = form.serialize();
        $.ajax({
            url         : '../data/ReadingHistory.data.php',
            data        : data,
            type        : 'POST',
            success: function (response) {
                hideLoading('#mainContentDIV');
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[0].resultMsg;
                var responseID =  reqResponse[0].id;

                $("#mainContentDIV").load('NewReadingHistory.php?Q0=' + responseID +
                                          '&activeTab=' + activeTab + '&msg=' + responseMsg);

            },
            error: function(jqXHR, textStatus, errorThrown) {
                hideLoading('#mainContentDIV');
                console.log(textStatus, errorThrown);
                alert("Something is wrong in reading history tab.");
            }
        });
    }
    else
    {
        setTimeout(function() {
            $('.configFileError').css("display", "none");
        }, 3000);

    }
}

function validateReadingHistoryForm()
{
    var ReadingHistoryName = $('#ReadingHistoryName').val();
    var L1 = $('#L1ID').val();
    var L2 = $('#L2ID').val();

    $('.readingHistoryError').css("display", "");

    if(ReadingHistoryName == "")
    {
        $('.ErrorMsg').html('Please Enter a Name for the Content');
        return false;
    }

    if(L1 == -1)
    {
        $('.ErrorMsg').html('Please Select a Language as translation language');
        return false;
    }

    if(L2 == -1)
    {
        $('.ErrorMsg').html('Please Select a Language as reading language');
        return false;
    }

    $('.readingHistoryError').css("display", "none");
    return true;
}

function showMessageOnload(message)
{
    var msgText = getMsgText(message);
    $('.readingHistoryError').css("display", "");
    $('.ErrorMsg').html(msgText);
}

function getMsgText(responseMsg)
{
    var msgToShow;
    if (responseMsg == "CreateDIRFailedAddReadingHistory")
    {
        msgToShow = "Failed to create reading history directory.";
    }
    else if (responseMsg == "FailedToCreateConfigFile")
    {
        msgToShow = "Failed to config reading history.";
    }
    else if (responseMsg == "NewReadingHistoryIsReady")
    {
        msgToShow = "Reading history is created successfully.";
    }
    else if (responseMsg == "NoChangeInPreferences")
    {
        msgToShow = "Reading history has not changed.";
    }
    else if (responseMsg == "NewPreferencesSaved")
    {
        msgToShow = "New preferences are saved.";
    }
    else if (responseMsg == "RecompileSucceed")
    {
        msgToShow = "Reading history is created with new preferences.";
    }
    else if (responseMsg == "RecompileFailure")
    {
        msgToShow = "Failed to recompile reading history.";
    }
    else if (responseMsg == "FailedToCreateConfigFile")
    {
        msgToShow = "Failed to config reading history.";
    }
    else if (responseMsg == "RecompileSucceed")
    {
        msgToShow = "Reading history is created with new resource.";
    }
    else if (responseMsg == "RecompileFailure")
    {
        msgToShow = "Failed to recompile reading history.";
    }
    else if (responseMsg == "DuplicatedResource")
    {
        msgToShow = "The resource already exists in this history.";
    }
    else if (responseMsg == "RecompileSucceedHR")
    {
        msgToShow = "Text added to the reading history.";
    }
    else if (responseMsg == "RecompileFailureHR")
    {
        msgToShow = "Failed to add text to reading history.";
    }
    else if (responseMsg == "RecompileSucceedRH")
    {
        msgToShow = "Reading history recompiled successfully.";
    }
    else if (responseMsg == "RecompileFailureRH")
    {
        msgToShow = "Failed to recompile reading history.";
    }


    return msgToShow;
}

function onLoadReadingHistories()
{
    $('#TableOfHistories').DataTable();
}

function deleteHistory(ReadingHistoryID, ReadingHistoryName)
{
    var confMsg = "Are you sure you want to delete " + ReadingHistoryName + "?";
    if(confirm(confMsg))
    {
        showLoading('#mainContentDIV');
        var data = { task: "DeleteHistory", ReadingHistoryID :  ReadingHistoryID};
        $.ajax({
            url         : '../data/ReadingHistory.data.php',
            data        : data,
            type        : 'GET',
            contentType : 'application/json; charset=utf-8',

            success: function (response) {
                hideLoading('#mainContentDIV');
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[0].resultMsg;
                var responseID =  reqResponse[0].id;

                if(responseMsg == "")
                {
                    alert("");
                }
                else if(responseMsg == "SuccessfulDeleteHistory")
                {
                    $("#mainContentDIV").load('ReadingHistories.php');
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                hideLoading('#mainContentDIV');
                console.log(textStatus, errorThrown);
                alert("Something is wrong in list of reading histories.");
            }
        });
    }
}

function addHistoryResource() {

    var activeTab = 1;

    showLoading('#mainContentDIV');
    var data = { task: "AddHistoryResource",
                    ReadingHistoryID :  $("#ReadingHistoryID").val(), ResourceID : $("#ResourceID").val()};
    $.ajax({
        url         : '../data/ReadingHistory.data.php',
        data        : data,
        type        : 'GET',
        contentType : 'application/json; charset=utf-8',

        success: function (response) {
            hideLoading('#mainContentDIV');
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[0].resultMsg;
            var responseID =  reqResponse[0].id;

            $("#mainContentDIV").load('NewReadingHistory.php?Q0=' + responseID +
                '&activeTab=' + activeTab + '&msg=' + responseMsg);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
            alert("Something is wrong in adding resource to the history.");
        }
    });
}

function ShowListOfHistoryResources(ReadingHistoryID, ReadingHistoryName) {

    var data = { task: "GetHistoryResources", ReadingHistoryID :  ReadingHistoryID};
    showLoading('#mainContentDIV');
    $.ajax({
        url         : '../data/ReadingHistory.data.php',
        data        : data,
        type        : 'GET',
        contentType : 'application/json; charset=utf-8',

        success: function (response) {
            hideLoading('#mainContentDIV');
            $('#ResourcesDialog').html(response);
            var opt = {
                autoOpen: false,
                modal: true,
                width: 400,
                height:300,
                title: 'Reading texts'
            };


            $('#ResourcesDialog').dialog(opt).dialog("open");
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
            alert("Something is wrong in list of reading histories.");
        }
    });
}

function loadNavigatePage(ReadingHistoryResourceID, PageToLoad)
{
    $("#mainContentDIV").load('NavigateHistoryResource.php?' +
                              'rhrID=' + ReadingHistoryResourceID +
                              '&pageToLoad=' + PageToLoad);
    $('#ResourcesDialog').dialog('destroy');
}

function goToNextPage(ReadingHistoryResourceID, CurrentPage)
{
    var NextPage = CurrentPage + 1;
    showLoading('#mainContentDIV');
    var data = { task: "GoToNextPage", ReadingHistoryResourceID :  ReadingHistoryResourceID, CurrentPage : CurrentPage};
    $.ajax({
        url         : '../data/ReadingHistory.data.php',
        data        : data,
        type        : 'GET',
        contentType : 'application/json; charset=utf-8',

        success: function (response) {
            hideLoading('#mainContentDIV');
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[0].resultMsg;
            var responseID =  reqResponse[0].id;

            if (responseMsg == "NoNextPage")
            {
                alert("Congratulation! you are at the last page.");
            }
            else if (responseMsg == "NextPageExists" || responseMsg == "NewPageAdded")
            {
                $("#mainContentDIV").load('NavigateHistoryResource.php?' +
                    'rhrID=' + ReadingHistoryResourceID + '&pageToLoad=' + NextPage);
            }
            else if (responseMsg == "FailedToCreateNewConfigFile")
            {
                alert("Failed To Create New Config File.");
            }
            else if (responseMsg == "FailedToAddNewPage")
            {
                alert("Failed To Add New Page.");
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
            alert("Something is wrong in adding page to resource.");
        }
    });

}

function goToPrvPage(ReadingHistoryResourceID, CurrentPage) {

    if (CurrentPage == 1)
    {
        alert("You are at the first page!");
    }
    else
    {
        var PrvPage = CurrentPage - 1;
        $("#mainContentDIV").load('NavigateHistoryResource.php?' +
            'rhrID=' + ReadingHistoryResourceID + '&pageToLoad=' + PrvPage);

    }
}