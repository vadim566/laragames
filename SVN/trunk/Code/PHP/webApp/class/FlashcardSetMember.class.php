<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: juin 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class FlashcardSetMember
{
    public $FlashcardSetMemberID;
    public $FlashcardsSetID;
    public $FlashcardNo;
    public $FlashcardPart;//ENUM('answer', 'distractors', 'question')
    public $FlashcardContent;
    public $FlashcardType;

    static function insertFlashcardSetMembers($contentInsertFileName)
    {
        $insertQuery = "load data local infile '$contentInsertFileName' into table FlashcardSetMembers
                            fields optionally enclosed by '\"' 
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (FlashcardsSetID,FlashcardNo,FlashcardPart,FlashcardContent,FlashcardType)";

        PdoDataAccess::runquery($insertQuery);
    }

    static function selectFlashcard($where, $whereParam)
    {
        $query = "select * from FlashcardSetMembers ";
        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function getNumberOfQuestions($where, $whereParam)
    {
        $query = "select count(distinct FlashcardNo) as numberOfTests 
                  from .FlashcardSetMembers ";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp[0]["numberOfTests"];
    }
}
