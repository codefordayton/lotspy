# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LotspyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ParcelItem(scrapy.Item):
    """
    A parcel

    Available metadata:

    - `db_field` - optional, the corresponding database table column name
    - `db_type` - optional, the type of the column in the database table
    """

    db_table_name = "parcels"
    db_extra = """
    CREATE UNIQUE INDEX IF NOT EXISTS parcels_parcel_number_idx
    ON parcels (parcel_number);
    """

    parcel = scrapy.Field(
        db_field="parcel_number",
        db_type="TEXT",
    )
    longitude = scrapy.Field(
        db_field="longitude",
        db_type="REAL",
    )
    latitude = scrapy.Field(
        db_field="latitude",
        db_type="REAL",
    )
    address = scrapy.Field(
        db_field="address",
        db_type="TEXT",
    )


class NoorpItem(scrapy.Item):
    """
    A single Non Owner Occupied Rental Property item.

    Available metadata:

    - `csv_source` - optional, name of the column in the CSV file. Useful
        if this field is a simple copy of the CSV data
    - `db_field` - optional, the corresponding database table column name
    - `db_type` - optional, the type of the column in the database table

    If a field is calculated or derived from other fields, it would not have
    a `csv_source` metadata field, but can still have `db_field` and `db_type` to
    be exported to the database.
    """

    db_table_name = "noorp"
    db_extra = """"
    CREATE UNIQUE INDEX IF NOT EXISTS noorp_parcel_idx
    ON noorp (parcel);
    """

    # define the fields for your item here like:
    tax_district = scrapy.Field(
        csv_source="TAX DISTRICT",
        db_field="tax_district",
        db_type="TEXT",
    )
    district_name = scrapy.Field(
        csv_source="DISTRICT NAME",
        db_field="district_name",
        db_type="TEXT",
    )
    parcel = scrapy.Field(
        csv_source="PARCEL",
        db_field="parcel",
        db_type="TEXT",
    )
    location = scrapy.Field(
        csv_source="LOCATION",
        db_field="location",
        db_type="TEXT",
    )
    location_street_number = scrapy.Field(
        csv_source="LOCATION STREET NUMBER",
        db_field="location_street_number",
        db_type="TEXT",
    )
    location_street_direction = scrapy.Field(
        csv_source="LOCATION STREET DIRECTION",
        db_field="location_street_direction",
        db_type="TEXT",
    )
    location_street_name = scrapy.Field(
        csv_source="LOCATION STREET NAME",
        db_field="location_street_name",
        db_type="TEXT",
    )
    location_street_suffix = scrapy.Field(
        csv_source="LOCATION STREET SUFFIX",
        db_field="location_street_suffix",
        db_type="TEXT",
    )
    location_street_suffix2 = scrapy.Field(
        csv_source="LOCATION STREET SUFFIX2",
        db_field="location_street_suffix2",
        db_type="TEXT",
    )
    agent_type = scrapy.Field(
        csv_source="AGENT TYPE",
        db_field="agent_type",
        db_type="TEXT",
    )
    agent_name = scrapy.Field(
        csv_source="AGENT NAME",
        db_field="agent_name",
        db_type="TEXT",
    )
    street_number = scrapy.Field(
        csv_source="STREET NUMBER",
        db_field="street_number",
        db_type="TEXT",
    )
    street_direction = scrapy.Field(
        csv_source="STREET DIRECTION",
        db_field="street_direction",
        db_type="TEXT",
    )
    street_name = scrapy.Field(
        csv_source="STREET NAME",
        db_field="street_name",
        db_type="TEXT",
    )
    street_suffix = scrapy.Field(
        csv_source="STREET SUFFIX",
        db_field="street_suffix",
        db_type="TEXT",
    )
    street_suffix2 = scrapy.Field(
        csv_source="STREET SUFFIX2",
        db_field="street_suffix2",
        db_type="TEXT",
    )
    city = scrapy.Field(
        csv_source="CITY",
        db_field="city",
        db_type="TEXT",
    )
    state = scrapy.Field(
        csv_source="STATE",
        db_field="state",
        db_type="TEXT",
    )
    zip = scrapy.Field(
        csv_source="ZIP",
        db_field="zip",
        db_type="TEXT",
    )
    phone = scrapy.Field(
        csv_source="PHONE",
        db_field="phone",
        db_type="TEXT",
    )
    number_units = scrapy.Field(
        csv_source="NUMBER UNITS",
        db_field="number_units",
        db_type="TEXT",
    )
    wen = scrapy.Field(
        csv_source="WEN",
        db_field="wen",
        db_type="TEXT",
    )
