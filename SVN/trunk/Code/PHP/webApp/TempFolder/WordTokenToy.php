<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 12/29/2019
 * Time: 08:03 PM
 */

$string = file_get_contents("TranslationFileFormatSamples/word_translations_tokens.json");
$json_a = json_decode($string, true);


echo "<table border='1'>";
for($i = 0; $i < count($json_a); $i++)
{
    for($j = 0; $j < 3; $j++)
    {
        echo "<tr>";
        for($k = 0; $k < count($json_a[$i][$j]); $k++)
        {
            echo "<td>";
            if($j == 1)
            {
                echo '<input type="text"  size="20" value="'. $json_a[$i][$j][$k] .'">';

            }
            else
            {
                echo $json_a[$i][$j][$k];
            }
            echo "</td>";
        }
        echo "</tr>";
    }
    echo "<tr><td colspan='3'><hr></td></tr>";
}
echo "</table>";
?>