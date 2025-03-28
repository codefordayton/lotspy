from io import BytesIO
import sqlite3
from typing import Any
from scrapy.exporters import BaseItemExporter

from lotspy.items import NoorpItem

# Mapping of NoorpItem fields to the SQLite3 table schema
# The keys are fields in the NoorpItem and the values define
# the column name and type in the SQL table
FIELD_MAPPING = {
    field_name: (field_meta["db_field"], field_meta["db_type"])
    for field_name, field_meta in NoorpItem.fields.items()
    if "db_field" in field_meta and "db_type" in field_meta
}


class Sqlite3Exporter(BaseItemExporter):

    def __init__(self, file: BytesIO, **kwargs: Any):
        super().__init__(dont_fail=False, **kwargs)

        # The file parameter is usually used in other exporters for writing directly,
        # but sqlite3 needs to manage the file itself, so we'll close this handle
        file.close()

        # Open the file as a sqlite3 database
        self.db = sqlite3.connect(file.name)

    def start_exporting(self):
        # Dynamically create the table using the FIELD_MAPPING
        # NOTE: We don't need to care about SQL injection here because
        # we're in full control of the field names via FIELD_MAPPING
        columns = ", ".join(
            f"{db_field} {db_type}" for _, (db_field, db_type) in FIELD_MAPPING.items()
        )
        self.db.execute(
            f"""
            CREATE TABLE IF NOT EXISTS rental_registry (
                {columns}
            )
            """
        )

    def finish_exporting(self):
        self.db.close()

    def export_item(self, item: Any) -> None:
        if not isinstance(item, NoorpItem):
            raise ValueError(
                "Sqlite3Exporter only supports exporting NoorpItems"
            )

        # Dynamically generate the INSERT statement
        # NOTE: We don't need to care about SQL injection with db_fields,
        # because we're in full control of the field names via FIELD_MAPPING
        # BUT! we do need to worry about SQL injection with the placeholders,
        # so we appropriately use ? placeholders and parameters
        db_fields = ", ".join(db_field for _, (db_field, _) in FIELD_MAPPING.items())
        placeholders = ", ".join("?" for _ in FIELD_MAPPING)
        insert_query = f"""
            INSERT INTO rental_registry ({db_fields})
            VALUES ({placeholders})
        """
        values = tuple(item[field] for field in FIELD_MAPPING)

        with self.db:
            self.db.execute(insert_query, values)
