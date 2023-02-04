<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 9/28/2019
 * Time: 10:36 PM
 */
require_once '../Config.php';
require_once '../class/ExternalCommandsLogs.class.php';
require_once '../class/DistributedResource.class.php';
require_once '../data/Content.data.php';
require_once 'ExtraModules.class.php';
require_once 'FolderZipArchive.class.php';
require_once 'LogConstants.php';
require_once '../questionnaire/Questionnaire.data.php';

if(isset($_REQUEST["download"]))
{
    if($_REQUEST["download"] == "rawFile" || $_REQUEST["download"] == "taggedFile")
    {
        $fileDir = LaraContentDir . $_REQUEST["fileDir"];
        $fileName = $_REQUEST["fileName"];

        $FileNameParts = explode('.', $fileName);
        $FileExt = $FileNameParts[count($FileNameParts) - 1];
        $FileExt = strtolower($FileExt);
        if ($FileExt == "txt")
            $mimeType = "text/plain";
        else if ($FileExt == "docx")
            $mimeType = "application/vnd.openxmlformats-officedocument.wordprocessingml.document";

        ob_end_clean();

        header('Content-Type: '.$mimeType);
        header('Content-Disposition: attachment; filename="' . basename($fileName) . '";');
        header('Content-Transfer-Encoding: binary');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($fileDir . "/" . $fileName));

        readfile($fileDir . "/" . $fileName);
        exit;

    }
    else if($_REQUEST["download"] == "csvFileDL")
    {
        $corpusDir = LaraContentDir . $_REQUEST["fileDir"] . "/" . SubDirNames["corpus"] . "/";
        $fileDir = ContentTmpDirectory . $_REQUEST["fileDir"] . "/" . SubDirNamesContentTmp["resourcesDir"] . "/";
        $backupDir = ContentTmpDirectory . $_REQUEST["fileDir"] . "/" . SubDirNamesContentTmp["resourcesBackup"] . "/";
        $contentID = $_REQUEST["contentID"];
        $createResourcesResult = CreateResourceFiles($corpusDir, $fileDir, $contentID);

        if($_REQUEST["fileType"] == "lemma")
        {
            $jsonFileName = "word_translations.json";
            $csvFileName = "word_translations_offline.csv";
        }
        else if($_REQUEST["fileType"] == "type")
        {
            $jsonFileName = "word_translations_surface_type.json";
            $csvFileName = "word_translations_surface_type_offline.csv";
        }

        $jsonToCSV = ExtraModules::WordTypeOrLemmaJsonToCsv($fileDir . "OfflineTranslationJsonToCSV.txt",
            $fileDir . $csvFileName,
            $backupDir . date("Ymd_His") . "_" . $csvFileName,
            $fileDir . $jsonFileName,
            $contentID);

        ob_end_clean();

        header("Content-Type: text/csv");
        header('Content-Disposition: attachment; filename="' . basename($csvFileName) . '";');
        header('Content-Transfer-Encoding: binary');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($fileDir . "/" . $csvFileName));

        readfile($fileDir . "/" . $csvFileName);
        exit;
    }
    else if($_REQUEST["download"] == "csvTokenAndSegmentFileDL")
    {
        $corpusDir = LaraContentDir . $_REQUEST["fileDir"] . "/" . SubDirNames["corpus"] . "/";
        $fileDir = ContentTmpDirectory . $_REQUEST["fileDir"] . "/" . SubDirNamesContentTmp["resourcesDir"] . "/";
        $contentID = $_REQUEST["contentID"];
        $createResourcesResult = CreateResourceFiles($corpusDir, $fileDir, $contentID);

        if($_REQUEST["fileType"] == "token")
            $csvFileName = "word_translations_tokens.csv";
        else if($_REQUEST["fileType"] == "segment")
            $csvFileName = "segment_translations.csv";

        ob_end_clean();

        header("Content-Type: text/csv");
        header('Content-Disposition: attachment; filename="' . basename($csvFileName) . '";');
        header('Content-Transfer-Encoding: binary');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($fileDir . "/" . $csvFileName));

        readfile($fileDir . "/" . $csvFileName);
        exit;
    }
    else if($_REQUEST["download"] == "flashcard")
    {
        $fileDir = ContentTmpDirectory . $_REQUEST["folderDir"] . "/" . SubDirNamesContentTmp["resourcesDir"] . "/";
        $fileName = "flashcard_" . $_SESSION[SessionIndex['UserID']] . ".json";
        $dlFileName = "flashcard_" . $_SESSION[SessionIndex['UserID']] . "_" . date('Ymd_His'). ".json";

        ob_end_clean();
        header("Content-Type: text/plain");
        header('Content-Disposition: attachment; filename="' . basename($dlFileName) . '";');
        header('Content-Transfer-Encoding: binary');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($fileDir . "/" . $fileName));

        readfile($fileDir . "/" . $fileName);
        exit;
    }
    else if ($_REQUEST["download"] == "finalPack")
    {
        $corpusDir = LaraContentDir . $_REQUEST["folderDir"] . "/" . SubDirNames["corpus"] . "/";
        $sourceConfigFile = $corpusDir . "local_config.json";
        $targetZipFile = WorkingTmpDirectory . $_REQUEST["zipFolderName"] ;
        $contentID = $_REQUEST["Q0"];
        $bashFile = $corpusDir . "MakeExportZipFile.txt";
        $fp = fopen( $bashFile, "w");
        $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py make_export_zipfile "
            . $sourceConfigFile . " " .  $targetZipFile . " 2>&1";
        fwrite($fp, $command);
        fclose($fp);

        $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentID, ContentRelatedPage);
        $output = shell_exec('bash < '  . $bashFile );
        ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentID, ContentRelatedPage, $LogID);
        if(strpos($output, "*** Error") === false)
        {
            ob_end_clean();
            header('Content-type: application/zip');
            header("Content-length: " . filesize($targetZipFile));
            header("Pragma: no-cache");
            header("Expires: 0");
            header('Content-Disposition: attachment; filename="' . basename($targetZipFile) . '";');
            readfile($targetZipFile);
            exit;
        }
        else
        {
            echo "somethingIsWrongHere";
            die();
        }
    }
    else if ($_REQUEST["download"] == "finalResourcePack")
    {
        $input = DistributedDir . $_REQUEST["folderDir"] ;
        $output = WorkingTmpDirectory . $_REQUEST["zipFolderName"] ;

        new FolderZipArchive($input, $output);

        ob_end_clean();
        header('Content-type: application/zip');
        header("Content-length: " . filesize($output));
        header("Pragma: no-cache");
        header("Expires: 0");
        header('Content-Disposition: attachment; filename="' . basename($output) . '";');
        readfile($output);
        exit;
    }
    else if ($_REQUEST["download"] == "compiledContent")
    {
        $input = ContentTmpDirectory . $_REQUEST["folderDir"] . "/compiled/" . $_REQUEST["folderName"] ;
        $output = WorkingTmpDirectory . $_REQUEST["folderName"] . ".zip";

        new FolderZipArchive($input, $output);

        ob_end_clean();
        header('Content-type: application/zip');
        header("Content-length: " . filesize($output));
        header("Pragma: no-cache");
        header("Expires: 0");
        header('Content-Disposition: attachment; filename="' . basename($output) . '";');
        readfile($output);
        exit;
    }
    else if($_REQUEST["download"] == "pythonTrace")
    {
        if(isset($_REQUEST["contentID"]))
            $temp = ExternalCommandsLogs::SearchExternalCommandsLogs($_REQUEST["contentID"], 'content');
        else if(isset($_REQUEST["rhID"]))
            $temp = ExternalCommandsLogs::SearchExternalCommandsLogs($_REQUEST["rhID"], 'history');

        $fileContent = "pythonTrace:" . "\n";
        for($i = 0; $i < count($temp); $i++)
        {
            $fileContent .= $temp[$i]["LogTime"] . " *** " . $temp[$i]["LogInfo"];
            $fileContent .=  "\n" . "----------------------------------" . "\n"  ;

        }
        header("Content-type: text/plain");
        header("Content-Disposition: attachment; filename=PythonTrace.txt");

        echo $fileContent;
    }
    else if($_REQUEST["download"] == "flashcardsPythonTrace")
    {
        $where = " RelatedPage = 'flashcard' and RelatedID = :relatedID and UserID = :userID";
        $whereParams = array(":relatedID" => $_REQUEST["contentID"], ":userID" => $_REQUEST["userID"]);
        $temp = ExternalCommandsLogs::SearchFlashcardsExternalCommandsLogs($where, $whereParams);

        $fileContent = "pythonTrace:" . "\n";
        for($i = 0; $i < count($temp); $i++)
        {
            $fileContent .= $temp[$i]["LogTime"] . " *** " . $temp[$i]["LogInfo"];
            $fileContent .=  "\n" . "----------------------------------" . "\n"  ;

        }
        header("Content-type: text/plain");
        header("Content-Disposition: attachment; filename=PythonTrace.txt");

        echo $fileContent;
    }
    else if($_REQUEST["download"] == "allResources")
    {
        $fileContent = "{" . "\n";
        for($i = 0; $i < count($temp); $i++)
        {
            $fileContent .=  $temp[$i]["ResID"] . ' : ';
            $fileContent .=  $temp[$i]["ResInfo"] .  ',' . "\n"  ;
        }
        $fileContent = rtrim($fileContent);
        $fileContent = rtrim($fileContent,",");
        $fileContent .=   "\n"  ;
        $fileContent .= "}" ;
        header("Content-type: text/plain");
        header("Content-Disposition: attachment; filename=all_resources.json");

        echo $fileContent;
    }
    else if($_REQUEST["download"] == "PythonOutputDetail")
    {
        $res = ExternalCommandsLogs::SearchPythonCommandRes($_REQUEST["relatedID"],$_REQUEST["relatedPage"], $_REQUEST["msgToShow"]);

        $fileContent = "details of error:" . "\n";
        $fileContent .= $res;

        header("Content-type: text/plain");
        header("Content-Disposition: attachment; filename=ErrorDetails.txt");

        echo $fileContent;
    }
    else if($_REQUEST["download"] == "mweLexicon")
    {
        $fileDir = LaraContentDir . strtolower($_REQUEST["languageName"]) . "/" . SubDirNames["corpus"] . "/";
        $fileName = "mwe_defs.txt";

        ob_end_clean();

        header("Content-Type: text/csv");
        header('Content-Disposition: attachment; filename="' . basename($fileName) . '";');
        header('Content-Transfer-Encoding: binary');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($fileDir . "/" . $fileName));

        readfile($fileDir . "/" . $fileName);
        exit;
    }

    else if($_REQUEST["download"] == "VQ_SegmentResponses")
    {
        $temp = SegmentResponses();
        $fileName = ContentTmpDirectory . 'VQ_SegmentResponses' . '_' . date("Ymd_His") . '.csv';
        $fp = fopen($fileName, 'w');

        foreach ($temp as $fields)
        {
            fputcsv($fp, $fields);
        }

        fclose($fp);

        ob_end_clean();

        header("Content-Type: text/csv");
        header('Content-Disposition: attachment; filename="' . basename($fileName) . '";');
        header('Content-Transfer-Encoding: binary');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($fileName));

        readfile($fileName);
        exit;
    }

    else if($_REQUEST["download"] == "VQ_VersionOverallResponses")
    {
        $temp = VersionOverallResponses();
        $fileName = ContentTmpDirectory . 'VQ_VersionOverallResponses' . '_' . date("Ymd_His") . '.csv' ;
        $fp = fopen($fileName, 'w');

        foreach ($temp as $fields)
        {
            fputcsv($fp, $fields);
        }

        fclose($fp);

        ob_end_clean();

        header("Content-Type: text/csv");
        header('Content-Disposition: attachment; filename="' . basename($fileName) . '";');
        header('Content-Transfer-Encoding: binary');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($fileName));

        readfile($fileName);
        exit;
    }

    else if($_REQUEST["download"] == "VQ_VersionResponses")
    {
        $temp = VersionResponses();
        $fileName = ContentTmpDirectory . 'VQ_VersionResponses' . '_' . date("Ymd_His") . '.csv';
        $fp = fopen($fileName, 'w');

        foreach ($temp as $fields)
        {
            fputcsv($fp, $fields);
        }

        fclose($fp);

        ob_end_clean();

        header("Content-Type: text/csv");
        header('Content-Disposition: attachment; filename="' . basename($fileName) . '";');
        header('Content-Transfer-Encoding: binary');
        header('Expires: 0');
        header('Cache-Control: must-revalidate');
        header('Pragma: public');
        header('Content-Length: ' . filesize($fileName));

        readfile($fileName);
        exit;
    }

}