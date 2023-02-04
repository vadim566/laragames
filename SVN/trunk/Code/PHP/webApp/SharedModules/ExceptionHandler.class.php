<?php

class ExceptionHandler
{
	private $exceptions;
	private static $globalExceptions = array();

	const ExceptionType_message = "message";
	const ExceptionType_warning = "warrning";
	const ExceptionType_error = "Error";

	public function  __construct() {
		$this->exceptions = array();
	}

	/**
	 * pushes $Description to the exception stack
	 *
	 * @param object/string/array $ErrorStr
	 * @param ExceptionHandler::ExceptionType_warning/ExceptionHandler::ExceptionType_error $errorType
	 * @return
	 */
	public function PushException($Description, $exceptionType = ExceptionHandler::ExceptionType_error)
	{
		if(isset($this) && isset($this->exceptions))
			$exceptionArray = & $this->exceptions;
		else 
			$exceptionArray = & self::$globalExceptions;
		//..............................................
		$exceptionArray[] = array("Desc" => $Description, "Type" => $exceptionType);
//		if(is_array($Description))
//			print_r($Description);
//		else
//			echo $Description;
//		print_r(debug_backtrace());
	}

	/**
	 * This method pops last exception record off the exceptions stack.
	 *
	 * @return pushed type
	 */
	public function PopException()
	{
		if(isset($this) && isset($this->exceptions))
			$exceptionArray = & $this->exceptions;
		else
			$exceptionArray = & self::$globalExceptions;
		//..............................................
		return array_pop($exceptionArray);
	}

	/**
	 * This method pops last exception description off the exceptions stack.
	 *
	 * @return pushed type
	 */
	public function popExceptionDescription()
	{
		 if(isset($this) && isset($this->exceptions))
			$exceptionArray = & $this->exceptions;
		else
			$exceptionArray = & self::$globalExceptions;
		//..............................................
		if(count($exceptionArray) == 0)
			return null;
		$record = array_pop($exceptionArray);
		return is_array($record["Desc"]) ? implode("\n", $record["Desc"]) : $record["Desc"];
	}

	/**
	* This method pops all exceptions off the exceptions stack.
	*
	* @return array list of exceptions
	*/
	public function PopAllExceptions()
	{
		if(isset($this) && isset($this->exceptions))
			$exceptionArray = & $this->exceptions;
		else
			$exceptionArray = & self::$globalExceptions;
		//..............................................
		$ErrList = $exceptionArray;
		$exceptionArray = array();

		return $ErrList;
	}

	/**
	* Returns count of exceptions that pushed by "PushException()" method
	*
	* @return int  number of exceptions
	*/
	public function GetExceptionCount()
	{
		if(isset($this) && isset($this->exceptions))
			$exceptionArray = & $this->exceptions;
		else
			$exceptionArray = & self::$globalExceptions;
		//..............................................
		return count($exceptionArray);
	}

	/**
	 * return all exception descs that imploded by the separator
	* @param  string  seprator
	* @return string  concated string of exceptions
	*/
	public function GetExceptionsToString($seprator = '\n', $include_errors = true, $include_warnings = true, $include_messages = true)
	{
		if(isset($this) && isset($this->exceptions))
			$exceptionArray = & $this->exceptions;
		else
			$exceptionArray = & self::$globalExceptions;
		//..............................................
		$result = "";
		for($i=0; $i < count($exceptionArray); $i++)
		{
			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_error && !$include_errors) continue;
			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_warning && !$include_warnings) continue;
			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_message && !$include_messages) continue;

			$result .= $exceptionArray[$i]["Desc"];
			$result .= $i < count($exceptionArray)-1 ? $seprator : "";
		}
		return $result;
	}

	/**
	 * show an Ext Panel at first of the div or table 
	 * @param <type> $elementID
	 * @return <type>
	 */
	public function showExceptionPanel($elementID,$include_errors = true, $include_warnings = true, $include_messages = true)
	{
		if(isset($this) && isset($this->exceptions))
			$exceptionArray = & $this->exceptions;
		else
			$exceptionArray = & self::$globalExceptions;
		//..............................................

		if(count($exceptionArray) == 0)
			return "";

		$errorStr = "";
		$warningStr = "";
		$messageStr = "";


		for($i=0; $i < count($exceptionArray); $i++)
		{
			$desc = $exceptionArray[$i]["Desc"];
			if(is_array($desc))
				$desc = implode("\n", $desc);
			$desc = addslashes($desc);

			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_error && !$include_errors) continue;
			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_warning && !$include_warnings) continue;
			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_message && !$include_messages) continue;

			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_error)
				$errorStr =  $desc . "<br>";
			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_warning)
				$warningStr = $desc . "<br>";
			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_message)
				$messageStr = $desc . "<br>";
		}
		
		if($errorStr != "")
			echo "<script> Ext.onReady(function(){ Ext.message.error('$elementID','خطا','" . $errorStr . "','98%')});</script>";
		if($warningStr != "")
			echo "<script> Ext.onReady(function(){ Ext.message.warning('$elementID','هشدار','" . $warningStr . "','98%')});</script>";
		if($messageStr != "")
			echo "<script> Ext.onReady(function(){ Ext.message.message('$elementID','پیغام','" . $messageStr . "','98%')});</script>";

		$exceptionArray = array();
	}

	function ConvertExceptionsToJsObject($include_errors = true, $include_warnings = true, $include_messages = true)
	{
		if(isset($this) && isset($this->exceptions))
			$exceptionArray = & $this->exceptions;
		else
			$exceptionArray = & self::$globalExceptions;
		//..............................................

		if(count($exceptionArray) == 0)
			return "";

		$errorStr = "";
		$warningStr = "";
		$messageStr = "";


		for($i=0; $i < count($exceptionArray); $i++)
		{
			$desc = $exceptionArray[$i]["Desc"];
			if(is_array($desc))
				$desc = implode("\n", $desc);
			$desc = addslashes($desc);

			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_error && !$include_errors) continue;
			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_warning && !$include_warnings) continue;
			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_message && !$include_messages) continue;

			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_error)
				$errorStr .=  $desc . "<br>";
			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_warning)
				$warningStr .= $desc . "<br>";
			if($exceptionArray[$i]["Type"] == ExceptionHandler::ExceptionType_message)
				$messageStr .= $desc . "<br>";
		}

		return "{errors : '" . $errorStr . "',warnings : '" . $warningStr . "',messages : '" . $messageStr . "'}";
	}

	
	function SaveExceptionsToSession($sessionName)
	{
		if(isset($this) && isset($this->exceptions))
			$exceptionArray = & $this->exceptions;
		else
			$exceptionArray = & self::$globalExceptions;

		$_SESSION["Exception_" . $sessionName] = $exceptionArray;
		
	}

	function RestoreExceptionsFromSession($sessionName)
	{
		if(isset($this) && isset($this->exceptions))
			$exceptionArray = & $this->exceptions;
		else
			$exceptionArray = & self::$globalExceptions;

		$exceptionArray = isset($_SESSION["Exception_" . $sessionName]) ? $_SESSION["Exception_" . $sessionName] : array();
		unset($_SESSION["Exception_" . $sessionName]);
	}
}
?>