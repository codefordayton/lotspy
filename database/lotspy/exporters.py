from functools import lru_cache
from io import BytesIO
import sqlite3
from typing import Any, Type
import scrapy
from scrapy.exporters import BaseItemExporter

from lotspy.items import NoorpItem, ParcelItem

EXPORTABLE_ITEMS = [
    ParcelItem,
    NoorpItem,
]


@lru_cache(maxsize=None)
def get_table_description(ItemClass: Type[scrapy.Item]):
    return {
        "name": ItemClass.db_table_name,
        "field_mappings": {
            field_name: (field_meta["db_field"], field_meta["db_type"])
            for field_name, field_meta in ItemClass.fields.items()
            if "db_field" in field_meta and "db_type" in field_meta
        },
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
        for ItemClass in EXPORTABLE_ITEMS:
            table_description = get_table_description(ItemClass)
            name = table_description["name"]
            field_mappings = table_description["field_mappings"]

            # NOTE: We don't need to care about SQL injection here because
            # we're in full control of the field names
            columns = ", ".join(
                f"{db_field} {db_type}"
                for _, (db_field, db_type) in field_mappings.items()
            )
            self.db.execute(
                f"""
                DROP TABLE IF EXISTS {name}
                """
            )
            self.db.execute(
                f"""
                CREATE TABLE {name} (
                    {columns}
                )
                """
            )

    def finish_exporting(self):
        self.db.close()

    def export_item(self, item: Any) -> None:
        if not item.__class__ in EXPORTABLE_ITEMS:
            raise ValueError(f"Item not supported by Sqlite3Exporter")

        table_description = get_table_description(item.__class__)
        name = table_description["name"]
        field_mappings = table_description["field_mappings"]

        # Dynamically generate the INSERT statement
        # NOTE: We don't need to care about SQL injection with db_fields,
        # because we're in full control of the field names.
        # BUT! we do need to worry about SQL injection with the values,
        # so we appropriately use ? placeholders and parameters
        db_fields = ", ".join(db_field for _, (db_field, _) in field_mappings.items())
        placeholders = ", ".join("?" for _ in field_mappings)
        insert_query = f"""
            INSERT INTO {name} ({db_fields})
            VALUES ({placeholders})
        """
        values = tuple(item[field] for field in field_mappings)

        with self.db:
            self.db.execute(insert_query, values)
