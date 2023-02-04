<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 13/07/2021
 * Time: 08:08 PM
 */
?>

<link rel="stylesheet" type="text/css" href="../SharedModules/dataTable/jquery.dataTables.css">
<script>
    $('.ShowLaraContent').click(function() {
        event.preventDefault();
        $("#mainContentDIV").load(this.getAttribute('href'));
    });
</script>

<?php

$now = new DateTime();
echo '<script type="text/javascript" charset="utf8" src="../js/LARAContent.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/dataTable/jquery.dataTables.js?' . $now->format('His') . '"></script>';
echo '<link rel="stylesheet" href="../css/MainContent.css?' . $now->format('His') . '">';

require_once '../Config.php';
require_once '../class/Content.class.php';

if(!isset($_SESSION[SessionIndex['UserID']]))
{
    echo "Please login again. <br />";
    echo "<a href='index.php?status=sessionExpired'>Click Here to Login</a>";
    die();
}

$where = " c.CrowdWorkerID is null and c.ParentID is not null";
$whereParam = array(":creatorID" => $_SESSION[SessionIndex['UserID']]);
$info = Content::FullSelect($where, $whereParam);
?>

<div class="LaraContents">
    <table id="TableOfContents" class="display" style="width:100%">
        <thead>
        <tr>
            <th>Text name</th>
            <th>Parent</th>
            <th>Reading language</th>
            <th>Translation language</th>
            <th>Requester</th>
            <th>Get it!</th>
        </tr>
        </thead>
        <tbody>
        <?php
        for($i = 0; $i < count($info); $i++)
        {
            $trString = "<tr>";
            $trString .= "<td style='text-align: center'>". $info[$i]["ContentName"] . "</td>";
            $trString .= "<td style='text-align: center'>" . $info[$i]["pContentName"] . "</td>";
            $trString .= "<td style='text-align: center'>" . $info[$i]["L2Name"] . "</td>";
            $trString .= "<td style='text-align: center'>" . $info[$i]["L1Name"] . "</td>";
            $trString .= "<td style='text-align: center'>" . $info[$i]["UserName"] . "</td>";

            $trString .= "<td style='text-align: center'>
                                <img src='../img/assign.png' title='View the last changes' 
                                    onclick='getTheTask(\"" . $info[$i]["ContentID"] . "\",\"" . $info[$i]["ContentName"] ."\");' >
                          </td>";
            $trString .= "</tr>";
            echo $trString;
        }
        ?>
        </tbody>
    </table>
    <script>
        onLoadLaraContents();
    </script>

</div>