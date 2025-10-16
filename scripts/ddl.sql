-- 1) Schema / Database
CREATE DATABASE IF NOT EXISTS expense_app
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE expense_app;

-- 2) Tabela de usuários
CREATE TABLE IF NOT EXISTS users (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  email           VARCHAR(255)     NOT NULL,
  password_hash   VARCHAR(255)     NOT NULL,             -- hash (ex.: bcrypt)
  full_name       VARCHAR(255)     NULL,
  is_active       TINYINT(1)       NOT NULL DEFAULT 1,
  created_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB;

-- 3) Tabela de categorias (escopo por usuário)
CREATE TABLE IF NOT EXISTS categories (
  id              BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
  user_id         BIGINT UNSIGNED  NOT NULL,
  name            VARCHAR(100)     NOT NULL,
  color           CHAR(7)          NULL,                 -- formato sugerido: '#RRGGBB'
  created_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_categories_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,
  CONSTRAINT ck_categories_name_not_blank
    CHECK (CHAR_LENGTH(TRIM(name)) > 0),
  UNIQUE KEY uq_categories_user_name (user_id, name)
) ENGINE=InnoDB;

-- 4) Tabela de despesas
CREATE TABLE IF NOT EXISTS expenses (
  id              BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT,
  user_id         BIGINT UNSIGNED  NOT NULL,
  category_id     BIGINT UNSIGNED  NULL,
  amount          DECIMAL(12,2)    NOT NULL,
  currency        CHAR(3)          NOT NULL DEFAULT 'BRL',   -- ISO 4217 (ex.: BRL, USD)
  description     VARCHAR(500)     NULL,
  date            DATE             NOT NULL,                  -- data do gasto (planejado ou realizado)
  paid_at         DATETIME         NULL,                      -- quando realmente foi pago
  payment_method  ENUM('CASH','CARD','PIX','TRANSFER') NOT NULL DEFAULT 'CARD',
  status          ENUM('PLANNED','PAID','CANCELLED')   NOT NULL DEFAULT 'PLANNED',
  created_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  CONSTRAINT fk_expenses_user
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE RESTRICT,
  CONSTRAINT fk_expenses_category
    FOREIGN KEY (category_id) REFERENCES categories(id)
    ON DELETE SET NULL
    ON UPDATE RESTRICT,
  CONSTRAINT ck_expenses_amount_positive
    CHECK (amount >= 0),
  INDEX idx_expenses_user_date (user_id, date),
  INDEX idx_expenses_user_category (user_id, category_id),
  INDEX idx_expenses_user_status (user_id, status)
) ENGINE=InnoDB;

-- 5) (Opcional) View básica para facilitar relatórios rápidos
CREATE OR REPLACE VIEW v_expenses_basic AS
SELECT
  e.id,
  e.user_id,
  e.category_id,
  c.name AS category_name,
  e.amount,
  e.currency,
  e.description,
  e.date,
  e.paid_at,
  e.payment_method,
  e.status,
  e.created_at,
  e.updated_at
FROM expenses e
LEFT JOIN categories c ON c.id = e.category_id;

-- 6) (Opcional) View de totais mensais por usuário e moeda
CREATE OR REPLACE VIEW v_expenses_monthly_totals AS
SELECT
  user_id,
  currency,
  EXTRACT(YEAR  FROM date) AS year,
  EXTRACT(MONTH FROM date) AS month,
  SUM(amount) AS total_amount
FROM expenses
WHERE status <> 'CANCELLED'
GROUP BY user_id, currency, EXTRACT(YEAR FROM date), EXTRACT(MONTH FROM date);
