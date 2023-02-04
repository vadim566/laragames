<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 08.09.2020
 * Time: 17:47
 */

require_once '../SharedModules/PdoDataAccess.class.php';
require_once '../data/MultiWordExpressions.data.php';

$query = "SELECT distinct text, prefix_part FROM pvc_infinitive where prefix_part != ''";
$temp = PdoDataAccess::runquery($query);
$mweObj = new MultiWordLexiconMWE();
$mweObj->LanguageID = "46";

for($i = 0; $i < count($temp); $i++)
{
    $row = $temp[$i];
    $verb = $row["text"];
    $prefix = $row["prefix_part"];
    $lightVerb = "*" . str_replace(' ', '', str_replace($prefix, '', $verb)) . "*" ;
    $mweObj->MweHeader = $prefix . $lightVerb;
    $mweObj->MweName = $verb;
    $mweObj->insert();
}