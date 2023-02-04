<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 6/10/2019
 * Time: 08:08 PM
 */
?>

<link rel="stylesheet" type="text/css" href="../SharedModules/dataTable/jquery.dataTables.css">
<link rel="stylesheet" type="text/css" href="../SharedModules/jquery/jquery-ui.css">
<?php

$now = new DateTime();
echo '<script type="text/javascript" charset="utf8" src="../js/Flashcards.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/dataTable/jquery.dataTables.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/jquery/jquery-ui.js?' . $now->format('His') . '"></script>';

echo '<link rel="stylesheet" href="../css/MainContent.css?' . $now->format('His') . '">';

require_once '../Config.php';
require_once '../class/Content.class.php';

if(!isset($_SESSION[SessionIndex['UserID']]))
{
    echo "Please login again. <br />";
    echo "<a href='index.php?status=sessionExpired'>Click Here to Login</a>";
    die();
}

$where = " c.IsDeleted = 'NO' and 
            (c.WordTranslationFC != 'NO' or c.AudioTranslationFC != 'NO' or c.SignedVideoFC != 'NO' or c.GapFC != 'NO')
            order by l2.LanguageName , l1.LanguageName , c.ContentName";
$info = Content::FullSelect($where);
?>

<div class="LaraContents">
    <table id="TableOfFlashcardContents" class="display" style="width:100%">
        <thead>
        <tr>
            <th>Text name</th>
            <th>Content creator</th>
            <th>Reading language</th>
            <th>Translation language</th>
            <th>Read text</th>
            <th>Take the test</th>
            <th>Download raw test</th>
            <th>Python trace</th>
        </tr>
        </thead>
        <tbody>
        <?php
            for($i = 0; $i < count($info); $i++)
            {
                $trString = "<tr>";
                $trString .= "<td style='text-align: center'>" . $info[$i]["ContentName"] . "</td>";
                $trString .= "<td style='text-align: center'>" . $info[$i]["UserName"] . "</td>";
                $trString .= "<td style='text-align: center'>" . $info[$i]["L2Name"] . "</td>";
                $trString .= "<td style='text-align: center'>" . $info[$i]["L1Name"] . "</td>";
                $trString .= "<td style='text-align: center'>
                                    <a target='_blank' href='" . $info[$i]["WebAddress"] . "'>
                                        <img src='../img/library-icon.png' title='Read content in browser' >
                                    </a>
                                </td>";
                $trString .= "<td style='text-align: center'>
                               <img src='../img/flashcard-icon.png' title='Start flashcard test' 
                               onclick='beforeGenerateFlashcardSet(\"" . $info[$i]["ContentID"] . "\"," .
                                                                   "\"" . $_SESSION[SessionIndex['UserID']] . "\"," .
                                                                   "\"" . $info[$i]["WordTranslationFC"] . "\"," .
                                                                   "\"" . $info[$i]["AudioTranslationFC"] . "\"," .
                                                                   "\"" . $info[$i]["SignedVideoFC"] . "\"," .
                                                                   "\"" . $info[$i]["GapFC"] . "\");' ></td>";
                $trString .= "<td style='text-align: center'>";
                $cmp = "&folderDir=" . $info[$i]["DirName"];
                $trString .= "<a target='_blank' id='FlashcardDL'
                                    href='../SharedModules/DownloadFile.php?download=flashcard" . $cmp . "'>
                                    <img src='../img/flashcard-info-icon.png' title='Download json format of the flashcard'>
                                    </a></td>";
                $trString .= "<td style='text-align: center'>
                                   <a target='_blank' id='PythonTraceDL'
                                        href='../SharedModules/DownloadFile.php?download=flashcardsPythonTrace" .
                                                    "&contentID=" . $info[$i]["ContentID"] . "&userID=" . $_SESSION[SessionIndex['UserID']] . "'>
                                        <img src='../img/utilites-icon.png' title='Download the trace of flashcards Python operation (advanced)'>
                                    </a></td>";
                $trString .= "</tr>";
                echo $trString;
            }
        ?>
        </tbody>
    </table>
<script>
        onLoadFlashcardContents();
</script>
</div>

<div id="FlashcardTypeDiv" style="display: none">
</div>