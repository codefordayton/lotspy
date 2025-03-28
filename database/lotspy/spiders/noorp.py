import csv
import io
import scrapy

from lotspy.items import NoorpItem


class NoorpSpider(scrapy.Spider):
    name = "noorp"
    allowed_domains = ["go.mcohio.org"]
    start_urls = ["https://go.mcohio.org"]

    def start_requests(self):
        urls = [
            "https://go.mcohio.org/ApplicationS/auditor/rentalreg/RENTAL_REGISTRATION_LIST.CFM",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_registry_index)

    def parse_registry_index(self, response):
        # Find all of the links in the table
        for file in response.css("table tr a::attr(href)").getall():
            # skip anything that's not a csv file
            if not file.endswith(".csv"):
                continue

            # the url is formatted with backslashes, so replace them with forward slashes
            file = file.replace("\\", "/")
            yield response.follow(file, callback=self.parse_registry_csv)

    def parse_registry_csv(self, response):
        csv_r = csv.reader(
            io.StringIO(response.text),
            delimiter=",",
            quotechar='"',
            lineterminator="\r\n",
        )

        try:
            # The first row of the csv file will be the headers
            headers = next(csv_r)

            # for some reason the csv rows include an extra comma at the end of the row
            # which gets parsed as an empty value.
            # I'm not sure if this is from a specific csv dialect. To handle it we can
            # just add an extra header to the end of the headers list for the empty
            # column that gets parsed to fall under.
            headers.append("WEIRD_EXTRA_COMMA")
        except StopIteration:
            return

        for row in csv_r:
            # ensure that the row is how we expect based on the headers
            if len(row) != len(headers):
                print(
                    f"ignoring row {csv_r.line_num} (length: {len(row)}, should be: {len(headers)})"
                )
                continue

            # label the row with the headers
            row = dict(zip(headers, row))

            # parse the row into a NoorpItem
            item = NoorpItem()

            # parse fields that are labeled with csv_source metadata
            for item_field, meta in item.fields.items():
                csv_source = meta.get("csv_source")
                if csv_source is None:
                    continue

                item[item_field] = row.get(csv_source)

            # parse fields that are not a simple 1 to 1 mapping here:
            # ...

            yield item