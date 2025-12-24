from src.stock_mcp.crawler.real_time_data import RealTimeDataSpider

real_time_spider = RealTimeDataSpider()
real_time_data = real_time_spider.get_real_time_data("688041.SH")
print(real_time_data)

mark_indices = real_time_spider.get_real_time_market_indices()
print(mark_indices)