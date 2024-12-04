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

DROP TABLE IF EXISTS `AUTH_CODES`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AUTH_CODES` (
  `auth_code` varchar(300) NOT NULL,
  `user_id` int NOT NULL,
  `user_type` varchar(50) NOT NULL,
  `expires_at` timestamp NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`auth_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AUTH_CODES`
--

LOCK TABLES `AUTH_CODES` WRITE;
/*!40000 ALTER TABLE `AUTH_CODES` DISABLE KEYS */;
/*!40000 ALTER TABLE `AUTH_CODES` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ADMIN`
--

LOCK TABLES `ADMIN` WRITE;
/*!40000 ALTER TABLE `ADMIN` DISABLE KEYS */;
INSERT INTO `ADMIN` VALUES (1,'admin_test_1','$2b$12$64YVUDG5F0tMGGtjF7bWX.pe3lXxVYHfHkFbnBb938KjZsz1EaUPW','admin_test_1@test.com',0,'0'),(2,'admin_test_2','$2b$12$9M6IQoABYNhALGXgGTxGIuxZQiWJO95AeFHT4g6/0XaC5f2L4a8Sa','admin_test_2@test.com',0,'0'),(3,'admin_test_3','$2b$12$ApvBVuy/CThKVDNkpiMnV.MhcTzP0/IRPg93xfhpNDWvzxjDK4dKa','admin_test_3@test.com',0,'0'),(4,'admin_test_4','$2b$12$P4XxRrUt1jl6a5G.2QWgzetw.TbBx1wCnfnTb0MOZOD.jxmypXtv2','admin_test_4@test.com',0,'0');
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
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `PLAYER`
--

LOCK TABLES `PLAYER` WRITE;
/*!40000 ALTER TABLE `PLAYER` DISABLE KEYS */;
INSERT INTO `PLAYER` VALUES (-1,'tresh','$2b$12$oLVN8TcwH5wQN0H0uSXsYO388fD1mSix5n.msaywlZ9wArSY8NgG.','tresh@system.sis',100,'0',NULL),(1,'test_1','$2b$12$oLVN8TcwH5wQN0H0uSXsYO388fD1mSix5n.msaywlZ9wArSY8NgG.','test_1@test.com',20,'0',NULL),(2,'test_2','$2b$12$WsqSbe53R8a.uUAIQ7JVRe4wB0AGH/bPr1aTtE6DsoD/VFnrDlwtS','test_2@test.com',20,'0',NULL),(3,'test_3','$2b$12$WHDLmtrs/5fx7PNra1NJOeJn/Zj9GW1gNKp7U1/sUH2eBhngf55e6','test_3@test.com',20,'0',NULL),(4,'test_4','$2b$12$gFo9xEtn.UeFuRS5Gg1EnOXhlCfFws8LTImPELV5SlHK3/L7A7XE6','test_4@test.com',20,'0',NULL);
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

-- Dump completed on 2024-12-02 12:53:39
