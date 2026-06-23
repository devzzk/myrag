"""
myrag Streamlit 前端应用
"""
import sys
from pathlib import Path
import streamlit as st
import traceback

# 添加项目根目录到路径
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from src.pipeline import create_pipeline, RAGPipeline

# 设置页面配置
st.set_page_config(
    page_title="myrag - 个人知识库",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 页面标题
st.title("📚 myrag - 个人知识库")
st.markdown("---")

# 初始化会话状态
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False  # 强制关闭演示模式

if "pipeline" not in st.session_state:
    try:
        with st.spinner("正在初始化系统..."):
            st.session_state.pipeline = create_pipeline(demo_mode=False)  # 强制使用正常模式
        st.session_state.pipeline_initialized = True
        st.success("✅ 系统初始化成功！")
    except Exception as e:
        st.error(f"❌ 系统初始化失败: {e}")
        st.session_state.pipeline_initialized = False

if "messages" not in st.session_state:
    st.session_state.messages = []

# 侧边栏
with st.sidebar:
    st.title("⚙️ 系统管理")
    st.markdown("---")
    
    # 显示当前模式
    st.info("🚀 当前运行在正常模式")
    
    st.markdown("---")
    
    # 知识库统计
    if st.session_state.pipeline_initialized:
        try:
            stats = st.session_state.pipeline.get_knowledge_stats()
            st.subheader("📊 知识库状态")
            col1, col2 = st.columns(2)
            col1.metric("文档数", stats["document_count"])
            col2.metric("内容块", stats["chunk_count"])
        except Exception as e:
            st.error(f"获取统计信息失败: {e}")
    
    st.markdown("---")
    
    # 文档管理
    st.subheader("📁 文档管理")
    
    # 上传文档
    uploaded_files = st.file_uploader(
        "上传 PDF 文档",
        type=["pdf"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("🚀 导入文档", type="primary"):
            try:
                with st.spinner("正在保存并处理文档..."):
                    # 保存上传的文件
                    pdf_dir = st.session_state.pipeline.config.pdf_dir
                    saved_count = 0
                    
                    for uploaded_file in uploaded_files:
                        save_path = pdf_dir / uploaded_file.name
                        with open(save_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        saved_count += 1
                        st.success(f"✅ 已保存: {uploaded_file.name}")
                    
                    if saved_count > 0:
                        # 执行处理流程
                        st.info(f"📄 正在处理 {saved_count} 个文档...")
                        
                        # 使用简单解析器
                        success = st.session_state.pipeline.process_all(use_simple_parser=True)
                        
                        if success:
                            st.success("🎉 文档处理完成！")
                            st.balloons()
                            # 刷新页面
                            st.rerun()
                        else:
                            st.warning("⚠️ 文档处理完成，但可能没有文档被解析")
            except Exception as e:
                st.error(f"❌ 导入失败: {e}")
                with st.expander("查看详细错误"):
                    st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # 重建知识库选项
    rebuild_mode = st.radio(
        "重建模式",
        ["增量重建", "完全清理并重建"],
        horizontal=True,
        help="完全清理会删除旧的向量库，重新构建"
    )
    
    if st.button("🔄 重建知识库"):
        try:
            with st.spinner("正在重建知识库..."):
                if rebuild_mode == "完全清理并重建":
                    # 删除旧的向量库
                    vector_db_dir = st.session_state.pipeline.config.vector_db_dir
                    import shutil
                    if vector_db_dir.exists():
                        shutil.rmtree(vector_db_dir)
                    st.info("已清理旧的向量库")
                
                success = st.session_state.pipeline.process_all(use_simple_parser=True)
                if success:
                    st.success("✅ 知识库重建完成！")
                    st.rerun()
                else:
                    st.warning("⚠️ 重建完成，但可能没有文档")
        except Exception as e:
            st.error(f"❌ 重建失败: {e}")
            with st.expander("查看详细错误"):
                st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # 清空对话
    if st.button("🗑️ 清空对话"):
        st.session_state.messages = []
        st.rerun()

# 主界面 - 问答区域
st.subheader("💬 智能问答")

# 欢迎消息
if not st.session_state.messages:
    st.info("""
        👋 欢迎使用 myrag 个人知识库系统！
        
        **当前模式**：正常模式（需要 API Key）
        
        **使用步骤**：
        1. 在左侧侧边栏上传 PDF 文档
        2. 点击「导入文档」处理文件
        3. 在下方输入框中提问！
    """)

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # 显示引用
        if message.get("references"):
            with st.expander("📚 引用来源"):
                for ref in message["references"]:
                    st.write(f"• {ref}")

# 用户输入
if prompt := st.chat_input("请输入您的问题..."):
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 生成回答
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 正在思考...")
        
        try:
            # 查询 RAG
            result = st.session_state.pipeline.query(prompt, top_k=5)
            
            # 显示回答
            answer = result.get("answer", "")
            message_placeholder.markdown(answer)
            
            # 显示引用
            if result.get("references"):
                with st.expander("📚 引用来源"):
                    for ref in result["references"]:
                        st.write(f"• {ref}")
            
            # 保存到历史
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "references": result.get("references", [])
            })
            
        except Exception as e:
            error_msg = f"❌ 出错了: {str(e)}"
            message_placeholder.error(error_msg)
            
            with st.expander("查看详细错误"):
                st.code(traceback.format_exc())
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg,
                "references": []
            })

# 页脚
st.markdown("---")
st.caption("myrag - 个人 RAG 知识库系统 | 阶段一 MVP")
