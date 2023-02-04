ALTER TABLE `LARA-portal`.`Users` 
RENAME TO  `LARA-portal`.`Accounts` ;

CREATE TABLE `LARA-portal`.`Users` (
  `UserID` INT NOT NULL AUTO_INCREMENT,
  `FirstName` VARCHAR(500) NULL,
  `MiddleName` VARCHAR(500) NULL,
  `LastName` VARCHAR(500) NULL,
  `DisplayName` VARCHAR(500) NULL,
  `Gender` ENUM('undefined', 'male', 'female', 'other', 'unsaid') NULL DEFAULT 'undefined',
  `CountryID` INT NULL,
  `BirthDate` DATE NULL,
  `WebsiteAddress` VARCHAR(1000) NULL,
  `Interests` TEXT NULL,
  `AboutMe` TEXT NULL,
  `PhotoExtension` VARCHAR(45) NULL,
  PRIMARY KEY (`UserID`));
  
CREATE TABLE `LARA-portal`.`UserLanguages` (
  `UserLanguageID` INT NOT NULL AUTO_INCREMENT,
  `UserID` INT NOT NULL,
  `LanguageID` INT NOT NULL,
  `LanguageLevel` ENUM('elementary', 'limited_proficiency', 'professional_proficiency', 'full_proficiency', 'native_bilingual_proficiency') NOT NULL,
  PRIMARY KEY (`UserLanguageID`));

ALTER TABLE `LARA-portal`.`UserActivitiesLogs` 
CHANGE COLUMN `RelatedPage` `RelatedPage` VARCHAR(500) NULL DEFAULT NULL ;
