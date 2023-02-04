-- phpMyAdmin SQL Dump
-- version 4.9.0.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 15, 2020 at 04:31 PM
-- Server version: 5.7.28-0ubuntu0.16.04.2-log
-- PHP Version: 7.0.33-0ubuntu0.16.04.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Database: `LARA-portal`
--
CREATE DATABASE IF NOT EXISTS `LARA-portal` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `LARA-portal`;

-- --------------------------------------------------------

--
-- Table structure for table `ContentConfig`
--

DROP TABLE IF EXISTS `ContentConfig`;
CREATE TABLE `ContentConfig` (
  `ContentConfigID` int(11) NOT NULL,
  `id` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `language` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `text_direction` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `max_examples_per_word_page` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `corpus` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `segment_audio_directory` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `word_audio_directory` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `translation_spreadsheet` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `segment_translation_spreadsheet` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `translation_mouseover` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `audio_mouseover` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `segment_translation_mouseover` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `untagged_corpus` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `tagged_corpus` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `compiled_directory` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `lara_tmp_directory` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `working_tmp_directory` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `image_directory` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `ContentID` int(11) DEFAULT NULL,
  `word_audio_directory_external` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `segment_audio_directory_external` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `translation_spreadsheet_external` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `segment_translation_spreadsheet_external` varchar(500) COLLATE utf8_bin DEFAULT NULL,
  `allow_table_of_contents` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `keep_comments` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `comments_by_default` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `linguistics_article_comments` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `coloured_words` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `audio_words_in_colour` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `extra_page_info` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `font` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `frequency_lists_in_main_text_page` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `add_postags_to_lemma` varchar(20) COLLATE utf8_bin DEFAULT NULL,
  `css_file` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `script_file` varchar(255) COLLATE utf8_bin DEFAULT NULL,
  `word_translations_on` varchar(255) COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Config file created by PHP code';

-- --------------------------------------------------------

--
-- Table structure for table `ContentEmbeddedItems`
--

DROP TABLE IF EXISTS `ContentEmbeddedItems`;
CREATE TABLE `ContentEmbeddedItems` (
  `ItemID` int(11) NOT NULL,
  `ItemType` enum('Image','Audio','CSS','Script') COLLATE utf8_bin DEFAULT NULL,
  `ItemName` varchar(45) COLLATE utf8_bin DEFAULT NULL,
  `IsUploaded` enum('YES','NO') COLLATE utf8_bin DEFAULT NULL,
  `ContentID` int(11) DEFAULT NULL,
  `ItemState` enum('NEW','OLD') COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='List of all embedded Items inside the uploaded text content';

-- --------------------------------------------------------

--
-- Table structure for table `ContentParols`
--

DROP TABLE IF EXISTS `ContentParols`;
CREATE TABLE `ContentParols` (
  `ContentParolID` int(11) NOT NULL,
  `ContentID` int(11) DEFAULT NULL,
  `ParolPairID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Contains the words of each content - Filles from excel file named word_translation and updates by user';

-- --------------------------------------------------------

--
-- Table structure for table `ContentRecordingMetadata`
--

DROP TABLE IF EXISTS `ContentRecordingMetadata`;
CREATE TABLE `ContentRecordingMetadata` (
  `RecordingMetadataID` int(11) NOT NULL,
  `ContentID` int(11) NOT NULL,
  `RecordingType` enum('word','segment') NOT NULL,
  `MetadataFileDirectory` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `ContentRecordingSegments`
--

DROP TABLE IF EXISTS `ContentRecordingSegments`;
CREATE TABLE `ContentRecordingSegments` (
  `ContentSegmentID` int(11) NOT NULL,
  `RecordingMetadataID` int(11) NOT NULL,
  `SegmentText` text COLLATE utf8_bin NOT NULL,
  `AudioFileName` varchar(255) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- Table structure for table `ContentRecordingTasks`
--

DROP TABLE IF EXISTS `ContentRecordingTasks`;
CREATE TABLE `ContentRecordingTasks` (
  `ContentRecordingTaskID` int(11) NOT NULL,
  `ContentID` int(11) DEFAULT NULL,
  `RecordingTaskID` int(11) DEFAULT NULL,
  `RecordingTaskType` enum('word','segment') COLLATE utf8_bin DEFAULT NULL,
  `RecordingTaskStatus` enum('valid','deleted','rejected') COLLATE utf8_bin DEFAULT 'valid'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Lists of assigned recording tasks to content	';

-- --------------------------------------------------------

--
-- Table structure for table `Contents`
--

DROP TABLE IF EXISTS `Contents`;
CREATE TABLE `Contents` (
  `ContentID` int(11) NOT NULL,
  `ContentName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `DirName` varchar(500) COLLATE utf8_unicode_ci DEFAULT 'null',
  `CreatorID` int(11) DEFAULT NULL COMMENT 'foreign key to Users.UserID',
  `L1ID` int(11) DEFAULT NULL COMMENT 'foreign key to Languages.LanguageID',
  `L2ID` int(11) DEFAULT NULL COMMENT 'foreign key to Languages.LanguageID',
  `TreeTaggerStatus` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `LangRepType` enum('Public','Private') COLLATE utf8_unicode_ci DEFAULT 'Public',
  `WordAudio` varchar(50) COLLATE utf8_unicode_ci DEFAULT '-1' COMMENT 'foreign key to ldt users',
  `SegmentAudio` varchar(50) COLLATE utf8_unicode_ci DEFAULT '-1' COMMENT 'foreign key to ldt users',
  `AudioMouseOver` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `WordTranslationMouseOver` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `AudioSegments` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `SegmentTranslationMouseOver` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `L1rtl` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `TableOfContents` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `KeepComments` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `CommentsByDefault` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `LinguisticsArticleComments` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `ColouredWords` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'YES',
  `AudioWordsInColour` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `MaxExamplesPerWordPage` enum('5','10','15') COLLATE utf8_unicode_ci DEFAULT '10',
  `ExtraPageInfo` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `Font` enum('serif','sans-serif','monospace') COLLATE utf8_unicode_ci DEFAULT 'serif',
  `FrequencyListsInMainText` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `AddPostagsToLemma` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `WordTranslationsOn` enum('lemma','surface_word_type','surface_word_token') COLLATE utf8_unicode_ci DEFAULT NULL,
  `RawTextFileName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `AutomatedTaggedTextFileName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `TaggedTextFileName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `ContentStatus` enum('raw','treeTagger','resources','pages') COLLATE utf8_unicode_ci DEFAULT 'raw',
  `WordLdtTaskID` int(11) DEFAULT NULL,
  `SegmentLdtTaskID` int(11) DEFAULT NULL,
  `HasExternalResources` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `HasContentCss` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `ContentCssFileName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `HasContentJs` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `ContentJsFileName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `HasEmbeddedImage` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `HasEmbeddedAudio` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `HasEmbeddedCSS` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `HasEmbeddedScript` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `WebAddress` text COLLATE utf8_unicode_ci,
  `IsDeleted` enum('YES','NO') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'NO',
  `DistributedResourceID` int(11) DEFAULT NULL,
  `HasLimitedConfig` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `HasMainConfig` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Created content by the user';

-- --------------------------------------------------------

--
-- Table structure for table `DistributedResourcePages`
--

DROP TABLE IF EXISTS `DistributedResourcePages`;
CREATE TABLE `DistributedResourcePages` (
  `ResourcePageID` int(11) NOT NULL,
  `ResourceID` int(11) NOT NULL,
  `PageNumber` int(11) DEFAULT NULL,
  `PageName` varchar(500) COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='List of pages for each distributed content resource';

-- --------------------------------------------------------

--
-- Table structure for table `DistributedResources`
--

DROP TABLE IF EXISTS `DistributedResources`;
CREATE TABLE `DistributedResources` (
  `ResourceID` int(11) NOT NULL,
  `ResourceName` varchar(1000) COLLATE utf8_bin NOT NULL,
  `WebAddress` text COLLATE utf8_bin NOT NULL,
  `ResourceType` enum('Language','Content') COLLATE utf8_bin NOT NULL,
  `ParentID` int(11) DEFAULT NULL,
  `UserID` int(11) NOT NULL,
  `L2ID` int(11) DEFAULT NULL,
  `IsDeleted` enum('YES','NO') COLLATE utf8_bin DEFAULT 'NO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Language and Content Resources Registered in LARA portal';

-- --------------------------------------------------------

--
-- Table structure for table `ExternalCommandsLogs`
--

DROP TABLE IF EXISTS `ExternalCommandsLogs`;
CREATE TABLE `ExternalCommandsLogs` (
  `LogID` int(11) NOT NULL,
  `LogType` enum('PythonCmnd','PythonRes','LdtCmnd','LdtRes','ConfigFile') COLLATE utf8_bin NOT NULL,
  `LogData` text COLLATE utf8_bin NOT NULL,
  `LogDateTime` datetime NOT NULL,
  `UserID` int(11) NOT NULL,
  `RelatedID` int(11) NOT NULL,
  `RelatedPage` enum('content','resource','history','import') COLLATE utf8_bin DEFAULT 'content',
  `ParentID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='This table keeps all Python, LDT, etc. commands and results which occures during the proccess.  ';

-- --------------------------------------------------------

--
-- Table structure for table `ImportContents`
--

DROP TABLE IF EXISTS `ImportContents`;
CREATE TABLE `ImportContents` (
  `ImportContentID` int(11) NOT NULL,
  `ImportFileName` varchar(255) NOT NULL,
  `CreatorID` int(11) NOT NULL COMMENT 'foreign key to Users.UserID',
  `ContentID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `LanguagePairs`
--

DROP TABLE IF EXISTS `LanguagePairs`;
CREATE TABLE `LanguagePairs` (
  `LanguagePairID` int(11) NOT NULL,
  `L1ID` int(11) NOT NULL,
  `L2ID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `Languages`
--

DROP TABLE IF EXISTS `Languages`;
CREATE TABLE `Languages` (
  `LanguageID` int(11) NOT NULL,
  `LanguageName` varchar(45) COLLATE utf8_unicode_ci DEFAULT NULL,
  `TreeTagger` enum('YES','NO') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'NO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='List of languages';

-- --------------------------------------------------------

--
-- Table structure for table `ParolPairs`
--

DROP TABLE IF EXISTS `ParolPairs`;
CREATE TABLE `ParolPairs` (
  `ParolPairID` int(11) NOT NULL,
  `LanguagePairID` int(11) DEFAULT NULL,
  `ParolInL1` text COLLATE utf8_bin,
  `ParolInL2` text COLLATE utf8_bin,
  `ParolType` enum('word','segment') COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Contains the main and translation pair of words or segments';

-- --------------------------------------------------------

--
-- Table structure for table `ReadingHistories`
--

DROP TABLE IF EXISTS `ReadingHistories`;
CREATE TABLE `ReadingHistories` (
  `ReadingHistoryID` int(11) NOT NULL,
  `ReadingHistoryName` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `UserID` int(11) DEFAULT NULL COMMENT 'foreign key to Users.UserID',
  `L1ID` int(11) DEFAULT NULL COMMENT 'foreign key to Languages.LanguageID',
  `L2ID` int(11) DEFAULT NULL COMMENT 'foreign key to Languages.LanguageID',
  `AudioMouseOver` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `WordTranslationMouseOver` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `SegmentTranslationMouseOver` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `TableOfContents` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'YES',
  `ColouredWords` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'YES',
  `AudioWordsInColour` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `MaxExamplesPerWordPage` enum('5','10','15') COLLATE utf8_unicode_ci DEFAULT '10',
  `Font` enum('serif','sans-serif','monospace') COLLATE utf8_unicode_ci DEFAULT 'serif',
  `FrequencyListsInMainText` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO',
  `IsDeleted` enum('YES','NO') COLLATE utf8_unicode_ci DEFAULT 'NO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ReadingHistoryResources`
--

DROP TABLE IF EXISTS `ReadingHistoryResources`;
CREATE TABLE `ReadingHistoryResources` (
  `ReadingHistoryResourceID` int(11) NOT NULL,
  `ReadingHistoryID` int(11) NOT NULL,
  `ResourceID` int(11) NOT NULL,
  `LastReadPage` int(11) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='Distributed Resources included in each Reading History';

-- --------------------------------------------------------

--
-- Table structure for table `ResultMsg`
--

DROP TABLE IF EXISTS `ResultMsg`;
CREATE TABLE `ResultMsg` (
  `﻿PageName` text,
  `FunctionName` text,
  `SentMsgToClientSide` text,
  `PythonRelatedCommand` text,
  `ResultMsgID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `ServerToClientReturns`
--

DROP TABLE IF EXISTS `ServerToClientReturns`;
CREATE TABLE `ServerToClientReturns` (
  `ServerToClientReturnID` int(11) NOT NULL,
  `PageName` varchar(255) COLLATE utf8_bin NOT NULL,
  `FunctionName` varchar(255) COLLATE utf8_bin NOT NULL,
  `SentMsgToClientSide` varchar(500) COLLATE utf8_bin NOT NULL,
  `PythonRelatedCommand` varchar(255) COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

-- --------------------------------------------------------

--
-- Table structure for table `SystemDBLog`
--

DROP TABLE IF EXISTS `SystemDBLog`;
CREATE TABLE `SystemDBLog` (
  `id` int(11) NOT NULL,
  `page` text,
  `query` text,
  `UserID` int(11) DEFAULT NULL,
  `IPAddress` varchar(45) DEFAULT NULL,
  `ExecutionTime` smallint(6) DEFAULT NULL,
  `QueryStatus` enum('SUCCESS','FAILED') DEFAULT NULL,
  `DBName` varchar(45) DEFAULT NULL,
  `ExecuteDateTime` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Table structure for table `UserActivitiesLogs`
--

DROP TABLE IF EXISTS `UserActivitiesLogs`;
CREATE TABLE `UserActivitiesLogs` (
  `LogID` int(11) NOT NULL,
  `LogData` varchar(255) COLLATE utf8_bin NOT NULL,
  `LogDateTime` datetime NOT NULL,
  `UserID` int(11) NOT NULL,
  `RelatedID` int(11) NOT NULL,
  `RelatedPage` enum('content','resource','history','import') COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin COMMENT='This table keeps log of actions during creating content';

-- --------------------------------------------------------

--
-- Table structure for table `Users`
--

DROP TABLE IF EXISTS `Users`;
CREATE TABLE `Users` (
  `UserID` int(11) NOT NULL,
  `UserName` varchar(45) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `Email` varchar(100) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `Password` varchar(256) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL,
  `PasswordSalt` varchar(45) CHARACTER SET utf8 COLLATE utf8_bin DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='Table of users login info';

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ContentConfig`
--
ALTER TABLE `ContentConfig`
  ADD PRIMARY KEY (`ContentConfigID`);

--
-- Indexes for table `ContentEmbeddedItems`
--
ALTER TABLE `ContentEmbeddedItems`
  ADD PRIMARY KEY (`ItemID`);

--
-- Indexes for table `ContentParols`
--
ALTER TABLE `ContentParols`
  ADD PRIMARY KEY (`ContentParolID`),
  ADD KEY `keyIndex` (`ContentParolID`),
  ADD KEY `contentIDIndex` (`ContentID`),
  ADD KEY `parolPairIndex` (`ParolPairID`);

--
-- Indexes for table `ContentRecordingMetadata`
--
ALTER TABLE `ContentRecordingMetadata`
  ADD PRIMARY KEY (`RecordingMetadataID`);

--
-- Indexes for table `ContentRecordingSegments`
--
ALTER TABLE `ContentRecordingSegments`
  ADD PRIMARY KEY (`ContentSegmentID`);

--
-- Indexes for table `ContentRecordingTasks`
--
ALTER TABLE `ContentRecordingTasks`
  ADD PRIMARY KEY (`ContentRecordingTaskID`);

--
-- Indexes for table `Contents`
--
ALTER TABLE `Contents`
  ADD PRIMARY KEY (`ContentID`);

--
-- Indexes for table `DistributedResourcePages`
--
ALTER TABLE `DistributedResourcePages`
  ADD PRIMARY KEY (`ResourcePageID`);

--
-- Indexes for table `DistributedResources`
--
ALTER TABLE `DistributedResources`
  ADD PRIMARY KEY (`ResourceID`);

--
-- Indexes for table `ExternalCommandsLogs`
--
ALTER TABLE `ExternalCommandsLogs`
  ADD PRIMARY KEY (`LogID`);

--
-- Indexes for table `ImportContents`
--
ALTER TABLE `ImportContents`
  ADD PRIMARY KEY (`ImportContentID`);

--
-- Indexes for table `LanguagePairs`
--
ALTER TABLE `LanguagePairs`
  ADD PRIMARY KEY (`LanguagePairID`),
  ADD KEY `KeyIndex` (`LanguagePairID`),
  ADD KEY `L1Index` (`L1ID`),
  ADD KEY `L2Index` (`L2ID`);

--
-- Indexes for table `Languages`
--
ALTER TABLE `Languages`
  ADD PRIMARY KEY (`LanguageID`);

--
-- Indexes for table `ParolPairs`
--
ALTER TABLE `ParolPairs`
  ADD PRIMARY KEY (`ParolPairID`),
  ADD KEY `keyIndex` (`ParolPairID`),
  ADD KEY `langPairIndex` (`LanguagePairID`);

--
-- Indexes for table `ReadingHistories`
--
ALTER TABLE `ReadingHistories`
  ADD PRIMARY KEY (`ReadingHistoryID`);

--
-- Indexes for table `ReadingHistoryResources`
--
ALTER TABLE `ReadingHistoryResources`
  ADD PRIMARY KEY (`ReadingHistoryResourceID`);

--
-- Indexes for table `ResultMsg`
--
ALTER TABLE `ResultMsg`
  ADD PRIMARY KEY (`ResultMsgID`);

--
-- Indexes for table `ServerToClientReturns`
--
ALTER TABLE `ServerToClientReturns`
  ADD PRIMARY KEY (`ServerToClientReturnID`);

--
-- Indexes for table `SystemDBLog`
--
ALTER TABLE `SystemDBLog`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `UserActivitiesLogs`
--
ALTER TABLE `UserActivitiesLogs`
  ADD PRIMARY KEY (`LogID`);

--
-- Indexes for table `Users`
--
ALTER TABLE `Users`
  ADD PRIMARY KEY (`UserID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ContentConfig`
--
ALTER TABLE `ContentConfig`
  MODIFY `ContentConfigID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ContentEmbeddedItems`
--
ALTER TABLE `ContentEmbeddedItems`
  MODIFY `ItemID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ContentParols`
--
ALTER TABLE `ContentParols`
  MODIFY `ContentParolID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ContentRecordingMetadata`
--
ALTER TABLE `ContentRecordingMetadata`
  MODIFY `RecordingMetadataID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ContentRecordingSegments`
--
ALTER TABLE `ContentRecordingSegments`
  MODIFY `ContentSegmentID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ContentRecordingTasks`
--
ALTER TABLE `ContentRecordingTasks`
  MODIFY `ContentRecordingTaskID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Contents`
--
ALTER TABLE `Contents`
  MODIFY `ContentID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `DistributedResourcePages`
--
ALTER TABLE `DistributedResourcePages`
  MODIFY `ResourcePageID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `DistributedResources`
--
ALTER TABLE `DistributedResources`
  MODIFY `ResourceID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ExternalCommandsLogs`
--
ALTER TABLE `ExternalCommandsLogs`
  MODIFY `LogID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ImportContents`
--
ALTER TABLE `ImportContents`
  MODIFY `ImportContentID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `LanguagePairs`
--
ALTER TABLE `LanguagePairs`
  MODIFY `LanguagePairID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Languages`
--
ALTER TABLE `Languages`
  MODIFY `LanguageID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ParolPairs`
--
ALTER TABLE `ParolPairs`
  MODIFY `ParolPairID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ReadingHistories`
--
ALTER TABLE `ReadingHistories`
  MODIFY `ReadingHistoryID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ReadingHistoryResources`
--
ALTER TABLE `ReadingHistoryResources`
  MODIFY `ReadingHistoryResourceID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ResultMsg`
--
ALTER TABLE `ResultMsg`
  MODIFY `ResultMsgID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `ServerToClientReturns`
--
ALTER TABLE `ServerToClientReturns`
  MODIFY `ServerToClientReturnID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `SystemDBLog`
--
ALTER TABLE `SystemDBLog`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `UserActivitiesLogs`
--
ALTER TABLE `UserActivitiesLogs`
  MODIFY `LogID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `Users`
--
ALTER TABLE `Users`
  MODIFY `UserID` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;
