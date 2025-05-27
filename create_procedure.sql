CREATE OR REPLACE PROCEDURE insert_multiple_json(json_list JSON)
LANGUAGE plpgsql
AS $$
DECLARE
    rec JSON;
    id_val TEXT;
    file_val TEXT;
    json_val JSONB;
BEGIN
        FOR rec IN SELECT * FROM json_array_elements(json_list)
        LOOP
            id_val := rec->>'id';
            file_val := rec->>'file_name';
            json_val := to_jsonb(rec);

            -- 嘗試插入單筆資料
            BEGIN
                INSERT INTO json_data(id, file_name, json_data)
                VALUES (id_val, file_val, json_val);
            EXCEPTION WHEN OTHERS THEN
                RAISE EXCEPTION '❌ 插入失敗 (id=%, file=%): %', id_val, file_val, SQLERRM;
            END;
        END LOOP;
END;
$$;
