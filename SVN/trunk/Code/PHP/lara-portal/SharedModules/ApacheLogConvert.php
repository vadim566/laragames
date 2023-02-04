<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 25.09.2020
 * Time: 12:41
 */

require_once '../class/ApacheLog.class.php';

$dateToExtract = date('d/M/Y',strtotime("-1 days"));
$dateToName = date('Y_m_d',strtotime("-1 days"));
$sourceAccessFile = "/var/log/apache2/wwwtim/access.log";
$destinationAccessDir =  "/export/data/www/LARA-data/AccessLog/";

$dateGreppedFile = $destinationAccessDir . $dateToName . ".log";
$readingHistoryGreppedFile = $destinationAccessDir . $dateToName . "_LaraReadingHistories.log";
$resourceContentGreppedFile = $destinationAccessDir . $dateToName . "_LaraResourceContent.log";
$apacheLogObj = new ApacheLog();


$dateGrepBashFile = $destinationAccessDir . $dateToName . ".txt";
$readingHistoryGrepBashFile = $destinationAccessDir . $dateToName . "_LaraReadingHistories.txt";
$resourceContentGrepBashFile = $destinationAccessDir . $dateToName . "_LaraResourceContent.txt";

$fp = fopen($dateGrepBashFile, "w");
$command = 'grep "' . $dateToExtract . '" ' . $sourceAccessFile . ' > ' . $dateGreppedFile . ' 2>&1';
fwrite($fp, $command);
fclose($fp);
$output = shell_exec('bash < '  . $dateGrepBashFile);

$fp = fopen($readingHistoryGrepBashFile, "w");
$command = 'grep "/callector/LaraReadingHistories/" ' . $dateGreppedFile . ' > ' . $readingHistoryGreppedFile . ' 2>&1';
fwrite($fp, $command);
fclose($fp);
$output = shell_exec('bash < '  . $readingHistoryGrepBashFile);

$fp = fopen($resourceContentGrepBashFile, "w");
$command = 'grep "/callector/LaraResourceContent/" ' . $dateGreppedFile . ' > ' . $resourceContentGreppedFile . ' 2>&1';
fwrite($fp, $command);
fclose($fp);
$output = shell_exec('bash < '  . $resourceContentGrepBashFile);

$rhFile = file($readingHistoryGreppedFile);
$readingHistoryLog = array();
foreach($rhFile as $log)
{
    $readingHistoryLog[] = explode (' ', $log);
}
for($i = 0; $i < count($readingHistoryLog); $i++)
{
    $apacheLogObj->IPAddress = $readingHistoryLog[$i][0];
    $apacheLogObj->Date = $readingHistoryLog[$i][3] . " " . $readingHistoryLog[$i][4];
    $apacheLogObj->AccessMethod = $readingHistoryLog[$i][5];
    $apacheLogObj->RequestedURL = $readingHistoryLog[$i][6];
    $apacheLogObj->Param7_9 = $readingHistoryLog[$i][7] . " " . $readingHistoryLog[$i][8] . " " . $readingHistoryLog[$i][9];
    $apacheLogObj->SourceURL = $readingHistoryLog[$i][10];
    $apacheLogObj->Browser = $readingHistoryLog[$i][11];
    $apacheLogObj->SystemInfo = $readingHistoryLog[$i][12] . " " . $readingHistoryLog[$i][13] . " " . $readingHistoryLog[$i][14] . " " .
                                $readingHistoryLog[$i][15] . " " . $readingHistoryLog[$i][16];
    $apacheLogObj->Param17_22 = $readingHistoryLog[$i][17] . " " . $readingHistoryLog[$i][18] . " " . $readingHistoryLog[$i][19] . " " .
                                $readingHistoryLog[$i][20] . " " . $readingHistoryLog[$i][21] . " " . $readingHistoryLog[$i][22];
    $apacheLogObj->GrepExpression = "LaraReadingHistories";
    $apacheLogObj->insert();
}

$rcFile = file($resourceContentGreppedFile);
$resourceContentLog = array();
foreach($rcFile as $log)
{
    $resourceContentLog[] = explode (' ', $log);
}
for($i = 0; $i < count($readingHistoryLog); $i++)
{
    $apacheLogObj->IPAddress = $readingHistoryLog[$i][0];
    $apacheLogObj->Date = $readingHistoryLog[$i][3] . " " . $readingHistoryLog[$i][4];
    $apacheLogObj->AccessMethod = $readingHistoryLog[$i][5];
    $apacheLogObj->RequestedURL = $readingHistoryLog[$i][6];
    $apacheLogObj->Param7_9 = $readingHistoryLog[$i][7] . " " . $readingHistoryLog[$i][8] . " " . $readingHistoryLog[$i][9];
    $apacheLogObj->SourceURL = $readingHistoryLog[$i][10];
    $apacheLogObj->Browser = $readingHistoryLog[$i][11];
    $apacheLogObj->SystemInfo = $readingHistoryLog[$i][12] . " " . $readingHistoryLog[$i][13] . " " . $readingHistoryLog[$i][14] . " " .
        $readingHistoryLog[$i][15] . " " . $readingHistoryLog[$i][16];
    $apacheLogObj->Param17_22 = $readingHistoryLog[$i][17] . " " . $readingHistoryLog[$i][18] . " " . $readingHistoryLog[$i][19] . " " .
        $readingHistoryLog[$i][20] . " " . $readingHistoryLog[$i][21] . " " . $readingHistoryLog[$i][22];
    $apacheLogObj->GrepExpression = "LaraResourceContent";
    $apacheLogObj->insert();
}
