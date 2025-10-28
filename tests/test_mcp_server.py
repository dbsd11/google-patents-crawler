#!/usr/bin/env python3
"""
测试 Google Patents Crawler MCP Server

这个脚本用于测试 MCP 服务器的功能，包括：
1. URL 构建功能测试
2. HTML 解析功能测试
3. 完整搜索流程测试
"""

import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_server import GooglePatentsCrawler
from logger import logger

async def test_url_building():
    """测试URL构建功能"""
    print("=" * 50)
    print("测试 URL 构建功能")
    print("=" * 50)
    
    crawler = GooglePatentsCrawler()
    
    # 测试基本搜索
    url1 = crawler.build_search_url("人工智能")
    print(f"基本搜索URL: {url1}")
    
    # 测试分页搜索
    url2 = crawler.build_search_url("机器学习", page_size=20, page=1)
    print(f"分页搜索URL: {url2}")
    
    # 测试排序搜索
    url3 = crawler.build_search_url("深度学习", sort="new")
    print(f"排序搜索URL: {url3}")
    
    # 测试复合参数
    url4 = crawler.build_search_url("智能制造", page_size=15, page=2, sort="new")
    print(f"复合参数URL: {url4}")
    
    print("✅ URL 构建功能测试完成\n")

async def test_html_parsing():
    """测试HTML解析功能"""
    print("=" * 50)
    print("测试 HTML 解析功能")
    print("=" * 50)
    
    crawler = GooglePatentsCrawler()
    
    # 读取示例HTML文件
    html_file_path = os.path.join(os.path.dirname(__file__), "google_search_result.html")
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        print(f"读取HTML文件: {html_file_path}")
        print(f"HTML内容长度: {len(html_content)} 字符")
        
        # 解析专利信息
        patents = crawler.parse_patent_results(html_content)
        
        print(f"解析到 {len(patents)} 个专利结果")
        
        # 显示前3个专利的详细信息
        for i, patent in enumerate(patents[:3], 1):
            print(f"\n【专利 {i}】")
            print(f"标题: {patent.title}")
            print(f"专利号: {patent.grant_number}")
            print(f"发明人: {patent.inventor}")
            print(f"申请人: {patent.assignee}")
            print(f"日期: {patent.dates}")
            print(f"摘要: {patent.abstract[:100]}...")
            if patent.pdf_link:
                print(f"PDF链接: {patent.pdf_link}")
        
        print("✅ HTML 解析功能测试完成\n")
        return len(patents) > 0
        
    except FileNotFoundError:
        print(f"❌ 未找到HTML文件: {html_file_path}")
        return False
    except Exception as e:
        print(f"❌ HTML解析测试失败: {str(e)}")
        return False

async def test_full_search():
    """测试完整搜索流程"""
    print("=" * 50)
    print("测试完整搜索流程")
    print("=" * 50)
    
    crawler = GooglePatentsCrawler()
    
    try:
        # 执行搜索
        print("正在搜索关键词: '人工智能'")
        results = await crawler.search_patents("人工智能", page_size=5, page=0, sort="new")
        
        print(f"搜索完成，找到 {len(results)} 个结果")
        
        # 显示结果
        for i, result in enumerate(results[:2], 1):
            print(f"\n【搜索结果 {i}】")
            print(f"标题: {result['title']}")
            print(f"专利号: {result['grant_number']}")
            print(f"发明人: {result['inventor']}")
            print(f"申请人: {result['assignee']}")
            print(f"日期: {result['dates']}")
            print(f"摘要: {result['abstract'][:100]}...")
        
        print("✅ 完整搜索流程测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 完整搜索测试失败: {str(e)}")
        logger.error(f"搜索测试错误: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始测试 Google Patents Crawler MCP Server")
    print("=" * 60)
    
    # 测试结果统计
    test_results = []
    
    # 1. 测试URL构建
    try:
        await test_url_building()
        test_results.append(("URL构建", True))
    except Exception as e:
        print(f"❌ URL构建测试失败: {str(e)}")
        test_results.append(("URL构建", False))
    
    # 2. 测试HTML解析
    try:
        parse_success = await test_html_parsing()
        test_results.append(("HTML解析", parse_success))
    except Exception as e:
        print(f"❌ HTML解析测试失败: {str(e)}")
        test_results.append(("HTML解析", False))
    
    # 3. 测试完整搜索流程（可选，需要网络连接）
    print("是否要测试完整搜索流程？(需要网络连接和ChromeDriver)")
    print("输入 'y' 继续，其他键跳过:")
    
    # 在自动化测试中，我们跳过需要用户输入的部分
    # user_input = input().strip().lower()
    # if user_input == 'y':
    #     try:
    #         search_success = await test_full_search()
    #         test_results.append(("完整搜索", search_success))
    #     except Exception as e:
    #         print(f"❌ 完整搜索测试失败: {str(e)}")
    #         test_results.append(("完整搜索", False))
    # else:
    #     print("⏭️  跳过完整搜索测试")
    #     test_results.append(("完整搜索", "跳过"))
    
    print("⏭️  跳过完整搜索测试（需要用户交互）")
    test_results.append(("完整搜索", "跳过"))
    
    # 显示测试结果汇总
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    for test_name, result in test_results:
        if result is True:
            status = "✅ 通过"
        elif result is False:
            status = "❌ 失败"
        else:
            status = "⏭️  跳过"
        
        print(f"{test_name:15} : {status}")
    
    # 计算通过率
    passed = sum(1 for _, result in test_results if result is True)
    total = len([r for _, r in test_results if r != "跳过"])
    
    if total > 0:
        pass_rate = (passed / total) * 100
        print(f"\n通过率: {passed}/{total} ({pass_rate:.1f}%)")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    asyncio.run(main())