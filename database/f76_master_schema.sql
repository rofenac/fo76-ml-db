-- MySQL dump 10.13  Distrib 8.0.44, for Linux (x86_64)
--
-- Host: localhost    Database: f76
-- ------------------------------------------------------
-- Server version	8.0.44-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `armor`
--

DROP TABLE IF EXISTS `armor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `armor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `armor_class_id` int DEFAULT NULL,
  `armor_slot_id` int DEFAULT NULL,
  `armor_type_id` int DEFAULT NULL,
  `damage_resistance` varchar(64) DEFAULT NULL,
  `energy_resistance` varchar(64) DEFAULT NULL,
  `radiation_resistance` varchar(64) DEFAULT NULL,
  `cryo_resistance` varchar(64) DEFAULT NULL,
  `fire_resistance` varchar(64) DEFAULT NULL,
  `poison_resistance` varchar(64) DEFAULT NULL,
  `set_name` varchar(128) DEFAULT NULL,
  `level` varchar(64) DEFAULT NULL,
  `source_url` text,
  PRIMARY KEY (`id`),
  KEY `idx_armor_name` (`name`),
  KEY `idx_armor_set` (`set_name`),
  KEY `idx_armor_level` (`level`),
  KEY `idx_armor_class_id` (`armor_class_id`),
  KEY `idx_armor_slot_id` (`armor_slot_id`),
  KEY `idx_armor_type_id` (`armor_type_id`),
  KEY `idx_armor_type_class_slot` (`armor_type_id`,`armor_class_id`,`armor_slot_id`),
  CONSTRAINT `fk_armor_class` FOREIGN KEY (`armor_class_id`) REFERENCES `armor_classes` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_armor_slot` FOREIGN KEY (`armor_slot_id`) REFERENCES `armor_slots` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_armor_type` FOREIGN KEY (`armor_type_id`) REFERENCES `armor_types` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=478 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `armor_classes`
--

DROP TABLE IF EXISTS `armor_classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `armor_classes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_armor_class` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `armor_slots`
--

DROP TABLE IF EXISTS `armor_slots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `armor_slots` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_armor_slot` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `armor_types`
--

DROP TABLE IF EXISTS `armor_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `armor_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_armor_type` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collectible_effects`
--

DROP TABLE IF EXISTS `collectible_effects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collectible_effects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `collectible_id` int NOT NULL,
  `effect_type_id` int NOT NULL,
  `value` decimal(10,2) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  KEY `idx_ceff_collectible` (`collectible_id`),
  KEY `idx_ceff_type` (`effect_type_id`),
  CONSTRAINT `collectible_effects_ibfk_1` FOREIGN KEY (`collectible_id`) REFERENCES `collectibles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `collectible_effects_ibfk_2` FOREIGN KEY (`effect_type_id`) REFERENCES `effect_types` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collectible_series`
--

DROP TABLE IF EXISTS `collectible_series`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collectible_series` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `collectible_type_id` int NOT NULL,
  `description` text,
  `total_issues` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_series_name` (`name`),
  KEY `idx_series_type` (`collectible_type_id`),
  CONSTRAINT `collectible_series_ibfk_1` FOREIGN KEY (`collectible_type_id`) REFERENCES `collectible_types` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collectible_special_modifiers`
--

DROP TABLE IF EXISTS `collectible_special_modifiers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collectible_special_modifiers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `collectible_id` int NOT NULL,
  `special_id` int NOT NULL,
  `modifier` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_csm_collectible` (`collectible_id`),
  KEY `idx_csm_special` (`special_id`),
  CONSTRAINT `collectible_special_modifiers_ibfk_1` FOREIGN KEY (`collectible_id`) REFERENCES `collectibles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `collectible_special_modifiers_ibfk_2` FOREIGN KEY (`special_id`) REFERENCES `special_attributes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collectible_types`
--

DROP TABLE IF EXISTS `collectible_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collectible_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_collectible_type_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collectibles`
--

DROP TABLE IF EXISTS `collectibles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `collectibles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `collectible_type_id` int NOT NULL,
  `series_id` int DEFAULT NULL,
  `issue_number` int DEFAULT NULL,
  `duration_seconds` int DEFAULT NULL,
  `stacking_behavior` enum('no_stack','duration_extends','effect_stacks') DEFAULT 'duration_extends',
  `weight` decimal(5,2) DEFAULT '0.00',
  `value` int DEFAULT NULL,
  `form_id` char(8) DEFAULT NULL,
  `source_url` text,
  `spawn_locations` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_collectible_name` (`name`),
  KEY `idx_collectible_type` (`collectible_type_id`),
  KEY `idx_collectible_series` (`series_id`),
  KEY `idx_collectible_issue` (`issue_number`),
  CONSTRAINT `collectibles_ibfk_1` FOREIGN KEY (`collectible_type_id`) REFERENCES `collectible_types` (`id`),
  CONSTRAINT `collectibles_ibfk_2` FOREIGN KEY (`series_id`) REFERENCES `collectible_series` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `consumables`
--

DROP TABLE IF EXISTS `consumables`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consumables` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `category` enum('food','drink','chem','aid','alcohol','beverage') NOT NULL,
  `subcategory` varchar(64) DEFAULT NULL,
  `effects` text,
  `duration` varchar(64) DEFAULT NULL,
  `hp_restore` varchar(32) DEFAULT NULL,
  `rads` varchar(32) DEFAULT NULL,
  `hunger_satisfaction` varchar(32) DEFAULT NULL,
  `thirst_satisfaction` varchar(32) DEFAULT NULL,
  `special_modifiers` text,
  `addiction_risk` varchar(128) DEFAULT NULL,
  `disease_risk` varchar(32) DEFAULT NULL,
  `weight` decimal(5,2) DEFAULT NULL,
  `value` int DEFAULT NULL,
  `form_id` char(8) DEFAULT NULL,
  `crafting_station` varchar(64) DEFAULT NULL,
  `source_url` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_consumable_name` (`name`),
  KEY `idx_consumable_category` (`category`),
  KEY `idx_consumable_subcategory` (`subcategory`)
) ENGINE=InnoDB AUTO_INCREMENT=181 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `effect_types`
--

DROP TABLE IF EXISTS `effect_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `effect_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `category` enum('buff','debuff','healing','damage','resistance','special','resource') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_effect_category` (`category`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `legendary_perk_ranks`
--

DROP TABLE IF EXISTS `legendary_perk_ranks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `legendary_perk_ranks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `legendary_perk_id` int NOT NULL,
  `rank` int NOT NULL,
  `description` text,
  `effect_value` varchar(128) DEFAULT NULL,
  `effect_type` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_legendary_perk_rank` (`legendary_perk_id`,`rank`),
  CONSTRAINT `fk_lpr_perk` FOREIGN KEY (`legendary_perk_id`) REFERENCES `legendary_perks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=225 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `legendary_perks`
--

DROP TABLE IF EXISTS `legendary_perks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `legendary_perks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `description` text,
  `race` varchar(32) DEFAULT 'Human, Ghoul',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_legendary_perk_name` (`name`),
  KEY `idx_legendary_race` (`race`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `legendary_effect_categories`
--

DROP TABLE IF EXISTS `legendary_effect_categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `legendary_effect_categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_category_name` (`name`),
  KEY `idx_category_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `legendary_effects`
--

DROP TABLE IF EXISTS `legendary_effects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `legendary_effects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `category_id` int NOT NULL,
  `star_level` int DEFAULT 1,
  `item_type` enum('weapon','armor','both') NOT NULL DEFAULT 'weapon',
  `description` text,
  `effect_value` varchar(128) DEFAULT NULL,
  `notes` text,
  `form_id` varchar(16) DEFAULT NULL,
  `source_url` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_effect_name_type` (`name`,`item_type`),
  KEY `idx_effect_category` (`category_id`),
  KEY `idx_effect_star_level` (`star_level`),
  KEY `idx_effect_item_type` (`item_type`),
  KEY `idx_effect_name` (`name`),
  CONSTRAINT `fk_effect_category` FOREIGN KEY (`category_id`) REFERENCES `legendary_effect_categories` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `legendary_effect_conditions`
--

DROP TABLE IF EXISTS `legendary_effect_conditions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `legendary_effect_conditions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `effect_id` int NOT NULL,
  `condition_type` varchar(64) NOT NULL,
  `condition_description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_effect_condition` (`effect_id`,`condition_type`),
  KEY `idx_condition_type` (`condition_type`),
  CONSTRAINT `fk_condition_effect` FOREIGN KEY (`effect_id`) REFERENCES `legendary_effects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mutation_effects`
--

DROP TABLE IF EXISTS `mutation_effects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mutation_effects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mutation_id` int NOT NULL,
  `effect_type` enum('positive','negative') NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_me_mutation` (`mutation_id`),
  KEY `idx_me_type` (`effect_type`),
  KEY `idx_mutation_effects_type` (`mutation_id`,`effect_type`),
  CONSTRAINT `fk_me_mutation` FOREIGN KEY (`mutation_id`) REFERENCES `mutations` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mutations`
--

DROP TABLE IF EXISTS `mutations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mutations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `positive_effects` text,
  `negative_effects` text,
  `form_id` char(8) DEFAULT NULL,
  `exclusive_with` varchar(128) DEFAULT NULL,
  `exclusive_with_id` int DEFAULT NULL,
  `suppression_perk` varchar(128) DEFAULT NULL,
  `suppression_perk_id` int DEFAULT NULL,
  `enhancement_perk` varchar(128) DEFAULT NULL,
  `enhancement_perk_id` int DEFAULT NULL,
  `source_url` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_mutation_name` (`name`),
  KEY `idx_mutation_name` (`name`),
  KEY `idx_mutation_suppression` (`suppression_perk_id`),
  KEY `idx_mutation_enhancement` (`enhancement_perk_id`),
  KEY `idx_mutation_exclusive` (`exclusive_with_id`),
  CONSTRAINT `fk_mutation_enhancement` FOREIGN KEY (`enhancement_perk_id`) REFERENCES `perks` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_mutation_exclusive` FOREIGN KEY (`exclusive_with_id`) REFERENCES `mutations` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_mutation_suppression` FOREIGN KEY (`suppression_perk_id`) REFERENCES `perks` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `perk_ranks`
--

DROP TABLE IF EXISTS `perk_ranks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `perk_ranks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `perk_id` int NOT NULL,
  `rank` int NOT NULL,
  `description` text NOT NULL,
  `form_id` char(8) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_perk_rank` (`perk_id`,`rank`),
  KEY `idx_prank_rank` (`rank`),
  CONSTRAINT `fk_pr_perk` FOREIGN KEY (`perk_id`) REFERENCES `perks` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=899 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `perks`
--

DROP TABLE IF EXISTS `perks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `perks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `special` char(1) DEFAULT NULL,
  `special_id` int DEFAULT NULL,
  `level` int DEFAULT NULL,
  `race` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_perk_name` (`name`),
  KEY `idx_perk_special` (`special`),
  KEY `idx_perk_race` (`race`),
  KEY `idx_perk_special_id` (`special_id`),
  CONSTRAINT `fk_perk_special` FOREIGN KEY (`special_id`) REFERENCES `special_attributes` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=481 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `races`
--

DROP TABLE IF EXISTS `races`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `races` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_race_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `special_attributes`
--

DROP TABLE IF EXISTS `special_attributes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `special_attributes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `code` char(1) NOT NULL,
  `name` varchar(32) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_special_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `v_armor_complete`
--

DROP TABLE IF EXISTS `v_armor_complete`;
/*!50001 DROP VIEW IF EXISTS `v_armor_complete`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_armor_complete` AS SELECT 
 1 AS `id`,
 1 AS `name`,
 1 AS `armor_type`,
 1 AS `class`,
 1 AS `slot`,
 1 AS `set_name`,
 1 AS `level`,
 1 AS `damage_resistance`,
 1 AS `energy_resistance`,
 1 AS `radiation_resistance`,
 1 AS `cryo_resistance`,
 1 AS `fire_resistance`,
 1 AS `poison_resistance`,
 1 AS `source_url`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_collectibles_complete`
--

DROP TABLE IF EXISTS `v_collectibles_complete`;
/*!50001 DROP VIEW IF EXISTS `v_collectibles_complete`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_collectibles_complete` AS SELECT 
 1 AS `collectible_id`,
 1 AS `collectible_name`,
 1 AS `collectible_type`,
 1 AS `series_name`,
 1 AS `issue_number`,
 1 AS `duration_seconds`,
 1 AS `duration`,
 1 AS `stacking_behavior`,
 1 AS `effects`,
 1 AS `special_modifiers`,
 1 AS `weight`,
 1 AS `value`,
 1 AS `form_id`,
 1 AS `spawn_locations`,
 1 AS `source_url`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_consumables_complete`
--

DROP TABLE IF EXISTS `v_consumables_complete`;
/*!50001 DROP VIEW IF EXISTS `v_consumables_complete`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_consumables_complete` AS SELECT 
 1 AS `consumable_id`,
 1 AS `consumable_name`,
 1 AS `category`,
 1 AS `subcategory`,
 1 AS `effects`,
 1 AS `duration`,
 1 AS `hp_restore`,
 1 AS `rads`,
 1 AS `hunger_satisfaction`,
 1 AS `thirst_satisfaction`,
 1 AS `special_modifiers`,
 1 AS `addiction_risk`,
 1 AS `disease_risk`,
 1 AS `weight`,
 1 AS `value`,
 1 AS `form_id`,
 1 AS `crafting_station`,
 1 AS `source_url`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_legendary_perks_all_ranks`
--

DROP TABLE IF EXISTS `v_legendary_perks_all_ranks`;
/*!50001 DROP VIEW IF EXISTS `v_legendary_perks_all_ranks`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_legendary_perks_all_ranks` AS SELECT 
 1 AS `legendary_perk_id`,
 1 AS `perk_name`,
 1 AS `base_description`,
 1 AS `race`,
 1 AS `rank`,
 1 AS `rank_description`,
 1 AS `effect_value`,
 1 AS `effect_type`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_legendary_effects_complete`
--

DROP TABLE IF EXISTS `v_legendary_effects_complete`;
/*!50001 DROP VIEW IF EXISTS `v_legendary_effects_complete`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_legendary_effects_complete` AS SELECT
 1 AS `effect_id`,
 1 AS `effect_name`,
 1 AS `category`,
 1 AS `star_level`,
 1 AS `item_type`,
 1 AS `description`,
 1 AS `effect_value`,
 1 AS `notes`,
 1 AS `form_id`,
 1 AS `conditions`,
 1 AS `source_url`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_weapon_legendary_effects`
--

DROP TABLE IF EXISTS `v_weapon_legendary_effects`;
/*!50001 DROP VIEW IF EXISTS `v_weapon_legendary_effects`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_weapon_legendary_effects` AS SELECT
 1 AS `effect_id`,
 1 AS `effect_name`,
 1 AS `category`,
 1 AS `star_level`,
 1 AS `description`,
 1 AS `effect_value`,
 1 AS `conditions`,
 1 AS `source_url`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_armor_legendary_effects`
--

DROP TABLE IF EXISTS `v_armor_legendary_effects`;
/*!50001 DROP VIEW IF EXISTS `v_armor_legendary_effects`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_armor_legendary_effects` AS SELECT
 1 AS `effect_id`,
 1 AS `effect_name`,
 1 AS `category`,
 1 AS `star_level`,
 1 AS `description`,
 1 AS `effect_value`,
 1 AS `conditions`,
 1 AS `source_url`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_mutations_complete`
--

DROP TABLE IF EXISTS `v_mutations_complete`;
/*!50001 DROP VIEW IF EXISTS `v_mutations_complete`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_mutations_complete` AS SELECT 
 1 AS `mutation_id`,
 1 AS `mutation_name`,
 1 AS `positive_effects`,
 1 AS `negative_effects`,
 1 AS `form_id`,
 1 AS `exclusive_with`,
 1 AS `suppression_perk`,
 1 AS `enhancement_perk`,
 1 AS `source_url`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_perks_all_ranks`
--

DROP TABLE IF EXISTS `v_perks_all_ranks`;
/*!50001 DROP VIEW IF EXISTS `v_perks_all_ranks`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_perks_all_ranks` AS SELECT 
 1 AS `perk_id`,
 1 AS `perk_name`,
 1 AS `special_attribute`,
 1 AS `special_code`,
 1 AS `min_level`,
 1 AS `race`,
 1 AS `rank`,
 1 AS `rank_description`,
 1 AS `form_id`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_weapon_mods_complete`
--

DROP TABLE IF EXISTS `v_weapon_mods_complete`;
/*!50001 DROP VIEW IF EXISTS `v_weapon_mods_complete`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_weapon_mods_complete` AS SELECT 
 1 AS `mod_id`,
 1 AS `weapon_name`,
 1 AS `slot_name`,
 1 AS `mod_name`,
 1 AS `damage_change`,
 1 AS `damage_is_percent`,
 1 AS `fire_rate_change`,
 1 AS `range_change`,
 1 AS `accuracy_change`,
 1 AS `ap_cost_change`,
 1 AS `recoil_change`,
 1 AS `spread_change`,
 1 AS `converts_to_auto`,
 1 AS `converts_to_semi`,
 1 AS `crit_damage_bonus`,
 1 AS `hip_fire_accuracy_bonus`,
 1 AS `armor_penetration`,
 1 AS `is_suppressed`,
 1 AS `is_scoped`,
 1 AS `mag_size_change`,
 1 AS `reload_speed_change`,
 1 AS `required_perk`,
 1 AS `required_perk_rank`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_weapons_with_perks`
--

DROP TABLE IF EXISTS `v_weapons_with_perks`;
/*!50001 DROP VIEW IF EXISTS `v_weapons_with_perks`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_weapons_with_perks` AS SELECT
 1 AS `id`,
 1 AS `weapon_name`,
 1 AS `weapon_type`,
 1 AS `weapon_class`,
 1 AS `level`,
 1 AS `damage`,
 1 AS `regular_perks`,
 1 AS `legendary_perks`,
 1 AS `mechanics`,
 1 AS `source_url`*/;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `weapon_classes`
--

DROP TABLE IF EXISTS `weapon_classes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapon_classes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_weapon_class` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weapon_legendary_perk_effects`
--

DROP TABLE IF EXISTS `weapon_legendary_perk_effects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapon_legendary_perk_effects` (
  `weapon_id` int NOT NULL,
  `legendary_perk_id` int NOT NULL,
  PRIMARY KEY (`weapon_id`,`legendary_perk_id`),
  KEY `fk_wlpe_perk` (`legendary_perk_id`),
  CONSTRAINT `fk_wlpe_perk` FOREIGN KEY (`legendary_perk_id`) REFERENCES `legendary_perks` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_wlpe_weapon` FOREIGN KEY (`weapon_id`) REFERENCES `weapons` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weapon_mechanic_types`
--

DROP TABLE IF EXISTS `weapon_mechanic_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapon_mechanic_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `description` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_mechanic_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weapon_mechanics`
--

DROP TABLE IF EXISTS `weapon_mechanics`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapon_mechanics` (
  `id` int NOT NULL AUTO_INCREMENT,
  `weapon_id` int NOT NULL,
  `mechanic_type_id` int NOT NULL,
  `numeric_value` decimal(10,2) DEFAULT NULL,
  `numeric_value_2` decimal(10,2) DEFAULT NULL,
  `string_value` varchar(255) DEFAULT NULL,
  `unit` varchar(32) DEFAULT NULL,
  `notes` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_weapon_mechanic` (`weapon_id`,`mechanic_type_id`),
  KEY `idx_wm_weapon` (`weapon_id`),
  KEY `idx_wm_mechanic` (`mechanic_type_id`),
  CONSTRAINT `weapon_mechanics_ibfk_1` FOREIGN KEY (`weapon_id`) REFERENCES `weapons` (`id`) ON DELETE CASCADE,
  CONSTRAINT `weapon_mechanics_ibfk_2` FOREIGN KEY (`mechanic_type_id`) REFERENCES `weapon_mechanic_types` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weapon_mod_crafting`
--

DROP TABLE IF EXISTS `weapon_mod_crafting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapon_mod_crafting` (
  `id` int NOT NULL AUTO_INCREMENT,
  `mod_id` int NOT NULL,
  `perk_id` int DEFAULT NULL,
  `perk_rank` int DEFAULT '1',
  PRIMARY KEY (`id`),
  KEY `idx_wmc_mod` (`mod_id`),
  KEY `fk_wmc_perk` (`perk_id`),
  CONSTRAINT `fk_wmc_mod` FOREIGN KEY (`mod_id`) REFERENCES `weapon_mods` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_wmc_perk` FOREIGN KEY (`perk_id`) REFERENCES `perks` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=297 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weapon_mod_slots`
--

DROP TABLE IF EXISTS `weapon_mod_slots`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapon_mod_slots` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `weapon_mod_slots`
--

LOCK TABLES `weapon_mod_slots` WRITE;
/*!40000 ALTER TABLE `weapon_mod_slots` DISABLE KEYS */;
INSERT INTO `weapon_mod_slots` VALUES (8,'barrel'),(9,'grip'),(10,'magazine'),(11,'muzzle'),(12,'receiver'),(13,'sight'),(14,'stock');
/*!40000 ALTER TABLE `weapon_mod_slots` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `weapon_mods`
--

DROP TABLE IF EXISTS `weapon_mods`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapon_mods` (
  `id` int NOT NULL AUTO_INCREMENT,
  `weapon_id` int NOT NULL,
  `slot_id` int NOT NULL,
  `name` varchar(128) NOT NULL,
  `damage_change` decimal(6,2) DEFAULT NULL,
  `damage_change_is_percent` tinyint(1) DEFAULT '0',
  `fire_rate_change` int DEFAULT NULL,
  `range_change` int DEFAULT NULL,
  `accuracy_change` int DEFAULT NULL,
  `ap_cost_change` decimal(5,2) DEFAULT NULL,
  `recoil_change` int DEFAULT NULL,
  `spread_change` decimal(5,2) DEFAULT NULL,
  `converts_to_auto` tinyint(1) DEFAULT '0',
  `converts_to_semi` tinyint(1) DEFAULT '0',
  `crit_damage_bonus` int DEFAULT NULL,
  `hip_fire_accuracy_bonus` int DEFAULT NULL,
  `armor_penetration` int DEFAULT NULL,
  `is_suppressed` tinyint(1) DEFAULT '0',
  `is_scoped` tinyint(1) DEFAULT '0',
  `mag_size_change` int DEFAULT NULL,
  `reload_speed_change` decimal(5,2) DEFAULT NULL,
  `weight_change` decimal(5,2) DEFAULT NULL,
  `value_change_percent` int DEFAULT NULL,
  `form_id` varchar(16) DEFAULT NULL,
  `source_url` text,
  PRIMARY KEY (`id`),
  KEY `idx_weapon_mod_weapon` (`weapon_id`),
  KEY `idx_weapon_mod_slot` (`slot_id`),
  KEY `idx_weapon_mod_name` (`name`),
  CONSTRAINT `fk_wm_slot` FOREIGN KEY (`slot_id`) REFERENCES `weapon_mod_slots` (`id`),
  CONSTRAINT `fk_wm_weapon` FOREIGN KEY (`weapon_id`) REFERENCES `weapons` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1149 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weapon_perk_rules`
--

DROP TABLE IF EXISTS `weapon_perk_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapon_perk_rules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `weapon_id` int NOT NULL,
  `perk_id` int NOT NULL,
  `weapon_class` enum('pistol','rifle','heavy','melee','explosive','any') DEFAULT 'any',
  `fire_mode` enum('auto','semi','any') DEFAULT 'any',
  `scope_state` enum('scoped','unscoped','any') DEFAULT 'any',
  `aim_state` enum('ads','hip_fire','any') DEFAULT 'any',
  `vats_state` enum('in_vats','out_vats','any') DEFAULT 'any',
  `mod_requirements` varchar(255) DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_wpr_weapon` (`weapon_id`),
  KEY `fk_wpr_perk` (`perk_id`),
  CONSTRAINT `fk_wpr_perk` FOREIGN KEY (`perk_id`) REFERENCES `perks` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_wpr_weapon` FOREIGN KEY (`weapon_id`) REFERENCES `weapons` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=127 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weapon_perks`
--

DROP TABLE IF EXISTS `weapon_perks`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapon_perks` (
  `weapon_id` int NOT NULL,
  `perk_id` int NOT NULL,
  PRIMARY KEY (`weapon_id`,`perk_id`),
  KEY `fk_wp_perk` (`perk_id`),
  CONSTRAINT `fk_wp_perk` FOREIGN KEY (`perk_id`) REFERENCES `perks` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_wp_weapon` FOREIGN KEY (`weapon_id`) REFERENCES `weapons` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weapon_types`
--

DROP TABLE IF EXISTS `weapon_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapon_types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_weapon_type` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weapons`
--

DROP TABLE IF EXISTS `weapons`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weapons` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `weapon_type_id` int DEFAULT NULL,
  `weapon_class_id` int DEFAULT NULL,
  `level` varchar(64) DEFAULT NULL,
  `damage` varchar(255) DEFAULT NULL,
  `perks_raw` text,
  `source_url` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_weapon_name` (`name`),
  KEY `idx_weapon_type_id` (`weapon_type_id`),
  KEY `idx_weapon_class_id` (`weapon_class_id`),
  KEY `idx_weapon_type_class` (`weapon_type_id`,`weapon_class_id`),
  CONSTRAINT `fk_weapon_class` FOREIGN KEY (`weapon_class_id`) REFERENCES `weapon_classes` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_weapon_type` FOREIGN KEY (`weapon_type_id`) REFERENCES `weapon_types` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=525 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'f76'
--

--
-- Final view structure for view `v_armor_complete`
--

/*!50001 DROP VIEW IF EXISTS `v_armor_complete`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`rofenac`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_armor_complete` AS select `a`.`id` AS `id`,`a`.`name` AS `name`,`at`.`name` AS `armor_type`,`ac`.`name` AS `class`,`asl`.`name` AS `slot`,`a`.`set_name` AS `set_name`,`a`.`level` AS `level`,`a`.`damage_resistance` AS `damage_resistance`,`a`.`energy_resistance` AS `energy_resistance`,`a`.`radiation_resistance` AS `radiation_resistance`,`a`.`cryo_resistance` AS `cryo_resistance`,`a`.`fire_resistance` AS `fire_resistance`,`a`.`poison_resistance` AS `poison_resistance`,`a`.`source_url` AS `source_url` from (((`armor` `a` left join `armor_types` `at` on((`a`.`armor_type_id` = `at`.`id`))) left join `armor_classes` `ac` on((`a`.`armor_class_id` = `ac`.`id`))) left join `armor_slots` `asl` on((`a`.`armor_slot_id` = `asl`.`id`))) order by `a`.`name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_collectibles_complete`
--

/*!50001 DROP VIEW IF EXISTS `v_collectibles_complete`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`rofenac`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_collectibles_complete` AS select `c`.`id` AS `collectible_id`,`c`.`name` AS `collectible_name`,`ct`.`name` AS `collectible_type`,`cs`.`name` AS `series_name`,`c`.`issue_number` AS `issue_number`,`c`.`duration_seconds` AS `duration_seconds`,(case when (`c`.`duration_seconds` >= 3600) then concat((`c`.`duration_seconds` / 3600),' hour(s)') when (`c`.`duration_seconds` >= 60) then concat((`c`.`duration_seconds` / 60),' minute(s)') else concat(`c`.`duration_seconds`,' second(s)') end) AS `duration`,`c`.`stacking_behavior` AS `stacking_behavior`,group_concat(distinct concat(`ce`.`description`) separator '; ') AS `effects`,group_concat(distinct concat((case when (`csm`.`modifier` > 0) then '+' else '' end),`csm`.`modifier`,' ',`sa`.`name`) order by `sa`.`name` ASC separator ', ') AS `special_modifiers`,`c`.`weight` AS `weight`,`c`.`value` AS `value`,`c`.`form_id` AS `form_id`,`c`.`spawn_locations` AS `spawn_locations`,`c`.`source_url` AS `source_url` from (((((`collectibles` `c` left join `collectible_types` `ct` on((`c`.`collectible_type_id` = `ct`.`id`))) left join `collectible_series` `cs` on((`c`.`series_id` = `cs`.`id`))) left join `collectible_effects` `ce` on((`c`.`id` = `ce`.`collectible_id`))) left join `collectible_special_modifiers` `csm` on((`c`.`id` = `csm`.`collectible_id`))) left join `special_attributes` `sa` on((`csm`.`special_id` = `sa`.`id`))) group by `c`.`id`,`c`.`name`,`ct`.`name`,`cs`.`name`,`c`.`issue_number`,`c`.`duration_seconds`,`c`.`stacking_behavior`,`c`.`weight`,`c`.`value`,`c`.`form_id`,`c`.`spawn_locations`,`c`.`source_url` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_consumables_complete`
--

/*!50001 DROP VIEW IF EXISTS `v_consumables_complete`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_consumables_complete` AS select `c`.`id` AS `consumable_id`,`c`.`name` AS `consumable_name`,`c`.`category` AS `category`,`c`.`subcategory` AS `subcategory`,`c`.`effects` AS `effects`,`c`.`duration` AS `duration`,`c`.`hp_restore` AS `hp_restore`,`c`.`rads` AS `rads`,`c`.`hunger_satisfaction` AS `hunger_satisfaction`,`c`.`thirst_satisfaction` AS `thirst_satisfaction`,`c`.`special_modifiers` AS `special_modifiers`,`c`.`addiction_risk` AS `addiction_risk`,`c`.`disease_risk` AS `disease_risk`,`c`.`weight` AS `weight`,`c`.`value` AS `value`,`c`.`form_id` AS `form_id`,`c`.`crafting_station` AS `crafting_station`,`c`.`source_url` AS `source_url` from `consumables` `c` order by `c`.`category`,`c`.`name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_legendary_perks_all_ranks`
--

/*!50001 DROP VIEW IF EXISTS `v_legendary_perks_all_ranks`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_legendary_perks_all_ranks` AS select `lp`.`id` AS `legendary_perk_id`,`lp`.`name` AS `perk_name`,`lp`.`description` AS `base_description`,`lp`.`race` AS `race`,`lpr`.`rank` AS `rank`,`lpr`.`description` AS `rank_description`,`lpr`.`effect_value` AS `effect_value`,`lpr`.`effect_type` AS `effect_type` from (`legendary_perks` `lp` left join `legendary_perk_ranks` `lpr` on((`lp`.`id` = `lpr`.`legendary_perk_id`))) order by `lp`.`name`,`lpr`.`rank` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_legendary_effects_complete`
--

/*!50001 DROP VIEW IF EXISTS `v_legendary_effects_complete`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_legendary_effects_complete` AS select `le`.`id` AS `effect_id`,`le`.`name` AS `effect_name`,`lec`.`name` AS `category`,`le`.`star_level` AS `star_level`,`le`.`item_type` AS `item_type`,`le`.`description` AS `description`,`le`.`effect_value` AS `effect_value`,`le`.`notes` AS `notes`,`le`.`form_id` AS `form_id`,group_concat(concat(`lecond`.`condition_type`,': ',`lecond`.`condition_description`) separator '; ') AS `conditions`,`le`.`source_url` AS `source_url` from ((`legendary_effects` `le` join `legendary_effect_categories` `lec` on((`le`.`category_id` = `lec`.`id`))) left join `legendary_effect_conditions` `lecond` on((`le`.`id` = `lecond`.`effect_id`))) group by `le`.`id`,`le`.`name`,`lec`.`name`,`le`.`star_level`,`le`.`item_type`,`le`.`description`,`le`.`effect_value`,`le`.`notes`,`le`.`form_id`,`le`.`source_url` order by `le`.`item_type`,`lec`.`name`,`le`.`star_level`,`le`.`name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_weapon_legendary_effects`
--

/*!50001 DROP VIEW IF EXISTS `v_weapon_legendary_effects`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_weapon_legendary_effects` AS select `le`.`id` AS `effect_id`,`le`.`name` AS `effect_name`,`lec`.`name` AS `category`,`le`.`star_level` AS `star_level`,`le`.`description` AS `description`,`le`.`effect_value` AS `effect_value`,group_concat(concat(`lecond`.`condition_type`,': ',`lecond`.`condition_description`) separator '; ') AS `conditions`,`le`.`source_url` AS `source_url` from ((`legendary_effects` `le` join `legendary_effect_categories` `lec` on((`le`.`category_id` = `lec`.`id`))) left join `legendary_effect_conditions` `lecond` on((`le`.`id` = `lecond`.`effect_id`))) where (`le`.`item_type` in ('weapon','both')) group by `le`.`id`,`le`.`name`,`lec`.`name`,`le`.`star_level`,`le`.`description`,`le`.`effect_value`,`le`.`source_url` order by `lec`.`name`,`le`.`star_level`,`le`.`name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_armor_legendary_effects`
--

/*!50001 DROP VIEW IF EXISTS `v_armor_legendary_effects`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_armor_legendary_effects` AS select `le`.`id` AS `effect_id`,`le`.`name` AS `effect_name`,`lec`.`name` AS `category`,`le`.`star_level` AS `star_level`,`le`.`description` AS `description`,`le`.`effect_value` AS `effect_value`,group_concat(concat(`lecond`.`condition_type`,': ',`lecond`.`condition_description`) separator '; ') AS `conditions`,`le`.`source_url` AS `source_url` from ((`legendary_effects` `le` join `legendary_effect_categories` `lec` on((`le`.`category_id` = `lec`.`id`))) left join `legendary_effect_conditions` `lecond` on((`le`.`id` = `lecond`.`effect_id`))) where (`le`.`item_type` in ('armor','both')) group by `le`.`id`,`le`.`name`,`lec`.`name`,`le`.`star_level`,`le`.`description`,`le`.`effect_value`,`le`.`source_url` order by `lec`.`name`,`le`.`star_level`,`le`.`name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_mutations_complete`
--

/*!50001 DROP VIEW IF EXISTS `v_mutations_complete`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`rofenac`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_mutations_complete` AS select `m`.`id` AS `mutation_id`,`m`.`name` AS `mutation_name`,group_concat(distinct (case when (`me`.`effect_type` = 'positive') then `me`.`description` end) separator '; ') AS `positive_effects`,group_concat(distinct (case when (`me`.`effect_type` = 'negative') then `me`.`description` end) separator '; ') AS `negative_effects`,`m`.`form_id` AS `form_id`,`m2`.`name` AS `exclusive_with`,`ps`.`name` AS `suppression_perk`,`pe`.`name` AS `enhancement_perk`,`m`.`source_url` AS `source_url` from ((((`mutations` `m` left join `mutation_effects` `me` on((`m`.`id` = `me`.`mutation_id`))) left join `mutations` `m2` on((`m`.`exclusive_with_id` = `m2`.`id`))) left join `perks` `ps` on((`m`.`suppression_perk_id` = `ps`.`id`))) left join `perks` `pe` on((`m`.`enhancement_perk_id` = `pe`.`id`))) group by `m`.`id`,`m`.`name`,`m`.`form_id`,`m2`.`name`,`ps`.`name`,`pe`.`name`,`m`.`source_url` order by `m`.`name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_perks_all_ranks`
--

/*!50001 DROP VIEW IF EXISTS `v_perks_all_ranks`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`rofenac`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_perks_all_ranks` AS select `p`.`id` AS `perk_id`,`p`.`name` AS `perk_name`,`sa`.`name` AS `special_attribute`,`p`.`special` AS `special_code`,`p`.`level` AS `min_level`,`p`.`race` AS `race`,`pr`.`rank` AS `rank`,`pr`.`description` AS `rank_description`,`pr`.`form_id` AS `form_id` from ((`perks` `p` left join `special_attributes` `sa` on((`p`.`special_id` = `sa`.`id`))) left join `perk_ranks` `pr` on((`p`.`id` = `pr`.`perk_id`))) order by `p`.`name`,`pr`.`rank` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_weapon_mods_complete`
--

/*!50001 DROP VIEW IF EXISTS `v_weapon_mods_complete`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_weapon_mods_complete` AS select `wm`.`id` AS `mod_id`,`w`.`name` AS `weapon_name`,`wms`.`name` AS `slot_name`,`wm`.`name` AS `mod_name`,`wm`.`damage_change` AS `damage_change`,`wm`.`damage_change_is_percent` AS `damage_is_percent`,`wm`.`fire_rate_change` AS `fire_rate_change`,`wm`.`range_change` AS `range_change`,`wm`.`accuracy_change` AS `accuracy_change`,`wm`.`ap_cost_change` AS `ap_cost_change`,`wm`.`recoil_change` AS `recoil_change`,`wm`.`spread_change` AS `spread_change`,`wm`.`converts_to_auto` AS `converts_to_auto`,`wm`.`converts_to_semi` AS `converts_to_semi`,`wm`.`crit_damage_bonus` AS `crit_damage_bonus`,`wm`.`hip_fire_accuracy_bonus` AS `hip_fire_accuracy_bonus`,`wm`.`armor_penetration` AS `armor_penetration`,`wm`.`is_suppressed` AS `is_suppressed`,`wm`.`is_scoped` AS `is_scoped`,`wm`.`mag_size_change` AS `mag_size_change`,`wm`.`reload_speed_change` AS `reload_speed_change`,`p`.`name` AS `required_perk`,`wmc`.`perk_rank` AS `required_perk_rank` from ((((`weapon_mods` `wm` join `weapons` `w` on((`wm`.`weapon_id` = `w`.`id`))) join `weapon_mod_slots` `wms` on((`wm`.`slot_id` = `wms`.`id`))) left join `weapon_mod_crafting` `wmc` on((`wm`.`id` = `wmc`.`mod_id`))) left join `perks` `p` on((`wmc`.`perk_id` = `p`.`id`))) order by `w`.`name`,`wms`.`name`,`wm`.`name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_weapons_with_perks`
--

/*!50001 DROP VIEW IF EXISTS `v_weapons_with_perks`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`rofenac`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_weapons_with_perks` AS select `w`.`id` AS `id`,`w`.`name` AS `weapon_name`,`wt`.`name` AS `weapon_type`,`wc`.`name` AS `weapon_class`,`w`.`level` AS `level`,`w`.`damage` AS `damage`,group_concat(distinct `p`.`name` order by `p`.`name` ASC separator '; ') AS `regular_perks`,group_concat(distinct `lp`.`name` order by `lp`.`name` ASC separator '; ') AS `legendary_perks`,group_concat(distinct concat(`wmt`.`name`,case when (`wm`.`numeric_value` is not null) then concat(': ',`wm`.`numeric_value`,coalesce(`wm`.`unit`,'')) when (`wm`.`string_value` is not null) then concat(': ',`wm`.`string_value`) else '' end,case when (`wm`.`numeric_value_2` is not null) then concat(' to ',`wm`.`numeric_value_2`,coalesce(`wm`.`unit`,'')) else '' end) order by `wmt`.`name` ASC separator '; ') AS `mechanics`,`w`.`source_url` AS `source_url` from ((((((((`weapons` `w` left join `weapon_types` `wt` on((`w`.`weapon_type_id` = `wt`.`id`))) left join `weapon_classes` `wc` on((`w`.`weapon_class_id` = `wc`.`id`))) left join `weapon_perks` `wp` on((`w`.`id` = `wp`.`weapon_id`))) left join `perks` `p` on((`wp`.`perk_id` = `p`.`id`))) left join `weapon_legendary_perk_effects` `wlpe` on((`w`.`id` = `wlpe`.`weapon_id`))) left join `legendary_perks` `lp` on((`wlpe`.`legendary_perk_id` = `lp`.`id`))) left join `weapon_mechanics` `wm` on((`w`.`id` = `wm`.`weapon_id`))) left join `weapon_mechanic_types` `wmt` on((`wm`.`mechanic_type_id` = `wmt`.`id`))) group by `w`.`id`,`w`.`name`,`wt`.`name`,`wc`.`name`,`w`.`level`,`w`.`damage`,`w`.`source_url` order by `w`.`name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-25 12:50:44
