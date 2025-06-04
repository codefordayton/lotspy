```console
# Start environment
$ poetry install
$ poetry shell

# Scrape and create the SQLite database
$ scrapy crawl parcels -o datasette/lotspy.db
$ scrapy crawl noorp -o datasette/lotspy.db

# Run the Datasette server
$ datasette ./datasette
```
