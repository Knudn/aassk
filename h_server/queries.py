
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