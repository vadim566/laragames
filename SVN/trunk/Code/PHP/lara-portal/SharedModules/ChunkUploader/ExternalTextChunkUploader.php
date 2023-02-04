<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<style type="text/css">
#file {
	margin-top: 1em;
	margin-bottom: 1em;
}

#abort {
	background-color: #FA9F31;
	cursor: pointer;
	color: #000;
}

#abort:disabled {
	background-color: #ccc;
}
</style>
<!--added by Hanieh-->
<link rel="stylesheet" href="../css/MainContent.css">
<link rel="stylesheet" href="../css/TableToDiv.css">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>

<?php
    $now = new DateTime();
    echo '<script src="../SharedModules/ChunkUploader/chunk-uploader.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/ShowLoading/ShowLoading.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/jquery/jquery-1.12.4.js?' . $now->format('His') . '"></script>';
    echo '<script src="../SharedModules/jquery/jquery-ui.js?' . $now->format('His') . '"></script>';

    require_once '../../Config.php';
    require_once ROOT . 'class/Language.class.php';

    if(!isset($_SESSION[SessionIndex['UserID']]))
    {
        echo "Please Login again. <br />";
        echo "<a href='index.php?status=sessionExpired'>Click Here to Login</a>";
        die();
    }

?>
<!-- end of added by Hanieh-->
<div class="importLaraContent" id="importLaraContentDiv">

    <script type="text/javascript">
        chunk_uploader=new MyChunkUploader();
    </script>
    <div class="table">
        <input type="hidden" id="UploadType" name="UploadType" value="Text">
        <div class="tr">
            <div class="tdTXT">
                Upload content :
                <input type="file" id="file" onchange="upload_file(this.files[0]);">
                <label for="file">
                    <img src="../img/upload-icon.png" title="Import zip file">
                </label> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                <input
                    type="button" id="abort" disabled value="Abort"
                    onclick="if(confirm('Are you sure?'))chunk_uploader.abort();">
            </div>
        </div>
        <div class="tr">
            <div class="tdTXT">
                <div id="status"
                    style="position: absolute; width: 45%; text-align: center; margin-top: 5px;"></div>
                <div id="progress_bar"
                    style="width: 0; height: 100%; background-color: #00adee; text-align: center;"></div>
            </div>
        </div>

        <div class="tr">
            <div class="tdTXT">
                <fieldset id="transfer_result"
                    style="display: none; border: 1px solid #ccc; border-radius: 5px">

                    <legend>Transfer result</legend>
                    <table style="text-align: left">
                        <tr>
                            <th>Client file size</th>
                            <td>:</td>
                            <td id="client_file_size"></td>
                        </tr>
                        <tr>
                            <th>Server sent bytes</th>
                            <td>:</td>
                            <td id="server_sent_bytes"></td>
                        </tr>
                        <tr>
                            <th>Elapsed time</th>
                            <td>:</td>
                            <td id="elapsed_time"></td>
                        </tr>
                        <tr>
                            <th>Remote file name</th>
                            <td>:</td>
                            <td id="remote_file_name"></td>
                        </tr>
                        <tr>
                            <th>Remote file path</th>
                            <td>:</td>
                            <td id="remote_file_path"></td>
                        </tr>
                        <tr>
                            <th>Remote file size</th>
                            <td>:</td>
                            <td id="remote_file_size"></td>
                        </tr>
                        <tr>
                            <th>Remote file chunks</th>
                            <td>:</td>
                            <td id="remote_file_chunks"></td>
                        </tr>
                        <tr>
                            <th>Remote file CRC32</th>
                            <td>:</td>
                            <td id="remote_file_crc"></td>
                        </tr>
                    </table>
                </fieldset>
            </div>
        </div>
    </div>
</div>