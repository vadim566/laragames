<?php

require_once '../Config.php';
require_once 'FolderZipArchive.class.php';
require_once '../class/ExternalCommandsLogs.class.php';
require_once '../class/UserActivitiesLogs.class.php';
require_once '../class/DistributedResource.class.php';


class ExtraModules{

	static function CreateResponse($val)
	{
		if (is_string($val)) return '"'.addslashes($val).'"';
		if (is_numeric($val)) return $val;
		if ($val === null) return 'null';
		if ($val === true) return 'true';
		if ($val === false) return 'false';

		$assoc = false;
		$i = 0;
		foreach ($val as $k=>$v){
			if ($k !== $i++){
				$assoc = true;
				break;
			}
		}
		$res = array();
		foreach ($val as $k=>$v){
			$v = ExtraModules::CreateResponse($v);
			if ($assoc){
				$k = '"'.addslashes($k).'"';
				$v = $k.':'.$v;
			}
			$res[] = $v;
		}
		$res = implode(',', $res);
		return ($assoc)? '{'.$res.'}' : '['.$res.']';
	}

	static function objToJS($object, $jsObjName)
	{
		$objArr = get_object_vars($object);
		$retVal = "<script>var ". $jsObjName." = " . json_encode($objArr). "</script>";
		return $retVal;
	}

	static function LogIntoLDT()
	{
        $url = 'https://regulus.unige.ch/litedevtools/server/token';

		$query = http_build_query(LaraLDT);

		$header = array(
			"Content-Type: application/x-www-form-urlencoded",
			"Content-Length: ".strlen($query),
			"User-Agent:MyAgent/1.0");

		$ch = curl_init();
		curl_setopt($ch, CURLOPT_URL, $url);
		curl_setopt($ch, CURLOPT_POST, 1);
		curl_setopt($ch, CURLOPT_HEADER, 0);
		curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
		curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/4.0 (compatible;)");
		curl_setopt($ch, CURLOPT_HTTPHEADER,$header);
		curl_setopt($ch, CURLOPT_FRESH_CONNECT, 1);
		curl_setopt($ch, CURLOPT_FORBID_REUSE, 1);
		curl_setopt($ch, CURLOPT_TIMEOUT, 100);
		curl_setopt($ch, CURLOPT_POSTFIELDS, $query);

		$result = curl_exec($ch);

		$resultArray = array();

		if ($result === FALSE)
		{
			$resultArray["access_token"] = "LDTAuthenticationFailed";
			$result = ExtraModules::CreateResponse($resultArray);
			curl_close($ch);
            return $result;
		}
		else
		{
			curl_close($ch);
			return $result;
		}
	}

	static function CreateDir($dirAddress, $subDirNames = "")
	{
		if (!file_exists( $dirAddress ) || !is_dir($dirAddress))
		{
			if(! mkdir($dirAddress, 0777, true))
			{
				return "CreateDIRFailed";
			}
			else
			{
				if($subDirNames != "")
				{
					for($i = 0; $i < count($subDirNames); $i++)
					{
						$subDir = $dirAddress . "/" . array_keys($subDirNames)[$i];
                        if( !mkdir($subDir, 0777, true))
                        {
                            return "CreateSubDIRFailed";
                        }
					}
				}
				return "DIRCreated";
			}
		}
		else
		{
            if($subDirNames != "")
            {
                for($i = 0; $i < count($subDirNames); $i++)
                {
                    $subDir = $dirAddress . "/" . array_keys($subDirNames)[$i];
                    if (!file_exists( $subDir ) || !is_dir($subDir))
                    {
                        if (!mkdir($subDir, 0777, true)) {
                            return "CreateSubDIRFailed";
                        }
                    }
                }
            }
			return "DIRExists";
		}
	}

	static function RemoveDir($dir) {
		if (is_dir($dir)) {
			$objects = scandir($dir);
			foreach ($objects as $object) {
				if ($object != "." && $object != "..") {
					if (is_dir($dir."/".$object))
						ExtraModules::RemoveDir($dir."/".$object);
					else
						unlink($dir."/".$object);
				}
			}
			rmdir($dir);
		}
	}

	static function ExternalCmndLog($LogType, $LogData, $RelatedID, $RelatedPage, $ParentID = "")
	{
        $ExternalLog = new ExternalCommandsLogs();
		$ExternalLog->LogType = $LogType;
		$ExternalLog->LogData = str_replace('\'', '"', $LogData);
		$ExternalLog->LogDateTime = (new DateTime('now'))->format('Y-m-d H:i:s');
		$ExternalLog->UserID = $_SESSION[SessionIndex['UserID']];
		$ExternalLog->RelatedID = $RelatedID;
		$ExternalLog->RelatedPage = $RelatedPage;
		if($ParentID != "")
			$ExternalLog->ParentID = $ParentID;
        $ExternalLog->insert();

        if($ParentID != "")
            return true;

        $where = " LogDateTime = :logDateTime and UserID = :userID ";
		$whereParam = array(":logDateTime" => $ExternalLog->LogDateTime, ":userID" => $ExternalLog->UserID);
        return ExternalCommandsLogs::lastID($where, $whereParam);
	}

	static function UserActivityLog($RelatedPage, $resultArray, $resultMsg = "" )
	{
		$ActivityLog = new UserActivitiesLogs();
		if($resultMsg != "")
			$resultArray[0]["resultMsg"] = $resultMsg;
		$ActivityLog->LogData = (array_key_exists("nextPage", $resultArray[0])) ?
            $resultArray[0]["resultMsg"] . " #" . $resultArray[0]["nextPage"] : $resultArray[0]["resultMsg"];
		$ActivityLog->LogDateTime = (new DateTime('now'))->format('Y-m-d H:i:s');
		$ActivityLog->RelatedID = $resultArray[0]["id"];
		$ActivityLog->RelatedPage = $RelatedPage;
		$ActivityLog->UserID = $_SESSION[SessionIndex['UserID']];
		$ActivityLog->IPAddress = $_SERVER['REMOTE_ADDR'];
		$ActivityLog->insert();

		return true;
	}

	static function FileExists($fileName)
	{
		if(file_exists($_FILES[$fileName]['tmp_name']) && is_uploaded_file($_FILES[$fileName]['tmp_name']))
			return true;
		return false;
	}

	static function FileExtensionIsValid($fileName, $validExt)
	{
		$ext = pathinfo($_FILES[$fileName]["name"], PATHINFO_EXTENSION);
		if(in_array($ext, $validExt))
			return true;
		return false;
	}

    static function UploadFile($fileName, $fileDir, $file)
    {
        $fp = fopen($fileDir . $fileName, "w");
        fwrite($fp, fread(fopen($file ['tmp_name'], 'r'), $file['size']));
        fclose($fp);
        return true;
    }

    static function FileUnicodeIsValid($fileName) {
		$content = file_get_contents($_FILES[$fileName]['tmp_name']);
		if(mb_detect_encoding($content, "utf-8-sig, utf-8, iso-8859-1, utf-16le, utf-16be"))
			return true;
		return false;
	}

	static function KillProcess($resultArray, $resultMsg = "")
	{
	   // print_r($resultArray);die();
		if($resultMsg != "")
			$resultArray[0]["resultMsg"] = $resultMsg;
		$result = ExtraModules::CreateResponse($resultArray);
		echo $result;
		die();
	}

	static function BackupFile($sourceFile, $destinationFile)
    {
        if(file_exists($sourceFile))
            if(copy($sourceFile,$destinationFile))
                return true;
            else
                return false;
        return true;
    }

    static function JsonToCsv($bashFile, $csvFile, $csvBackupFile, $jsonFile, $contentID)
    {
        $fp = fopen( $bashFile, "w");
        $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py json_to_csv  " .
            $jsonFile . " " . $csvFile . " 2>&1;";
        fwrite($fp, $command);

        if($csvBackupFile != "")
            ExtraModules::BackupFile($csvFile, $csvBackupFile);
        $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentID, ContentRelatedPage);
        $output = shell_exec('bash < '  . $bashFile );
        ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentID, ContentRelatedPage, $LogID);

        if(strpos($output, "*** Error") === false)
            return true;
        return false;
    }

    static function CsvToJson($bashFile, $jsonFile, $jsonBackupFile, $csvFile, $contentID)
    {
        $fp = fopen( $bashFile, "w");
        $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py csv_to_json  " .
            $csvFile . " " . $jsonFile . " 2>&1;";
        fwrite($fp, $command);

        if($jsonBackupFile != "")
            ExtraModules::BackupFile($jsonFile, $jsonBackupFile);
        $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentID, ContentRelatedPage);
        $output = shell_exec('bash < '  . $bashFile );
        ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentID, ContentRelatedPage, $LogID);

        if(strpos($output, "*** Error") === false)
            return true;
        return false;
    }

    static function WordTypeOrLemmaJsonToCsv($bashFile, $csvFile, $csvBackupFile, $jsonFile, $contentID)
    {
        $fp = fopen( $bashFile, "w");
        $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py word_type_or_lemma_json_to_csv  " .
            $jsonFile . " " . $csvFile . " 2>&1;";
        fwrite($fp, $command);

        if($csvBackupFile != "")
            ExtraModules::BackupFile($csvFile, $csvBackupFile);
        $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentID, ContentRelatedPage);
        $output = shell_exec('bash < '  . $bashFile );
        ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentID, ContentRelatedPage, $LogID);

        if(strpos($output, "*** Error") === false)
            return true;
        return false;
    }


    static function MergeUpdateTranslationSpreadsheet($bashFile, $csvMainFile, $csvMainBackFile, $csvNewMaterial, $contentID)
    {
        $fp = fopen( $bashFile, "w");
        $command = LaraEnv . " " . PythonCmnd . " " . PythonDir . "lara_run_for_portal.py merge_update_translation_spreadsheet " .
            $csvMainFile . " " . $csvNewMaterial. " 2>&1;";
        fwrite($fp, $command);

        ExtraModules::BackupFile($csvMainFile, $csvMainBackFile);
        $LogID = ExtraModules::ExternalCmndLog(EL_TypePythonCmnd, $command, $contentID, ContentRelatedPage);
        $output = shell_exec('bash < '  . $bashFile );
        ExtraModules::ExternalCmndLog(EL_TypePythonRes, $output, $contentID, ContentRelatedPage, $LogID);

        if(strpos($output, "*** Error") === false)
            return true;

        $resultArray[0]["id"] = $contentID;
        $resultArray[0]["resultMsg"] = "FailedToMergeCsv";
        ExtraModules::UserActivityLog(ContentRelatedPage, $resultArray);
        ExtraModules::KillProcess($resultArray);
    }
}