<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 9/30/2019
 * Time: 03:41 PM
 */


//added 11/06/2020
$srcNames =  "/export/data/www/LARA-data/french/translations/";
$destNames = "/export/data/www/LARA-data-stage/french/translations/";

if( is_dir($destNames) === false )
{
    mkdir($destNames);
}
echo "copying" . $srcNames . "...";
$bashFile ="/export/data/www/LARA-data-stage/CopyCommand.txt";
$fp = fopen($bashFile, "w");
$command = "scp -r " . $srcNames . "* " . $destNames . "  2>&1";
fwrite($fp, $command);
fclose($fp);
$output = shell_exec('bash < '  . $bashFile );
$resFile ="/export/data/www/LARA-data-stage/CopyRes.txt";
$fp = fopen($resFile, "w");
fwrite($fp, $output);
fclose($fp);
echo "ends.\n";
die();
// end of block 11/06/2020
$srcNames = array("/export/data/www/LARA-data/english/",
    "/export/data/www/LARA-data/farsi/",
    "/export/data/www/LARA-data/french/",
    "/export/data/www/LARA-data/icelandic/",
    "/export/data/www/LARA-data/italian/",
    "/export/data/www/LARA-data/japanese/",
    "/export/data/www/LARA-data/pitjantjatjara/",
    "/export/data/www/LARA-data/russian/",
    "/export/data/www/LARA-data/swedish/");

$destNames = array("/export/data/www/LARA-data-stage/english/",
    "/export/data/www/LARA-data-stage/farsi/",
    "/export/data/www/LARA-data-stage/french/",
    "/export/data/www/LARA-data-stage/icelandic/",
    "/export/data/www/LARA-data-stage/italian/",
    "/export/data/www/LARA-data-stage/japanese/",
    "/export/data/www/LARA-data-stage/pitjantjatjara/",
    "/export/data/www/LARA-data-stage/russian/",
    "/export/data/www/LARA-data-stage/swedish/");

for($i=0; $i<count($srcNames); $i++)
{
    if( is_dir($destNames[$i]) === false )
    {
        mkdir($destNames[$i]);
    }
    echo "copying" . $srcNames[$i] . "...";
    $bashFile ="/export/data/www/LARA-data-stage/CopyCommand" . $i . ".txt";
    $fp = fopen($bashFile, "w");
    $command = "scp -r " . $srcNames[$i] . "* " . $destNames[$i] . "  2>&1";
    fwrite($fp, $command);
    fclose($fp);
    $output = shell_exec('bash < '  . $bashFile );
    $resFile ="/export/data/www/LARA-data-stage/CopyRes" . $i . ".txt";
    $fp = fopen($resFile, "w");
    fwrite($fp, $output);
    fclose($fp);
    echo "ends.\n";
}

echo "end of copying";
die();

?>