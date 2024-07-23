import os.path
import requests
import re
import time
from tqdm import tqdm
import parsel
import csv
import random
from concurrent.futures import ThreadPoolExecutor

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
}

proxy_pools = ['14ada72cb0207:9a882d85be@2.56.187.17:12323', '14ada72cb0207:9a882d85be@213.109.155.19:12323',
               '14ada72cb0207:9a882d85be@45.12.12.93:12323', '14ada72cb0207:9a882d85be@45.9.153.207:12323',
               '14ada72cb0207:9a882d85be@72.14.139.196:12323']

url = "https://www.qvc.com/jai-sterling-silver-textured-dome-ring.product.J436129.html"


def request(url):
    proxy_pool = random.choices(proxy_pools)
    proxies = {
        "http": "http://" + proxy_pool[0],
        "https": "http://" + proxy_pool[0]
    }
    reponse = requests.get(url=url, headers=headers, proxies=proxies).text
    return reponse


def get_contens(product_url_1):
    # product_url = "https://www.qvc.com/adorna-polished-diamond-cut-byzantine-72g-bracelet%2C-14k.product.J436718.html"
    product_respons = request(product_url_1)
    select_page = parsel.Selector(product_respons)
    title = select_page.xpath('//*[@id="pageContent"]//h1/text()').get()
    price_1 = re.findall('data-sale-price=\"(.*)\"', product_respons)
    price_2 = re.findall('data-qvc-price=\"(.*)\"', product_respons)
    # price = select_page.xpath('//*[@id="pageContent"]/div[6]/div[2]/div[2]/div[1]/div[1]/div/span').get()
    print("正在爬取产品:{}".format(title))

    if not os.path.exists('img\\' + title):
        os.mkdir('img\\' + title)

    with open("qvc_jewelry.csv", mode="a", encoding="utf-8", newline="", errors='ignore') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow([title, price_1, price_2])

    img_srcs = select_page.xpath('//*[@id="imageThumbnails"]/div/a/@href').getall()
    for img_src in img_srcs:
        full_src = "https:" + img_src
        # print(full_src)
        img_name0 = img_src.split("?")[0]
        img_nameint = random.randint(100000, 999999)
        img_name = str(img_nameint) + "img" + img_name0.split('/')[-1] + '.webp'

        img_content = requests.get(url=full_src, headers=headers).content
        with open(f"img\\{title}\\{img_name}", mode='wb') as file:
            file.write(img_content)
            time.sleep(1)


def get_product_url(collections_url_1):
    # collections_url = 'https://www.qvc.com/jewelry/bracelets/_/N-mfmw/c.html?currentPage=1#plModule'
    collections_response = request(collections_url_1)
    collections_select = parsel.Selector(collections_response)
    product_urls = collections_select.xpath(
        '//*[@id="plModule"]/div/div[3]/div/div/div[2]/div/div/div/a/@href').getall()
    # print(product_urls)
    return product_urls




for page in tqdm(range(1, 46)):
    print("正在爬取第{}页".format(page))
    time.sleep(10)
    collections_url = 'https://www.qvc.com/jewelry/earrings/_/N-nkty/c.html?currentPage={}#plModule'.format(page)
    producturls = get_product_url(collections_url)
    # for product_url in producturls:
    #     try:
    #         get_contens(product_url)
    #     except:
    #         print("爬取{}失败".format(product_url))
    #         continue

    with ThreadPoolExecutor(16) as t:
        for product_url in producturls:
            try:
                t.submit(get_contens, product_url)
            except:
                print("爬取{}失败".format(product_url))
                continue

