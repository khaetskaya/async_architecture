import json
from jsonschema import Draft7Validator
import os


class Validator:
    def __init__(self):
        self.loaded_schemas = {}
        self.root_dir = os.path.dirname(os.path.abspath(__file__))

    def load_schema(self, schema_name, version):
        if schema_name not in self.loaded_schemas:
            path = schema_name.replace('.', '/')
            schema_file_path = os.path.join(self.root_dir, 'schemas', f'{path}/{version}.json')
            try:
                with open(schema_file_path) as f:
                    self.loaded_schemas[schema_name] = json.load(f)
                    print(f"Schema '{schema_name}' loaded successfully.")
            except FileNotFoundError:
                print(f"Schema '{schema_name}' not found.")

    def validate_data(self, schema_name, version, data):
        if schema_name not in self.loaded_schemas:
            self.load_schema(schema_name, version)

        schema = self.loaded_schemas.get(schema_name)
        if schema:
            validator = Draft7Validator(schema)
            errors = list(validator.iter_errors(data))
            if not errors:
                return True, None  # Valid data
            else:
                print(errors)
                return False, errors  # Invalid data with errors
        else:
            return False, 'Schema not found'
