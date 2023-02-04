<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 8/23/2019
 * Time: 18:08 PM
 */
?>

<link rel="stylesheet" type="text/css" href="../css/MainContent.css">
<link rel="stylesheet" type="text/css" href="../SharedModules/dataTable/jquery.dataTables.css">
<link rel="stylesheet" type="text/css" href="../SharedModules/jquery/jquery-ui.css">
 <script>
        $('.NavigateHistory').click(function() {
            event.preventDefault();
            $("#mainContentDIV").load(this.getAttribute('href'));
        });
</script>


<?php

$now = new DateTime();
echo '<script type="text/javascript" charset="utf8" src="../js/ReadingHistory.js?' . $now->format('His') . '"></script>';
echo '<script src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/jquery/jquery-1.12.4.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/jquery/jquery-ui.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/dataTable/jquery.dataTables.js?' . $now->format('His') . '"></script>';

require_once '../Config.php';
require_once '../class/ReadingHistory.class.php';

if(!isset($_SESSION[SessionIndex['UserID']]))
{
    echo "Please login again. <br />";
    echo "<a href='index.php?status=sessionExpired'>Click here to login</a>";
    die();
}

$where = " UserID = :userID and IsDeleted = 'NO'";
$whereParam = array(":userID" => $_SESSION[SessionIndex['UserID']]);
$info = ReadingHistory::FullSelect($where, $whereParam);
?>



<div class="ReadingHistories">
    <table id="TableOfHistories" class="display" style="width:100%">
        <thead>
        <tr>
            <th>Reading history</th>
            <th>Reading language</th>
            <th>Translation language</th>
            <th>Modify</th>
            <th>View texts</th>
            <th>Delete</th>
            <th>Python trace</th>
        </tr>
        </thead>
        <tbody>
        <?php
            for($i = 0; $i < count($info); $i++)
            {
                $trString = "<tr>";
                $trString .= "<td style='text-align: center'>" . $info[$i]["ReadingHistoryName"] . "</td>";
                $trString .= "<td style='text-align: center'>" . $info[$i]["L2Name"] . "</td>";
                $trString .= "<td style='text-align: center'>" . $info[$i]["L1Name"] . "</td>";
                $trString .= "<td style='text-align: center'>
                                    <a target='_blank' class='NavigateHistory'
                                        href='NewReadingHistory.php?Q0=" . $info[$i]["ReadingHistoryID"] . "'>
                                        <img src='../img/edit-icon.png' title='Modify history' >
                                    </a>
                                </td>";
                $trString .= "<td style='text-align: center'>
                                <img src='../img/nav-icon.png' title='View or read texts in history' class='pointerCursor'
                                     onclick='ShowListOfHistoryResources(\"" . $info[$i]["ReadingHistoryID"] . "\",\"" . $info[$i]["ReadingHistoryName"] ."\");' >
                                </td>";
                //delete is here
                $trString .= "<td style='text-align: center'>
                               <img src='../img/delete.gif' title='Delete content' class='pointerCursor'
                               onclick='deleteHistory(\"" . $info[$i]["ReadingHistoryID"] . "\",\"" . $info[$i]["ReadingHistoryName"] ."\");' >
                            </td>";
                $trString .= "<td style='text-align: center'>
                                   <a target='_blank' id='PythonTraceDL'
                                        href='../SharedModules/DownloadFile.php?download=pythonTrace&rhID=" . $info[$i]["ReadingHistoryID"] . "'>
                                        <img src='../img/about.png' title='Download Python trace (advanced)'>
                                    </a></td>";

                $trString .= "</tr>";
                echo $trString;
            }
        ?>
        </tbody>
    </table>
<script>
    onLoadReadingHistories();
</script>

   </div>
<div id="ResourcesDialog"></div>
