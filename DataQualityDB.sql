CREATE DATABASE DataQualityDB;
GO

USE DataQualityDB;
GO

CREATE TABLE Raw_Sales (
    Transaction_ID INT,
    Product_Name VARCHAR(100),
    Quantity INT,
    Unit_Price DECIMAL(18, 2),
    Customer_Email VARCHAR(150),
    Transaction_Date DATETIME
);
GO

CREATE TABLE Clean_Sales (
    Clean_ID INT IDENTITY(1,1) PRIMARY KEY,
    Transaction_ID INT,
    Product_Name VARCHAR(100),
    Quantity INT,
    Unit_Price DECIMAL(18, 2),
    Customer_Email VARCHAR(150),
    Transaction_Date DATETIME,
    Processed_At DATETIME DEFAULT GETDATE()
);
GO

CREATE TABLE Quarantine_Sales (
    Quarantine_ID INT IDENTITY(1,1) PRIMARY KEY,
    Transaction_ID INT,
    Product_Name VARCHAR(100),
    Quantity INT,
    Unit_Price DECIMAL(18, 2),
    Customer_Email VARCHAR(150),
    Transaction_Date DATETIME,
    Rejection_Reason VARCHAR(255),
    Processed_At DATETIME DEFAULT GETDATE()
);
GO

-- View the total number of records ingested vs processed
SELECT 
    (SELECT COUNT(*) FROM Raw_Sales) AS Raw_Ingested,
    (SELECT COUNT(*) FROM Clean_Sales) AS Gold_Clean,
    (SELECT COUNT(*) FROM Quarantine_Sales) AS DeadLetter_Quarantine;

-- Calculate the exact percentage of clean data vs corrupted data
SELECT 
    Total_Clean,
    Total_Quarantine,
    Total_Processed,
    CAST((Total_Clean * 100.0 / NULLIF(Total_Processed, 0)) AS DECIMAL(5,2)) AS Health_Score_Percentage
FROM (
    SELECT 
        (SELECT COUNT(*) FROM Clean_Sales) AS Total_Clean,
        (SELECT COUNT(*) FROM Quarantine_Sales) AS Total_Quarantine,
        (SELECT COUNT(*) FROM Clean_Sales) + (SELECT COUNT(*) FROM Quarantine_Sales) AS Total_Processed
) AS Metrics;

-- Identify which data quality rules are failing the most and their percentages
SELECT 
    Rejection_Reason,
    COUNT(*) AS Anomaly_Count,
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Quarantine_Sales) AS DECIMAL(5,2)) AS Percentage_Of_Errors
FROM Quarantine_Sales
GROUP BY Rejection_Reason
ORDER BY Anomaly_Count DESC;

-- Calculate the estimated revenue lost or blocked due to quarantined records
-- (Using ABS to avoid negative revenue calculations from negative prices/qty)
SELECT 
    'Gold Data (Validated Revenue)' AS Data_Tier, 
    CAST(SUM(Quantity * Unit_Price) AS DECIMAL(18,2)) AS Total_Financial_Value 
FROM Clean_Sales
UNION ALL
SELECT 
    'Quarantine Data (Blocked Revenue)' AS Data_Tier, 
    CAST(SUM(ABS(Quantity * Unit_Price)) AS DECIMAL(18,2)) AS Total_Financial_Value 
FROM Quarantine_Sales;

-- Generate sales metrics strictly from the 'Single Source of Truth' (Clean table)
SELECT TOP 5
    Product_Name,
    SUM(Quantity) AS Total_Units_Sold,
    CAST(SUM(Quantity * Unit_Price) AS DECIMAL(18,2)) AS Gross_Revenue
FROM Clean_Sales
GROUP BY Product_Name
ORDER BY Gross_Revenue DESC;

-- Extract a sample of invalid customer emails for the marketing team to fix
SELECT TOP 10
    Transaction_ID,
    Customer_Email,
    Processed_At
FROM Quarantine_Sales
WHERE Rejection_Reason = 'Malformed Email'
ORDER BY Processed_At DESC;

-- Extract records where mathematical boundaries were violated
SELECT TOP 10
    Transaction_ID,
    Product_Name,
    Quantity,
    Unit_Price,
    Rejection_Reason
FROM Quarantine_Sales
WHERE Rejection_Reason IN ('Invalid Quantity', 'Invalid Price')
ORDER BY Unit_Price ASC, Quantity ASC;

-- Measure the average time gap between the actual transaction and when our ETL processed it
SELECT 
    AVG(DATEDIFF(HOUR, Transaction_Date, Processed_At)) AS Avg_Pipeline_Latency_Hours,
    MIN(DATEDIFF(HOUR, Transaction_Date, Processed_At)) AS Min_Latency_Hours,
    MAX(DATEDIFF(HOUR, Transaction_Date, Processed_At)) AS Max_Latency_Hours
FROM Clean_Sales;

-- Calculate how much money is locked in quarantine strictly due to typing errors 
-- (e.g., Malformed Emails can be fixed and recovered, unlike negative quantities)
SELECT 
    Rejection_Reason,
    COUNT(*) AS Blocked_Transactions,
    CAST(SUM(ABS(Quantity * Unit_Price)) AS DECIMAL(18,2)) AS Recoverable_Revenue
FROM Quarantine_Sales
WHERE Rejection_Reason = 'Malformed Email'
GROUP BY Rejection_Reason;

-- Discover if a specific product catalog is generating the most corrupted data
SELECT TOP 5
    ISNULL(Product_Name, 'NULL_PRODUCT') AS Product,
    COUNT(*) AS Total_Errors,
    Rejection_Reason
FROM Quarantine_Sales
GROUP BY Product_Name, Rejection_Reason
ORDER BY Total_Errors DESC;

-- Audit the volume of data processed by the pipeline per day
SELECT 
    CAST(Processed_At AS DATE) AS Processing_Date,
    COUNT(*) AS Total_Records_Processed
FROM Clean_Sales
GROUP BY CAST(Processed_At AS DATE)
ORDER BY Processing_Date DESC;

-- Business Intelligence on valid users to help the Marketing department
SELECT TOP 5
    RIGHT(Customer_Email, LEN(Customer_Email) - CHARINDEX('@', Customer_Email)) AS Email_Domain,
    COUNT(*) AS Customer_Count,
    CAST(SUM(Quantity * Unit_Price) AS DECIMAL(18,2)) AS Total_Revenue_By_Domain
FROM Clean_Sales
GROUP BY RIGHT(Customer_Email, LEN(Customer_Email) - CHARINDEX('@', Customer_Email))
ORDER BY Customer_Count DESC;

-- Determine if data corruption happens more frequently on specific days of the week
SELECT 
    DATEPART(WEEKDAY, Transaction_Date) AS Day_Of_Week,
    COUNT(*) AS Corrupted_Records_Count
FROM Quarantine_Sales
GROUP BY DATEPART(WEEKDAY, Transaction_Date)
ORDER BY Corrupted_Records_Count DESC;

-- Find the top 10 most expensive transactions that were rejected to prioritize manual review
SELECT TOP 10
    Transaction_ID,
    Product_Name,
    ABS(Quantity * Unit_Price) AS Blocked_Value,
    Rejection_Reason
FROM Quarantine_Sales
ORDER BY Blocked_Value DESC;

-- Isolate records where the product name is completely missing to alert the catalog team
SELECT 
    Transaction_ID,
    Transaction_Date,
    Quantity,
    Unit_Price,
    Customer_Email
FROM Quarantine_Sales
WHERE Rejection_Reason = 'Missing/Null Values'
ORDER BY Transaction_Date DESC;