import os
import requests
from bs4 import BeautifulSoup

from .spider_base import SpiderBase


class SpiderECCV(SpiderBase):
    def __init__(self, conference:str, year:int, data_file="data.db"):
        super().__init__(conference, year, data_file)
    
        self.base_url = "https://openaccess.thecvf.com"

    def spider_all_paper_query_list(self) -> list[dict]:
        if not os.path.exists('temp/'):
            os.makedirs('temp/')
        if os.path.exists('temp/eccv_{}.html'.format(self.year)):
            print("Loading from temp...")
            with open('temp/eccv_{}.html'.format(self.year), 'r', encoding='utf8') as f:
                html = f.read()
        else:
            # 使用新的URL格式获取ECCV论文列表
            url = "https://eccv{}.ecva.net/virtual/{}/papers.html".format(self.year, self.year)
            print(f"正在访问URL: {url}")
            response = requests.get(url, headers=self.base_headers)
            response.raise_for_status()
            html = response.text
            with open('temp/eccv_{}.html'.format(self.year), 'w', encoding='utf8') as f:
                f.write(html)
        soup = BeautifulSoup(html, "html.parser")

        paper_query_list = []
        
        # 首先尝试从noscript标签中获取论文列表（这是ECCV 2024页面的实际结构）
        noscript_tag = soup.find("noscript", class_="noscript")
        if noscript_tag:
            print("找到noscript标签，尝试从中提取论文列表...")
            # 查找noscript标签内的ul元素
            ul_tag = noscript_tag.find("ul")
            if ul_tag:
                # 获取所有li元素
                paper_elements = ul_tag.find_all("li")
                print(f"找到{len(paper_elements)}篇论文")
                
                for paper in paper_elements:
                    a_tag = paper.find("a")
                    if a_tag:
                        paper_name = a_tag.text.strip()
                        href_url = a_tag.get("href")
                        if href_url:
                            # 处理相对URL
                            if not href_url.startswith('http'):
                                href_url = "https://eccv{}.ecva.net{}".format(
                                    self.year, 
                                    href_url if href_url.startswith('/') else '/' + href_url
                                )
                            paper_query_list.append({
                                "paper_name": paper_name,
                                "href_url": href_url
                            })
            
        # 如果从noscript中没有找到论文，尝试其他可能的结构
        if not paper_query_list:
            print("从noscript中未找到论文，尝试其他结构...")
            # 适配新的HTML结构，查找论文列表
            paper_elements = soup.select(".paper")  # 假设新页面中论文项有paper类
            if not paper_elements:
                # 尝试另一种可能的选择器
                paper_elements = soup.find_all("h3", class_="card-title")
                
            if not paper_elements:
                # 尝试使用原始的选择逻辑作为后备方案
                container_div = soup.find("div", {"id": "content"})
                if container_div:
                    paper_elements = container_div.find_all("dt", {"class": "ptitle"})
                    
            for paper in paper_elements:
                if hasattr(paper, 'find'):
                    a_tag = paper.find("a")
                    if a_tag:
                        paper_name = a_tag.text.strip()
                        href_url = a_tag.get("href")
                        if href_url and not href_url.startswith('http'):
                            # 处理相对URL
                            href_url = "https://eccv{}.ecva.net{}".format(self.year, href_url if href_url.startswith('/') else '/' + href_url)
                        paper_query_list.append({
                            "paper_name": paper_name,
                            "href_url": href_url
                        })
        
        print(f"最终提取到{len(paper_query_list)}篇论文")
        return paper_query_list
    
    def spider_single_paper_abstract(self, query_data:dict):
        # 检查URL是否已经是完整的URL
        if query_data["href_url"].startswith('http'):
            url = query_data["href_url"]
        else:
            # 对于相对URL，使用当前年份的ECVA网站
            url = "https://eccv{}.ecva.net{}".format(self.year, query_data["href_url"] if query_data["href_url"].startswith('/') else '/' + query_data["href_url"])
        
        response = requests.get(url, headers=self.base_headers)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        
        # 尝试多种可能的摘要选择器
        abstract = ""
        abstract_div = soup.find("div", {"id": "abstract"})
        if abstract_div:
            abstract = abstract_div.text.strip()
        else:
            # 尝试查找class为abstract的元素
            abstract_div = soup.find("div", class_="abstract")
            if abstract_div:
                abstract = abstract_div.text.strip()
            else:
                # 尝试查找id包含abstract的元素
                abstract_div = soup.find("div", id=lambda x: x and "abstract" in x.lower())
                if abstract_div:
                    abstract = abstract_div.text.strip()
                else:
                    # 如果找不到摘要，设置默认值
                    abstract = "Abstract not available"
        
        return abstract