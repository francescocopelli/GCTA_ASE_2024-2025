DROP TABLE IF EXISTS `Auctions`;
CREATE TABLE `Auctions`
(
    `auction_id`  TEXT         DEFAULT NULL,
    `gacha_id`    INTEGER      DEFAULT NULL,
    `seller_id`   INTEGER      DEFAULT NULL,
    `base_price`  INTEGER      DEFAULT NULL,
    `highest_bid` INTEGER      DEFAULT NULL,
    `buyer_id`    varchar(255) DEFAULT NULL,
    `status`      varchar(255) DEFAULT NULL,
    `end_time`    TIMESTAMP    DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `Auctions`
VALUES
        ('ba8c840d-1e83-416a-ad2a-45305ba20ca0', 399, 1, 100, 0, NULL, 'active',
        '2024-11-29 22:24:00'),
       ('4a0cddb3-9cd0-40a7-8dce-2a2d9341e9d9', 100, 1, 100, 0, NULL, 'active',
        '2024-11-29 22:24:00');

DROP TABLE IF EXISTS `Bids`;
CREATE TABLE `Bids`
(
    `bid_id`     TEXT NOT NULL,
    `auction_id` TEXT NOT NULL,
    `user_id`    INTEGER      DEFAULT NULL,
    `bid_amount` INTEGER      DEFAULT NULL,
    `bid_time`   TIMESTAMP DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;