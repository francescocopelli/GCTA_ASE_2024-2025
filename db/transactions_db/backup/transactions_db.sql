-- MySQL dump 10.13  Distrib 8.0.40, for Linux (x86_64)
--
-- Host: localhost    Database: transactions
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
-- Table structure for table `Transactions`
--

DROP TABLE IF EXISTS `Transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Transactions` (
  `transaction_id` text,
  `user_id` int DEFAULT NULL,
  `transaction_type` varchar(255) DEFAULT NULL,
  `amount` int DEFAULT NULL,
  `transaction_date` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Transactions`
--

LOCK TABLES `Transactions` WRITE;
/*!40000 ALTER TABLE `Transactions` DISABLE KEYS */;
INSERT INTO `Transactions` VALUES ('3e984c3d-cbb2-4163-a966-d4e34ed422d5',1,'unknown',1,'0000-00-00 00:00:00'),('b425a5be-8c34-44fb-bda7-8bbe5db1e06a',1,'unknown',1,'0000-00-00 00:00:00'),('4aec5a64-1dd9-48a3-b89f-361f6e47eddc',1,'unknown',1,'0000-00-00 00:00:00'),('d9d47981-f918-4323-b140-ff41741292ed',1,'roll_purchase',1,'0000-00-00 00:00:00'),('32ebe870-f2cb-4d24-ab25-f8f4966d987f',1,'roll_purchase',1,'0000-00-00 00:00:00'),('edf2344d-f134-4fe4-94b6-23f1282ae4e2',1,'roll_purchase',1,'0000-00-00 00:00:00'),('86c69c4a-df45-4d51-968d-70f0dc87c635',1,'roll_purchase',1,'0000-00-00 00:00:00'),('91b65a2c-852a-4f29-b0df-81ef1482ac56',1,'roll_purchase',1,'0000-00-00 00:00:00'),('6851b268-9424-4998-a585-9c9ed1a5b216',1,'roll_purchase',1,'0000-00-00 00:00:00'),('f7b62ec5-6c91-44b5-805f-19cd04fce96e',1,'roll_purchase',1,'0000-00-00 00:00:00'),('59aaa12c-9e14-40fb-8721-f7ffb26902a2',1,'roll_purchase',1,'0000-00-00 00:00:00'),('048d0bc3-fb1c-49ef-9313-c1b7c1d0134f',1,'roll_purchase',1,'0000-00-00 00:00:00'),('f42dec42-c6a6-4169-8851-161bd49e9ebb',1,'roll_purchase',1,'0000-00-00 00:00:00'),('3bd6b94b-868e-4d5e-a232-5cf57551331e',1,'roll_purchase',1,'0000-00-00 00:00:00'),('c6e71a71-216e-4041-b024-403089b4695b',1,'roll_purchase',1,'0000-00-00 00:00:00'),('0632a2ea-dc28-4b60-b4b7-75abbcd7b3af',1,'roll_purchase',1,'0000-00-00 00:00:00'),('86a506fe-398e-4f68-9924-a3d0f5a90f2f',1,'roll_purchase',5,'0000-00-00 00:00:00'),('7fc62de1-26bb-458a-90e2-c5c3f28c0600',1,'unknown',3,'0000-00-00 00:00:00'),('b92e21f6-f131-489e-9b9d-2ebf21807ae5',1,'unknown',3,'0000-00-00 00:00:00'),('cff776fc-acf0-4be8-91cf-aabc1ba959ed',2,'auction_credit',152,'0000-00-00 00:00:00'),('da9a17ec-70c9-45fe-83fe-1657cec4b40d',1,'auction_debit',152,'0000-00-00 00:00:00'),('e3e6cba8-3e69-4977-ac0b-793078e324da',2,'auction_credit',152,'0000-00-00 00:00:00'),('36380a89-17c4-4d77-afea-b98fde8208fc',1,'auction_debit',152,'0000-00-00 00:00:00'),('a1a9ab08-50c7-4cb3-adb8-98a2808bc40d',2,'auction_credit',152,'0000-00-00 00:00:00'),('a2efcc78-411e-4d4a-b5c1-17af79b4adc0',1,'auction_debit',152,'0000-00-00 00:00:00'),('5441d9c2-aec0-4fa5-917b-dc643ad9ca06',2,'auction_credit',152,'0000-00-00 00:00:00'),('8822a351-3c7a-4fdb-816a-0fc5054491cb',1,'auction_debit',152,'0000-00-00 00:00:00'),('4028838b-7e5a-4432-90b9-c3b5baaa05fc',2,'auction_credit',152,'0000-00-00 00:00:00'),('c46badc8-8b9d-4ff0-a7ff-25e8a98f0b68',1,'auction_debit',152,'0000-00-00 00:00:00'),('3b0314c3-a5c1-4dec-bd0d-1f8073a4eb52',2,'auction_credit',152,'0000-00-00 00:00:00'),('1c960453-583b-4239-84cd-22a5ac91f437',1,'auction_debit',152,'0000-00-00 00:00:00'),('e4012be8-3f2e-4784-bc14-643a0ef4ca69',2,'auction_credit',152,'0000-00-00 00:00:00'),('4b918303-2d56-48e4-8b55-81d60b6716b5',1,'auction_debit',152,'0000-00-00 00:00:00'),('9d6b5a4e-2b51-4a4f-8b73-43cbb5768c8a',2,'auction_credit',152,'0000-00-00 00:00:00'),('82ca7d30-ac08-4351-af3f-91a8e0737eee',1,'auction_debit',152,'0000-00-00 00:00:00'),('96502c1a-7e35-4cb6-8eb2-5ecee91c25b6',2,'auction_credit',1,'0000-00-00 00:00:00'),('5b207d46-0a87-47a3-b530-84cc3ffcd02e',1,'auction_debit',1,'0000-00-00 00:00:00'),('36d22185-4369-4f46-8310-61fc7f0a47c9',1,'auction_credit',2,'0000-00-00 00:00:00'),('4998c924-116e-4372-a6af-d7c61dcebbab',2,'auction_debit',2,'0000-00-00 00:00:00'),('845791d9-b822-4a09-a529-a1c8d4359fdf',2,'roll_purchase',5,'0000-00-00 00:00:00'),('265c4ba2-055d-4988-a15e-32c47220184b',2,'roll_purchase',5,'0000-00-00 00:00:00'),('760b89f7-f4ed-4e55-bf61-342ceaf5da9b',2,'roll_purchase',5,'0000-00-00 00:00:00'),('7d3a82b7-206c-41e8-9c24-ce17dd5c4455',2,'roll_purchase',5,'0000-00-00 00:00:00'),('f289411c-95c2-4ec4-a72d-f17e4f9286d2',2,'roll_purchase',5,'0000-00-00 00:00:00'),('caa2679c-7345-49c6-aebe-7cecf683b206',2,'roll_purchase',5,'0000-00-00 00:00:00'),('eba1142d-2e97-43b7-8e1f-f4afaf9749c3',2,'roll_purchase',5,'0000-00-00 00:00:00'),('7aaf88f1-9f7d-40b4-80c9-63e4e8935fcf',2,'roll_purchase',5,'0000-00-00 00:00:00'),('f4ce6a1b-f0ea-4aae-a3cf-4d0597887175',2,'roll_purchase',5,'0000-00-00 00:00:00'),('e5bd1d2c-f1cc-46f3-9f3e-70a0fa447f09',2,'roll_purchase',5,'0000-00-00 00:00:00'),('335842fb-dccf-4a23-a205-222e98aaa1d1',2,'roll_purchase',5,'0000-00-00 00:00:00'),('4ab0b0a5-88a9-404b-8017-7f198e5061b3',2,'roll_purchase',5,'0000-00-00 00:00:00'),('c07db538-cb8c-423a-a899-fb8f876cadc4',2,'roll_purchase',5,'0000-00-00 00:00:00'),('0cb16964-f91c-4e14-99c0-380db484a2e0',2,'roll_purchase',5,'0000-00-00 00:00:00'),('d33940c2-5fce-4253-9b45-571943ec57c7',2,'roll_purchase',5,'0000-00-00 00:00:00'),('6ab3fcab-ddb7-45f9-8863-9c2d3f11d2d3',2,'roll_purchase',5,'0000-00-00 00:00:00'),('03095547-777d-47ba-b94f-b54f9b704eab',2,'roll_purchase',5,'0000-00-00 00:00:00'),('7f7f3a0a-1092-47c6-8c23-1699c82aff43',2,'roll_purchase',5,'0000-00-00 00:00:00'),('716da7f5-e898-43e7-8245-5e8bb8eca178',2,'roll_purchase',5,'0000-00-00 00:00:00'),('c8b66e63-0aba-4697-97df-c038b390fe45',2,'roll_purchase',5,'0000-00-00 00:00:00'),('7ac9ad64-40ef-44c4-b5f3-5d48ab71869c',2,'roll_purchase',5,'0000-00-00 00:00:00'),('0acaf896-2f65-4e6b-a2fa-b70b9d6088e8',2,'roll_purchase',5,'0000-00-00 00:00:00'),('71b2fcc4-7a25-4beb-928a-85006a9eae11',2,'roll_purchase',5,'0000-00-00 00:00:00'),('952fcddb-518b-4196-bb08-3d914b9c6048',2,'roll_purchase',5,'0000-00-00 00:00:00'),('4bd5ce5a-b020-4d9a-a8fc-16b97eb2f24e',2,'roll_purchase',5,'0000-00-00 00:00:00'),('d36489e0-efcd-4856-9128-cf8708e529c3',2,'roll_purchase',5,'0000-00-00 00:00:00'),('7cc50705-bf39-4521-a9e8-801b45a470bb',2,'roll_purchase',5,'0000-00-00 00:00:00'),('4388d993-ca1b-44f7-bd7b-c15efaebe0d1',2,'roll_purchase',5,'0000-00-00 00:00:00'),('de792c07-d738-4f98-bbbe-01b67baea56a',2,'roll_purchase',5,'0000-00-00 00:00:00'),('852f3d7f-8ec8-4455-9a8b-0db929203615',2,'roll_purchase',5,'0000-00-00 00:00:00'),('0f8ba6ab-77b1-48f7-9655-e26e2087552e',2,'roll_purchase',5,'0000-00-00 00:00:00'),('bd603cc3-a659-442d-ba72-15125c50a9bd',2,'roll_purchase',5,'0000-00-00 00:00:00'),('cac87329-d565-4c94-9e7e-5293460f4307',2,'roll_purchase',5,'0000-00-00 00:00:00'),('50c05ea7-d356-416a-81e5-b2e9589245f2',2,'roll_purchase',5,'0000-00-00 00:00:00'),('6e77aeae-03dd-4c14-886a-83072d78508c',2,'roll_purchase',5,'0000-00-00 00:00:00'),('dc0a5baf-8e46-4e04-b7a9-683c76ea90e9',2,'roll_purchase',5,'0000-00-00 00:00:00'),('42da9b67-5a52-48c2-ab70-1c5846a3806b',2,'roll_purchase',5,'0000-00-00 00:00:00'),('d96adacc-5cde-4ea8-becd-ec0b155e1ff5',2,'roll_purchase',5,'0000-00-00 00:00:00'),('5b4cf72d-2aba-4182-82e4-3be2204375b7',2,'roll_purchase',5,'0000-00-00 00:00:00'),('ed933ceb-bf96-4808-9c5f-53454a9b0dc3',2,'roll_purchase',5,'0000-00-00 00:00:00'),('44e7b647-3011-4035-a6e9-c256fe5e9255',2,'roll_purchase',5,'0000-00-00 00:00:00'),('d86d2e36-428d-43d0-a0b2-72e232cbddda',2,'roll_purchase',5,'0000-00-00 00:00:00'),('54cdfaab-4ebc-4a15-ab37-a0305a59c5ca',2,'roll_purchase',5,'0000-00-00 00:00:00'),('1163807c-97a2-4d43-b6d3-592d63eae579',2,'roll_purchase',5,'0000-00-00 00:00:00'),('c271c955-bd09-4d7c-9c3e-abde5e4110be',2,'roll_purchase',5,'0000-00-00 00:00:00'),('e6c316eb-e96b-40fb-8e6a-f52ef5ae97c0',2,'roll_purchase',5,'0000-00-00 00:00:00'),('8f7b5b15-2eea-4ec3-9c81-444f509f27b2',2,'roll_purchase',5,'0000-00-00 00:00:00'),('85021628-b739-4350-92d8-c4337d0fe265',2,'roll_purchase',5,'0000-00-00 00:00:00'),('4f69240d-2291-4f23-990b-5378867313ac',2,'roll_purchase',5,'0000-00-00 00:00:00'),('983cd025-0a15-4c9c-ad50-b41ab3a2b1b5',2,'roll_purchase',5,'0000-00-00 00:00:00'),('b12d303c-b76d-490d-b784-727cddc21783',2,'roll_purchase',5,'0000-00-00 00:00:00'),('236968d3-1334-46e8-ad3b-658ed65e19b7',2,'roll_purchase',5,'0000-00-00 00:00:00'),('14b4b942-d936-411a-8d65-c016cac8f835',2,'roll_purchase',5,'0000-00-00 00:00:00'),('af7e31d4-5632-4a17-a2dc-c88fe664d7d6',2,'roll_purchase',5,'0000-00-00 00:00:00'),('d6068f83-323d-4063-be17-8f362a0f28a4',2,'roll_purchase',5,'0000-00-00 00:00:00'),('d1002a53-dcee-479a-9988-c9eaa4a7940b',2,'roll_purchase',5,'0000-00-00 00:00:00'),('61980288-9151-4a52-9dc4-352356cafe53',2,'roll_purchase',5,'0000-00-00 00:00:00'),('7b2087c8-5357-470e-99c8-ff2bf609463c',2,'roll_purchase',5,'0000-00-00 00:00:00'),('53feb91a-ed74-4549-b9de-7185cc6137a6',2,'roll_purchase',5,'0000-00-00 00:00:00'),('f79526a5-eb7f-4450-aec8-87134151bdf7',2,'roll_purchase',5,'0000-00-00 00:00:00'),('5e2669f2-f150-4e7a-8508-7d9abcb8b427',2,'roll_purchase',5,'0000-00-00 00:00:00'),('23c8e42a-501c-4a42-bd20-34de2034ac18',1,'top_up',50,NULL),('e9cace8a-cee7-4d7c-b170-853169c4ffa2',1,'roll_purchase',5,NULL),('6b167d9b-52f8-46ce-aa36-f28eeee7933e',2,'top_up',50,NULL),('93fc0f2b-990e-4f5a-a0cf-05072f440d0a',2,'roll_purchase',5,NULL);
/*!40000 ALTER TABLE `Transactions` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-12-02 12:53:38
