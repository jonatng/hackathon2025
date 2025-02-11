-- SQL queries for the Mental Distress page data tables and visualizations
-- Each query retrieves key health metrics for older adults across different locations

--table one:
SELECT 
    STRATIFICATION1 AS CATEGORY, 
    AVG(DATA_VALUE) AS AVERAGE_DATA_VALUE
FROM HEALTHY_AGING
WHERE QUESTION = 'Percentage of older adults who are experiencing frequent mental distress' 
AND DATA_VALUE IS NOT NULL
AND STRATIFICATION1 IS NOT NULL
GROUP BY STRATIFICATION1;


--table 2:
SELECT 
    LOCATIONABBR AS CATEGORY, 
    AVG(DATA_VALUE) AS AVERAGE_DATA_VALUE
FROM HEALTHY_AGING
WHERE QUESTION = 'Percentage of older adults who are experiencing frequent mental distress' 
AND DATA_VALUE IS NOT NULL
AND LOCATIONABBR IS NOT NULL
GROUP BY LOCATIONABBR;

--table 3:
SELECT 
    STRATIFICATION2 AS CATEGORY, 
    AVG(DATA_VALUE) AS AVERAGE_DATA_VALUE
FROM HEALTHY_AGING
WHERE QUESTION = 'Percentage of older adults who are experiencing frequent mental distress' 
AND DATA_VALUE IS NOT NULL
AND STRATIFICATION2 IS NOT NULL
AND STRATIFICATION2 IN ('Male', 'Female')  
GROUP BY STRATIFICATION2;

--table 4:
SELECT 
    STRATIFICATION2 AS CATEGORY, 
    AVG(DATA_VALUE) AS AVERAGE_DATA_VALUE
FROM HEALTHY_AGING
WHERE QUESTION = 'Percentage of older adults who are experiencing frequent mental distress' 
AND DATA_VALUE IS NOT NULL
AND STRATIFICATION2 IS NOT NULL
AND STRATIFICATION2 NOT IN ('Male', 'Female')
GROUP BY STRATIFICATION2;

