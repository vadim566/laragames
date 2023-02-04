<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class Content
{
    public $ContentID;
    public $ContentName;
    public $DirName;
    public $CreatorID;
    public $L1ID;
    public $L2ID;
    public $TreeTaggerStatus;
    public $LdtDeactivateStatus;
    public $LangRepType;
    public $WordAudio;
    public $SegmentAudio;
    public $HasAudioTracking;
    public $AudioMouseOver;
    public $WordTranslationMouseOver;
    public $SegmentTranslationMouseOver;
    public $SegmentTranslationCharacter;
    public $AudioSegments;
    public $WordsNote;
    public $L1rtl;
    public $PlayParts;
    public $SegmentAudioKeepDuplicates;
    public $TableOfContents;
    public $KeepComments;
    public $CommentsByDefault;
    public $LinguisticsArticleComments;
    public $ColouredWords;
    public $AudioWordsInColour;
    public $MweWordsInColour;
    public $VideoAnnotations;
    public $VideoAnnotationsFromTranslation;
    public $MaxExamplesPerWordPage;
    public $ExtraPageInfo;
    public $Font;
    public $FrequencyListsInMainText;
    public $IgnoreLargeFileTransfer;
    public $AddPostagsToLemma;
    public $WordTranslationsOn;
    public $WordTranslationFC;
    public $AudioTranslationFC;
	public $SignedVideoFC;
	public $GapFC;
	public $ShowTextContext;
	public $ShowMultimediaContext;
    public $RawTextFileName;
    public $AutomatedTaggedTextFileName;
    public $TaggedTextFileName;
    public $ContentStatus;
    public $WordLdtTaskID;
    public $SegmentLdtTaskID;
    public $HasExternalResources;
    public $HasContentCss;
    public $ContentCssFileName;
    public $HasContentJs;
    public $ContentJsFileName;
    public $HasPinyin;
    public $PinyinFileName;
    public $HasEmbeddedImage;
    public $HasEmbeddedAudio;
    public $HasEmbeddedCSS;
    public $HasEmbeddedScript;
    public $WebAddress;
    public $IsDeleted;
    public $DistributedResourceID;
    public $HasLimitedConfig;
    public $HasMainConfig;
    public $TranslatedWordsInColour;
    public $SegmentTranslationAsPopup;
    //needed for crowdsourcing
    public $CrowdworkerID;
    public $ParentID;
    public $CrowdsourcingStatus;

    //the two following are used in social network.
    public $CoverPictureExtension;
    public $ProfilePictureExtension;


    function insert()
    {
        PdoDataAccess::insert("Contents", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("Contents", "ContentID", $where, $whereParams);
    }

    static function SearchContent($where = "", $whereParam = array())
    {
        $query = "select * from Contents ";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function FullSelect($where = "", $whereParam = array())
    {
        $query = "select 
                    c.ContentID,                                                       
                    c.ContentName,
                    c.DirName,
                    c.WebAddress,
                    c.TreeTaggerStatus,                    
                    c.ContentStatus,
                    c.HasMainConfig,                    
                    c.WordTranslationFC,
                    c.AudioTranslationFC,
                    c.SignedVideoFC,
                    c.GapFC,
                    c.ShowTextContext,
                    c.ShowMultimediaContext,
                    c.CrowdsourcingStatus,
                    c.CrowdWorkerID, 
                    a.UserID,
                    a.UserName,  
                    l1.LanguageName L1Name,
                    l2.LanguageName L2Name,
                    cw.UserID cwUserID,
                    cw.UserName cwUserName,
                    p.ContentID pContentID,
                    p.ContentName pContentName
                from Contents c
                left join Contents p on (p.ContentID = c.ParentID)
                left join Accounts a on (a.UserID = c.CreatorID)
				left join Accounts cw on (cw.UserID = c.CrowdWorkerID)
                left join Languages l1 on (c.L1ID = l1.LanguageID)
                left join Languages l2 on (c.L2ID = l2.LanguageID)";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    function update()
    {
        $whereParams[":contentID"] = $this->ContentID;
        return PdoDataAccess::update("Contents", $this, "ContentID=:contentID", $whereParams);
    }

    static function PartialUpdate($setPart, $wherePart, $params)
    {
        $query = "update Contents set " . $setPart . " where " . $wherePart;
        PdoDataAccess::runquery($query, $params);
    }

    static function getElemCount($where = "", $whereParam = array())
    {
        $query = "select c.ContentID, 
                         typeCT.typeCount,
                         tokenCT.tokenCount,
                         lemmaCT.lemmaCount,
                         segmentCT.segmentCount,
                         mweCT.mweCount
                from Contents c 
                left join 
                  (select ContentID, count(*)  typeCount from ContentTypes group by ContentID) typeCT  
                    on (c.ContentID = typeCT. ContentID)
                left join 
                  (select ContentID, count(*)  tokenCount from ContentTokens group by ContentID) tokenCT 
                    on (c.ContentID = tokenCT. ContentID)
                left join 
                  (select ContentID, count(*)  lemmaCount from ContentLemmas group by ContentID) lemmaCT 
                    on (c.ContentID = lemmaCT. ContentID)
                left join 
                  (select ContentID, count(*)  segmentCount from ContentSegments group by ContentID) segmentCT
                    on (c.ContentID = segmentCT. ContentID)
                left join 
                  (select ContentID, count(*)  mweCount from ContentMultiWords group by ContentID) mweCT
                    on (c.ContentID = mweCT. ContentID)";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        return $temp;
    }

    static function ContentDropBox($dropBoxName, $creatorID, $selectedID = -1)
    {
        $retStr = "<select name=$dropBoxName id=$dropBoxName>";
        $retStr .= "<option value=-1 ";
        if($selectedID == -1)
            $retStr .= " selected ";
        $retStr .= ">all</option>";

        $query = "select ContentID, ContentName from Contents where IsDeleted = 'NO' and CreatorID = :cID 
                  order by ContentID desc";
        $whereParam = array(":cID" => $creatorID);
        $temp = PdoDataAccess::runquery($query, $whereParam);
        for($i=0; $i<count($temp); $i++)
        {
            $retStr .= "<option value='" . $temp[$i]["ContentID"] . "'" ;
            if($temp[$i]["ContentID"] == $selectedID)
                $retStr .= " selected ";
            $retStr .= " >";
            $retStr .= $temp[$i]["ContentName"];
            $retStr .= "</option>";
        }

        $retStr .= "</select>";
        return $retStr;
    }
}
?>
