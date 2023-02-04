<?php

require_once  ROOT . '/shared-modules/InputValidation.class.php';

class DataMember extends InputValidation{

	const DT_DATE = parent::Pattern_Date;

	public static function CreateDMA($DataType, $defaultValue = null, $NotNull = false)
	{
		return array("DataType" => $DataType,
					 "NotNull" => $NotNull,
					 "defaultValue" => $defaultValue);
	}

	/**
	 * @param  DMA $DMA produced by DataMember::CreateDMA()
	 * @param  $val value 
	 * @return boolean (true/false)
	 */
	static function IsValid($DMA , $val)
	{
		if(!is_array($DMA))
			return false;
		
		if((!isset($val) || $val == "") && $DMA["NotNull"])
			return false;

		$ErrorMessage = "";
		$result = InputValidation::validate($val, $DMA["DataType"], false, $ErrorMessage);
		if(!$result)
			ExceptionHandler::PushException ($ErrorMessage);
		return $result;	}

	static function GetDefaultValue($DMA)
	{
		if(is_array($DMA))
			return $DMA["defaultValue"];
	}

	static function GetNotNullValue($DMA)
	{
		return $DMA["NotNull"] == "1" || $DMA["NotNull"] == true ? true : false;
	}

}
?>
