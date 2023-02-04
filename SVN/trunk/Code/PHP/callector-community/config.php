<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 08/27/2020
 * Time: 04:28 PM
 */
session_start();

define("SessionIndex", array (
    'UserID' => 'SN_StageUserID',
    'UserName' => 'SN_StageUserName',
    'UserEmail' => 'SN_StageEmail',
    'UserInfo' => 'SN_StageUserInfo'
));

define("LaraDB", array("driver" => 'mysql',
    "host" => '127.0.0.1',
    "user" => 'laraportaluser',
    "pass" => 'blahblah',
    "database" => 'callector-community'));


define("ROOT", "/export/data/www/issco-site/en/research/projects/callector-community");
define("WebAddress", "https://www.issco.unige.ch/en/research/projects/callector-community/");
define("Repository","/export/data/www/callector-community-data/");
