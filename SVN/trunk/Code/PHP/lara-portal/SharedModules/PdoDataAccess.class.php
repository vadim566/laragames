<?php


define("PDONULL", "%pdonull%");
define("PDONOW", "now()");
define("DEBUGQUERY", true);
require_once __DIR__ . '/../Config.php';
include_once 'ExceptionHandler.class.php';
require_once 'DataMember.class.php';
require_once 'InputValidation.class.php';

class PdoDataAccess extends ExceptionHandler
{
	private static $DB;
	private static $statements = array();
	private static $queryString = "";
	private static $executionTime = "";
	private static $defaultDB = "";

	function  __construct() {
		parent::__construct();
	}
	
	private static function CorrectFarsiString($query)
	{
		$ar_ya = "ي";
      	$fa_ya = "ی";
      	$ar_kaf = "ك";
      	$fa_kaf = "ک";
      	$trans = array($ar_ya => $fa_ya , $ar_kaf => $fa_kaf, "¬" => " ");
      	
      	return strtr($query, $trans);
	}
	
	public static function getPdoObject($_host = "", $_user = "", $_pass = "", $_default_db = "",$ShowException=false)
	{
		if($_host != "" && $_user != "" && $_pass != "" && $_default_db != "")
		{
			try{
				self::$defaultDB = $_default_db;
				return new PDO("mysql:host=" . $_host . ";dbname=" . $_default_db,
								$_user,
								$_pass,
								array(
									PDO::MYSQL_ATTR_INIT_COMMAND =>  "SET NAMES utf8",
									PDO::MYSQL_ATTR_LOCAL_INFILE => true
								));
			}
	 	        catch (PDOException $e) 
		        {
					if ($ShowException)
							echo $e->getMessage().'<br>';
					echo " error connecting database1\n";
					die();			
			}
			return null;	
		}
		
		if(!isset(self::$DB))
		{
			try{
			    $_host = LaraDB['host'];
			    $_user = LaraDB['user'];
			    $_pass = LaraDB['pass'];
			    $_default_db = LaraDB['database'];
				self::$defaultDB = $_default_db;
				
				self::$DB = new PDO("mysql:host=" . $_host . ";dbname=" . $_default_db,
									$_user,
									$_pass,
									array(
										PDO::MYSQL_ATTR_INIT_COMMAND =>  "SET NAMES utf8",
										PDO::MYSQL_ATTR_LOCAL_INFILE => true
									));
				
				return self::$DB;
		    }
		    catch (PDOException $e) 
		    {
				if ($ShowException)
						echo $e->getMessage().'<br>';
				echo " error connecting database2\n";
				die();		
			}
			return null;	
		}
		else 
			return self::$DB;
	}
	
	public static function FillObjectByArray($obj, $record)
	{
		$keys = array_keys(get_object_vars($obj));

		for($i=0; $i < count($keys); $i++)
			if(isset($record[$keys[$i]]))
			{
				$record[$keys[$i]] = preg_replace('/\'/', "\\'", $record[$keys[$i]]);
				if($record[$keys[$i]] == "NULL")
					$obj->{ $keys[$i] } = null;
				else 
					$obj->{ $keys[$i] } = $record[$keys[$i]];
			}
		return true;
	}

	public static function FillObjectByJsonData($obj, $jsonData)
	{
		$st = stripslashes(stripslashes($jsonData));
		$data = json_decode($st);
		
		return self::FillObjectByObject($data, $obj);
	}

	public static function FillObjectByObject($sourceObj, $destinationObj)
	{
		$src_keys = array_keys(get_object_vars($sourceObj));
		$dst_keys = array_keys(get_object_vars($destinationObj));
		
		for($i=0; $i < count($src_keys); $i++)
		{
			$index = array_search($src_keys[$i], $dst_keys);
			
			if(is_int($src_keys[$i]))
				continue;
			
			if($index !== false && !isset($destinationObj->$src_keys[$i]))
				$destinationObj->{ $src_keys[$i] } = $sourceObj->{ $src_keys[$i] };
		}
		return true;
	}

	public static function FillObject($obj, $query, $whereParams = array(), $pdoObject = null)
	{
		$PDO_Obj = $pdoObject != null ? $pdoObject : self::getPdoObject();
		/*@var $PDO_Obj PDO*/
		//-------------------
		$mainQuery = $query;
		
		$statement = $PDO_Obj->prepare($query);
		
		$keys = array_keys($whereParams);
		for($i=0; $i < count($keys); $i++)
		{
			$st = (is_int($keys[$i])) ? $keys[$i] + 1 : $keys[$i];
			$whereParams[$keys[$i]] = self::CorrectFarsiString($whereParams[$keys[$i]]);
			$statement->bindParam($st, $whereParams[$keys[$i]]);
			
			if((is_int($keys[$i])))
				$mainQuery = preg_replace("/\?/", "'".$whereParams[$keys[$i]]."'", $mainQuery, 1);
			else
				$mainQuery = str_replace ($keys[$i], "'".$whereParams[$keys[$i]]."'", $mainQuery);
		}
		$statement->setFetchMode( PDO::FETCH_INTO, $obj);
		
		//.............................
		$startTime = microtime(true);
		$statement->execute();
		$endTime = microtime(true);
		self::$executionTime = $endTime - $startTime;
		self::$statements[$PDO_Obj->getAttribute(PDO::ATTR_CONNECTION_STATUS)] = $statement;
		self::$queryString = $mainQuery;
		self::LogQueryToDB();
		//.............................
		if($statement->errorCode() == "00000")
		{
			$obj = $statement->fetch( PDO::FETCH_INTO );
			$statement->closeCursor();
			return true;
		}
		
		parent::PushException($statement->errorInfo());
		return false;
	}

	public static function runquery($query, $whereParams = array(), $pdoObject = null)
	{
		$PDO_Obj = $pdoObject != null ? $pdoObject : self::getPdoObject();
		/*@var $PDO_Obj PDO*/
		//-------------------
		$mainQuery = $query;
		
		$statement = $PDO_Obj->prepare(self::CorrectFarsiString($query));
		
		if(!is_array($whereParams))
			$whereParams = array($whereParams);
		
		$keys = array_keys($whereParams);
		for($i=0; $i < count($keys); $i++)
		{
			$st = (is_int($keys[$i])) ? $keys[$i] + 1 : $keys[$i];
			$whereParams[$keys[$i]] = self::CorrectFarsiString($whereParams[$keys[$i]]);
			$statement->bindParam($st, $whereParams[$keys[$i]]);
			
			if((is_int($keys[$i])))
				$mainQuery = preg_replace("/\?/", "'".$whereParams[$keys[$i]]."'", $mainQuery, 1);
			else
				$mainQuery = str_replace ($keys[$i], "'".$whereParams[$keys[$i]]."'", $mainQuery);
		}
		//.............................
		$startTime = microtime(true);
		$statement->execute();
		$endTime = microtime(true);
		self::$executionTime = $endTime - $startTime;
		self::$statements[$PDO_Obj->getAttribute(PDO::ATTR_CONNECTION_STATUS)] = $statement;
		self::$queryString = $mainQuery;
		self::LogQueryToDB();
		//.............................	

		if($statement->errorCode() == "00000")
			return $statement->fetchAll();
		parent::PushException(array_merge($statement->errorInfo(), array("query" => $statement->queryString)));
		return false;
	} 
	
	public static function fetchAll($statement, $start, $limit)
	{
		$temp = array();
		
		$index = 0;
		while($index < $start*1)
		{
			if(!$statement->fetch(PDO::FETCH_ASSOC))
				return $temp;
			$index++;
		}
		
		while($index < $start*1 + $limit*1)
		{
			$row = $statement->fetch(PDO::FETCH_ASSOC);
			if(!$row)
				return $temp;
			$temp[] = $row;
			$index++;
		}		
		return $temp;
	}

	public static function insert($tableName, $obj, $pdoObject = null)
	{
		$PDO_Obj = $pdoObject != null ? $pdoObject : self::getPdoObject();
		/*@var $PDO_Obj PDO*/
		//-------------------
		$Arr = self::GetObjectMembers($obj, "insert");
		if($Arr === false)
		{
			ExceptionHandler::PushException("Error in Input Data");
			return false;
		}
		$KeyArr = array_keys($Arr);
		//.................................................
		$flds = "";
		$values = "";
		for($i=0; $i < count($KeyArr); $i++)
		{
			$st = $Arr[$KeyArr[$i]];

			if($st === PDONULL || $st === "")
				$st = null;
			else if($st === PDONOW)
			{
				$flds .= $KeyArr[$i] . ",";
				$values .= "now(),";
			}else
			{
				$flds .= $KeyArr[$i] . ",";
				$values .= ":fld" . ($i<10 ? "0" : "") . $i . ",";
			}
		}
		$flds = substr($flds, 0, strlen($flds) - 1);
		$values = substr($values, 0, strlen($values) - 1);

		//.................................................
		$mainQuery = "insert into " . $tableName . "(" . $flds . ") values (" . $values . ")";
		$statement = $PDO_Obj->prepare("insert into " . $tableName . "(" . $flds . ") values (" . $values . ")");

		for($i=0; $i < count($KeyArr); $i++)
		{
			$Arr[$KeyArr[$i]] = self::CorrectFarsiString($Arr[$KeyArr[$i]]);
			if($Arr[$KeyArr[$i]] !== PDONULL && $Arr[$KeyArr[$i]] !== "" && $Arr[$KeyArr[$i]] !== PDONOW)
			{
				$statement->bindValue(":fld" . ($i<10 ? "0" : "") . $i, $Arr[$KeyArr[$i]]);
				$mainQuery = str_replace(":fld" . ($i<10 ? "0" : "") . $i, "'".$Arr[$KeyArr[$i]]."'", $mainQuery);
			}
		}
		//.............................
		$startTime = microtime(true);
		$statement->execute();
		$endTime = microtime(true);

		self::$executionTime = $endTime - $startTime;
		self::$statements[$PDO_Obj->getAttribute(PDO::ATTR_CONNECTION_STATUS)] = $statement;
		self::$queryString = $mainQuery;
		self::LogQueryToDB();
		//.............................
		if($statement->errorCode() == "00000")
			return true;

		parent::PushException($statement->errorInfo());
		return false;
	}

	public static function update($tableName, $obj, $where = "", $whereParams = array(), $pdoObject = null)
	{
       
		$PDO_Obj = $pdoObject != null ? $pdoObject : self::getPdoObject();
		/*@var $PDO_Obj PDO*/
		//-------------------
		
		$Arr = self::GetObjectMembers($obj, "update");
		if($Arr === false)
		{
			ExceptionHandler::PushException("Error in Input Data");
			return false;
		}
		$KeyArr = array_keys($Arr);


		$flds = "";
		for($i=0; $i < count($KeyArr); $i++)
		{
			$st = $Arr[$KeyArr[$i]];
			if($st === PDONULL || $st === "")
			{
				$flds .= $KeyArr[$i] . "=null,";
			}
			else if($st === PDONOW)
			{
				$flds .= $KeyArr[$i] . "=now(),";
			}
			else 
			{
				$flds .= $KeyArr[$i] . "=:fld" . ($i<10 ? "0" : "") . $i . ",";
			}
		}
		$flds = substr($flds, 0, strlen($flds) - 1);
		$where = ($where != "") ? " where " . $where : "";
		$mainQuery = "update " . $tableName . " set " . $flds . $where;
		$statement = $PDO_Obj->prepare("update " . $tableName . " set " . $flds . $where);
		$keys = array_keys($whereParams);
		for($i=0; $i < count($keys); $i++)
		{
			$whereParams[$keys[$i]] = self::CorrectFarsiString($whereParams[$keys[$i]]);
			$st = (is_int($keys[$i])) ? $keys[$i] + 1 : $keys[$i];
			$statement->bindParam($st, $whereParams[$keys[$i]]);

			if((is_int($keys[$i])))
				$mainQuery = preg_replace("/\?/", "'".$whereParams[$keys[$i]]."'", $mainQuery, 1);
			else
				$mainQuery = str_replace ($keys[$i], "'".$whereParams[$keys[$i]]."'", $mainQuery);
		}

		for($i=0; $i < count($KeyArr); $i++)
		{
			$Arr[$KeyArr[$i]] = self::CorrectFarsiString($Arr[$KeyArr[$i]]);
			if($Arr[$KeyArr[$i]] !== PDONULL && $Arr[$KeyArr[$i]] !== "" && $Arr[$KeyArr[$i]] !== PDONOW)
			{
				$statement->bindParam(":fld" . ($i<10 ? "0" : "") . $i, $Arr[$KeyArr[$i]]);
				$mainQuery = str_replace(":fld" . ($i<10 ? "0" : "") . $i, "'".$Arr[$KeyArr[$i]]."'", $mainQuery);
			}
		}

		//.............................
		$startTime = microtime(true);
		$statement->execute();
		$endTime = microtime(true);
		self::$executionTime = $endTime - $startTime;
		self::$statements[$PDO_Obj->getAttribute(PDO::ATTR_CONNECTION_STATUS)] = $statement;
		self::$queryString = $mainQuery;
		self::LogQueryToDB();
		//.............................
		if($statement->errorCode() == "00000")
			return true;

		parent::PushException($statement->errorInfo());
		return false;
	}
	
	public static function replace($tableName, $obj, $pdoObject = null)
	{	
		$PDO_Obj = $pdoObject != null ? $pdoObject : self::getPdoObject();
		
		$Arr = self::GetObjectMembers($obj, "");
		$KeyArr = array_keys($Arr);
		//.................................................		
		$flds = "";
		$flds2 = "";
		$values = "";
		for($i=0; $i < count($KeyArr); $i++)
		{
			$st = $Arr[$KeyArr[$i]];
			$flds .= $KeyArr[$i] . ",";
			$values .= ":fld" . $i . ",";				
						
			if($st === PDONULL || $st === "")
			{
				$flds2 .= $KeyArr[$i] . "=null,";
			}
			else if($st === PDONOW)
			{
				$flds2 .= $KeyArr[$i] . "=now(),";
			}
			else
			{
				$flds2 .= $KeyArr[$i] . "=:fld" . $i . ",";
			}
		}
		$flds = substr($flds, 0, strlen($flds) - 1);
		$flds2 = substr($flds2, 0, strlen($flds2) - 1);
		$values = substr($values, 0, strlen($values) - 1);
		//.................................................
		$query = "insert into " . $tableName . "(" . $flds . ") values (" . $values . ")
			ON DUPLICATE KEY UPDATE " . $flds2;
		$mainQuery = $query;
		
		$statement = $PDO_Obj->prepare($query);
		
		for($i=0; $i < count($KeyArr); $i++)
		{
			$st = $Arr[$KeyArr[$i]];
			$statement->bindValue(":fld" . $i, self::CorrectFarsiString($st));
			
			$mainQuery = str_replace(":fld" . $i, "'".self::CorrectFarsiString($st)."'", $mainQuery);
		}
		
		//.............................
		$startTime = microtime(true);
		$statement->execute();
		$endTime = microtime(true);
		self::$executionTime = $endTime - $startTime;
		self::$statements[$PDO_Obj->getAttribute(PDO::ATTR_CONNECTION_STATUS)] = $statement;
		self::$queryString = $mainQuery;
		self::LogQueryToDB();
		//.............................
		if($statement->errorCode() == "00000")
			return true;

		parent::PushException($statement->errorInfo());
		return false;
	}

	public static function delete($tableName, $where = "", $whereParams = array(), $pdoObject = null)
	{
		$PDO_Obj = $pdoObject != null ? $pdoObject : self::getPdoObject();
			
		$where = ($where != "") ? " where " . $where : "";
		$statement = $PDO_Obj->prepare("delete from " . $tableName . $where);
		$mainQuery = "delete from " . $tableName . $where;
		
		$keys = array_keys($whereParams);
		for($i=0; $i < count($keys); $i++)
		{
			$whereParams[$keys[$i]] = self::CorrectFarsiString($whereParams[$keys[$i]]);
			$st = (is_int($keys[$i])) ? $keys[$i] + 1 : $keys[$i];
			$statement->bindParam($st, $whereParams[$keys[$i]]);
			
			if((is_int($keys[$i])))
				$mainQuery = preg_replace("/\?/", "'".self::CorrectFarsiString($whereParams[$keys[$i]])."'", $mainQuery, 1);
			else
				$mainQuery = str_replace ($keys[$i], "'".self::CorrectFarsiString($whereParams[$keys[$i]])."'", $mainQuery);
		}

		//.............................
		$startTime = microtime(true);
		$statement->execute();
		$endTime = microtime(true);
		self::$executionTime = $endTime - $startTime;
		self::$statements[$PDO_Obj->getAttribute(PDO::ATTR_CONNECTION_STATUS)] = $statement;
		self::$queryString = $mainQuery;
		self::LogQueryToDB();
		//.............................
		if($statement->errorCode() == "00000")
			return true;

		parent::PushException($statement->errorInfo());
		return false;
	}
	
	public static function GetLastID($tableName, $field, $where = "", $whereParams = array(), $pdoObject = null)
	{
		$PDO_Obj = $pdoObject != null ? $pdoObject : self::getPdoObject();
			
		$where = ($where != "") ? " where " . $where : "";
		$statement = $PDO_Obj->prepare("select ifnull(max($field),0) as id from $tableName" . $where);
		$mainQuery = "select ifnull(max($field),0) as id from $tableName" . $where;
		
		$keys = array_keys($whereParams);
		for($i=0; $i < count($keys); $i++)
		{
			$st = (is_int($keys[$i])) ? $keys[$i] + 1 : $keys[$i];
			$whereParams[$keys[$i]] = self::CorrectFarsiString($whereParams[$keys[$i]]);
			$statement->bindParam($st, $whereParams[$keys[$i]]);
			
			if((is_int($keys[$i])))
				$mainQuery = preg_replace("/\?/", "'".self::CorrectFarsiString($whereParams[$keys[$i]])."'", $mainQuery, 1);
			else
				$mainQuery = str_replace ($keys[$i], "'".self::CorrectFarsiString($whereParams[$keys[$i]])."'", $mainQuery);
		}
		
		$statement->execute();
		//.............................
		self::$statements[$PDO_Obj->getAttribute(PDO::ATTR_CONNECTION_STATUS)] = $statement;
		//.............................
		self::$queryString = $mainQuery;
		//.............................
		if($statement->errorCode() == "00000")
		{
			$dt = $statement->fetchAll();
			return (count($dt) != 0) ? $dt[0][0] : 0;
		}

		parent::PushException($statement->errorInfo());
		return false;
	}

	public static function RecordExist($tableName, $obj)
	{
		$PDO_Obj = self::getPdoObject();
		/*@var $PDO_Obj PDO*/
		//-------------------

		$Arr = self::GetObjectMembers($obj, "update");
		if($Arr === false)
			return false;
		$KeyArr = array_keys($Arr);

		$where = "1=1";
		for($i=0; $i < count($KeyArr); $i++)
		{
			$st = $Arr[$KeyArr[$i]];
			if($st === PDONULL || $st === "")
			{
				$where .= " AND " . $KeyArr[$i] . " is null";
			}
			else if($st === PDONOW)
			{
				$where .= " AND " . $KeyArr[$i] . "=now()";
			}
			else 
			{
				$where .= " AND " . $KeyArr[$i] . "=:fld" . ($i<10 ? "0" . $i : $i);
			}
		}

		$mainQuery = "select * from " . $tableName . " where " . $where;
		$statement = $PDO_Obj->prepare($mainQuery);

		for($i=0; $i < count($KeyArr); $i++)
		{
			$st = $Arr[$KeyArr[$i]];
			if($st !== PDONULL && $st !== "" && $st !== PDONOW)
			{
				$statement->bindParam(":fld" . ($i<10 ? "0" . $i : $i), self::CorrectFarsiString($st));
				$mainQuery = str_replace(":fld" . ($i<10 ? "0" . $i : $i), "'".self::CorrectFarsiString($st)."'", $mainQuery);
			}
		}

		//.............................
		$startTime = microtime(true);
		$statement->execute();
		$endTime = microtime(true);
		self::$executionTime = $endTime - $startTime;
		self::$statements[$PDO_Obj->getAttribute(PDO::ATTR_CONNECTION_STATUS)] = $statement;
		self::$queryString = $mainQuery;
		self::LogQueryToDB();
		//.............................
		if($statement->errorCode() == "00000")
			return $statement->rowCount() != 0;

		parent::PushException($statement->errorInfo());
		return false;
	}
	
	public static function GetLatestQueryString()
	{
		if(self::$queryString != "")
			return self::$queryString;
	}
	
	public static function runquery_photo($query, $photoParams = array() , $whereParams = array(), $pdoObject = null)
	{
		
		$PDO_Obj = $pdoObject != null ? $pdoObject : self::getPdoObject();
		/*@var $PDO_Obj PDO*/
		//-------------------
		$mainQuery = $query;
		
		$statement = $PDO_Obj->prepare(self::CorrectFarsiString($query));
		
		if(!is_array($whereParams))
			$whereParams = array($whereParams);
		
		$index = 1;
		
		$keys = array_keys($photoParams);
		for($i=0; $i < count($keys); $i++)
		{
			$st = (is_int($keys[$i])) ? $index++ : $keys[$i];
			$statement->bindParam($st, $photoParams[$keys[$i]], PDO::PARAM_LOB);
		}
		
		$keys = array_keys($whereParams);
		for($i=0; $i < count($keys); $i++)
		{
			$st = (is_int($keys[$i])) ? $index++ : $keys[$i];
			$whereParams[$keys[$i]] = self::CorrectFarsiString($whereParams[$keys[$i]]);
			$statement->bindParam($st, $whereParams[$keys[$i]]);
			if((is_int($keys[$i])))
				$mainQuery = preg_replace("/\?/", "'".$whereParams[$keys[$i]]."'", $mainQuery, 1);
			else
				$mainQuery = str_replace ($keys[$i], "'".$whereParams[$keys[$i]]."'", $mainQuery);
		}
		
		//.............................
		$startTime = microtime(true);
		$statement->execute();
		$endTime = microtime(true);
		self::$executionTime = $endTime - $startTime;
		self::$statements[$PDO_Obj->getAttribute(PDO::ATTR_CONNECTION_STATUS)] = $statement;
		self::$queryString = $mainQuery;
		self::LogQueryToDB();
		//.............................	
		
		if($statement->errorCode() == "00000")
			return $statement->fetchAll();

		parent::PushException(array_merge($statement->errorInfo(), array("query" => $statement->queryString)));
		return false;
	}
	
	private static function LogQueryToDB()
	{
		if(DEBUGQUERY === false)
			return;

		$pdo = self::getPdoObject();
		$statement = self::$statements[$pdo->getAttribute(PDO::ATTR_CONNECTION_STATUS)];

		$logPage = $_SERVER['SERVER_NAME'].$_SERVER['PHP_SELF'];
		$logQuery = self::$queryString . ($statement->errorCode() == "00000" ? "" : "\n\n" . implode(",", $statement->errorInfo()));
		$logUserID = isset($_SESSION[SessionIndex['UserID']]) ? $_SESSION[SessionIndex['UserID']] : "-1";
		$logIPAddress = $_SERVER['REMOTE_ADDR'];
		$logExecutionTime = self::$executionTime;
		$logQueryStatus = $statement->errorCode() == "00000" ? "SUCCESS" : "FAILED";
		$logDB = self::$defaultDB;
		$logExecuteDateTime = (new DateTime('now'))->format('Y-m-d H:i:s');

				
		$query = "insert into SystemDBLog (page, query, UserID, IPAddress, ExecutionTime, QueryStatus, DBName, ExecuteDateTime)
				values (:page, :query, :UserID, :IPAddress, :ExecutionTime, :QueryStatus, :DBName, :ExecuteDateTime)";

		$stm = $pdo->prepare($query);
		$whereParam = array(
			':page' => $logPage,
			":query" => $logQuery,
			':UserID' => $logUserID,
			':IPAddress' => $logIPAddress,
			':ExecutionTime' => $logExecutionTime,
			':QueryStatus' => $logQueryStatus,
			':DBName' => $logDB,
			':ExecuteDateTime' => $logExecuteDateTime);
		$keys = array_keys($whereParam);
		for($i=0; $i < count($keys); $i++)
		{
			$st = (is_int($keys[$i])) ? $keys[$i] + 1 : $keys[$i];
			$stm->bindParam($keys[$i], $whereParam[$keys[$i]]);
		}
		
		$stm->execute();
		return true;
	}
	
	private static function GetObjectMembers($obj, $action)
	{
		$obj = (array) $obj;

		$KeyArr = array_keys($obj);
		$valueArr = array();
		for($i=0; $i<count($KeyArr); $i++)
		{
			$origName = $KeyArr[$i];

			if(is_array($obj[$origName]))
				continue;
			if($origName == "exceptions")
				continue;
			if($origName[0] == "_")
				continue;
			if(strlen($origName) > 3 && substr($origName, 0, 3) == "DT_")
				continue;

			$KeyArr[$i] = str_replace(chr(0), "&", $KeyArr[$i]);
			$temp = preg_split('/&/', $KeyArr[$i]);
			$KeyArr[$i] = $temp[count($temp)-1];

			$st = self::DataMemberValidation($action, $obj, $KeyArr[$i], $obj[$origName]);
			if($st === false)
				return false;

			if(isset($st))
				$valueArr[$KeyArr[$i]] = $st;
		}
		return $valueArr;
	}

	private static function DataMemberValidation($action, $obj, $key, $value)
	{
		$checkDT = (isset($obj['DT_' . $key])) ? $obj['DT_' . $key] : null;
		
		if($checkDT === null)
			return $value;
		//...................................
		if($action == "insert" && DataMember::GetNotNullValue($checkDT) && ($value == PDONULL || $value == ""))
		{
			ExceptionHandler::PushException("Field named " . $key . " can not be null.");
			return false;
		}
		//...................................
		$defaultValue = DataMember::GetDefaultValue($checkDT);
		if(!isset($value))
		{
			if($defaultValue != null)
				$value = $defaultValue;
			else
				return $value;
		}
		//...................................
		if(!DataMember::IsValid($checkDT, $value))
			return false;
		//...................................
		switch ($checkDT["DataType"])
		{
			case InputValidation::Pattern_Date :
			case InputValidation::Pattern_GDate :
			case InputValidation::Pattern_DateTime :
				if($value != PDONOW)
					$value = PDONOW;
				break;
			case InputValidation::Pattern_Time :
				if(strlen($value) > 8)
					$value = substr($value, strlen($value)-8);
		}

		return $value;
	}
        
	public static function EnterReplacement($string)
	{
          $trans = array("\n"=>".","\r"=>".","\n\r"=>".","\r\n"=>".");
          $string = strtr($string,$trans);
          return $string;

        }

}
?>
