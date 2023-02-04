<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 4/16/2019
 * Time: 12:16 PM
 */

require_once '../Config.php';
require_once '../class/Content.class.php';
require_once '../class/Language.class.php';
require_once '../class/Account.class.php';
require_once '../class/ContentEmbeddedItem.class.php';
require_once '../class/DistributedResource.class.php';
require_once '../class/DistributedResourcePage.class.php';
require_once '../class/ImportContent.class.php';
require_once '../class/ContentRecordingTask.class.php';
require_once '../class/UserActivitiesLogs.class.php';
require_once '../class/ContentRequesterWorkerMessage.class.php';
require_once '../class/ContentGiveUpReason.class.php';
require_once '../SharedModules/DocxConversion.class.php';
require_once '../SharedModules/ExtraModules.class.php';
require_once '../SharedModules/LogConstants.php';
require_once 'SegmentsAndWords.data.php';
require_once 'MultiWordExpressions.data.php';


$task = isset($_REQUEST["task"]) ? $_REQUEST["task"] :  "";

switch ($task)
{
    case "TagRawText":
        TagRawText();

    case "SetConfig":
        CreateResources(false);

    case "CreateResources":
        CreateResources();

    case "CreatePages":
        CreatePages();

    case "DeleteContent":
        DeleteContent();

    case "PublishContent":
        PublishContent();

    case "ImportLaraContent":
        ImportLaraContent(false);

    case "ImportLaraResource":
        ImportLaraResource();

    case "GetContentLog":
        GetContentLog();

    case "ApplyTypeToToken":
        ApplyTypeToToken();

    case "DistributeContent":
        DistributeContent();

    case "GetTask":
        GetTask();

    case "CollectContent":
        CollectContent();

    case "GiveUpTask":
        GiveUpTask();

    case "FinalizeTask":
        FinalizeTask();

    case "SendContentMessage":
        SendContentMessage();

    case "GetContentMessages":
        GetContentMessages();

    case "TtsEnginesList":
        TtsEnginesList();

    case "GenerateSegmentsTTS":
        GenerateSegmentsTTS();

    case "GenerateWordsTTS":
        GenerateWordsTTS();
}

function TagRawText()
{
    //json response is created using this array
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $contentObj = FillItems($_REQUEST);

    if ($contentObj->ContentID == null) {
        $resultArray[0]["id"] = -1;
    }
    else{
        $resultArray[0]["id"] = $contentObj->ContentID;
    }

    //Check if user wants to use tagger but has not upload a file.
    if(!ExtraModules::FileExists('RawText') && $contentObj->ContentID == null)
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "FileUploadErrorTagRawText");
        ExtraModules::KillProcess($resultArray, "FileUploadErrorTagRawText");
    }


    if(!ExtraModules::FileUnicodeIsValid('RawText'))
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "RtFileUnicodeError");
        ExtraModules::KillProcess($resultArray, "RtFileUnicodeError");
    }

    if(!ExtraModules::FileExtensionIsValid('RawText', array('txt', 'docx')))
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "RtFileTypeError");
        ExtraModules::KillProcess($resultArray, "RtFileTypeError");
    }

    //continue with file to create tagged file
    if ($contentObj->ContentID == null)
    {
        //create new data raw in database for new content
        $contentObj->insert();
        $contentObj->ContentID = $contentObj->lastID();
        $resultArray[0]["id"] = $contentObj->ContentID;
    }
    else
    {
        //edit the existing content raw in database
        $oldDirName = $contentObj->DirName;
        $newDirName = $contentObj->ContentID . "_" . str_replace(" ","_",$contentObj->ContentName);
        if(!empty($oldDirName) && $oldDirName != $newDirName)
        {
            rename(LaraContentDir . $oldDirName, LaraContentDir . $newDirName);
            $contentObj->DirName = $newDirName;
        }
        $contentObj->update();
    }

    //creating the folder structure for the saved content
    $dirName = $contentObj->ContentID . "_" . str_replace(" ","_",$contentObj->ContentName);

    $contentDirAddress = LaraContentDir . $dirName;
    $createDIRRes = ExtraModules::CreateDir($contentDirAddress, SubDirNames);

    $tmpDirAddress = ContentTmpDirectory . $dirName;
    $createTmpDIRRes = ExtraModules::CreateDir($tmpDirAddress, SubDirNamesContentTmp);

    //check failure or success in creating directories
    if (in_array($createDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, $createDIRRes . "TagRawText");
        ExtraModules::KillProcess($resultArray, $createDIRRes . "TagRawText");
    }
    else if (in_array($createTmpDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {   ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, $createTmpDIRRes . "TagRawText");
        ExtraModules::KillProcess($resultArray, $createTmpDIRRes . "TagRawText");
    }
    else if (in_array($createDIRRes, array("DIRExists","DIRCreated")) &&
             in_array($createTmpDIRRes, array("DIRExists","DIRCreated")))
    {
        if($createDIRRes == "DIRCreated")
        {
            $contentObj->DirName = $dirName;
            $setPart = "DirName = :dirName";
            $wherePart = "ContentID = :contentID";
            $params = array(":dirName" => $contentObj->DirName, ":contentID" => $contentObj->ContentID);
            Content::PartialUpdate($setPart, $wherePart, $params);
        }

        $corpusDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/";
        $file = $_FILES['RawText'];
        $fileName = str_replace(" ","_",$file['name']);

        //upload the raw file in corpus directory
        if(ExtraModules::UploadFile($fileName, $corpusDir, $file))
        {
            $contentObj->RawTextFileName = $fileName;
            $setPart = "RawTextFileName = :rawTextFileName";
            $wherePart = "ContentID = :contentID";
            $params = array(":rawTextFileName" => $contentObj->RawTextFileName, ":contentID" => $contentObj->ContentID);
            Content::PartialUpdate($setPart, $wherePart, $params);

            //check for segmentation
            $FileExt = pathinfo($fileName, PATHINFO_EXTENSION);
            if ($FileExt == "txt")
            {
                $fileContent = file_get_contents($file['tmp_name']);
            }
            else if ($FileExt == "docx" )
            {
                 $docxObj = new DocxConversion(LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/" . $contentObj->RawTextFileName);
                 $fileContent = $docxObj->convertToText();
            }
            if( strpos($fileContent,"||") === false)
            {
                $oldName = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/" . $contentObj->RawTextFileName;
                $newName = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/notsegmented_" . $contentObj->RawTextFileName;
                if(rename($oldName,$newName))
                    if(!SegmentizeIt($contentObj,'raw'))
                    {
                        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "FailToSegmentizeTagRawText");
                        ExtraModules::KillProcess($resultArray, "FailToSegmentizeTagRawText");
                    }
            }

            CreateConfigFile($corpusDir, $contentObj, "", true);

            //using Manny's python code to create the tagged file
            $taggingResult = CreateTaggedFile($corpusDir, $contentObj->ContentID, $contentObj->L2ID);
            if($taggingResult == true)
            {
                $contentObj->TreeTaggerStatus = "YES";
                $contentObj->ContentStatus = "treeTagger";
                $contentObj->AutomatedTaggedTextFileName = "Tagged_" . $contentObj->RawTextFileName;
                $setPart = "TreeTaggerStatus = :treeTaggerStatus, ContentStatus = :contentStatus, 
                            AutomatedTaggedTextFileName = :automatedTaggedTextFileName, HasLimitedConfig = 'YES' ";
                $wherePart = "ContentID = :contentID";
                $params = array(":treeTaggerStatus" => $contentObj->TreeTaggerStatus, ":contentStatus" => $contentObj->ContentStatus,
                                ":automatedTaggedTextFileName" => $contentObj->AutomatedTaggedTextFileName, ":contentID" => $contentObj->ContentID);
                Content::PartialUpdate($setPart, $wherePart, $params);
                $resultArray[0]["resultMsg"] = "TaggedFileCreated";
            }
            else
            {
                $resultArray[0]["resultMsg"] = "TaggedFileFailed";
            }
        }
        else
        {
            $resultArray[0]["resultMsg"] = "UploadFileFailedTagRawText";
        }
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
}

function CreateResources($fullProcess = true)
{
    //json response is created using this array
   // $start = microtime(true);

    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $contentObj = FillItems($_REQUEST);
    if ($contentObj->ContentID == null) {
        $resultArray[0]["id"] = -1;
    } else {
        $resultArray[0]["id"] = $contentObj->ContentID;
    }

    if ($_FILES['RawText']['error'] == 1 || $_FILES['TaggedText']['error'] == 1 ||
        $_FILES['EmbeddedAudio']['error'] == 1 || $_FILES['EmbeddedCss']['error'] == 1 ||
        $_FILES['EmbeddedImage']['error'] == 1 || $_FILES['EmbeddedScript']['error'] == 1 ||
        $_FILES['ContentJs']['error'] == 1  || $_FILES['ContentCss']['error'] == 1 ||
        $_FILES['PinyinFile']['error'] == 1  || $_FILES['TtsSubstitutionFile']['error'] == 1  ||
        $_FILES['UploadLemmaTranslation']['error'] == 1 || $_FILES['UploadTypeTranslation']['error'] == 1 ||
        $_FILES['UploadTokenTranslation']['error'] == 1 || $_FILES['UploadSegmentTranslation']['error'] == 1) {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "FileSizeError");
        ExtraModules::KillProcess($resultArray, "FileSizeError");
    }

    //checking format and encoding for uploaded files
    if (ExtraModules::FileExists('TaggedText')) {
        if (!ExtraModules::FileUnicodeIsValid("TaggedText"))
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "TtFileUnicodeError");
            ExtraModules::KillProcess($resultArray, "TtFileUnicodeError");
        }

        if (!ExtraModules::FileExtensionIsValid("TaggedText", array('txt', 'docx')))
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "TtFileTypeError");
            ExtraModules::KillProcess($resultArray, "TtFileTypeError");
        }
    } else {
        if (ExtraModules::FileExists('EmbeddedAudio'))
            if (!ExtraModules::FileExtensionIsValid('EmbeddedAudio', array('zip')))
            {
                ExtraModules::KillProcess($resultArray, "eAudioTypeError");
            }

        if (ExtraModules::FileExists('EmbeddedCss'))
            if (!ExtraModules::FileExtensionIsValid('EmbeddedCss', array('zip')))
            {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "eCSSTypeError");
                ExtraModules::KillProcess($resultArray, "eCSSTypeError");
            }

        if (ExtraModules::FileExists('EmbeddedImage'))
            if (!ExtraModules::FileExtensionIsValid('EmbeddedImage', array('zip')))
            {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "eImageTypeError");
                ExtraModules::KillProcess($resultArray, "eImageTypeError");
            }

        if (ExtraModules::FileExists('EmbeddedScript'))
            if (!ExtraModules::FileExtensionIsValid('EmbeddedScript', array('zip')))
            {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "eScriptTypeError");
                ExtraModules::KillProcess($resultArray, "eScriptTypeError");
            }
    }

    if (isset($_REQUEST["ContentCssStatus"]) && ExtraModules::FileExists('ContentCss'))
        if (!ExtraModules::FileExtensionIsValid('ContentCss', array('css')))
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "contentCssTypeError");
            ExtraModules::KillProcess($resultArray, "contentCssTypeError");
        }

    if (isset($_REQUEST["ContentJsStatus"]) && ExtraModules::FileExists('ContentJs'))
        if (!ExtraModules::FileExtensionIsValid('ContentJs', array('js')))
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "contentJsTypeError");
            ExtraModules::KillProcess($resultArray,"contentJsTypeError");
        }

    if (isset($_REQUEST["PinyinStatus"]) && ExtraModules::FileExists('PinyinFile'))
        if (!ExtraModules::FileExtensionIsValid('PinyinFile', array('txt')))
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "pinyinTypeError");
            ExtraModules::KillProcess($resultArray, "pinyinTypeError");
        }

    if (isset($_REQUEST["TtsSubstitutionStatus"]) && ExtraModules::FileExists('TtsSubstitutionFile'))
        if (!ExtraModules::FileExtensionIsValid('TtsSubstitutionFile', array('csv')))
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "ttsSubstitutionTypeError");
            ExtraModules::KillProcess($resultArray, "ttsSubstitutionTypeError");
        }
//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Check uploading files: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    //add or update content to database
    if ($contentObj->ContentID == null)
    {
        //create new data raw in database for new content
        $contentObj->insert();
        $contentObj->ContentID = $contentObj->lastID();
        $resultArray[0]["id"] = $contentObj->ContentID;
    }
    else
    {
        //edit the existing content raw in database
        $oldDirName = $contentObj->DirName;
        $newDirName = $contentObj->ContentID . "_" . str_replace(" ","_",$contentObj->ContentName);
        if(!empty($oldDirName) && $oldDirName != $newDirName)
        {
            rename(LaraContentDir . $oldDirName, LaraContentDir . $newDirName);
            $contentObj->DirName = $newDirName;
        }
        $contentObj->update();
    }

    //creating the folder structure for the saved content
    $dirName = $contentObj->ContentID . "_" . str_replace(" ","_",$contentObj->ContentName);

    $contentDirAddress = LaraContentDir . $dirName;
    $createDIRRes = ExtraModules::CreateDir($contentDirAddress, SubDirNames);

    $tmpDirAddress = ContentTmpDirectory . $dirName;
    $createTmpDIRRes = ExtraModules::CreateDir($tmpDirAddress, SubDirNamesContentTmp);

    //check failure or success in creating directories
    if (in_array($createDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, $createDIRRes . "CreateResources");
        ExtraModules::KillProcess($resultArray, $createDIRRes . "CreateResources");
    }
    else if(in_array($createTmpDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, $createTmpDIRRes . "CreateResources");
        ExtraModules::KillProcess($resultArray, $createTmpDIRRes . "CreateResources");
    }
    else if (in_array($createDIRRes, array("DIRExists","DIRCreated")) &&
             in_array($createTmpDIRRes, array("DIRExists","DIRCreated")))
    {
        if($createDIRRes == "DIRCreated")
        {
            $contentObj->DirName = $dirName;
            $setPart = "DirName = :dirName";
            $wherePart = "ContentID = :contentID";
            $params = array(":dirName" => $contentObj->DirName, ":contentID" => $contentObj->ContentID);
            Content::PartialUpdate($setPart, $wherePart, $params);
        }

        $corpusDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/";
        $resourcesDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
        $backupDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;
        $createBackupDIRRes = ExtraModules::CreateDir($backupDir);
        if (in_array($createBackupDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, $createBackupDIRRes . "CreateResources");
            ExtraModules::KillProcess($resultArray, $createBackupDIRRes . "CreateResources");
        }

//        $time_elapsed_secs = microtime(true) - $start;
//        echo("Creating directories: " . $time_elapsed_secs. "----");
//        $start = microtime(true);
        //if the user uploaded a tagged text, so it should be uploaded on the server and check for segmentation and embedded files
        //if not, check for embedded files
        if(ExtraModules::FileExists('TaggedText'))
        {
            $file = $_FILES['TaggedText'];
            $fileName = str_replace(" ","_",$file['name']);
            if(ExtraModules::UploadFile($fileName, $corpusDir, $file))
            {
                $contentObj->TaggedTextFileName = $fileName;
                $setPart = "TaggedTextFileName = :taggedTextFileName";
                $wherePart = "ContentID = :contentID";
                $params = array(":taggedTextFileName" => $contentObj->TaggedTextFileName, ":contentID" => $contentObj->ContentID);
                Content::PartialUpdate($setPart, $wherePart, $params);

                //check for segmentation
                $FileExt = pathinfo($fileName, PATHINFO_EXTENSION);
                if ($FileExt == "txt")
                {
                    $fileContent = file_get_contents($file['tmp_name']);
                }
                else if ($FileExt == "docx" )
                {
                    $docxObj = new DocxConversion(LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/" . $contentObj->TaggedTextFileName);
                    $fileContent = $docxObj->convertToText();
                }
                if(strpos($fileContent,"||") === false)
                {
                    $oldName = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/" . $contentObj->TaggedTextFileName;
                    $newName = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/notsegmented_" . $contentObj->TaggedTextFileName;
                    if(rename($oldName,$newName))
                        if(!SegmentizeIt($contentObj, 'tagged'))
                        {
                            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "FailToSegmentizeCreateResources");
                            ExtraModules::KillProcess($resultArray,"FailToSegmentizeCreateResources");
                        }
                }

                //check for embedded files in tagged file
                $hasEmbeddedFiles = CheckForEmbeddedFiles($contentObj);
                if ($hasEmbeddedFiles == 'hasEmbedded') {
                    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "hasEmbedded");
                    ExtraModules::KillProcess($resultArray, $hasEmbeddedFiles);
                }
            }
            else {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "UploadFileFailedCreateResources");
                ExtraModules::KillProcess($resultArray, "UploadFileFailedCreateResources");
            }
        }
        else if(isset($_REQUEST["UseAutomatedTaggedTextStatus"]))
        {
            $contentObj->TaggedTextFileName = $contentObj->AutomatedTaggedTextFileName;
            $setPart = "TaggedTextFileName = :taggedTextFileName";
            $wherePart = "ContentID = :contentID";
            $params = array(":taggedTextFileName" => $contentObj->TaggedTextFileName, ":contentID" => $contentObj->ContentID);
            Content::PartialUpdate($setPart, $wherePart, $params);

            //check for embedded files in tagged file
            $hasEmbeddedFiles = CheckForEmbeddedFiles($contentObj);
            if ($hasEmbeddedFiles == 'hasEmbedded') {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, $hasEmbeddedFiles);
                ExtraModules::KillProcess($resultArray, $hasEmbeddedFiles);
            }
        }
        else
        {
            if($contentObj->HasEmbeddedImage == 'YES' && ExtraModules::FileExists('EmbeddedImage'))
                ManageEmbeddedItems("EmbeddedImage", "images.zip", "images", "Image", "FailedToExtractZipFile", $contentObj);

            if($contentObj->HasEmbeddedCSS == 'YES'&& ExtraModules::FileExists('EmbeddedCss'))
                ManageEmbeddedItems("EmbeddedCss", "css.zip", "corpus", "CSS", "FailedToOpenZipFile", $contentObj);

            if($contentObj->HasEmbeddedScript == 'YES'&& ExtraModules::FileExists('EmbeddedScript'))
                ManageEmbeddedItems("EmbeddedScript", "script.zip", "corpus", "Script", "FailedToOpenZipFile", $contentObj);

            if($contentObj->HasEmbeddedAudio == 'YES'&& ExtraModules::FileExists('EmbeddedAudio'))
                ManageEmbeddedItems("EmbeddedAudio", "audio.zip", "----- ", "Audio", "FailedToOpenZipFile", $contentObj);
        }

        //check if any CSS for content is uploaded
        if(isset($_REQUEST["ContentCssStatus"]) && ExtraModules::FileExists('ContentCss'))
        {
            $file = $_FILES['ContentCss'];
            $fileName = $file['name'];
            if(ExtraModules::UploadFile($fileName, $corpusDir, $file))
            {
                $contentObj->ContentCssFileName = $fileName;
                $setPart = "ContentCssFileName = :contentCssFileName, HasContentCss = 'YES'";
                $wherePart = "ContentID = :contentID";
                $params = array(":contentCssFileName" => $contentObj->ContentCssFileName, ":contentID" => $contentObj->ContentID);
                Content::PartialUpdate($setPart, $wherePart, $params);
            }
            else {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "UploadCssFileFailed");
                ExtraModules::KillProcess($resultArray, "UploadCssFileFailed");
            }
        }

        //check if any pinyin for content is uploaded
        if(isset($_REQUEST["PinyinStatus"]) && ExtraModules::FileExists('PinyinFile'))
        {
            $file = $_FILES['PinyinFile'];
            $fileName = $file['name'];
            if(ExtraModules::UploadFile($fileName, $corpusDir, $file))
            {
                $contentObj->PinyinFileName = $fileName;
                $setPart = "PinyinFileName = :pinyinFileName, HasPinyin = 'YES'";
                $wherePart = "ContentID = :contentID";
                $params = array(":pinyinFileName" => $contentObj->PinyinFileName, ":contentID" => $contentObj->ContentID);
                Content::PartialUpdate($setPart, $wherePart, $params);
            }
            else {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "UploadPinyinFileFailed");
                ExtraModules::KillProcess($resultArray, "UploadPinyinFileFailed");
            }
        }

        //check if any tts substitution for content is uploaded
        if(isset($_REQUEST["TtsSubstitutionStatus"]) && ExtraModules::FileExists('TtsSubstitutionFile'))
        {
            $file = $_FILES['TtsSubstitutionFile'];
            $fileName = $file['name'];
            if(ExtraModules::UploadFile($fileName, $corpusDir, $file))
            {
                $contentObj->TtsSubstitutionFileName = $fileName;
                $setPart = "TtsSubstitutionFileName = :tsFileName, HasTtsSubstitution = 'YES'";
                $wherePart = "ContentID = :contentID";
                $params = array(":tsFileName" => $contentObj->TtsSubstitutionFileName, ":contentID" => $contentObj->ContentID);
                Content::PartialUpdate($setPart, $wherePart, $params);
            }
            else {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "UploadTtsSubstitutionFileFailed");
                ExtraModules::KillProcess($resultArray, "UploadTtsSubstitutionFileFailed");
            }
        }

        //check if any JS for content is uploaded
        if(isset($_REQUEST["ContentJsStatus"]) && ExtraModules::FileExists('ContentJs'))
        {
            $file = $_FILES['ContentJs'];
            $fileName = $file['name'];
            if(ExtraModules::UploadFile($fileName, $corpusDir, $file))
            {
                $contentObj->ContentJsFileName = $fileName;
                $setPart = "ContentJsFileName = :contentJsFileName, HasContentJs = 'YES'";
                $wherePart = "ContentID = :contentID";
                $params = array(":contentJsFileName" => $contentObj->ContentJsFileName, ":contentID" => $contentObj->ContentID);
                Content::PartialUpdate($setPart, $wherePart, $params);
            }
            else {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "UploadJsFileFailed");
                ExtraModules::KillProcess($resultArray, "UploadJsFileFailed");
            }
        }

//        $time_elapsed_secs = microtime(true) - $start;
//        echo("Check embedded files: " . $time_elapsed_secs . "----");
//        $start = microtime(true);
        //Create and save Config file
        $tokenType = $_REQUEST["tokenType"];
        $accessToken = $_REQUEST["accessToken"];
        $headerInfo = $tokenType . " " . $accessToken ;
        CreateConfigFile($corpusDir, $contentObj, $headerInfo, false);


        if(!$fullProcess)
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "ConfigParamsSet");
            ExtraModules::KillProcess($resultArray,   "ConfigParamsSet");
        }

//        $time_elapsed_secs = microtime(true) - $start;
//        echo("Create Config file:" . $time_elapsed_secs . "----");
//        $start = microtime(true);

        $wordLDT = $contentObj->WordLdtTaskID;
        $segmentLDT = $contentObj->SegmentLdtTaskID;

        if (($contentObj->WordsAudioType == 'human' || $contentObj->SegmentsAudioType == 'human') &&
            ($wordLDT != '' || $segmentLDT != '') &&
            $contentObj->LdtDeactivateStatus == 'NO')
            if (!InstallHumanAudio($contentObj, $tokenType, $accessToken))
            {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "InstallPrvAudioFailed");
                ExtraModules::KillProcess($resultArray, "InstallPrvAudioFailed");
            }

//        $time_elapsed_secs = microtime(true) - $start;
//        echo("Install Human Audio: " . $time_elapsed_secs . "----");
//        $start = microtime(true);

        if($contentObj->WordsAudioType == 'tts')
            if (!InstallTTS($contentObj, "words"))
            {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "InstallPrvTTSWordsFailed");
                ExtraModules::KillProcess($resultArray, "InstallPrvTTSWordFailed");
            }

//        $time_elapsed_secs = microtime(true) - $start;
//        echo("Install TTS Words: " . $time_elapsed_secs . "----");
//        $start = microtime(true);


        if($contentObj->SegmentsAudioType == 'tts')
            if (!InstallTTS($contentObj, "segments"))
            {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "InstallPrvTTSSegmentsFailed");
                ExtraModules::KillProcess($resultArray, "InstallPrvTTSSegmentsFailed");
            }

//        $time_elapsed_secs = microtime(true) - $start;
//        echo("Install TTS Segments: " . $time_elapsed_secs . "----");
//        $start = microtime(true);

	// Begin Picturebook functionality added by MR
	$downloadFromSelectorToolResult = DownloadFromSelectorTool($corpusDir, $contentObj->ContentID);

	if($downloadFromSelectorToolResult == "Failed")
	{
	     ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "DownloadFromSelectorToolFailed");
             ExtraModules::KillProcess($resultArray, "DownloadFromSelectorToolFailed");
        }
	// End Picturebook functionality added by MR

        //using Python code to create the resources file
        $createResourcesResult = CreateResourceFiles($corpusDir, $resourcesDir, $contentObj->ContentID);

	// Begin Picturebook functionality added by MR
	// $selectorToolWebDir is probably better defined in a config file
	$selectorToolWebDir = CallectorDir . word_locations;
	$uploadToSelectorToolResult = InstallAndUploadToSelectorTool($corpusDir, $resourcesDir, $selectorToolWebDir, $contentObj->ContentID);

	if($uploadToSelectorToolResult == "Failed")
	{
	     ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "UploadToSelectorToolFailed");
             ExtraModules::KillProcess($resultArray, "UploadToSelectorToolFailed");
        }
	// End Picturebook functionality added by MR

//        $time_elapsed_secs = microtime(true) - $start;
//        echo("Create resources using Python: " . $time_elapsed_secs . "----");
//        $start = microtime(true);

        if($createResourcesResult == "SucceedWithWarning" ||
           $createResourcesResult == "Succeed") {

            if(!CreateMultiWordFile($corpusDir, $resourcesDir, $contentObj->ContentID))
            {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "CreateMultiWordAnnotationFailed");
                ExtraModules::KillProcess($resultArray, "CreateMultiWordAnnotationFailed");
            }

//            $time_elapsed_secs = microtime(true) - $start;
//            echo("Create Multi Word File: " . $time_elapsed_secs . "----");
//            $start = microtime(true);

            if($contentObj->IgnoreLargeFileTransfer == "NO")
            {
                ReadContentLemmas($resourcesDir, $backupDir, $contentObj->ContentID);

//                $time_elapsed_secs = microtime(true) - $start;
//                echo("Read lemma(Total): " . $time_elapsed_secs . "----");
//                $start = microtime(true);

                ReadContentTypes($resourcesDir, $backupDir, $contentObj->ContentID);

//                $time_elapsed_secs = microtime(true) - $start;
//                echo("Read type(Total): " . $time_elapsed_secs . "----");
//                $start = microtime(true);

                ReadContentSegments($resourcesDir, $backupDir, $contentObj->ContentID);

//                $time_elapsed_secs = microtime(true) - $start;
//                echo("Read segment(Total): " . $time_elapsed_secs . "----");
//                $start = microtime(true);

                ReadContentTokens($resourcesDir, $backupDir, $contentObj->ContentID);

//                $time_elapsed_secs = microtime(true) - $start;
//                echo("Read Token(Total): " . $time_elapsed_secs . "----");
//                $start = microtime(true);

                ReadContentMultiWords($resourcesDir, $backupDir, $contentObj->ContentID);

//                $time_elapsed_secs = microtime(true) - $start;
//                echo("Read multi words(Total): " . $time_elapsed_secs . "----");
//                $start = microtime(true);

               /* ReadRawData($resourcesDir, $backupDir, $contentObj->ContentID);
                $time_elapsed_secs = microtime(true) - $start;
                echo("Read Raw data(Total): " . $time_elapsed_secs . "----");
                $start = microtime(true);*/
            }

            if ($contentObj->WordsAudioType == 'human' &&
                filesize($resourcesDir . 'ldt_word_recording_full.json') != 0 &&
                $contentObj->LdtDeactivateStatus == 'NO')
            {
                if ($wordLDT != '' && !DeleteLDTTask($tokenType, $accessToken, $wordLDT)) {
                        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "DeletePrvWordFailed");
                        ExtraModules::KillProcess($resultArray, "DeletePrvWordFailed");
                    }

//                $time_elapsed_secs = microtime(true) - $start;
//                echo("Delete LDT words: " . $time_elapsed_secs . "----");
//                $start = microtime(true);


                $wordLDT = CreateLDTTask($tokenType, $accessToken, $resourcesDir . 'ldt_word_recording_full.json',
                            $contentObj->ContentName . "_words", $contentObj->WordAudio, $contentObj->VideoAnnotations);
                if ($wordLDT != "-1")
                {
                    $contentObj->WordLdtTaskID = $wordLDT;
                    //LogLDTTaskTrace("word", $contentObj->WordLdtTaskID, $contentObj->ContentID );
                }

//                $time_elapsed_secs = microtime(true) - $start;
//                echo("Create LDT words: " . $time_elapsed_secs . "----");
//                $start = microtime(true);
            }

            if ($contentObj->SegmentsAudioType == 'human' &&
                filesize($resourcesDir . 'ldt_segment_recording_full.json') != 0 &&
                $contentObj->LdtDeactivateStatus == 'NO')
            {
                if($contentObj->SegmentLdtTaskID != '' && !DeleteLDTTask($tokenType, $accessToken, $contentObj->SegmentLdtTaskID))
                {
                    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "DeletePrvSegFailed");
                    ExtraModules::KillProcess($resultArray, "DeletePrvSegFailed");
                }

//                $time_elapsed_secs = microtime(true) - $start;
//                echo("Delete LDT segment: " . $time_elapsed_secs . "----");
//                $start = microtime(true);

                $segmentLDT = CreateLDTTask($tokenType, $accessToken, $resourcesDir . 'ldt_segment_recording_full.json',
                                        $contentObj->ContentName . "_segments", $contentObj->SegmentAudio, $contentObj->VideoAnnotations);
                if($segmentLDT != "-1")
                {
                    $contentObj->SegmentLdtTaskID = $segmentLDT;
                    //LogLDTTaskTrace("segment", $contentObj->SegmentLdtTaskID, $contentObj->ContentID );
                }

//                $time_elapsed_secs = microtime(true) - $start;
//                echo("create LDT segments: " . $time_elapsed_secs . "----");
//                $start = microtime(true);
            }

            if($contentObj->LdtDeactivateStatus == 'NO' && ($wordLDT == "-1" || $segmentLDT == "-1"))
            {
                $resultArray[0]["resultMsg"] = "CreateLDTTaskFailed";
            }
            else {
                if($createResourcesResult  == "SucceedWithWarning")
                    $resultArray[0]["resultMsg"] = "FirstCompileStepWithWarningDone";
                else
                    $resultArray[0]["resultMsg"] = "FirstCompileStepDone";

                $contentObj->ContentStatus = "resources";
                $setPart = "  HasMainConfig = 'YES', ContentStatus = :contentStatus";
                $params = array(":contentStatus" => $contentObj->ContentStatus);

                if (!empty($contentObj->WordLdtTaskID) && $contentObj->LdtDeactivateStatus == 'NO') {
                    $setPart .= ", WordLdtTaskID = :wordLDT";
                    $params[":wordLDT"] = $contentObj->WordLdtTaskID;
                }

                if (!empty($contentObj->SegmentLdtTaskID) && $contentObj->LdtDeactivateStatus == 'NO')
                {
                    $setPart .= ", SegmentLdtTaskID = :segmentLDT ";
                    $params[":segmentLDT"] = $contentObj->SegmentLdtTaskID;
                }

                $wherePart = "ContentID = :contentID";
                $params[":contentID"] = $contentObj->ContentID;

                Content::PartialUpdate($setPart, $wherePart, $params);
            }
        }
        else
        {
            $resultArray[0]["resultMsg"] = "FirstCompileStepFailed";
        }
    }

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("register ldt tasks id in db : " . $time_elapsed_secs . "----");
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function CreatePages()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $_GET["contentID"]);
    $info = Content::SearchContent($where, $whereParam);
    $contentObj = FillItems($info[0]);

    $resultArray[0]["id"] = $contentObj->ContentID;

    $tokenType = $_REQUEST["tokenType"];
    $accessToken = $_REQUEST["accessToken"];

    $wordLDT = $contentObj->WordLdtTaskID;
    $segmentLDT = $contentObj->SegmentLdtTaskID;

    if (($contentObj->WordsAudioType == 'human' || $contentObj->SegmentsAudioType == 'human') &&
        ($wordLDT != '' || $segmentLDT != '') &&
        $contentObj->LdtDeactivateStatus == 'NO')
        if (!InstallHumanAudio($contentObj, $tokenType, $accessToken))
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "InstallZipfileFailed");
            ExtraModules::KillProcess($resultArray, "InstallZipfileFailed");
        }

    if($contentObj->WordsAudioType == 'tts')
        if (!InstallTTS($contentObj, "words"))
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "InstallTTSWordsFailed");
            ExtraModules::KillProcess($resultArray, "InstallTTSWordsFailed");
        }

    if($contentObj->SegmentsAudioType == 'tts')
        if (!InstallTTS($contentObj, "segments"))
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "InstallTTSSegmentsFailed");
            ExtraModules::KillProcess($resultArray, "InstallTTSSegmentsFailed");
        }

    $dirName = $contentObj->ContentID . "_" . str_replace(" ","_",$contentObj->ContentName);
    $audioDir = LaraContentDir . $dirName . "/" . SubDirNames["audio"] . "/";
    $corpusDir = LaraContentDir . $dirName . "/" . SubDirNames["corpus"] . "/";
    $configFile = $corpusDir . "local_config.json";

    // Begin Picturebook functionality added by MR
    $downloadFromSelectorToolResult = DownloadFromSelectorTool($corpusDir, $contentObj->ContentID);

    if($downloadFromSelectorToolResult == "Failed")
	{
	     ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "DownloadFromSelectorToolFailed");
             ExtraModules::KillProcess($resultArray, "DownloadFromSelectorToolFailed");
        }
    // End Picturebook functionality added by MR

    if($contentObj->HasEmbeddedAudio == "YES")
        if(!InstallNonLdtAudio($audioDir, $configFile, $contentObj->ContentID))
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "InstallNonLDTAudioFailed");
            ExtraModules::KillProcess($resultArray, "InstallNonLDTAudioFailed");
        }

    if (CreatePageFiles($corpusDir, $contentObj->ContentID)) {
        $compileDir = ContentTmpDirectory . $dirName . "/" . SubDirNamesContentTmp["compiled"] . "/";
        $srcDirName = str_replace(" ", "_", $contentObj->ContentName). "vocabpages";
        $destDirName = $contentObj->DirName . "vocabpages";
        if (CopyToWeb($compileDir, $srcDirName, $destDirName, $contentObj->ContentID))
        {
            $resultArray[0]["resultMsg"] = "PageCreationDone";
            $contentObj->ContentStatus ="pages";
            $contentObj->WebAddress = WebRoot . $destDirName . "/_hyperlinked_text_.html";
            $setPart = "WebAddress = :webAddress, ContentStatus = :contentStatus ";
            $wherePart = "ContentID = :contentID";
            $params = array(":webAddress" => $contentObj->WebAddress, ":contentStatus" => $contentObj->ContentStatus, ":contentID" => $contentObj->ContentID);
            Content::PartialUpdate($setPart, $wherePart, $params);

            /*if(CreatePageFilesForSocialNetwork($corpusDir, $contentObj->ContentID))
            {
                $destDirName = SnContentDir . $contentObj->DirName;
                if (!CopyToSnDir($compileDir, $srcDirName, $destDirName, $contentObj->ContentID))
                {
                    $resultArray[0]["resultMsg"] = "CopyingPagesForSnFailed";
                }
            }
            else
            {
                $resultArray[0]["resultMsg"] = "CreatePagesForSnFailed";

            }*/
        }
        else{
            $resultArray[0]["resultMsg"] = "CopyingPagesFailed";
        }
    }
    else {
        $resultArray[0]["resultMsg"] = "CreatePagesFailed";
    }

    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function FillItems($src)
{
    $contentObj = new Content();
    PdoDataAccess::FillObjectByArray($contentObj, $src);
    return $contentObj;
}

function MakeEmptyContent()
{
    $contentObj = new Content();
    $contentObj->CreatorID = $_SESSION[SessionIndex['UserID']];
    $contentObj->L1ID = -1;
    $contentObj->L2ID = -1;
    $contentObj->WordsAudioType = 'human';
    $contentObj->SegmentsAudioType = 'human';
    $contentObj->WordAudio = -1;
    $contentObj->SegmentAudio = -1;
    $contentObj->ContentStatus = 'raw';
    $contentObj->TreeTaggerStatus = 'NO';
    $contentObj->LdtDeactivateStatus = 'NO';
    $contentObj->AudioMouseOver = 'YES';
    $contentObj->WordTranslationMouseOver = 'YES';
    $contentObj->WordsNote = 'YES';
    $contentObj->AudioSegments = 'YES';
    $contentObj->HasAudioTracking = 'NO';
    $contentObj->SegmentTranslationMouseOver = 'YES';
    $contentObj->SegmentTranslationAsPopup = 'YES';
    $contentObj->WordTranslationsOn = 'lemma';
    $contentObj->WordTranslationFC = 'NO';
    $contentObj->AudioTranslationFC= 'NO';
    $contentObj->SignedVideoFC= 'NO';
    $contentObj->GapFC= 'NO';
    $contentObj->ShowTextContext = 'YES';
    $contentObj->ShowMultimediaContext = 'YES';
    $contentObj->L1rtl = 'NO';
    $contentObj->SegmentAudioKeepDuplicates = "NO";
    $contentObj->TableOfContents = 'NO';
    $contentObj->KeepComments = 'NO';
    $contentObj->CommentsByDefault = 'NO';
    $contentObj->LinguisticsArticleComments = 'NO';
    $contentObj->ColouredWords = 'NO';
    $contentObj->AudioWordsInColour = 'NO';
    $contentObj->TranslatedWordsInColour = 'NO';
    $contentObj->MweWordsInColour = 'NO';
    $contentObj->VideoAnnotations= 'NO';
    $contentObj->VideoAnnotationsFromTranslation= 'NO';
    $contentObj->MaxExamplesPerWordPage = '10';
    $contentObj->ExtraPageInfo = 'NO';
    $contentObj->Font = 'serif';
    $contentObj->FrequencyListsInMainText = 'NO';
    $contentObj->IgnoreLargeFileTransfer = 'NO';
    $contentObj->AddPostagsToLemma = 'NO';
    $contentObj->HasEmbeddedAudio = 'NO';
    $contentObj->HasEmbeddedCSS = 'NO';
    $contentObj->HasEmbeddedImage = 'NO';
    $contentObj->HasEmbeddedScript = 'NO';
    $contentObj->HasExternalResources = 'NO';
    $contentObj->HasContentCss = 'NO';
    $contentObj->HasContentJs = 'NO';
    $contentObj->HasPinyin = 'NO';
    $contentObj->HasTtsSubstitution = 'NO';
    $contentObj->LangRepType = 'Public';
    $contentObj->HasLimitedConfig = 'NO';
    $contentObj->HasMainConfig = 'NO';
    $contentObj->CrowdsourcingStatus =  'None';
    $contentObj->SegmentTranslationCharacter = '✎';
    return $contentObj;
}

function CreateTaggedFile($fileDir, $contentID, $l2ID)
{
    if($l2ID == 136000)//polish
    {
        $bashFile = $fileDir . "CheckPolishTaggerServeStatus.txt";
        $fp = fopen( $bashFile, "w");
        $command = LaraEnv . " " . MorfeuszEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py check_concraft_server_status " .
            $fileDir . "limited_local_config.json " . $fileDir . "CheckPolishTaggerServeStatusReply.txt 2>&1";
        fwrite($fp, $command);
        fclose($fp);

        $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentID, ContentRelatedPage);
        $output = shell_exec('bash < '  . $bashFile );
        ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentID, ContentRelatedPage, $LogID);

        if(strpos(file_get_contents($fileDir . "CheckPolishTaggerServeStatusReply.txt"),"*** Error:") !== false)
            return false;
    }

    $bashFile = $fileDir . "TreeTaggerCommand.txt";
    $fp = fopen( $bashFile, "w");
    $command = LaraEnv . " " . TreeTaggerEnv . " " . MorfeuszEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py treetagger " .
        $fileDir . "limited_local_config.json 2>&1";
    fwrite($fp, $command);
    fclose($fp);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentID, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentID, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") === false)
        return true;
    else
        return false;
}

function UnzipIt($zipFile, $destination)
{
    $bashFile = $destination . "unzipIt.txt";
    $fp = fopen( $bashFile, "w");
    // Sanitise arguments - MR
    $zipFileSanitised = filter_var($zipFile, FILTER_SANITIZE_STRING);
    $destinationSanitised = filter_var($destination, FILTER_SANITIZE_STRING);
    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py unzip " . $zipFileSanitised .
        " " .  $destinationSanitised . " 2>&1";
    fwrite($fp, $command);
    fclose($fp);

    //$LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentID, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    //ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentID, ContentRelatedPage, $LogID);

    if(strpos($output, "Unzipped") !== false)
        return true;
    else
        return false;
}

function CreateConfigFile($corpusDir, $contentObj, $headerInfo, $limited = false)
{
    $L1Name = Language::getLanguageName($contentObj->L1ID);
    $L1DirName = LaraContentDir . $L1Name;
    $l1DirRes = ExtraModules::CreateDir($L1DirName);

    $L2Name = Language::getLanguageName($contentObj->L2ID);
    $L2DirName = LaraContentDir . $L2Name;
    $l2DirRes = ExtraModules::CreateDir($L2DirName);
    $UserName = Account::GetUserName($contentObj->CreatorID);
    $TranslationFileName = $L2Name . "_" . $L1Name . ".csv";

    $local_config_data = array();
    $local_config_data["id"] = str_replace(" ", "_", $contentObj->ContentName);
    $local_config_data["language"] =  $L2Name;
    $resourcesDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;

    if(!$limited)
    {
        $local_config_file = $corpusDir . 'local_config.json';
        $sn_config_file = $corpusDir . 'sn_config.json';

        $wordUserName = Account::GetLdtUserName($headerInfo, $contentObj->WordAudio);
        $segmentUserName = Account::GetLdtUserName($headerInfo, $contentObj->SegmentAudio);

        if ($contentObj->L1rtl == 'YES') {
            $local_config_data["text_direction"] = "rtl";
        }
        $local_config_data["max_examples_per_word_page"] = $contentObj->MaxExamplesPerWordPage;
        $local_config_data["corpus"] = $corpusDir . $contentObj->TaggedTextFileName;

        if($contentObj->WordsAudioType == 'human')
            $local_config_data["word_audio_directory"] = LaraContentDir . $L2Name . '/' . SubDirNames["audio"] . '/' . $wordUserName;
        else if($contentObj->WordsAudioType == 'tts')
            $local_config_data["word_audio_directory"] = LaraContentDir . $L2Name . '/' . SubDirNames["audio"] . '/' .
                $L2Name . "_" . $contentObj->TtsEngine . "_" . $contentObj->TtsVoice;

        if($contentObj->LangRepType == "Public") {
            if ($contentObj->WordTranslationsOn == 'lemma')
            {
                $local_config_data["translation_spreadsheet"] = LaraContentDir . $L2Name . '/' . SubDirNames["translations"] . '/' . $TranslationFileName ;
            }
            else if ($contentObj->WordTranslationsOn == 'surface_word_type')
            {
                $local_config_data["translation_spreadsheet_surface"] = LaraContentDir . $L2Name . '/' . SubDirNames["translations"] . '/type_' . $TranslationFileName ;
            }
            else if ($contentObj->WordTranslationsOn == 'surface_word_token')
            {
                $local_config_data["translation_spreadsheet_surface"] = LaraContentDir . $L2Name . '/' . SubDirNames["translations"] . '/type_' . $TranslationFileName;
                $local_config_data["translation_spreadsheet_tokens"] =  LaraContentDir . $contentObj->DirName . '/' . SubDirNames["translations"] . '/token_' . $TranslationFileName;
            }
        }
        else
        {
            $local_config_data["translation_spreadsheet"] = LaraContentDir . $L2Name . '/' . SubDirNames["translations"] . '/' . $UserName . '_' . $TranslationFileName;
        }

        if($contentObj->WordsNote == "YES")
        {
            $local_config_data["notes_spreadsheet"] = LaraContentDir . $contentObj->DirName . '/' . SubDirNames["corpus"] . '/notes.csv';
            $local_config_data["note_words_in_colour"] = "yes";
        }

        if($contentObj->HasAudioTracking == "YES")
            $local_config_data["audio_tracking_file"] = LaraContentDir . $contentObj->DirName . '/' . SubDirNames["audio"] . '/' . $segmentUserName . '/audio_tracking.json';

        if($contentObj->SegmentsAudioType == 'human')
            $local_config_data["segment_audio_directory"] = LaraContentDir . $contentObj->DirName . '/' . SubDirNames["audio"] . '/' . $segmentUserName ;
        else if($contentObj->SegmentsAudioType == 'tts')
            $local_config_data["segment_audio_directory"] = LaraContentDir . $contentObj->DirName . '/' . SubDirNames["audio"] . '/' .
                $L2Name . "_" . $contentObj->TtsEngine . "_" . $contentObj->TtsVoice;

        $local_config_data["segment_translation_spreadsheet"] = LaraContentDir . $contentObj->DirName . '/' . SubDirNames["translations"] . '/' . $TranslationFileName ;

        $local_config_data["translation_mouseover"] = strtolower($contentObj->WordTranslationMouseOver) ;
        $local_config_data["audio_mouseover"] = strtolower($contentObj->AudioMouseOver) ;
        $local_config_data["segment_translation_mouseover"] = strtolower($contentObj->SegmentTranslationMouseOver) ;
        $local_config_data["segment_translation_as_popup"] = strtolower($contentObj->SegmentTranslationAsPopup) ;
        if(!empty($contentObj->SegmentTranslationCharacter))
            $local_config_data["segment_translation_character"] = $contentObj->SegmentTranslationCharacter ;
        $local_config_data["audio_segments"] = strtolower($contentObj->AudioSegments) ;
        $local_config_data["word_translations_on"] = $contentObj->WordTranslationsOn ;

        if($contentObj->PlayParts == "")
            $local_config_data["play_parts"] = [];
        else
            $local_config_data["play_parts"] =  json_decode($contentObj->PlayParts);

        $local_config_data["segment_audio_keep_duplicates"] = strtolower($contentObj->SegmentAudioKeepDuplicates) ;
        $local_config_data["allow_table_of_contents"] = strtolower($contentObj->TableOfContents) ;
        $local_config_data["keep_comments"] = strtolower($contentObj->KeepComments) ;
        $local_config_data["comments_by_default"] =  strtolower($contentObj->CommentsByDefault) ;
        $local_config_data["linguistics_article_comments"] = strtolower($contentObj->LinguisticsArticleComments) ;
        $local_config_data["coloured_words"] = strtolower($contentObj->ColouredWords) ;
        $local_config_data["extra_page_info"] = strtolower($contentObj->ExtraPageInfo) ;
        if ($contentObj->AudioWordsInColour == 'YES')
            $local_config_data["audio_words_in_colour"] = "red";
        $local_config_data["translated_words_in_colour"] =  strtolower($contentObj->TranslatedWordsInColour) ;
        $local_config_data["font"] = strtolower($contentObj->Font) ;
        $local_config_data["frequency_lists_in_main_text_page"] = strtolower($contentObj->FrequencyListsInMainText) ;

        if($contentObj->ContentCssFileName != "")
            $local_config_data["css_file"] = $contentObj->ContentCssFileName ;
        if($contentObj->ContentJsFileName != "")
            $local_config_data["script_file"] = $contentObj->ContentJsFileName ;
        if($contentObj->PinyinFileName != "")
            $local_config_data["pinyin_corpus"] = $corpusDir . $contentObj->PinyinFileName ;

        if($contentObj->TtsSubstitutionFileName != "")
            $local_config_data["tts_word_substitution_spreadsheet"] = $corpusDir . $contentObj->TtsSubstitutionFileName;

        //add MWE options
        $local_config_data["mwe_words_in_colour"] = strtolower($contentObj->MweWordsInColour) ;
        $local_config_data["video_annotations"] = strtolower($contentObj->VideoAnnotations) ;
        $local_config_data["video_annotations_from_translation"] = strtolower($contentObj->VideoAnnotationsFromTranslation) ;

        $local_config_data["mwe_file"] = LaraContentDir . $L2Name . '/' . SubDirNames["corpus"] . '/mwe_defs.txt';
        $local_config_data["mwe_annotations_file"] = $resourcesDir . 'mwe_annotations.json';

        //tts engine and voice
        if($contentObj->TtsEngine != -1)
        {
            $local_config_data["tts_engine"] = $contentObj->TtsEngine;
            $local_config_data["tts_voice"] = $contentObj->TtsVoice;
        }
    }
    else
    {
        $local_config_file = $corpusDir . 'limited_local_config.json';

        $local_config_data["untagged_corpus"] =  $corpusDir . $contentObj->RawTextFileName ;
        $local_config_data["tagged_corpus"] = $corpusDir . "Tagged_" . $contentObj->RawTextFileName ;
        $local_config_data["add_postags_to_lemma"] = strtolower($contentObj->AddPostagsToLemma) ;
    }

    $local_config_data["compiled_directory"] = ContentTmpDirectory . $contentObj->DirName . '/' . SubDirNamesContentTmp["compiled"] ;
    $local_config_data["lara_tmp_directory"] = ContentTmpDirectory . $contentObj->DirName . '/' . SubDirNamesContentTmp["laraTmpDirectory"] ;
    $local_config_data["working_tmp_directory"] = WorkingTmpDirectory ;
    $local_config_data["image_directory"] = LaraContentDir . $contentObj->DirName . '/' . SubDirNames["images"];

    $handle = fopen($local_config_file, 'w') or die('Cannot open file:  ' . $local_config_file);
    fwrite($handle, json_encode($local_config_data,JSON_PRETTY_PRINT | JSON_NUMERIC_CHECK ));
    fclose($handle);

    if(!$limited)
    {
        $sn_config_data = $local_config_data;
        $sn_config_data["html_style"] = "social_network";
        $sn_config_data["relative_compiled_directory"] = SnContentDir . $contentObj->DirName ;

        $handle = fopen($sn_config_file, 'w') or die('Cannot open file:  ' . $sn_config_file);
        fwrite($handle, json_encode($sn_config_data,JSON_PRETTY_PRINT | JSON_NUMERIC_CHECK));
        fclose($handle);
    }

    $LogID = ExtraModules::ExternalCmndLog(EL_TypeConfigFile, $local_config_data, $contentObj->ContentID, ContentRelatedPage);
    return true;
}

function CountAudioAndTranslation($contentObj)
{
    $corpusDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/";
    // Sanitise argument - MR
    $corpusDirSanitised = filter_var($corpusDir, FILTER_SANITIZE_STRING);
    $configFile = $corpusDirSanitised . "local_config.json";
    $resFile  = $corpusDirSanitised. "AudioAndTranslationRes.json";
    $bashFile = $corpusDirSanitised . "AudioAndTranslationCount.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py " .
        "count_audio_and_translation_files  " . $configFile."  " . $resFile . " 2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentObj->ContentID, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentObj->ContentID, ContentRelatedPage, $LogID);

    if($output == false || strpos($output, "*** Error") !== false )
        return false;

    $outputString = file_get_contents($resFile);
    return json_decode($outputString, true);
}

function SegmentizeIt($contentObj, $stage)
{
    $corpusDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/";
    // Sanitise argument - MR
    $corpusDirSanitised = filter_var($corpusDir, FILTER_SANITIZE_STRING);

    $contentL2 = Language::getLanguageName($contentObj->L2ID);
    if($stage == 'raw')
    {        $nonSegfileName = "notsegmented_" . $contentObj->RawTextFileName;
        $fileName = $contentObj->RawTextFileName;
    }
    else if($stage == 'tagged')
    {
        $nonSegfileName = "notsegmented_" . $contentObj->TaggedTextFileName;
        $fileName = $contentObj->TaggedTextFileName;
    }

    $bashFile = $corpusDirSanitised . "SegmentFile.txt";
    $fp = fopen( $bashFile, "w");
    $command = LaraEnv . " " . TreeTaggerEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py segment_file " .
        $corpusDirSanitised . $nonSegfileName . " " . $corpusDirSanitised . $fileName . " " . $contentL2 . " 2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentObj->ContentID, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile);
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentObj->ContentID, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") === false)
        return true;
    else
        return false;

}

function CheckForEmbeddedFiles($contentObj)
{
    $corpusDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/";
    // Sanitise argument - MR
    $corpusDirSanitised = filter_var($corpusDir, FILTER_SANITIZE_STRING);
    $fileName = $contentObj->TaggedTextFileName;
    $bashFile = $corpusDirSanitised . "CheckForEmbeddedFiles.txt";
    $fp = fopen( $bashFile, "w");
    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py extract_css_img_and_audio_files_basic " .
        $corpusDirSanitised . $fileName . " " . $corpusDirSanitised . "embeddedFiles.json 2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentObj->ContentID, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile);
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentObj->ContentID, ContentRelatedPage, $LogID);

    $outputString = file_get_contents($corpusDirSanitised."embeddedFiles.json");
    $jsonOutput = json_decode($outputString, true); // decode the JSON into an associative array

    ContentEmbeddedItem::MakeItemsStateOld($contentObj->ContentID);

    if(count($jsonOutput['audio_files']) == 0 &&
        count($jsonOutput['css_files']) == 0 &&
        count($jsonOutput['img_files']) == 0 &&
        count($jsonOutput['script_files']) == 0)
    {
        $contentObj->HasEmbeddedAudio = 'NO';
        $contentObj->HasEmbeddedCSS = 'NO';
        $contentObj->HasEmbeddedImage = 'NO';
        $contentObj->HasEmbeddedScript = 'NO';
        $setPart = "HasEmbeddedAudio = :noEmbedded, HasEmbeddedCSS = :noEmbedded,
                    HasEmbeddedImage = :noEmbedded, HasEmbeddedScript = :noEmbedded";
        $wherePart = "ContentID = :contentID";
        $params = array(":noEmbedded" => 'NO', ":contentID" => $contentObj->ContentID);
        Content::PartialUpdate($setPart, $wherePart, $params);

        $retVal = "noEmbeddedFile";
    }
    else {
        $setPart = "";
        if (count($jsonOutput['audio_files']) != 0)
        {
            $contentObj->HasEmbeddedAudio = 'YES';
            $setPart .= " HasEmbeddedAudio = :hasEmbedded,";
            for($i = 0; $i < count($jsonOutput['audio_files']); $i++)
            {
                if(ContentEmbeddedItem::itemExists($contentObj->ContentID, EmbeddedItemsTypes["Audio"], $jsonOutput['audio_files'][$i]))
                {
                    ContentEmbeddedItem::updateItemState($contentObj->ContentID, EmbeddedItemsTypes["Audio"], $jsonOutput['audio_files'][$i]);
                }
                else
                {
                    CreateEmbeddedItem(EmbeddedItemsTypes["Audio"], $jsonOutput['audio_files'][$i], $contentObj->ContentID);
                }
            }
        }
        if(count($jsonOutput['css_files']) != 0)
        {
            $contentObj->HasEmbeddedCSS = 'YES';
            $setPart .= " HasEmbeddedCSS = :hasEmbedded,";
            for($i = 0; $i < count($jsonOutput['css_files']); $i++)
            {
                if(ContentEmbeddedItem::itemExists($contentObj->ContentID, EmbeddedItemsTypes["CSS"], $jsonOutput['css_files'][$i]))
                {
                    ContentEmbeddedItem::updateItemState($contentObj->ContentID, EmbeddedItemsTypes["CSS"], $jsonOutput['css_files'][$i]);
                }
                else
                {
                    CreateEmbeddedItem(EmbeddedItemsTypes["CSS"], $jsonOutput['css_files'][$i], $contentObj->ContentID);
                }
            }
        }
        if(count($jsonOutput['img_files']) != 0)
        {
            $contentObj->HasEmbeddedImage = 'YES';
            $setPart .= " HasEmbeddedImage = :hasEmbedded,";
            for($i = 0; $i < count($jsonOutput['img_files']); $i++)
            {
                if(ContentEmbeddedItem::itemExists($contentObj->ContentID, EmbeddedItemsTypes["Image"], $jsonOutput['img_files'][$i]))
                {
                    ContentEmbeddedItem::updateItemState($contentObj->ContentID, EmbeddedItemsTypes["Image"], $jsonOutput['img_files'][$i]);
                }
                else
                {
                    CreateEmbeddedItem(EmbeddedItemsTypes["Image"], $jsonOutput['img_files'][$i], $contentObj->ContentID);
                }
            }
        }
        if(count($jsonOutput['script_files']))
        {
            $contentObj->HasEmbeddedScript = 'YES';
            $setPart .= " HasEmbeddedScript = :hasEmbedded,";
            for($i = 0; $i < count($jsonOutput['script_files']); $i++)
            {
                if(ContentEmbeddedItem::itemExists($contentObj->ContentID, EmbeddedItemsTypes["Script"], $jsonOutput['script_files'][$i]))
                {
                    ContentEmbeddedItem::updateItemState($contentObj->ContentID, EmbeddedItemsTypes["Script"], $jsonOutput['script_files'][$i]);
                }
                else
                {
                    CreateEmbeddedItem(EmbeddedItemsTypes["Script"], $jsonOutput['script_files'][$i], $contentObj->ContentID);
                }
            }
        }
        $setPart = rtrim($setPart,',');
        $wherePart = "ContentID = :contentID";
        $params = array(":hasEmbedded" => 'YES', ":contentID" => $contentObj->ContentID);
        Content::PartialUpdate($setPart, $wherePart, $params);

        $retVal = "hasEmbedded";
    }

    $where = "ContentID = :contentID and ItemState = 'OLD'";
    $whereParam = array(":contentID" => $contentObj->ContentID);
    ContentEmbeddedItem::delete($where, $whereParam);

    if(ContentEmbeddedItem::allUploaded($contentObj->ContentID))
    {
        $retVal = "noEmbeddedFile";
    }

    return $retVal;
}

function MergeLanguageResources($externalDir, $mainDir, $mergedDir)
{
    // Sanitise arguments - MR
    $externalDirSanitised = filter_var($externalDir, FILTER_SANITIZE_STRING);
    $mainDirSanitised = filter_var($mainDir, FILTER_SANITIZE_STRING);
    $mergedDirSanitised = filter_var($mergedDir, FILTER_SANITIZE_STRING);
    $bashFile = $externalDir . "MergeResources.txt";
    $fp = fopen( $bashFile, "w");
    $configFile = ImportContentsDirectory . "import_local_config.json";
    $configFileSanitised = filter_var($configFile, FILTER_SANITIZE_STRING);

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py merge_language_resources " .
        $mainDirSanitised . " " . $externalDirSanitised . " " . $mergedDirSanitised . " " . $configFileSanitised . " 2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, "111111", ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, "111111", ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") === false)
        return true;
    else
        return false;
}

function CreateResourceFiles($corpusDir, $destDir, $contentID)
{
    // Sanitise arguments - MR
    $corpusDirSanitised = filter_var($corpusDir, FILTER_SANITIZE_STRING);
    $destDirSanitised = filter_var($destDir, FILTER_SANITIZE_STRING);
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);
    $createRsrcDest = ExtraModules::CreateDir($destDirSanitised);
    $bashFile = $corpusDirSanitised . "FirstPhaseCommand.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py resources_and_copy " .
        $corpusDirSanitised . "local_config.json " . $destDirSanitised . " 2>&1"; ;
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentIDSanitised, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") !== false)
        return "Failed";
    else if(strpos($output, "Warning") !== false)
        return "SucceedWithWarning";
    else
        return "Succeed";
}

// Begin Picturebook functionality added by MR
//   python3 get_and_store_selector_tool_data <ConfigFile>

function DownloadFromSelectorTool($corpusDir, $contentID)
{
    // Sanitise arguments - MR
    $corpusDirSanitised = filter_var($corpusDir, FILTER_SANITIZE_STRING);
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);
    $bashFile = $corpusDirSanitised . "SelectorToolDownloadCommand.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py get_and_store_selector_tool_data " .
        $corpusDirSanitised . "local_config.json " . " 2>&1"; 
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentIDSanitised, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") !== false)
        return "Failed";
    else if(strpos($output, "Warning") !== false)
        return "SucceedWithWarning";
    else
        return "Succeed";
}

//   python3 copy_tmp_picturebook_data_into_place <ConfigFile> <TmpWordLocationsFile> <TmpWordLocationsZipfile> <Dir>

function InstallAndUploadToSelectorTool($corpusDir, $resourcesDir, $selectorToolWebDir, $contentID)
{
    // Sanitise arguments - MR
    $corpusDirSanitised = filter_var($corpusDir, FILTER_SANITIZE_STRING);
    $resourcesDirSanitised = filter_var($resourcesDir, FILTER_SANITIZE_STRING);
    $selectorToolWebDirSanitised = filter_var($selectorToolWebDir, FILTER_SANITIZE_STRING);
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);

    $bashFile = $corpusDirSanitised . "SelectorToolUploadCommand.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py copy_tmp_picturebook_data_into_place " .
        $corpusDirSanitised . "local_config.json " .
	$resourcesDirSanitised . "word_locations.json " . $resourcesDirSanitised . "word_locations_zipfile.zip " . $selectorToolWebDirSanitised . " 2>&1"; 
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentIDSanitised, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") !== false)
        return "Failed";
    else if(strpos($output, "Warning") !== false)
        return "SucceedWithWarning";
    else
        return "Succeed";
}
// End Picturebook functionality added by MR

function CreateMultiWordFile($corpusDir, $destDir, $contentID)
{
    // Sanitise arguments - MR
    $corpusDirSanitised = filter_var($corpusDir, FILTER_SANITIZE_STRING);
    $destDirSanitised = filter_var($destDir, FILTER_SANITIZE_STRING);
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);

    $createRsrcDest = ExtraModules::CreateDir($destDirSanitised);
    $bashFile = $corpusDir . "MultiWordCommand.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py mwe_annotate_and_copy " .
        $corpusDirSanitised . "local_config.json " . $destDirSanitised . "mwe_annotations.json 2>&1";;
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentIDSanitised, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") !== false)
        return false;
    else
        return true;
}

function DeleteLDTTask($tokenType, $accessToken, $TaskID)
{
    // Sanitise arguments - MR
    $TaskIDSanitised = filter_var($TaskID, FILTER_SANITIZE_STRING);
    
    $url = 'https://regulus.unige.ch/litedevtools/server/api/lara/deleteRecordingTask/' . $TaskIDSanitised;
    $header = [
        "Authorization: " . $tokenType . " " . $accessToken
    ];

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "DELETE");
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible;)");
    curl_setopt($ch, CURLOPT_HTTPHEADER,$header);
    curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
    curl_setopt($ch, CURLOPT_FORBID_REUSE, 1);
    curl_setopt($ch, CURLOPT_TIMEOUT, 100);

    $result = curl_exec($ch);
    curl_close($ch);
    if ($result === FALSE) {
        //echo "Error sending" . $fname .  " " . curl_error($ch);
        return false;
    }else{
        return true;
    }
}

function CreateLDTTask($tokenType, $accessToken, $fileDir, $taskName, $ldtUserID, $VideoAnnotations)
{
    // Sanitise arguments - MR
    $fileDirSanitised = filter_var($fileDir, FILTER_SANITIZE_STRING);

    $url = 'https://regulus.unige.ch/litedevtools/server/api/lara/postRecordingTask';
    $fname = $fileDirSanitised;
    $cfile = new CURLFile(realpath($fname));

    $post = array (
        'file' => $cfile,
        'taskName' => $taskName
    );

    if($VideoAnnotations == "YES")
        $post["taskType"] = 'video';

    if($ldtUserID == -1)
    {
        $post["anonymousTask"] = 'true';
    }
    else
    {
        $post["anonymousTask"] = 'false';
        $post["assignedUserId"] = $ldtUserID;
    }

    $header = [
        "Content-Type: multipart/form-data",
        "Authorization: " . $tokenType . " " . $accessToken
    ];

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible;)");
    curl_setopt($ch, CURLOPT_HTTPHEADER,$header);
    curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
    curl_setopt($ch, CURLOPT_FORBID_REUSE, 1);
    curl_setopt($ch, CURLOPT_TIMEOUT, 100);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $post);

    $result = curl_exec($ch);
    if ($result === FALSE) {
        curl_close($ch);
        return "-1";
    }else{
        $RecTaskRes = json_decode($result, true);
        $ldtTaskID = $RecTaskRes["id"];
        curl_close($ch);
        return $ldtTaskID;
    }
}

function InstallHumanAudio($contentObj, $tokenType, $accessToken)
{

    $headerInfo = $tokenType . " " . $accessToken ;

    $dirName = $contentObj->ContentID . "_" . str_replace(" ","_",$contentObj->ContentName);
    $audioDir = LaraContentDir . $dirName . "/" . SubDirNames["audio"] . "/";
    $corpusDir = LaraContentDir . $dirName . "/" . SubDirNames["corpus"] . "/";
    $resourcesDir = ContentTmpDirectory . $dirName . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $configFile = $corpusDir . "local_config.json";


    if($contentObj->WordsAudioType == "human" && !empty($contentObj->WordLdtTaskID))
    {
        LastLDTTaskStatus($contentObj, $headerInfo, "word");
        if(ContentRecordingTask::RecordingsHasChanged($contentObj->ContentID, "word"))
            if(!(DownloadFromLDT($contentObj, $audioDir, $headerInfo, "word") &&
                InstallWordAudio($resourcesDir, $audioDir, $configFile, $contentObj)))
                    return false;
    }


    if($contentObj->SegmentsAudioType == 'human' && !empty($contentObj->SegmentLdtTaskID))
    {
        LastLDTTaskStatus($contentObj, $headerInfo, "segment");
        if(ContentRecordingTask::RecordingsHasChanged($contentObj->ContentID, "segment"))
            if(!(DownloadFromLDT($contentObj, $audioDir, $headerInfo, "segment") &&
                InstallSegmentAudio($resourcesDir, $audioDir, $configFile, $contentObj)))
                        return false;
    }

    return true;
}

function DownloadFromLDT($contentObj, $audioDir, $headerInfo, $type)
{
    if($contentObj->LdtDeactivateStatus == 'YES')
        return true;

    if($type == "word")
    {
        $url = 'https://regulus.unige.ch/litedevtools/server/api/lara/downloadRecordedFiles/' . $contentObj->WordLdtTaskID;
        $FileToSave = $audioDir . 'ldtWords.zip';
    }
    elseif ($type == "segment")
    {
        $url = 'https://regulus.unige.ch/litedevtools/server/api/lara/downloadRecordedFiles/' . $contentObj->SegmentLdtTaskID;
        $FileToSave = $audioDir . 'ldtSegments.zip';
    }
    // Sanitise arguments - MR
    $urlSanitised = filter_var($url, FILTER_SANITIZE_STRING);
    $FileToSaveSanitised = filter_var($FileToSave, FILTER_SANITIZE_STRING);

    $header = [
        "Authorization: " . $headerInfo
    ];

    $result = FALSE;

    if ($fh = fopen($FileToSaveSanitised, 'wb+')) {

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $urlSanitised);
        curl_setopt($ch, CURLOPT_USERAGENT, "MozillaXYZ/1.0");
        curl_setopt($ch, CURLOPT_TIMEOUT, 300);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HEADER, 0);
        curl_setopt($ch, CURLOPT_HTTPHEADER,$header);
        // tell it you want response written to file
        curl_setopt($ch, CURLOPT_FILE, $fh);

        $result = curl_exec($ch);
        curl_close($ch);
        fclose($fh);
    }

    if ($result === FALSE)
        return false;
    else
        return true;
}

function LastLDTTaskStatus($contentObj, $headerInfo, $type)
{
    if($type == "word")
    {
        $url = 'https://regulus.unige.ch/litedevtools/server/api/lara/taskStatus/' . $contentObj->WordLdtTaskID;
    }
    elseif ($type == "segment")
    {
        $url = 'https://regulus.unige.ch/litedevtools/server/api/lara/taskStatus/' . $contentObj->SegmentLdtTaskID;
    }

    $header = [
        "Authorization: " . $headerInfo
    ];

    //$result = FALSE;

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_USERAGENT, "MozillaXYZ/1.0");
    curl_setopt($ch, CURLOPT_TIMEOUT, 300);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_setopt($ch, CURLOPT_HTTPHEADER,$header);

    $result = curl_exec($ch);
    curl_close($ch);

    $taskObj = json_decode($result, true);

    //no task was registered
    if(!empty($taskObj["message"]))
        return false;

    LogLDTTaskTrace($taskObj, $contentObj->ContentID, $type);

    return true;
}

function InstallWordAudio($resourcesDir, $audioDir, $configFile, $contentObj)
{
    // Sanitise arguments - MR
    $audioDirSanitised = filter_var($audioDir, FILTER_SANITIZE_STRING);
    $configFileSanitised = filter_var($configFile, FILTER_SANITIZE_STRING);
    
    $bashFile = $audioDir . "InstallWords.txt";
    $wordRecFile = $resourcesDir . "ldt_word_recording_full.json";
    $badMetadataFile = $resourcesDir . "BadRecordedWords.json";

    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py install_ldt_zipfile " .
        $audioDirSanitised . "ldtWords.zip " . $wordRecFile . " words " .  $configFileSanitised . " " . $badMetadataFile . " 2>&1" ;
    fwrite($fp, $command);

    if(file_exists( $audioDir . "ldtWords.zip") && !empty($contentObj->WordLdtTaskID) )
    {
        $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentObj->ContentID, ContentRelatedPage);
        $output = shell_exec('bash < '  . $bashFile );
        ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentObj->ContentID, ContentRelatedPage, $LogID);
        if(strpos($output, "*** Error") === false)
            return true;
        return false;
    }
    return true;
}

function InstallSegmentAudio($resourcesDir, $audioDir, $configFile, $contentObj)
{
    // Sanitise arguments - MR
    $audioDirSanitised = filter_var($audioDir, FILTER_SANITIZE_STRING);
    $resourcesDirSanitised = filter_var($resourcesDir, FILTER_SANITIZE_STRING);
    $configFileSanitised = filter_var($configFile, FILTER_SANITIZE_STRING);
    
    $bashFile = $audioDir . "InstallSegments.txt";
    $segRecFile = $resourcesDir . "ldt_segment_recording_full.json";
    $badMetadataFile = $resourcesDir . "BadRecordedSegments.json";

    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py install_ldt_zipfile " .
        $audioDirSanitised . "ldtSegments.zip " . $segRecFile . " segments " . $configFileSanitised . " " . $badMetadataFile . " 2>&1" ;
    fwrite($fp, $command);

    if(file_exists( $audioDir . "ldtSegments.zip") && !empty($contentObj->SegmentLdtTaskID))
    {
        $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentObj->ContentID, ContentRelatedPage);
        $output = shell_exec('bash < '  . $bashFile );
        ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentObj->ContentID, ContentRelatedPage, $LogID);
        if(strpos($output, "*** Error") === false)
            return true;
        return false;
    }
    return true;
}

function InstallNonLdtAudio($audioDir, $configFile, $contentID)
{
    // Sanitise arguments - MR
    $audioDirSanitised = filter_var($audioDir, FILTER_SANITIZE_STRING);
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);
    $configFileSanitised = filter_var($configFile, FILTER_SANITIZE_STRING);
    
    $bashFile = $audioDirSanitised . "InstallNonLDTAudio.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py install_non_ldt_audio_zipfile  " .
        $audioDirSanitised . "audio.zip " .  $configFileSanitised . " 2>&1" ;
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentIDSanitised, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") === false)
    {
        return true;
    }
    else
    {
        return false;
    }
}

function CreatePageFiles($corpusDir, $contentID)
{
    // Sanitise arguments - MR
    $corpusDirSanitised = filter_var($corpusDir, FILTER_SANITIZE_STRING);
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);
    
    $bashFile = $corpusDirSanitised . "CreatePagesCommand.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py word_pages  " .
        $corpusDirSanitised . "local_config.json  2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentIDSanitised, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") === false)
        return true;
    else
        return false;
}

function CreatePageFilesForSocialNetwork($corpusDir, $contentID)
{
    // Sanitise arguments - MR
    $corpusDirSanitised = filter_var($corpusDir, FILTER_SANITIZE_STRING);
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);
    
    $bashFile = $corpusDirSanitised . "CreatePagesForSocialNetworkCommand.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py word_pages  " .
        $corpusDirSanitised . "sn_config.json  2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentIDSanitised, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") === false)
        return true;
    else
        return false;
}

function CopyToWeb($CompileDir, $srcDirName, $destDirName, $contentID)
{
    // Sanitise arguments - MR
    $CompileDirSanitised = filter_var($CompileDir, FILTER_SANITIZE_STRING);
    $srcDirNameSanitised = filter_var($srcDirName, FILTER_SANITIZE_STRING);
    $destDirNameSanitised = filter_var($destDirName, FILTER_SANITIZE_STRING);
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);
    
    $bashFile = $CompileDirSanitised . "CopyCommand.txt";
    $fp = fopen($bashFile, "w");

    if( is_dir(CallectorDir . $destDirNameSanitised) === false )
    {
        mkdir(CallectorDir . $destDirNameSanitised);
    }
    $command = "scp -r " . $CompileDirSanitised . $srcDirNameSanitised . "/* " . CallectorDir . $destDirNameSanitised . "/  2>&1";
    fwrite($fp, $command);
    fclose($fp);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );

    if ($output == '')
    {
        return true;
    }
    else
    {
        ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentID, ContentRelatedPage, $LogID);
        return false;
    }
}

function CopyToSnDir($CompileDir, $srcDirName, $destDirName, $contentID)
{
    // Sanitise arguments - MR
    $CompileDirSanitised = filter_var($CompileDir, FILTER_SANITIZE_STRING);
    $srcDirNameSanitised = filter_var($srcDirName, FILTER_SANITIZE_STRING);
    $destDirNameSanitised = filter_var($destDirName, FILTER_SANITIZE_STRING);
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);

    $bashFile = $CompileDirSanitised . "CopyToSnCommand.txt";
    $fp = fopen($bashFile, "w");

    if( is_dir($destDirName) === false )
    {
        mkdir($destDirName);
    }
    $command = "scp -r " . $CompileDirSanitised . $srcDirNameSanitised . "/* " .  $destDirNameSanitised . "/  2>&1";
    fwrite($fp, $command);
    fclose($fp);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );

    if ($output == '')
    {
        return true;
    }
    else
    {
        ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentIDSanitised, ContentRelatedPage, $LogID);
        return false;
    }
}

function CreateEmbeddedItem($ItemType, $ItemName, $ContentID)
{
    $EmbeddedItem = new ContentEmbeddedItem();

    $EmbeddedItem->ItemType = $ItemType;
    $EmbeddedItem->ItemName = $ItemName;
    $EmbeddedItem->IsUploaded = 'NO';
    $EmbeddedItem->ContentID = $ContentID;
    $EmbeddedItem->ItemState = "NEW";

    $EmbeddedItem->insert();

    return true;
}

function DeleteContent()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $_GET["contentID"]);
    $info = Content::SearchContent($where, $whereParam);
    $contentObj = FillItems($info[0]);

    $resultArray[0]["id"] = $contentObj->ContentID;

    $whereParam = array(":pID" => $contentObj->ContentID);
    if(Content::hasTakenChildren($whereParam))
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "HasTakenChildren");
        ExtraModules::KillProcess($resultArray, "HasTakenChildren");
    }

    $where = " contentID = :contentID";
    $whereParam = array(":contentID" => $contentObj->ContentID);
    ContentEmbeddedItem::delete($where, $whereParam);
    //todo adding new calls for deleting content elements

    $setPart = "IsDeleted = 'YES'";
    Content::PartialUpdate($setPart, $where, $whereParam);
    if(!empty($contentObj->DirName))
    {
        $dirName = LaraContentDir . $contentObj->DirName;
        ExtraModules::RemoveDir($dirName);
    }
    if(!empty($contentObj->WebAddress))
    {
        $vocabDirName = CallectorDir .  $contentObj->DirName . "vocabpages";
        ExtraModules::RemoveDir($vocabDirName);
    }

    $childrenRows = Content::ContentChildrenList($contentObj->ContentID);
    for ($i = 0; $i < count($childrenRows); $i++)
        DeleteSubContent($childrenRows[$i]["ContentID"]);

    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "SuccessfulDeleteContent");
    ExtraModules::KillProcess($resultArray, "SuccessfulDeleteContent");
}

function DeleteSubContent($contentID)
{
    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $contentID);
    $info = Content::SearchContent($where, $whereParam);
    $contentObj = FillItems($info[0]);

    ContentEmbeddedItem::delete($where, $whereParam);
    //todo adding new calls for deleting content elements

    $setPart = "IsDeleted = 'YES'";
    Content::PartialUpdate($setPart, $where, $whereParam);

    if(!empty($contentObj->DirName))
    {
        $dirName = LaraContentDir . $contentObj->DirName;
        ExtraModules::RemoveDir($dirName);
    }

    if(!empty($contentObj->WebAddress))
    {
        $vocabDirName = CallectorDir .  $contentObj->DirName . "vocabpages";
        ExtraModules::RemoveDir($vocabDirName);
    }
    return true;
}

function PublishContent()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $_GET["contentID"]);
    $info = Content::SearchContent($where, $whereParam);
    $contentObj = FillItems($info[0]);

    $resultArray[0]["id"] = $contentObj->ContentID;

    $L2Name = Language::getLanguageName($contentObj->L2ID);

    if(AddMetaData($contentObj, $L2Name))
    {
        $CompileDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["compiled"] . "/";
        $dirName = $contentObj->DirName;

	// Sanitise arguments - MR
	$CompileDirSanitised = filter_var($CompileDir, FILTER_SANITIZE_STRING);
	$dirNameSanitised = filter_var($dirName, FILTER_SANITIZE_STRING);
	$L2NameSanitised = filter_var($L2Name, FILTER_SANITIZE_STRING);

        $bashFile = $CompileDir . "CopyResourceCommand.txt";
        $fp = fopen($bashFile, "w");

        //Copy the content package from LaraData to LaraResource
        if (is_dir(DistributedDir . $dirName) === false) {
            mkdir(DistributedDir . $dirName);
        }
        $command = "scp -r " . LaraContentDir . $dirNameSanitised . "/* " . DistributedDir . $dirNameSanitised . "/  2>&1";
        fwrite($fp, $command);
        fclose($fp);
        $output = shell_exec('bash < ' . $bashFile);

        if ($output != '')
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "FailedToCopyResource");
            ExtraModules::KillProcess($resultArray, "FailedToCopyResource");
        }

        //Copy the language package from LaraData to LaraResource
        $bashFile = $CompileDir . "CopyLangResourceCommand.txt";
        $fp = fopen($bashFile, "w");

        if (is_dir(DistributedDir . $L2NameSanitised ) === false)
            mkdir(DistributedDir . $L2NameSanitised );


        $command = "scp -r " . LaraContentDir . $L2NameSanitised . "/* " .DistributedDir . $L2NameSanitised . "/  2>&1";
        fwrite($fp, $command);
        fclose($fp);
        $output = shell_exec('bash < ' . $bashFile);

        $langCopyResFile = $CompileDir . "CopyLangResourceRes.txt";
        $fp = fopen($langCopyResFile, "w");
        fwrite($fp, $output);
        fclose($fp);

        if ($output != '')
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "FailedToCopyLangResource");
            ExtraModules::KillProcess($resultArray, "FailedToCopyLangResource");
        }

        $intendedWebAddress = DistributedWebRoot . $L2Name ;
        $LangResRegCheck = DistributedResource::isLanguageResourceRegistered($intendedWebAddress);
        if( $LangResRegCheck == "-1")
        {
            $lRscObj = new DistributedResource();
            $lRscObj->ResourceName =  $L2Name;
            $lRscObj->WebAddress = DistributedWebRoot . $L2Name ;
            $lRscObj->ResourceType = "Language";
            $lRscObj->UserID = $contentObj->CreatorID;
            $lRscObj->L2ID = $contentObj->L2ID;
            $lRscObj->insert();
            $lRscObj->ResourceID = DistributedResource::lastID();
            $parentID = $lRscObj->ResourceID;
        }
        else
        {
            $parentID = $LangResRegCheck;
        }

        $rscObj = new DistributedResource();
        $rscObj->ResourceName = str_replace(" ","_",$contentObj->ContentName);
        $rscObj->WebAddress = DistributedWebRoot . $dirName ;
        $rscObj->ResourceType = "Content";
        $rscObj->UserID =  $contentObj->CreatorID;
        $rscObj->L2ID =  $contentObj->L2ID;
        $rscObj->ParentID = $parentID;

        if(empty($contentObj->DistributedResourceID))
        {
            $rscObj->insert();
            $rscObj->ResourceID = DistributedResource::lastID();

            $setPart = "DistributedResourceID = :drID";
            $wherePart = "ContentID = :contentID";
            $params = array(":drID" => $rscObj->ResourceID, ":contentID" => $contentObj->ContentID);
            Content::PartialUpdate($setPart, $wherePart, $params);
        }
        else
        {
            $rscObj->ResourceID = $contentObj->DistributedResourceID;
            $rscObj->update();

            //PageNamesShouldBeExtractedAgain
            $where = "ResourceID = :rID";
            $whereParam = array(":rID" => $contentObj->DistributedResourceID);
            DistributedResourcePage::delete($where, $whereParam);
        }

        if (!ExtractResourcePageNames($CompileDir, $rscObj, $contentObj->ContentID, $contentObj->DirName))
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "FailedToExtractPageNamesPublish");
            ExtraModules::KillProcess($resultArray, "FailedToExtractPageNamesPublish");
        }

        $resultArray[0]["resultMsg"] = "SuccessfulPublish";
    }
    else
    {
        $resultArray[0]["resultMsg"] = "FailedPublish";
    }
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function AddMetaData($contentObj, $L2Name)
{
    $corpusDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/";
    $resourceDir = LaraContentDir . $contentObj->DirName ;

    // Sanitise arguments - MR
    $corpusDirSanitised = filter_var($corpusDir, FILTER_SANITIZE_STRING);
    $resourceDirSanitised = filter_var($resourceDir, FILTER_SANITIZE_STRING);
    
    $bashFile = $corpusDirSanitised . "AddMetadataCmnd.txt";
    $fp = fopen( $bashFile, "w");
    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py add_metadata " .
        $resourceDirSanitised  . " corpus 2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentObj->ContentID, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile);
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentObj->ContentID, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") !== false)
    {
        return false;
    }
    else
    {
        $corpusDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/";
        $resourceDir = LaraContentDir . $L2Name ;

	// Sanitise arguments - MR
    	$corpusDirSanitised = filter_var($corpusDir, FILTER_SANITIZE_STRING);
    	$resourceDirSanitised = filter_var($resourceDir, FILTER_SANITIZE_STRING);
	
        ExtraModules::CreateDir($resourceDir);
        $bashFile = $corpusDirSanitised . "AddMetadataCmndForLangRep.txt";
        $fp = fopen( $bashFile, "w");
        $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py add_metadata " .
            $resourceDirSanitised  . " language 2>&1";
        fwrite($fp, $command);

        $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentObj->ContentID, ContentRelatedPage);
        $output = shell_exec('bash < '  . $bashFile);
        ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentObj->ContentID, ContentRelatedPage, $LogID);

        if(strpos($output, "*** Error") !== false)
            return false;
        else
            return true;
    }
}

function ExtractResourcePageNames($compileDir, $rscObj, $contentID, $DirName)
{
    // Sanitise arguments - MR
    $compileDirSanitised = filter_var($compileDir, FILTER_SANITIZE_STRING);
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);
    
    //1- create resource file
    $resourceFile = $compileDirSanitised . "resource.json";
    $fp = fopen($resourceFile, "w");
    $fileContent = '{"' . $rscObj->ResourceID . '_' . $rscObj->ResourceName . '" : ["' .
                $rscObj->WebAddress . '",""]}';
    fwrite($fp, $fileContent);
    fclose($fp);

    //2- create config file
    $configFile = $compileDirSanitised . "config.json";
    $fp = fopen($configFile, "w");
    $fileContent = '{"id": "abc", "reading_history": [], 
        "working_tmp_directory" : "' . WorkingTmpDirectory . '", 
        "lara_tmp_directory" : "' . ContentTmpDirectory . $DirName . '/' . SubDirNamesContentTmp["laraTmpDirectory"] . '", 
        "compiled_directory" : "' . ContentTmpDirectory . $DirName . '/' . SubDirNamesContentTmp["compiled"] . '",
        "resource_file" : "' . $resourceFile .'"}';
    fwrite($fp, $fileContent);
    fclose($fp);

    //3- create and run bash command file
    $pageNamesFile = $compileDirSanitised . "pageNames.json";
    $bashFile = $compileDirSanitised . "PageNamesForResource.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py " .
                "get_page_names_for_resource  " . $rscObj->ResourceID . '_' . $rscObj->ResourceName .
                " " .  $configFile."  " . $pageNamesFile . " 2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentID, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentIDSanitised, ContentRelatedPage, $LogID);

    if($output == false || strpos($output, "*** Error") !== false )
        return false;

    //4- read json file
    $outputString = file_get_contents($pageNamesFile);
    $PagesNamesArray = json_decode($outputString, true); // decode the JSON into an associative array

    //6- save in DistributedResourcePages table
    for($i = 0; $i < count($PagesNamesArray); $i++)
    {
        $resourcePage = new DistributedResourcePage();
        $resourcePage->ResourceID = $rscObj->ResourceID;
        $resourcePage->PageNumber = $PagesNamesArray[$i]['page_number'];
        $resourcePage->PageName = $PagesNamesArray[$i]['base_file'];
        $resourcePage->insert();
    }

    return true;
}

function ManageEmbeddedItems($embeddedFile, $zipFileName, $dest, $type, $killMsg, $contentObj)
{
    if($type == "Audio")
        $SrcDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["audio"] . "/"  ;
    else
        $SrcDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["laraTmpDirectory"] . "/"  ;
    $DestDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames[$dest] . "/"  ;

    $file = $_FILES[$embeddedFile];
    $path = $file['tmp_name'];
    $zip = new ZipArchive;

    ExtraModules::UploadFile($zipFileName,$SrcDir, $file);
    if ($zip->open($path) === true) {
        for ($i = 0; $i < $zip->numFiles; $i++) {
            $filename = $zip->getNameIndex($i);
            $fileinfo = pathinfo($filename);
            if($type != "Audio")
                copy("zip://" . $path . "#" . $filename, $DestDir . $fileinfo['basename']);
            if (ContentEmbeddedItem::itemExists($contentObj->ContentID, EmbeddedItemsTypes[$type],  $fileinfo['basename'])) {
                ContentEmbeddedItem::updateUploadStatus($contentObj->ContentID,
                    EmbeddedItemsTypes[$type],  $fileinfo['basename']);
            }
        }
        $zip->close();
        return;
    }
    else{
        $resultArray[0]["id"] = $contentObj->ContentID;
        $resultArray[0]["resultMsg"] = $killMsg;
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
}

// MR 20220717: make args 2, 3, 4 optional as well, since they're only needed for crowdsourcing
function ImportLaraContent($forDistributing = false, $parentID = false, $fileName = false, $fileDirectory = false)
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = -1;

    $contentObj = new Content();
    if($forDistributing)
        $contentObj->ParentID = $parentID;
    $contentObj->CreatorID = $_SESSION[SessionIndex['UserID']];
    $contentObj->insert();
    $contentObj->ContentID = $contentObj->lastID();

    $iContentObj = new ImportContent();

    if($forDistributing)
        $iContentObj->ImportFileName = $fileName;
    else
        $iContentObj->ImportFileName = $_REQUEST["fileName"];

    $iContentObj->CreatorID = $_SESSION[SessionIndex['UserID']];
    $iContentObj->ContentID = $contentObj->ContentID;
    $iContentObj->insert();
    $iContentObj->ImportContentID = $iContentObj->lastID();
    $resultArray[0]["id"] = $iContentObj->ImportContentID;

    //creating the folder structure for the saved content
    $tmpDirName =   "Imported_" . $iContentObj->ContentID;

    $createDIRRes = ExtraModules::CreateDir(LaraContentDir . $tmpDirName);
    //check failure or success in creating directories
    if (in_array($createDIRRes, array("DIRExists","CreateDIRFailed")))
    {
        ExtraModules::UserActivityLog(ImportRelatedPage, $resultArray, $createDIRRes . "ImportLaraContent");
        ExtraModules::KillProcess($resultArray, $createDIRRes . "ImportLaraContent");
    }

    if($forDistributing)
    {
        $iContentDir = LaraContentDir . $tmpDirName . "/" . $fileName;
        $src = $fileDirectory . $fileName;
    }
    else
    {
        $iContentDir = LaraContentDir . $tmpDirName . "/" . $_REQUEST["fileName"];
        $src = ContentTmpDirectory . $_REQUEST["fileName"];
    }
    //upload the raw file in corpus directory
    if(copy($src, $iContentDir))
    {
        if(ImportZipfile($iContentObj, $tmpDirName))
        {
            $logInRes = ExtraModules::LogIntoLDT();
            $logInRes = json_decode($logInRes, true);

            if($logInRes["access_token"] == "LDTAuthenticationFailed")
            {
                if($forDistributing)
                    return "LoginToLdtFailed";
                ExtraModules::UserActivityLog(ImportRelatedPage, $resultArray, "LoginToLdtFailed");
                ExtraModules::KillProcess($resultArray, "LoginToLdtFailed");
            }

            $tokenType = $logInRes["token_type"];
            $accessToken = $logInRes["access_token"];
            $headerInfo = $tokenType . " " . $accessToken ;

            if(FulfillContentObj($contentObj, $tmpDirName, $headerInfo))
            {
                $oldName = LaraContentDir . $tmpDirName;
                $newName = LaraContentDir . $contentObj->DirName;
                rename ($oldName , $newName);

                $where = " ContentID = :contentID";
                $whereParam = array(":contentID" => $contentObj->ContentID);
                $info = Content::SearchContent($where, $whereParam);
                $fullContentObj = FillItems($info[0]);
                CreateConfigFile($newName . "/" . SubDirNames["corpus"] . "/", $fullContentObj, $headerInfo, false);

                $tmpDirAddress = ContentTmpDirectory . $contentObj->DirName;
                $createTmpDIRRes = ExtraModules::CreateDir($tmpDirAddress, SubDirNamesContentTmp);
                if (in_array($createTmpDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
                {
                    if($forDistributing)
                        return $createTmpDIRRes . "ImportLaraContent";
                    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, $createTmpDIRRes . "ImportLaraContent");
                    ExtraModules::KillProcess($resultArray, $createTmpDIRRes . "ImportLaraContent");
                }

                rename($newName . "/corpus/mwe_annotations.json", $tmpDirAddress . "/resourcesDir/mwe_annotations.json");

                if($forDistributing)
                    return "SuccessfullyImported";
                ExtraModules::UserActivityLog(ImportRelatedPage, $resultArray, "SuccessfullyImported");
                ExtraModules::KillProcess($resultArray, "SuccessfullyImported");
            }
            else
            {
                if($forDistributing)
                    return "FulfillingFailed";
                ExtraModules::UserActivityLog(ImportRelatedPage, $resultArray, "FulfillingFailed");
                ExtraModules::KillProcess($resultArray, "FulfillingFailed");
            }
        }
        else
        {
            if($forDistributing)
                return "ImportZipFileFailed";
            ExtraModules::UserActivityLog(ImportRelatedPage, $resultArray, "ImportZipFileFailed");
            ExtraModules::KillProcess($resultArray, "ImportZipFileFailed");
        }
    }
    else {
        if($forDistributing)
            return "UploadFileFailedImportLaraContent";
        ExtraModules::UserActivityLog(ImportRelatedPage, $resultArray, "UploadFileFailedImportLaraContent");
        ExtraModules::KillProcess($resultArray, "UploadFileFailedImportLaraContent");
    }
}

function ImportLaraResource()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = -1;

    $languageID = $_REQUEST["languageID"];
    $zipFileName = $_REQUEST["fileName"];
    $rootDestDir = ExternalResourceDirectory .  "lang" . $languageID ."/" ;
    $res = ExtraModules::CreateDir($rootDestDir);
    if (in_array($res, array("DIRExists","DIRCreated"))) {
        $destDir = $rootDestDir . date("Ymd_His") . "/";
        $resDest = ExtraModules::CreateDir($destDir);
        if ($resDest != "CreateDIRFailed") {
            $mergedDir = $rootDestDir . "merged/";
            $resMerged = ExtraModules::CreateDir($mergedDir);
            if ($resMerged != "CreateDIRFailed") {
                if (UnzipIt(ContentTmpDirectory . $zipFileName, $destDir) == false) {
                    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "FailedToExtractExtResFile");
                    ExtraModules::KillProcess($resultArray, "FailedToExtractExtResFile");
                }
                else {
                    //uploaded folder for external resource
                    $dirs = glob($destDir . '*' , GLOB_ONLYDIR);
                    $externalDir = $dirs[0];
                    //main language resource
                    $L2Name = Language::getLanguageName($languageID);
                    $mainDir = LaraContentDir . $L2Name;

                    if (!file_exists($mainDir) || !is_dir($mainDir))
                    {
                        rename($externalDir, $mainDir);
                    } else {
                        $mergeRes = MergeLanguageResources($externalDir, $mainDir, $mergedDir);
                        if($mergeRes == true)
                        {
                            ExtraModules::RemoveDir($mainDir);
                            rename($mergedDir, $mainDir);
                        }
                        else
                        {
                            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "MergeLanguageResourcesFailed");
                            ExtraModules::KillProcess($resultArray, "MergeLanguageResourcesFailed");
                        }
                    }
                }
            }
            else
            {
                ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "CreateDIRFailedExtMerg");
                ExtraModules::KillProcess($resultArray, "CreateDIRFailedExtMerg");
            }
        }
        else
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "CreateDIRFailedExtTmp");
            ExtraModules::KillProcess($resultArray, "CreateDIRFailedExtTmp");
        }
    }
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "MergeLanguageResourcesSucceed");
    ExtraModules::KillProcess($resultArray, "MergeLanguageResourcesSucceed");
}

function ImportZipFile($iContentObj, $tmpDirName)
{
    // Sanitise argument - MR
    $tmpDirNameSanitised = filter_var($tmpDirName, FILTER_SANITIZE_STRING);
    
    $zipFile = LaraContentDir . $tmpDirNameSanitised . "/" . $iContentObj->ImportFileName;
    $corpusDir = LaraContentDir . $tmpDirNameSanitised;
    $languageRootDir = LaraContentDir;
    $configFile = ImportContentsDirectory . "import_local_config.json";

    $bashFile = ImportContentsDirectory . $iContentObj->ImportContentID . "_ImportZipFile.txt";
    $fp = fopen( $bashFile, "w");
    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py import_zipfile "
        . $zipFile . " " .  $corpusDir . " " . $languageRootDir . " " . $configFile . " 2>&1";
    fwrite($fp, $command);
    fclose($fp);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $iContentObj->ImportContentID, ImportRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $iContentObj->ImportContentID, ImportRelatedPage, $LogID);
    if(strpos($output, "*** Error") === false)
        return true;
    else
        return false;
}

function FulfillContentObj($contentObj, $tmpDirName, $headerInfo)
{
    $tmpDir = LaraContentDir . $tmpDirName . "/" . SubDirNames["corpus"] . "/";
    $configFile = $tmpDir . "local_config.json";
    $configFileContent = file_get_contents($configFile);
    $contentObjValue = get_object_vars(json_decode($configFileContent));

    $ContentConfigIndexes = array("id",
        "max_examples_per_word_page",
        "translation_mouseover",
        "audio_mouseover",
        "segment_translation_mouseover",
        "segment_translation_character",
        "audio_segments",
        "play_parts",
        "segment_audio_keep_duplicates",
        "allow_table_of_contents",
        "keep_comments",
        "comments_by_default",
        "linguistics_article_comments",
        "coloured_words",
        "font",
        "frequency_lists_in_main_text_page",
        "add_postags_to_lemma",
        "css_file",
        "script_file",
        "pinyin_file",
        "tts_word_substitution_spreadsheet",
        "word_translations_on",
        "mwe_words_in_colour",
        "video_annotations",
        "video_annotations_from_translation",
        "segment_translation_as_popup",
        "translated_words_in_colour"
        );

    $ContentIndexes = array("ContentName",
        "MaxExamplesPerWordPage",
        "WordTranslationMouseOver",//yes-no
        "AudioMouseOver",//yes-no
        "SegmentTranslationMouseOver",//yes-no
        "SegmentTranslationCharacter",
        "AudioSegments",//yes-no
        "PlayParts",
        "SegmentAudioKeepDuplicates",//yes-no
        "TableOfContents",//yes-no
        "KeepComments",//yes-no
        "CommentsByDefault",//yes-no
        "LinguisticsArticleComments",//yes-no
        "ColouredWords",//yes-no
        "Font",//'serif', 'sans-serif', 'monospace'
        "FrequencyListsInMainText",//yes-no
        "AddPostagsToLemma",//yes-no
        "ContentCssFileName",
        "ContentJsFileName",
        "PinyinFileName",
        "TtsSubstitutionFileName",
        "WordTranslationsOn",
        "MweWordsInColour",//yes-no
        "VideoAnnotations",//yes-no
        "VideoAnnotationsFromTranslation",//yes-no
        "SegmentTranslationAsPopup",//yes-no
        "TranslatedWordsInColour"//yes-no
    );

    for($i = 0; $i < count($ContentConfigIndexes); $i++)
    {
        if($contentObjValue[$ContentConfigIndexes[$i]] == 'yes' || $contentObjValue[$ContentConfigIndexes[$i]] == 'no')
            $contentObjValue[$ContentConfigIndexes[$i]] = strtoupper( $contentObjValue[$ContentConfigIndexes[$i]]);
        $index = $ContentIndexes[$i];
        $contentObj->$index = $contentObjValue[$ContentConfigIndexes[$i]];
    }
    if(!empty($contentObjValue["play_parts"]))
        $contentObj->PlayParts =  json_encode($contentObjValue["play_parts"]);

    $taggedTextFileName = "";
    $rawTextFileName = "";
    $automatedTaggedTextFileName = "";

    if(!empty($contentObjValue["corpus"]))
    {
        $FileNameParts = explode("/", $contentObjValue["corpus"]);
        $taggedTextFileName = $FileNameParts[count($FileNameParts) - 1];
        $nameParts = explode ( ".", $taggedTextFileName);
        $extension = strtolower($nameParts[count ($nameParts) - 1]);
        if(file_exists($tmpDir . $taggedTextFileName))
        {
            $contentObj->TaggedTextFileName = "ImportedTaggedFile." . $extension ;
            rename($tmpDir . $taggedTextFileName, $tmpDir . $contentObj->TaggedTextFileName);
        }
    }

    if(!empty($contentObjValue["untagged_corpus"]))
    {
        $FileNameParts = explode("/", $contentObjValue["untagged_corpus"]);
        $rawTextFileName = $FileNameParts[count($FileNameParts) - 1];
        $nameParts = explode ( ".", $rawTextFileName);
        $extension = strtolower($nameParts[count ($nameParts) - 1]);
        if(file_exists($tmpDir . $rawTextFileName))
        {
            $contentObj->RawTextFileName = "ImportedRawFile." . $extension ;
            rename($tmpDir . $rawTextFileName, $tmpDir . $contentObj->RawTextFileName);
        }
    }

    if(!empty($contentObjValue["tagged_corpus"]))
    {
        $FileNameParts = explode("/", $contentObjValue["tagged_corpus"]);
        $automatedTaggedTextFileName = $FileNameParts[count($FileNameParts) - 1];
        $nameParts = explode ( ".", $automatedTaggedTextFileName);
        $extension = strtolower($nameParts[count ($nameParts) - 1]);
        if(file_exists($tmpDir . $automatedTaggedTextFileName))
        {
                $contentObj->AutomatedTaggedTextFileName = "ImportedAutomatedTaggedFile." . $extension;
                rename($tmpDir . $automatedTaggedTextFileName, $tmpDir . $contentObj->AutomatedTaggedTextFileName);
        }
    }

    if($contentObjValue["extra_page_info"] != "")
    {
        $contentObj->ExtraPageInfo = "YES";
    }

    if($contentObjValue["audio_words_in_colour"] == "red")
    {
        $contentObj->AudioWordsInColour = "YES";
    }

    if(empty($contentObjValue["word_translations_on"]))
    {
        $contentObj->WordTranslationsOn = "lemma";
    }

    if($contentObjValue["translation_spreadsheet"] != "")
    {
        $pieces = explode("/", $contentObjValue["translation_spreadsheet"]);
        $fileName = $pieces[count($pieces) - 1];
        $languages = explode("_", explode("." , $fileName)[0]);
        $contentObj->L2ID = Language::getLanguageID($languages[0]);
        $contentObj->L1ID = Language::getLanguageID($languages[1]);
    }
    else if($contentObjValue["translation_spreadsheet_surface"] != "")
    {
        $pieces = explode("/", $contentObjValue["translation_spreadsheet_surface"]);
        $fileName = $pieces[count($pieces) - 1];
        $languages = explode("_", explode("." , $fileName)[0]);
        $contentObj->L2ID = Language::getLanguageID($languages[1]);
        $contentObj->L1ID = Language::getLanguageID($languages[2]);
    }
    else if($contentObjValue["translation_spreadsheet_tokens"] != "")
    {
        $pieces = explode("/", $contentObjValue["translation_spreadsheet_tokens"]);
        $fileName = $pieces[count($pieces) - 1];
        $languages = explode("_", explode("." , $fileName)[0]);
        $contentObj->L2ID = Language::getLanguageID($languages[1]);
        $contentObj->L1ID = Language::getLanguageID($languages[2]);
    }
    if($contentObjValue["segment_audio_directory"] != "")
    {
        $pieces = explode("/", $contentObjValue["segment_audio_directory"]);
        $segLdtUserName = $pieces[count($pieces) - 1];
        if($segLdtUserName != "")
        {
            $segmentAudio = Account::GetLdtUserID($headerInfo, $segLdtUserName);
            $contentObj->SegmentAudio = $segmentAudio != "" ? $segmentAudio : "-1";
        }
    }
    if($contentObjValue["word_audio_directory"] != "")
    {
        $pieces = explode("/", $contentObjValue["word_audio_directory"]);
        $wordLdtUserName = $pieces[count($pieces) - 1];
        if($wordLdtUserName != "")
        {
            $wordAudio = Account::GetLdtUserID($headerInfo, $wordLdtUserName);
            $contentObj->WordAudio = $wordAudio != "" ? $wordAudio : "-1";
        }
    }

    if($contentObjValue["notes_spreadsheet"] != "")
    {
        $contentObj->WordsNote = "YES";
    }
    if($contentObjValue["audio_tracking_file"] != "")
    {
        $contentObj->HasAudioTracking = "YES";
    }
    $contentObj->DirName = $contentObj->ContentID . "_" . str_replace(" ","_", $contentObj->ContentName);

    return $contentObj->update();
}

function LogLDTTaskTrace($ldtStatusObject, $contentID, $taskType)
{
    $cRecordingTask = new ContentRecordingTask();
    $cRecordingTask->ContentID = $contentID;
    $cRecordingTask->TaskID = $ldtStatusObject["id"];
    $cRecordingTask->TaskType = $taskType;
    $cRecordingTask->LastUpdate = $ldtStatusObject["lastUpdated"];
    $cRecordingTask->TotalItems = $ldtStatusObject["items"];
    $cRecordingTask->RecordedItems = $ldtStatusObject["recordedItems"];;
    $cRecordingTask->insert();
    return true;
}

function GetContentLog()
{
    $where = "";
    $whereParam = array();

    if(!empty($_REQUEST["StartDate"]))
    {
        $where .= " and LogDateTime > :startDate";
        $whereParam[":startDate"] = $_REQUEST["StartDate"];
    }

    if(!empty($_REQUEST["EndDate"]))
    {
        $where .= " and LogDateTime < :endDate";
        $whereParam[":endDate"] = $_REQUEST["EndDate"];
    }

    if($_REQUEST["ContentID"] != -1)
    {
        $where .= " and RelatedID = :contentID";
        $whereParam[":contentID"] = $_REQUEST["ContentID"];
    }

    $contentLogRes = UserActivitiesLogs::SearchContentLogs($where, $whereParam);


    $LogHistory = "<table border='1'>" ;
    $LogHistory .= "<tr>
                        <th style='width: 5%'>#</th>
                        <th style='width: 40%'>which</th>
                        <th style='width: 30%;'>what</th>
                        <th style='width: 25%'>when</th>
                        </tr>" ;
    if(count($contentLogRes) > 0)
    {
        for($i = 0; $i < count($contentLogRes); $i++)
        {
            $LogHistory .= "<tr>";
            $LogHistory .=  "<td>" . ($i+1) . "</td>"  ;
            $LogHistory .=  "<td>" . $contentLogRes[$i]["ContentName"] . "</td>"  ;
            $LogHistory .=  "<td>" . $contentLogRes[$i]["LogData"] . "</td>"  ;
            $LogHistory .=  "<td>" . $contentLogRes[$i]["LogDateTime"] . "</td>"  ;
            $LogHistory .= "</tr>";
        }
    }
    $LogHistory .= "</table>" ;

    echo $LogHistory;
    die();
}

function ApplyTypeToToken()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $contentID = $_GET["contentID"];
    // Sanitise argument - MR
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);

    $resultArray[0]["id"] = $contentIDSanitised;
    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $contentIDSanitised);
    $info = Content::SearchContent($where, $whereParam);
    $contentObj = FillItems($info[0]);

    $corpusDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/";
    $resourcesDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;

    $bashFile = $resourcesDir . "ApplyTypeToToken.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py tokens_from_types_and_copy " .
        $corpusDir . "local_config.json " . $resourcesDir . " 2>&1";;
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentID, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") !== false)
    {
        $resultArray[0]["resultMsg"] = "FailedToApplyTypes";
    }
    else
    {
        ReadContentTokens($resourcesDir, $backupDir, $contentObj->ContentID);
        $langTranslationDir = LaraContentDir . $_REQUEST["DirName"] . "/" . SubDirNames["translations"] . "/";
        $langTranslationFileName = "token_" . Language::getLanguageName($_REQUEST["L2ID"]) . "_" . Language::getLanguageName($_REQUEST["L1ID"]) . ".csv";
        updateTokenRep($resourcesDir, $backupDir, $langTranslationDir, $langTranslationFileName);
        $resultArray[0]["resultMsg"] = "TypeTranslationApplied";
    }
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function DistributeContent()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $contentID = $_GET["contentID"];
    // Sanitise arguments - MR
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);

    $resultArray[0]["id"] = $contentIDSanitised;
    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $contentIDSanitised);
    $info = Content::SearchContent($where, $whereParam);
    $contentObj = FillItems($info[0]);

    $corpusDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/";
    $resourcesDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;
    $crowdsourceZipFile = $contentObj->DirName . "_crowdsource.zip";
    $crowdsourceDir = $contentObj->DirName . "_crowdsource/";

    $crowdSourceDirRes = ExtraModules::CreateDir($resourcesDir . $crowdsourceDir);

    $bashFile = $resourcesDir . "CutUpProject.txt";
    $fp = fopen( $bashFile, "w");

    ExtraModules::BackupFile($resourcesDir . $crowdsourceZipFile,
        $backupDir . date("Ymd_His") . "_" . $crowdsourceZipFile);

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py cut_up_project " .
        $corpusDir . "local_config.json " . $resourcesDir . $crowdsourceZipFile . " 2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentID, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentID, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") !== false)
    {
        if(strpos($output, "unable to find occurrences of") !== false &&
            strpos($output, "cut") !== false)
        {
            $resultArray[0]["resultMsg"] = "NotSuitableForCut";
        }
        else
        {
            $resultArray[0]["resultMsg"] = "FailedDistribute";
        }
    }
    else
    {
        if (UnzipIt($resourcesDir . $crowdsourceZipFile , $resourcesDir . $crowdsourceDir) == false)
        {
            ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "FailedToExtractExtResFile");
            ExtraModules::KillProcess($resultArray, "FailedToExtractExtResFile");
        }
        $dirContents = scandir($resourcesDir . $crowdsourceDir);

        foreach ($dirContents as $file) {
            $extension = pathinfo($file, PATHINFO_EXTENSION);
            if ($extension == 'zip')
            {
                $importRes = ImportLaraContent(true, $contentID, $file, $resourcesDir . $crowdsourceDir);
                if($importRes != "SuccessfullyImported")
                {
                    $resultArray[0]["resultMsg"] = $importRes;
                    //todo delete any project where ParentId is $contentID
                    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
                    ExtraModules::KillProcess($resultArray);
                }
            }
        }

        $contentObj->CrowdsourcingStatus = 'Distributed';
        $setPart = "CrowdsourcingStatus = :crowdsourcingStatus";
        $wherePart = "ContentID = :contentID";
        $params = array(":crowdsourcingStatus" => $contentObj->CrowdsourcingStatus, ":contentID" => $contentObj->ContentID);
        Content::PartialUpdate($setPart, $wherePart, $params);
        $resultArray[0]["resultMsg"] = "SuccessfulDistributeContent";
    }
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function CollectContent()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $contentID = $_GET["contentID"];
    // Sanitise arguments - MR
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);

    $resultArray[0]["id"] = $contentIDSanitised;
    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $contentIDSanitised);
    $info = Content::SearchContent($where, $whereParam);
    $contentObj = FillItems($info[0]);

    $corpusDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/";
    $resourcesDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["resourcesDir"] . "/";
    $backupDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/";
    $bashFile = $resourcesDir . "StickTogetherProject.txt";
    $fp = fopen($bashFile, "w");

    $childrenRows = Content::ContentChildrenList($contentID);
    $childrenDirs = array();
    for ($i = 0; $i < count($childrenRows); $i++)
        $childrenDirs[$i] = LaraContentDir . $childrenRows[$i]["DirName"] . "/" . SubDirNames["corpus"] . "/" . "local_config.json";

    $childrenConfigFiles = $resourcesDir . "ChildrenConfigFiles.json";
    ExtraModules::BackupFile($resourcesDir . "ChildrenConfigFiles.json",
        $backupDir . date("Ymd_His") . "_ChildrenConfigFiles.json");
    $handle = fopen($childrenConfigFiles, "w") or die("Cannot open file:  " . $childrenConfigFiles);
    fwrite($handle, json_encode($childrenDirs));
    fclose($handle);

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py stick_together_projects " .
        $childrenConfigFiles . " " . $corpusDir . "local_config.json " . " 2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < ' . $bashFile);
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentIDSanitised, ContentRelatedPage, $LogID);

    if (strpos($output, "*** Error") !== false)
    {
        $resultArray[0]["resultMsg"] = "FailedCollect";
    }
    else
    {
        $contentObj->CrowdsourcingStatus = 'Collected';
        $setPart = "CrowdsourcingStatus = :crowdsourcingStatus";
        $wherePart = "ContentID = :contentID";
        $params = array(":crowdsourcingStatus" => $contentObj->CrowdsourcingStatus, ":contentID" => $contentObj->ContentID);
        Content::PartialUpdate($setPart, $wherePart, $params);
        $resultArray[0]["resultMsg"] = "SuccessfulCollectContent";
    }
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function GetTask()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $_GET["contentID"]);
    $info = Content::SearchContent($where, $whereParam);
    $contentObj = FillItems($info[0]);

    $resultArray[0]["id"] = $contentObj->ContentID;

    if(!empty($contentObj->CrowdworkerID))
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "AlreadyTaken");
        ExtraModules::KillProcess($resultArray, "AlreadyTaken");
    }

    $setPart = "CrowdWorkerID = :cwID";
    $where = " contentID = :contentID";
    $whereParam = array(":cwID" => $_SESSION[SessionIndex['UserID']], ":contentID" => $contentObj->ContentID);
    Content::PartialUpdate($setPart, $where, $whereParam);

    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "SuccessfullyAssigned");
    ExtraModules::KillProcess($resultArray, "SuccessfullyAssigned");
}

function GiveUpTask()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_GET["contentID"];

    $giveUpObj = new ContentGiveUpReason();
    $giveUpObj->ContentID = $_GET["contentID"];
    $giveUpObj->UserID = $_SESSION[SessionIndex['UserID']];
    $giveUpObj->UserRole = $_GET["currentRole"];
    $giveUpObj->ReasonBody = $_GET["reasonBody"];
    $giveUpObj->ReasonDateTime = date('Y-m-d H:i:s');

    $giveUpObj->insert();

    $setPart = "CrowdWorkerID = NULL";
    $where = " contentID = :contentID";
    $whereParam = array( ":contentID" => $_GET["contentID"]);
    Content::PartialUpdate($setPart, $where, $whereParam);

    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "SuccessfullyTakenBack");
    ExtraModules::KillProcess($resultArray, "SuccessfullyTakenBack");
}

function SendContentMessage()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_GET["contentID"];

    $messageObj = new ContentRequesterWorkerMessage();
    $messageObj->ContentID = $_GET["contentID"];
    $messageObj->UserID = $_SESSION[SessionIndex['UserID']];
    $messageObj->UserRole = $_GET["currentRole"];
    $messageObj->MessageBody = $_GET["messageBody"];
    $messageObj->MessageDateTime = date('Y-m-d H:i:s');

    $messageObj->insert();

    if($_GET["currentRole"] == "Worker")
        $setPart = "CrowdsourcedPartStatus = 'SentToRequester'";
    else
        $setPart = "CrowdsourcedPartStatus = 'SentToWorker'";

    $where = " contentID = :contentID";
    $whereParam = array( ":contentID" => $_GET["contentID"]);
    Content::PartialUpdate($setPart, $where, $whereParam);

    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "SuccessfullySentMessage");
    ExtraModules::KillProcess($resultArray, "SuccessfullySentMessage");
}

function GetContentMessages()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = -1;

    $whereParam = array(":cID" => $_REQUEST["contentID"]);
    $ContentMessages = ContentRequesterWorkerMessage::selectMessages($whereParam);

    if(count($ContentMessages) == 0)
    {
        $resultArray[0]["resultMsg"] = "noMessageFound";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        echo "No message found here.";
        die();
    }

    $tableInfo = "<table class='responstable' style='width: 100%'>";
    $tableInfo .= "<tr><th>User</th>";
    $tableInfo .= "<th>Role</th>";
    $tableInfo .= "<th>Time</th>";
    $tableInfo .= "<th>Message</th>";
    $tableInfo .=  "</tr>";
    for($i = 0; $i < count($ContentMessages); $i++)
    {
        $thisRow = $ContentMessages[$i];
        $UserName = $thisRow["UserName"];
        $UserRole = $thisRow["UserRole"];
        $MessageDateTime = $thisRow["MessageDateTime"];
        $MessageBody = $thisRow["MessageBody"];

        $rowString  = "<tr>";
        $rowString .= "<td>" . $UserName . "</td>";
        $rowString .= "<td>" . $UserRole . "</td>";
        $rowString .= "<td>" . $MessageDateTime . "</td>";
        $rowString .= "<td>" . $MessageBody . "</td>";
        $rowString .= "</tr>";
        $tableInfo .= $rowString;
    }
    $tableInfo .= "</table></td></tr>";

    $resultArray[0]["id"] = $_REQUEST["contentID"];
    $resultArray[0]["resultMsg"] = "SuccessfullyRetrievedMessages";

    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    echo $tableInfo;
    die();
}

function FinalizeTask()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_GET["contentID"];

    $setPart = "CrowdsourcedPartStatus = 'Approved'";
    $where = " contentID = :contentID";
    $whereParam = array( ":contentID" => $_GET["contentID"]);
    Content::PartialUpdate($setPart, $where, $whereParam);

    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, "SuccessfullyFinalized");
    ExtraModules::KillProcess($resultArray, "SuccessfullyFinalized");
}

function TtsEnginesList()
{
    $languageID = $_REQUEST["LanguageID"];
    // Sanitise arguments - MR
    $languageIDSanitised = filter_var($languageID, FILTER_SANITIZE_STRING);

    $LanguageName = Language::getLanguageName($languageIDSanitised);
    $LangCorpusDirName = ContentTmpDirectory . $LanguageName . "/";
    $langDirRes = ExtraModules::CreateDir($LangCorpusDirName, SubDirNamesContentTmp);
    $resourcesDir = $LangCorpusDirName . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $enginesListFile = $resourcesDir . "ttsEngines.txt";
    $bashFile = $resourcesDir . "GetTtsEngines.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py get_tts_engines " .
        $LanguageName . " " . $enginesListFile . " 2>&1";
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $languageIDSanitised, LanguageRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $languageIDSanitised, LanguageRelatedPage, $LogID);

    $res = json_decode(file_get_contents($enginesListFile), true);
    $retArray = array();
    for($i = 0; $i < count($res); $i++)
    {
        $retArray['engines'][$i] = $res[$i]['engine'];
        for($j = 0; $j < count($res[$i]['voices']); $j++)
        {
            $retArray[$res[$i]['engine']][$j] = $res[$i]['voices'][$j];
        }
    }

    echo json_encode($retArray);

    die();
}

function GenerateSegmentsTTS()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $contentID = $_GET["contentID"];
    // Sanitise arguments - MR
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);

    $resultArray[0]["id"] = $contentIDSanitised;
    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $contentIDSanitised);
    $info = Content::SearchContent($where, $whereParam);
    $contentObj = FillItems($info[0]);

    $corpusDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/";
    $resourcesDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $recordingScriptFile = $resourcesDir . 'ldt_segment_recording_full.json';
    $zipFile = $resourcesDir . $contentObj->TtsEngine . "_" . $contentObj->TtsVoice . "_segments.zip";
    $bashFile = $resourcesDir . "create_tts_audio_segments.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py create_tts_audio " .
        $recordingScriptFile . " " . $corpusDir . "local_config.json " . $zipFile . " 2>&1";;
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentIDSanitised, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") !== false)
        $resultArray[0]["resultMsg"] = "FailedToGenerateSegmentsTTS";
    else
        $resultArray[0]["resultMsg"] = "SegmentTTSDone";

    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function GenerateWordsTTS()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $contentID = $_GET["contentID"];
    // Sanitise arguments - MR
    $contentIDSanitised = filter_var($contentID, FILTER_SANITIZE_STRING);

    $resultArray[0]["id"] = $contentIDSanitised;
    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $contentIDSanitised);
    $info = Content::SearchContent($where, $whereParam);
    $contentObj = FillItems($info[0]);

    $corpusDir = LaraContentDir . $contentObj->DirName . "/" . SubDirNames["corpus"] . "/";
    $resourcesDir = ContentTmpDirectory . $contentObj->DirName . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $recordingScriptFile = $resourcesDir . 'ldt_word_recording_full.json';
    $zipFile = $resourcesDir . $contentObj->TtsEngine . "_" . $contentObj->TtsVoice . "_words.zip";
    $bashFile = $resourcesDir . "create_tts_audio_words.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py create_tts_audio " .
        $recordingScriptFile . " " . $corpusDir . "local_config.json " . $zipFile . " 2>&1";;
    fwrite($fp, $command);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentIDSanitised, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentIDSanitised, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") !== false)
        $resultArray[0]["resultMsg"] = "FailedToGenerateWordsTTS";
    else
        $resultArray[0]["resultMsg"] = "WordTTSDone";

    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function InstallTTS($contentObj, $type)
{
    $dirName = $contentObj->ContentID . "_" . str_replace(" ","_",$contentObj->ContentName);
    // Sanitise arguments - MR
    $dirNameSanitised = filter_var($dirName, FILTER_SANITIZE_STRING);

    $audioDir = LaraContentDir . $dirNameSanitised . "/" . SubDirNames["audio"] . "/";
    $corpusDir = LaraContentDir . $dirNameSanitised . "/" . SubDirNames["corpus"] . "/";
    $resourcesDir = ContentTmpDirectory . $dirNameSanitised . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $configFile = $corpusDir . "local_config.json";
    if($type == "words")
    {
        $bashFile = $audioDir . "InstallWordsTTS.txt";
        $recFile = $resourcesDir . "ldt_word_recording_full.json";
        $zipFile = $resourcesDir . $contentObj->TtsEngine . "_" . $contentObj->TtsVoice . "_words.zip";
    }
    else
    {
        $bashFile = $audioDir . "InstallSegmentsTTS.txt";
        $recFile = $resourcesDir . "ldt_segment_recording_full.json";
        $zipFile = $resourcesDir . $contentObj->TtsEngine . "_" . $contentObj->TtsVoice . "_segments.zip";
    }

    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py install_ldt_zipfile " .
        $zipFile . " " . $recFile . " " . $type . " " . $configFile . " 2>&1" ;
    fwrite($fp, $command);

    if(file_exists($zipFile))
    {
        $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentObj->ContentID, ContentRelatedPage);
        $output = shell_exec('bash < '  . $bashFile );
        ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentObj->ContentID, ContentRelatedPage, $LogID);
        if(strpos($output, "*** Error") === false)
            return true;
        return false;
    }
    return true;
}