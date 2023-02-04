<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 8/10/2019
 * Time: 08:08 PM
 */
?>

<link rel="stylesheet" type="text/css" href="../SharedModules/dataTable/jquery.dataTables.css">
 <script>
        $('.ShowResource').click(function() {
            event.preventDefault();
            $("#mainContentDIV").load(this.getAttribute('href'));
        });
</script>


<?php

$now = new DateTime();
echo '<script type="text/javascript" charset="utf8" src="../js/DistributedResource.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
echo '<script type="text/javascript" charset="utf8" src="../SharedModules/dataTable/jquery.dataTables.js?' . $now->format('His') . '"></script>';
echo '<link rel="stylesheet" href="../css/MainContent.css?' . $now->format('His') . '">';

require_once '../Config.php';
require_once '../class/DistributedResource.class.php';

if(!isset($_SESSION[SessionIndex['UserID']]))
{
    echo "Please login again. <br />";
    echo "<a href='index.php?status=sessionExpired'>Click Here to Login</a>";
    die();
}

$resourceType = $_REQUEST["rType"];

$where = " dr.IsDeleted = 'NO' and ResourceType = :resourceType";
$whereParam = array(":resourceType" => $resourceType);
$info = DistributedResource::FullSelect($where, $whereParam);

if($resourceType == 'Content')
    $nameTitle = "Text name";
else if($resourceType == 'Language')
    $nameTitle = "Resource name";
?>

<div class="LaraContents">
    <table id="TableOfDistributed" class="display" style="width:100%">
        <thead>
        <tr>
            <th>
                <?php echo $nameTitle; ?>
            </th>
            <th>Creator</th>
            <th>Language</th>
            <?php if($resourceType == 'Language')
            {
                echo  "<th>Export zip file</th>";
            }?>
            <th>Unpublish</th>
        </tr>
        </thead>
        <tbody>
        <?php
            for($i = 0; $i < count($info); $i++)
            {
                $trString = "<tr>";
                $trString .= "<td style='text-align: center'>";
                if($resourceType == 'Content' && !empty($info[$i]["contentWebAddress"]))
                    $trString .= "<a href = '" . $info[$i]["contentWebAddress"]  . "' target='_blank'>" . $info[$i]["ResourceName"] . "</a>";
                else
                    $trString .= $info[$i]["ResourceName"] ;
                $trString .= "</td>" ;
                $trString .= "<td style='text-align: center'>" . $info[$i]["UserName"] . "</td>";
                $trString .= "<td style='text-align: center'>" . $info[$i]["LanguageName"] . "</td>";

                if($resourceType == 'Language')
                {
                    //downloading language resource

                    $trString .= "<td style='text-align: center'>";
                    $ZipFolderName = str_replace(" ", "_", $info[$i]["ResourceName"]) . "_export.zip";
                    $FolderDir = $info[$i]["ResourceName"];
                    $cmp = "&folderDir=" . $FolderDir . "&zipFolderName=" . $ZipFolderName;
                    $trString .= "<a target='_blank' id='FinalLangResDL'
                                    href='../SharedModules/DownloadFile.php?download=finalResourcePack" . $cmp . "'>
                                    <img src='../img/download-folder-icon.png' title='Download the zip file of language resource'>
                                    </a></td>";
                }

                if($info[$i]["UserID"] == $_SESSION[SessionIndex['UserID']])
                {
                    //unpublishing is here
                    $trString .= "<td style='text-align: center'>
                                   <img src='../img/delete.gif' title='Remove from published resources' 
                                     onclick='deleteResource(\"" . $info[$i]["ResourceID"] .
                                                             "\",\"" . $info[$i]["ResourceName"] .
                                                             "\",\"" .  $resourceType . "\");' >
                                   </td>";
                }
                else
                {
                    $trString .= "<td style='text-align: center'>
                                    <img src='../img/forbidden-icon.png' title='unpublish forbidden'>
                                  </td>";
                }

                $trString .= "</tr>";
                echo $trString;
            }
        ?>
        </tbody>
    </table>

<script>
    onLoadDistributedList();
</script>
    <table style="width: 90%; font-weight: bold; font-size: 20px">
        <tr>
            <td >
                <a target='_blank' id='allResources' href='../SharedModules/DownloadFile.php?download=allResources'>
                    <img src="../img/download-icon.png" title="Download resources json file">
                </a></td>
            </td>
        </tr>
    </table>
   </div>

