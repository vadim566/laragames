<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 16/06/2020
 * Time: 08:08 PM
 */
?>

<link rel="stylesheet" type="text/css" href="../SharedModules/dataTable/jquery.dataTables.css">

<?php

$now = new DateTime();
echo '<script type="text/javascript" charset="utf8" src="../js/MultiWordLexicons.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/dataTable/jquery.dataTables.js?' . $now->format('His') . '"></script>';
echo '<link rel="stylesheet" href="../css/MainContent.css?' . $now->format('His') . '">';

require_once '../Config.php';
require_once '../class/Language.class.php';

if(!isset($_SESSION[SessionIndex['UserID']]))
{
    echo "Please login again. <br />";
    echo "<a href='index.php?status=sessionExpired'>Click Here to Login</a>";
    die();
}

$listOfLanguages = Language::getListOfLanguages();

?>

<div class="LaraContents">
    <table id="TableOfLexicons" class="display" style="width:100%">
        <thead>
        <tr>
            <th>Language</th>
            <th>Classes</th>
            <th>MWEs</th>
            <th>Transforms</th>
            <th>Download lexicon</th>
        </tr>
        </thead>
        <tbody>
        <?php
            for($i = 0; $i < count($listOfLanguages); $i++)
            {
                $trString = "<tr>";
                $trString .= "<td style='text-align: center'>" . $listOfLanguages[$i]["LanguageName"] . "</td>";
                $trString .= "<td style='text-align: center'>
                               <img src='../img/Dictionary-Book-icon.png' title='Edit lexicon classes' 
                                 onclick='loadLexiconData(\"classes\",\"" . $listOfLanguages[$i]["LanguageID"] ."\");' >
                            </td>";
                $trString .= "<td style='text-align: center'>
                               <img src='../img/Dictionary-Book-icon.png' title='Edit lexicon mwes' 
                                 onclick='loadLexiconData(\"mwes\",\"" . $listOfLanguages[$i]["LanguageID"] ."\");' >
                            </td>";
                $trString .= "<td style='text-align: center'>
                               <img src='../img/Dictionary-Book-icon.png' title='Edit lexicon transforms' 
                                 onclick='loadLexiconData(\"transforms\",\"" . $listOfLanguages[$i]["LanguageID"] ."\");' >
                            </td>";
                $trString .= "<td style='text-align: center'>
                                <a target='_blank' id='FinalLangResDL'
                                    href='../SharedModules/DownloadFile.php?download=mweLexicon&languageName=" . $listOfLanguages[$i]["LanguageName"] . "'>
                                    <img src='../img/blue-document-download-icon.png' title='Download multi word lexicons'>
                                </a></td>";
                $trString .= "</tr>";
                echo $trString;
            }
        ?>
        </tbody>
    </table>

<script>
    onLoadLexicons();
</script>
</div>

