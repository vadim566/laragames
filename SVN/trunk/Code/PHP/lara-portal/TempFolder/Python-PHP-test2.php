


<?php




$LARA = '/export/data/www/issco-site/en/research/projects/LARA-portal/trunk';
$LARA_data = '/export/data/www/LARA-data';

$command = "LARA='/export/data/www/issco-site/en/research/projects/LARA-portal/trunk' python3.7 $LARA/Code/Python/lara_run_for_portal.py resources_basic $LARA_data/LP/corpus/local_config.json $LARA_data/LP/corpus/word_recording.txt $LARA_data/LP/corpus/segment_recording.txt $LARA_data/LP/corpus/word_translation.csv $LARA_data/LP/corpus/segment_translation.csv 2>&1";


//$command = "LARA='/export/data/www/issco-site/en/research/projects/LARA-portal/trunk' python3.7 $LARA/Code/Python/check_lara_env.py  2>&1";
$res = shell_exec($command);
print_r($res);

die();

?>

