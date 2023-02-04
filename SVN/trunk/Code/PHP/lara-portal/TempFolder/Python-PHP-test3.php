
<?php

$LARA = '/export/data/callslt/habibih/LARA/trunk';

$command = "LARA='/export/data/callslt/habibih/LARA/trunk' python3.7 
$LARA/Code/Python/lara_run_for_portal.py resources_basic 
$LARA/Content/Arash/corpus/local_config.json 
$LARA/Content/Arash/corpus/word_recording.txt 
$LARA/Content/Arash/corpus/segment_recording.txt 
$LARA/Content/Arash/corpus/word_translation.csv 
$LARA/Content/Arash/corpus/segment_translation.csv 2>&1";
$res = shell_exec($command);
print_r($res);

die();

?>