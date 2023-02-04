<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 7/24/2019
 * Time: 01:28 AM
 */

$data = file_get_contents("Tagged_le_petit_prince_small.txt");
$pageArray = explode("<page>", $data);

for($iPage = 0; $iPage < count($pageArray); $iPage++)
{
    $tagFreePage = strip_tags($pageArray[$iPage]);
    $segmentArray = explode("||", $tagFreePage);
    for($iSeg = 0; $iSeg < count($segmentArray); $iSeg++)
    {
        echo $segmentArray[$iSeg] . "**" . "<br/>";
    }
}

die();

?>