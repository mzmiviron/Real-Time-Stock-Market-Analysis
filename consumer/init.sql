-- Initialize the stock_data database

-- Create table for stock prices
CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    volume BIGINT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on symbol and timestamp for better query performance
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_timestamp ON stock_prices (symbol, timestamp);