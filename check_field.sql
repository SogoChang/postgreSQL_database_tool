CREATE OR REPLACE FUNCTION validate_json_fields_before_insert()
RETURNS TRIGGER AS $$
BEGIN
    -- 檢查 SQL 欄位 id 是否為空
    IF NEW.id IS NULL OR length(trim(NEW.id)) = 0 THEN
        RAISE EXCEPTION 'Missing SQL field: id';
    END IF;

    -- 檢查 SQL 欄位 file_name 是否為空
    IF NEW.file_name IS NULL OR length(trim(NEW.file_name)) = 0 THEN
        RAISE EXCEPTION 'Missing SQL field: file_name';
    END IF;

    -- 檢查 JSON 欄位 response_data 是否存在
    IF NEW.json_data->'response_data' IS NULL THEN
        RAISE EXCEPTION 'Missing field: response_data in json_data';
    END IF;

    -- 檢查 JSON 欄位 response_data.fitness 是否存在
    IF NEW.json_data->'response_data'->'fitness' IS NULL THEN
        RAISE EXCEPTION 'Missing field: response_data.fitness in json_data';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
