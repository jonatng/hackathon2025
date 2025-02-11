-- SQL queries for the home page data tables and visualizations
-- Each query retrieves key health metrics for older adults across different locations


-- Table 1: Mammogram Screening Rates
-- Displays the percentage of older women who have received recent mammogram screenings
-- Helps visualize preventive healthcare access across different locations and demographics
SELECT ID,
       STRATIFICATION1,
       LOCATIONDESC,
       DATA_VALUE
FROM HEALTHY_AGING
WHERE QUESTION = 'Percentage of older adult women who have received a mammogram within the past 2 years' 
AND DATA_VALUE IS NOT NULL;

-- Table 2: Mental Health Status
-- Shows the prevalence of frequent mental distress among older adults
-- Important indicator for mental health services needs and well-being
SELECT ID,
       STRATIFICATION1,
       LOCATIONDESC,
       DATA_VALUE
FROM HEALTHY_AGING
WHERE QUESTION = 'Percentage of older adults who are experiencing frequent mental distress' 
AND DATA_VALUE IS NOT NULL;

-- Table 3: Disability Statistics
-- Tracks disability rates including physical, sensory, mental, and emotional limitations
-- Critical for understanding accessibility needs and healthcare requirements
SELECT ID,
       STRATIFICATION1,
       LOCATIONDESC,
       DATA_VALUE
FROM HEALTHY_AGING
WHERE QUESTION = 'Percentage of older adults who report having a disability (includes limitations related to sensory or mobility impairments or a physical, mental, or emotional condition)' 
AND DATA_VALUE IS NOT NULL;

-- Table 4: Dental Health Metrics
-- Measures tooth retention as an indicator of oral health
-- Reflects access to dental care and overall oral health maintenance
SELECT ID,
       STRATIFICATION1,
       LOCATIONDESC,
       DATA_VALUE
FROM HEALTHY_AGING
WHERE QUESTION = 'Percentage of older adults who report having lost 5 or fewer teeth due to decay or gum disease' 
AND DATA_VALUE IS NOT NULL;