<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 30.09.2020
 * Time: 12:54
 */

require_once '../Config.php';
require_once '../class/RawContentSegment.class.php';
require_once '../class/RawContentParticle.class.php';
require_once '../SharedModules/ExtraModules.class.php';
//reformat Python json
$resourcesDir = ContentTmpDirectory . "240_Le_petit_prince/resourcesDir/";
$splitFileJsonData = json_decode(file_get_contents($resourcesDir . 'split.json'), true);

$segmentArray[] = array("ContentID","PageNo","SegmentNo","RawSegment","ProcessedSegment");
$particleArray[] = array("ContentID","PageNo","SegmentNo","ParticleNo","Particle","ParticleRoot");
$contentID = 240;
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

//put split array in json
$rawSegmentJson = "rawSegment.json";
ExtraModules::BackupFile($resourcesDir . $rawSegmentJson, $backupDir . date("Ymd_His") . "_" . $rawSegmentJson);
file_put_contents($resourcesDir . $rawSegmentJson, json_encode($segmentArray, JSON_PRETTY_PRINT));

//put split index array in json
$rawParticleJson = "rawParticle.json";
ExtraModules::BackupFile($resourcesDir . $rawParticleJson, $backupDir . date("Ymd_His") . "_" . $rawParticleJson);
file_put_contents($resourcesDir . $rawParticleJson, json_encode($particleArray, JSON_PRETTY_PRINT));

//put split json in csv
$rawSegmentCsv = "rawSegment.csv";
$segToCSV = ExtraModules::JsonToCsv($resourcesDir . "rawSegment.txt",
    $resourcesDir . $rawSegmentCsv,
    $backupDir . date("Ymd_His") . "_" . $rawSegmentCsv,
    $resourcesDir . $rawSegmentJson,
    $contentID);

//put split index json in csv
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

//put particle csv in table
if($parToCSV)
{
    RawContentParticle::delete($where, $whereParam);
    RawContentParticle::insertRawContentParticle($resourcesDir . $rawParticleCsv);
}

echo "done";

