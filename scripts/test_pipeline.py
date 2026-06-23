"""
测试 RAG 流水线
"""
import sys
from pathlib import Path

# 添加项目根目录
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from src.pipeline import create_pipeline


def test_basic_functionality():
    """
    测试基本功能
    """
    print("=" * 60)
    print("myrag - 基础功能测试")
    print("=" * 60)
    
    # 创建流水线
    print("\n1. 创建 RAG 流水线...")
    pipeline = create_pipeline()
    print("✅ 流水线创建成功")
    
    # 显示统计
    print("\n2. 知识库状态:")
    stats = pipeline.get_knowledge_stats()
    print(f"   文档数: {stats['document_count']}")
    print(f"   块数: {stats['chunk_count']}")
    
    # 如果有知识库，测试查询
    if stats['chunk_count'] > 0:
        print("\n3. 测试查询...")
        test_question = "请介绍一下知识库中的内容"
        print(f"   问题: {test_question}")
        
        result = pipeline.query(test_question, top_k=3)
        print(f"   回答: {result['answer']}")
        
        if result['references']:
            print("   引用:")
            for ref in result['references']:
                print(f"     - {ref}")
        
        print("\n✅ 查询测试完成")
    else:
        print("\nℹ️  知识库为空，请先导入文档")
        print("   可以通过以下方式导入文档:")
        print("   1. 运行 streamlit run app/streamlit_app.py")
        print("   2. 或手动将 PDF 放入 data/stock_data/pdf_reports/")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_basic_functionality()
