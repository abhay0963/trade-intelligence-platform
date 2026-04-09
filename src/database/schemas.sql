-- DIMENSION TABLE 1: Countries
-- Stores info about every country in our data
CREATE TABLE IF NOT EXISTS dim_country (
    country_id      SERIAL PRIMARY KEY,
    country_code    VARCHAR(3) UNIQUE NOT NULL,  -- e.g. 'IND', 'USA', 'CHN'
    country_name    VARCHAR(100) NOT NULL,
    region          VARCHAR(100),                -- e.g. 'South Asia'
    income_group    VARCHAR(50),                 -- e.g. 'Upper middle income'
    created_at      TIMESTAMP DEFAULT NOW()
);

-- DIMENSION TABLE 2: Commodities
-- Stores info about what is being traded
CREATE TABLE IF NOT EXISTS dim_commodity (
    commodity_id    SERIAL PRIMARY KEY,
    hs_code         VARCHAR(10) UNIQUE NOT NULL, -- Harmonized System code e.g. '0901' = coffee
    commodity_name  VARCHAR(200) NOT NULL,
    category        VARCHAR(100),               -- e.g. 'Agricultural', 'Electronics'
    unit_of_measure VARCHAR(50),                -- e.g. 'metric tons', 'USD'
    created_at      TIMESTAMP DEFAULT NOW()
);

-- DIMENSION TABLE 3: Time
-- Breaks dates into parts for easy filtering
CREATE TABLE IF NOT EXISTS dim_time (
    time_id         SERIAL PRIMARY KEY,
    full_date       DATE UNIQUE NOT NULL,
    year            INTEGER NOT NULL,
    quarter         INTEGER NOT NULL,           -- 1, 2, 3, or 4
    month           INTEGER NOT NULL,           -- 1 to 12
    month_name      VARCHAR(20) NOT NULL,       -- e.g. 'January'
    week_number     INTEGER,
    is_year_end     BOOLEAN DEFAULT FALSE
);

-- DIMENSION TABLE 4: Economic Indicators
-- Stores types of economic measurements
CREATE TABLE IF NOT EXISTS dim_indicator (
    indicator_id    SERIAL PRIMARY KEY,
    indicator_code  VARCHAR(50) UNIQUE NOT NULL, -- e.g. 'NY.GDP.MKTP.CD'
    indicator_name  VARCHAR(200) NOT NULL,        -- e.g. 'GDP (current US dollar)'
    source          VARCHAR(100),                 -- e.g. 'World Bank'
    unit            VARCHAR(50)                   -- e.g. 'USD', 'Percentage'
);

-- FACT TABLE: Trade Flows
-- The center of our star - actual trade data
-- Each row = one trade event between two countries
CREATE TABLE IF NOT EXISTS fact_trade_flows (
    trade_id        SERIAL PRIMARY KEY,
    time_id         INTEGER REFERENCES dim_time(time_id),
    exporter_id     INTEGER REFERENCES dim_country(country_id),
    importer_id     INTEGER REFERENCES dim_country(country_id),
    commodity_id    INTEGER REFERENCES dim_commodity(commodity_id),
    trade_value_usd NUMERIC(20, 2),             -- value in US dollars
    quantity        NUMERIC(20, 4),             -- physical quantity
    unit_price_usd  NUMERIC(15, 4),             -- price per unit
    data_source     VARCHAR(50),                -- 'UN_COMTRADE', 'WORLD_BANK'
    created_at      TIMESTAMP DEFAULT NOW()
);

-- FACT TABLE 2: Economic Indicators Data
-- Stores GDP, inflation, and other indicator values
CREATE TABLE IF NOT EXISTS fact_economic_indicators (
    indicator_data_id SERIAL PRIMARY KEY,
    country_id        INTEGER REFERENCES dim_country(country_id),
    indicator_id      INTEGER REFERENCES dim_indicator(indicator_id),
    time_id           INTEGER REFERENCES dim_time(time_id),
    value             NUMERIC(20, 4),
    created_at        TIMESTAMP DEFAULT NOW()
);

-- INDEXES for fast querying
-- These make SELECT queries much faster
CREATE INDEX IF NOT EXISTS idx_trade_time     ON fact_trade_flows(time_id);
CREATE INDEX IF NOT EXISTS idx_trade_exporter ON fact_trade_flows(exporter_id);
CREATE INDEX IF NOT EXISTS idx_trade_importer ON fact_trade_flows(importer_id);
CREATE INDEX IF NOT EXISTS idx_trade_commodity ON fact_trade_flows(commodity_id);
CREATE INDEX IF NOT EXISTS idx_econ_country   ON fact_economic_indicators(country_id);
CREATE INDEX IF NOT EXISTS idx_econ_indicator ON fact_economic_indicators(indicator_id);

