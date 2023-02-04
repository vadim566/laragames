<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 6/6/2019
 * Time: 05:45 PM
 */


require_once '../Config.php';
require_once '../data/Content.data.php';
require_once '../class/Content.class.php';
require_once '../class/ContentType.class.php';
require_once '../class/ContentTypeExample.class.php';
require_once '../class/ContentLemma.class.php';
require_once '../class/ContentLemmaExample.class.php';
require_once '../class/ContentSegment.class.php';
require_once '../class/ContentToken.class.php';
require_once '../class/RawContentSegment.class.php';
require_once '../class/RawContentParticle.class.php';
require_once '../class/Language.class.php';
require_once '../class/LanguagePair.class.php';
require_once '../SharedModules/ExtraModules.class.php';

$task = isset($_REQUEST["task"]) ? $_REQUEST["task"] :  "";

switch ($task)
{
    case "saveLemma":
        saveLemma(false);

    case "saveNote":
        saveLemma(true);

    case "saveType":
        saveType();

    case "saveSegment":
        saveSegment();

    case "saveToken":
        saveToken();

    case "loadLemmaPage":
        loadLemmaPage();

    case "loadSegmentPage":
        loadSegmentPage();

    case "loadTypePage":
        loadTypePage();

    case "loadTokenPage":
        loadTokenPage();

    case "UploadTokenTranslation":
        UploadTokenTranslation();

    case "UploadTypeTranslation":
        UploadTypeTranslation();

    case "UploadLemmaTranslation":
        UploadLemmaTranslation();

    case "UploadSegmentTranslation":
        UploadSegmentTranslation();
}

//----- Lemmas -----//
function ReadContentLemmas($resourcesDir, $backupDir, $contentID)
{

//    $start = microtime(true);

    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $contentID);

    //reformat Python json
    $lemmasFileJsonData = json_decode(file_get_contents($resourcesDir . 'word_translations.json'), true);
    $notesFileJsonData = json_decode(file_get_contents($resourcesDir . 'notes.json'), true);


//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Read lemma translation and notes json: " . $time_elapsed_secs . "----");
//    $start = microtime(true);


    $lemmaArray[] = array("ContentID","LemmaOrder","EntryInL1","EntryInL2","Frequency","Notes");
    $lemmaExampleArray[] = array("ContentID","LemmaOrder","ExampleText");

    for($i = 0; $i < count($lemmasFileJsonData); $i++)
    {
        $index = $i + 1;
        $lemmaArray[$index][0] = $contentID;
        $lemmaArray[$index][1] = $index;
        $lemmaArray[$index][2] = $lemmasFileJsonData[$i][1];
        $lemmaArray[$index][3] = $lemmasFileJsonData[$i][0];
        $lemmaArray[$index][4] = $lemmasFileJsonData[$i][2];
        $lemmaArray[$index][5] = "";

        for($k = 0; $k < count($notesFileJsonData); $k++)
        {
            if($notesFileJsonData[$k][0] ==  $lemmasFileJsonData[$i][0])
            {
                $lemmaArray[$index][5] = $notesFileJsonData[$k][1];
                $k = count($notesFileJsonData);
            }
        }

        for($j = 0; $j < count($lemmasFileJsonData[$i][3]); $j++)
        {
            $lemmaExampleArray[] = array($contentID , $index, $lemmasFileJsonData[$i][3][$j]);
        }
    }

    //put lemma array in json
    $lemmaJson = "word_lemma.json";
    ExtraModules::BackupFile($resourcesDir . $lemmaJson, $backupDir . date("Ymd_His") . "_" . $lemmaJson);
    file_put_contents($resourcesDir . $lemmaJson, json_encode($lemmaArray, JSON_PRETTY_PRINT));

    //put lemma example array in json
    $lemmaExampleJson = "word_lemma_ex.json";
    ExtraModules::BackupFile($resourcesDir . $lemmaExampleJson, $backupDir . date("Ymd_His") . "_" . $lemmaExampleJson);
    file_put_contents($resourcesDir . $lemmaExampleJson, json_encode($lemmaExampleArray, JSON_PRETTY_PRINT));

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Convert Python jsons to PHP jsons: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    //put lemma json in csv
    $lemmaCsv = "word_lemma.csv";
    $wordLemmaToCSV = ExtraModules::JsonToCsv($resourcesDir . "LemmaResourceToCSV.txt",
        $resourcesDir . $lemmaCsv,
        $backupDir . date("Ymd_His") . "_" . $lemmaCsv,
        $resourcesDir . $lemmaJson,
        $contentID);

    //put lemma example json in csv
    $lemmaExampleCsv = "word_lemma_ex.csv";
    $wordLemmaExToCSV = ExtraModules::JsonToCsv($resourcesDir . "LemmaExampleResourceToCSV.txt",
        $resourcesDir . $lemmaExampleCsv,
        $backupDir . date("Ymd_His") . "_" . $lemmaExampleCsv,
        $resourcesDir . $lemmaExampleJson,
        $contentID);

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Convert PHP lemma jsons to CSV using python: " . $time_elapsed_secs . "----");
//    $start = microtime(true);


    //put lemma csv in table
    if($wordLemmaToCSV)
    {
        ContentLemma::delete($where, $whereParam);
        ContentLemma::insertContentLemmas($resourcesDir . $lemmaCsv);
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToLemma";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Put lemma csv in db: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    //put lemma example csv in table
    if($wordLemmaExToCSV)
    {
        ContentLemmaExample::delete($where, $whereParam);
        ContentLemmaExample::insertContentLemmaExamples($resourcesDir . $lemmaExampleCsv);
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToLemmaExample";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Put lemma example csv in db: " . $time_elapsed_secs . "----");

    return true;
}

function loadLemmaPage()
{
    $contentID = $_REQUEST["contentID"];
    $pageToLoad = $_REQUEST["pageToLoad"];
    $justNote = $_REQUEST["justNote"];
    $editMode = $_REQUEST["mode"];
    $saveFunction = ($justNote == "yes") ? 'saveNote' : 'saveLemma';
    $checkOnSubmit = true;

    $where = " cl.ContentID = :contentID ";
    $whereParam = array(":contentID" => $contentID);
    $info = ContentLemma::SearchContentLemma($where, $whereParam, $pageToLoad);

    $where = " ContentID = :contentID ";
    $whereParam = array(":contentID" => $contentID);
    $contentInfo = Content::SearchContent($where, $whereParam);
    $L1Name =  Language::getLanguageName($contentInfo[0]["L1ID"]);
    $L2Name =  Language::getLanguageName($contentInfo[0]["L2ID"]);

    $idIndex = "ContentLemmaID";
    $l1Index = "EntryInL1";
    $l2Index = "EntryInL2";
    $example = "examples";
    $notes = "Notes";

    $l1String = "";
    $noteString = "";

    $tableInfo = "<tr id='translationError'  style='display: none'>
                    <td><p class='ErrorMsg'></p></td>
                  </tr>
                  <tr style='width: 100%'>
                <td>";

    $tableInfo .= "<table class='responstable' style='width: 100%'>";
    $tableInfo .= "<tr><th>" . $L2Name . "</th>";
    if($justNote == 'no')
        $tableInfo .= "<th>" . $L1Name . "</th>";
    $tableInfo .=  "<th>Notes</th></tr>";
    for($i = 0; $i < min(RowPerPage, count($info)) ; $i++)
    {
        $thisRow = $info[$i];
        $id = $thisRow[$idIndex];
        $valueInL1 = $thisRow[$l1Index];
        $l1String .= $thisRow[$l1Index] . "**";
        $valueInL2 = $thisRow[$l2Index];
        $exampleVal = $thisRow[$example];
        $notesVal = $thisRow[$notes];
        $noteString .= $thisRow[$notes] . "**";

        $rowString  = "<tr>";
        $rowString  .= "<input type='hidden' id='lemmaInfo[" . $i . "][0]' 
                              name='lemmaInfo[" . $i . "][0]' value='" . $id . "'>";
        $rowString .= "<td title='" . htmlspecialchars($exampleVal, ENT_QUOTES) . "'>" . $valueInL2 . "</td>";
        if($justNote == 'no')
        {
            $rowString .= "<td>
                               <input type='text' name='lemmaInfo[" . $i . "][1]' class='l1Input'
                                id='lemmaInfo[" . $i . "][1]' value='". htmlspecialchars($valueInL1, ENT_QUOTES) ."'>
                            </td>";
        }
        $rowString .= "<td>
                           <input type='text' name='lemmaInfo[" . $i . "][2]' class='noteInput'
                            id='lemmaInfo[" . $i . "][2]'  value='". htmlspecialchars($notesVal, ENT_QUOTES) ."'>
                        </td>";
        $rowString .= "</tr>";
        $tableInfo .= $rowString;
    }
    if($justNote == 'no')
        $tableInfo .= "<input type='hidden' id='l1String' name='l1String' value='" . $l1String . "'>";
    $tableInfo .= "<input type='hidden' id='noteString' name='noteString' value='" . $noteString . "'>";
    $tableInfo .= "</table></td></tr>";

    $numberOfPages = ContentLemma::NumberOfPages($contentID);

    $pageNumbersRows = ceil($numberOfPages / 20);
    for($j = 0; $j < $pageNumbersRows; $j++) {
        $tableInfo .= "<tr><td align='center'>";
        $pageNumbersRow = "";
        if ($j == 0)
        {
            $prvPage = $pageToLoad - 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToLemmaPage(" .$prvPage . "," . $checkOnSubmit . ")'> prv </span>";
        }
        for ($i = 1; $i <= 20; $i++) {
            $spanIndex = ($j * 20) + $i;
            if ($spanIndex <= $numberOfPages) {
                $pageNumbersRow .= "<span class='pageNumber' ";
                if ($spanIndex == $pageToLoad)
                    $pageNumbersRow .= " style='background-color:#008080' ";
                $pageNumbersRow .= " onclick='goToLemmaPage(" . $spanIndex . "," . $checkOnSubmit . ")'>" . $spanIndex . "</span>";
            }
        }
        if ($j == $pageNumbersRows - 1)
        {
            $nextPage = $pageToLoad + 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToLemmaPage(" . $nextPage . "," . $checkOnSubmit . ")'> nxt </span>";
        }
        $tableInfo .= $pageNumbersRow . "</td></tr>";
    }

    $tableInfo .= "<tr>
                    <td align='center'>";
    if($editMode != 'readOnly')
    {
        $tableInfo .= "<input type='button'  id='SendButton' name='SendButton'
                               value='Save translations' onclick='sendTranslation(\"JustSave\",\"" . $saveFunction . "\")'>
                        <input type='button'  id='SendAndCopyButton' name='SendAndCopyButton'
                               value='Save and exit' onclick='sendTranslation(\"SaveAndExit\",\"" .  $saveFunction . "\")'>";
    }
    $tableInfo .= "<input type='button'  id='ExitButton' name='ExitButton' value='Exit' onclick='exitWithoutSaving()'>";
    $tableInfo .= "</td></tr>";

    echo $tableInfo;
    die();
}

function saveLemma($justNote = false)
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_REQUEST["ContentID"];

    $where = "ContentID = :contentID";
    $whereParam = array(":contentID" => $_REQUEST["ContentID"]);
    $contentResult = Content::SearchContent($where, $whereParam);

    $resourcesDir = ContentTmpDirectory . $contentResult[0]["DirName"] . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = ContentTmpDirectory . $contentResult[0]["DirName"]  . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;
    $corpusDir = LaraContentDir . $contentResult[0]["DirName"] . "/" . SubDirNames["corpus"] . "/";
    $langDir = LaraContentDir . Language::getLanguageName($contentResult[0]["L2ID"]);
    ExtraModules::CreateDir($langDir,SubDirNames);
    $langTranslationDir =  $langDir . "/" . SubDirNames["translations"] . "/";
    $langTranslationFileName = Language::getLanguageName($contentResult[0]["L2ID"]) . "_" . Language::getLanguageName($contentResult[0]["L1ID"]) . ".csv";

    $createBackupDIRRes = ExtraModules::CreateDir($backupDir);
    if (in_array($createBackupDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, $createBackupDIRRes . "CreateResources");
        ExtraModules::KillProcess($resultArray, $createBackupDIRRes . "CreateResources");
    }
    saveLemmaInDB($resourcesDir, $backupDir, $justNote);
    updateLemmaRep($resourcesDir, $backupDir, $corpusDir, $langTranslationDir, $langTranslationFileName, $justNote);
    $resultArray[0]["resultMsg"] = "DataIsSavedForItems";
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function saveLemmaInDB( $resourcesDir, $backupDir, $justNote)
{
    $lemmaInfo = $_REQUEST["lemmaInfo"];
    $contentID = $_REQUEST["ContentID"];
    $insertFileContentArray = array();
    $insertFileContentArray[] = array("ContentLemmaID","ContentID","LemmaOrder","EntryInL1","EntryInL2","Frequency","Notes");
    for($i = 0; $i < count($lemmaInfo); $i++)
    {
        $ContentLemmaID = $lemmaInfo[$i][0];
        $EntryInL1 = $justNote ? "" : $lemmaInfo[$i][1];
        $Notes = $lemmaInfo[$i][2];
        $insertFileContentArray[] = array($ContentLemmaID, $contentID, $i, $EntryInL1, "", "", $Notes);
    }
    $lemmaUiJson = "word_lemma_ui.json";
    ExtraModules::BackupFile($resourcesDir . $lemmaUiJson, $backupDir . date("Ymd_His") . "_" . $lemmaUiJson);
    file_put_contents($resourcesDir . $lemmaUiJson, json_encode($insertFileContentArray, JSON_PRETTY_PRINT));

    $lemmaUiCSV = "word_lemma_ui.csv";
    $lemmaUiToCSV = ExtraModules::JsonToCsv($resourcesDir . "LemmaFromUiToCSV.txt",
        $resourcesDir . $lemmaUiCSV,
        $backupDir . date("Ymd_His") . "_" . $lemmaUiCSV,
        $resourcesDir . $lemmaUiJson,
        $contentID);

    if($lemmaUiToCSV)
    {
        ContentLemma::updateContentLemmas($resourcesDir . $lemmaUiCSV, $contentID . "_" . date("Ymd_His"), $justNote);
        return true;
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToGenerateCsv";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
}

function updateLemmaRep($resourcesDir, $backupDir, $corpusDir, $langTranslationDir, $langTranslationFileName, $justNote)
{
    $where = "ContentID = :contentID";
    $whereParam = array(":contentID" => $_REQUEST["ContentID"]);
    $finalRawData = ContentLemma::SelectForCSV($where, $whereParam);
    $finalTranslationArray[] = array("EntryInL2","EntryInL1");
    $finalNoteArray[] = array("EntryInL2","Notes");
    for($i = 0; $i < count($finalRawData); $i++)
    {
        if(!empty($finalRawData[$i]['EntryInL1']))
            $finalTranslationArray[] = array($finalRawData[$i]['EntryInL2'], $finalRawData[$i]['EntryInL1']);
        if(!empty($finalRawData[$i]['Notes']))
            $finalNoteArray[] = array($finalRawData[$i]['EntryInL2'], $finalRawData[$i]['Notes']);
    }

    $finalNoteFile = "lemmaNote.json";
    ExtraModules::BackupFile($resourcesDir . $finalNoteFile, $backupDir . date("Ymd_His") . "_" . $finalNoteFile);
    file_put_contents($resourcesDir . $finalNoteFile, json_encode($finalNoteArray, JSON_PRETTY_PRINT));

    $noteDBToCSV = ExtraModules::JsonToCsv($resourcesDir . "NoteConvertToCSV.txt",
        $resourcesDir . "lemmaNote.csv",
        $backupDir . date("Ymd_His") . "_lemmaNote.csv",
        $resourcesDir . $finalNoteFile,
        $_REQUEST["ContentID"]);

    if($noteDBToCSV)
    {
        ExtraModules::BackupFile($corpusDir . "notes.csv", $backupDir . date("Ymd_His") . "_notes.csv");
        copy($resourcesDir . "lemmaNote.csv", $corpusDir . "notes.csv");
    }
    else{
        return false;
    }

    if(!$justNote)
    {
        $finalTranslationFile = "lemmaTranslation.json";
        ExtraModules::BackupFile($resourcesDir . $finalTranslationFile, $backupDir . date("Ymd_His") . "_" . $finalTranslationFile);
        file_put_contents($resourcesDir . $finalTranslationFile, json_encode($finalTranslationArray, JSON_PRETTY_PRINT));

        $lemmaDBToCSV = ExtraModules::JsonToCsv($resourcesDir . "LemmaConvertToCSV.txt",
            $resourcesDir . "lemmaTranslation.csv",
            $backupDir . date("Ymd_His") . "_lemmaTranslation.csv",
            $resourcesDir . $finalTranslationFile,
            $_REQUEST["ContentID"]);

        if($lemmaDBToCSV)
        {
            if(file_exists($langTranslationDir . $langTranslationFileName))
            {
                ExtraModules::MergeUpdateTranslationSpreadsheet($resourcesDir . "LemmaMergeCSVs.txt",
                    $langTranslationDir. $langTranslationFileName,
                    $backupDir . date("Ymd_His") . "_lemma_" . $langTranslationFileName,
                    $resourcesDir . "lemmaTranslation.csv",
                    $_REQUEST["ContentID"]);
            }
            else
            {
                copy($resourcesDir . "lemmaTranslation.csv", $langTranslationDir . $langTranslationFileName);
                return true;
            }
        }
        else
        {
            return false;
        }
    }
    return true;
}

function UploadLemmaTranslation()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_REQUEST["ContentID"];

    $resourcesDir = ContentTmpDirectory . $_REQUEST["DirName"] . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = ContentTmpDirectory . $_REQUEST["DirName"] . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;

    if (!ExtraModules::FileExists('UploadLemmaTranslation'))
        ExtraModules::KillProcess($resultArray, "lemmaTranslationFileDoesNotExist");

    if (!ExtraModules::FileExtensionIsValid('UploadLemmaTranslation', array('csv')))
        ExtraModules::KillProcess($resultArray, "lemmaTranslationFileFormatNotValid");

    $file = $_FILES['UploadLemmaTranslation'];
    $fileName = "uploaded_word_translations.csv";
    ExtraModules::BackupFile($resourcesDir . "uploaded_word_translations.csv",
        $backupDir . date("Ymd_His") . "uploaded_word_translations.csv");
    if(!ExtraModules::UploadFile($fileName, $resourcesDir, $file))
        ExtraModules::KillProcess($resultArray, "lemmaTranslationFileNotUploaded");

    $csvFileOnServer = "word_translations_offline.csv";
    ExtraModules::MergeUpdateTranslationSpreadsheet($resourcesDir . "OfflineLemmaMergeCSVs.txt",
        $resourcesDir. $csvFileOnServer,
        $backupDir . date("Ymd_His") . "_" . $csvFileOnServer,
        $resourcesDir . $fileName,
        $_REQUEST["ContentID"]);

    $jsonFileName = "uploaded_word_translations.json";
    $wordTypeToCSV = ExtraModules::CsvToJson($resourcesDir . "lemmaConvertToJson.txt",
        $resourcesDir . $jsonFileName,
        $backupDir . date("Ymd_His") . "_" . $jsonFileName,
        $resourcesDir . $csvFileOnServer,
        $_REQUEST["ContentID"]);

    ReadUploadedContentLemma($resourcesDir, $backupDir, $_REQUEST["ContentID"]);

    $langDir = LaraContentDir . Language::getLanguageName($_REQUEST["L2ID"]);
    ExtraModules::CreateDir($langDir,SubDirNames);
    $langTranslationDir =  $langDir . "/" . SubDirNames["translations"] . "/";
    $langTranslationFileName = Language::getLanguageName($_REQUEST["L2ID"]) . "_" . Language::getLanguageName($_REQUEST["L1ID"]) . ".csv";
    updateLemmaRepAfterUpload($resourcesDir, $backupDir, $langTranslationDir, $langTranslationFileName);
    $resultArray[0]["resultMsg"] = "DataFromFileIsSavedForItems";
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function ReadUploadedContentLemma($resourcesDir, $backupDir, $contentID)
{
    $lemmasFileJsonData = json_decode(file_get_contents($resourcesDir . 'uploaded_word_translations.json'), true);

    $lemmaArray[] = array("ContentLemmaID", "ContentID","LemmaOrder","EntryInL1","EntryInL2","Frequency","Notes");

    for($i = 1; $i < count($lemmasFileJsonData); $i++)
    {
        $index = $i;
        $lemmaArray[$index][0] = $index;
        $lemmaArray[$index][1] = $contentID;
        $lemmaArray[$index][2] = $index;
        $lemmaArray[$index][3] = $lemmasFileJsonData[$i][1];
        $lemmaArray[$index][4] = $lemmasFileJsonData[$i][0];
        $lemmaArray[$index][5] = 0;
        $lemmaArray[$index][6] = "";
    }

    $lemmaJson = "word_lemma.json";
    ExtraModules::BackupFile($resourcesDir . $lemmaJson, $backupDir . date("Ymd_His") . "_" . $lemmaJson);
    file_put_contents($resourcesDir . $lemmaJson, json_encode($lemmaArray, JSON_PRETTY_PRINT));

    $lemmaCsv = "word_lemma.csv";
    $wordLemmaToCSV = ExtraModules::JsonToCsv($resourcesDir . "LemmaResourceToCSV.txt",
        $resourcesDir . $lemmaCsv,
        $backupDir . date("Ymd_His") . "_" . $lemmaCsv,
        $resourcesDir . $lemmaJson,
        $contentID);

    if($wordLemmaToCSV)
    {
        ContentLemma::updateContentLemmas($resourcesDir . $lemmaCsv, $contentID . "_" . date("Ymd_His"));
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToLemma";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    return true;
}

function updateLemmaRepAfterUpload($resourcesDir, $backupDir, $langTranslationDir, $langTranslationFileName)
{
    $where = "ContentID = :contentID";
    $whereParam = array(":contentID" => $_REQUEST["ContentID"]);
    $finalRawData = ContentLemma::SelectForCSV($where, $whereParam);
    $finalTranslationArray[] = array("EntryInL2","EntryInL1");
    for($i = 0; $i < count($finalRawData); $i++)
    {
        if(!empty($finalRawData[$i]['EntryInL1']))
            $finalTranslationArray[] = array($finalRawData[$i]['EntryInL2'], $finalRawData[$i]['EntryInL1']);
    }

    $finalTranslationFile = "lemmaTranslation.json";
    ExtraModules::BackupFile($resourcesDir . $finalTranslationFile, $backupDir . date("Ymd_His") . "_" . $finalTranslationFile);
    file_put_contents($resourcesDir . $finalTranslationFile, json_encode($finalTranslationArray, JSON_PRETTY_PRINT));

    $lemmaDBToCSV = ExtraModules::JsonToCsv($resourcesDir . "LemmaConvertToCSV.txt",
        $resourcesDir . "lemmaTranslation.csv",
        $backupDir . date("Ymd_His") . "_lemmaTranslation.csv",
        $resourcesDir . $finalTranslationFile,
        $_REQUEST["ContentID"]);

    if($lemmaDBToCSV)
    {
        if(file_exists($langTranslationDir . $langTranslationFileName))
        {
            ExtraModules::MergeUpdateTranslationSpreadsheet($resourcesDir . "LemmaMergeCSVs.txt",
                $langTranslationDir. $langTranslationFileName,
                $backupDir . date("Ymd_His") . "_lemma_" . $langTranslationFileName,
                $resourcesDir . "lemmaTranslation.csv",
                $_REQUEST["ContentID"]);
        }
        else
        {
            copy($resourcesDir . "lemmaTranslation.csv", $langTranslationDir . $langTranslationFileName);
            return true;
        }
    }
    else
    {
        return false;
    }

    return true;
}
//----- Types -----//
function ReadContentTypes($resourcesDir, $backupDir, $contentID)
{
//    $start = microtime(true);

    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $contentID);

    $typesFileJsonData = json_decode(file_get_contents($resourcesDir . 'word_translations_surface_type.json'), true);
    $recordingFileJsonData = json_decode(file_get_contents($resourcesDir . 'ldt_word_recording_full.json'), true);

    $typeArray[] = array("ContentID","TypeOrder","EntryInL1","EntryInL2","Frequency","RecordingFileName");
    $typeExampleArray[] = array("ContentID","TypeOrder","ExampleText");

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Read Type translation and recording json: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    for($i = 0; $i < count($typesFileJsonData); $i++)
    {
        $index = $i + 1;
        $typeArray[$index][0] = $contentID;
        $typeArray[$index][1] = $index;
        $typeArray[$index][2] = $typesFileJsonData[$i][1];
        $typeArray[$index][3] = $typesFileJsonData[$i][0];
        $typeArray[$index][4] = $typesFileJsonData[$i][2];
        $typeArray[$index][5] = "";

        for($k = 0; $k < count($recordingFileJsonData); $k++)
        {
            if($recordingFileJsonData[$k]["text"] ==  $typesFileJsonData[$i][0])
            {
                $typeArray[$index][5] = $recordingFileJsonData[$k]["file"];
                $k = count($recordingFileJsonData);
            }
        }

        for($j = 0; $j < count($typesFileJsonData[$i][3]); $j++)
        {
            $typeExampleArray[] = array($contentID , $index, $typesFileJsonData[$i][3][$j]);
        }
    }

    $typeJson = "word_type.json";
    ExtraModules::BackupFile($resourcesDir . $typeJson, $backupDir . date("Ymd_His") . "_" . $typeJson);
    file_put_contents($resourcesDir . $typeJson, json_encode($typeArray, JSON_PRETTY_PRINT));

    $typeExampleJson = "word_type_ex.json";
    ExtraModules::BackupFile($resourcesDir . $typeExampleJson, $backupDir . date("Ymd_His") . "_" . $typeExampleJson);
    file_put_contents($resourcesDir . $typeExampleJson, json_encode($typeExampleArray, JSON_PRETTY_PRINT));

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Convert type Python jsons to PHP jsons: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    $typeCsv = "word_type.csv";
    $wordTypeToCSV = ExtraModules::JsonToCsv($resourcesDir . "TypeResourceToCSV.txt",
        $resourcesDir . $typeCsv,
        $backupDir . date("Ymd_His") . "_" . $typeCsv,
        $resourcesDir . $typeJson,
        $contentID);

    $typeExampleCsv = "word_type_ex.csv";
    $wordTypeExToCSV = ExtraModules::JsonToCsv($resourcesDir . "TypeExampleResourceToCSV.txt",
        $resourcesDir . $typeExampleCsv,
        $backupDir . date("Ymd_His") . "_" . $typeExampleCsv,
        $resourcesDir . $typeExampleJson,
        $contentID);

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Convert PHP Type jsons to CSV using python: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    if($wordTypeToCSV)
    {
        ContentType::delete($where, $whereParam);
        ContentType::insertContentTypes($resourcesDir . $typeCsv);
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToType";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Put type csv in db: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    if($wordTypeExToCSV)
    {
        ContentTypeExample::delete($where, $whereParam);
        ContentTypeExample::insertContentTypeExamples($resourcesDir . $typeExampleCsv);}
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToTypeExample";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Put Type example csv in db: " . $time_elapsed_secs . "----");
    return true;
}

function loadTypePage()
{
    $contentID = $_REQUEST["contentID"];
    $pageToLoad = $_REQUEST["pageToLoad"];
    $checkOnSubmit = true;
    $editMode = $_REQUEST["mode"];

    $where = " ct.ContentID = :contentID ";
    $whereParam = array(":contentID" => $contentID);
    $info = ContentType::SearchContentType($where, $whereParam, $pageToLoad);

    $where = " ContentID = :contentID ";
    $whereParam = array(":contentID" => $contentID);
    $contentInfo = Content::SearchContent($where, $whereParam);
    $L1Name =  Language::getLanguageName($contentInfo[0]["L1ID"]);
    $L2Name =  Language::getLanguageName($contentInfo[0]["L2ID"]);

    $idIndex = "ContentTypeID";
    $l1Index = "EntryInL1";
    $l2Index = "EntryInL2";
    $example = "examples";

    $l1String = "";

    $tableInfo = "<tr id='translationError'  style='display: none'>
                    <td><p class='ErrorMsg'></p></td>
                  </tr>
                  <tr style='width: 100%'>
                <td>";

    $tableInfo .= "<table class='responstable' style='width: 100%'>";
    $tableInfo .= "<tr><th>" . $L2Name . "</th>";
    $tableInfo .= "<th>" . $L1Name . "</th>";
    $tableInfo .=  "</tr>";
    for($i = 0; $i < min(RowPerPage, count($info)) ; $i++)
    {
        $thisRow = $info[$i];
        $id = $thisRow[$idIndex];
        $valueInL1 = $thisRow[$l1Index];
        $l1String .= $thisRow[$l1Index] . "**";
        $valueInL2 = $thisRow[$l2Index];
        $exampleVal = $thisRow[$example];

        $rowString  = "<tr>";
        $rowString  .= "<input type='hidden' id='typeInfo[" . $i . "][0]' 
                              name='typeInfo[" . $i . "][0]' value='" . $id . "'>";
        $rowString .= "<td title='" . htmlspecialchars($exampleVal, ENT_QUOTES) . "'>" . $valueInL2 . "</td>";
        $rowString .= "<td>
                           <input type='text' name='typeInfo[" . $i . "][1]' class='l1Input'
                            id='typeInfo[" . $i . "][1]' value='". htmlspecialchars($valueInL1, ENT_QUOTES) ."'>
                        </td>";
        $rowString .= "</tr>";
        $tableInfo .= $rowString;
    }
    $tableInfo .= "<input type='hidden' id='l1String' name='l1String' value='" . $l1String . "'>";
    $tableInfo .= "</table></td></tr>";

    $numberOfPages = ContentType::NumberOfPages($contentID);

    $pageNumbersRows = ceil($numberOfPages / 20);
    for($j = 0; $j < $pageNumbersRows; $j++) {
        $tableInfo .= "<tr><td align='center'>";
        $pageNumbersRow = "";
        if ($j == 0)
        {
            $prvPage = $pageToLoad - 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToTypePage(" .$prvPage . "," . $checkOnSubmit . ")'> prv </span>";
        }
        for ($i = 1; $i <= 20; $i++) {
            $spanIndex = ($j * 20) + $i;
            if ($spanIndex <= $numberOfPages) {
                $pageNumbersRow .= "<span class='pageNumber' ";
                if ($spanIndex == $pageToLoad)
                    $pageNumbersRow .= " style='background-color:#008080' ";
                $pageNumbersRow .= " onclick='goToTypePage(" . $spanIndex  . "," . $checkOnSubmit . ")'>" . $spanIndex . "</span>";
            }
        }
        if ($j == $pageNumbersRows - 1)
        {
            $nextPage = $pageToLoad + 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToTypePage(" . $nextPage  . "," . $checkOnSubmit . ")'> nxt </span>";
        }
        $tableInfo .= $pageNumbersRow . "</td></tr>";
    }

    $tableInfo .= "<tr>
                    <td align='center'>";
    if($editMode != 'readOnly')
    {
        $tableInfo .= "<input type='button'  id='SendButton' name='SendButton'
                             value='Save translations' onclick='sendTranslation(\"JustSave\",\"saveType\")'>
                        <input type='button'  id='SendAndCopyButton' name='SendAndCopyButton'
                            value='Save and exit' onclick='sendTranslation(\"SaveAndExit\",\"saveType\")'>";
    }
    $tableInfo .= "<input type='button'  id='ExitButton' name='ExitButton' value='Exit' onclick='exitWithoutSaving()'>";
    $tableInfo .= "</td></tr>";

    echo $tableInfo;
    die();
}

function saveType()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_REQUEST["ContentID"];

    $where = "ContentID = :contentID";
    $whereParam = array(":contentID" => $_REQUEST["ContentID"]);
    $contentResult = Content::SearchContent($where, $whereParam);

    $langDir = LaraContentDir . Language::getLanguageName($contentResult[0]["L2ID"]);
    ExtraModules::CreateDir($langDir,SubDirNames);
    $langTranslationDir = $langDir . "/" . SubDirNames["translations"] . "/";
    $langTranslationFileName = "type_" . Language::getLanguageName($contentResult[0]["L2ID"]) . "_" . Language::getLanguageName($contentResult[0]["L1ID"]) . ".csv";
    $resourcesDir = ContentTmpDirectory . $contentResult[0]["DirName"] . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = ContentTmpDirectory . $contentResult[0]["DirName"]  . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;
    $createBackupDIRRes = ExtraModules::CreateDir($backupDir);
    if (in_array($createBackupDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, $createBackupDIRRes . "CreateResources");
        ExtraModules::KillProcess($resultArray, $createBackupDIRRes . "CreateResources");
    }

    saveTypeInDB($resourcesDir, $backupDir);
    updateTypeRep($resourcesDir, $backupDir, $langTranslationDir, $langTranslationFileName);

    $resultArray[0]["resultMsg"] = "DataIsSavedForItems";
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function saveTypeInDB($resourcesDir, $backupDir)
{
    $typeInfo = $_REQUEST["typeInfo"];
    $contentID = $_REQUEST["ContentID"];
    $insertFileContentArray = array();
    $insertFileContentArray[] = array("ContentTypeID","ContentID","TypeOrder","EntryInL1","EntryInL2","Frequency","RecordingFileName");
    for($i = 0; $i < count($typeInfo); $i++)
    {
        $ContentTypeID = $typeInfo[$i][0];
        $EntryInL1 = $typeInfo[$i][1];
        $insertFileContentArray[] = array($ContentTypeID, $contentID, $i, $EntryInL1, "", "", "");
    }
    $typeUiJson = "word_surface_type_ui.json";
    ExtraModules::BackupFile($resourcesDir . $typeUiJson, $backupDir . date("Ymd_His") . "_" . $typeUiJson);
    file_put_contents($resourcesDir . $typeUiJson, json_encode($insertFileContentArray, JSON_PRETTY_PRINT));

    $typeUiCSV = "word_surface_type_ui.csv";
    $typeUiToCSV = ExtraModules::JsonToCsv($resourcesDir . "TypeFromUiToCSV.txt",
        $resourcesDir . $typeUiCSV,
        $backupDir . date("Ymd_His") . "_" . $typeUiCSV,
        $resourcesDir . $typeUiJson,
        $contentID);

    if($typeUiToCSV)
    {
        ContentType::updateContentTypes($resourcesDir . $typeUiCSV, $contentID . "_" . date("Ymd_His"));
        return true;
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToGenerateCsv";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
}

function updateTypeRep($resourcesDir, $backupDir, $langTranslationDir, $langTranslationFileName)
{
    $where = "ContentID = :contentID";
    $whereParam = array(":contentID" => $_REQUEST["ContentID"]);
    $finalRawData = ContentType::SelectForCSV($where, $whereParam);
    $finalTranslationArray[] = array("EntryInL2","EntryInL1");
    for($i = 0; $i < count($finalRawData); $i++)
    {
        if(!empty($finalRawData[$i]['EntryInL1']))
            $finalTranslationArray[] = array($finalRawData[$i]['EntryInL2'], $finalRawData[$i]['EntryInL1']);
    }

    $finalTranslationFile = "typeTranslation.json";
    ExtraModules::BackupFile($resourcesDir . $finalTranslationFile, $backupDir . date("Ymd_His") . "_" . $finalTranslationFile);
    file_put_contents($resourcesDir . $finalTranslationFile, json_encode($finalTranslationArray, JSON_PRETTY_PRINT));

    $typeDBToCSV = ExtraModules::JsonToCsv($resourcesDir . "typeConvertToCSV.txt",
        $resourcesDir . "typeTranslation.csv",
        $backupDir . date("Ymd_His") . "_typeTranslation.csv",
        $resourcesDir . $finalTranslationFile,
        $_REQUEST["ContentID"]);

    if($typeDBToCSV)
    {
        if(file_exists($langTranslationDir . $langTranslationFileName))
        {
            ExtraModules::MergeUpdateTranslationSpreadsheet($resourcesDir . "TypeMergeCSVs.txt",
                $langTranslationDir. $langTranslationFileName,
                $backupDir . date("Ymd_His") . "_" . $langTranslationFileName,
                $resourcesDir . "typeTranslation.csv",
                $_REQUEST["ContentID"]);
        }
        else
        {
            copy($resourcesDir . "typeTranslation.csv", $langTranslationDir . $langTranslationFileName);
        }
    }
    else
    {
        return false;
    }
    return true;
}

function UploadTypeTranslation()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_REQUEST["ContentID"];

    $resourcesDir = ContentTmpDirectory . $_REQUEST["DirName"] . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = ContentTmpDirectory . $_REQUEST["DirName"] . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;

    if (!ExtraModules::FileExists('UploadTypeTranslation'))
        ExtraModules::KillProcess($resultArray, "typeTranslationFileDoesNotExist");

    if (!ExtraModules::FileExtensionIsValid('UploadTypeTranslation', array('csv')))
        ExtraModules::KillProcess($resultArray, "typeTranslationFileFormatNotValid");

    $file = $_FILES['UploadTypeTranslation'];
    $fileName = "uploaded_word_translations_surface_type.csv";
    ExtraModules::BackupFile($resourcesDir . "uploaded_word_translations_surface_type.csv",
        $backupDir . date("Ymd_His") . "uploaded_word_translations_surface_type.csv");
    if(!ExtraModules::UploadFile($fileName, $resourcesDir, $file))
        ExtraModules::KillProcess($resultArray, "typeTranslationFileNotUploaded");

    $csvFileOnServer = "word_translations_surface_type_offline.csv";
    ExtraModules::MergeUpdateTranslationSpreadsheet($resourcesDir . "OfflineTypeMergeCSVs.txt",
        $resourcesDir. $csvFileOnServer,
        $backupDir . date("Ymd_His") . "_" . $csvFileOnServer,
        $resourcesDir . $fileName,
        $_REQUEST["ContentID"]);

    $jsonFileName = "uploaded_word_translations_surface_type.json";
    $wordTypeToCSV = ExtraModules::CsvToJson($resourcesDir . "typeConvertToJson.txt",
        $resourcesDir . $jsonFileName,
        $backupDir . date("Ymd_His") . "_" . $jsonFileName,
        $resourcesDir . $csvFileOnServer,
        $_REQUEST["ContentID"]);

    ReadUploadedContentTypes($resourcesDir, $backupDir, $_REQUEST["ContentID"]);

    $langDir = LaraContentDir . Language::getLanguageName($_REQUEST["L2ID"]);
    ExtraModules::CreateDir($langDir,SubDirNames);
    $langTranslationDir = $langDir . "/" . SubDirNames["translations"] . "/";
    $langTranslationFileName = "type_" . Language::getLanguageName($_REQUEST["L2ID"]) . "_" . Language::getLanguageName($_REQUEST["L1ID"]) . ".csv";
    updateTypeRep($resourcesDir, $backupDir, $langTranslationDir, $langTranslationFileName);
    $resultArray[0]["resultMsg"] = "DataFromFileIsSavedForItems";

    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function ReadUploadedContentTypes($resourcesDir, $backupDir, $contentID)
{
    $typesFileJsonData = json_decode(file_get_contents($resourcesDir . 'uploaded_word_translations_surface_type.json'), true);

    $typeArray[] = array("ContentTypeID","ContentID","TypeOrder","EntryInL1","EntryInL2","Frequency","RecordingFileName");

    for($i = 1; $i < count($typesFileJsonData); $i++)
    {
        $index = $i;
        $typeArray[$index][0] = $index;
        $typeArray[$index][1] = $contentID;
        $typeArray[$index][2] = $index;
        $typeArray[$index][3] = $typesFileJsonData[$i][1];
        $typeArray[$index][4] = $typesFileJsonData[$i][0];
        $typeArray[$index][5] = 0;
        $typeArray[$index][6] = "";
    }

    $typeJson = "word_type.json";
    ExtraModules::BackupFile($resourcesDir . $typeJson, $backupDir . date("Ymd_His") . "_" . $typeJson);
    file_put_contents($resourcesDir . $typeJson, json_encode($typeArray, JSON_PRETTY_PRINT));

    $typeCsv = "word_type.csv";
    $wordTypeToCSV = ExtraModules::JsonToCsv($resourcesDir . "TypeResourceToCSV.txt",
        $resourcesDir . $typeCsv,
        $backupDir . date("Ymd_His") . "_" . $typeCsv,
        $resourcesDir . $typeJson,
        $contentID);

    if($wordTypeToCSV)
    {
        ContentType::updateContentTypes($resourcesDir . $typeCsv, $contentID . "_" . date("Ymd_His"));
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToType";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    return true;
}
//----- Segments -----//
function ReadContentSegments($resourcesDir, $backupDir, $contentID)
{
//    $start = microtime(true);

    $translationFileJsonData = json_decode(file_get_contents($resourcesDir . 'segment_translations.json'), true);
    $recordingFileJsonData = json_decode(file_get_contents($resourcesDir . 'ldt_segment_recording_full.json'), true);

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Read segment translation and recording json: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    $segmentArray[] = array("ContentID","SegmentInL1","SegmentInL2","SegmentOrder","RecordingFileName");

    for($i = 0; $i < count($translationFileJsonData); $i++)
    {
        $index = $i + 1;
        $segmentArray[$index][0] = $contentID;
        $segmentArray[$index][1] = $translationFileJsonData[$i][1];
        $segmentArray[$index][2] = $translationFileJsonData[$i][0];
        $segmentArray[$index][3] = $index;
        $segmentArray[$index][4] = "";

        for($k = 0; $k < count($recordingFileJsonData); $k++)
        {
            if($recordingFileJsonData[$k]["text"] ==  $translationFileJsonData[$i][0])
            {
                $segmentArray[$index][4] = $recordingFileJsonData[$k]["file"];
                $k = count($recordingFileJsonData);
            }
        }
    }

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Convert segment Python jsons to PHP jsons: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    $segmentJson = "segment_translations_processed.json";
    ExtraModules::BackupFile($resourcesDir . $segmentJson, $backupDir . date("Ymd_His") . "_" . $segmentJson);
    file_put_contents($resourcesDir . $segmentJson, json_encode($segmentArray, JSON_PRETTY_PRINT));

    $segmentCsv = "segment_translations_processed.csv";
    $segmentToCSV = ExtraModules::JsonToCsv($resourcesDir . "SegmentResourceToCSV.txt",
        $resourcesDir . $segmentCsv,
        $backupDir . date("Ymd_His") . "_" . $segmentCsv,
        $resourcesDir . $segmentJson,
        $contentID);

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Convert PHP Type jsons to CSV using python: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    if($segmentToCSV)
    {
        $where = " ContentID = :contentID";
        $whereParam = array(":contentID" => $contentID);
        ContentSegment::delete($where, $whereParam);
        ContentSegment::insertContentSegments($resourcesDir . $segmentCsv);
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToSegment";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Put Type example csv in db: " . $time_elapsed_secs . "----");
    return true;
}

function loadSegmentPage()
{
    $contentID = $_REQUEST["contentID"];
    $pageToLoad = $_REQUEST["pageToLoad"];
    $checkOnSubmit = true;
    $editMode = $_REQUEST["mode"];

    $where = " ContentID = :contentID ";
    $whereParam = array(":contentID" => $contentID);
    $info = ContentSegment::SearchContentSegment($where, $whereParam, $pageToLoad);

    $contentInfo = Content::SearchContent($where, $whereParam);
    $L1Name =  Language::getLanguageName($contentInfo[0]["L1ID"]);
    $L2Name =  Language::getLanguageName($contentInfo[0]["L2ID"]);

    $idIndex = "ContentSegmentID";
    $l1Index = "SegmentInL1";
    $l2Index = "SegmentInL2";

    $l1String = "";

    $tableInfo = "<tr id='translationError'  style='display: none'>
                    <td><p class='ErrorMsg'></p></td>
                  </tr>
                  <tr style='width: 100%'>
                <td>";

    $tableInfo .= "<table class='responstable' style='width: 100%'>";
    $tableInfo .= "<tr><th>Translate segments from " . ucfirst($L2Name) . " to " . ucfirst($L1Name) . "</th>" .  "</tr>";
    for($i = 0; $i < min(RowPerPage, count($info)) ; $i++)
    {
        $thisRow = $info[$i];
        $id = $thisRow[$idIndex];
        $valueInL1 = $thisRow[$l1Index];
        $l1String .= $thisRow[$l1Index] . "**";
        $valueInL2 = $thisRow[$l2Index];

        $rowString  = "<tr>";
        $rowString  .= "<input type='hidden' id='segmentInfo[" . $i . "][0]' 
                              name='segmentInfo[" . $i . "][0]' value='" . $id . "'>";
        $rowString .= "<td style='text-align: left'>" . $valueInL2 . "</td></tr>";
        $rowString .= "<tr><td>
                           <input type='text' name='segmentInfo[" . $i . "][1]'  class='l1Input'
                                id='segmentInfo[" . $i . "][1]' value='". htmlspecialchars($valueInL1, ENT_QUOTES) ."'>
                            </td>";
        $rowString .= "</tr>";
        $tableInfo .= $rowString;
    }
    $tableInfo .= "<input type='hidden' id='l1String' name='l1String' value='" . $l1String . "'>";
    $tableInfo .= "</table></td></tr>";

    $numberOfPages = ContentSegment::NumberOfPages($contentID);

    $pageNumbersRows = ceil($numberOfPages / 20);
    for($j = 0; $j < $pageNumbersRows; $j++) {
        $tableInfo .= "<tr><td align='center'>";
        $pageNumbersRow = "";
        if ($j == 0)
        {
            $prvPage = $pageToLoad - 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToSegmentPage(" .$prvPage . "," . $checkOnSubmit . ")'> prv </span>";
        }
        for ($i = 1; $i <= 20; $i++) {
            $spanIndex = ($j * 20) + $i;
            if ($spanIndex <= $numberOfPages) {
                $pageNumbersRow .= "<span class='pageNumber' ";
                if ($spanIndex == $pageToLoad)
                    $pageNumbersRow .= " style='background-color:#008080' ";
                $pageNumbersRow .= " onclick='goToSegmentPage(" . $spanIndex . "," . $checkOnSubmit . ")'>" . $spanIndex . "</span>";
            }
        }
        if ($j == $pageNumbersRows - 1)
        {
            $nextPage = $pageToLoad + 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToSegmentPage(" . $nextPage . "," . $checkOnSubmit . ")'> nxt </span>";
        }
        $tableInfo .= $pageNumbersRow . "</td></tr>";
    }

    $tableInfo .= "<tr>
                    <td align='center'>";
    if($editMode != 'readOnly')
    {
        $tableInfo .= "<input type='button'  id='SendButton' name='SendButton'
                               value='Save translations' onclick='sendTranslation(\"JustSave\",\"saveSegment\")'>
                        <input type='button'  id='SendAndCopyButton' name='SendAndCopyButton'
                               value='Save and exit' onclick='sendTranslation(\"SaveAndExit\",\"saveSegment\")'>";
    }
    $tableInfo .= "<input type='button'  id='ExitButton' name='ExitButton' value='Exit' onclick='exitWithoutSaving()'>";
    $tableInfo .= "</td></tr>";

    echo $tableInfo;
    die();
}

function saveSegment()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_REQUEST["ContentID"];

    $where = "ContentID = :contentID";
    $whereParam = array(":contentID" => $_REQUEST["ContentID"]);
    $contentResult = Content::SearchContent($where, $whereParam);

    $langTranslationDir = LaraContentDir . $contentResult[0]["DirName"] . "/" . SubDirNames["translations"] . "/";
    $langTranslationFileName = Language::getLanguageName($contentResult[0]["L2ID"]) . "_" . Language::getLanguageName($contentResult[0]["L1ID"]) . ".csv";
    $resourcesDir = ContentTmpDirectory . $contentResult[0]["DirName"] . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = ContentTmpDirectory . $contentResult[0]["DirName"]  . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;
    $createBackupDIRRes = ExtraModules::CreateDir($backupDir);
    if (in_array($createBackupDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, $createBackupDIRRes . "CreateResources");
        ExtraModules::KillProcess($resultArray, $createBackupDIRRes . "CreateResources");
    }

    savSegmentInDB($resourcesDir, $backupDir);
    updateSegmentRep($resourcesDir, $backupDir, $langTranslationDir, $langTranslationFileName);

    $resultArray[0]["resultMsg"] = "DataIsSavedForItems";
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function savSegmentInDB($resourcesDir, $backupDir)
{
    $segmentInfo = $_REQUEST["segmentInfo"];
    $contentID = $_REQUEST["ContentID"];

    $insertFileContentArray[] = array("ContentSegmentID","ContentID","SegmentInL1","SegmentInL2","SegmentOrder","RecordingFileName");
    for($i = 0; $i < count($segmentInfo); $i++)
    {
        $ContentSegmentID = $segmentInfo[$i][0];
        $SegmentInL1 = $segmentInfo[$i][1];
        $insertFileContentArray[] = array($ContentSegmentID, $contentID, $SegmentInL1, "", $i, "");
    }
    $segmentUiJson = "segment_translations_ui.json";
    ExtraModules::BackupFile($resourcesDir . $segmentUiJson, $backupDir . date("Ymd_His") . "_" . $segmentUiJson);
    file_put_contents($resourcesDir . $segmentUiJson, json_encode($insertFileContentArray, JSON_PRETTY_PRINT));

    $segmentUiCsv = "segment_translations_ui.csv";
    $segmentUiToCSV = ExtraModules::JsonToCsv($resourcesDir . "SegmentFromUiToCSV.txt",
        $resourcesDir . $segmentUiCsv,
        $backupDir . date("Ymd_His") . "_" . $segmentUiCsv,
        $resourcesDir . $segmentUiJson,
        $contentID);

    if($segmentUiToCSV)
    {
        ContentSegment::updateContentSegments($resourcesDir . $segmentUiCsv, $contentID . "_" . date("Ymd_His"));
        return true;
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToGenerateCsv";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
}

function updateSegmentRep($resourcesDir, $backupDir, $langTranslationDir, $langTranslationFileName)
{
    $where = "ContentID = :contentID";
    $whereParam = array(":contentID" => $_REQUEST["ContentID"]);
    $finalRawData = ContentSegment::SearchContentSegment($where, $whereParam);
    $finalTranslationArray[] = array("SegmentInL1","SegmentInL2");
    for($i = 0; $i < count($finalRawData); $i++)
    {
        if(!empty($finalRawData[$i]['SegmentInL1']))
            $finalTranslationArray[] = array($finalRawData[$i]['SegmentInL2'], $finalRawData[$i]['SegmentInL1']);
    }

    $finalTranslationFile = "segmentTranslation.json";
    ExtraModules::BackupFile($resourcesDir . $finalTranslationFile, $backupDir . date("Ymd_His") . "_" . $finalTranslationFile);
    file_put_contents($resourcesDir . $finalTranslationFile, json_encode($finalTranslationArray, JSON_PRETTY_PRINT));

    $segmentDBToCSV = ExtraModules::JsonToCsv($resourcesDir . "segmentConvertToCSV.txt",
        $resourcesDir . "segmentTranslation.csv",
        $backupDir . date("Ymd_His") . "_segmentTranslation.csv",
        $resourcesDir . $finalTranslationFile,
        $_REQUEST["ContentID"]);

    if($segmentDBToCSV)
    {
        copy($resourcesDir . "segmentTranslation.csv", $langTranslationDir . $langTranslationFileName);
    }
    else
    {
        return false;
    }
    return true;
}

function UploadSegmentTranslation()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_REQUEST["ContentID"];

    $resourcesDir = ContentTmpDirectory . $_REQUEST["DirName"] . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = ContentTmpDirectory . $_REQUEST["DirName"] . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;

    if (!ExtraModules::FileExists('UploadSegmentTranslation'))
        ExtraModules::KillProcess($resultArray, "segmentTranslationFileDoesNotExist");

    if (!ExtraModules::FileExtensionIsValid('UploadSegmentTranslation', array('csv')))
        ExtraModules::KillProcess($resultArray, "segmentTranslationFileFormatNotValid");

    $file = $_FILES['UploadSegmentTranslation'];
    $fileName = "uploaded_segment_translations.csv";
    ExtraModules::BackupFile($resourcesDir . "uploaded_segment_translations.csv",
        $backupDir . date("Ymd_His") . "uploaded_segment_translations.csv");
    if(!ExtraModules::UploadFile($fileName, $resourcesDir, $file))
        ExtraModules::KillProcess($resultArray, "segmentTranslationFileNotUploaded");

    $csvFileOnServer = "segment_translations.csv";
    ExtraModules::MergeUpdateTranslationSpreadsheet($resourcesDir . "OfflineSegmentMergeCSVs.txt",
        $resourcesDir. $csvFileOnServer,
        $backupDir . date("Ymd_His") . "_" . $csvFileOnServer,
        $resourcesDir . $fileName,
        $_REQUEST["ContentID"]);

    $jsonFileName = "uploaded_segment_translations.json";
    $segmentToCSV = ExtraModules::CsvToJson($resourcesDir . "segmentConvertToJson.txt",
        $resourcesDir . $jsonFileName,
        $backupDir . date("Ymd_His") . "_" . $jsonFileName,
        $resourcesDir . $csvFileOnServer,
        $_REQUEST["ContentID"]);

    ReadUploadedContentSegments($resourcesDir, $backupDir, $_REQUEST["ContentID"]);

    $langTranslationDir = LaraContentDir . $_REQUEST["DirName"] . "/" . SubDirNames["translations"] . "/";
    $langTranslationFileName = Language::getLanguageName($_REQUEST["L2ID"]) . "_" . Language::getLanguageName($_REQUEST["L1ID"]) . ".csv";
    updateSegmentRep($resourcesDir, $backupDir, $langTranslationDir, $langTranslationFileName);
    $resultArray[0]["resultMsg"] = "DataFromFileIsSavedForItems";

    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function ReadUploadedContentSegments($resourcesDir, $backupDir, $contentID)
{
    $translationFileJsonData = json_decode(file_get_contents($resourcesDir . 'uploaded_segment_translations.json'), true);

    $segmentArray[] = array("ContentSegmentID","ContentID","SegmentInL1","SegmentInL2","SegmentOrder","RecordingFileName");

    for($i = 1; $i < count($translationFileJsonData); $i++)
    {
        $index = $i;
        $segmentArray[$index][0] = $index;
        $segmentArray[$index][1] = $contentID;
        $segmentArray[$index][2] = $translationFileJsonData[$i][1];
        $segmentArray[$index][3] = $translationFileJsonData[$i][0];
        $segmentArray[$index][4] = $index;
        $segmentArray[$index][5] = "";
    }

    $segmentJson = "segment_translations_processed.json";
    ExtraModules::BackupFile($resourcesDir . $segmentJson, $backupDir . date("Ymd_His") . "_" . $segmentJson);
    file_put_contents($resourcesDir . $segmentJson, json_encode($segmentArray, JSON_PRETTY_PRINT));

    $segmentCsv = "segment_translations_processed.csv";
    $segmentToCSV = ExtraModules::JsonToCsv($resourcesDir . "SegmentResourceToCSV.txt",
        $resourcesDir . $segmentCsv,
        $backupDir . date("Ymd_His") . "_" . $segmentCsv,
        $resourcesDir . $segmentJson,
        $contentID);

    if($segmentToCSV)
    {
        ContentSegment::updateContentSegments($resourcesDir . $segmentCsv, $contentID . "_" . date("Ymd_His"));
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToSegment";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    return true;
}

//----- Tokens -----//
function ReadContentTokens($resourcesDir, $backupDir, $contentID, $userUpload = false)
{
//    $start = microtime(true);

    if($userUpload)
    {
        $jsonToRead = "uploaded_word_translations_tokens.json";
        $tokenArray[] = array("ContentTokenID","ContentID","SegmentOrder","SectionType","OrderInSection","EntryText");
    }
    else
    {
        $jsonToRead = "word_translations_tokens.json";
        $tokenArray[] = array("ContentID","SegmentOrder","SectionType","OrderInSection","EntryText");
    }


//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Read token translation and recording json: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    $tokenFileJsonData = json_decode(file_get_contents($resourcesDir . $jsonToRead), true);
    $dataType = array('token','type','segment');
    $fakeID = 1;

    for($i = 0; $i < count($tokenFileJsonData); $i++)
    {
        for($j = 0; $j < 3; $j++)
        {
            for($k = 0; $k < count($tokenFileJsonData[$i][$j]); $k++)
            {
                $segmentOrder = $i + 1;
                $orderInSection = $k + 1;
                if($userUpload)
                    $tokenArray[] = array($fakeID++,$contentID, $segmentOrder, $dataType[$j], $orderInSection, $tokenFileJsonData[$i][$j][$k]);
                else
                    $tokenArray[] = array($contentID, $segmentOrder, $dataType[$j], $orderInSection, $tokenFileJsonData[$i][$j][$k]);
            }
        }
    }
    $tokenJson = "word_translations_tokens_processed.json";
    ExtraModules::BackupFile($resourcesDir . $tokenJson, $backupDir . date("Ymd_His") . "_" . $tokenJson);
    file_put_contents($resourcesDir . $tokenJson, json_encode($tokenArray, JSON_PRETTY_PRINT));

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Convert token Python jsons to PHP jsons: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    $tokenCsv = "word_translations_tokens_processed.csv";
    $tokenToCSV = ExtraModules::JsonToCsv($resourcesDir . "TokenResourceToCSV.txt",
        $resourcesDir . $tokenCsv,
        $backupDir . date("Ymd_His") . "_" . $tokenCsv,
        $resourcesDir . $tokenJson,
        $contentID);

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Convert PHP Token jsons to CSV using python: " . $time_elapsed_secs . "----");
//    $start = microtime(true);

    if($tokenToCSV)
    {
        if($userUpload)
        {
            ContentToken::updateContentTokens($resourcesDir . $tokenCsv, $contentID . "_" . date("Ymd_His"));
        }
        else
        {
            $where = " ContentID = :contentID";
            $whereParam = array(":contentID" => $contentID);
            ContentToken::delete($where, $whereParam);
            ContentToken::insertContentTokens($resourcesDir . $tokenCsv);
        }
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToToken";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }

//    $time_elapsed_secs = microtime(true) - $start;
//    echo("Put token example csv in db: " . $time_elapsed_secs . "----");
    return true;
}

function loadTokenPage()
{
    $contentID = $_REQUEST["contentID"];
    $pageToLoad = $_REQUEST["pageToLoad"];
    $editMode = $_REQUEST["mode"];

    $segStart = (($pageToLoad - 1) * 5) + 1;
    $segEnd = (($pageToLoad - 1) * 5) + 5;
    $where = " ContentID = :contentID and SegmentOrder between :segStart and :segEnd ";
    $whereParam = array(":contentID" => $contentID, ":segStart" => $segStart, ":segEnd" => $segEnd);
    $tokenInfo = ContentToken::SearchContentToken($where, $whereParam);
    $checkOnSubmit = true;

    $l1String = "";

    $tableInfo = "<input type='hidden' id='PageNumber' name='PageNumber' value='" . $pageToLoad . "'>
                  <tr id='translationError'  style='display: none'>
                    <td><p class='ErrorMsg'></p></td>
                  </tr>
                  <tr style='width: 100%'>
                    <td>";

    $tableInfo .= "<table class='responstable' style='width: 100%'>";

    for($i = $segStart; $i <= $segEnd; $i++)
    {
		$tdCountFull = max(count($tokenInfo[$i][1]), count($tokenInfo[$i][2]), count($tokenInfo[$i][3]));
		// Use short lines because alignment is not working with the middle line where values get filled in
		$maxLineLength = 8;
		$tdSubSegmentsCount = intdiv($tdCountFull, $maxLineLength);
		// k0 counts the subsegments, if we've had to split a segment into several pieces because it was too long. Start at zero.
		for($k0 = 0; $k0 <= $tdSubSegmentsCount; $k0++)
		{
			$producedSubSegment = "no";
			for($j = 1; $j <= 3; $j++)
			{
				$tableInfo .= "<tr>";
				$CountPreviousSubsegments = $k0 * $maxLineLength;
				if ($k0 < $tdSubSegmentsCount)
					// We are not on the last subsegment
					$tdCountSub = $maxLineLength;
				elseif($j == 3)
					$tdCountSub = count($tokenInfo[$i][3]) - $CountPreviousSubsegments;
				else
					$tdCountSub = max(count($tokenInfo[$i][1]), count($tokenInfo[$i][2])) - $CountPreviousSubsegments;
				// $k1 counts the current segment. Start at zero
				for($k1 = 0; $k1 <= $tdCountSub - 1; $k1++)
				{
					// $k0 and $k1 start at zero, but $k needs to start at 1, so add 1
					$k = $CountPreviousSubsegments + $k1 + 1;
					$tableInfo .= "<td>";
					if($j == 2)
					{
						$l1String .= $tokenInfo[$i][$j][$k]["EntryText"] . "**";
						$tableInfo .= "<input type='hidden' id='tokenInfo[" . $i . "][" . $k . "][0]' 
														  name='tokenInfo[" . $i . "][" . $k . "][0]' 
														  value='" . $i . "@@" . $k . "@@" .
							$tokenInfo[$i][$j][$k]["ContentTokenID"] . "'>";

						$tableInfo .= "<input type='text' name='tokenInfo[" . $i . "][" . $k . "][1]' class='l1Input'
														id='tokenInfo[" . $i . "][" . $k . "][1]' 
														value='". htmlspecialchars($tokenInfo[$i][$j][$k]["EntryText"], ENT_QUOTES) ."'>";
					}
					else
					{
						$dataToPrint = $tokenInfo[$i][$j][$k]["EntryText"];
						if(strpos($dataToPrint,"mwe__") !== false)
							$dataToPrint = "<span style='color: red'>" . str_replace("mwe__", '',$dataToPrint ) . "</span>";
						$tableInfo .= $dataToPrint;
					}
					$tableInfo .= "</td>";
					$producedSubSegment = "yes";
				}
				$tableInfo .= "</tr>";
			}
			// Add a horizontal rule after a non-empty group of three lines 
			if ( $producedSubSegment == "yes" )
				$tableInfo .= "<tr><td colspan=\"" . $maxLineLength . "\"><hr></td></tr>";
		}
    }
    $tableInfo .= "<input type='hidden' id='l1String' name='l1String' value='" . $l1String . "'>";
    $tableInfo .= "</table></td></tr>";

    $numberOfPages = ContentToken::NumberOfPages($contentID);

    $pageNumbersRows = ceil($numberOfPages / 20);
    for($j = 0; $j < $pageNumbersRows; $j++) {
        $tableInfo .= "<tr><td align='center'>";
        $pageNumbersRow = "";
        if ($j == 0)
        {
            $prvPage = $pageToLoad - 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToTokenPage(" .$prvPage . "," . $checkOnSubmit . ")'> prv </span>";
        }
        for ($i = 1; $i <= 20; $i++) {
            $spanIndex = ($j * 20) + $i;
            if ($spanIndex <= $numberOfPages) {
                $pageNumbersRow .= "<span class='pageNumber' ";
                if ($spanIndex == $pageToLoad)
                    $pageNumbersRow .= " style='background-color:#008080' ";
                $pageNumbersRow .= " onclick='goToTokenPage(" . $spanIndex . "," . $checkOnSubmit . ")'>" . $spanIndex . "</span>";
            }
        }
        if ($j == $pageNumbersRows - 1)
        {
            $nextPage = $pageToLoad + 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToTokenPage(" . $nextPage . "," . $checkOnSubmit . ")'> nxt </span>";
        }
        $tableInfo .= $pageNumbersRow . "</td></tr>";
    }

    $tableInfo .= "<tr>
                    <td align='center'>";
    if($editMode != 'readOnly')
    {
        $tableInfo .= "<input type='button'  id='SendButton' name='SendButton'
                               value='Save translations' onclick='sendTranslation(\"JustSave\",\"saveToken\")'>
                        <input type='button'  id='SendAndCopyButton' name='SendAndCopyButton'
                               value='Save and exit' onclick='sendTranslation(\"SaveAndExit\",\"saveToken\")'>";
    }
    $tableInfo .= "<input type='button'  id='ExitButton' name='ExitButton' value='Exit' onclick='exitWithoutSaving()'>";
    $tableInfo .= "</td></tr>";

    echo $tableInfo;
    die();
}

function saveToken(){

    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_REQUEST["ContentID"];

    $where = "ContentID = :contentID";
    $whereParam = array(":contentID" => $_REQUEST["ContentID"]);
    $contentResult = Content::SearchContent($where, $whereParam);

    $langTranslationDir = LaraContentDir . $contentResult[0]["DirName"] . "/" . SubDirNames["translations"] . "/";
    $langTranslationFileName = "token_" . Language::getLanguageName($contentResult[0]["L2ID"]) . "_" . Language::getLanguageName($contentResult[0]["L1ID"]) . ".csv";
    $resourcesDir = ContentTmpDirectory . $contentResult[0]["DirName"] . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = ContentTmpDirectory . $contentResult[0]["DirName"]  . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;
    $createBackupDIRRes = ExtraModules::CreateDir($backupDir);
    if (in_array($createBackupDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, $createBackupDIRRes . "CreateResources");
        ExtraModules::KillProcess($resultArray, $createBackupDIRRes . "CreateResources");
    }

    saveTokenInDB($resourcesDir, $backupDir);
    updateTokenRep($resourcesDir, $backupDir, $langTranslationDir, $langTranslationFileName);

    $resultArray[0]["resultMsg"] = "DataIsSavedForItems";
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);

}

function saveTokenInDB($resourcesDir, $backupDir)
{
    $updateFileContentArray[] = array("ContentTokenID","ContentID","SegmentOrder","SectionType","OrderInSection","EntryText");
    $insertFileContentArray[] = array("ContentID","SegmentOrder","SectionType","OrderInSection","EntryText");

    $tokenInfo = $_REQUEST["tokenInfo"];
    $contentID = $_REQUEST["ContentID"];
    $pageNumber = $_REQUEST["PageNumber"];
    $segStart = (($pageNumber - 1) * 5) + 1;
    $segEnd = (($pageNumber - 1) * 5) + 5;

    for($i = $segStart; $i <= $segEnd; $i++)
    {
        for($j = 1; $j <= count($tokenInfo[$i]); $j++)
        {
            $rowInfo = explode("@@", $tokenInfo[$i][$j][0]);
            $segmentOrder =  $rowInfo[0];
            $orderInSection =  $rowInfo[1];
            $contentTokenID =  $rowInfo[2];
            $entryText = $tokenInfo[$i][$j][1];
            $sectionType = "type";

            if(!empty($contentTokenID))
            {
                $updateFileContentArray[] = array($contentTokenID, $contentID, $segmentOrder,$sectionType, $orderInSection, $entryText);
            }
            else if(!empty($entryText))
            {
                $insertFileContentArray[] = array($contentID, $segmentOrder,$sectionType, $orderInSection, $entryText);
            }
        }
    }

    $uTokenUiJson = "word_translations_tokens_ui_update.json";
    ExtraModules::BackupFile($resourcesDir . $uTokenUiJson, $backupDir . date("Ymd_His") . "_" . $uTokenUiJson);
    file_put_contents($resourcesDir . $uTokenUiJson, json_encode($updateFileContentArray, JSON_PRETTY_PRINT));

    $iTokenUiJson = "word_translations_tokens_ui_insert.json";
    ExtraModules::BackupFile($resourcesDir . $iTokenUiJson, $backupDir . date("Ymd_His") . "_" . $iTokenUiJson);
    file_put_contents($resourcesDir . $iTokenUiJson, json_encode($insertFileContentArray, JSON_PRETTY_PRINT));

    $uTokenUiCsv = "word_translations_tokens_ui_update.csv";
    $uTokenUiToCSV = ExtraModules::JsonToCsv($resourcesDir . "uTokenFromUiToCSV.txt",
        $resourcesDir . $uTokenUiCsv,
        $backupDir . date("Ymd_His") . "_" . $uTokenUiCsv,
        $resourcesDir . $uTokenUiJson,
        $contentID);

    if($uTokenUiToCSV)
    {
        ContentToken::updateContentTokens($resourcesDir . $uTokenUiCsv, $contentID . "_" . date("Ymd_His"));
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToGenerateCsv";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }

    $iTokenUiCsv = "word_translations_tokens_ui_insert.csv";

    $iTokenUiToCSV = ExtraModules::JsonToCsv($resourcesDir . "iTokenFromUiToCSV.txt",
        $resourcesDir . $iTokenUiCsv,
        $backupDir . date("Ymd_His") . "_" . $iTokenUiCsv,
        $resourcesDir . $iTokenUiJson,
        $contentID);

    if($iTokenUiToCSV)
    {
        ContentToken::insertContentTokens($resourcesDir . $iTokenUiCsv);
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToGenerateCsv";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    return true;
}

function updateTokenRep($resourcesDir, $backupDir, $langTranslationDir, $langTranslationFileName)
{
    $where = "ContentID = :contentID";
    $whereParam = array(":contentID" => $_REQUEST["ContentID"]);
    $finalRawData = ContentToken::SearchContentToken($where, $whereParam);
    $finalTranslationArray = array();

    for($i = 1; $i <= count($finalRawData); $i++)
    {
        $middleTranslationArray = array();
        for($j = 1; $j <= 3; $j++)
        {
            $tdCount = max(count($finalRawData[$i][1]), count($finalRawData[$i][2]));
            $innerTranslationArray = array();
            for ($k = 1; $k <= $tdCount; $k++)
            {
                if(!empty($finalRawData[$i][$j][$k]['EntryText']))
                    $innerTranslationArray[] = $finalRawData[$i][$j][$k]['EntryText'];
                else
                    $innerTranslationArray[] = " ";
            }
            $middleTranslationArray[] = $innerTranslationArray;
        }
        $finalTranslationArray[] = $middleTranslationArray;
    }

    $finalTranslationFile = "tokenTranslation.json";
    ExtraModules::BackupFile($resourcesDir . $finalTranslationFile, $backupDir . date("Ymd_His") . "_" . $finalTranslationFile);
    file_put_contents($resourcesDir . $finalTranslationFile, json_encode($finalTranslationArray, JSON_PRETTY_PRINT));

    $bashFile = $resourcesDir . "tokenConvertToCSV.txt";
    $fp = fopen( $bashFile, "w");
    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py word_token_json_to_csv  " .
        $resourcesDir . "tokenTranslation.json " . $resourcesDir. "tokenTranslation.csv 2>&1";
    fwrite($fp, $command);
    ExtraModules::BackupFile($resourcesDir . "tokenTranslation.csv", $backupDir . date("Ymd_His") . "_tokenTranslation.csv");
    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $_REQUEST["ContentID"], ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $_REQUEST["ContentID"], ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") === false)
    {
        ExtraModules::BackupFile($langTranslationDir . $langTranslationFileName,
            $backupDir . date("Ymd_His") . $langTranslationFileName);
        copy($resourcesDir. "tokenTranslation.csv", $langTranslationDir . $langTranslationFileName);
    }
    else
    {
        return false;
    }
}

function UploadTokenTranslation()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_REQUEST["ContentID"];

    $resourcesDir = ContentTmpDirectory . $_REQUEST["DirName"] . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = ContentTmpDirectory . $_REQUEST["DirName"] . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;

    if (!ExtraModules::FileExists('UploadTokenTranslation'))
        ExtraModules::KillProcess($resultArray, "tokenTranslationFileDoesNotExist");

    if (!ExtraModules::FileExtensionIsValid('UploadTokenTranslation', array('csv')))
        ExtraModules::KillProcess($resultArray, "tokenTranslationFileFormatNotValid");

    $file = $_FILES['UploadTokenTranslation'];
    $fileName = "uploaded_word_translations_tokens.csv";
    ExtraModules::BackupFile($resourcesDir . "uploaded_word_translations_tokens.csv",
                          $backupDir . date("Ymd_His") . "_uploaded_word_translations_tokens.csv");
    if(!ExtraModules::UploadFile($fileName, $resourcesDir, $file))
        ExtraModules::KillProcess($resultArray, "tokenTranslationFileNotUploaded");

    $bashFile = $resourcesDir . "tokenConvertToJson.txt";
    $fp = fopen( $bashFile, "w");
    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py word_token_csv_to_json " .
        $resourcesDir . "uploaded_word_translations_tokens.csv " . $resourcesDir. "uploaded_word_translations_tokens.json 2>&1";
    fwrite($fp, $command);
    ExtraModules::BackupFile($resourcesDir . "uploaded_word_translations_tokens.json",
        $backupDir . date("Ymd_His") . "_uploaded_word_translations_tokens.json");
    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $_REQUEST["ContentID"], ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $_REQUEST["ContentID"], ContentRelatedPage, $LogID);

    ReadContentTokens($resourcesDir, $backupDir, $_REQUEST["ContentID"], true);

    $langTranslationDir = LaraContentDir . $_REQUEST["DirName"] . "/" . SubDirNames["translations"] . "/";
    $langTranslationFileName = "token_" . Language::getLanguageName($_REQUEST["L2ID"]) . "_" . Language::getLanguageName($_REQUEST["L1ID"]) . ".csv";
    updateTokenRep($resourcesDir, $backupDir, $langTranslationDir, $langTranslationFileName);
    $resultArray[0]["resultMsg"] = "DataFromFileIsSavedForItems";

    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

//----- Raw -----//
function ReadRawData($resourcesDir, $backupDir, $contentID)
{
    if(!file_exists($resourcesDir . 'split.json'))
    {
        if(!file_exists($resourcesDir . 'split.txt'))
            return true;
        else
            rename($resourcesDir . 'split.txt', $resourcesDir . 'split.json');
    }

    $splitFileJsonData = json_decode(file_get_contents($resourcesDir . 'split.json'), true);

    $segmentArray[] = array("ContentID","PageNo","SegmentNo","RawSegment","ProcessedSegment");
    $particleArray[] = array("ContentID","PageNo","SegmentNo","ParticleNo","Particle","ParticleRoot");

    $segmentIndex = 1;
    $particleIndex = 1;

    for($i = 0; $i < count($splitFileJsonData); $i++) {

        $pageNo = $splitFileJsonData[$i][0]["page"];
        $segmentInfo = $splitFileJsonData[$i][1];
        for ($j = 0; $j < count($segmentInfo); $j++) {
            $segmentNo = $j + 1;
            $segmentArray[$segmentIndex][0] = $contentID;
            $segmentArray[$segmentIndex][1] = $pageNo;
            $segmentArray[$segmentIndex][2] = $segmentNo;
            $segmentArray[$segmentIndex][3] = $segmentInfo[$j][0];
            $segmentArray[$segmentIndex][4] = $segmentInfo[$j][1];
            $particleInfo = $segmentInfo[$j][2];
            for ($k = 0; $k < count($particleInfo); $k++) {
                $particleNo = $k + 1;
                $particleArray[$particleIndex][0] = $contentID;
                $particleArray[$particleIndex][1] = $pageNo;
                $particleArray[$particleIndex][2] = $segmentNo;
                $particleArray[$particleIndex][3] = $particleNo;
                $particleArray[$particleIndex][4] = $particleInfo[$k][0];
                $particleArray[$particleIndex][5] = $particleInfo[$k][1];
                $particleIndex++;
            }
            $segmentIndex++;
        }
    }

    //put segment array in json
    $rawSegmentJson = "rawSegment.json";
    ExtraModules::BackupFile($resourcesDir . $rawSegmentJson, $backupDir . date("Ymd_His") . "_" . $rawSegmentJson);
    file_put_contents($resourcesDir . $rawSegmentJson, json_encode($segmentArray, JSON_PRETTY_PRINT));

    //put particle array in json
    $rawParticleJson = "rawParticle.json";
    ExtraModules::BackupFile($resourcesDir . $rawParticleJson, $backupDir . date("Ymd_His") . "_" . $rawParticleJson);
    file_put_contents($resourcesDir . $rawParticleJson, json_encode($particleArray, JSON_PRETTY_PRINT));

    //put segment json in csv
    $rawSegmentCsv = "rawSegment.csv";
    $segToCSV = ExtraModules::JsonToCsv($resourcesDir . "rawSegment.txt",
        $resourcesDir . $rawSegmentCsv,
        $backupDir . date("Ymd_His") . "_" . $rawSegmentCsv,
        $resourcesDir . $rawSegmentJson,
        $contentID);

    //put particle json in csv
    $rawParticleCsv = "rawParticle.csv";
    $parToCSV = ExtraModules::JsonToCsv($resourcesDir . "rawParticle.txt",
        $resourcesDir . $rawParticleCsv,
        $backupDir . date("Ymd_His") . "_" . $rawParticleCsv,
        $resourcesDir . $rawParticleJson,
        $contentID);



    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $contentID);

    //put segment csv in table
    if($segToCSV)
    {
        RawContentSegment::delete($where, $whereParam);
        RawContentSegment::insertRawContentSegment($resourcesDir . $rawSegmentCsv);
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToRawSegment";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }

    //put particle csv in table
    if($parToCSV)
    {
        RawContentParticle::delete($where, $whereParam);
        RawContentParticle::insertRawContentParticle($resourcesDir . $rawParticleCsv);
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToRawParticle";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    return true;
}
