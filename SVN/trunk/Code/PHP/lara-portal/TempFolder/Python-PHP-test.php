<?php

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */


/*$command = "perl C:/TreeTagger/cmd/utf8-tokenize.perl -i -a
C:/TreeTagger/lib/italian-abbreviations C:/TreeTagger/dante.txt";
$command = "perl C:/TreeTagger/cmd/utf8-tokenize.perl -i -a  %TREETAGGER%/lib/italian-abbreviations %TREETAGGER%/dante.txt > C:/TreeTagger/tmp2.txt 2>&1";
//| C:/TreeTagger/bin/tree-tagger C:/TreeTagger/lib/italian.par -token -lemma -sgml -no-unknown > C:/TreeTagger/tmp2.txt";

//$res = shell_exec("python C:\wamp64\www\LARA-portal\mkdir.py hello 2>&1");
//$res = shell_exec("sicstus -l lara_run_toy.pl -a hannnn TempFolder/toy_output.txt 2>&1");
*/

$command = TreeTaggerEnv . " " . LaraEnv . " " . PythonCmnd . " C:/PhD/regulus-code/trunk/Regulus/Python/LARA/lara_run.py treetagger_basic italian C:/wamp64/www/LARA-portal/lara_content/2_Dante/corpus/dante.txt C:/wamp64/www/LARA-portal/lara_content/2_Dante/corpus/Tagged_dante.txt";

require_once '../Config.php';


$bashFileName = "temp_" . rand(1000,9999) . ".txt";
$fp = fopen(TempDir . $bashFileName, "w");
$command = LaraEnv . " " . TreeTaggerEnv . " " . PythonCmnd . " " . PythonDir . "lara_run.py treetagger_basic italian " .
    TempDir . "dante.txt " . TempDir . "Tagged_dante.txt 2>&1";
fwrite($fp, $command);

$sOutput = shell_exec('bash <  C:/wamp64/www/LARA-portal/lara_content/56_a/corpus/TreeTaggerCommand.txt');
echo $sOutput;


?>
