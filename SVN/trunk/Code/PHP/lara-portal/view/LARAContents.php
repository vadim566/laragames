<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 6/10/2019
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

$where = " c.IsDeleted = 'NO' and c.CreatorID = :creatorID and c.ParentID is null";
$whereParam = array(":creatorID" => $_SESSION[SessionIndex['UserID']]);
$info = Content::FullSelect($where, $whereParam);
?>

<div class="LaraContents">
    <table id="TableOfContents" class="display" style="width:100%">
        <thead>
        <tr>
            <th>Text name</th>
            <th>Progress status</th>
            <th>Reading language</th>
            <th>Translation language</th>
            <th>Edit project</th>
            <th>Distribute project</th>
            <th>CALLect project</th>
            <th>Export zip file</th>
            <th>Delete</th>
           <th>Python trace</th>
        </tr>
        </thead>
        <tbody>
        <?php
            for($i = 0; $i < count($info); $i++)
            {
                $trString = "<tr>";
                $trString .= "<td style='text-align: center'>" . $info[$i]["ContentName"] . "</td>";
                $trString .= "<td style='text-align: center'>" . $info[$i]["ContentStatus"] . "</td>";
                $trString .= "<td style='text-align: center'>" . $info[$i]["L2Name"] . "</td>";
                $trString .= "<td style='text-align: center'>" . $info[$i]["L1Name"] . "</td>";
               //edit - distribute - collect
                if($info[$i]["CrowdsourcingStatus"] == "Distributed")
                {
                    $trString .= "<td style='text-align: center'>                                    
                                    <img src='../img/under-construction.png' title='Under construction by crowd-workers' >
                                </td>";
                    $trString .= "<td style='text-align: center'>
                               <img src='../img/cut-bw.png' title='Already distributed' >
                            </td>";
                }
                else
                {
                    $trString .= "<td style='text-align: center'>
                                    <a target='_blank' class='ShowLaraContent'
                                        href='NewLARAContent.php?Q0=" . $info[$i]["ContentID"] . "'> 
                                        <img src='../img/edit-icon.png' title='Change or add to your project' >
                                    </a>
                                </td>";
                    $trString .= "<td style='text-align: center'>
                               <img src='../img/cut.png' title='Distribute project' 
                               onclick='distributeContent(\"" . $info[$i]["ContentID"] . "\",\"" . $info[$i]["ContentName"] ."\");' >
                            </td>";

                }

                if($info[$i]["CrowdsourcingStatus"] == "None")
                {
                    $trString .= "<td style='text-align: center'>
                               <img src='../img/data-collection-bw.png' title='Not distributed' >
                            </td>";
                }
                else
                {
                    $trString .= "<td style='text-align: center'>
                               <img src='../img/data-collection.png' title='Collect project pieces' 
                               onclick='collectContent(\"" . $info[$i]["ContentID"] . "\",\"" . $info[$i]["ContentName"] ."\");' >
                            </td>";
                }

                if($info[$i]["HasMainConfig"] == "YES") {
                    $trString .= "<td style='text-align: center'>";
                    $ZipFolderName = str_replace(" ", "_", $info[$i]["ContentName"]) . "_export.zip";
                    $FolderDir = $info[$i]["DirName"];
                    $cmp = "&Q0=" . $info[$i]["ContentID"] . "&folderDir=" . $FolderDir . "&zipFolderName=" . $ZipFolderName;
                    $trString .= "<a target='_blank' id='FinalPackDL'
                                    href='../SharedModules/DownloadFile.php?download=finalPack" . $cmp . "'>
                                    <img src='../img/download-folder-icon.png' title='Download the zip file of whole project'>
                                    </a></td>";
                }
                else
                {
                    $trString .= "<td style='text-align: center'>
                                    <img src='../img/forbidden-icon.png' title='Not ready to download' >
                                  </td>";
                }
                //delete is here
                $trString .= "<td style='text-align: center'>
                               <img src='../img/delete.gif' title='Delete project' 
                               onclick='deleteContent(\"" . $info[$i]["ContentID"] . "\",\"" . $info[$i]["ContentName"] ."\");' >
                            </td>";
                $trString .= "<td style='text-align: center'>
                                   <a target='_blank' id='PythonTraceDL'
                                        href='../SharedModules/DownloadFile.php?download=pythonTrace&contentID=" . $info[$i]["ContentID"] . "'>
                                        <img src='../img/about.png' title='Download the trace of Python operation (advanced)'>
                                    </a></td>";
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

