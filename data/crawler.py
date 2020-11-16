import os
import logging, time

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

li = os.listdir('/home/tupt/Documents/QuoraScraperData/input')

print(f"Total {len(li)} files")

cmd = "quora-scraper answers -f "

for i in range(0, len(li)):
    name = li[i]
    print("[INFO] Crawl answer for: ", i, "-", name)
    new_cmd = cmd + name
    os.system(new_cmd)
    
print("Crawl successfully!")
    