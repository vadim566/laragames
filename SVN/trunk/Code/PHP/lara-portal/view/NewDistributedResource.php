<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 8/6/2019

 */

?>

<link rel="stylesheet" href="../css/MainContent.css">
<link rel="stylesheet" href="../css/TableToDiv.css">
<link rel="stylesheet" href="../SharedModules/jquery/jquery-ui.css">
<meta charset="utf-8">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

<?php
    $now = new DateTime();
    echo '<script src="../js/DistributedResource.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/jquery/jquery-1.12.4.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/jquery/jquery-ui.js?' . $now->format('His') . '"></script>';

require_once '../Config.php';
require_once '../SharedModules/ExtraModules.class.php';
require_once '../class/Language.class.php';
require_once '../class/DistributedResource.class.php';
require_once '../data/DistributedResource.data.php';

if(!isset($_SESSION[SessionIndex['UserID']]))
{
    echo "Please login again. <br />";
    echo "<a href='index.php?status=sessionExpired'>Click here to login</a>";
    die();
}

$drp_L2 = Language::LanguageDropBox("L2ID", true);
$drp_LanguageResources = DistributedResource::LanguageResourceDropBox("ParentID", true);

$resourceObj = array();

if(isset($_GET["Q0"]))
{
    $where = " ResourceID = :rID";
    $whereParam = array(":rID" => $_GET["Q0"]);
    $info = DistributedResource::SearchResource($where, $whereParam);
	if(count($info) != 0)
	{
        $resourceObj = FillDistributedResourceItems($info[0]);
    }
}
else
{
    $resourceObj = MakeEmptyResource();
}

$jsObjName = "ResourceVal";
echo ExtraModules::objToJS($resourceObj, $jsObjName);

echo '<script>onLoad();</script>';
?>

<div class="newResource">

    <div class="table ResourceError"  style="display: none">
        <div class="tr">
            <div class="tdTXT">
                <p class="ErrorMsg"></p>
            </div>
        </div>
    </div>


    <form method="POST" id="ResourceForm" enctype='multipart/form-data'>
        <input type="hidden" id="task" name="task" value="AddDistributedResource">
        <input type="hidden" id="ResourceID" name="ResourceID">
        <input type="hidden" id="UserID" name="UserID">

        <!--START OF Page-->
        <div class="table" id="firstStepData">
            <div id="GeneralDataInput" class="table">
                <div class="tr">
                    <div class="tdTitle">Resource Type:</div>
                    <div class="tdInput">
                        <input type="radio" id="ResourceType_Lng" name="ResourceType"  value="Language" >Language
                        <input type="radio"  id="ResourceType_Cnt" name="ResourceType"  value="Content" >Content
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Resource name:</div>
                    <div class="tdInput">
                        <input type="text" name="ResourceName" id="ResourceName"  size="20"
                               value=<?php echo $resourceObj->ResourceName; ?>>
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Web address:</div>
                    <div class="tdInput">
                        <input type="text" name="WebAddress" id="WebAddress"  size="20"
                               value=<?php echo $resourceObj->WebAddress; ?>>
                    </div>
                </div>
                <div class="tr">
                    <div class="tdTitle">Reading language:</div>
                    <div class="tdInput">
                        <?php echo $drp_L2; ?>
                    </div>
                </div>
            </div>

            <div id="ParentDataInputForContentResources" class="table">
                <div class="tr">
                    <div class="tdTitle">Language resource:</div>
                    <div class="tdInput">
                        <?php echo $drp_LanguageResources; ?>
                    </div>
                </div>
            </div>

            <div id="SaveInfo" class="table">
                <div class="tr">
                    <div class="tdButton">
                        <input type="button"  id="SaveResource" name="SaveResource"
                               onclick="SaveDistributedResource()" value="Save resource" >
                    </div>
                </div>
            </div>
        </div>
        <!--END OF Page-->
    </form>
    <div class="table ResourceError"  style="display: none">
        <div class="tr">
            <div class="tdTXT">
                <p class="ErrorMsg"></p>
            </div>
        </div>
    </div>
</div>