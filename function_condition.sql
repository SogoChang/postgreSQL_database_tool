CREATE OR REPLACE FUNCTION get_ids_by_conditions(
    min_sharpe NUMERIC,
    min_fitness NUMERIC,
    max_turnover NUMERIC
)
RETURNS TABLE(id TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT jd.id
    FROM json_data jd
    WHERE 
        -- 條件 1: sharpe
        (jd.json_data->'response_data'->>'sharpe')::NUMERIC >= min_sharpe

        -- 條件 2: fitness
        AND (jd.json_data->'response_data'->>'fitness')::NUMERIC >= min_fitness

        -- 條件 3: checks 陣列中存在 name = 'CONCENTRATED_WEIGHT' AND result = 'PASS'
        AND EXISTS (
            SELECT 1
            FROM jsonb_array_elements(jd.json_data->'response_data'->'checks') AS elem
            WHERE elem->>'name' = 'CONCENTRATED_WEIGHT'
              AND elem->>'result' = 'PASS'
        )

        -- 條件 4: turnover
        AND (jd.json_data->'response_data'->>'turnover')::NUMERIC <= max_turnover

        -- 條件 5: sub_universe_sharpe
        AND EXISTS (
            SELECT 1
            FROM jsonb_array_elements(jd.json_data->'response_data'->'checks') AS elem
            WHERE elem->>'name' = 'LOW_SUB_UNIVERSE_SHARPE'
              AND elem->>'result' = 'PASS'
        );
END;
$$ LANGUAGE plpgsql;
