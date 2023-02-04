var TaskValues = ["TagRawText", "SetConfig", "CreateResources"];
var enginesAndVoices;

function onLoad(activeTab, msgToShow)
{
    $("#TaggingButton").css("display","none");
    $("#SetConfigButton").css("display","");
    $("#CreateResourceButton").css("display","");

    var inputNames = Object.keys(contentVal);

    var inputName;
    var inputID;

    for (i = 0; i < inputNames.length; i++) {
        inputName = inputNames[i];
        inputID = "#" + inputName;
        if($('input:radio[name="' + inputName + '"]').length)
        {
            $('input:radio[name="' + inputName + '"]').val([contentVal[inputName]]);
        }
        else if($('input:checkbox[name="' + inputName + '"]').length)
        {
            if(contentVal[inputName] == "YES")
                $('input:checkbox[name="' + inputName + '"]').attr("checked",true);
        }
        else
        {
            $(inputID).val(contentVal[inputName]);
        }
    }

    if ($("#WTFC_lemma").is(':checked') || $("#WTFC_token").is(':checked'))
        $('#WTFC_checkbox').attr("checked",true);

    if (!$("#WTFC_checkbox").is(':checked'))
    {
        $("#WTFC_lemma").prop("disabled", true);
        $("#WTFC_token").prop("disabled", true);
    }

    if ($("#WAFC_lemma").is(':checked') || $("#WAFC_token").is(':checked'))
        $('#WAFC_checkbox').attr("checked",true);

    if (!$("#WAFC_checkbox").is(':checked'))
    {
        $("#WAFC_lemma").prop("disabled", true);
        $("#WAFC_token").prop("disabled", true);
    }

    var form = $('#configFileForm');

    var L2 = $('#L2ID').val();
    if(L2 != -1)
    {
        var url = "../data/Language.data.php";
        var data = "LanguageID=" + L2 + "&task=hasTreeTagger";

        $.ajax({
            url: url,
            type: "post",
            data: data,
            success: function(response) {
                if (response.indexOf("YES") != -1) {
                    $("#TreeTaggerStatusTR").css("display","");

                }
                else {
                    $("#TreeTaggerStatusTR").css("display", "none");
                }
            }
        });

        var url = "../data/Content.data.php";
        var data = "LanguageID=" + L2 + "&task=TtsEnginesList";

        $.ajax({
            url: url,
            type: "post",
            data: data,
            success: function(response) {
                enginesAndVoices = $.parseJSON(response);
                loadTtsEngines();
            }
        });
    }

    //OptionalComplementaries
    $( "#OptionalComplementary" ).accordion({
        collapsible: true, active : 'none'
    });

    //PlayComplementaries
    $( "#PlayComplementary" ).accordion({
        collapsible: true, active : 'none'
    });

    //TranslationComplementaries
    $( "#TranslationComplementary" ).accordion({
        collapsible: true, active : 'none'
    });

    //TranslationComplementaries
    $( "#FlashcardComplementary" ).accordion({
        collapsible: true, active : 'none'
    });

    if($("#AutomatedTaggedTextFileName").val()  != "")
    {
        $("#UseAutomatedTaggedTextTR").css("display","");
    }
    //embeddedImages
    if($("#HasEmbeddedImage").val() == 'YES' && emItemVal["ImageNames"] != null && emItemVal["ImageNames"] != "")
    {
        var ImageNames = emItemVal["ImageNames"].split("@@");
        var ImageDescription = "";
        for(i = 0 ; i < ImageNames.length; i++)
        {
            var ImageNameParts = ImageNames[i].split(":");
            if(ImageNameParts[1] == 'NO')
            {
                ImageDescription = ImageDescription.concat(ImageNameParts[0] + ",");
            }
        }
        if(ImageDescription == "")
        {
            ImageDescription = "You have already uploaded all images."
        }
        else
        {
            $("#EmbeddedFilesDesc").css("display","");
            ImageDescription = "List of Images: " + ImageDescription ;
        }
        $("#EmbeddedImageTR").css("display","");
        $('#eImageFileName').css("display", "");
        $('#eImageFileName').html(ImageDescription);
    }
    //embeddedAudios
    if($("#HasEmbeddedAudio").val() == 'YES' && emItemVal["AudioNames"] != null && emItemVal["AudioNames"] != "")
    {
        var AudioNames = emItemVal["AudioNames"].split("@@");
        var AudioDescription = "";
        for(i = 0 ; i < AudioNames.length; i++)
        {
            var AudioNameParts = AudioNames[i].split(":");
            if(AudioNameParts[1] == 'NO')
            {
                AudioDescription = AudioDescription.concat(AudioNameParts[0] + ",");
            }
        }
        if(AudioDescription == "")
        {
            AudioDescription = "You have already uploaded all audios."
        }
        else
        {
            $("#EmbeddedFilesDesc").css("display","");
            AudioDescription = "List of Audios: " + AudioDescription ;
        }
        $("#EmbeddedAudioTR").css("display","");
        $('#eAudioFileName').css("display", "");
        $('#eAudioFileName').html(AudioDescription);
    }
    //embeddedCSS
    if($("#HasEmbeddedCSS").val() == 'YES' && emItemVal["cssNames"] != null && emItemVal["cssNames"] != "")
    {
        var cssNames = emItemVal["cssNames"].split("@@");
        var CssDescription = "";
        for(i = 0 ; i < cssNames.length; i++)
        {
            var CssNameParts = cssNames[i].split(":");
            if(CssNameParts[1] == 'NO')
            {
                CssDescription = CssDescription.concat(CssNameParts[0] + ",");
            }
        }
        if(CssDescription == "")
        {
            CssDescription = "You have already uploaded all css files."
        }
        else
        {
            $("#EmbeddedFilesDesc").css("display","");
            CssDescription = "List of CSS: " + CssDescription ;
        }
        $("#EmbeddedCssTR").css("display","");
        $('#eCssFileName').css("display", "");
        $('#eCssFileName').html(CssDescription);
    }
    //embeddedScript
    if($("#HasEmbeddedScript").val() == 'YES' && emItemVal["ScriptNames"] != null && emItemVal["ScriptNames"] != "")
    {
        var scriptNames = emItemVal["ScriptNames"].split("@@");
        var ScriptDescription = "";
        for(i = 0 ; i < scriptNames.length; i++)
        {
            var ScriptNameParts = scriptNames[i].split(":");
            if(ScriptNameParts[1] == 'NO')
            {
                ScriptDescription = ScriptDescription.concat(ScriptNameParts[0] + ",");
            }
        }
        if(ScriptDescription == "")
        {
            ScriptDescription = "You have already uploaded all script files."
        }
        else
        {
            $("#EmbeddedFilesDesc").css("display","");
            ScriptDescription = "List of Script: " + ScriptDescription ;
        }
        $("#EmbeddedScriptTR").css("display","");
        $('#eScriptFileName').css("display", "");
        $('#eScriptFileName').html(ScriptDescription);
    }
    if($("input[name='WordsAudioType']:checked").val() == "tts" ||
        $("input[name='SegmentsAudioType']:checked").val() == "tts")
    {
        $("#TtsEngineTR").css("display","");
        $("#TtsVoiceTR").css("display","");
    }
    if($("input[name='WordsAudioType']:checked").val()  == "human")
    {
        $("#LdtDeactivateStatusTR").css("display","");
        $("#WordAudioTR").css("display","");
    }
    if($("input[name='SegmentsAudioType']:checked").val() == "human")
    {
        $("#LdtDeactivateStatusTR").css("display","");
        $("#SegmentAudioTR").css("display","");
    }
    if($("input[name='LdtDeactivateStatus']:checked").val() == "YES")
    {
        $("#WordAudioTR").css("display","none");
        $("#SegmentAudioTR").css("display","none");
    }

    var lemmaAndTypeCmp = "&fileDir=" + contentVal["DirName"] + "&download=csvFileDL&contentID=" + $("#ContentID").val();
    $('#LemmaCsvDL').attr("href","../SharedModules/DownloadFile.php?fileType=lemma" + lemmaAndTypeCmp);
    $('#TypeCsvDL').attr("href","../SharedModules/DownloadFile.php?fileType=type" + lemmaAndTypeCmp);

    var tokenAndSegmentCmp = "&fileDir=" + contentVal["DirName"] + "&download=csvTokenAndSegmentFileDL&contentID=" + $("#ContentID").val();
    $('#TokenCsvDL').attr("href","../SharedModules/DownloadFile.php?fileType=token" + tokenAndSegmentCmp);
    $('#SegmentCsvDL').attr("href","../SharedModules/DownloadFile.php?fileType=segment" + tokenAndSegmentCmp);


    var mode = $("#EditMode").val();
    $('#LemmaNote').click(function () {
        $("#mainContentDIV").load('TranslateLemma.php?contentID=' + $("#ContentID").val() + '&justNote=yes' + '&mode=' + mode);
    });

    $('#LemmaTrnslt').click(function () {
        $("#mainContentDIV").load('TranslateLemma.php?contentID=' + $("#ContentID").val() + '&mode=' + mode);
    });

    $('#TypeTrnslt').click(function () {
        $("#mainContentDIV").load('TranslateType.php?contentID=' + $("#ContentID").val() + '&mode=' + mode);
    });

    $('#ApplyToToken').click(function() {
        applyTypeToToken();
    });

    $('#TokenTrnslt').click(function () {
        $("#mainContentDIV").load('TranslateToken.php?contentID=' + $("#ContentID").val() + '&mode=' + mode);
    });

    $('#SgmntTrnslt').click(function () {
        $("#mainContentDIV").load('TranslateSegment.php?contentID=' + $("#ContentID").val() + '&mode=' + mode);
    });

    $('#MultiWordAnnotation').click(function () {
        $("#mainContentDIV").load('AnnotateMWE.php?contentID=' + $("#ContentID").val() + '&mode=' + mode);
    });

    $('#UploadLemmaTranslation').change(function() {
        $("#task").val("UploadLemmaTranslation");
        saveSubContentTranslation();
    });

    $('#UploadTypeTranslation').change(function() {
        $("#task").val("UploadTypeTranslation");
        saveSubContentTranslation();
    });

    $('#UploadTokenTranslation').change(function() {
        $("#task").val("UploadTokenTranslation");
        saveSubContentTranslation();
    });

    $('#UploadSegmentTranslation').change(function() {
        $("#task").val("UploadSegmentTranslation");
        saveSubContentTranslation();
    });

    $( "#TranslationAndRecordingDiv" ).accordion({
        collapsible: true,
        active : 0,
        heightStyle: "content"
    });

    if($("#WebAddress").val() != "") {

        var ContentName = $('#ContentName').val();
        var FolderName = ContentName.replace(/ /g,"_") + 'vocabpages';

        var cmpld = "&folderDir=" + contentVal["DirName"] + "&folderName=" + FolderName;
        $('#CompiledFolderDL').attr("href","../SharedModules/DownloadFile.php?download=compiledContent" + cmpld);

        $("#WebAddressTR").css("display", "");
        $("#CompiledFolderDLTR").css("display", "");
    }

    $( "#tabs" ).tabs();
    $( "#tabs" ).tabs( "option", "active", activeTab);

    if(msgToShow != "notSetYet")
    {
        showMessageOnload(msgToShow);
    }

    if($('#EditMode').val() == "crowdWorker")
    {
        $('#firstStep').find('input, textarea, button, select').attr('disabled',true);
        $('#WordAudio').attr('disabled', false);
        $('#SegmentAudio').attr('disabled', false);
		$('#WordsAudioType_human').attr('disabled', false);
		$('#WordsAudioType_tts').attr('disabled', false);
		$('#SegmentsAudioType_human').attr('disabled', false);
		$('#SegmentsAudioType_tts').attr('disabled', false);
		$('#TtsEngineTR').attr('disabled', false);
		$('#TtsVoiceTR').attr('disabled', false);
		$('#WordTranslationMouseOver_Y').attr('disabled', false);
		$('#WordTranslationMouseOver_N').attr('disabled', false);
		$('#SegmentTranslationMouseOver_Y').attr('disabled', false);
		$('#SegmentTranslationMouseOver_N').attr('disabled', false);
		$('#AudioMouseOver_Y').attr('disabled', false);
		$('#AudioMouseOver_N').attr('disabled', false);
		$('#AudioSegments_Y').attr('disabled', false);
		$('#AudioSegments_N').attr('disabled', false);
        $('#TaggedText').attr('disabled', false);
        $('#CreateResourceButton').attr('disabled', false);
    }

}

$("#L2ID").change(function(e) {
    $('#TreeTaggerStatus').prop('checked', false);
    $("#RawTextTR").css("display","none");
    $("#OnServerRawTextTR").css("display","");
    $("#TreeTaggerResultTR").css("display","");
    $("#PosTaggerTR").css("display","none");
    $("#ComplementaryDiv").css("display","");
    $("#TaggingButton").css("display","none");
    $("#SetConfigButton").css("display","");
    $("#CreateResourceButton").css("display","");
    var valueSelected = this.value;

    var url = "../data/Language.data.php";
    var data = "LanguageID=" + valueSelected + "&task=hasTreeTagger";

    $.ajax({
        url: url,
        type: "post",
        data: data,
        success: function(response) {
            if (response.indexOf("YES") != -1) {
                $("#TreeTaggerStatusTR").css("display","");
            }
            else {
                $("#TreeTaggerStatusTR").css("display", "none");
            }
        }
    });


    $('#ttsEngines').empty();
    $('#tssEngineVoices').empty();
    var url = "../data/Content.data.php";
    var data = "LanguageID=" + valueSelected + "&task=TtsEnginesList";

    $.ajax({
        url: url,
        type: "post",
        data: data,
        success: function(response) {
            enginesAndVoices = $.parseJSON(response);
            loadTtsEngines();
        }
    });
});

$("#RawText").change(function(e) {
    var PrvRawText = $("#RawTextFileName").val();
    var fileName = e.target.files[0].name;
    if(PrvRawText != "")
    {
        var confMsg = "You have already uploaded " + PrvRawText + " and the tagged file is ready to download. " +
            "Are you sure you want to tag another file?"
        if(confirm(confMsg))
        {
            var alrtMsg = "Okay.. New file named " + fileName + " is selected. Do not forget to click on" +
                " 'Tag Raw text' button to tag it.";
            alert(alrtMsg);
            $('#rawFileName').css("display", "");
            $('#rawFileName').html(fileName);
            $('#TreeTaggerPRV').css("display", "none");
        }
        else
        {
            $("#RawText").val('');
        }
    }
    else
    {
        $('#rawFileName').css("display", "");
        $('#rawFileName').html(fileName);
    }

});

$("#TaggedText").change(function(e) {
    var PrvTaggedText = $("#TaggedTextFileName").val();
    var fileName = e.target.files[0].name;
    if(PrvTaggedText != "")
    {
        var confMsg = "You have already uploaded " + PrvTaggedText + " and made resources for it. " +
            "Are you sure you want to change it?"
        if(confirm(confMsg))
        {
            var alrtMsg = "Okay.. New file named " + fileName + " is selected. Do not forget to click on" +
                " 'Create Resources' button. Keep in mind that the resources might change.";
            alert(alrtMsg);
            $('#taggedFileName').css("display", "");
            $('#taggedFileName').html(fileName);
            $('#TaggedPRV').css("display", "none");

        }
        else
        {
            $("#TaggedText").val('');
        }
    }
    else
    {
        $('#taggedFileName').css("display", "");
        $('#taggedFileName').html(fileName);
    }
});

$("#EmbeddedAudio").change(function(e) {
    var fileName = e.target.files[0].name;
    $('#eAudioFileName').css("display", "");
    $('#eAudioFileName').html(fileName);
});

$("#EmbeddedCss").change(function(e) {
    var fileName = e.target.files[0].name;
    $('#eCssFileName').css("display", "");
    $('#eCssFileName').html(fileName);
});

$("#EmbeddedImage").change(function(e) {
    var fileName = e.target.files[0].name;
    $('#eImageFileName').css("display", "");
    $('#eImageFileName').html(fileName);
});

$("#EmbeddedScript").change(function(e) {
    var fileName = e.target.files[0].name;
    $('#eScriptFileName').css("display", "");
    $('#eScriptFileName').html(fileName);
});

$( "#TreeTaggerStatus").change(function(e) {
    var $input = $( this );
    if($input.is( ":checked" )){
        $("#RawTextTR").css("display","");
        $("#OnServerRawTextTR").css("display","");
        $("#TreeTaggerResultTR").css("display","");
        $("#PosTaggerTR").css("display","");
        $("#ComplementaryDiv").css("display","none");
        $("#TaggingButton").css("display","");
        $("#SetConfigButton").css("display","none");
        $("#CreateResourceButton").css("display","none");
    }
    else
    {
        $("#RawTextTR").css("display","none");
        $("#OnServerRawTextTR").css("display","none");
        $("#TreeTaggerResultTR").css("display","none");
        $("#PosTaggerTR").css("display","none");
        $("#ComplementaryDiv").css("display","");
        $("#TaggingButton").css("display","none");
        $("#SetConfigButton").css("display","");
        $("#CreateResourceButton").css("display","");
    }
});

$( "#WTFC_checkbox").change(function(e) {
    var $input = $( this );
    if($input.is( ":checked" )){
        $("#WTFC_lemma").prop("disabled", false);
        $("#WTFC_token").prop("disabled", false);
    }
    else
    {
        $("#WTFC_lemma").prop("disabled", true);
        $("#WTFC_token").prop("disabled", true);
    }
});

$( "#WAFC_checkbox").change(function(e) {
    var $input = $( this );
    if($input.is( ":checked" )){
        $("#WAFC_lemma").prop("disabled", false);
        $("#WAFC_token").prop("disabled", false);
    }
    else
    {
        $("#WAFC_lemma").prop("disabled", true);
        $("#WAFC_token").prop("disabled", true);
    }
});

$("input[name='WordsAudioType']").click(function(e) {
    if($("input[name='WordsAudioType']:checked").val() == 'tts')
    {
        $("#TtsEngineTR").css("display","");
        $("#TtsVoiceTR").css("display","");
        $("#WordAudioTR").css("display","none");
        if($("input[name='SegmentsAudioType']:checked").val() == 'tts')
            $("#LdtDeactivateStatusTR").css("display","none");
    }
    else
    {
        $("#WordAudioTR").css("display","");
        $("#LdtDeactivateStatusTR").css("display","");
        if($("input[name='SegmentsAudioType']:checked").val() == 'human')
        {
            $("#TtsEngineTR").css("display","none");
            $("#TtsVoiceTR").css("display","none");
        }
    }
});

$("input[name='SegmentsAudioType']").click(function(e) {
    if($("input[name='SegmentsAudioType']:checked").val() == 'tts')
    {
        $("#TtsEngineTR").css("display","");
        $("#TtsVoiceTR").css("display","");
        $("#SegmentAudioTR").css("display","none");
        if($("input[name='WordsAudioType']:checked").val() == 'tts')
            $("#LdtDeactivateStatusTR").css("display","none");
    }
    else
    {
        $("#LdtDeactivateStatusTR").css("display","");
        $("#SegmentAudioTR").css("display","");
        if($("input[name='WordsAudioType']:checked").val() == 'human')
        {
            $("#TtsEngineTR").css("display","none");
            $("#TtsVoiceTR").css("display","none");
        }
    }
});

$("input[name='LdtDeactivateStatus']").click(function(e) {
    if($("input[name='LdtDeactivateStatus']:checked").val() == 'YES')
    {
        $("#WordAudioTR").css("display","none");
        $("#SegmentAudioTR").css("display","none");
    }
    else
    {
        $("#WordAudioTR").css("display","");
        $("#SegmentAudioTR").css("display","");
    }
});

$("#ExternalResource").change(function(e) {
    var fileName = e.target.files[0].name;
    $('#ExternalResFileName').css("display", "");
    $('#ExternalResFileName').html(fileName);
});

$( "#ContentCssStatus").change(function(e) {
    var $input = $( this );
    if($input.is( ":checked" )){
        $("#ContentCssTR").css("display","");
    }
    else{
        $("#ContentCssTR").css("display","none");
    }
});

$("#ContentCss").change(function(e) {
    var fileName = e.target.files[0].name;
    $('#ContentCssFileNameSpan').css("display", "");
    $('#ContentCssFileNameSpan').html(fileName);
});

$( "#ContentJsStatus").change(function(e) {
    var $input = $( this );
    if($input.is( ":checked" )){
        $("#ContentJsTR").css("display","");
    }
    else{
        $("#ContentJsTR").css("display","none");
    }
});

$("#ContentJs").change(function(e) {
    var fileName = e.target.files[0].name;
    $('#ContentJsFileNameSpan').css("display", "");
    $('#ContentJsFileNameSpan').html(fileName);
});

$( "#PinyinStatus").change(function(e) {
    var $input = $( this );
    if($input.is( ":checked" )){
        $("#PinyinTR").css("display","");
    }
    else{
        $("#PinyinTR").css("display","none");
    }
});

$("#PinyinFile").change(function(e) {
    var fileName = e.target.files[0].name;
    $('#PinyinFileNameSpan').css("display", "");
    $('#PinyinFileNameSpan').html(fileName);
});

$( "#TtsSubstitutionStatus").change(function(e) {
    var $input = $( this );
    if($input.is( ":checked" )){
        $("#TtsSubstitutionTR").css("display","");
    }
    else{
        $("#TtsSubstitutionTR").css("display","none");
    }
});

$("#TtsSubstitutionFile").change(function(e) {
    var fileName = e.target.files[0].name;
    $('#TtsSubstitutionFileNameSpan').css("display", "");
    $('#TtsSubstitutionFileNameSpan').html(fileName);
});


function loadTtsEngines()
{
    if(enginesAndVoices.length == 0)
    {
        $('#ttsEngines').html("No TTS engine available for this language");
        $('#tssEngineVoices').html("----");
        return;
    }
    $('#tssEngineVoices').empty();

    var ttsEngineDrp = "<select name='TtsEngine' id='TtsEngine'>";
    ttsEngineDrp += "<option value=-1>---</option>";

    for(let i = 0; i < enginesAndVoices['engines'].length; i++) {
        ttsEngineDrp += "<option value='" + enginesAndVoices['engines'][i] + "' " ;
        if($('#L2ID').val() == contentVal["L2ID"] &&
            enginesAndVoices['engines'][i] == contentVal["TtsEngine"])
        {
            ttsEngineDrp += "selected";
            loadTtsVoices(contentVal["TtsEngine"]);
        }
        ttsEngineDrp += " >" + enginesAndVoices['engines'][i] + "</option>";
    }
    ttsEngineDrp += "</select>";
    $('#ttsEngines').html(ttsEngineDrp);
}

document.addEventListener('change',function(e){
    if(e.target && e.target.id== 'TtsEngine')
        loadTtsVoices($('#TtsEngine').val());
});

function loadTtsVoices(detailDrpName)
{
    var ttsVoiceDrp = "<select name='TtsVoice' id='TtsVoice'>";
    ttsVoiceDrp += "<option value=-1>---</option>";

    for(let i = 0; i < enginesAndVoices[detailDrpName].length; i++) {
        ttsVoiceDrp += "<option value='" + enginesAndVoices[detailDrpName][i] + "' ";
        if(enginesAndVoices[detailDrpName][i] == contentVal["TtsVoice"])
            ttsVoiceDrp += "selected";
        ttsVoiceDrp += " >" + enginesAndVoices[detailDrpName][i] + "</option>";
    }
    ttsVoiceDrp += "</select>";
    $('#tssEngineVoices').html(ttsVoiceDrp);
}

function createResources(taskType)
{
    var activeTab = 0;
    $("#task").prop("value",TaskValues[taskType]);
    var mode = $("#EditMode").val();

    //task values : "TagRawText" OR "SetConfig" or "CreateResources"
    if(validateConfigFileForm())
    {
        $('#firstStep').find('input, textarea, button, select').attr('disabled',false);

        showLoading('#mainContentDIV');
        var form = $('#configFileForm');
        var formdata = false;
        if (window.FormData){
            formdata = new FormData(form[0]);
        }
        var data = formdata ? formdata : form.serialize();
        $.ajax({
            url         : '../data/Content.data.php',
            data        : data,
            cache       : false,
            contentType : false,
            processData : false,
            type        : 'POST',
            success: function (response) {
                hideLoading('#mainContentDIV');
                var reqResponse = $.parseJSON(response);
                var responseMsg = reqResponse[0].resultMsg;
                var responseID =  reqResponse[0].id;
                $("#mainContentDIV").load('NewLARAContent.php?Q0=' + responseID +
                            '&activeTab=' + activeTab + '&msg=' + responseMsg + '&mode=' + mode);

            },
            error: function(jqXHR, textStatus, errorThrown) {
                hideLoading('#mainContentDIV');
                console.log(textStatus, errorThrown);
                alert("Something is wrong here.");
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

function createPages()
{
    var activeTab = 2;
    var mode = $("#EditMode").val();

    showLoading('#mainContentDIV');
    var data = { task: "CreatePages", contentID :  $("#ContentID").val(),
        tokenType : $("#tokenType").val(), accessToken : $("#accessToken").val()};
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

            $("#mainContentDIV").load('NewLARAContent.php?Q0=' + responseID +
                '&activeTab=' + activeTab + '&msg=' + responseMsg + '&mode=' + mode);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
            alert("Something is wrong here.");
        }
    });
}

function publishResource()
{
    var activeTab = 2;
    var mode = $("#EditMode").val();
    var confMsg = "Are you sure you want to publish " + $('#ContentName').val() + "?";

    if(confirm(confMsg))
    {
        showLoading('#mainContentDIV');
        var data = { task: "PublishContent", contentID :  $('#ContentID').val()};
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

                $("#mainContentDIV").load('NewLARAContent.php?Q0=' + responseID +
                    '&activeTab=' + activeTab + '&msg=' + responseMsg+ '&mode=' + mode);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                hideLoading('#mainContentDIV');
                console.log(textStatus, errorThrown);
                alert("Something is wrong here.");
            }
        });
    }
}

function validateConfigFileForm()
{
    var ContentName = $('#ContentName').val();
    var laraIdPattern = /^[A-Za-z\u00C0-\u017F0-9_-\s]+$/;

    var L1 = $('#L1ID').val();
    var L2 = $('#L2ID').val();

    $('.configFileError').css("display", "");

    if(ContentName == "")
    {
        $('.ErrorMsg').html('Please enter a name for the text');
        return false;
    }

    if(!laraIdPattern.test(ContentName))
    {
        $('.ErrorMsg').html("Text name can't include anything except uppercase and lowercase letters, numbers, - and _.");
        return false;
    }
    if(L1 == -1)
    {
        $('.ErrorMsg').html('Please select a language as translation language');
        return false;
    }

    if(L2 == -1)
    {
        $('.ErrorMsg').html('Please select a language as reading language');
        return false;
    }

    var currentRawText = $('#RawText').val();
    var currentTaggedText = $("#TaggedText").val();
    var currentImage = $("#EmbeddedImage").val();
    var currentAudio = $("#EmbeddedAudio").val();
    var currentCss = $("#EmbeddedCss").val();
    var currentScript = $("#EmbeddedScript").val();
    var currentExtRes = $("#ExternalResource").val();
    var currentContentCss = $("#ContentCss").val();
    var currentContentJs = $("#ContentJs").val();
    var currentPinyin = $("#PinyinFile").val();
    var currentTtsSubstitution = $("#TtsSubstitutionFile").val();

    if(currentRawText != '' &&
        (currentTaggedText != '' ||
         currentImage != '' ||
         currentAudio != '' ||
         currentCss != '' ||
         currentScript != '' ||
         currentExtRes != '' ||
         currentContentCss != '' ||
         currentContentJs != ''||
         currentPinyin != '' ||
         currentTtsSubstitution != ''))
    {
        if($("#task").val() == TaskValues[2])//create resource
        {
            var msg = "You have selected new file for tagging. Are you sure you want to ignore it" +
                " and create resources for " + currentTaggedText + "?";
            if(!confirm(msg))
            {
                return false;
            }
        }
        else if($("#task").val() == TaskValues[0])//tag raw text
        {
            var msg = "Are you sure you want to ignore creating resources " +
                " and tag " + currentRawText + "?";
            if(!confirm(msg))
            {
                return false;
            }
        }
    }

    if($("#task").val() == TaskValues[1] || $("#task").val() == TaskValues[2])//create resource or set configuration
    {
        var WordAudioVal = $('#WordAudio').val();
        var SegmentAudioVal = $('#SegmentAudio').val();
        var notSelectedItems = new Array();
        var notSelectedItemsIndex = 0;

        if (!$("input[name='L1rtl']").is(':checked'))
        {
            notSelectedItems[notSelectedItemsIndex] = "Reading language is Right to Left";
            notSelectedItemsIndex++;
        }
        if (!$("input[name='AudioMouseOver']").is(':checked'))
        {
            notSelectedItems[notSelectedItemsIndex] = "Audio mouseover";
            notSelectedItemsIndex++;
        }
        if (!$("input[name='WordTranslationMouseOver']").is(':checked'))
        {
            notSelectedItems[notSelectedItemsIndex] = "Word translation mouseOver";
            notSelectedItemsIndex++;
        }
        if (!$("input[name='SegmentTranslationMouseOver']").is(':checked'))
        {
            notSelectedItems[notSelectedItemsIndex] = "Segment translation mouseOver";
            notSelectedItemsIndex++;
        }
        if (!$("input[name='AudioSegments']").is(':checked'))
        {
            notSelectedItems[notSelectedItemsIndex] = "Segment audio mouseOver";
            notSelectedItemsIndex++;
        }
        if(notSelectedItemsIndex != 0)
        {
            var errorMsg = "Please select a value for these items:</br>";
            for(i = 0 ; i < notSelectedItems.length; i++)
            {
                errorMsg += notSelectedItems[i] + "</br>";
            }
            $('.ErrorMsg').html(errorMsg);
            return false;
        }

        var PrvTaggedText = $("#TaggedTextFileName").val();
        var AutomatedTaggedText = $("#AutomatedTaggedTextFileName").val();

        var ext = $('#TaggedText').val().split('.').pop().toLowerCase();

        if(currentTaggedText == "" && PrvTaggedText == "" && AutomatedTaggedText == "")
        {
            $('.ErrorMsg').html('please upload the tagged Text File.');
            return false;
        }
        if(currentTaggedText != "" && $.inArray(ext, ['txt', 'docx']) == -1) {
            $('.ErrorMsg').html('Invalid extention! Please upload a .txt or .docx File.');
            return false;
        }

        //Let's do some checking about embedded items
        if($("#HasEmbeddedImage").val == 'YES' && currentImage == '')
        {
            var msg = "Are you sure you want to continue without uploading images?";
            if(!confirm(msg))
            {
                return false;
            }
        }
        if($("#HasEmbeddedAudio").val == 'YES' && currentAudio == '')
        {
            var msg = "Are you sure you want to continue without uploading audios?";
            if(!confirm(msg))
            {
                return false;
            }
        }
        if($("#HasEmbeddedCSS").val == 'YES' && currentCss == '')
        {
            var msg = "Are you sure you want to continue without uploading css files? ";
            if(!confirm(msg))
            {
                return false;
            }
        }
        if($("#HasEmbeddedScript").val == 'YES' && currentScript == '')
        {
            var msg = "Are you sure you want to continue without uploading scripts? ";
            if(!confirm(msg))
            {
                return false;
            }
        }

        if($("#ContentCssStatus").is(":checked") && currentContentCss == '')
        {
            var msg = "Are you sure you want to continue without uploading CSS file? ";
            if(!confirm(msg))
            {
                return false;
            }
        }
        if($("#HasContentCss").val == 'YES' && $("#ContentCssStatus").is(":checked") && currentContentCss != '')
        {
            var msg = "You have already import a CSS file. Are you sure you want to add another one?";
            if(!confirm(msg))
            {
                return false;
            }
        }
        if($("#ContentJsStatus").is(":checked") && currentContentJs == '')
        {
            var msg = "Are you sure you want to continue without uploading JS file? ";
            if(!confirm(msg))
            {
                return false;
            }
        }
        if($("#HasContentJs").val == 'YES' && $("#ContentJsStatus").is(":checked") && currentContentJs != '')
        {
            var msg = "You have already import a JS file. Are you sure you want to add another one?";
            if(!confirm(msg))
            {
                return false;
            }
        }
        if($("#PinyinStatus").is(":checked") && currentPinyin == '')
        {
            var msg = "Are you sure you want to continue without uploading CSS file? ";
            if(!confirm(msg))
            {
                return false;
            }
        }
        if($("#HasPinyin").val == 'YES' && $("#PinyinStatus").is(":checked") && currentPinyin != '')
        {
            var msg = "You have already import a Pinyin file. Are you sure you want to add another one?";
            if(!confirm(msg))
            {
                return false;
            }
        }

        if($("#TtsSubstitutionStatus").is(":checked") && currentTtsSubstitution == '')
        {
            var msg = "Are you sure you want to continue without uploading TTS substitution file? ";
            if(!confirm(msg))
            {
                return false;
            }
        }
        if($("#HasTtsSubstitution").val == 'YES' && $("#TtsSubstitutionStatus").is(":checked") && currentTtsSubstitution != '')
        {
            var msg = "You have already import a TTS substitution file. Are you sure you want to add another one?";
            if(!confirm(msg))
            {
                return false;
            }
        }


    }
    else if($("#task").val() == TaskValues[0])//tag raw text
    {
        var PrvRawText = $("#RawTextFileName").val();
        var ext = $('#RawText').val().split('.').pop().toLowerCase();

        if(currentRawText == "" && PrvRawText == "")
        {
            $('.ErrorMsg').html('Please upload the raw text file.');
            return false;
        }
        if(currentRawText != "" && $.inArray(ext, ['txt', 'docx']) == -1) {
            $('.ErrorMsg').html('Invalid extention! Please upload a .txt or docx file.');
            return false;
        }
    }

    $('.configFileError').css("display", "none");
    return true;
}

function applyTypeToToken()
{
    var activeTab = 1;
    var mode = $("#EditMode").val();

    var data = { task: "ApplyTypeToToken", contentID :  $('#ContentID').val()};
    showLoading('#mainContentDIV');

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

            $("#mainContentDIV").load('NewLARAContent.php?Q0=' + responseID +
                '&activeTab=' + activeTab + '&msg=' + responseMsg+ '&mode=' + mode);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
            alert("Something is wrong in applying translation");
        }
    });
}

function saveSubContentTranslation()
{
    var activeTab = 1;
    var mode = $("#EditMode").val();

    var form = $('#configFileForm');
    var formdata = false;
    if (window.FormData){
        formdata = new FormData(form[0]);
    }
    var data = formdata ? formdata : form.serialize();
    showLoading('#mainContentDIV');
    $.ajax({
        url         : '../data/SegmentsAndWords.data.php',
        data        : data,
        cache       : false,
        contentType : false,
        processData : false,
        type        : 'POST',
        success: function (response) {
            hideLoading('#mainContentDIV');
            var reqResponse = $.parseJSON(response);
            var responseMsg = reqResponse[0].resultMsg;
            var responseID =  reqResponse[0].id;

            $("#mainContentDIV").load('NewLARAContent.php?Q0=' + responseID +
                '&activeTab=' + activeTab + '&msg=' + responseMsg + '&mode=' + mode);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
            alert("Something is wrong here");
        }
    });
}

function showMessageOnload(message)
{
    var msgText = getMsgText(message);
    $('.configFileError').css("display", "");
    $('.ErrorMsg').html(msgText);
}

function getMsgText(responseMsg)
{
    var msgToShow;
    if (responseMsg == "fileUploadError")
    {
        msgToShow = "You should upload a text file as raw text.";
    }
    else if (responseMsg == "RtFileTypeError")
    {
        msgToShow = "Uploaded raw text file must be a txt or docx.";
    }
    else if (responseMsg == "RtFileUnicodeError")
    {
        msgToShow = "Uploaded raw text file encoding not supported.";
    }
    else if (responseMsg == "TtFileTypeError")
    {
        msgToShow = "Uploaded tagged text file must be a txt or docx.";
    }
    else if (responseMsg == "TtFileUnicodeError")
    {
        msgToShow = "Uploaded tagged text file encoding not supported.";
    }
    else if (responseMsg == "FileSizeError")
    {
        msgToShow = "The maximum upload size for files exceeded.";
    }
    else if (responseMsg == "extResTypeError")
    {
        msgToShow = "External resources must be uploaded in zip format.";
    }
    else if (responseMsg == "contentCssTypeError")
    {
        msgToShow = "Content css must be uploaded in css format.";
    }
    else if (responseMsg == "contentJsTypeError")
    {
        msgToShow = "Content js must be uploaded in js format.";
    }
    else if (responseMsg == "pinyinTypeError")
    {
        msgToShow = "Pinyin must be uploaded in txt format.";
    }
    else if (responseMsg == "ttsSubstitutionTypeError")
    {
        msgToShow = "TTS Substitution must be uploaded in csv format.";
    }
    else if (responseMsg == "eAudioTypeError")
    {
        msgToShow = "Embedded audios must be uploaded in zip format.";
    }
    else if (responseMsg == "eCSSTypeError")
    {
        msgToShow = "Embedded CSS must be uploaded in zip format.";
    }
    else if (responseMsg == "eImageTypeError")
    {
        msgToShow = "Embedded images must be uploaded in zip format.";
    }
    else if (responseMsg == "eScriptTypeError")
    {
        msgToShow = "Embedded scripts must be uploaded in zip format.";
    }
    else if (responseMsg == "CreateDIRFailedCreateResources" ||
             responseMsg == "CreateDIRFailedExtMerg" ||
             responseMsg == "CreateDIRFailedExtRoot" ||
             responseMsg == "CreateDIRFailedExtTmp" ||
             responseMsg == "CreateDIRFailedSaveTranslation" ||
             responseMsg == "CreateDIRFailedTagRawText" ||
             responseMsg == "CreateDIRFailedUploadTranslation" ||
             responseMsg == "CreateDIRFailedImportLaraContent" )
    {
        msgToShow = "Failed to create the directory.";
    }
    else if (responseMsg == "CreateSubDIRFailedTagRawText" ||
             responseMsg == "CreateSubDIRFailedCreateResources" ||
             responseMsg == "CreateSubDIRFailedImportLaraContent")
    {
        msgToShow = "Failed to create one of the subdirectories.";
    }
    else if (responseMsg == "UploadFileFailedTagRawText" ||
             responseMsg == "UploadFileFailedCreateResources"||
             responseMsg == "UploadFileFailedImportLaraContent"||
             responseMsg == "UploadFileFailedUploadTranslation" )
    {
        msgToShow = "Failed to upload the file.";
    }
    else if (responseMsg == "TaggedFileFailed")
    {
        msgToShow = "Failed to tag the file.";
    }
    else if (responseMsg == "TaggedFileCreated")
    {
        msgToShow = "Tagged file is created and ready to download.";
    }
    else if (responseMsg == "FirstCompileStepFailed")
    {
        msgToShow = "Failed to complete the first phase of compiling.";
    }
    else if (responseMsg == "CreateLDTTaskFailed")
    {
        msgToShow = "Failed to create LDT task for audio parts.";
    }
    else if (responseMsg == "FirstCompileStepDone")
    {
        msgToShow = "Resources are created and ready to download.";
    }
    else if (responseMsg == "FirstCompileStepWithWarningDone")
    {
        msgToShow = "Resources are created, but there are some warnings.";
    }
    else if (responseMsg == "hasEmbedded")
    {
        msgToShow = "The tagged file has embedded media. Please upload them.";
    }
    else if (responseMsg == "FailedToOpenZipFile")
    {
        msgToShow = "Unable to open the the uploaded zip file.";
    }
    else if (responseMsg == "FailedToExtractZipFile")
    {
        msgToShow = "Unable to extract the uploaded zip file.";
    }
    else if (responseMsg == "FailedToExtractExtResFile")
    {
        msgToShow = "Unable to extract the uploaded zip file for External resource.";
    }
    else if (responseMsg == "MergeLanguageResourcesFailed")
    {
        msgToShow = "Unable to merge the uploaded file for External resource.";
    }
    else if(responseMsg == "ConfigParamsSet")
    {
        msgToShow = "Configuration parameters set successfully.";
    }
    else if(responseMsg == "InstallPrvAudioFailed")
    {
        msgToShow = "Downloading recorded audio from LDT failed. You can continue creating pages after deactivating audio recording in the 'create resources' tab.";
    }
    else if(responseMsg == "InstallPrvTTSWordFailed")
    {
        msgToShow = "Installing already generated TTS audio for words failed.";
    }
    else if(responseMsg == "InstallPrvTTSSegmentsFailed")
    {
        msgToShow = "Installing already generated TTS audio for segments failed.";
    }
    else if(responseMsg == "MetadataToDatabaseFailed")
    {
        msgToShow = "Saving metadata info to database failed.";
    }
    else if(responseMsg == "DeletePrvWordFailed")
    {
        msgToShow = "Deleting previous recorded audio for words failed.";
    }
    else if(responseMsg == "DeletePrvSegFailed")
    {
        msgToShow = "Deleting previous recorded audio for segments failed.";
    }
    else if(responseMsg == "CreateMultiWordAnnotationFailed")
    {
        msgToShow = "Creating multi word annotation failed.";
    }
    else if(responseMsg == "FailToSegmentize")
    {
        msgToShow = "Auto segmentation failed.";
    }
    else if(responseMsg == "DownloadFromLdtFailed")
    {
        msgToShow = "Downloading recorded audio from LDT failed. You can continue creating pages after deactivating audio recording in the 'create resources' tab.";
    }
    else if(responseMsg == "InstallNonLDTAudioFailed")
    {
        msgToShow = "Installing non-ldt recorded audio failed.";
    }
    else if(responseMsg == "PageCreationDone")
    {
        msgToShow = "Pages are created and copied to the web.";
    }
    else if(responseMsg == "CopyingPagesFailed")
    {
        msgToShow = "Copying pages to web failed.";
    }
    else if(responseMsg == "CopyingPagesForSnFailed")
    {
        msgToShow = "Copying pages for social network failed.";
    }
    else if(responseMsg == "CreatePagesFailed")
    {
        msgToShow = "Creating pages failed.";
    }
    else if(responseMsg == "CreatePagesForSnFailed")
    {
        msgToShow = "Creating pages for social network failed.";
    }
    else if(responseMsg == "InstallZipfileFailed")
    {
        msgToShow = "Installing recorded audio from LDT failed.";
    }
    else if(responseMsg == "InstallTTSWordsFailed")
    {
        msgToShow = "Installing words tts audio failed.";
    }
    else if(responseMsg == "InstallTTSSegmentsFailed")
    {
        msgToShow = "Installing segments tts audio failed.";
    }
    else if(responseMsg == "FailedToCopyResource")
    {
        msgToShow = "Failed to copy content resource.";
    }
    else if(responseMsg == "FailedToCopyLangResource")
    {
        msgToShow = "Failed to copy language resource.";
    }
    else if(responseMsg == "FailedPublish")
    {
        msgToShow = "Failed to publish.";
    }
    else if(responseMsg == "FailedToExtractPageNamesPublish")
    {
        msgToShow = "Could not extract the page names of the resource.";
    }
    else if(responseMsg == "SuccessfulPublish")
    {
        msgToShow = "Resource is published successfully.";
    }
    else if (responseMsg == "fileTypeError")
    {
        msgToShow = "Uploaded file format must be CSV.";
    }
    else if (responseMsg == "FinalCopyFailedSaveTranslation" ||
             responseMsg == "FinalCopyFailedUploadTranslation")
    {
        msgToShow = "Copied to final destination failed!";
    }
    else if (responseMsg == "UploadedAndCopied")
    {
        msgToShow = "Saved and copied to final destination!";
    }
    else if (responseMsg == "TransferToDbFailed")
    {
        msgToShow = "Transferring to database failed!";
    }
    else if (responseMsg == "UploadJsFileFailed")
    {
        msgToShow = "Uploading js file to server failed!";
    }
    else if (responseMsg == "UploadCssFileFailed")
    {
        msgToShow = "Uploading css file to server failed!";
    }
    else if (responseMsg == "UploadPinyinFileFailed")
    {
        msgToShow = "Uploading pinyin file to server failed!";
    }
    else if (responseMsg == "UploadTtsSubstitutionFileFailed")
    {
        msgToShow = "Uploading TTS Substitution file to server failed!";
    }
    else if (responseMsg == "SuccessfullyImported")
    {
        msgToShow = "Content imports successfully and you can check it in your list.";
    }
    else if (responseMsg == "FulfillingFailed")
    {
        msgToShow = "Failed to fulfill the content.";
    }
    else if (responseMsg == "ImportZipFileFailed")
    {
        msgToShow = "Failed to import content.";
    }
    else if(responseMsg == "LoginToLdtFailed")
    {
        msgToShow = "Failed to log into LDT.";
    }
    else if(responseMsg == "FileUploadErrorImportLaraContent")
    {
        msgToShow = "Failed to send zip file to the server.";
    }
    else if(responseMsg == "FailedToApplyTypes")
    {
        msgToShow = "Failed to apply type translation in tokens.";
    }
    else if(responseMsg == "TypeTranslationApplied")
    {
        msgToShow = "You can now check the token translation.";
    }
    else if(responseMsg == "SegmentTTSDone")
    {
        msgToShow = "TTS files for segments are ready.";
    }
    else if(responseMsg == "WordTTSDone")
    {
        msgToShow = "TTS files for words are ready.";
    }
    else if(responseMsg == "FailedToTransferToLemma")
    {
        msgToShow = "Failed to transfer Lemmas.";
    }
    else if(responseMsg == "FailedToTransferToLemmaExample")
    {
        msgToShow = "Failed to transfer Lemma examples.";
    }
    else if(responseMsg == "FailedToTransferToMultiWord")
    {
        msgToShow = "Failed to transfer multi words.";
    }
    else if(responseMsg == "FailedToTransferToMultiWordIndex")
    {
        msgToShow = "Failed to transfer multi word indexes.";
    }
    else if(responseMsg == "FailedToTransferToMultiWordChunk")
    {
        msgToShow = "Failed to transfer multi word chunks.";
    }
    else if(responseMsg == "FailedToTransferToType")
    {
        msgToShow = "Failed to transfer Types.";
    }
    else if(responseMsg == "FailedToTransferToTypeExample")
    {
        msgToShow = "Failed to transfer Type examples.";
    }
    else if(responseMsg == "FailedToTransferToSegment")
    {
        msgToShow = "Failed to transfer Segments.";
    }
    else if(responseMsg == "FailedToTransferToToken")
    {
        msgToShow = "Failed to transfer Tokens.";
    }
    else if(responseMsg == "FailedToTransferToRawSegment")
    {
        msgToShow = "Failed to transfer Split segments.";
    }
    else if(responseMsg == "FailedToTransferToRawParticle")
    {
        msgToShow = "Failed to transfer Split particles.";
    }
    else if(responseMsg == "DataFromFileIsSavedForItems")
    {
        msgToShow = "Uploaded data in file saved successfully.";
    }
    else if(responseMsg == "FailedToGenerateSegmentsTTS")
    {
        msgToShow = "Failed to generate tts files for segments.";
    }
    else if(responseMsg == "FailedToGenerateWordsTTS")
    {
        msgToShow = "Failed to generate tts files for words.";
    }
    return msgToShow;
}

function generateTTS(type)
{
    var activeTab = 1;
    var mode = $("#EditMode").val();
    var task;
    if(type == "segment")
        task = "GenerateSegmentsTTS";
    else if(type == "word")
        task = "GenerateWordsTTS";

    var data = { task: task, contentID :  $('#ContentID').val()};
    showLoading('#mainContentDIV');

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

            $("#mainContentDIV").load('NewLARAContent.php?Q0=' + responseID +
                '&activeTab=' + activeTab + '&msg=' + responseMsg+ '&mode=' + mode);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            hideLoading('#mainContentDIV');
            console.log(textStatus, errorThrown);
            alert("Something is wrong in applying translation");
        }
    });
}