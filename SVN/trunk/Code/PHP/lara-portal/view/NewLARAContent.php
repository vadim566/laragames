<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 4/16/2019

 */

?>

<link rel="stylesheet" href="../css/MainContent.css">
<link rel="stylesheet" href="../css/TableToDiv.css">
<link rel="stylesheet" href="../SharedModules/jquery/jquery-ui.css">
<meta charset="utf-8">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

<?php
    $now = new DateTime();
    echo '<script src="../js/NewLaraContent.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/jquery/jquery-1.12.4.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/jquery/jquery-ui.js?' . $now->format('His') . '"></script>';

require_once '../Config.php';
require_once '../SharedModules/ExtraModules.class.php';
require_once '../class/Language.class.php';
require_once '../class/Account.class.php';
require_once '../class/Content.class.php';
require_once '../data/Content.data.php';
require_once '../class/ContentSegment.class.php';
require_once '../class/ContentLemma.class.php';
require_once '../class/ContentType.class.php';
require_once '../class/ContentToken.class.php';
require_once '../class/ContentEmbeddedItem.class.php';
require_once '../class/DistributedResource.class.php';

if(!isset($_SESSION[SessionIndex['UserID']]))
{
    echo "Please Login again. <br />";
    echo "<a href='index.php?status=sessionExpired'>Click Here to Login</a>";
    die();
}

$editMode = (isset($_REQUEST["mode"])) ? $_REQUEST["mode"] : "editable";

$logInRes = ExtraModules::LogIntoLDT();
$logInRes = json_decode($logInRes, true);

if($logInRes["access_token"] == "LDTAuthenticationFailed")
{
    echo "Oops. Unable to login to LDT.";
    die();
}
else
{
    $tokenType = $logInRes["token_type"];
    $accessToken = $logInRes["access_token"];
    $headerInfo = $tokenType . " " . $accessToken ;
    $drp_Word    = Account::LdtUserDropBox($headerInfo, "WordAudio");
    $drp_Segment = Account::LdtUserDropBox($headerInfo, "SegmentAudio");
}
$drp_L1 = Language::LanguageDropBox("L1ID", true);
$drp_L2 = Language::LanguageDropBox("L2ID", true);
$contentObj = array();
$wordAndSegObj = (object) array("lemmaTotal" => "0",
                                "typeTotal" => "0",
                                "tokenTotal" => "0",
                                "segTotal"=>"0",
                                "mweTotal"=>"0");

$emItemsObj = (object) array("ImageNames"=>"",
                             "AudioNames"=>"",
                             "cssNames"=>"",
                             "ScriptNames"=>"");

if(isset($_GET["Q0"]))
{
    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $_GET["Q0"]);

    $info = Content::SearchContent($where, $whereParam);

	if(count($info) != 0)
	{
        $contentObj = FillItems($info[0]);

        if($contentObj->HasMainConfig == "YES")
        {
            $summaryOfData = CountAudioAndTranslation($contentObj);

            $recordedSeg = $summaryOfData["segments"]["recorded"];
            $nonRecordedSeg = $summaryOfData["segments"]["not_recorded"];
            $translatedSeg = $summaryOfData["segments"]["translated"];
            $nonTranslatedSeg = $summaryOfData["segments"]["not_translated"];
            $totalSeg = $translatedSeg + $nonTranslatedSeg;


            $recordedWord = $summaryOfData["words"]["recorded"];
            $nonRecordedWord = $summaryOfData["words"]["not_recorded"];
            $uniqueWords = $recordedWord + $nonRecordedWord;

            $translatedWord = $summaryOfData["words"]["translated"];
            $nonTranslatedWord = $summaryOfData["words"]["not_translated"];
            $uniqueUninflectedWords = $translatedWord + $nonTranslatedWord;


        }
        else
        {
            $recordedSeg = 0;
            $translatedSeg = 0;
            $recordedWord = 0;
            $translatedWord = 0;
            $totalSeg = 0;
            $uniqueWords = 0;
            $uniqueUninflectedWords = 0;
        }

        $elemCntWhere = " c.ContentID = :contentID";
        $elemCntWhereParam = array(":contentID" => $_GET["Q0"]);
        $wordAndSegmentInfo = Content::getElemCount($elemCntWhere, $elemCntWhereParam);
        if(count($wordAndSegmentInfo) != 0)
        {
            $wordAndSegObj->lemmaTotal = $wordAndSegmentInfo[0]["lemmaCount"];
            $wordAndSegObj->typeTotal = $wordAndSegmentInfo[0]["typeCount"];
            $wordAndSegObj->tokenTotal = $wordAndSegmentInfo[0]["tokenCount"];
            $wordAndSegObj->segTotal =  $wordAndSegmentInfo[0]["segmentCount"];
            $wordAndSegObj->mweTotal =  $wordAndSegmentInfo[0]["mweCount"];
        }

        //EmbeddedItemsInfo
        $emItemsInfo = ContentEmbeddedItem::ListOfContentEItems($_GET["Q0"]);
        if($emItemsInfo != false)
        {
            $emItemsObj->ImageNames = $emItemsInfo["ImageNames"];
            $emItemsObj->AudioNames = $emItemsInfo["AudioNames"];
            $emItemsObj->cssNames = $emItemsInfo["cssNames"];
            $emItemsObj->ScriptNames = $emItemsInfo["ScriptNames"];
        }

        /* This is wrong. Why? because one can be both requester AND crowd worker, BUT open the content from my crowdsourced task.
        Solution : Keeping $_REQUEST["mode"] in all the calls
        if($contentObj->CrowdworkerID == $_SESSION[SessionIndex['UserID']])
            $editMode = "crowdWorker";
        */
    }
}
else
{
    $contentObj = MakeEmptyContent();
}

$jsObjName = "contentVal";
echo ExtraModules::objToJS($contentObj, $jsObjName);

$jsObjName = "wordAndSegVal";
echo ExtraModules::objToJS($wordAndSegObj, $jsObjName);

$jsObjName = "emItemVal";
echo ExtraModules::objToJS($emItemsObj, $jsObjName);

$activeTab = 0;
if(isset($_GET["activeTab"]))
{
    $activeTab = $_GET["activeTab"];
}

$MsgToShow = "notSetYet";
$PythonFailureReturnMsgs = array("TaggedFileFailed", "FailedToExtractExtResFile", "FailToSegmentizeCreateResources",
            "FailToSegmentizeTagRawText", "MergeLanguageResourcesFailed",
            "FirstCompileStepFailed", "FirstCompileStepWithWarningDone",
            "InstallPrvAudioFailed", "InstallPrvTTSWordFailed", "InstallPrvTTSSegmentsFailed",
            "InstallZipfileFailed", "InstallTTSWordsFailed", "InstallTTSSegmentsFailed", "InstallNolLDTAudioFailed",
            "CreatePagesFailed", "CreatePagesForSnFailed",
            "FailedToExtractPageNamesDR", "FailedToExtractPageNamesPublish", "FailedPublish", "DataFromFileIsSavedForItems");

if(isset($_GET["msg"]))
{
    $MsgToShow = $_GET["msg"];
}

$backwardButton = '<div class="table">
        <div class="tr">
            <div class="tdTitle">
                <img src="../img/backward-icon.png" title="click to go back"
                     onclick=\'$("#mainContentDIV").load("LARAContents.php");\' >
            </div>
        </div>
    </div>';


echo '<script>onLoad(' . $activeTab . ',"'. $MsgToShow .'");</script>';
?>

<div class="newLaraContent">

    <?php echo $backwardButton;?>
    <div class="table configFileError"  style="display: none">
        <div class="tr">
            <div class="tdInput">
                <p class="ErrorMsg"></p>
            </div>
            <div class="tdTitle">
                <img src='../img/ok-icon.png' title='hide it'
                      onclick='$(".configFileError").css("display", "none");' >
                <?php
                    if(in_array($MsgToShow, $PythonFailureReturnMsgs)){
                        echo "<a target='_blank' 
                              href='../SharedModules/DownloadFile.php?" .
                            "download=PythonOutputDetail&relatedID=" . $contentObj->ContentID .
                            "&relatedPage=content&msgToShow=" . $MsgToShow . "'><img src='../img/detail-icon.png' title='more detail'></a>";
                    }
                ?>
            </div>
        </div>
    </div>
    <?php if(isset($_GET["Q0"])) { ?>
        <div class="table">
            <div class="tr">
                <div class="tdTXT">
                    <p class="CautionMsg">
                        Currently editing project "<?php echo $contentObj->ContentName; ?>"
                    </p>
                </div>
            </div>
        </div>
    <?php } ?>

    <div id="tabs">

    <form method="POST" id="configFileForm" enctype='multipart/form-data'>
        <input type="hidden" id="task" name="task">
        <input type="hidden" id="accessToken" name="accessToken" value="<?php echo $accessToken; ?>">
        <input type="hidden" id="tokenType" name="tokenType" value="<?php echo $tokenType; ?>">
        <input type="hidden" id="EditMode" name="EditMode" value="<?php echo $editMode; ?>">
        <input type="hidden" id="ContentID" name="ContentID">
        <input type="hidden" id="DirName" name="DirName">
        <input type="hidden" id="CreatorID" name="CreatorID">
        <input type="hidden" id="RawTextFileName" name="RawTextFileName">
        <input type="hidden" id="AutomatedTaggedTextFileName" name="AutomatedTaggedTextFileName">
        <input type="hidden" id="TaggedTextFileName" name="TaggedTextFileName">
        <input type="hidden" id="ContentStatus" name="ContentStatus">
        <input type="hidden" id="WordLdtTaskID" name="WordLdtTaskID">
        <input type="hidden" id="SegmentLdtTaskID" name="SegmentLdtTaskID">
        <input type="hidden" id="HasAudioTracking" name="HasAudioTracking">
        <input type="hidden" id="HasExternalResources" name="HasExternalResources">
        <input type="hidden" id="HasContentCss" name="HasContentCss">
        <input type="hidden" id="ContentCssFileName" name="ContentCssFileName">
        <input type="hidden" id="HasContentJs" name="HasContentJs">
        <input type="hidden" id="ContentJsFileName" name="ContentJsFileName">
        <input type="hidden" id="HasPinyin" name="HasPinyin">
        <input type="hidden" id="PinyinFileName" name="PinyinFileName">
        <input type="hidden" id="HasTtsSubstitution" name="HasTtsSubstitution">
        <input type="hidden" id="TtsSubstitutionFileName" name="TtsSubstitutionFileName">
        <input type="hidden" id="HasEmbeddedImage" name="HasEmbeddedImage">
        <input type="hidden" id="HasEmbeddedAudio" name="HasEmbeddedAudio">
        <input type="hidden" id="HasEmbeddedCSS" name="HasEmbeddedCSS">
        <input type="hidden" id="HasEmbeddedScript" name="HasEmbeddedScript">
        <input type="hidden" id="WebAddress" name="WebAddress">
        <input type="hidden" id="DistributedResourceID" name="DistributedResourceID">
        <input type="hidden" id="CrowdworkerID" name="CrowdworkerID">
        <input type="hidden" id="ParentID" name="ParentID">
        <input type="hidden" id="CrowdsourcingStatus" name="CrowdsourcingStatus">

        <ul>
            <li><a href="#firstStep">Step 1 : create resources</a></li>
            <li><a href="#secondStep">Step 2 : fill out resources</a></li>
            <li><a href="#thirdStep">Step 3 : create pages</a></li>
        </ul>
        <!--START OF FIRST TAB, ie Uploading ALL necessary data-->
        <div class="table" id="firstStep">
            <div id="MandatoryDiv" class="table">
                <div class="tr">
                    <div class="tdTitle">Text name:</div>
                    <div class="tdInput">
                        <input type="text" name="ContentName" id="ContentName"  size="20" value="">
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Reading language:</div>
                    <div class="tdInput">
                        <?php echo $drp_L2; ?>
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Translation language:</div>
                    <div class="tdInput">
                        <?php echo $drp_L1; ?>
                    </div>
                </div>
            </div>
            <div id="AutomaticTagger" class="table">
                <div class="tr" id="TreeTaggerStatusTR" style="display: none">
                    <div class="tdTitle"></div>
                    <div class="tdInput">
                        <input type="checkbox" id="TreeTaggerStatus" name="TreeTaggerStatus" value="YES">
                        <label for="TreeTaggerStatus">Use automatic tagging</label>
                    </div>
                </div>
                <div class="tr" id="PosTaggerTR" style="display: none">
                    <div class="tdTitle">Add POS tag to lemma:</div>
                    <div class="tdInput">
                        <input type="radio" id="AddPostagsToLemma_Y" name="AddPostagsToLemma"  value="YES" >On
                        <input type="radio" id="AddPostagsToLemma_N" name="AddPostagsToLemma"  value="NO" >Off&nbsp;
                    </div>
                </div>
                <div class="tr" id="RawTextTR" style="display: none">
                    <div class="tdTitle">Upload plain text:</div>
                    <div class="tdInput">
                        <input type="file" name="RawText" id="RawText" />
                        <label for="RawText">
                            <img src="../img/upload-icon.png" title="Upload plain text">
                        </label>
                        <span  class="FileUploadMsg" id="rawFileName" style="display: none"></span>
                    </div>
                </div>
                <?php if(!empty($contentObj->RawTextFileName)){
                    $href = "../SharedModules/DownloadFile.php?download=rawFile&fileDir=" . $contentObj->DirName . "/corpus&fileName=" . $contentObj->RawTextFileName ;
                    echo '<div class="tr" id="OnServerRawTextTR">
                        <div class="tdTitle">
                            <span style="font-size: small">Download plain text:</span>
                        </div>
                        <div class="tdInput">                       
                            <a target="_blank" href=' . $href . ' id="TreeTaggerPRV">
                                <img src="../img/download-icon-2.png" title="Download plain text" >
                            </a>
                        </div>
                    </div>';
                }?>
                <?php if(!empty($contentObj->AutomatedTaggedTextFileName)){
                    $href = "../SharedModules/DownloadFile.php?download=rawFile&fileDir=" . $contentObj->DirName . "/corpus&fileName=" . $contentObj->AutomatedTaggedTextFileName;
                    echo '<div class="tr" id="TreeTaggerResultTR">
                            <div class="tdTitle">Automatically created tagged text:</div>
                            <div class="tdInput">
                                <a target="_blank" href=' . $href . ' id="TreeTaggerResultDL">
                                    <img src="../img/download-icon.png" title="Download tagged text" >
                                </a>
                            </div>
                        </div>';
                }?>
            </div>
            <div id="ComplementaryDiv" class="table">
                <div id="ComplementaryDiv_Sec1_1" class="table">
                    <div class="tr">
                        <div class="tdTitle">Language resource type:</div>
                        <div class="tdInput">
                            <input type="radio" id="LangRepType_pub" name="LangRepType"  value="Public" >Public
                            <input type="radio"  id="LangRepType_prv" name="LangRepType"  value="Private" >Private &nbsp;
                        </div>
                    </div>

                    <div class="tr">
                        <div class="tdTitle">Audio type for words:</div>
                        <div class="tdInput">
                            <input type="radio" id="WordsAudioType_human" name="WordsAudioType"  value="human">Human
                            <input type="radio" id="WordsAudioType_tts"   name="WordsAudioType"  value="tts">TTS &nbsp;
                        </div>
                    </div>
                    <div class="tr">
                        <div class="tdTitle">Audio type for segments:</div>
                        <div class="tdInput">
                            <input type="radio" id="SegmentsAudioType_human" name="SegmentsAudioType"  value="human">Human
                            <input type="radio" id="SegmentsAudioType_tts"   name="SegmentsAudioType"  value="tts">TTS &nbsp;
                        </div>
                    </div>

                    <div class="tr" id="TtsEngineTR" style="display: none">
                        <div class="tdTitle">TTS Engine:</div>
                        <div class="tdInput" id="ttsEngines">
                        </div>
                    </div>
                    <div class="tr" id="TtsVoiceTR" style="display: none">
                        <div class="tdTitle">TTS Voice:</div>
                        <div class="tdInput" id="tssEngineVoices">
                        </div>
                    </div>
                    <div class="tr" id="LdtDeactivateStatusTR" style="display: none">
                        <div class="tdTitle">Deactivate audio recording:</div>
                        <div class="tdInput">
                            <input type="radio" id="LdtDeactivateStatus_Y" name="LdtDeactivateStatus"  value="YES" >Yes
                            <input type="radio" id="LdtDeactivateStatus_N" name="LdtDeactivateStatus"  value="NO" >No &nbsp;
                        </div>
                    </div>
                    <div class="tr" id="WordAudioTR" style="display: none">
                        <div class="tdTitle">Assign recording voice for words:</div>
                        <div class="tdInput">
                            <?php echo $drp_Word; ?>
                        </div>
                    </div>
                    <div class="tr" id="SegmentAudioTR" style="display: none">
                        <div class="tdTitle">Assign recording voice for segments:</div>
                        <div class="tdInput">
                            <?php echo $drp_Segment; ?>
                        </div>
                    </div>
                </div>
                <div id="ComplementaryDiv_Sec1_2" class="table">
                    <div class="tr">
                        <div class="tdAccordion" id ="TranslationComplementary" >
                            <h3>Translation, audio and note settings</h3>
                            <div class="tableAccordion" style="height: 350px;">
                                <div class="tr">
                                    <div class="tdTitle">Word translations model:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="WTO_lemma" name="WordTranslationsOn"  value="lemma" >lemma
                                        <input type="radio" id="WTO_surface_word_type" name="WordTranslationsOn"  value="surface_word_type" >surface word type
                                        <input type="radio" id="WTO_surface_word_token"  name="WordTranslationsOn"  value="surface_word_token" >surface word token
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Word translation mouseover:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="WordTranslationMouseOver_Y" name="WordTranslationMouseOver"  value="YES" >On
                                        <input type="radio" id="WordTranslationMouseOver_N" name="WordTranslationMouseOver"  value="NO" >Off
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Segment translation mouseover:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="SegmentTranslationMouseOver_Y" name="SegmentTranslationMouseOver"  value="YES" >On
                                        <input type="radio" id="SegmentTranslationMouseOver_N" name="SegmentTranslationMouseOver"  value="NO" >Off&nbsp;
                                     </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Segment translation as popup:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="SegmentTranslationAsPopup_Y" name="SegmentTranslationAsPopup"  value="YES" >On
                                        <input type="radio" id="SegmentTranslationAsPopup_N" name="SegmentTranslationAsPopup"  value="NO" >Off&nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Segment translation character:</div>
                                    <div class="tdInput">
                                        <input type="text" name="SegmentTranslationCharacter" id="SegmentTranslationCharacter"
                                               style="width: 5%" size="5">
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Add note to words:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="WordsNote_Y" name="WordsNote"  value="YES" >On
                                        <input type="radio" id="WordsNote_N" name="WordsNote"  value="NO" >Off &nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Word audio mouseover:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="AudioMouseOver_Y" name="AudioMouseOver"  value="YES" >On
                                        <input type="radio" id="AudioMouseOver_N" name="AudioMouseOver"  value="NO" >Off &nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Segment audio mouseover:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="AudioSegments_Y" name="AudioSegments"  value="YES" >On
                                        <input type="radio" id="AudioSegments_N" name="AudioSegments"  value="NO" >Off &nbsp;
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div id="ComplementaryDiv_Sec1_3" class="table">
                    <div class="tr">
                        <div class="tdAccordion" id ="FlashcardComplementary" >
                            <h3>Flashcard settings</h3>
                            <div class="tableAccordion" style="height: 350px;">
                                    <div class="tr">
                                        <div class="tdTitle">Flashcard test types:</div>
                                        <div class="tdInput">
                                            <input type="checkbox" id="WTFC_checkbox" name="WTFC_checkbox" >
                                            <label for="WTFC_checkbox">Word translation</label>
                                            <input type='hidden' name='WordTranslationFC' value='NO'>
                                            <input type="radio" id="WTFC_lemma" name="WordTranslationFC" value="LEMMA">Lemma translation
                                            <input type="radio" id="WTFC_token" name="WordTranslationFC" value="TOKEN">Token translation
                                        </div>
                                    </div>
                                    <div class="tr">
                                        <div class="tdTitle"></div>
                                        <div class="tdInput">
                                            <input type="checkbox" id="WAFC_checkbox" name="WAFC_checkbox">
                                            <label for="WAFC_checkbox">Audio translation</label>
                                            <input type='hidden' name='AudioTranslationFC' value='NO'>
                                            <input type="radio" id="WAFC_lemma" name="AudioTranslationFC" value="LEMMA">Lemma translation
                                            <input type="radio" id="WAFC_token" name="AudioTranslationFC" value="TOKEN">Token translation
                                        </div>
                                    </div>
                                    <div class="tr">
                                        <div class="tdTitle"></div>
                                        <div class="tdInput">
                                            <input type='hidden' name='SignedVideoFC' value='NO'>
                                            <input type="checkbox" id="SignedVideoFC" name="SignedVideoFC" value="YES">
                                            <label for="SignedVideoFC">Signed video</label>
                                        </div>
                                    </div>
                                    <div class="tr">
                                        <div class="tdTitle"></div>
                                        <div class="tdInput">
                                            <input type='hidden' name='GapFC' value='NO'>
                                            <input type="checkbox" id="GapFC" name="GapFC" value="YES">
                                            <label for="GapFC">Sentence with gap</label>
                                        </div>
                                    </div>
                                    <div class="tr">
                                        <div class="tdTitle">Show question context for:</div>
                                        <div class="tdInput">
                                            <input type='hidden' name='ShowTextContext' value='NO'>
                                            <input type="checkbox" id="ShowTextContext" name="ShowTextContext" value="YES">
                                            <label for="ShowTextContext">text</label>&nbsp;&nbsp;&nbsp;
                                            <input type='hidden' name='ShowMultimediaContext' value='NO'>
                                            <input type="checkbox" id="ShowMultimediaContext" name="ShowMultimediaContext" value="YES">
                                            <label for="ShowMultimediaContext">multimedia</label>
                                        </div>
                                    </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div id="ComplementaryDiv_Sec2_0" class="table">
                    <div class="tr">
                        <div class="tdAccordion" id ="PlayComplementary" >
                            <h3>Play options</h3>
                            <div class="tableAccordion" style="height: 150px;">
                                <div class="tr">
                                    <div class="TdTitle">Play parts:</div>
                                    <div class="TdInput">
                                        <input type="text" name="PlayParts" id="PlayParts"  size="20" value="">
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Keep segment audio duplicates:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="SegmentAudioKeepDuplicates_Y" name="SegmentAudioKeepDuplicates"  value="YES" >On
                                        <input type="radio" id="SegmentAudioKeepDuplicates_N" name="SegmentAudioKeepDuplicates"  value="NO" >Off&nbsp;
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div id="ComplementaryDiv_Sec2" class="table">
                    <div class="tr">
                        <div class="tdAccordion" id ="OptionalComplementary" >
                            <h3>Advanced options</h3>
                            <div class="tableAccordion" style="height: 490px;">
                                <div class="tr">
                                    <div class="tdTitle">Reading language is right to left:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="L1rtl_Y" name="L1rtl"  value="YES" >Yes
                                        <input type="radio"  id="L1rtl_N" name="L1rtl"  value="NO" >No &nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Table of contents:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="TableOfContents_Y" name="TableOfContents"  value="YES" >On
                                        <input type="radio" id="TableOfContents_N" name="TableOfContents"  value="NO" >Off&nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Keep comments:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="KeepComments_Y" name="KeepComments"  value="YES" >On
                                        <input type="radio" id="KeepComments_N" name="KeepComments"  value="NO" >Off&nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Comments by default:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="CommentsByDefault_Y" name="CommentsByDefault"  value="YES" >On
                                        <input type="radio" id="CommentsByDefault_N" name="CommentsByDefault"  value="NO" >Off&nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Linguistics article comments:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="LinguisticsArticleComments_Y" name="LinguisticsArticleComments"  value="YES" >On
                                        <input type="radio" id="LinguisticsArticleComments_N" name="LinguisticsArticleComments"  value="NO" >Off&nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Coloured words:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="ColouredWords_Y" name="ColouredWords"  value="YES" >On
                                        <input type="radio" id="ColouredWords_N" name="ColouredWords"  value="NO" >Off&nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Audio words in colour:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="AudioWordsInColour_Y" name="AudioWordsInColour"  value="YES" >Yes, red
                                        <input type="radio" id="AudioWordsInColour_N" name="AudioWordsInColour"  value="NO" >No &nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Translated words in colour:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="TranslatedWordsInColour_Y" name="TranslatedWordsInColour"  value="YES" >Yes
                                        <input type="radio" id="TranslatedWordsInColour_N" name="TranslatedWordsInColour"  value="NO" >No &nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">MWE words in colour:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="MweWordsInColour_Y" name="MweWordsInColour"  value="YES" >Yes
                                        <input type="radio" id="MweWordsInColour_N" name="MweWordsInColour"  value="NO" >No &nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Video annotation:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="VideoAnnotations_Y" name="VideoAnnotations"  value="YES" >Yes
                                        <input type="radio" id="VideoAnnotations_N" name="VideoAnnotations"  value="NO" >No &nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Video annotation from translation:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="VideoAnnotationsFromTranslation_Y" name="VideoAnnotationsFromTranslation"  value="YES" >Yes
                                        <input type="radio" id="VideoAnnotationsFromTranslation_N" name="VideoAnnotationsFromTranslation"  value="NO" >No &nbsp;
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Max examples per word page:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="MaxExamplesPerWordPage_5"  name="MaxExamplesPerWordPage"  value="5" >5
                                        <input type="radio" id="MaxExamplesPerWordPage_10" name="MaxExamplesPerWordPage"  value="10" >10 &nbsp;
                                        <input type="radio" id="MaxExamplesPerWordPage_15" name="MaxExamplesPerWordPage"  value="15" >15
                                        <input type="radio" id="MaxExamplesPerWordPage_1000" name="MaxExamplesPerWordPage"  value="1000" >1000
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Extra page info:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="ExtraPageInfo_Y" name="ExtraPageInfo"  value="YES" >On
                                        <input type="radio" id="ExtraPageInfo_N" name="ExtraPageInfo"  value="NO" >Off
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Font:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="Font_serif"      name="Font"  value="serif" >serif
                                        <input type="radio" id="Font_sans-serif" name="Font"  value="sans-serif" >sans-serif
                                        <input type="radio" id="Font_monospace"  name="Font"  value="monospace" >monospace
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">Frequency lists in:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="FrequencyListsInMainText_Y" name="FrequencyListsInMainText"  value="YES" >Main text page
                                        <input type="radio" id="FrequencyListsInMainText_N" name="FrequencyListsInMainText"  value="NO" >Word page &nbsp;
                                    </div>
                                </div>
                                <div class="tr" id="IgnoreLargeFileTransferTR">
                                    <div class="tdTitle">Ignore large files:</div>
                                    <div class="tdInput">
                                        <input type="radio" id="IgnoreLargeFileTransfer_Y" name="IgnoreLargeFileTransfer"  value="YES" >Yes
                                        <input type="radio" id="IgnoreLargeFileTransfer_N" name="IgnoreLargeFileTransfer"  value="NO" >No &nbsp;
                                    </div>
                                </div>
                                <div class="tr" id="ExternalResourceTR" style="display: none">
                                    <div class="tdTitle">External resource:</div>
                                    <div class="tdInput">
                                        <input type="file" name="ExternalResource" id="ExternalResource" />
                                        <label for="ExternalResource">
                                            <img src="../img/upload-icon.png" title="Upload external language resource zipfile">
                                        </label>
                                        <span  class="FileUploadMsg"  id="ExternalResFileName" style="display: none"></span>
                                    </div>
                                </div>
                                <!-- added 10-15-2019 -->
                                <div class="tr">
                                    <div class="tdTitle">
                                        <input type="checkbox" id="ContentCssStatus" name="ContentCssStatus" value="YES">
                                        <label for="ContentCssStatus">Import CSS for content</label>
                                    </div>
                                    <div class="tdInput"></div>
                                </div>
                                <div class="tr" id="ContentCssTR" style="display: none">
                                    <div class="tdTitle">CSS file:</div>
                                    <div class="tdInput">
                                        <input type="file" name="ContentCss" id="ContentCss" />
                                        <label for="ContentCss">
                                            <img src="../img/upload-icon.png" title="Upload CSS file for this text">
                                        </label>
                                        <span  class="FileUploadMsg"  id="ContentCssFileNameSpan" style="display: none"></span>
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">
                                        <input type="checkbox" id="ContentJsStatus" name="ContentJsStatus" value="YES">
                                        <label for="ContentJsStatus">Import JS for whole content</label>
                                    </div>
                                    <div class="tdInput"></div>
                                </div>
                                <div class="tr" id="ContentJsTR" style="display: none">
                                    <div class="tdTitle">JS file:</div>
                                    <div class="tdInput">
                                        <input type="file" name="ContentJs" id="ContentJs" />
                                        <label for="ContentJs">
                                            <img src="../img/upload-icon.png" title="Upload Javascript file for this text">
                                        </label>
                                        <span  class="FileUploadMsg"  id="ContentJsFileNameSpan" style="display: none"></span>
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">
                                        <input type="checkbox" id="PinyinStatus" name="PinyinStatus" value="YES">
                                        <label for="PinyinStatus">Import Pinyin for chinese</label>
                                    </div>
                                    <div class="tdInput"></div>
                                </div>
                                <div class="tr" id="PinyinTR" style="display: none">
                                    <div class="tdTitle">Pinyin file:</div>
                                    <div class="tdInput">
                                        <input type="file" name="PinyinFile" id="PinyinFile" />
                                        <label for="PinyinFile">
                                            <img src="../img/upload-icon.png" title="Upload pinyin file for this text">
                                        </label>
                                        <span  class="FileUploadMsg"  id="PinyinFileNameSpan" style="display: none"></span>
                                    </div>
                                </div>
                                <div class="tr">
                                    <div class="tdTitle">
                                        <input type="checkbox" id="TtsSubstitutionStatus" name="TtsSubstitutionStatus" value="YES">
                                        <label for="TtsSubstitutionStatus">Import TTS substitution for words</label>
                                    </div>
                                    <div class="tdInput"></div>
                                </div>
                                <div class="tr" id="TtsSubstitutionTR" style="display: none">
                                    <div class="tdTitle">Tts substitution file:</div>
                                    <div class="tdInput">
                                        <input type="file" name="TtsSubstitutionFile" id="TtsSubstitutionFile" />
                                        <label for="TtsSubstitutionFile">
                                            <img src="../img/upload-icon.png" title="Upload TTS substitution file for this text">
                                        </label>
                                        <span  class="FileUploadMsg"  id="TtsSubstitutionFileNameSpan" style="display: none"></span>
                                    </div>
                                </div>


                            </div>
                        </div>
                    </div>
                </div>
                <div id="ComplementaryDiv_Sec3" class="table">
                    <div class="tr">
                        <div class="tdTitle">Upload edited tagged text:</div>
                        <div class="tdInput">
                            <input type="file" name="TaggedText" id="TaggedText" />
                            <label for="TaggedText">
                                <img src="../img/upload-icon.png" title="Upload edited tagged text">
                            </label>
                            <span id="taggedFileName" class="FileUploadMsg" style="display: none"></span>
                        </div>
                    </div>
                    <?php if(!empty($contentObj->TaggedTextFileName)){
                        $href = "../SharedModules/DownloadFile.php?download=taggedFile&fileDir=" . $contentObj->DirName . "/corpus&fileName=" . $contentObj->TaggedTextFileName ;
                        echo '<div class="tr">
                            <div class="tdTitle">
                                <span style="font-size: small"> Download tagged text: </span></div>
                            <div class="tdInput">
                                <a target="_blank" href=' . $href . ' id="TaggedPRV">
                                        <img src="../img/download-icon-2.png" title="Download tagged text" >
                                  </a>
                            </div>
                        </div>';
                    } ?>
                    <div class="tr" id="UseAutomatedTaggedTextTR" style="display: none">
                        <div class="tdTitle">
                        </div>
                        <div class="tdInput">
                            <input type="checkbox" id="UseAutomatedTaggedTextStatus" name="UseAutomatedTaggedTextStatus" value="YES">
                            <label for="UseAutomatedTaggedTextStatus">Use automated tagged text file generated with Portal tagger.</label>
                        </div>
                    </div>
                </div>
            </div>
            <div id="EmbeddedFilesDesc" class="table" style="display: none;width: 100%">
                <p class="CautionMsg">
                    The uploaded text contains some embedded media.
                    Please upload embedded files in zip format and click "Create Resource" to continue this step.
                </p>
            </div>
            <div id="EmbeddedFiles" class="table">
                <div class="tr" id="EmbeddedAudioTR" style="display: none;">
                    <div class="tdTitle">Embedded audio:</div>
                    <div class="tdInput">
                        <input type="file" name="EmbeddedAudio" id="EmbeddedAudio" />
                        <label for="EmbeddedAudio">
                            <img src="../img/upload-icon.png" title="Upload a zipfile of all the embedded audio files used in this text">
                        </label>
                       <span  class="FileUploadMsg"  id="eAudioFileName" style="display: none"></span>
                    </div>
                </div>
                <div class="tr" id="EmbeddedCssTR" style="display: none;">
                    <div class="tdTitle">Embedded CSS:</div>
                    <div class="tdInput">
                        <input type="file" name="EmbeddedCss" id="EmbeddedCss" />
                        <label for="EmbeddedCss">
                            <img src="../img/upload-icon.png" title="Upload a zipfile of all the embedded CSS files used in this text">
                        </label>
                        <span  class="FileUploadMsg"  id="eCssFileName" style="display: none"></span>
                    </div>
                </div>
                <div class="tr" id="EmbeddedImageTR" style="display: none;">
                    <div class="tdTitle">Embedded image:</div>
                    <div class="tdInput">
                        <input type="file" name="EmbeddedImage" id="EmbeddedImage" />
                        <label for="EmbeddedImage">
                            <img src="../img/upload-icon.png" title="Upload a zipfile of all the embedded image files used in this text">
                        </label>
                        <span  class="FileUploadMsg"  id="eImageFileName" style="display: none"></span>
                    </div>
                </div>
                <div class="tr" id="EmbeddedScriptTR" style="display: none;">
                    <div class="tdTitle">Embedded script:</div>
                    <div class="tdInput">
                        <input type="file" name="EmbeddedScript" id="EmbeddedScript" />
                        <label for="EmbeddedScript">
                            <img src="../img/upload-icon.png" title="Upload a zipfile of all the embedded Javascript files used in this text">
                        </label>
                        <span  class="FileUploadMsg"  id="eScriptFileName" style="display: none"></span>
                    </div>
                </div>
            </div>
            <?php if($editMode != 'readOnly' ) { ?>
                <div id="SaveFirstStepInfo" class="table">
                    <div class="tr">
                        <div class="tdTitle"></div>
                        <div class="tdInput">
                            <?php if($editMode != 'crowdWorker' ) { ?>
                                <input type="button" id="TaggingButton" name="TaggingButton" onclick="createResources(0)"
                                       title="Tag raw text automatically" value="Tag raw text" style="display: none">
                                <input type="button" id="SetConfigButton" name="SetConfigButton" onclick="createResources(1)"
                                       title="Set config file parameters" value="Set configs" style="display: none">
                            <?php } ?>
                            <input type="button" id="CreateResourceButton" name="CreateResourceButton" onclick="createResources(2)"
                                   title="Post audio recording tasks, find words and sentences to translate" value="Create resources" style="display: none">
                        </div>
                    </div>
                </div>
            <?php } ?>
        </div>
        <!--END OF FIRST TAB-->
        <!--****************************************************************-->
        <!--START OF SECOND TAB, ie result of first phase compile-->
        <div class="table" id="secondStep">
            <div id="TranslationAndRecordingDiv" class="table">
                <h3>Translation</h3>
                <div id="TranslationDiv" class="tableAccordion" style="height: 240px">
                    <fieldset>
                        <legend>&nbsp;&nbsp;Fill out translations <b>online</b>
                            <img src="../img/information-icon.png" title="Enter the word and segment translation windows and then fill out the translations there">&nbsp;&nbsp;
                        </legend>
                    <div class="table">
                        <div class="tr">
                            <div class="tdTitle">Lemma notes:</div>
                            <div class="tdInput">
                                <?php if($wordAndSegObj->lemmaTotal != 0 &&
                                    ($contentObj->WordTranslationsOn == 'lemma' || $contentObj->WordsNote == 'YES'))
                                {
                                    echo '<img src="../img/fillout-icon.png" 
                                    id="LemmaNote" title="Click here to add note for lemmas." >';
                                }
                                else
                                {
                                    echo '<span  class="FileUploadMsg">
                                            No lemma to add note.            
                                            </span>';
                                }
                                ?>
                            </div>
                        </div>
                        <div class="tr">
                            <div class="tdTitle">Lemma translation:</div>
                            <div class="tdInput">
                                <?php if($wordAndSegObj->lemmaTotal != 0 && $contentObj->WordTranslationsOn == 'lemma')
                                {
                                    echo '<img src="../img/fillout-icon.png" 
                                    id="LemmaTrnslt" title="Click here to fill out lemma translation form." >';
                                }
                                else
                                {
                                    echo '<span  class="FileUploadMsg">
                                            No lemma to translate.            
                                            </span>';
                                }
                                ?>
                            </div>
                        </div>
                        <div class="tr">
                            <div class="tdTitle">Type translation:</div>
                            <div class="tdInput">
                                <?php if($wordAndSegObj->typeTotal != 0 &&
                                    ($contentObj->WordTranslationsOn == 'surface_word_type' || $contentObj->WordTranslationsOn == 'surface_word_token'))
                                {
                                    echo '<img src="../img/fillout-icon.png" 
                                    id="TypeTrnslt" title="Click here to fill out type translation form." >';
                                    if($editMode != 'readOnly' ) {
                                        echo '&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp';
                                        echo '<img src="../img/apply-icon.png" 
                                       id="ApplyToToken" title="Click here to apply type translation on token translation." >';
                                    }
                                }
                                else
                                {
                                    echo '<span  class="FileUploadMsg">
                                            No type to translate.            
                                            </span>';
                                }
                                ?>
                            </div>
                        </div>
                        <div class="tr">
                            <div class="tdTitle">Token translation:</div>
                            <div class="tdInput">
                                <?php if($wordAndSegObj->tokenTotal != 0 && $contentObj->WordTranslationsOn == 'surface_word_token')
                                {
                                    echo '<img src="../img/fillout-icon.png" 
                                    id="TokenTrnslt" title="Click here to fill out token translation form." >';
                                }
                                else
                                {
                                    echo '<span  class="FileUploadMsg">
                                            No token to translate.            
                                            </span>';
                                }
                                ?>
                            </div>
                        </div>
                        <div class="tr">
                            <div class="tdTitle">Segment translation:</div>
                            <div class="tdInput">
                                <?php if($wordAndSegObj->segTotal != 0)
                                {
                                    echo '<img src="../img/fillout-icon.png" 
                                    id="SgmntTrnslt" title="Click here to fill out segment translation form." >';
                                }
                                else
                                {
                                    echo '<span  class="FileUploadMsg">No segment to translate.</span>';
                                }
                                ?>
                            </div>
                        </div>
                    </div>
                    </fieldset>
                    <div class="table">
                        <div class="tr">
                            <div class="tdTXT CautionMsg"> OR  </div>
                        </div>
                    </div>
                    <fieldset>
                        <legend>&nbsp;&nbsp;Fill out translations <b>offline</b>
                            <img src="../img/information-icon.png" title="Download a spreadsheet, fill it out on your machine, then upload filled out spreadsheet">&nbsp;&nbsp;
                        </legend>
                        <div  class="table">
                            <div class="tr">
                                <div class="tdTitle">Lemma translation:</div>
                                <div class="tdInput">
                                    <?php if($wordAndSegObj->lemmaTotal != 0 && $contentObj->WordTranslationsOn == 'lemma'){ ?>
                                        <a target="_blank" href="" id="LemmaCsvDL">
                                            <img src="../img/download-icon.png" title="Download lemma spreadsheet" >
                                        </a>&nbsp;&nbsp;&nbsp;&nbsp;
                                        <?php if($editMode != 'readOnly' ) { ?>
                                            <label for="UploadLemmaTranslation">
                                                <img src="../img/upload-icon.png" title="Upload filled out lemma spreadsheet">
                                            </label>
                                            <input id="UploadLemmaTranslation" name="UploadLemmaTranslation" type="file" />
                                        <?php }
                                    }
                                    else {
                                        echo '<span  class="FileUploadMsg">No lemma to translate.</span>';
                                    } ?>
                                </div>
                            </div>
                            <div class="tr">
                                <div class="tdTitle">Type translation:</div>
                                <div class="tdInput">
                                    <?php if($wordAndSegObj->typeTotal != 0 &&
                                    ($contentObj->WordTranslationsOn == 'surface_word_type' || $contentObj->WordTranslationsOn == 'surface_word_token'))
                                    { ?>
                                        <a target="_blank" href="" id="TypeCsvDL">
                                            <img src="../img/download-icon.png" title="Download type spreadsheet" >
                                        </a>&nbsp;&nbsp;&nbsp;&nbsp;
                                        <?php if($editMode != 'readOnly' ) { ?>
                                            <label for="UploadTypeTranslation">
                                                <img src="../img/upload-icon.png" title="Upload filled out type spreadsheet">
                                            </label>
                                            <input id="UploadTypeTranslation" name="UploadTypeTranslation" type="file" />
                                    <?php }
                                    }
                                    else {
                                        echo '<span  class="FileUploadMsg">No type to translate.</span>';
                                    } ?>
                                </div>
                            </div>
                            <div class="tr">
                                <div class="tdTitle">Token translation:</div>
                                <div class="tdInput">
                                    <?php if($wordAndSegObj->tokenTotal != 0 && $contentObj->WordTranslationsOn == 'surface_word_token')
                                     { ?>
                                        <a target="_blank" href="" id="TokenCsvDL">
                                            <img src="../img/download-icon.png" title="Download token spreadsheet" >
                                        </a>&nbsp;&nbsp;&nbsp;&nbsp;
                                        <?php if($editMode != 'readOnly' ) { ?>
                                            <label for="UploadTokenTranslation">
                                                <img src="../img/upload-icon.png" title="Upload filled out token spreadsheet">
                                            </label>
                                            <input id="UploadTokenTranslation" name="UploadTokenTranslation" type="file" />
                                        <?php }
                                     }else {
                                        echo '<span  class="FileUploadMsg">No token to translate.</span>';
                                     } ?>
                                </div>
                            </div>
                            <div class="tr">
                                <div class="tdTitle">Segment translation:</div>
                                <div class="tdInput">
                                    <?php if($wordAndSegObj->segTotal != 0) { ?>
                                        <a target="_blank" href="" id="SegmentCsvDL">
                                            <img src="../img/download-icon.png" title="Download segment spreadsheet" >
                                        </a>&nbsp;&nbsp;&nbsp;&nbsp;
                                        <?php if($editMode != 'readOnly' ) { ?>
                                            <label for="UploadSegmentTranslation">
                                            <img src="../img/upload-icon.png" title="Upload filled out segment spreadsheet">
                                            </label>
                                            <input id="UploadSegmentTranslation" name="UploadSegmentTranslation" type="file" />
                                        <?php }
                                        }
                                        else {
                                            echo '<span  class="FileUploadMsg">No segment to translate.</span>';
                                    } ?>
                                </div>
                            </div>
                        </div>
                    </fieldset>
                </div>
                <h3>Multi word expressions</h3>
                <div id="MultiWordDiv" class="tableAccordion" style="height: 40px">
                    <div class="table">
                        <div class="tr">
                            <div class="tdTitle">Multi words annotation:</div>
                            <div class="tdInput">
                                <?php if($wordAndSegObj->mweTotal != 0)
                                {
                                    echo '<img src="../img/Checklist-icon.png" 
                                    id="MultiWordAnnotation" title="Click here to annotate multi words." >';
                                }
                                else
                                {
                                    echo '<span  class="FileUploadMsg">
                                            No multi word to annotate.            
                                            </span>';
                                }
                                ?>
                            </div>
                        </div>
                    </div>
                </div>
                <h3>Recording</h3>
                <div id="RecordingDiv" class="tableAccordion" style="height: 80px">
                    <div class="table">
                        <?php if($contentObj->WordsAudioType == 'human' || $contentObj->SegmentsAudioType == 'human') { ?>
                            <div class="tr">
                                <div class="tdTXT" >
                                    <a href="https://regulus.unige.ch/litedevtools/client/#/home" target="_blank">
                                        <p class="RecordingMsg">
                                            Click here to go to recording platform.
                                        </p>
                                    </a>
                                </div>
                            </div>
                        <?php } if($contentObj->WordsAudioType == 'tts') { ?>
                            <div class="tr">
                                <div class="tdTXT" >
                                    <a href="javascript:generateTTS('word');">
                                        <p class="RecordingMsg">
                                            Click here to generate words tts files.
                                        </p>
                                    </a>
                                </div>
                            </div>
                        <?php } if($contentObj->SegmentsAudioType == 'tts') { ?>
                            <div class="tr">
                                <div class="tdTXT" >
                                    <a href="javascript:generateTTS('segment');">
                                        <p class="RecordingMsg">
                                            Click here to generate segments tts files.
                                        </p>
                                    </a>
                                </div>
                            </div>
                        <?php } ?>
                    </div>
                </div>
            </div>
        </div>
        <!--END OF SECOND TAB-->
        <!--****************************************************************-->
        <!--START OF THIRD TAB, ie checking filled information and creating pages-->
        <div class="table" id="thirdStep">
        <?php if($contentObj->HasMainConfig == 'NO') {?>
            <div class="tr">
                <div class="tdTXT">
                    <p class="CautionMsg">
                        NOT IN THE STEP OF CREATING PAGES YET. PLEASE CREATE AND COMPLETE THE RESOURCES.
                    </p>
                </div>
            </div>
        <?php } else { ?>
            <div class="tr">
                <div class="tdTXT">
                    <b>Summary: </b><br/>
                    Original text file: <?php echo $contentObj->TaggedTextFileName; ?>  <br/>
                    Segments: <?php echo $totalSeg; ?> (<?php echo $translatedSeg; ?> translated; <?php echo $recordedSeg; ?> recorded)<br/>
                    Unique words:  <?php echo $uniqueWords; ?> (<?php echo $recordedWord; ?> recorded)<br/>
                    Unique uninflected words:  <?php echo $uniqueUninflectedWords; ?> (<?php echo $translatedWord; ?> translated)<br/>
                </div>
            </div>
            <div class="tr">
                <div class="tdTXT">
                    <?php if($editMode != 'readOnly' ) { ?>
                        <input type="button" class="aquaButton" id="PageCreationButt" name="PageCreationButt" title="Create standalone LARA pages"
                               value="Create pages" onclick="createPages()" > &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    <?php } ?>
                    <span id="WebAddressTR" style="display: none;">
                        <a target="_blank" href=<?php echo $contentObj->WebAddress;?>>
                            <input type="button" class="aquaButton" value="Preview pages" title="Show the standalone LARA pages">
                        </a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        <?php if($editMode != 'readOnly' ) { ?>
                            <input type="button" id="PublishRsrc" name="PublishRsrc"
                                   title="Publish or republish resource" value="Publish" onclick="publishResource()" >
                        <?php } ?>
                    </span>
                </div>
            </div>
            <div class="tr">
                <span id="CompiledFolderDLTR" style="display: none;font-size: small">
                    Download zipfile of standalone pages &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                    <a target="_blank" href="" id="CompiledFolderDL">
                          <img src="../img/download-folder-icon.png" title="Download zipfile of standalone LARA pages" >
                    </a>
                </span>
            </div>
        <?php }?>
        </div>
        <!--END OF THIRD TAB-->
        <!--****************************************************************-->
    </form>
    </div>
    <?php echo $backwardButton; ?>
</div>