<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: 10/7/2019
 * Time: 12:42 PM
 */

require_once '../SharedModules/PdoDataAccess.class.php';


class FlashcardResponse
{
    public $FlashcardResponseID;
    public $ExaminerID;
    public $FlashcardsSetID;
    public $FlashcardNo;
    public $FlashcardSetMemberID;

    function insert()
    {
        PdoDataAccess::insert("FlashcardResponses", $this);
    }

    static function getResponseSummary($setID = "")
    {
        $query = "select r.*, q.FlashcardContent question, a.FlashcardContent answer,
                          if(a.FlashcardPart = 'answer', 'correct', 'incorrect') as answerStatus
                  from FlashcardResponses r
                  left join FlashcardSetMembers q on (q.FlashcardsSetID = r.FlashcardsSetID and q.FlashcardNo = r.FlashcardNo and q. FlashcardPart = 'question')
                  left join FlashcardSetMembers a on (a.FlashcardSetMemberID = r.FlashcardSetMemberID)
                  where r.FlashcardsSetID = :setID order by  r.FlashcardNo, FlashcardResponseID";
        $whereParam = array(":setID" => $setID);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp;
    }

    static function getFlashcardScore($setID = "", $flashcardNo = "")
    {
        $query = "select r.*, a.FlashcardPart from FlashcardResponses r 
                    left join FlashcardSetMembers a on (a.FlashcardSetMemberID = r.FlashcardSetMemberID)
                    where r.FlashcardsSetID = :setID and r.FlashcardNo = :flashcarNo order by FlashcardResponseID limit 2;";
        $whereParam = array(":setID" => $setID, ":flashcarNo" => $flashcardNo);
        $temp = PdoDataAccess::runquery($query, $whereParam);

        if($temp[0]["FlashcardPart"] == "answer")
            return 3;
        else if($temp[1]["FlashcardPart"] == "answer")
            return 1;
        else
            return 0;
    }

    static function AnsweredFlashcardsInSet($setID = "")
    {
        $query = "select distinct FlashcardNo from FlashcardResponses where FlashcardsSetID = :setID";
        $whereParam = array(":setID" => $setID);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        return $temp;
    }
}
?>