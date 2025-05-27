CREATE TRIGGER trg_check_fields_before_insert
BEFORE INSERT ON json_data
FOR EACH ROW
EXECUTE FUNCTION validate_json_fields_before_insert();
