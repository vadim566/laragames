function onLoad()
{
    $("#ui-datepicker-div").remove();

    $("#StartDate").datepicker({
        dateFormat : "yy-mm-dd"
    });
    $("#EndDate").datepicker({
        dateFormat : "yy-mm-dd"
    });
}

function searchContentLog()
{
    showLoading('#mainContentDIV');
    var form = $('#contentLogForm');

    var data = form.serialize();
    $.ajax({
        url         : '../data/Content.data.php',
        data        : data,
        type        : 'POST',
        success: function (response) {
            hideLoading('#mainContentDIV');
            $("#ContentLogsDataDiv").empty().append(response);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
        }
    });
}

function searchFlashcardLog()
{
    showLoading('#mainContentDIV');
    var form = $('#FlashcardLogForm');

    var data = form.serialize();
    $.ajax({
        url         : '../data/Flashcards.data.php',
        data        : data,
        type        : 'POST',
        success: function (response) {
            hideLoading('#mainContentDIV');
            $("#FlashcardLogsDataDiv").empty().append(response);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
        }
    });
}

function searchReadingLog()
{
    showLoading('#mainContentDIV');
    var form = $('#readingLogForm');

    var data = form.serialize();
    $.ajax({
        url         : '../data/ReadingHistory.data.php',
        data        : data,
        type        : 'POST',
        success: function (response) {
            hideLoading('#mainContentDIV');
            $("#HistoryLogsDataDiv").empty().append(response);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
        }
    });
}