from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from jdsports.spiders.jdsports_spider import JDSportsSpider

def run_spider():
    process = CrawlerProcess(get_project_settings())
    process.crawl(JDSportsSpider)
    process.start()
