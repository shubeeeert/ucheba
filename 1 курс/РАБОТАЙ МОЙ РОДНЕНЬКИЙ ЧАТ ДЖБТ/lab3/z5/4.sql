-- ===================================================================
-- ANALYTICAL QUERIES FOR VETERINARY CLINIC
-- ===================================================================

-- -------------------------------------------------------------------
-- Query 1: Top-5 pets with the highest number of visits in the last year
-- Uses: JOIN, LEFT JOIN, COALESCE, GROUP BY, HAVING, ORDER BY, LIMIT
-- -------------------------------------------------------------------
SELECT 
    p.pet_id,
    p.name AS pet_name,
    s.name AS species,
    COALESCE(o.full_name, 'No Owner (Deleted)') AS owner_name,
    COUNT(v.visit_id) AS total_visits
FROM pet p
JOIN visit v ON p.pet_id = v.pet_id
JOIN breed b ON p.breed_id = b.breed_id
JOIN species s ON b.species_id = s.species_id
LEFT JOIN owner o ON p.owner_id = o.owner_id
WHERE v.visit_datetime >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY 
    p.pet_id, 
    p.name, 
    s.name, 
    o.full_name
HAVING COUNT(v.visit_id) > 1
ORDER BY total_visits DESC
LIMIT 5;

-- -------------------------------------------------------------------
-- Query 2: Average days between vaccination appointments per doctor
-- Uses: CTE (WITH), Window Function (LAG, OVER, PARTITION BY), JOIN, GROUP BY, HAVING
-- -------------------------------------------------------------------
WITH DoctorVaccinations AS (
    SELECT 
        v.doctor_id,
        vac.vaccination_id,
        vac.date_administered,
        -- Get the date of the previous vaccination administered by THIS doctor
        LAG(vac.date_administered) OVER (
            PARTITION BY v.doctor_id 
            ORDER BY vac.date_administered
        ) AS prev_vaccine_date
    FROM visit v
    JOIN vaccination vac 
        ON v.pet_id = vac.pet_id 
        -- Assuming vaccination was done on the same day as the visit
        AND v.visit_datetime::DATE = vac.date_administered
)
SELECT 
    d.full_name AS doctor_name,
    COUNT(dv.vaccination_id) AS total_vaccines_done,
    -- Subtracting dates in PostgreSQL returns an integer (number of days)
    ROUND(AVG(dv.date_administered - dv.prev_vaccine_date), 2) AS avg_days_between_vaccines
FROM DoctorVaccinations dv
JOIN doctor d ON dv.doctor_id = d.doctor_id
WHERE dv.prev_vaccine_date IS NOT NULL
GROUP BY 
    d.doctor_id, 
    d.full_name
HAVING COUNT(dv.vaccination_id) > 1;

-- -------------------------------------------------------------------
-- Query 3: 3-month moving average of clinic visits
-- Uses: CTE (WITH), Window Function (AVG, OVER, ORDER BY, ROWS BETWEEN), DATE_TRUNC
-- -------------------------------------------------------------------
WITH MonthlyStats AS (
    -- Aggregate total visits per month
    SELECT 
        DATE_TRUNC('month', visit_datetime)::DATE AS visit_month,
        COUNT(visit_id)::NUMERIC AS total_visits
    FROM visit
    GROUP BY DATE_TRUNC('month', visit_datetime)
)
SELECT 
    visit_month,
    total_visits AS current_month_visits,
    -- Calculate Moving Average for the last 3 months (Current + 2 Preceding)
    ROUND(
        AVG(total_visits) OVER (
            ORDER BY visit_month 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2
    ) AS moving_avg_3_months
FROM MonthlyStats
ORDER BY visit_month;