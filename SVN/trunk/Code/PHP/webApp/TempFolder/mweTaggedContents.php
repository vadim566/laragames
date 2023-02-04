<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 19.12.2020
 * Time: 17:47
 */

require_once '../SharedModules/PdoDataAccess.class.php';
require_once '../SharedModules/DocxConversion.class.php';

$query = "select DirName, TaggedTextFileName from Contents 
            where IsDeleted = 'NO' and TaggedTextFileName is not null order by ContentID";
$temp = PdoDataAccess::runquery($query);

for($i = 0; $i < count($temp); $i++)
{
    $fileName = LaraContentDir . $temp[$i]["DirName"] . "/" . SubDirNames["corpus"] . "/" . $temp[$i]["TaggedTextFileName"];

    $FileExt = pathinfo($fileName, PATHINFO_EXTENSION);
    if ($FileExt == "txt")
    {
        $fileContent = file_get_contents($fileName);
    }
    else if ($FileExt == "docx" )
    {
        $docxObj = new DocxConversion($fileName);
        $fileContent = $docxObj->convertToText();
    }

    if( strpos($fileContent,"#mwe_part_") !== false) {
        echo $fileName . "</br>";
    }
}