DROP TABLE IF EXISTS ADMIN;
CREATE TABLE ADMIN
(
    user_id          INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username         varchar(255) DEFAULT NULL,
    password         TEXT         DEFAULT NULL,
    email            varchar(255) DEFAULT NULL,
    currency_balance INTEGER      DEFAULT 0,
    session_token    TEXT         DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS PLAYER;
CREATE TABLE PLAYER
(
    user_id          INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    username         varchar(255) DEFAULT NULL,
    password         TEXT         DEFAULT NULL,
    email            varchar(255) DEFAULT NULL,
    currency_balance INTEGER      DEFAULT 20,
    session_token    TEXT         DEFAULT NULL,
    image            MEDIUMBLOB   DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO ADMIN
VALUES (1, 'provando',
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo4LCJ1c2VyX3R5cGUiOiJBRE1JTiIsImV4cGlyYXRpb24iOiIyMDI0LTExLTI5IDIxOjAyOjE0LjMxNzk4NCJ9.PBrDCJpexDvz0zJj9iV8SXzLmKvgHzDHTgUWj3dpI-A',
        'aa@gmail.com', 0,
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VyX3R5cGUiOiJBRE1JTiIsImV4cGlyYXRpb24iOiIyMDI0LTExLTIyIDE2OjAwOjI1LjMyODU4MiJ9.oAs_Qfoc4hqBFfNX5s9ILJo0cz66WCgQJnj6l8yNtOc'),
       (2, 'provando121_', '6258a5e0eb772911d4f92be5b5db0e14511edbe01d1d0ddd1d5a2cb9db9a56ba', 'prova12312@gmail.con',
        0, '0'),
       (3, 'user_5jjkf11y_1732710916302', 'b02b003b2364dce8d60eac19aa5ea537aaebb4c1778c5f0dfe3e1dde8c3173cf',
        'user_5jjkf11y_1732710916302@example.com', 0, '0'),
       (4, 'admin_test_1', '6258a5e0eb772911d4f92be5b5db0e14511edbe01d1d0ddd1d5a2cb9db9a56ba',
        'user_xfmymfkn_1732710950960@example.com', 0,
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo0LCJ1c2VyX3R5cGUiOiJBRE1JTiIsImV4cGlyYXRpb24iOiIyMDI0LTExLTI3IDIyOjA2OjAyLjk2NTQzMCJ9.hjUnW-vAEFRMVtsK8dQbMRNbC73xMLhAuYyQu3YQjoA'),
       (5, 'admin_test_2', '6258a5e0eb772911d4f92be5b5db0e14511edbe01d1d0ddd1d5a2cb9db9a56ba',
        'user_o4btr119_1732710956389@example.com', 0,
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo1LCJ1c2VyX3R5cGUiOiJBRE1JTiIsImV4cGlyYXRpb24iOiIyMDI0LTExLTI3IDIyOjA2OjAzLjAxMzQ1NiJ9.wsCFL3KryM5W145hBskXqgcEUdW7_hJxUnN7ez3H6Vg'),
       (6, 'admin_test_3', '6258a5e0eb772911d4f92be5b5db0e14511edbe01d1d0ddd1d5a2cb9db9a56ba',
        'user_meev1bdm_1732712921141@example.com', 0,
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJ1c2VyX3R5cGUiOiJBRE1JTiIsImV4cGlyYXRpb24iOiIyMDI0LTExLTI3IDIyOjA2OjAzLjA5NDAxMyJ9.AR3R5tJ4i_A81CcL83VHahPBosxGHx2auVvi7pjRYk0'),
       (7, 'admin_test_4', '6258a5e0eb772911d4f92be5b5db0e14511edbe01d1d0ddd1d5a2cb9db9a56ba',
        'user_974jcl3a_1732712948243@example.com', 0, '0');
