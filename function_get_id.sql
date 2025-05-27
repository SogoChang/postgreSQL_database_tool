CREATE OR REPLACE FUNCTION get_pnl_by_id(target_id TEXT)
RETURNS JSONB AS $$
DECLARE
    pnl_data JSONB;
BEGIN
    SELECT json_data->'pnl' INTO pnl_data
    FROM json_data
    WHERE id = target_id;

    RETURN pnl_data;
END;
$$ LANGUAGE plpgsql;
