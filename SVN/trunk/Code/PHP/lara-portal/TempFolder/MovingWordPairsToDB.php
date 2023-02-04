<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 9/11/2019
 * Time: 03:59 PM
 */


require_once '../class/ParolPair.class.php';
require_once '../SharedModules/PHPExcel/Classes/PHPExcel.php';

$inputFileName = "/export/data/www/LARA-data-stage/english/translations/english_swedish.csv";
$LangPairID = "7920";

$inputFileType = 'CSV';
$objReader = PHPExcel_IOFactory::createReader($inputFileType)->setDelimiter("\t");;
$objPHPExcel = $objReader->load($inputFileName);
$worksheet = $objPHPExcel->getActiveSheet();
$maxRow = $worksheet->getHighestRow();

for($row=2; $row<=$maxRow ; $row++)
{
    $ppObj= new ParolPair();
    $ppObj->LanguagePairID = $LangPairID;
    $ppObj->ParolInL2 = $worksheet->getCellByColumnAndRow(0, $row)->getValue();
    $ppObj->ParolInL1 = $worksheet->getCellByColumnAndRow(1, $row)->getValue();
    $ppObj->ParolType = "word";

    if($ppObj->ParolPairExists() == false)
    {
        $ppObj->insert();
    }
    else
    {
        $ppObj->update();
    }
}


echo "done";

?>