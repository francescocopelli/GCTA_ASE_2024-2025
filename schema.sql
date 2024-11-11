-- Creazione della tabella PLAYERCREATE TABLE PLAYER (
    user_id INTEGER PRIMARY KEY,                    -- ID unico per ogni utente    username VARCHAR(255) NOT NULL UNIQUE,          -- Nome utente univoco
    password VARCHAR(255) NOT NULL,                 -- Password hashata per l'autenticazione    email VARCHAR(255) NOT NULL UNIQUE,             -- Indirizzo email univoco
    currency_balance INTEGER DEFAULT 0              -- Saldo della valuta di gioco);
-- Creazione della tabella ADMIN
CREATE TABLE ADMIN (    user_id INTEGER PRIMARY KEY,                    -- ID unico per ogni amministratore
    username VARCHAR(255) NOT NULL UNIQUE,          -- Nome utente univoco    password VARCHAR(255) NOT NULL,                 -- Password hashata per l'autenticazione
    email VARCHAR(255) NOT NULL UNIQUE,             -- Indirizzo email univoco    currency_balance INTEGER DEFAULT 0              -- Saldo della valuta di gioco
);
