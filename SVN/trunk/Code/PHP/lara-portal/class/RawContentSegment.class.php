<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class RawContentSegment
{

    public $RawContentSegmentID;
    public $ContentID;
    public $PageNo;
    public $SegmentNo;
    public $RawSegment;
    public $ProcessedSegment;

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("RawContentSegments", $where, $whereParams);
    }

    static function insertRawContentSegment($insertFile)
    {
        $insertQuery = "load data local infile '$insertFile' into table RawContentSegments
                           fields optionally enclosed by '\"'
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentID, PageNo, SegmentNo, RawSegment, ProcessedSegment)";

        PdoDataAccess::runquery($insertQuery);
    }
}
