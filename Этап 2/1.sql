--Создание слоя для сырых данных
CREATE SCHEMA stg;

--Создание слоя для витрин 
CREATE SCHEMA ddl;

--создание таблицы для сырых данных в слое stg
CREATE TABLE stg.weather_data (
    city VARCHAR(50),
    date DATE,
    hour INT,
    temperature_c INT,
    pressure_mm INT,
    is_rainy INT
);

-- перенос данных с лой stg
COPY stg.weather_data 
FROM 'C:\Users\Gera\Test_work\Этап 1\weather_data.csv' DELIMITER ',' CSV HEADER;

--создание таблицы для 1 витрины, пункт 2.1.1
CREATE TABLE ddl_1 (
    city VARCHAR(50),
    date DATE,
    hour_start_rain INT
);

--создание таблицы для 2 витрины, пункт 2.1.2
CREATE TABLE ddl_2 (
    city VARCHAR(50),
    date DATE,
    hour INT,
    temperature_c INT,
    temp_rolling_avg FLOAT,
    pressure_mm INT,
    pressure_rolling_avg FLOAT
);


-- перенос данных из stg в витрину 1
WITH rainy_hours AS (SELECT city, 
                            date, 
                            MIN(hour) AS hour_start_rain
                     FROM your_table_name
                     WHERE is_rainy = 1
                     GROUP BY city, date)
INSERT INTO ddl_1 (city, date, hour_start_rain)
SELECT a.city, 
       a.date, 
       a.hour_start_rain
FROM rainy_hours a;

--Перенос данных из stg в витрину 2
WITH temp_avg AS (SELECT city, 
                         date, 
                         hour, 
                         temperature_c, 
                         AVG(temperature_c) OVER(PARTITION BY city, date ORDER BY hour ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS temp_rolling_avg
                  FROM your_table_name
),
     pressure_avg AS (SELECT city, 
                             date, 
                             hour, 
                             pressure_mm, 
                             AVG(pressure_mm) OVER(PARTITION BY city, date ORDER BY hour ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS pressure_rolling_avg
                      FROM your_table_name
)
INSERT INTO ddl_2 (city, date, hour, temperature_c, temp_rolling_avg, pressure_mm, pressure_rolling_avg)
SELECT t.city, 
       t.date, 
       t.hour, 
       t.temperature_c, 
       t.temp_rolling_avg,
       p.pressure_mm, 
       p.pressure_rolling_avg
FROM temp_avg t
JOIN pressure_avg p
ON t.city = p.city AND t.date = p.date AND t.hour = p.hour;


