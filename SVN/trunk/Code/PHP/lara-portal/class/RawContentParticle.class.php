<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: april 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class RawContentParticle
{

    public $RawContentParticleID;
    public $ContentID;
    public $PageNo;
    public $SegmentNo;
    public $ParticleNo;
    public $Particle;
    public $ParticleRoot;

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("RawContentParticles", $where, $whereParams);
    }

    static function insertRawContentParticle($insertFile)
    {
        $insertQuery = "load data local infile '$insertFile' into table RawContentParticles
                           fields optionally enclosed by '\"'
                            terminated by '\t'
                            lines terminated by '\n'
                            ignore 1 lines
                            (ContentID, PageNo, SegmentNo, ParticleNo, Particle, ParticleRoot)";

        PdoDataAccess::runquery($insertQuery);
    }
}
