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
                    //todo I have to change here
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

function getTheTask(contentID, contentName)
{
    var confMsg = "Are you sure you want to assign " + contentName + " to yourself?";
    if(confirm(confMsg))
    {
        showLoading('#mainContentDIV');
        var data = { task: "GetTheTask", contentID :  contentID};
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
                    alert("You can now edit the task in your LARA texts.");
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