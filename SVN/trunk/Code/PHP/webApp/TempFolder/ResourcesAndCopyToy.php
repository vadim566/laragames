<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 1/2/2020
 * Time: 02:35 PM
 */

require_once '../Config.php';
require_once '../data/SegmentsAndWords.data.php';
ini_set('display_errors', 1);
$corpusDir = LaraContentDir . "94_NTM_1/" . SubDirNames["corpus"] . "/";
$baseFileName = ContentTmpDirectory . "94_NTM_1/resourcesDir/";

if( is_dir($baseFileName) === false )
{
    mkdir($baseFileName, 0777, true);
}
/*
$bashFile = $baseFileName . "FirstPhaseCommand.txt";
$fp = fopen( $bashFile, "w");

$resFile = $baseFileName . "FirstPhaseRes.txt";
$resFP = fopen( $resFile, "w");

$command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py resources_and_copy " .
    $corpusDir . "local_config.json " . $baseFileName ;
fwrite($fp, $command);

$output = shell_exec('bash < '  . $bashFile );
fwrite($resFP, $output);

ReadContentLemmas($baseFileName,94);
ReadContentTypes($baseFileName, 94);
ReadContentSegments($baseFileName, 94);*/
ReadContentTokens($baseFileName, 94);

echo "Check the results now";

?>