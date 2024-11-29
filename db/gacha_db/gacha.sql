DROP TABLE IF EXISTS `GachaItems`;
CREATE TABLE `GachaItems` (
  `gacha_id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `name` varchar(255) DEFAULT NULL,
  `rarity` varchar(255) CHECK ( rarity IN ('common', 'epic', 'rare') ) DEFAULT 'common',
  `description` varchar(255) DEFAULT NULL,
  `status` varchar(255) CHECK ( status IN ('available', 'out_of_stock') ) DEFAULT 'available',
  `image` MEDIUMBLOB DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `UserGachaInventory`;
CREATE TABLE `UserGachaInventory` (
  `inventory_id` INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `user_id` INTEGER DEFAULT NULL,
  `gacha_id` INTEGER DEFAULT NULL,
  `acquired_date` DATETIME DEFAULT NOW(),
  `locked` varchar(255) CHECK ( locked IN ('locked', 'unlocked') ) DEFAULT 'unlocked'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;