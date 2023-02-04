<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 6/6/2019
 * Time: 05:45 PM
 */


require_once '../Config.php';
require_once '../class/Language.class.php';
require_once '../data/Content.data.php';
require_once '../class/Content.class.php';
require_once '../class/ContentMultiWord.class.php';
require_once '../class/ContentMultiWordIndex.class.php';
require_once '../class/ContentMultiWordChunk.class.php';
require_once '../class/MultiWordLexiconMWE.class.php';
require_once '../class/MultiWordLexiconClass.class.php';
require_once '../class/MultiWordLexiconTransform.class.php';
require_once '../SharedModules/ExtraModules.class.php';

$task = isset($_REQUEST["task"]) ? $_REQUEST["task"] :  "";

switch ($task)
{
    case "saveMultiWordAnnotation":
        saveMultiWordAnnotation();

    case "loadMultiWordPage":
        loadMultiWordPage();

    case "loadLexiconClassesPage":
        loadLexiconClassesPage();

    case "loadLexiconMWEsPage":
        loadLexiconMWEsPage();

    case "loadLexiconTransformsPage":
        loadLexiconTransformsPage();

    case "saveLexiconClasses":
        saveLexiconClasses();

    case "saveLexiconMWEs":
        saveLexiconMWEs();

    case "saveLexiconTransforms":
        saveLexiconTransforms();

    case "saveNewMWE":
        saveNewMWE();

    case "deleteMWE":
        deleteMWE();
}

function saveMultiWordAnnotation()
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

    $createBackupDIRRes = ExtraModules::CreateDir($backupDir);
    if (in_array($createBackupDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray, $createBackupDIRRes . "CreateResources");
        ExtraModules::KillProcess($resultArray, $createBackupDIRRes . "CreateResources");
    }
    saveMultiWordInDB($_REQUEST, $resourcesDir, $backupDir);
    updateMultiWordRep($_REQUEST["ContentID"], $resourcesDir, $backupDir, $corpusDir);
    //applyAnnotation($_REQUEST["ContentID"], $resourcesDir, $backupDir, $corpusDir, $contentResult[0]["TaggedTextFileName"]);
    $resultArray[0]["resultMsg"] = "DataIsSavedForItems";
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}

function saveMultiWordInDB($post, $resourcesDir, $backupDir)
{
    $multiWordInfo = $post["multiWordInfo"];
    $contentID = $post["ContentID"];
    $insertFileContentArray = array();
    $insertFileContentArray[] = array("ContentMWID","ContentID","MultiWordOrder","MultiWordMatch","MultiWord","MultiWordStatus","MultiWordPOS","MultiWordSkipped");
    for($i = 0; $i < count($multiWordInfo); $i++)
    {
        $ContentMWID = $multiWordInfo[$i][0];
        $MultiWordStatus =  $multiWordInfo[$i][1];
        $insertFileContentArray[] = array($ContentMWID, $contentID, "0", "", "", $MultiWordStatus, "", "0");
    }
    $mweUiJson = "multi_word_ui.json";
    ExtraModules::BackupFile($resourcesDir . $mweUiJson, $backupDir . date("Ymd_His") . "_" . $mweUiJson);
    file_put_contents($resourcesDir . $mweUiJson, json_encode($insertFileContentArray, JSON_PRETTY_PRINT));

    $mweUiCSV = "multi_word_ui.csv";
    $mweUiToCSV = ExtraModules::JsonToCsv($resourcesDir . "MultiWordFromUiToCSV.txt",
        $resourcesDir . $mweUiCSV,
        $backupDir . date("Ymd_His") . "_" . $mweUiCSV,
        $resourcesDir . $mweUiJson,
        $contentID);

    if($mweUiToCSV)
    {
        ContentMultiWord::updateContentMultiWords($resourcesDir . $mweUiCSV, $contentID . "_" . date("Ymd_His"));
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

function updateMultiWordRep($contentID, $resourcesDir, $backupDir, $corpusDir)
{
    $where = "cmw.ContentID = :contentID";
    $whereParam = array(":contentID" => $contentID);
    $finalRawData = ContentMultiWord::SearchContentMultiWordForRep($where, $whereParam);

    $finalAnnotationArray[] = array();

    $startFor = microtime(true);
    for($i = 0; $i < count($finalRawData); $i++)
    {
        $finalAnnotationArray[$i]["match"] = $finalRawData[$i]['MultiWordMatch'];
        $finalAnnotationArray[$i]["mwe"] = $finalRawData[$i]['MultiWord'];
        $finalAnnotationArray[$i]["ok"] = $finalRawData[$i]['MultiWordStatus'];
        $finalAnnotationArray[$i]["pos"] = $finalRawData[$i]['MultiWordPOS'];
        $finalAnnotationArray[$i]["skipped"] = intval($finalRawData[$i]['MultiWordSkipped']);

        $finalIndexRawData = explode("@*@", $finalRawData[$i]["entryIndex"]);
        for($j = 0; $j < count($finalIndexRawData); $j++)
        {
            $finalAnnotationArray[$i]["word_index_list"][$j] = intval($finalIndexRawData[$j]);
        }

        $finalChunkRawData = explode("@*@", $finalRawData[$i]["entryChunk"]);

        for($j = 0; $j < count($finalChunkRawData); $j++)
        {
            $finalChunkRawDataParts = explode("::", $finalChunkRawData[$j]);
            $finalAnnotationArray[$i]["words"][$j][0] = $finalChunkRawDataParts[0];
            $finalAnnotationArray[$i]["words"][$j][1] = $finalChunkRawDataParts[1];
        }
    }

    $finalAnnotationFile = "mwe_annotations.json";
    ExtraModules::BackupFile($resourcesDir . $finalAnnotationFile, $backupDir . date("Ymd_His") . "_" . $finalAnnotationFile);
    file_put_contents($resourcesDir . $finalAnnotationFile, json_encode($finalAnnotationArray, JSON_PRETTY_PRINT));
    return true;
}

function applyAnnotation($contentID, $resourcesDir, $backupDir, $corpusDir, $taggedFileName)
{
    $bashFile = $resourcesDir . "applyAnnotation.txt";
    $fp = fopen( $bashFile, "w");
    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py apply_mwe_annotations_and_copy " .
        $corpusDir . "local_config.json " .
        $corpusDir. $taggedFileName . " " .
        $resourcesDir . "mwe_trace.html 2>&1";
    fwrite($fp, $command);
    ExtraModules::BackupFile($resourcesDir . "mwe_trace.html", $backupDir . date("Ymd_His") . "_mwe_trace.html.csv");
    ExtraModules::BackupFile($corpusDir . $taggedFileName, $backupDir . date("Ymd_His") . $taggedFileName);
    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentID, ContentRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentID, ContentRelatedPage, $LogID);

    if(strpos($output, "*** Error") === false)
        return true;
    else
        return false;
}

function ReadContentMultiWords($resourcesDir, $backupDir, $contentID)
{
    $where = " ContentID = :contentID";
    $whereParam = array(":contentID" => $contentID);

    //reformat Python json
    $mweFileJsonData = json_decode(file_get_contents($resourcesDir . 'mwe_annotations.json'), true);
    $mweArray[] = array("ContentID","MultiWordOrder","MultiWordMatch","MultiWord","MultiWordStatus","MultiWordPOS","MultiWordSkipped");
    $mweIndexesArray[] = array("ContentID","MultiWordOrder","MultiWordIndex");
    $mweChunksArray[] = array("ContentID","MultiWordOrder","MultiWordChunk","MultiWordChunkPOS");

    for($i = 0; $i < count($mweFileJsonData); $i++)
    {
        $index = $i + 1;
        $mweArray[$index][0] = $contentID;
        $mweArray[$index][1] = $index;
        $mweArray[$index][2] = $mweFileJsonData[$i]['match'];
        $mweArray[$index][3] = $mweFileJsonData[$i]['mwe'];
        $mweArray[$index][4] = $mweFileJsonData[$i]['ok'];
        $mweArray[$index][5] = $mweFileJsonData[$i]['pos'];
        $mweArray[$index][6] = $mweFileJsonData[$i]['skipped'];

        for($j = 0; $j < count($mweFileJsonData[$i]['word_index_list']); $j++)
        {
            $mweIndexesArray[] = array($contentID , $index, $mweFileJsonData[$i]['word_index_list'][$j]);
        }
        for($j = 0; $j < count($mweFileJsonData[$i]['words']); $j++)
        {
            $mweChunksArray[] = array($contentID , $index, $mweFileJsonData[$i]['words'][$j][0], $mweFileJsonData[$i]['words'][$j][1]);
        }
    }

    //put mwe array in json
    $mweJson = "mwe.json";
    ExtraModules::BackupFile($resourcesDir . $mweJson, $backupDir . date("Ymd_His") . "_" . $mweJson);
    file_put_contents($resourcesDir . $mweJson, json_encode($mweArray, JSON_PRETTY_PRINT));

    //put mwe index array in json
    $mweIndexJson = "mwe_index.json";
    ExtraModules::BackupFile($resourcesDir . $mweIndexJson, $backupDir . date("Ymd_His") . "_" . $mweIndexJson);
    file_put_contents($resourcesDir . $mweIndexJson, json_encode($mweIndexesArray, JSON_PRETTY_PRINT));

    //put mwe chunk array in json
    $mweChunkJson = "mwe_chunk.json";
    ExtraModules::BackupFile($resourcesDir . $mweChunkJson, $backupDir . date("Ymd_His") . "_" . $mweChunkJson);
    file_put_contents($resourcesDir . $mweChunkJson, json_encode($mweChunksArray, JSON_PRETTY_PRINT));

    //put mwe json in csv
    $mweCsv = "mwe.csv";
    $mwToCSV = ExtraModules::JsonToCsv($resourcesDir . "mweToCSV.txt",
        $resourcesDir . $mweCsv,
        $backupDir . date("Ymd_His") . "_" . $mweCsv,
        $resourcesDir . $mweJson,
        $contentID);

    //put mwe index json in csv
    $mweIndexCsv = "mwe_index.csv";
    $mweIndexToCSV = ExtraModules::JsonToCsv($resourcesDir . "mweIndexToCSV.txt",
        $resourcesDir . $mweIndexCsv,
        $backupDir . date("Ymd_His") . "_" . $mweIndexCsv,
        $resourcesDir . $mweIndexJson,
        $contentID);

    //put mwe chunk json in csv
    $mweChunkCsv = "mwe_chunk.csv";
    $mweChunkToCSV = ExtraModules::JsonToCsv($resourcesDir . "mweChunkToCSV.txt",
        $resourcesDir . $mweChunkCsv,
        $backupDir . date("Ymd_His") . "_" . $mweChunkCsv,
        $resourcesDir . $mweChunkJson,
        $contentID);

    //put mwe csv in table
    if($mwToCSV)
    {
        ContentMultiWord::delete($where, $whereParam);
        ContentMultiWord::insertContentMultiWords($resourcesDir . $mweCsv);
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToMultiWord";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }

    //put mwe index csv in table
    if($mweIndexToCSV)
    {
        ContentMultiWordIndex::delete($where, $whereParam);
        ContentMultiWordIndex::insertContentMultiWordIndexes($resourcesDir . $mweIndexCsv);
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToMultiWordIndex";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }

    //put mwe chunk csv in table
    if($mweChunkToCSV)
    {
        ContentMultiWordChunk::delete($where, $whereParam);
        ContentMultiWordChunk::insertContentMultiWordChunks($resourcesDir . $mweChunkCsv);
    }
    else
    {
        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToMultiWordChunk";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    return true;
}

function loadMultiWordPage()
{
    $contentID = $_REQUEST["contentID"];
    $pageToLoad = $_REQUEST["pageToLoad"];
    $checkOnSubmit = true;

    $where = " ContentID = :contentID ";
    $whereParam = array(":contentID" => $contentID);
    $info = ContentMultiWord::SearchContentMultiWord($where, $whereParam, $pageToLoad);

    $idIndex = "ContentMWID";
    $mweMatch = "MultiWordMatch";
    $mwe = "MultiWord";
    $mweStatus = "MultiWordStatus";

    $mweStatusString = "";

    $tableInfo = "<tr id='annotationError'  style='display: none'>
                    <td><p class='ErrorMsg'></p></td>
                  </tr>
                  <tr style='width: 100%'>
                <td>";

    $tableInfo .= "<table class='responstable' style='width: 100%'>";
    $tableInfo .= "<tr><th style='width: 70%'>Multi word expression</th>";
    $tableInfo .=  "<th style='width: 10%'>Unknown</th>";
    $tableInfo .=  "<th style='width: 10%'>Yes</th>";
    $tableInfo .=  "<th style='width: 10%'>No</th></tr>";
    for($i = 0; $i < min(RowPerPage, count($info)) ; $i++)
    {
        $thisRow = $info[$i];
        $id = $thisRow[$idIndex];
        $mweText = "<span style='color:#ff6666'>" . $thisRow[$mwe] . "</span> in: <br/>" . $thisRow[$mweMatch];
        $mweStatusVal = $thisRow[$mweStatus];
        $mweStatusString .= $thisRow[$mweStatus] == 'mwe_not_okay' ? "1**" :
                            $thisRow[$mweStatus] == 'mwe_okay' ? "2**" : "3**";

        $rowString  = "<tr>";
        $rowString  .= "<input type='hidden' id='multiWordInfo[" . $i . "][0]' 
                              name='multiWordInfo[" . $i . "][0]' value='" . $id . "'>";
        $rowString .= "<td>" . $mweText . "</td>";
        $rowString .= "<td>
                           <input type='radio' name='multiWordInfo[" . $i . "][1]' value='mwe_status_unknown' ";
        if($mweStatusVal == 'mwe_status_unknown') $rowString .= "checked";
        $rowString .= "></td>";
        $rowString .= "<td>
                           <input type='radio' name='multiWordInfo[" . $i . "][1]' value='mwe_okay' ";
        if($mweStatusVal == 'mwe_okay') $rowString .= "checked";
        $rowString .= "></td>";
        $rowString .= "<td>
                           <input type='radio' name='multiWordInfo[" . $i . "][1]' value='mwe_not_okay' ";
        if($mweStatusVal == 'mwe_not_okay') $rowString .= "checked";
        $rowString .= "></td>";
        $rowString .= "</tr>";
        $tableInfo .= $rowString;
    }
    $tableInfo .= "<input type='hidden' id='mweStatusString' name='mweStatusString' value='" . $mweStatusString . "'>";
    $tableInfo .= "</table></td></tr>";

    $numberOfPages = ContentMultiWord::NumberOfPages($contentID);

    $pageNumbersRows = ceil($numberOfPages / 20);
    for($j = 0; $j < $pageNumbersRows; $j++) {
        $tableInfo .= "<tr><td align='center'>";
        $pageNumbersRow = "";
        if ($j == 0)
        {
            $prvPage = $pageToLoad - 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToMultiWordPage(" .$prvPage . "," . $checkOnSubmit . ")'> prv </span>";
        }
        for ($i = 1; $i <= 20; $i++) {
            $spanIndex = ($j * 20) + $i;
            if ($spanIndex <= $numberOfPages) {
                $pageNumbersRow .= "<span class='pageNumber' ";
                if ($spanIndex == $pageToLoad)
                    $pageNumbersRow .= " style='background-color:#008080' ";
                $pageNumbersRow .= " onclick='goToMultiWordPage(" . $spanIndex . "," . $checkOnSubmit . ")'>" . $spanIndex . "</span>";
            }
        }
        if ($j == $pageNumbersRows - 1)
        {
            $nextPage = $pageToLoad + 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToMultiWordPage(" . $nextPage . "," . $checkOnSubmit . ")'> nxt </span>";
        }
        $tableInfo .= $pageNumbersRow . "</td></tr>";
    }

    $tableInfo .= "<tr>
                    <td align='center'>
                        <input type='button'  id='SendButton' name='SendButton'
                               value='Save annotation' onclick='saveMultiWordAnnotation(\"JustSave\")'>
                        <input type='button'  id='SendAndCopyButton' name='SendAndCopyButton'
                               value='Save and exit' onclick='saveMultiWordAnnotation(\"SaveAndExit\")'>
                    </td></tr>";

    echo $tableInfo;
    die();
}

function ReadLexiconMultiWords($mweFileJsonData, $languageID, $LangCorpusDirName)
{
    $where = " LanguageID = :languageID";
    $whereParam = array(":languageID" => $languageID);

    $mweFileJsonIndexes = array_keys($mweFileJsonData);
    //reformat Python json
    $mweArray[] = array("LanguageID","MweHeader","MweName","MwePos");

    for($i = 0; $i < count($mweFileJsonData); $i++)
    {
        $index = $i + 1;
        $MweHeader = $mweFileJsonIndexes[$i];
        $mweArray[$index][0] = $languageID;
        $mweArray[$index][1] = $MweHeader;
        $mweArray[$index][2] = $mweFileJsonData[$MweHeader]['name'];
        $mweArray[$index][3] = $mweFileJsonData[$MweHeader]['pos'];
    }

    //put mwe array in json
    $mweJson = $LangCorpusDirName . "/" . "mwes.json";
    file_put_contents( $mweJson, json_encode($mweArray, JSON_PRETTY_PRINT));

    //put mwe json in csv
    $mweCsv = $LangCorpusDirName . "/" . "mwes.csv";
    $bashFile = $LangCorpusDirName . "/mwesToCSV.txt";
    $mweToCSV = ExtraModules::JsonToCsv($bashFile, $mweCsv,"", $mweJson, $languageID);

    //put mwe csv in table
    if($mweToCSV)
    {
        MultiWordLexiconMWE::delete($where, $whereParam);
        MultiWordLexiconMWE::insertMultiWordLexiconMWES($mweCsv);
    }
    else
    {
        $resultArray[0]["id"] = $languageID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToMultiWordLexicon";
        ExtraModules::UserActivityLog(LanguageRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    return true;
}

function ReadLexiconClasses($classFileJsonData, $languageID, $LangCorpusDirName)
{
    $where = " LanguageID = :languageID";
    $whereParam = array(":languageID" => $languageID);

    $classFileJsonIndexes = array_keys($classFileJsonData);
    //reformat Python json
    $classArray[] = array("LanguageID","ClassID","ClassHeader","ClassMember");
    $index = 1;
    for($i = 0; $i < count($classFileJsonIndexes); $i++)
    {
        $LanguageID = $languageID;
        $ClassID = $i + 1;
        $ClassHeader = $classFileJsonIndexes[$i];
        for($j = 0; $j < count($classFileJsonData[$ClassHeader]); $j++) {
            $classArray[$index][0] = $LanguageID;
            $classArray[$index][1] = $ClassID;
            $classArray[$index][2] = $ClassHeader;
            $classArray[$index][3] = $classFileJsonData[$ClassHeader][$j];
            $index++;
        }
    }

    //put class array in json
    $classJson = $LangCorpusDirName . "/" . "classes.json";
    file_put_contents( $classJson, json_encode($classArray, JSON_PRETTY_PRINT));

    //put class json in csv
    $classCsv = $LangCorpusDirName . "/" . "classes.csv";
    $bashFile = $LangCorpusDirName . "/classesToCSV.txt";
    $classToCSV = ExtraModules::JsonToCsv($bashFile, $classCsv,"", $classJson, $languageID);

    //put class csv in table
    if($classToCSV)
    {
        MultiWordLexiconClass::delete($where, $whereParam);
        MultiWordLexiconClass::insertMultiWordLexiconClasses($classCsv);
    }
    else
    {
        $resultArray[0]["id"] = $languageID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToMultiWordLexicon";
        ExtraModules::UserActivityLog(LanguageRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    return true;
}

function ReadLexiconTransforms($transformFileJsonData, $languageID, $LangCorpusDirName)
{
    $where = " LanguageID = :languageID";
    $whereParam = array(":languageID" => $languageID);

    //reformat Python json
    $transformArray[] = array("LanguageID","TransformMember");

    for($i = 0; $i < count($transformFileJsonData); $i++)
    {
        $index = $i + 1;
        $transformArray[$index][0] = $languageID;
        $transformArray[$index][1] = $transformFileJsonData[$i];
    }

    //put class array in json
    $transformJson = $LangCorpusDirName . "/" . "transforms.json";
    file_put_contents( $transformJson, json_encode($transformArray, JSON_PRETTY_PRINT));

    //put class json in csv
    $transformCsv = $LangCorpusDirName . "/" . "transforms.csv";
    $bashFile = $LangCorpusDirName . "/transformsToCSV.txt";
    $transformToCSV = ExtraModules::JsonToCsv($bashFile, $transformCsv,"", $transformJson, $languageID);

    //put class csv in table
    if($transformToCSV)
    {
        MultiWordLexiconTransform::delete($where, $whereParam);
        MultiWordLexiconTransform::insertMultiWordLexiconTransforms($transformCsv);
    }
    else
    {
        $resultArray[0]["id"] = $languageID;
        $resultArray[0]["resultMsg"] = "FailedToTransferToMultiWordLexicon";
        ExtraModules::UserActivityLog(LanguageRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    return true;
}

function loadLexiconClassesPage()
{
    $languageID = $_REQUEST["languageID"];
    $pageToLoad = $_REQUEST["pageToLoad"];
    $checkOnSubmit = true;

    $where = " LanguageID = :languageID ";
    $whereParam = array(":languageID" => $languageID);
    $info = MultiWordLexiconClass::SearchMultiWordLexiconClass($where, $whereParam, $pageToLoad);

    $idsIndex = "MembersIDs";
    $valuesIndex = "MembersValues";
    $classHeader = "ClassHeader";
    $index = 0;
    $memberString = "";

    $tableInfo = "<tr id='lexiconError'  style='display: none'>
                    <td><p class='ErrorMsg'></p></td>
                  </tr>
                  <tr style='width: 100%'>
                <td>";

    $tableInfo .= "<table class='responstable' style='width: 100%'>";
    $tableInfo .= "<tr><th>Class header</th>";
    $tableInfo .=  "<th>Class members</th></tr>";
    //each row
    for($i = 0; $i < min(RowPerPage, count($info)) ; $i++)
    {
        $thisRow = $info[$i];
        $ids = explode("**", $thisRow[$idsIndex]);
        $values = explode("**", $thisRow[$valuesIndex]);
        $headerVal = $thisRow[$classHeader];
        $memberString .= $thisRow[$valuesIndex] . "**";

        $rowString  = "<tr>";
        $rowString .= "<td>" . $headerVal . "</td>";
        $rowString .= "<td>";
        //each cell
        for($j = 0; $j < count($ids); $j++)
        {
            $rowString  .= "<input type='hidden' id='classInfo[" . $index . "][0]' 
                              name='classInfo[" . $index . "][0]' value='" . $ids[$j] . "'>";
            $rowString .= "<input type='text' name='classInfo[" . $index . "][1]' class='memberInput'
                            id='classInfo[" . $index . "][1]'  value='". htmlspecialchars($values[$j], ENT_QUOTES) ."'>";
            $index++;
        }
        $rowString .= "</td>";
        $rowString .= "</tr>";
        $tableInfo .= $rowString;
    }
    $tableInfo .= "<input type='hidden' id='memberString' name='memberString' value='" . $memberString . "'>";
    $tableInfo .= "</table></td></tr>";

    $numberOfPages = MultiWordLexiconClass::NumberOfPages($languageID);

    $pageNumbersRows = ceil($numberOfPages / 20);
    for($j = 0; $j < $pageNumbersRows; $j++) {
        $tableInfo .= "<tr><td align='center'>";
        $pageNumbersRow = "";
        if ($j == 0)
        {
            $prvPage = $pageToLoad - 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToClassPage(" .$prvPage . "," . $checkOnSubmit . ")'> prv </span>";
        }
        for ($i = 1; $i <= 20; $i++) {
            $spanIndex = ($j * 20) + $i;
            if ($spanIndex <= $numberOfPages) {
                $pageNumbersRow .= "<span class='pageNumber' ";
                if ($spanIndex == $pageToLoad)
                    $pageNumbersRow .= " style='background-color:#008080' ";
                $pageNumbersRow .= " onclick='goToClassPage(" . $spanIndex . "," . $checkOnSubmit . ")'>" . $spanIndex . "</span>";
            }
        }
        if ($j == $pageNumbersRows - 1)
        {
            $nextPage = $pageToLoad + 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToClassPage(" . $nextPage . "," . $checkOnSubmit . ")'> nxt </span>";
        }
        $tableInfo .= $pageNumbersRow . "</td></tr>";
    }

    $tableInfo .= "<tr>
                    <td align='center'>
                        <input type='button'  id='SendButton' name='SendButton'
                               value='Save translations' onclick='saveLexiconClass(\"JustSave\")'>
                        <input type='button'  id='SendAndCopyButton' name='SendAndCopyButton'
                               value='Save and exit' onclick='saveLexiconClass(\"SaveAndExit\")'>
                    </td></tr>";

    echo $tableInfo;
    die();
}

function loadLexiconMWEsPage()
{
    $languageID = $_REQUEST["languageID"];
    $pageToLoad = $_REQUEST["pageToLoad"];
    $checkOnSubmit = true;

    $where = " LanguageID = :languageID ";
    $whereParam = array(":languageID" => $languageID);
    $info = MultiWordLexiconMWE::SearchMultiWordLexiconMWE($where, $whereParam, $pageToLoad);

    $idIndex = "MultiWordLexiconMWEID";
    $mweHeader = "MweHeader";
    $mweName = "MweName";
    $mwePos = "MwePos";

    $nameString = "";
    $posString = "";

    $tableInfo = "<tr id='lexiconError'  style='display: none'>
                    <td><p class='ErrorMsg'></p></td>
                  </tr>
                  <tr style='width: 100%'>
                <td>";

    $tableInfo .= "<table class='responstable' style='width: 100%'>";
    $tableInfo .= "<tr><th>Multi word</th>";
    $tableInfo .= "<th>Definition</th>";
    $tableInfo .= "<th>Multi word pos</th>";
    $tableInfo .=  "<th>Remove it</th></tr>";
    for($i = 0; $i < min(RowPerPage, count($info)) ; $i++)
    {
        $thisRow = $info[$i];
        $id = $thisRow[$idIndex];
        $headerVal = $thisRow[$mweHeader];
        $nameVal = $thisRow[$mweName];
        $nameString .= $nameVal . "**";
        $posVal = $thisRow[$mwePos];
        $posString .= $posVal . "**";

        $rowString  = "<tr>";
        $rowString  .= "<input type='hidden' id='mweInfo[" . $i . "][0]' 
                              name='mweInfo[" . $i . "][0]' value='" . $id . "'>";
        $rowString .= "<td>
                           <input type='text' name='mweInfo[" . $i . "][1]' class='nameInput'
                                id='mweInfo[" . $i . "][1]' value='". htmlspecialchars($nameVal, ENT_QUOTES) ."'>
                        </td>";
        $rowString .= "<td>" . $headerVal . "</td>";
        $rowString .= "<td>
                           <input type='text' name='mweInfo[" . $i . "][2]' class='posInput'
                            id='mweInfo[" . $i . "][2]'  value='". htmlspecialchars($posVal, ENT_QUOTES) ."'>
                        </td>";
        $rowString .= "<td style='text-align: center'>
                               <img src='../img/delete.gif' title='Delete MWE' 
                               onclick='deleteLexiconMWE(\"" . $id ."\");' >
                            </td>";
        $rowString .= "</tr>";
        $tableInfo .= $rowString;
    }
    $tableInfo .= "<input type='hidden' id='nameString' name='nameString' value='" . $nameString . "'>";
    $tableInfo .= "<input type='hidden' id='posString' name='posString' value='" . $posString . "'>";
    $tableInfo .= "</table></td></tr>";

    $numberOfPages = MultiWordLexiconMWE::NumberOfPages($languageID);

    $pageNumbersRows = ceil($numberOfPages / 20);
    for($j = 0; $j < $pageNumbersRows; $j++) {
        $tableInfo .= "<tr><td align='center'>";
        $pageNumbersRow = "";
        if ($j == 0)
        {
            $prvPage = $pageToLoad - 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToMwePage(" .$prvPage . "," . $checkOnSubmit . ")'> prv </span>";
        }
        for ($i = 1; $i <= 20; $i++) {
            $spanIndex = ($j * 20) + $i;
            if ($spanIndex <= $numberOfPages) {
                $pageNumbersRow .= "<span class='pageNumber' ";
                if ($spanIndex == $pageToLoad)
                    $pageNumbersRow .= " style='background-color:#008080' ";
                $pageNumbersRow .= " onclick='goToMwePage(" . $spanIndex . "," . $checkOnSubmit . ")'>" . $spanIndex . "</span>";
            }
        }
        if ($j == $pageNumbersRows - 1)
        {
            $nextPage = $pageToLoad + 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToMwePage(" . $nextPage . "," . $checkOnSubmit . ")'> nxt </span>";
        }
        $tableInfo .= $pageNumbersRow . "</td></tr>";
    }

    $tableInfo .= "<tr>
                    <td align='center'>
                        <input type='button'  id='SendButton' name='SendButton'
                               value='Save' onclick='saveLexiconMWE(\"JustSave\")'>
                        <input type='button'  id='SendAndCopyButton' name='SendAndCopyButton'
                               value='Save and exit' onclick='saveLexiconMWE(\"SaveAndExit\")'>
                    </td></tr>";

    echo $tableInfo;
    die();
}

function loadLexiconTransformsPage()
{
    $languageID = $_REQUEST["languageID"];
    $pageToLoad = $_REQUEST["pageToLoad"];
    $checkOnSubmit = true;

    $where = " LanguageID = :languageID ";
    $whereParam = array(":languageID" => $languageID);
    $info = MultiWordLexiconTransform::SearchMultiWordLexiconTransform($where, $whereParam, $pageToLoad);

    $idIndex = "MultiWordLexiconTransformID";
    $transformMember = "TransformMember";

    $memberString = "";

    $tableInfo = "<tr id='lexiconError'  style='display: none'>
                    <td><p class='ErrorMsg'></p></td>
                  </tr>
                  <tr style='width: 100%'>
                <td>";

    $tableInfo .= "<table class='responstable' style='width: 100%'>";
    $tableInfo .= "<tr><th>Transform</th></tr>";
    for($i = 0; $i < min(RowPerPage, count($info)) ; $i++)
    {
        $thisRow = $info[$i];
        $id = $thisRow[$idIndex];
        $memberVal = $thisRow[$transformMember];
        $memberString .= $memberVal . "**";

        $rowString  = "<tr>";
        $rowString  .= "<input type='hidden' id='transformInfo[" . $i . "][0]' 
                              name='transformInfo[" . $i . "][0]' value='" . $id . "'>";
        $rowString .= "<td>
                           <input type='text' name='transformInfo[" . $i . "][1]' class='transformInput'
                                id='transformInfo[" . $i . "][1]' value='". htmlspecialchars($memberVal, ENT_QUOTES) ."'>
                        </td>";
        $rowString .= "</tr>";
        $tableInfo .= $rowString;
    }
    $tableInfo .= "<input type='hidden' id='memberString' name='memberString' value='" . $memberString . "'>";

    $numberOfPages = MultiWordLexiconTransform::NumberOfPages($languageID);

    $pageNumbersRows = ceil($numberOfPages / 20);
    for($j = 0; $j < $pageNumbersRows; $j++) {
        $tableInfo .= "<tr><td align='center'>";
        $pageNumbersRow = "";
        if ($j == 0)
        {
            $prvPage = $pageToLoad - 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToTransformPage(" .$prvPage . "," . $checkOnSubmit . ")'> prv </span>";
        }
        for ($i = 1; $i <= 20; $i++) {
            $spanIndex = ($j * 20) + $i;
            if ($spanIndex <= $numberOfPages) {
                $pageNumbersRow .= "<span class='pageNumber' ";
                if ($spanIndex == $pageToLoad)
                    $pageNumbersRow .= " style='background-color:#008080' ";
                $pageNumbersRow .= " onclick='goToTransformPage(" . $spanIndex . "," . $checkOnSubmit . ")'>" . $spanIndex . "</span>";
            }
        }
        if ($j == $pageNumbersRows - 1)
        {
            $nextPage = $pageToLoad + 1;
            $pageNumbersRow .= "<span class='pageNumber' onclick='goToTransformPage(" . $nextPage . "," . $checkOnSubmit . ")'> nxt </span>";
        }
        $tableInfo .= $pageNumbersRow . "</td></tr>";
    }

    $tableInfo .= "<tr>
                    <td align='center'>
                        <input type='button'  id='SendButton' name='SendButton'
                               value='Save translations' onclick='saveLexiconTransform(\"JustSave\")'>
                        <input type='button'  id='SendAndCopyButton' name='SendAndCopyButton'
                               value='Save and exit' onclick='saveLexiconTransform(\"SaveAndExit\")'>
                    </td></tr>";

    echo $tableInfo;
    die();
}

function saveLexiconClasses()
{
    $classInfo = $_REQUEST["classInfo"];
    $languageID = $_REQUEST["LanguageID"];

    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $languageID;

    $languageName = Language::getLanguageName($languageID);
    $langTempDir = ContentTmpDirectory . $languageName . "/"  ;
    $createBackupDIRRes = ExtraModules::CreateDir($langTempDir, SubDirNamesContentTmp);
    if (in_array($createBackupDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(LanguageRelatedPage, $resultArray, $createBackupDIRRes . "CreateResources");
        ExtraModules::KillProcess($resultArray, $createBackupDIRRes . "CreateResources");
    }

    $resourcesDir = $langTempDir . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = $langTempDir  . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;

    $insertFileContentArray = array();
    $insertFileContentArray[] = array("MultiWordLexiconClassID","LanguageID","ClassID","ClassHeader","ClassMember");
    for($i = 0; $i < count($classInfo); $i++)
    {
        $MultiWordLexiconClassID = $classInfo[$i][0];
        $ClassMember =  $classInfo[$i][1];
        $insertFileContentArray[] = array($MultiWordLexiconClassID, $languageID, "0", "",  $ClassMember);
    }
    $classUiJson = "lexicon_class_ui.json";
    ExtraModules::BackupFile( $resourcesDir . $classUiJson, $backupDir . date("Ymd_His") . "_" . $classUiJson);
    file_put_contents($resourcesDir . $classUiJson, json_encode($insertFileContentArray, JSON_PRETTY_PRINT));

    $classUiCSV = "lexicon_class_ui.csv";
    $classUiToCSV = ExtraModules::JsonToCsv($resourcesDir . "LexiconClassToCSV.txt",
        $resourcesDir . $classUiCSV,
        $backupDir . date("Ymd_His") . "_" . $classUiCSV,
        $resourcesDir . $classUiJson,
        $languageID);

    if($classUiToCSV)
    {
        MultiWordLexiconClass::updateMultiWordLexiconClasses($resourcesDir . $classUiCSV, $languageID . "_" . date("Ymd_His"));
        if(isset($_REQUEST["updateRep"]) && $_REQUEST["updateRep"] == "yes")
            updateMultiWordLexiconRep($languageID, $languageName, $langTempDir);
        $resultArray[0]["resultMsg"] = "DataIsSavedForItems";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    else
    {
        $resultArray[0]["resultMsg"] = "FailedToGenerateCsv";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
}

function saveLexiconMWEs()
{
    $mweInfo = $_REQUEST["mweInfo"];
    $languageID = $_REQUEST["LanguageID"];

    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $languageID;

    $languageName = Language::getLanguageName($languageID);
    $langTempDir = ContentTmpDirectory . $languageName . "/"  ;
    $createBackupDIRRes = ExtraModules::CreateDir($langTempDir, SubDirNamesContentTmp);
    if (in_array($createBackupDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(LanguageRelatedPage, $resultArray, $createBackupDIRRes . "CreateResources");
        ExtraModules::KillProcess($resultArray, $createBackupDIRRes . "CreateResources");
    }

    $resourcesDir = $langTempDir . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = $langTempDir  . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;

    $insertFileContentArray = array();
    $insertFileContentArray[] = array("MultiWordLexiconMWEID","LanguageID","MweHeader","MweName","MwePos");
    for($i = 0; $i < count($mweInfo); $i++)
    {
        $MultiWordLexiconClassID = $mweInfo[$i][0];
        $MweName =  $mweInfo[$i][1];
        $MwePos =  $mweInfo[$i][2];
        $insertFileContentArray[] = array($MultiWordLexiconClassID, $languageID, "", $MweName,  $MwePos);
    }
    $mweUiJson = "lexicon_mwe_ui.json";
    ExtraModules::BackupFile( $resourcesDir . $mweUiJson, $backupDir . date("Ymd_His") . "_" . $mweUiJson);
    file_put_contents($resourcesDir . $mweUiJson, json_encode($insertFileContentArray, JSON_PRETTY_PRINT));

    $mweUiCSV = "lexicon_mwe_ui.csv";
    $mweUiToCSV = ExtraModules::JsonToCsv($resourcesDir . "LexiconMweToCSV.txt",
        $resourcesDir . $mweUiCSV,
        $backupDir . date("Ymd_His") . "_" . $mweUiCSV,
        $resourcesDir . $mweUiJson,
        $languageID);

    if($mweUiToCSV)
    {
        MultiWordLexiconMWE::updateMultiWordLexiconMWES($resourcesDir . $mweUiCSV, $languageID . "_" . date("Ymd_His"));
        if(isset($_REQUEST["updateRep"]) && $_REQUEST["updateRep"] == "yes")
            updateMultiWordLexiconRep($languageID, $languageName, $langTempDir);
        $resultArray[0]["resultMsg"] = "DataIsSavedForItems";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    else
    {
        $resultArray[0]["resultMsg"] = "FailedToGenerateCsv";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
}

function saveNewMWE()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $_REQUEST["LanguageID"];

    $mweObj = new MultiWordLexiconMWE();
    PdoDataAccess::FillObjectByArray($mweObj, $_REQUEST);
    if(empty($mweObj->MweName))
        $mweObj->MweName = strtolower(preg_replace("/\*/", "", $mweObj->MweHeader));
    $mweObj->insert();
    syncResources($resultArray, "saveMWE");
}

function saveLexiconTransforms()
{
    $transformInfo = $_REQUEST["transformInfo"];
    $languageID = $_REQUEST["LanguageID"];

    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $languageID;

    $languageName = Language::getLanguageName($languageID);
    $langTempDir = ContentTmpDirectory . $languageName . "/"  ;
    $createBackupDIRRes = ExtraModules::CreateDir($langTempDir, SubDirNamesContentTmp);
    if (in_array($createBackupDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(LanguageRelatedPage, $resultArray, $createBackupDIRRes . "CreateResources");
        ExtraModules::KillProcess($resultArray, $createBackupDIRRes . "CreateResources");
    }

    $resourcesDir = $langTempDir . "/" . SubDirNamesContentTmp["resourcesDir"] . "/"  ;
    $backupDir = $langTempDir  . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/"  ;

    $insertFileContentArray = array();
    $insertFileContentArray[] = array("MultiWordLexiconTransformID","LanguageID","TransformMember");
    for($i = 0; $i < count($transformInfo); $i++)
    {
        $MultiWordLexiconTransformID = $transformInfo[$i][0];
        $TransformMember =  $transformInfo[$i][1];
        $insertFileContentArray[] = array($MultiWordLexiconTransformID, $languageID, $TransformMember);
    }
    $transformUiJson = "lexicon_transform_ui.json";
    ExtraModules::BackupFile( $resourcesDir . $transformUiJson, $backupDir . date("Ymd_His") . "_" . $transformUiJson);
    file_put_contents($resourcesDir . $transformUiJson, json_encode($insertFileContentArray, JSON_PRETTY_PRINT));

    $transformUiCSV = "lexicon_transform_ui.csv";
    $transformUiToCSV = ExtraModules::JsonToCsv($resourcesDir . "LexiconTransformToCSV.txt",
        $resourcesDir . $transformUiCSV,
        $backupDir . date("Ymd_His") . "_" . $transformUiCSV,
        $resourcesDir . $transformUiJson,
        $languageID);

    if($transformUiToCSV)
    {
        MultiWordLexiconTransform::updateMultiWordLexiconTransforms($resourcesDir . $transformUiCSV, $languageID . "_" . date("Ymd_His"));
        if(isset($_REQUEST["updateRep"]) && $_REQUEST["updateRep"] == "yes")
            updateMultiWordLexiconRep($languageID, $languageName, $langTempDir);
        $resultArray[0]["resultMsg"] = "DataIsSavedForItems";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    else
    {
        $resultArray[0]["resultMsg"] = "FailedToGenerateCsv";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
}

function updateMultiWordLexiconRep($languageID, $languageName, $langTempDir)
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";
    $resultArray[0]["id"] = $languageID;

    $where = " LanguageID = :languageID ";
    $whereParam = array(":languageID" => $languageID);
    $classInfo = MultiWordLexiconClass::SearchMultiWordLexiconClass($where, $whereParam);
    $mweInfo = MultiWordLexiconMWE::SearchMultiWordLexiconMWE($where, $whereParam);
    $transformInfo = MultiWordLexiconTransform::SearchMultiWordLexiconTransform($where, $whereParam);

    $finalArray = array();
    $finalArray["classes"] = array();
    $finalArray["mwes"] = array();
    $finalArray["transforms"] = array();
    for($i = 0; $i < count($classInfo) ; $i++)
    {
        $header = $classInfo[$i]["ClassHeader"];
        $values = explode("**", $classInfo[$i]["MembersValues"]);
        $finalArray["classes"][$header] = $values;
    }

    for($i = 0; $i < count($mweInfo) ; $i++)
    {
        $header = $mweInfo[$i]["MweHeader"];
        $finalArray["mwes"][$header]["name"] = (empty($mweInfo[$i]["MweName"])) ? '' : $mweInfo[$i]["MweName"] ;
        $finalArray["mwes"][$header]["pos"] = (empty($mweInfo[$i]["MwePos"])) ? '' : $mweInfo[$i]["MwePos"] ;
    }

    for($i = 0; $i < count($transformInfo) ; $i++)
    {
        $finalArray["transforms"][] = $transformInfo[$i]["TransformMember"];
    }

    $resourcesDir = $langTempDir . SubDirNamesContentTmp["resourcesDir"] . "/";
    $backupDir = $langTempDir   . SubDirNamesContentTmp["resourcesBackup"] . "/";
    $lexiconJson = "mwe_defs.json";

    ExtraModules::BackupFile( $resourcesDir . $lexiconJson, $backupDir . date("Ymd_His") . "_" . $lexiconJson);
    file_put_contents($resourcesDir . $lexiconJson, json_encode($finalArray, JSON_PRETTY_PRINT));

    $txtFileDir = LaraContentDir . $languageName . '/' . SubDirNames["corpus"] . '/';
    $txtFileName = 'mwe_defs.txt';
    $bashFile = $resourcesDir . "/MweJsonToTxt.txt";
    $fp = fopen( $bashFile, "w");

    $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py mwe_json_defs_to_txt " .
        $resourcesDir . $lexiconJson . " " . $txtFileDir . $txtFileName . " 2>&1";
    fwrite($fp, $command);
    ExtraModules::BackupFile( $txtFileDir . $txtFileName, $backupDir . date("Ymd_His") . "_" . $txtFileName);

    $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $languageID, LanguageRelatedPage);
    $output = shell_exec('bash < '  . $bashFile );
    ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $languageID, LanguageRelatedPage, $LogID);

    if(strpos($output, "*** Error") !== false)
    {
        $resultArray[0]["resultMsg"] = "FailedConvertingToTxtDefinition";
        ExtraModules::UserActivityLog(LanguageRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    return true;
}

function deleteMWE()
{
    $resultArray = array();
    $resultArray[0]["resultMsg"] = "notSetYet";

    $where = " MultiWordLexiconMWEID = :mweID";
    $whereParam = array(":mweID" => $_GET["MultiWordLexiconMWEID"]);
    MultiWordLexiconMWE::delete($where, $whereParam);
    syncResources($resultArray, "deleteMWE");
}

function syncResources($resultArray, $type)
{
    $languageID = $_REQUEST["LanguageID"];
    $languageName = Language::getLanguageName($languageID);
    $langTempDir = ContentTmpDirectory . $languageName . "/"  ;
    $createBackupDIRRes = ExtraModules::CreateDir($langTempDir, SubDirNamesContentTmp);
    if (in_array($createBackupDIRRes,array("CreateDIRFailed","CreateSubDIRFailed")))
    {
        ExtraModules::UserActivityLog(LanguageRelatedPage, $resultArray, $createBackupDIRRes . "CreateResources");
        ExtraModules::KillProcess($resultArray, $createBackupDIRRes . "CreateResources");
    }
    if(!updateMultiWordLexiconRep($languageID, $languageName, $langTempDir))
    {
        $resultArray[0]["resultMsg"] = $type == "saveMWE" ? "NewMWEFailed" : "DeleteMWEFailed";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
    $resultArray[0]["resultMsg"] = $type == "saveMWE" ? "NewMWESaved" : "MWEDeleted";
    ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
    ExtraModules::KillProcess($resultArray);
}