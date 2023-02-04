function onLoadFlashcardContents()
{
    $('#TableOfFlashcardContents').DataTable( {
        "order": []
    } );
}

function beforeGenerateFlashcardSet(contentID, userID, wordTranslationFC, audioTranslationFC, signedVideoFC, gapFC)
{
    var innerHtml = "<div>Number of cards:<br/><input type='text' name='NumberOfTests' id='NumberOfTests' value='10'></div><br/>" ;


    innerHtml += "<div>Choose language level:<br/>";
    innerHtml += '<input type="radio" id="FCL_beginner" name="FlashcardLevel" value="beginner">Beginner<br/>';
    innerHtml += '<input type="radio" id="FCL_intermediate" name="FlashcardLevel" value="intermediate">Intermediate<br/>';
    innerHtml += '<input type="radio" id="FCL_advanced" name="FlashcardLevel" value="advanced">Advanced<br/>';
    innerHtml += '<input type="radio" id="FCL_multiword" name="FlashcardLevel" value="multiword_expressions">Multiword expressions<br/>';
    innerHtml += '</div>';



    innerHtml += "<div>Choose type of cards:<br/>";
    if(wordTranslationFC == "LEMMA")
        innerHtml += '<input type="radio" id="FC_lemma" name="FlashcardType" value="lemma_translation_ask_l2">Word translation<br/>';
    else if(wordTranslationFC == "TOKEN")
        innerHtml += '<input type="radio" id="FC_token" name="FlashcardType" value="token_translation_ask_l2">Word translation<br/>';
    if(audioTranslationFC == "LEMMA")
        innerHtml += '<input type="radio" id="FC_lemma_audio" name="FlashcardType" value="lemma_translation_ask_l2_audio">Word translation with audio<br/>';
    else if(audioTranslationFC == "TOKEN")
        innerHtml += '<input type="radio" id="FC_token_audio" name="FlashcardType" value="token_translation_ask_l2_audio">Word translation with audio<br/>';
    if(signedVideoFC == "YES")
        innerHtml += '<input type="radio" id="FC_signed_video" name="FlashcardType" value="signed_video_ask_l2">signed video<br/>';
    if(gapFC == "YES")
        innerHtml += '<input type="radio" id="FC_gap" name="FlashcardType" value="sentence_with_gap">sentence with gap<br/>';
    innerHtml += '</div>';

    $('#FlashcardTypeDiv').html(innerHtml);
    $('#FlashcardTypeDiv').dialog({
        autoOpen: true,
        width: 550,
        height: 350,
        closeOnEscape: true,
        draggable: true,
        title: 'Choose flashcard type',
        buttons: {
            'Start test': function () {
                var flashcardsNumber = $('#NumberOfTests').val();
                if(flashcardsNumber == "")
                {
                    alert("Please fill in the number of cards.");
                    return;
                }

                var flashcardType = $("input[name='FlashcardType']:checked").val();
                if(!flashcardType)
                {
                    alert("Please select type of cards.");
                    return;
                }

                var flashcardLevel = $("input[name='FlashcardLevel']:checked").val();
                if(!flashcardLevel)
                {
                    alert("Please select level of cards.");
                    return;
                }
                generateFlashcardSet(contentID, userID, flashcardType, flashcardsNumber, flashcardLevel);
            },
            'Cancel': function () {
                $('#FlashcardTypeDiv').dialog('destroy');
            }

        }
    });
}

function generateFlashcardSet(contentID, userID, flashcardType, flashcardsNumber, flashcardLevel)
{
    $('#FlashcardTypeDiv').dialog('destroy');

    showLoading('#mainContentDIV');
    var data = { task: "generateFlashcardSet", contentID :  contentID,
                 userID : userID, flashcardType: flashcardType,
                 flashcardsNumber: flashcardsNumber , flashcardLevel: flashcardLevel};
    $.ajax({
        url         : '../data/Flashcards.data.php',
        data        : data,
        type        : 'GET',
        contentType : 'application/json; charset=utf-8',

        success: function (response) {
            hideLoading('#mainContentDIV');
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[0].resultMsg;
            var responseID =  reqResponse[0].id;

            if(responseMsg == "GenerateFailed")
            {
                alert("Failed to create flashcard.");
            }
            else if(responseMsg == "GenerateSucceed")
            {
                $("#mainContentDIV").load('FlashcardTest.php?setID=' + responseID + '&flashcardNo=1&flashcardType=' + flashcardType);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
            alert("Something is wrong here.");
        }
    });
}

function goToFlashcard(setID, flashcardNo, flashcardType, numberOfTests)
{
    $("#ShowResponseSummary").css("display","none");
    $("#ResponseSummaryDiv").css("display","none");
    if (flashcardNo == 0)
    {
        alert("You are at the first flashcard!");
    }
    else if (flashcardNo > numberOfTests)
    {
        alert("You are at the last flashcard!");
        $("#ShowResponseSummary").css("display","");
    }
    else
    {
        $("#mainContentDIV").load('FlashcardTest.php?setID=' + setID + '&flashcardNo=' + flashcardNo + "&flashcardType=" + flashcardType);
    }
}

function checkAnswer(setID, flashcardNo, flashcardType, numberOfTests)
{
    var currentFlashcardNo = flashcardNo - 1;
    var responseID = $("input[name='Answers']:checked").attr('id');

    showLoading('#mainContentDIV');
    var data = { task: "saveResponse", responseID:  responseID,
                flashcardNo: currentFlashcardNo, setID: setID};
    $.ajax({
        url         : '../data/Flashcards.data.php',
        data        : data,
        type        : 'GET',
        contentType : 'application/json; charset=utf-8',

        success: function (response) {
            hideLoading('#mainContentDIV');
            $('#currentScore').html(response);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
            alert("Failed to save response");
            return;
        }
    });

    var correct = document.getElementById("Correct");
    var incorrect = document.getElementById("Incorrect");
    
    correct.hidden = true;
    incorrect.hidden = true;
    
    var answerValue = $("input[name='Answers']:checked").val();
    if(answerValue == 'yes')
    {
        correct.hidden = false;

        if ($('#audioForSentenceWithGap').length)
        {
            $("#audioForSentenceWithGap").css("display","");
        }
        else
        {
            setTimeout(function() {
                goToFlashcard(setID, flashcardNo, flashcardType, numberOfTests)
            }, 2000);
        }
    }
    else
    {
        incorrect.hidden = false;
    }
}

function showResponsesSummary($setID)
{
    showLoading('#mainContentDIV');
    var data = { task: "getResponseSummary", setID:  $setID};
    $.ajax({
        url         : '../data/Flashcards.data.php',
        data        : data,
        type        : 'GET',
        contentType : 'application/json; charset=utf-8',

        success: function (response) {
            hideLoading('#mainContentDIV');
            $('#ResponseSummaryDiv').html(response);
            $("#ResponseSummaryDiv").css("display","");
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
            alert("Failed to retrieve responses");
            return;
        }
    });
}