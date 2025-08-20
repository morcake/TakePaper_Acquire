import os
import re
import requests
from bs4 import BeautifulSoup

from .spider_base import SpiderBase


class SpiderIJCAI(SpiderBase):
    def __init__(self, conference:str, year:int, data_file="data.db"):
        super().__init__(conference, year, data_file)
        
        # IJCAI的基础URL
        self.base_url = "https://www.ijcai.org"

    def spider_all_paper_query_list(self) -> list[dict]:
        if not os.path.exists('temp/'):
            os.makedirs('temp/')
        
        temp_file_path = 'temp/ijcai_{}.html'.format(self.year)
        
        if os.path.exists(temp_file_path):
            print("Loading from temp...")
            with open(temp_file_path, 'r', encoding='utf8') as f:
                html = f.read()
        else:
            # 构建IJCAI会议论文列表的URL
            # IJCAI会议的URL格式通常为：https://www.ijcai.org/proceedings/{year}/
            url = "https://www.ijcai.org/proceedings/{}/".format(self.year)
            print(f"正在访问URL: {url}")
            
            try:
                response = requests.get(url, headers=self.base_headers, timeout=30)
                response.raise_for_status()
                html = response.text
                
                # 保存到临时文件
                with open(temp_file_path, 'w', encoding='utf8') as f:
                    f.write(html)
            except Exception as e:
                print(f"获取会议页面失败: {e}")
                # 如果获取失败，尝试备选URL
                print("尝试备选URL格式...")
                
                # IJCAI的另一种可能的URL格式
                alt_url = "https://ijcai-{}.papers.nips.cc/".format(self.year)
                print(f"正在访问备选URL: {alt_url}")
                
                try:
                    response = requests.get(alt_url, headers=self.base_headers, timeout=30)
                    response.raise_for_status()
                    html = response.text
                    
                    # 保存到临时文件
                    with open(temp_file_path, 'w', encoding='utf8') as f:
                        f.write(html)
                except Exception as e:
                    print(f"获取备选页面也失败: {e}")
                    # 如果都失败，返回空列表
                    return []
        
        soup = BeautifulSoup(html, "html.parser")
        
        paper_query_list = []
        
        # 专门针对IJCAI的URL格式优化爬取逻辑
        # IJCAI每篇论文的信息URL通常为：https://www.ijcai.org/proceedings/{year}/{paper_id}
        
        # 方法1: 查找主内容区域
        main_content = soup.find("div", class_="content") or soup.find("main") or soup
        
        # 方法2: 查找所有符合IJCAI论文URL格式的链接
        # 匹配格式: /proceedings/{year}/数字 或者 proceedings/{year}/数字
        paper_pattern = f"/proceedings/{self.year}/\\d+"
        paper_links = main_content.find_all("a", href=lambda x: x and (paper_pattern in x or 
                                                                       x.startswith(f"proceedings/{self.year}/") and x[14:].isdigit()))
        
        # 如果没有找到匹配的链接，尝试更通用的方法
        if not paper_links:
            print("未找到符合特定格式的论文链接，尝试通用方法...")
            paper_links = main_content.find_all("a", href=True)
        
        print(f"找到{len(paper_links)}个潜在的论文链接")
        
        # 去重 - 确保每篇论文只被添加一次
        seen_papers = set()
        
        for link in paper_links:
            try:
                href_url = link.get("href")
                
                # 过滤掉不相关的链接
                if not href_url or not any([f"/proceedings/{self.year}/" in href_url, 
                                           href_url.startswith(f"proceedings/{self.year}/")]):
                    continue
                
                # 过滤掉PDF链接
                if "pdf" in href_url.lower():
                    continue
                
                # 处理链接格式
                # 确保是相对路径格式如 /proceedings/2024/1
                if href_url.startswith(f"proceedings/{self.year}/") and not href_url.startswith('/'):
                    href_url = '/' + href_url
                    
                # 构建完整URL
                if not href_url.startswith('http'):
                    full_url = self.base_url + href_url
                else:
                    full_url = href_url
                
                # 尝试从URL中提取论文ID
                match = re.search(r'/proceedings/\\d+/(\\d+)', full_url)
                if match:
                    # 提取URL中的最后一部分数字作为论文ID
                    paper_id = match.group(1)
                    # 构建默认标题
                    paper_name = f"IJCAI {self.year} Paper {paper_id}"
                else:
                    # 如果无法提取ID，使用更通用的标题
                    paper_name = f"IJCAI {self.year} Paper - {len(paper_query_list) + 1}"
                
                # 确保链接唯一
                if full_url in seen_papers:
                    continue
                seen_papers.add(full_url)
                
                paper_query_list.append({
                    "paper_name": paper_name,
                    "href_url": full_url
                })
            except Exception as e:
                print(f"处理论文链接时出错: {e}")
                continue
        
        # 去重，避免重复的论文
        seen_titles = set()
        unique_papers = []
        
        for paper in paper_query_list:
            title = paper["paper_name"]
            if title not in seen_titles:
                seen_titles.add(title)
                unique_papers.append(paper)
        
        print(f"找到{len(unique_papers)}篇论文")
        
        return unique_papers
    
    def spider_single_paper_abstract(self, query_data:dict):
        # 使用已经在基类run_spider方法中处理过的完整URL
        url = query_data["href_url"]
        
        print(f"正在获取论文摘要: {url}")
        
        try:
            response = requests.get(url, headers=self.base_headers, timeout=30)
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            
            # 尝试从当前页面提取正确的论文标题
            correct_title = None
            
            # 策略1: 查找meta标签中的标题
            meta_title = soup.find('meta', attrs={'name': 'citation_title'})
            if meta_title and meta_title.get('content'):
                correct_title = meta_title.get('content')
                print(f"从meta标签获取到正确标题: {correct_title}")
                # 更新query_data中的论文标题
                query_data["paper_name"] = correct_title
            
            # 策略2: 查找页面中的h1/h2标题
            elif soup.find('h1') and len(soup.find('h1').text.strip()) > 5:
                correct_title = soup.find('h1').text.strip()
                print(f"从h1标签获取到正确标题: {correct_title}")
                query_data["paper_name"] = correct_title
            elif soup.find('h2') and len(soup.find('h2').text.strip()) > 5:
                correct_title = soup.find('h2').text.strip()
                print(f"从h2标签获取到正确标题: {correct_title}")
                query_data["paper_name"] = correct_title
            
            # 策略3: 查找特定class的标题元素
            elif soup.find('div', class_='title') and len(soup.find('div', class_='title').text.strip()) > 5:
                correct_title = soup.find('div', class_='title').text.strip()
                print(f"从title类div获取到正确标题: {correct_title}")
                query_data["paper_name"] = correct_title
            
            # 如果没有找到更好的标题，保持原有的标题
            if not correct_title:
                correct_title = query_data["paper_name"]
                print(f"未找到更好的标题，保持原有标题: {correct_title}")
            
            # 提取论文摘要 - 基于观察到的IJCAI页面结构优化
            abstract = None
            
            # 策略1：IJCAI特定页面结构 - 直接从container-fluid proceedings-detail中提取摘要
            proceedings_detail = soup.find('div', class_='container-fluid proceedings-detail')
            if proceedings_detail:
                # 查找proceedings-detail下的所有div.row
                rows = proceedings_detail.find_all('div', class_='row')
                if len(rows) >= 3:
                    # 根据HTML结构，第三个row包含摘要内容
                    third_row = rows[2]
                    content_div = third_row.find('div', class_='col-md-12')
                    if content_div:
                        # 直接获取div中的文本作为摘要
                        abstract = content_div.text.strip()
                        # 移除可能的keywords部分
                        if 'Keywords:' in abstract:
                            abstract = abstract.split('Keywords:')[0].strip()
            
            # 策略2：直接从meta标签中提取摘要信息
            if not abstract:
                meta_abstract = soup.find('meta', attrs={'name': 'citation_abstract_html_url'})
                if meta_abstract:
                    # 如果有abstract HTML URL，可以尝试访问，但通常就是当前页面
                    # 我们继续尝试其他方法提取当前页面的摘要
                    pass
            
            # 策略3：查找包含论文内容的主要段落
            if not abstract:
                # 查看页面中是否有特定结构的论文内容
                all_divs = soup.find_all('div')
                for div in all_divs:
                    # 寻找包含大量文本且不包含明显非摘要内容的div
                    text = div.text.strip()
                    if len(text) > 300 and not any(keyword in text.lower() for keyword in 
                                              ['pdf', 'download', 'bibtex', 'keywords', 'authors']):
                        # 检查是否包含学术关键词
                        if any(keyword in text.lower() for keyword in 
                              ['this paper', 'we present', 'in this work', 'we propose', 'abstract']):
                            abstract = text
                            break
            
            # 策略4：查找meta标签中的描述
            if not abstract:
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content') and len(meta_desc.get('content')) > 20:
                    abstract = meta_desc.get('content')
            
            # 策略5：查找所有段落，寻找可能的摘要
            if not abstract:
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.text.strip()
                    if len(text) > 100 and any(keyword in text.lower() for keyword in 
                                            ['abstract', 'introduction', 'this paper', 'we present', 'in this work']):
                        abstract = text
                        break
            
            # 清理摘要内容
            if abstract:
                # 移除多余的空白字符
                abstract = ' '.join(abstract.split())
                # 确保摘要内容合理
                if len(abstract) < 50:
                    abstract = None
            
            # 如果找不到摘要，返回默认文本
            if not abstract:
                abstract = "Abstract not available"
            
            # 返回正确的标题和摘要
            return correct_title, abstract
        except requests.Timeout:
            print(f"请求超时: {url}")
            # 请求超时也返回原标题，这样不会丢失信息
            return query_data["paper_name"], "Abstract not available due to timeout"
        except requests.RequestException as e:
            print(f"请求异常: {e}")
            return query_data["paper_name"], "Abstract not available due to request error"
        except Exception as e:
            print(f"处理摘要时出错: {e}")
            return query_data["paper_name"], "Abstract not available due to processing error"