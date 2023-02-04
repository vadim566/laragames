<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 8/7/2019
 * Time: 05:20 PM
 */
//check the svn connection on the server part 2

require_once '../SharedModules/PdoDataAccess.class.php';
require_once '../Config.php';
require_once '../class/Language.class.php';

$folderToCreate = "/export/data/www/callector-community-data-stage/lara-content-files";
if (!file_exists( $folderToCreate ) && !is_dir($folderToCreate))
{
    //if not, try to create the root directory
    if(! mkdir($folderToCreate, 0777, true))
    {
        echo "CreateDIRFailed";
    }
    else
    {
        echo "DIRCreated";
    }
}
else
{
    echo "DIRExists";
}

die();
$query = "select lower(LanguageName) from Languages ";
$temp = PdoDataAccess::runquery($query);

for($j = 0; $j <= count($temp); $j++)
{
    $dirAddress = LaraContentDir . $temp[$j][0];

    $subDirNames= SubDirNames;

    if (file_exists( $dirAddress ) && is_dir($dirAddress))
    {
        echo $dirAddress . " exists"  . "<br/>";
        for($i = 0; $i < count($subDirNames); $i++)
        {
            $subDir = $dirAddress . "/" . array_keys($subDirNames)[$i];
            if (!file_exists( $subDir ) && !is_dir($subDir))
            {
                echo $subDir . " does not exist" . "<br/>";
                if( mkdir($subDir, 0777, true))
                    echo $subDir . " created" . "<br/>";
                else
                    echo $subDir . " failed to create" . "<br/>";
            }

            else
                echo $subDir . " exists" . "<br/>";
        }
    }
    else
    {
        echo $dirAddress . " does not exist" . "<br/>";
    }
}

die();



$query = "SELECT DirName FROM `Contents`";
$temp = PdoDataAccess::runquery($query);
for($i = 0 ; $i < count($temp); $i++) {
    $dirAddress = ContentTmpDirectory . $temp[$i][0];
    echo $dirAddress;
    if (!file_exists( $dirAddress ) && !is_dir($dirAddress))
    {
        //if not, try to create the root directory
        if(! mkdir($dirAddress, 0777, true))
        {
            echo "CreateDIRFailed";
        }
        else
        {
          $subDir = $dirAddress . "/compiled/";
            echo $subDir;
            if( !mkdir($subDir, 0777, true))
            {
                echo "CreateSubDIR1Failed";
            }
            $subDir = $dirAddress . "/laraTmpDirectory/";
            echo $subDir;
            if( !mkdir($subDir, 0777, true))
            {
                echo "CreateSubDIR2Failed";
            }

            echo "DIRCreated";
        }
    }
    else
    {
        echo "DIRExists";
    }
echo "***********************";
}
