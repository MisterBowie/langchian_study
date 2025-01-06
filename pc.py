from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from lxml import html, etree
import csv
import time

# 设置Chrome的选项，避免打开浏览器界面
chrome_options = Options()
chrome_options.add_argument('--headless')  # 无头模式
chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
chrome_options.add_argument('--no-sandbox')  # Linux下需要

# 启动Chrome浏览器
options = webdriver.ChromeOptions()
options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36')
driver = webdriver.Chrome(options=options)
# URL（请根据实际情况修改）
url = "https://www.sigmaaldrich.cn/CN/zh/products/analytical-chemistry/reference-materials?country=CN&language=zh&cmsRoute=products&cmsRoute=analytical-chemistry&cmsRoute=reference-materials&page="

# 页码循环最大次数
max_pages = 80

# 用于爬取数据的XPath
_xpath = '//*[@id="products"]/div/div[2]/div[2]/div/div[2]'  # 这是每行的XPath路径


def fetch_page_data(page_number):
    # 生成带有分页的URL
    page_url = f"{url}{page_number}"  # 根据实际分页URL参数调整

    # 使用Selenium打开网页
    print(f"正在打开第{page_number}页: {page_url}")
    driver.get(page_url)

    # 等待页面加载完成，适当增加等待时间，确保页面渲染完毕
    time.sleep(3)  # 根据页面复杂度调整等待时间

    # 获取页面内容
    page_content = driver.page_source
    print(f"第{page_number}页加载完成。")
    return page_content


def parse_row_data(row):
    # 解析每行数据
    product_id = row.xpath("div[@class='jss314']/a/text()")  # 货号
    product_name = row.xpath(
        "div[@class='jss299']//a//b//span/text()")  # 产品名称
    product_desc = row.xpath("div[@class='jss300']//a//span/text()")  # 产品描述

    # 返回抓取到的数据
    data = {
        '货号': product_id[0] if product_id else '',
        '产品名称': product_name[0] if product_name else '',
        '产品描述': product_desc[0] if product_desc else ''
    }

    return data


def save_to_csv(data, filename="output.csv"):
    # 使用csv模块将数据写入CSV文件
    print(f"将数据保存到CSV文件: {filename}")
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['货号', '产品名称', '产品描述'])
        writer.writeheader()  # 写入表头
        for row in data:
            writer.writerow(row)
    print(f"数据已成功保存到{filename}.")


def main():
    all_data = []
    print(f"开始爬取数据，共{max_pages}页。")

    # 循环80次，爬取每一页的数据
    for page in range(1, max_pages + 1):
        print(f"正在爬取第{page}页数据...")
        page_content = fetch_page_data(page)

        if page_content:
            tree = html.fromstring(page_content)
            table = tree.xpath(_xpath)  # 获取所有行
            print(f"第{page}页共抓取到{len(table)}行数据。")
            rows = table[0].xpath("div")
            # first_row_html = etree.tostring(
            #     rows[4], pretty_print=True, encoding='unicode')
            # print(first_row_html)
            print(f'-------------------{len(rows)}行数据')
            for row in rows:
                # first_row_html = etree.tostring(
                #   row, pretty_print=True, encoding='unicode')
                # print(first_row_html)
                # first_row_html = etree.tostring(
                #   rows[1], pretty_print=True, encoding='unicode')
                # print(first_row_html)

                row_data = parse_row_data(row)
                print(f"第{page}页共抓取到 {row_data} 数据。")
                all_data.append(row_data)  # 将当前行的数据加入到总数据中
        else:
            print(f"第{page}页爬取失败，跳过该页")

    # 输出爬取到的数据
    print(f"共爬取到{len(all_data)}条数据")
    # 将数据保存到CSV文件
    save_to_csv(all_data)


if __name__ == "__main__":
    main()

    # 关闭浏览器
    print("爬取完成，关闭浏览器。")
    driver.quit()
