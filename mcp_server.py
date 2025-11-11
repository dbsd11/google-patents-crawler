#!/usr/bin/env python3
"""
Google Patents Crawler MCP Server

This MCP server provides tools for searching Google Patents and extracting patent information.
It supports keyword search, pagination, and sorting options.
"""

import urllib.parse
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
)

from common.tools.browser.browser import get_global_driver, wait_for_page_load
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from logger import logger

@dataclass
class PatentInfo:
    """专利信息数据类"""
    title: str
    grant_number: str
    inventor: str
    assignee: str
    dates: str
    abstract: str
    pdf_link: Optional[str] = None

class GooglePatentsCrawler:
    """Google专利搜索爬虫类"""
    
    def __init__(self):
        self.base_url = "https://patents.google.com/"
        self.driver = None
    
    def build_search_url(self, keywords: str, page_size: int = 10, page: int = 0, sort: str = "") -> str:
        """
        构建Google专利搜索URL
        
        Args:
            keywords: 搜索关键词
            page_size: 每页结果数量 (默认10)
            page: 页码，从0开始 (默认0)
            sort: 排序方式，"new"表示按时间排序，空字符串表示按相关性排序
            
        Returns:
            完整的搜索URL
        """        
        # 构建查询参数
        params = {
            'q': keywords,
            'num': str(page_size),
            'page': str(page),
            'country': 'CN',
            'language': 'CHINESE',
        }
        
        # 如果指定了排序方式，添加sort参数
        if sort == "new":
            params['sort'] = 'new'
        elif sort == "old":
            params['sort'] = 'old'
        
        # 构建完整URL
        query_string = urllib.parse.urlencode(params)
        full_url = f"{self.base_url}?{query_string}"
        
        logger.info(f"构建的搜索URL: {full_url}")
        return full_url
    
    def parse_patent_results(self, html_content: str) -> List[PatentInfo]:
        """
        解析HTML内容，提取专利信息
        
        Args:
            html_content: 页面HTML内容
            
        Returns:
            专利信息列表
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        patents = []
        
        # 查找所有专利结果项
        result_items = soup.find_all('search-result-item', class_='style-scope search-results')
        
        logger.info(f"找到 {len(result_items)} 个专利结果")
        
        for item in result_items:
            try:
                # 提取标题
                title_element = item.find('h3', class_='style-scope search-result-item')
                title = ""
                if title_element:
                    title_span = title_element.find('span', id='htmlContent')
                    if title_span:
                        title = title_span.get_text(strip=True)
                
                # 提取专利授权号
                grant_number = ""
                patent_link = item.find('a', class_='pdfLink style-scope search-result-item')
                if patent_link:
                    patent_span = patent_link.find('span')
                    if patent_span:
                        grant_number = patent_span.get_text(strip=True)
                else:
                    # 如果没有PDF链接，尝试从其他位置提取专利授权号
                    metadata = item.find('h4', class_='metadata style-scope search-result-item')
                    if metadata:
                        spans = metadata.find_all('span')
                        for span in spans:
                            text = span.get_text(strip=True)
                            if text and len(text) > 5 and ('CN' in text or 'US' in text or 'EP' in text):
                                grant_number = text
                                break
                
                # 提取发明人
                inventor = ""
                inventor_spans = item.find_all('span', class_='style-scope search-result-item')
                for span in inventor_spans:
                    html_content_span = span.find('span', id='htmlContent')
                    if html_content_span:
                        text = html_content_span.get_text(strip=True)
                        # 简单判断是否为人名（中文姓名通常较短）
                        if text and len(text) <= 10 and not any(char in text for char in ['公司', '大学', '研究', '科技', '有限']):
                            inventor = text
                            break
                
                # 提取申请人/公司
                assignee = ""
                for span in inventor_spans:
                    html_content_span = span.find('span', id='htmlContent')
                    if html_content_span:
                        text = html_content_span.get_text(strip=True)
                        # 判断是否为公司名称
                        if text and any(char in text for char in ['公司', '大学', '研究', '科技', '有限', 'Inc', 'Corp', 'Ltd']):
                            assignee = text
                            break
                
                # 提取日期信息
                dates = ""
                dates_element = item.find('h4', class_='dates style-scope search-result-item')
                if dates_element:
                    dates = dates_element.get_text(strip=True)
                
                # 提取摘要
                abstract = ""
                abstract_element = item.find('raw-html', class_='style-scope search-result-item')
                if abstract_element:
                    abstract_span = abstract_element.find('span', id='htmlContent')
                    if abstract_span:
                        abstract = abstract_span.get_text(strip=True)
                
                # 提取PDF链接
                pdf_link = ""
                if patent_link and patent_link.get('href'):
                    pdf_link = patent_link.get('href')
                
                # 创建专利信息对象
                if title or grant_number:  # 至少要有标题或专利授权号
                    patent = PatentInfo(
                        title=title,
                        grant_number=grant_number,
                        inventor=inventor,
                        assignee=assignee,
                        dates=dates,
                        abstract=abstract,
                        pdf_link=pdf_link
                    )
                    patents.append(patent)
                    
            except Exception as e:
                logger.error(f"解析专利信息时出错: {str(e)}")
                continue
        
        return patents
    
    async def search_patents(self, keywords: str, page_size: int = 10, page: int = 0, sort: str = "") -> List[Dict[str, Any]]:
        """
        搜索专利并返回结果
        
        Args:
            keywords: 搜索关键词
            page_size: 每页结果数量
            page: 页码
            sort: 排序方式
            
        Returns:
            专利信息字典列表
        """
        try:
            # 构建搜索URL
            search_url = self.build_search_url(keywords, page_size, page, sort)
            
            # 获取浏览器驱动
            self.driver = get_global_driver()
            
            # 访问搜索页面
            logger.info(f"正在访问: {search_url}")
            self.driver.get(search_url)
            
            # 等待页面加载
            wait_for_page_load(self.driver, timeout=30)
            
            # 等待搜索结果加载
            numResultsLabel = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.ID, "numResultsLabel"))
            )
            # About 29,110 results
            total_num_results_str = numResultsLabel[0].text.strip()
            total_num_results = int(total_num_results_str.split()[1].replace(',', ''))
            
            # 获取页面HTML内容
            html_content = self.driver.page_source
            
            # 解析专利信息
            patents = self.parse_patent_results(html_content)
            
            # 转换为字典格式
            results = []
            for patent in patents:
                results.append({
                    "title": patent.title,
                    "grant_number": patent.grant_number,
                    "inventor": patent.inventor,
                    "assignee": patent.assignee,
                    "dates": patent.dates,
                    "abstract": patent.abstract,
                    "pdf_link": patent.pdf_link
                })
            
            logger.info(f"成功解析 {len(results)} 个专利结果")
            return {
                "total_num_results": total_num_results,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"搜索专利时出错: {str(e)}")
            raise

# 创建MCP服务器实例
server = Server("google-patents-crawler")
crawler = GooglePatentsCrawler()

search_patents_tool = Tool(
    name="search_patents",
    description="搜索Google专利数据库，支持关键词搜索、分页和排序",
    inputSchema={
        "type": "object",
        "properties": {
            "keywords": {
                "type": "string",
                "description": "搜索关键词，支持多个关键词用空格分隔"
            },
            "page_size": {
                "type": "integer",
                "description": "每页结果数量，默认10，最大100",
                "default": 10,
                "minimum": 1,
                "maximum": 100
            },
            "page": {
                "type": "integer",
                "description": "页码，从0开始，默认0",
                "default": 0,
                "minimum": 0
            },
            "sort": {
                "type": "string",
                "description": "排序方式：relevance(相关性), new(从新到旧), old(从旧到新)",
                "enum": ["relevance", "new", "old"],
                "default": "relevance"
            }
        },
        "required": ["keywords"]
    },
    outputSchema={
        "type": "object",
        "properties": {
            "results": {
                "type": "array",
                "description": "专利搜索结果列表",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "专利标题"
                        },
                        "grant_number": {
                            "type": "string",
                            "description": "专利授权号"
                        },
                        "inventor": {
                            "type": "string",
                            "description": "发明人"
                        },
                        "assignee": {
                            "type": "string",
                            "description": "申请人/受让人"
                        },
                        "dates": {
                            "type": "string",
                            "description": "相关日期"
                        },
                        "abstract": {
                            "type": "string",
                            "description": "专利摘要"
                        },
                        "pdf_link": {
                            "type": "string",
                            "description": "PDF文档链接",
                            "format": "uri"
                        }
                    },
                    "required": ["title", "grant_number", "abstract"]
                }
            },
            "total_count": {
                "type": "integer",
                "description": "搜索结果总数"
            }
        },
        "required": ["results", "total_count"]
    }
)

@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """
    列出可用的工具
    """
    return ListToolsResult(
        tools=[
            search_patents_tool
        ]
    )

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> Any:
    """
    处理工具调用
    """
    if name == "search_patents":
        try:
            # 提取参数
            keywords = arguments.get("keywords", "")
            page_size = arguments.get("page_size", 10)
            page = arguments.get("page", 0)
            sort = arguments.get("sort", "relevance")
            
            if not keywords:
                return CallToolResult(
                    content=[TextContent(type="text", text="错误：必须提供搜索关键词")]
                )
            
            # 执行搜索
            results = await crawler.search_patents(keywords, page_size, page, sort)
            total_num_results = results["total_num_results"]
            
            # 构建结构化响应数据
            structured_output = {
                "results": results["results"],
                "total_count": total_num_results
            }
            
            import jsonschema
            jsonschema.validate(instance=structured_output, schema=search_patents_tool.outputSchema)

            return structured_output
            
        except Exception as e:
            error_msg = f"搜索专利时发生错误: {str(e)}"
            logger.error(error_msg)
            return CallToolResult(
                content=[TextContent(type="text", text=error_msg)],
                isError=True
            )
    else:
        return CallToolResult(
            content=[TextContent(type="text", text=f"未知工具: {name}")],
            isError=True
        )

async def run_stdio():
    """运行 stdio 传输"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )