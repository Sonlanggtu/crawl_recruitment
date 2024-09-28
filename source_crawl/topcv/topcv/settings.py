# Scrapy settings for topcv project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "topcv"

SPIDER_MODULES = ["topcv.spiders"]
NEWSPIDER_MODULE = "topcv.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "topcv (+https://www.topcv.vn)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   "topcv.middlewares.TopcvSpiderMiddleware": 543,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
   "topcv.middlewares.TopcvDownloaderMiddleware": 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   "topcv.pipelines.TopcvPipeline": 300,
}

#Config DB Mongo
MONGODB_SERVER = "localhost"
#MONGODB_SERVER = "mongo"
MONGODB_PORT = 27017
MONGODB_DB = "Crawl_Recruitment"
MONGODB_COLLECTION = "Job"
MONGODB_COLLECTION_ERROR = "Job_Error"

#Config get jobs
#LINK_GET_JOB_TOPCV = "https://www.topcv.vn/api-featured-jobs?limit=20&city=0&salary=&exp=&category="

#Config get jobs
#GET_NUMBER_PAGE = 50 # 1 page have 50 job

CONFIG_MAIL = {
   "SMTP_SERVER":"smtp.gmail.com",
   "SMTP_PORT":587,
   "SMTP_USERNAME":"",
   "SMTP_PASSWORD":"",
   "FROM_EMAIL":"",
   "TO_EMAIL":""
}

#PROXY FORMAT = 'http://username:password@your_proxy_address:port'
#PROXY = ''

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
RETRY_HTTP_CODES = [429]


# Enable retry middleware
RETRY_ENABLED = True

# Number of retries
RETRY_TIMES = 15
MAX_RETRY_TIMES = 20
PRIORITY_ADJUST = 1

# HTTP status codes to retry (default: [500, 502, 503, 504])
#RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

# Delay between retries in seconds (optional)
#RETRY_DELAY = 20000

# RETRY_EXCEPTIONS = (
#     'scrapy.exceptions.IgnoreRequest',
#     'scrapy.core.downloader.handlers.http.HttpDownloadHandler',
#     'socket.timeout',
#     'requests.exceptions.RequestException',
# )