import json
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from jdsports_spider import JDSportsSpider

def run_spider():
    items = []

    class CustomSpider(JDSportsSpider):
        def parse(self, response):
            for item in super().parse(response):
                if item["discount"] >= 30:
                    items.append(item)

    process = CrawlerProcess(get_project_settings())
    process.crawl(CustomSpider)
    process.start()
    return items

if __name__ == "__main__":
    data = run_spider()
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
