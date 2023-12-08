
def get_all_drivers():
    return "select * from drivers;"

def get_ladder_results():
    return """
WITH FinalResults AS (
    SELECT 
        r.race_id,
        MAX(r.run_id) AS last_pair_id,
        MAX(r.pair_id) AS last_run_id
    FROM 
        run r
    JOIN 
        races ra ON r.race_id = ra.id
    WHERE 
        ra.mode = 3
    GROUP BY 
        r.race_id
),
Thirdplace AS (
    SELECT 
        r.race_id,
        d.first_name || ' ' || d.last_name AS winner,
        '3' AS position,
        rd.title || ' - ' || ra.title AS race_name
    FROM 
        run r
    JOIN 
        FinalResults fr ON r.race_id = fr.race_id AND r.run_id = fr.last_run_id AND r.pair_id = fr.last_pair_id
    JOIN 
        drivers d ON r.driver_id = d.id
    JOIN 
        races ra ON r.race_id = ra.id
    JOIN 
        racedays rd ON ra.raceday_id = rd.id
    WHERE 
        r.status = 1
),
FourthPlace AS (
    SELECT 
        r.race_id,
        d.first_name || ' ' || d.last_name AS runner_up,
        '4' AS position,
        rd.title || ' - ' || ra.title AS race_name
    FROM 
        run r
    JOIN 
        FinalResults fr ON r.race_id = fr.race_id AND r.run_id = fr.last_run_id AND r.pair_id = fr.last_pair_id
    JOIN 
        drivers d ON r.driver_id = d.id
    JOIN 
        races ra ON r.race_id = ra.id
    JOIN 
        racedays rd ON ra.raceday_id = rd.id
    WHERE 
        r.status = 2
),
FirstAndSecond AS (
    SELECT 
        r.race_id,
        d.first_name || ' ' || d.last_name AS driver,
        CASE
            WHEN r.status = 1 THEN '1'
            ELSE '2'
        END AS position,
        rd.title || ' - ' || ra.title AS race_name
    FROM 
        run r
    JOIN 
        FinalResults fr ON r.race_id = fr.race_id AND r.run_id = fr.last_run_id AND r.pair_id = fr.last_pair_id - 1
    JOIN 
        drivers d ON r.driver_id = d.id
    JOIN 
        races ra ON r.race_id = ra.id
    JOIN 
        racedays rd ON ra.raceday_id = rd.id
    WHERE 
        ra.mode = 3
)


SELECT * FROM Thirdplace
UNION ALL
SELECT * FROM FourthPlace
UNION ALL
SELECT * FROM FirstAndSecond
ORDER BY race_id, position;

    """

def get_parallel_driver_results_sql(driver):
    return """SELECT 
    d1.name,
    d2.name,
    CASE 
        WHEN r1.status = 1 THEN 'Winner'
        WHEN r1.status = 2 THEN 'Loser'
        ELSE 'Unknown'
    END as result_driver1,
    CASE 
        WHEN r2.status = 1 THEN 'Winner'
        WHEN r2.status = 2 THEN 'Loser'
        ELSE 'Unknown'
    END as result_driver2,
	rd.title AS race_day,
    ra.title AS race_title,
    rd.date AS race_date,
	r1.finishtime AS d1_finishtime,
	r2.finishtime AS d2_finishtime,
	r1.vehicle AS d1_snowmobile,
	r2.vehicle AS d2_snowmobile
FROM 
    run r1
JOIN 
    drivers d1 ON r1.driver_id = d1.id
LEFT JOIN 
    run r2 ON r1.race_id = r2.race_id AND r1.run_id = r2.run_id AND r1.pair_id = r2.pair_id AND r1.driver_id != r2.driver_id
LEFT JOIN 
    drivers d2 ON r2.driver_id = d2.id
JOIN 
    races ra ON r1.race_id = ra.id
JOIN 
    racedays rd ON ra.raceday_id = rd.id
WHERE 
    (d1.name = '{0}')
    AND ((ra.mode IN (2, 3) AND r2.id IS NOT NULL))
ORDER BY 
    rd.date, ra.title, r1.run_id, r1.pair_id;""".format(driver)



def get_snowmobiles_sql(driver):
    return """
        SELECT DISTINCT d.name, r.vehicle, rd.date, rd.title
        FROM drivers d
        JOIN run r ON d.id = r.driver_id
        JOIN races ra ON r.race_id = ra.id
        JOIN racedays rd ON ra.raceday_id = rd.id
        WHERE d.name = '{0}' AND r.vehicle <> '';
    """.format(driver)

def get_ladder_placement_sql(driver):
    return """
WITH DriverLastRun AS (
    SELECT 
        driver_id, 
        race_id, 
        MAX(run_id) AS last_run_id
    FROM 
        "run"
    GROUP BY 
        driver_id, race_id
),
LastRunIdPerRace AS (
    SELECT
        race_id,
        MAX(run_id) AS final_run_id
    FROM
        "run"
    GROUP BY
        race_id
),
DriverPositionInLastRun AS (
    SELECT 
        r.driver_id,
        r.race_id,
        r.vehicle,
        r.finishtime,
        r.pair_id,
        lr.final_run_id,
        CASE 
            WHEN lr.final_run_id = r.run_id THEN
                CASE 
                    WHEN r.pair_id = 1 THEN
                        RANK() OVER (PARTITION BY r.race_id, r.run_id ORDER BY r.finishtime ASC)
                    WHEN r.pair_id = 2 THEN
                        RANK() OVER (PARTITION BY r.race_id, r.run_id ORDER BY r.finishtime ASC) + 2
                END
            ELSE
                DENSE_RANK() OVER (PARTITION BY r.race_id ORDER BY r.run_id DESC, r.finishtime ASC) + 4
        END as raw_position
    FROM 
        "run" r
    INNER JOIN 
        DriverLastRun dlr ON r.driver_id = dlr.driver_id AND r.race_id = dlr.race_id AND r.run_id = dlr.last_run_id
    INNER JOIN
        LastRunIdPerRace lr ON r.race_id = lr.race_id
    WHERE 
        r.finishtime IS NOT NULL
),
FilteredRaces AS (
    SELECT rs.id AS race_id
    FROM "races" rs
    JOIN "racedays" rsd ON rs.raceday_id = rsd.id
    WHERE rs.mode = 3
),
RankedPositions AS (
    SELECT
        *,
        DENSE_RANK() OVER (PARTITION BY race_id ORDER BY raw_position ASC) as final_position
    FROM
        DriverPositionInLastRun
)
SELECT 
    d."name" AS "driver_name", 
    rsd.title AS "raceday_title", 
    rs.title AS "race_title", 
    rp.final_position,
    rsd.date,
    rs.mode,
    rp.vehicle,
    (SELECT COUNT(DISTINCT driver_id) FROM "run" WHERE race_id = fr.race_id) AS total_drivers,
    rp.finishtime
FROM 
    FilteredRaces fr
JOIN 
    "races" rs ON fr.race_id = rs.id
JOIN 
    "racedays" rsd ON rs.raceday_id = rsd.id
LEFT JOIN 
    DriverLastRun dlr ON fr.race_id = dlr.race_id
LEFT JOIN 
    "drivers" d ON dlr.driver_id = d.id
LEFT JOIN 
    RankedPositions rp ON d.id = rp.driver_id AND dlr.race_id = rp.race_id
WHERE 
    d."name" = '{0}'
ORDER BY  
    rsd.date DESC;
        """.format(driver)

def get_single_placement_sql(driver):
    return """
SELECT 
    sub.race_date,
    sub.full_race_title,
    sub.race_id,
    sub.driver_name,
    sub.vehicle,
    sub.finishtime,
    sub.placement,
    sub.total_drivers
FROM 
    (SELECT 
        rd.date AS race_date,
        rd.title || ' - ' || r.title AS full_race_title,
        r.id AS race_id,
        d.name AS driver_name,
        ru.vehicle,
        ru.finishtime,
        RANK() OVER (PARTITION BY ru.race_id ORDER BY ru.finishtime ASC) as placement,
        COUNT(*) OVER (PARTITION BY ru.race_id) as total_drivers
    FROM 
        racedays rd
    INNER JOIN 
        races r ON rd.id = r.raceday_id
    INNER JOIN 
        run ru ON r.id = ru.race_id
    INNER JOIN 
        drivers d ON ru.driver_id = d.id
    WHERE 
        r.mode = 0 AND 
        ru.finishtime > 0 AND 
        ru.penalty = 0) sub
WHERE 
    sub.driver_name = '{0}' AND 
	sub.full_race_title NOT LIKE '%Kval%'
ORDER BY 
    sub.race_date, sub.race_id, sub.finishtime;
        """.format(driver)





