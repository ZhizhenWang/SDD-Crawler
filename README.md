# SDD Crawler
SDD stands for Subtainability Disclosure Database, the aim is to scrape the data from [GRI Website](http://database.globalreporting.org)

## Describe
Use scrapy to store data in MongoDB, and generates 3 collections:
- `org_items` stores organization informations
- `report_items` stores gri reports related with organization
- `search_items` stores orginal search result conntecting above two collections

## Configure settings.py
Following parameter should be changed if not using default value:
```python
MONGODB_SERVER = 'localhost'
MONGODB_PORT = 27017
```

## Usage
To put the spider to work, go to the project’s top level directory and run:
```bash
scrapy crawl reports
```

## LICENSE
[Read more here](./LICENSE).