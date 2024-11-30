-- MySQL dump 10.13  Distrib 8.0.40, for Linux (x86_64)
--
-- Host: localhost    Database: users
-- ------------------------------------------------------
-- Server version	8.0.40

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
-- Table structure for table `ADMIN`
--

DROP TABLE IF EXISTS `ADMIN`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ADMIN` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT NULL,
  `password` text,
  `email` varchar(255) DEFAULT NULL,
  `currency_balance` int DEFAULT '0',
  `session_token` text,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ADMIN`
--

LOCK TABLES `ADMIN` WRITE;
/*!40000 ALTER TABLE `ADMIN` DISABLE KEYS */;
INSERT INTO `ADMIN` VALUES (1,'provando','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo4LCJ1c2VyX3R5cGUiOiJBRE1JTiIsImV4cGlyYXRpb24iOiIyMDI0LTExLTI5IDIxOjAyOjE0LjMxNzk4NCJ9.PBrDCJpexDvz0zJj9iV8SXzLmKvgHzDHTgUWj3dpI-A','aa@gmail.com',0,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VyX3R5cGUiOiJBRE1JTiIsImV4cGlyYXRpb24iOiIyMDI0LTExLTIyIDE2OjAwOjI1LjMyODU4MiJ9.oAs_Qfoc4hqBFfNX5s9ILJo0cz66WCgQJnj6l8yNtOc'),(2,'provando121_','6258a5e0eb772911d4f92be5b5db0e14511edbe01d1d0ddd1d5a2cb9db9a56ba','prova12312@gmail.con',0,'0'),(3,'user_5jjkf11y_1732710916302','b02b003b2364dce8d60eac19aa5ea537aaebb4c1778c5f0dfe3e1dde8c3173cf','user_5jjkf11y_1732710916302@example.com',0,'0'),(4,'admin_test_1','6258a5e0eb772911d4f92be5b5db0e14511edbe01d1d0ddd1d5a2cb9db9a56ba','user_xfmymfkn_1732710950960@example.com',0,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0LCJ1c2VyX3R5cGUiOiJBRE1JTiIsImV4cGlyYXRpb24iOiIyMDI0LTExLTI3IDIyOjA2OjAyLjk2NTQzMCJ9.hjUnW-vAEFRMVtsK8dQbMRNbC73xMLhAuYyQu3YQjoA'),(5,'admin_test_2','6258a5e0eb772911d4f92be5b5db0e14511edbe01d1d0ddd1d5a2cb9db9a56ba','user_o4btr119_1732710956389@example.com',0,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo1LCJ1c2VyX3R5cGUiOiJBRE1JTiIsImV4cGlyYXRpb24iOiIyMDI0LTExLTI3IDIyOjA2OjAzLjAxMzQ1NiJ9.wsCFL3KryM5W145hBskXqgcEUdW7_hJxUnN7ez3H6Vg'),(6,'admin_test_3','6258a5e0eb772911d4f92be5b5db0e14511edbe01d1d0ddd1d5a2cb9db9a56ba','user_meev1bdm_1732712921141@example.com',0,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJ1c2VyX3R5cGUiOiJBRE1JTiIsImV4cGlyYXRpb24iOiIyMDI0LTExLTI3IDIyOjA2OjAzLjA5NDAxMyJ9.AR3R5tJ4i_A81CcL83VHahPBosxGHx2auVvi7pjRYk0'),(7,'admin_test_4','6258a5e0eb772911d4f92be5b5db0e14511edbe01d1d0ddd1d5a2cb9db9a56ba','user_974jcl3a_1732712948243@example.com',0,'0'),(8,'user_r5rfljb8_1732978327775','4b065c8ba906f01ab999c5d3aaf4ebafb63d90104f9d2cb39f7d606928aeed22','user_r5rfljb8_1732978327775@example.com',0,'0');
/*!40000 ALTER TABLE `ADMIN` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `PLAYER`
--

DROP TABLE IF EXISTS `PLAYER`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `PLAYER` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT NULL,
  `password` text,
  `email` varchar(255) DEFAULT NULL,
  `currency_balance` int DEFAULT '20',
  `session_token` text,
  `image` mediumblob,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PLAYER`
--

LOCK TABLES `PLAYER` WRITE;
/*!40000 ALTER TABLE `PLAYER` DISABLE KEYS */;
INSERT INTO `PLAYER` VALUES (1,'user_nyaghbdv','38c3c12406fa7fc5b475d6c8ebac097056f2b6115a2aa8639f3d860c7ce13a0f','user_nyaghbdv@example.com',52,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VyX3R5cGUiOiJQTEFZRVIiLCJleHBpcmF0aW9uIjoiMjAyNC0xMS0zMCAyMDo1MjowNy4yODEyNzgifQ.seowDNbneIZg4UtTh871HKtqEVMRa95lW7l1gZYeKR0',NULL);
/*!40000 ALTER TABLE `PLAYER` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-30 14:52:39
