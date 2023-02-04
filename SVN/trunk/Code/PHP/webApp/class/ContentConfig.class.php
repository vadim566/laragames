<?php
/**
 * Created by PhpStorm.
 * User: habibih
 * Date: july 2019
 */


require_once '../SharedModules/PdoDataAccess.class.php';

class ContentConfig
{
    public $ContentConfigID;
    public $ContentID;
    public $id;
    public $language;
    public $text_direction;
    public $max_examples_per_word_page;
    public $corpus;
    public $segment_audio_directory;
    public $audio_tracking_file;
    public $word_audio_directory;
    public $translation_spreadsheet;
    public $translation_spreadsheet_surface;
    public $translation_spreadsheet_tokens;
    public $notes_spreadsheet;
    public $note_words_in_colour;
    public $segment_translation_spreadsheet;
    public $translation_mouseover;
    public $audio_mouseover;
    public $segment_translation_mouseover;
    public $segment_translation_character;
    public $audio_segments;
    public $play_parts;
    public $segment_audio_keep_duplicates;
    public $allow_table_of_contents;
    public $keep_comments;
    public $comments_by_default;
    public $linguistics_article_comments;
    public $coloured_words;
    public $audio_words_in_colour;
    public $extra_page_info;
    public $font;
    public $frequency_lists_in_main_text_page;
    public $add_postags_to_lemma;
    public $untagged_corpus;
    public $tagged_corpus;
    public $compiled_directory;
    public $lara_tmp_directory;
    public $working_tmp_directory;
    public $image_directory;
    public $word_audio_directory_external;
    public $segment_audio_directory_external;
    public $translation_spreadsheet_external;
    public $segment_translation_spreadsheet_external;
    public $css_file;
    public $script_file;
    public $pinyin_file;
    public $word_translations_on;
    public $mwe_annotations_file;
    public $mwe_file;
    public $mwe_words_in_colour;
    public $video_annotations;
    public $video_annotations_from_translation;
    public $segment_translation_as_popup;
    public $translated_words_in_colour;


    function insert()
    {
        PdoDataAccess::insert("ContentConfig", $this);
    }

    static function lastID($where = "", $whereParams = array())
    {
        return PdoDataAccess::GetLastID("ContentConfig", "ContentConfigID", $where, $whereParams);
    }

    static function SearchContentConfig($where = "", $whereParam = array())
    {
        $query = "select * from ContentConfig ";

        $query .= (!empty($where)) ? " where " . $where : "";

        if(!empty($whereParam))
            $temp = PdoDataAccess::runquery($query, $whereParam);
        else
            $temp = PdoDataAccess::runquery($query);

        if(count($temp) == 0)
            return false;
        return $temp[0];
    }

    static function delete($where, $whereParams)
    {
        return PdoDataAccess::delete("ContentConfig", $where, $whereParams);
    }
}
?>
