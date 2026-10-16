DROP DATABASE IF EXISTS `2026_MF_PIFA`;

CREATE DATABASE `2026_MF_PIFA`;
USE `2026_MF_PIFA`;

CREATE TABLE fund_categories (
    fund_category_id INT PRIMARY KEY AUTO_INCREMENT
    fund_category VARCHAR(100)
);

CREATE TABLE universe (
    fund_id INT PRIMARY KEY AUTO_INCREMENT,
    fund_name VARCHAR(255) NOT NULL,
    fund_category_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_funds_fund_type
        FOREIGN KEY (fund_type_id)
        REFERENCES fund_categories(fund_type_id)
        ON UPDATE CASCADE,

    CONSTRAINT uq_fund_name
        UNIQUE (fund_name)
);

CREATE TABLE fund_focus (
    fund_id INT,
    investment_focus VARCHAR(255) NOT NULL,

    PRIMARY KEY (fund_id, investment_focus),

    CONSTRAINT fk_fund_id
        FOREIGN KEY (fund_id)
        REFERENCES universe(fund_id)
)

CREATE TABLE fund_monthly_reports (
    fund_id INT NOT NULL,
    report_date DATE NOT NULL,

    assets DECIMAL(20, 2),
    liabilities DECIMAL(20, 2),

    equity_investments DECIMAL(20, 2),
    number_of_accounts INT,

    monthly_sales DECIMAL(20, 2),
    monthly_redemption DECIMAL(20, 2),

    ytd_sales DECIMAL(20, 2),
    ytd_redemption DECIMAL(20, 2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (fund_id, report_date),

    CONSTRAINT fk_monthly_reports_fund
        FOREIGN KEY (fund_id)
        REFERENCES funds(fund_id)
);
