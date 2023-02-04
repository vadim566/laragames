function onLoad()
{
    var inputNames = Object.keys(ResourceVal);

    var inputName;
    var inputID;

    for (i = 0; i < inputNames.length; i++) {
        inputName = inputNames[i];
        inputID = "#" + inputName;
        if($('input:radio[name="' + inputName + '"]').length)
        {
            $('input:radio[name="' + inputName + '"]').val([ResourceVal[inputName]]);
        }
        else
        {
            $(inputID).val(ResourceVal[inputName]);
        }
    }
    if(ResourceVal["ResourceType"] == "Language")
        $("#ParentDataInputForContentResources").css("display","none");
    else
        $("#ParentDataInputForContentResources").css("display","");

}

$('input[type=radio][name=ResourceType]').change(function() {
    if (this.value == 'Content') {
        $("#ParentDataInputForContentResources").css("display","");
    }
    else if (this.value == 'Language') {
        $("#ParentDataInputForContentResources").css("display","none");
    }
});

function SaveDistributedResource()
{
    if(validateResourceForm())
    {
        showLoading('#mainContentDIV');
        var form = $('#ResourceForm');

        var data = form.serialize();
        $.ajax({
            url         : '../data/DistributedResource.data.php',
            data        : data,
            type        : 'POST',
            success: function (response) {
                hideLoading('#mainContentDIV');
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[0].resultMsg;
                var responseID =  reqResponse[0].id;
                if (responseMsg == "ResourceAdded")
                {
                    showMessage("The new resource is added successfully.", responseID, 3000);
                }
                else if (responseMsg == "FailedToExtractPageNamesDR")
                {
                    showMessage("Could not extract the page names of the resource.", responseID, 3000);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                hideLoading('#mainContentDIV');
                console.log(textStatus, errorThrown);
                showMessage("Something is wrong in distributed resource adding/edditing.", -1, 5000);
            }
        });
    }
    else
    {
        setTimeout(function() {
            $('.ResourceError').css("display", "none");
        }, 3000);

    }
}

function validateResourceForm()
{
    var ResourceNameReg = /[A-Za-z\u00C0-\u017F][A-Za-z\u00C0-\u017F0-9_-]*/;
    var ResourceName = $('#ResourceName').val();

    if(!ResourceNameReg.test(ResourceName))
    {
        alert('Resource name must be letters and digits.');
        return false;
    }

    return true;
}

function showMessage(message, ResourceID, timeout)
{
    $('.ResourceError').css("display", "");
    $('.ErrorMsg').html(message);
    setTimeout(function() {
        $('.ErrorMsg').html("");
        $('.ResourceError').css("display", "none");
        if(ResourceID != -1)
        {
            $("#mainContentDIV").load('NewDistributedResource.php?Q0=' + ResourceID);
        }
    }, timeout);
}

function onLoadDistributedList()
{
    $('#TableOfDistributed').DataTable();
}

function deleteResource(resourceID, resourceName, rType)
{
    var confMsg = "Are you sure you want to delete " + resourceName + "?";
    if(confirm(confMsg))
    {
        showLoading('#mainContentDIV');
        var data = { task: "DeleteResource", resourceID :  resourceID};
        $.ajax({
            url         : '../data/DistributedResource.data.php',
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
                else if(responseMsg == "SuccessfulDeleteResource")
                {
                    $("#mainContentDIV").load('DistributedResourcesList.php?rType=' + rType);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                hideLoading('#mainContentDIV');
                console.log(textStatus, errorThrown);
                alert("Something is wrong in deleting the resource.");
            }
        });
    }
}
