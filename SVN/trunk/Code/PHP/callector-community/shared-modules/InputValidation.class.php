<?php

class InputValidation {
    /* we used const in methodes also in all over System,Programmers must use this Patterns */
    
	const TEST_PARAM = 1000;
    const Pattern_Num =				'/^-?(?:\d+|\d*\.\d+)$/u';
    const Pattern_NumComma =		'/^([0-9]|[\. \-\,])*$/i';
    const Pattern_EnAlphaNum =		'/^([A-Za-z0-9]|[\._ \-])*$/i';
	const Pattern_FaAlphaNum =		'/^([0-9]|[\p{Arabic}]|[\._ \-])*$/u';
    const Pattern_FaEnAlphaNum =	'/^([a-zA-Z0-9]|[\p{Arabic}]|[\x{200C}ّ– ً]|["\'\/]|[\\\]|[\s،,\._ \-%\(\)\*\+=÷:;؛-])*$/u';
    const Pattern_FaEnAlphaNumSafe =        '/^([a-zA-Z0-9]|[\p{Arabic}]|[\x{200C}ّ– ُ ِ َ ً]|[\/]|[\\\]|[\n\s،,\._ \-%\*\+=÷:@؛-])*$/u';
    const Pattern_FaEnAlphaNumSafe_extjs = '/^([a-zA-Z0-9]|[\p{Arabic}]|[\/]|[\\\]|["]|[\s،,\._ \-%\*\+=÷:;؛-]|[\{\}\[\]])*$/u'; 
    const Pattern_FaEnAlphaNumSafe_extjs_WithAmpersand = '/^([&]|[\x{200C}]|[a-zA-Z0-9]|[\p{Arabic}]|[\/]|[\\\]|["]|[\s،,\._ \-%\*\+=÷:;؛-]|[\{\}\[\]])*$/u'; 
    const Pattern_FaEnAlphaNumSafe_extjs_unsafe = '/^([&]|[\)\(]|[a-zA-Z0-9]|[\p{Arabic}]|[\/]|[\\\]|["]|[\s،,\._ \-%\*\+=÷:;؛-]|[\{\}\[\]])*$/u'; 
    const Pattern_FaEnAlphaNumSafe_withHTMLSpace =        '/^([\[\]\"]|[&nbsp;]|[a-zA-Z0-9]|[\p{Arabic}]|[\/]|[\\\]|[\n\s ^ ,\._ \-%\*\+=  :@ ^ -])*$/u';
    const Pattern_FaEnAlphaNumSafe_withAmpersand =        '/^([&]|[a-zA-Z0-9]|[\p{Arabic}]|[\/]|[\\\]|[\n\s ^ ,\._ \-%\*\+=  :@ ^ -])*$/u';    
    const Pattern_SQL_blackList = '/^(((S|s)(E|e)(L|l)(E|e)(C|c)(T|t).*(F|f)(R|r)(O|o)(M|m))|(U|u)(P|p)(D|d)(A|a)(T|t)(E|e).*(S|s)(E|e)(T|t))$/u';
    const Pattern_FaEnAlphaNumS =        '/^([a-zA-Z0-9]|[\p{Arabic}]|[\/]|[\\\]|[\n\s ^ ,\._ \-%\*\+=  :@ ^ -\[\]])*$/u';
	const Pattern_FaEnAlphaNumSafe2 = '/^([a-zA-Z0-9]|[\p{Arabic}]|[\\\]|[\s،,\._ \-%\*\+=÷:;؛-\[\]\{\}])*$/u';
    const Pattern_Json = '/
          (?(DEFINE)
             (?<number>   -? (?= [1-9]|0(?!\d) ) \d+ (\.\d+)? ([eE] [+-]? \d+)? )
             (?<boolean>   true | false | null )
             (?<string>    " ([^"\n\r\t\\\\]* | \\\\ ["\\\\bfnrt\/] | \\\\ u [0-9a-f]{4} )* " )
             (?<array>     \[  (?:  (?&json)  (?: , (?&json)  )*  )?  \s* \] )
             (?<pair>      \s* (?&string) \s* : (?&json)  )
             (?<object>    \{  (?:  (?&pair)  (?: , (?&pair)  )*  )?  \s* \} )
             (?<json>   \s* (?: (?&number) | (?&boolean) | (?&string) | (?&array) | (?&object) ) \s* )
          )
          \A (?&json) \Z
          /six';
    const Pattern_Html =			'';
    const Pattern_Time =			'/^([0-9]|[:])*$/';
    const Pattern_Date =			'/^[0-9]{4}[-\/][0-9]{1,2}[-\/][0-9]{1,2}$/';
	const Pattern_DateTime =			'/^[0-9]{4}[-\/][0-9]{1,2}[-\/][0-9]{1,2}[ ][0-9]{2}[:][0-9]{2}[:][0-9]{2}$/';
    const Pattern_GDate =			'/^([12][09][0-9]{2}[-\/][0-9]{1,2}[-\/][0-9]{1,2})|([0]{4}[-\/][0]{2}[-\/][0]{2})$/';
    const Pattern_FileName =		'/^([a-zA-Z0-9]|[\p{Arabic}]|[_ -])*\.([a-zA-Z0-9]{1,5})*$/u';
    //const Pattern_url =			'(https?:\/\/(?:www\.|(?!www))[^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})';
	const Pattern_IP =			'ip'; //Use the filter function is better
	const Pattern_Email =		'email'; //Use the filter function is better
	const Pattern_Url =			'url'; //Use the filter function is better
	const Pattern_Boolean =		'boolean'; //Use the filter function is better
	/**
	 * این تابع ورودی را با الگو مورد نظر اعتبار سنجی می کند
	 * @param string $value مقدار ورودی
	 * @param string $pattern الگوی مورد نظر
	 * @param boolean $DieOnError در صورت خطا اجرا خاتمه یابد
	 * @param string $ErrorMessage خطای رخ داده
	 * @return boolean
	 */
    public static function validate(&$value, $pattern, $DieOnError = true, &$ErrorMessage = "") {
		
		//------ for server overload testing -------
		//return true;
		//------------------------------------------

		if(empty($value))
			return true;
		
		if($value == "%pdonull%")
			return true;
		
		if($value == "%pdonull%")
			return true;
		
		if(($pattern == self::Pattern_Date ||
			$pattern == self::Pattern_GDate || $pattern == self::Pattern_DateTime) && $value == "now()")
			return true;
		
		switch($pattern)
		{
			case self::Pattern_IP :			$result = self::validateIp($value);				break;
			case self::Pattern_Email :		$result = self::validateEmail($value);			break;
			case self::Pattern_Url :		$result = self::validateUrl($value);			break;
			case self::Pattern_Boolean :	$result = self::validateBoolean($value);		break;
			case self::Pattern_Html	:		
				$value = self::htmlEncode($value); 
				$result= true;	
				break;
			default:						$result = preg_match($pattern, $value);				
		}        
		
		if(!$result)
		{
			$ErrorMessageText = "Input " . "'" . htmlspecialchars($value) . "' is not compatible with " . self::GetPatternName($pattern) . " pattern.";
			if($DieOnError)
			{
				if($pattern==self::Pattern_FaEnAlphaNumSafe)
				{
					$ErrorMessage = '<html dir="rtl" xmlns="http://www.w3.org/1999/xhtml" >
						<head>
						<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
						<title></title>
						</head>
						<body>
						<center>
						<b>' .
							$ErrorMessageText
						. '</b>
						</center>
						</body>
						</html>';
				}
				echo $ErrorMessage;
				die();
			}
			else
			{
				if(class_exists("ExceptionHandler"))
					ExceptionHandler::PushException($ErrorMessage);
				return false;
			}
		}
		return true;
    }

	public static function ArrayValidate(&$ValueList, $pattern, $DieOnError = true, &$ErrorMessage = "") {
		foreach ($ValueList as $key => &$value)
		{
			if(is_array($value)) {
				$res = self::ArrayValidate($value, $pattern, $DieOnError, $ErrorMessage);
				if (!$res) {
					return false;
				}
			}
			else {
				$res = self::validate($value, $pattern, $DieOnError, $ErrorMessage);
				if (!$res) {
					return false;
				}
			}
		}
		return true;
	}

    /* Validates that the specified value does not have null or empty value. */
    public static function validateRequired($value) {
        if (is_null($value)) {
            return false;
        } elseif (is_string($value) && trim($value) === '') {
            return false;
        }
        return true;
    }

    public static function validateNumeric($value) {
        return is_numeric($value);
    }

    public static function validateLengthBetween($value, $max, $min) {

        $length = self::stringLength($value);
        // Length between
        return $length >= $min && $length <= $max;
    }

    public static function validateLengthEqual($value, $len) {
        $length = self::stringLength($value);
        // Length between
        return $length == $len;
    }

    public static function stringLength($value) {

        if (!is_string($value)) {
           return false;
        } elseif (function_exists('mb_strlen')) {
            return mb_strlen($value);
        }
        return strlen($value);
    }

	static public function validateAccepted($acceptable, $value) {
        return in_array($value, $acceptable, true);
    }

    public static function ArrayEncoding(&$InputArr){
		
		foreach ($InputArr as $key => &$value) 
		{
			if(is_array($value))
				self::ArrayEncoding($value);
			else
				$InputArr[$key] = htmlspecialchars($value);
		}
	}

	function ObjectEncoding(&$InputObj){
		$varList = get_object_vars($InputObj);
		foreach ($varList as $key=>$val)
			$InputObj->{$key} = htmlspecialchars($val);
	}

	/* encode HTML special chars */
    /* Use this function,When the user is not allowed to enter the HTML Tags  */

    public static function htmlEncode($str) {

        return htmlspecialchars($str);
    }

   //****************************************************************
	private static function GetPatternName($pattern){
		
		$tmp = new ReflectionClass(get_called_class());
		$a = $tmp->getConstants();
        $b = array_flip($a);

		$titles = array(
			"Pattern_Num" => "Numbers",
			"Pattern_NumComma" => "Separated Numbers",
			"Pattern_EnAlphaNum" => "English Alphabet",
			"Pattern_FaAlphaNum" => "Arabic Alphabet",
			"Pattern_FaEnAlphaNum" => "Letters and digits",
			"Pattern_Time" => "time",
			"Pattern_Date" => "date",
			"Pattern_DateTime" => "date time",
			"Pattern_GDate" => "Christian Date",
			"Pattern_FileName" => "File Name",
			"Pattern_IP" => "IP address",
			"Pattern_Email" => "Email Address",
			"Pattern_Url" => "URL Address",
			"Pattern_Json" => "json",
			"Pattern_FaEnAlphaNumSafe" => "Safe Characters",
			"Pattern_FaEnAlphaNumSafe_extjs" => "Input Params",
			"Pattern_FaEnAlphaNumSafe_extjs_WithAmpersand" => "Input Params start with &",
			"Pattern_Boolean" => ""
		);
        return isset($titles[$b[$pattern]]) ? $titles[$b[$pattern]] : '';
       // return $b[$pattern];
	}

    private static function validateIp($value) {
        return filter_var($value, \FILTER_VALIDATE_IP) !== false;
    }
	
    private static function validateEmail( $value) {
        return filter_var($value, \FILTER_VALIDATE_EMAIL) !== false;
    }

    private static function validateUrl( $value) {
            return filter_var($value, \FILTER_VALIDATE_URL) !== false;
    }

    private static function validateBoolean($value) {
        return (is_bool($value)) ? true : false;
    }

	//-----------------------------------------------------

   public static function ValidateGlobalParams($ExtjsMode = false, $temp = false){

		$pattern = !$ExtjsMode ? InputValidation::Pattern_FaEnAlphaNumSafe :
				InputValidation::Pattern_FaEnAlphaNumSafe_extjs;

		foreach ($_POST as $key => $value)
		{
			if(!is_array($_POST[$key]))
			{
				if(!InputValidation::validate($value, $pattern))
				{
					$_SESSION = array();
					die();
				}
				$_POST[$key] = addslashes(trim($value));
			}
			else
			{
				foreach ($_POST[$key] as $key2=>$value2)
				{

					if(!InputValidation::validate($value2, $pattern))
					{
						$_SESSION = array();
						die();
					}
					$_POST[$key][$key2] = addslashes(trim($value2));
				}
			}
		}
		foreach ($_GET as $key => $value)
		{
			if(!is_array($_GET[$key]))
			{

				if(!InputValidation::validate($value, $pattern))
				{
					$_SESSION = array();
					die();
				}
				$_GET[$key] = addslashes(trim($value));
			}
			else
			{
				foreach ($_GET[$key] as $key2=>$value2)
				{

					if(!InputValidation::validate($value2, $pattern))
					{
						$_SESSION = array();
						die();
					}
					$_GET[$key][$key2] = addslashes(trim($value2));
				}
			}
		}
		foreach ($_REQUEST as $key => $value)
		{
			if(!is_array($_REQUEST[$key]))
			{

				if(!InputValidation::validate($value, $pattern))
				{
					$_SESSION = array();
					die();
				}
				$_REQUEST[$key] = addslashes(trim($value));
			}
			else
			{
				foreach ($_REQUEST[$key] as $key2=>$value2)
				{

					if(!InputValidation::validate($value2, $pattern))
					{
						$_SESSION = array();
						die();
					}
					$_REQUEST[$key][$key2] = addslashes(trim($value2));
				}
			}
		}
    }
}

?>
