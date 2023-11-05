import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('Multi_Strat_ATS.db')
cursor = conn.cursor()

# Create AccountInformation table
cursor.execute('''
CREATE TABLE IF NOT EXISTS AccountInformation (
    AccountID INTEGER PRIMARY KEY AUTOINCREMENT,
    Date DATE,
    EquityValue DOUBLE,
    DailyPnL DOUBLE,
    DailyReturn DOUBLE,
    TimeStamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# Create GlobalSettings table
cursor.execute('''
CREATE TABLE IF NOT EXISTS GlobalSettings (
    SettingID INTEGER PRIMARY KEY AUTOINCREMENT,
    StrategyName TEXT,
    MinWeight DOUBLE,
    MaxWeight DOUBLE,
    TimeStamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# Create CombinedLogs table
cursor.execute('''
CREATE TABLE IF NOT EXISTS CombinedLogs (
    LogID INTEGER PRIMARY KEY AUTOINCREMENT,
    StrategyName TEXT,
    LogMessage TEXT,
    TimeStamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
''')

# Create Strategy-specific tables
# Replace "strategy_name" with the actual strategy names you use
for strategy_name in ["Strategy1", "Strategy2"]:  # Add more strategy names as needed
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS Strategy_{strategy_name} (
        StrategyID INTEGER PRIMARY KEY AUTOINCREMENT,
        Date DATE,
        StrategyEquity DOUBLE,
        DailyPnL DOUBLE,
        DailyReturn DOUBLE,
        OpenPositions TEXT,
        ClosedPositions TEXT,
        StrategyLogs TEXT,
        TimeStamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

# Commit changes and close connection
conn.commit()
conn.close()
