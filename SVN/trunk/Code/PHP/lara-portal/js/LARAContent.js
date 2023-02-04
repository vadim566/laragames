function onLoadLaraContents()
{
    $('#TableOfContents').DataTable();
}

function deleteContent(contentID, contentName)
{
    var confMsg = "Are you sure you want to delete " + contentName + "?";
    if(confirm(confMsg))
    {
        showLoading('#mainContentDIV');
        var data = { task: "DeleteContent", contentID :  contentID};
        $.ajax({
            url         : '../data/Content.data.php',
            data        : data,
            type        : 'GET',
            contentType : 'application/json; charset=utf-8',

            success: function (response) {
                hideLoading('#mainContentDIV');
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[0].resultMsg;
                var responseID =  reqResponse[0].id;

                if(responseMsg == "FailedDelete")
                {
                    alert("Failed to delete.");
                }
                else if(responseMsg == "HasTakenChildren")
                {
                    alert("Some people are working on the sub-contents. You can not delete it.");
                }
                else if(responseMsg == "SuccessfulDeleteContent")
                {
                    $("#mainContentDIV").load('LARAContents.php');
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

function distributeContent(contentID, contentName)
{
    var confMsg = "Are you sure you want to distribute " + contentName + "?";
    if(confirm(confMsg))
    {
        showLoading('#mainContentDIV');
        var data = { task: "DistributeContent", contentID :  contentID};
        $.ajax({
            url         : '../data/Content.data.php',
            data        : data,
            type        : 'GET',
            contentType : 'application/json; charset=utf-8',

            success: function (response) {
                hideLoading('#mainContentDIV');
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[0].resultMsg;
                var responseID =  reqResponse[0].id;

                if(responseMsg == "FailedDistribute")
                {
                    alert("Failed to distribute.");
                }
                if(responseMsg == "NotSuitableForCut")
                {
                    alert("unable to find occurrences of \"<cut>\"");
                }
                else if(responseMsg == "SuccessfulDistributeContent")
                {
                    alert("Successfully Distributed. You can check the sub-contents in your crowd-worker tasks.");
                    $("#mainContentDIV").load('LARAContents.php');
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

function collectContent(contentID, contentName)
{
    var confMsg = "Are you sure you want to stick piece of " + contentName + " together?";
    if(confirm(confMsg))
    {
        showLoading('#mainContentDIV');
        var data = { task: "CollectContent", contentID :  contentID};
        $.ajax({
            url         : '../data/Content.data.php',
            data        : data,
            type        : 'GET',
            contentType : 'application/json; charset=utf-8',

            success: function (response) {
                hideLoading('#mainContentDIV');
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[0].resultMsg;
                var responseID =  reqResponse[0].id;

                if(responseMsg == "FailedCollect")
                {
                    alert("Failed to distribute.");
                }
                else if(responseMsg == "SuccessfulCollectContent")
                {
                    alert("Successfully Collected.");
                    $("#mainContentDIV").load('LARAContents.php');
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

function getTask(contentID, contentName)
{
    var confMsg = "Are you sure you want to assign " + contentName + " to yourself?";
    if(confirm(confMsg))
    {
        showLoading('#mainContentDIV');
        var data = { task: "GetTask", contentID :  contentID};
        $.ajax({
            url         : '../data/Content.data.php',
            data        : data,
            type        : 'GET',
            contentType : 'application/json; charset=utf-8',

            success: function (response) {
                hideLoading('#mainContentDIV');
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[0].resultMsg;
                var responseID =  reqResponse[0].id;

                if(responseMsg == "AlreadyTaken")
                {
                    alert("Sorry, the task is not availabe anymore.");
                }
                else if(responseMsg == "SuccessfullyAssigned")
                {
                    alert("You can now edit the task in your crowd-worker tasks.");
                    $("#mainContentDIV").load('AvailableTasks.php');
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

function beforeGiveUp(contentID, contentName, currentRole)
{
    var placeHolder;
    if(currentRole == "Requester")
        placeHolder = 'why to take ' + contentName + ' back ..';
    else
        placeHolder = 'why to give ' + contentName + ' back ..';

    $('#reasonBody').prop('placeholder', placeHolder);

    $('#GiveUpReasonDiv').dialog({
        autoOpen: true,
        width: 520,
        height: 220,
        closeOnEscape: true,
        draggable: true,
        title: 'Send for revision',
        buttons: {
            'Okay': function () {
                var reasonBody = $('#reasonBody').val();
                giveUpTask(contentID, reasonBody, currentRole);
            },
            'Cancel': function () {
                $('#GiveUpReasonDiv').dialog('destroy');
            }
        }
    });
}

function giveUpTask(contentID, reasonBody, currentRole)
{
    $('#GiveUpReasonDiv').dialog('destroy');
    showLoading('#mainContentDIV');
    var data = { task: "GiveUpTask", contentID :  contentID,
                reasonBody: reasonBody, currentRole : currentRole};
        $.ajax({
            url         : '../data/Content.data.php',
            data        : data,
            type        : 'GET',
            contentType : 'application/json; charset=utf-8',

            success: function (response) {
                hideLoading('#mainContentDIV');
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[0].resultMsg;
                var responseID =  reqResponse[0].id;

                if(responseMsg == "SuccessfullyTakenBack")
                {
                    alert("The task is again available.");
                    if(currentRole == "Requester")
                        $("#mainContentDIV").load('CrowdRequesterTasks.php');
                    else
                        $("#mainContentDIV").load('CrowdWorkerTasks.php');
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                hideLoading('#mainContentDIV');
                console.log(textStatus, errorThrown);
                alert("Something is wrong here.");
            }
        });

}

function beforeSendForRevision(contentID, currentRole)
{
    $('#MessageDiv').dialog({
        autoOpen: true,
        width: 520,
        height: 220,
        closeOnEscape: true,
        draggable: true,
        title: 'Send for revision',
        buttons: {
            'Send it!': function () {
                var messageBody = $('#messageBody').val();
                sendContentMessage(contentID, messageBody, currentRole);
            },
            'Cancel': function () {
                $('#MessageDiv').dialog('destroy');
            }
        }
    });
}

function sendContentMessage(contentID, messageBody, currentRole)
{
    $('#MessageDiv').dialog('destroy');
    showLoading('#mainContentDIV');
    var data = { task: "SendContentMessage", contentID :  contentID,
                 messageBody: messageBody, currentRole : currentRole};
    $.ajax({
        url         : '../data/Content.data.php',
        data        : data,
        type        : 'GET',
        contentType : 'application/json; charset=utf-8',

        success: function (response) {
            hideLoading('#mainContentDIV');
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[0].resultMsg;
            var responseID =  reqResponse[0].id;

            if(responseMsg == "SuccessfullySentMessage")
            {
                if(currentRole == "Requester")
                    $("#mainContentDIV").load('CrowdRequesterTasks.php');
                else
                    $("#mainContentDIV").load('CrowdWorkerTasks.php');
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
            alert("Something is wrong here.");
        }
    });
}

function ShowRequesterNotes(contentID)
{
    var data = { task: "GetContentMessages", contentID :  contentID};
    $
    $.ajax({
        url         : '../data/Content.data.php',
        data        : data,
        type        : 'GET',
        contentType : 'application/json; charset=utf-8',

        success: function (response) {
            hideLoading('#mainContentDIV');
            $('#MessageHistoryDiv').html(response);
            var opt = {
                autoOpen: false,
                modal: true,
                width: 600,
                height:300,
                title: 'Reading texts'
            };

            $('#MessageHistoryDiv').dialog(opt).dialog("open");
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
            alert("Something is wrong here.");
        }
    });
}

function finalizeTask(contentID)
{
    var confMsg = "Are you sure the task is all done? It won't be available for crowd worker anymore.";

    if(confirm(confMsg))
    {
        showLoading('#mainContentDIV');
        var data = { task: "FinalizeTask", contentID :  contentID};
        $.ajax({
            url         : '../data/Content.data.php',
            data        : data,
            type        : 'GET',
            contentType : 'application/json; charset=utf-8',

            success: function (response) {
                hideLoading('#mainContentDIV');
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[0].resultMsg;
                var responseID =  reqResponse[0].id;

                if(responseMsg == "SuccessfullyFinalized")
                {
                    alert("Thanks for your participation.");
                    $("#mainContentDIV").load('CrowdRequesterTasks.php');
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