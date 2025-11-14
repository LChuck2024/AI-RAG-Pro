import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 检查 NumPy 版本，避免与 llama-index 的 OpenAILike 冲突
def _check_numpy_version():
    """检查 NumPy 版本，如果版本过高则提示用户"""
    try:
        import numpy as np
        numpy_version = np.__version__
        # 检查是否是 2.0 或更高版本
        major_version = int(numpy_version.split('.')[0])
        if major_version >= 2:
            logging.warning(
                f"检测到 NumPy {numpy_version}，可能与 llama-index 的 OpenAILike 冲突。"
                f"建议降级: pip install 'numpy<2'"
            )
            return False
        return True
    except ImportError:
        # NumPy 未安装，不影响
        return True
    except Exception:
        # 版本检查失败，不影响主流程
        return True

# 在模块加载时检查 NumPy 版本
_check_numpy_version()

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
    Settings,
    PromptTemplate,
)
try:
    from llama_index.embeddings.dashscope import (
        DashScopeEmbedding,
        DashScopeTextEmbeddingModels,
    )
except ModuleNotFoundError:
    DashScopeEmbedding = None
    DashScopeTextEmbeddingModels = None

# 尝试导入 Chroma 向量存储
try:
    import chromadb
    from llama_index.vector_stores.chroma import ChromaVectorStore
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    chromadb = None
    ChromaVectorStore = None

from llama_index.llms.openai import OpenAI

# 延迟导入 OpenAILike，避免 NumPy 版本冲突
def _get_openai_like():
    """
    延迟导入 OpenAILike，避免导入时的依赖冲突
    
    Returns:
        OpenAILike 类或 None（如果导入失败）
    """
    try:
        from llama_index.llms.openai_like import OpenAILike
        return OpenAILike
    except ImportError as e:
        error_detail = str(e)
        # 检查是否是 NumPy 版本问题
        if "numpy" in error_detail.lower() or "numpy" in str(type(e)).lower():
            logging.error(f"OpenAILike 导入失败（NumPy 版本冲突）: {e}")
            logging.error("解决方案: pip install 'numpy<2'")
        else:
            logging.warning(f"无法导入 OpenAILike: {e}")
        return None
    except (ModuleNotFoundError, RuntimeError) as e:
        logging.warning(f"无法导入 OpenAILike: {e}")
        return None
    except Exception as e:
        # 捕获其他可能的错误（如 NumPy 版本冲突导致的运行时错误）
        error_detail = str(e)
        if "numpy" in error_detail.lower():
            logging.error(f"OpenAILike 导入失败（可能是 NumPy 版本冲突）: {e}")
            logging.error("解决方案: pip install 'numpy<2'")
        else:
            logging.warning(f"无法导入 OpenAILike（未知错误）: {e}")
        return None
from src.feedback import FeedbackStore
from config.load_key import load_config, get_api_key, get_model_config, get_available_llm, load_key
try:
    from prompt import get_industry_assistant_prompt
except ImportError:
    get_industry_assistant_prompt = None

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class RAGManager:
    def __init__(self, 
                 knowledge_space_dir: str = None,
                 intent_space_dir: str = None,
                 persist_dir_knowledge: str = None,
                 persist_dir_intent: str = None,
                 embed_model_name: str = None,
                 llm_model_name: str = None):
        """
        初始化RAG管理器，配置模型和路径。
        如果参数为None，则从配置文件读取。
        """
        # 加载配置
        config = load_config()
        rag_config = config.get("rag", {})
        
        # 使用配置文件的默认值或传入的参数
        self.knowledge_space_dir = knowledge_space_dir or rag_config.get("knowledge_space_dir", "./rag_source/knowledge_space")
        self.intent_space_dir = intent_space_dir or rag_config.get("intent_space_dir", "./rag_source/intent_space")
        self.persist_dir_knowledge = persist_dir_knowledge or rag_config.get("persist_dir_knowledge", "./data/storage/knowledge_space")
        self.persist_dir_intent = persist_dir_intent or rag_config.get("persist_dir_intent", "./data/storage/intent_space")
        
        # Chroma 数据库路径（如果使用 Chroma）
        self.chroma_db_path = rag_config.get("chroma_db_path", "./data/chroma_db")
        self.use_chroma = CHROMA_AVAILABLE and rag_config.get("use_chroma", True)  # 默认使用 Chroma
        
        # 确保必要的目录存在
        os.makedirs(self.knowledge_space_dir, exist_ok=True)
        os.makedirs(self.intent_space_dir, exist_ok=True)
        # 注意：persist_dir_knowledge 和 persist_dir_intent 已废弃，不再创建目录
        # 系统现在仅使用 Chroma 向量存储
        
        # 初始化 Chroma 客户端（系统要求使用向量存储）
        self.chroma_client = None
        if self.use_chroma and CHROMA_AVAILABLE:
            try:
                os.makedirs(self.chroma_db_path, exist_ok=True)
                self.chroma_client = chromadb.PersistentClient(
                    path=self.chroma_db_path,
                    settings=chromadb.Settings(anonymized_telemetry=False)
                )
                logging.info(f"✅ Chroma 向量数据库已初始化: {self.chroma_db_path}")
            except Exception as e:
                error_msg = f"Chroma 初始化失败: {e}。系统要求使用向量存储，请检查配置或安装 chromadb"
                logging.error(error_msg, exc_info=True)
                raise RuntimeError(error_msg)
        elif not CHROMA_AVAILABLE:
            error_msg = "Chroma 未安装。系统要求使用向量存储，请安装: pip install chromadb"
            logging.error(error_msg)
            raise RuntimeError(error_msg)
        
        # 初始化错误信息存储（必须在 LLM 初始化之前）
        self.llm_error_msg = None  # 存储 LLM 初始化错误信息
        self.embed_error_msg = None  # 存储嵌入模型初始化错误信息
        
        # 配置全局的LLM和Embedding模型
        # 从配置文件获取可用的LLM
        available_llm = get_available_llm()
        if available_llm:
            model_config = get_model_config(available_llm)
            if model_config:
                api_key = get_api_key(model_config["api_key_env"])
                if api_key:
                    base_url = model_config["base_url"]
                    model_name = model_config["model_name"]
                    # 检查是否是 OpenAI 官方 API
                    is_openai_official = "api.openai.com" in base_url.lower()
                    
                    # 如果不是 OpenAI 官方 API，必须使用 OpenAILike
                    if not is_openai_official:
                        OpenAILike = _get_openai_like()
                        if OpenAILike is None:
                            error_msg = f"无法使用 {available_llm} API：需要 OpenAILike 支持自定义 base_url，但导入失败（可能是 NumPy 版本冲突）。请降级 NumPy: pip install 'numpy<2'"
                            logging.error(error_msg)
                            self.llm_error_msg = error_msg
                            self.llm = None
                        else:
                            try:
                                self.llm = OpenAILike(
                                    model=model_name,
                                    api_base=base_url,
                                    api_key=api_key,
                                    is_chat_model=True,
                                    temperature=model_config.get("temperature", 0.1),
                                )
                                logging.info(f"使用 {available_llm} API 作为 LLM (OpenAILike)")
                            except Exception as e:
                                error_msg = f"OpenAILike 初始化失败: {e}"
                                logging.error(error_msg)
                                self.llm_error_msg = error_msg
                                self.llm = None
                    else:
                        # OpenAI 官方 API，可以使用 OpenAI 类
                        try:
                            self.llm = OpenAI(
                                model=model_name,
                                api_key=api_key,
                                base_url=base_url,
                                temperature=model_config.get("temperature", 0.1),
                            )
                            logging.info(f"使用 {available_llm} API 作为 LLM (OpenAI)")
                        except Exception as e:
                            error_msg = f"OpenAI 初始化失败: {e}"
                            logging.error(error_msg)
                            self.llm_error_msg = error_msg
                            self.llm = None
                else:
                    error_msg = f"未找到 {available_llm} 的API密钥"
                    logging.warning(error_msg)
                    self.llm_error_msg = error_msg
                    self.llm = None
            else:
                error_msg = f"未找到 {available_llm} 的配置"
                logging.warning(error_msg)
                self.llm_error_msg = error_msg
                self.llm = None
        else:
            error_msg = "未找到可用的LLM配置，请检查配置文件"
            logging.warning(error_msg)
            self.llm_error_msg = error_msg
            self.llm = None
        
        # 如果仍然没有LLM，尝试使用默认配置（DashScope/Qwen）
        if self.llm is None:
            OpenAILike = _get_openai_like()
            if OpenAILike is not None:
                dashscope_key = get_api_key("DASHSCOPE_API_KEY")
                if dashscope_key:
                    try:
                        self.llm = OpenAILike(
                            model=llm_model_name or "qwen-plus",
                            api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                            api_key=dashscope_key,
                            is_chat_model=True,
                        )
                        logging.info("使用 DashScope (Qwen) API 作为 LLM (fallback, OpenAILike)")
                    except Exception as e:
                        error_msg = f"OpenAILike 初始化失败: {e}"
                        logging.warning(error_msg)
                        self.llm_error_msg = error_msg
                        self.llm = None
                else:
                    error_msg = "未找到 DashScope API Key，无法使用 fallback LLM"
                    logging.warning(error_msg)
                    self.llm_error_msg = error_msg
                    self.llm = None
            else:
                # 如果 OpenAILike 不可用，无法使用非 OpenAI API
                error_msg = "OpenAILike 不可用，无法使用 DeepSeek 或千问 API。请运行: pip install 'numpy<2'"
                logging.warning(error_msg)
                self.llm_error_msg = error_msg
                self.llm = None
        
        # 配置Embedding模型
        self.embed_model = None
        embedding_config = config.get("embedding", {})
        embed_provider = embedding_config.get("provider", "dashscope")
        
        if embed_provider == "dashscope":
            if DashScopeEmbedding is None or DashScopeTextEmbeddingModels is None:
                error_msg = "未安装 llama-index-embeddings-dashscope 模块"
                logging.error(error_msg)
                self.embed_error_msg = f"{error_msg}。请运行: pip install llama-index-embeddings-dashscope"
            else:
                try:
                    # 确保API Key已加载到环境变量
                    load_key()
                    embed_api_key = get_api_key(embedding_config.get("api_key_env", "DASHSCOPE_API_KEY"))
                    if embed_api_key:
                        # 确保环境变量已设置
                        os.environ["DASHSCOPE_API_KEY"] = embed_api_key
                        # 初始化DashScopeEmbedding，显式传递api_key参数
                        try:
                            self.embed_model = DashScopeEmbedding(
                                model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2,
                                api_key=embed_api_key
                            )
                            logging.info("✅ DashScope Embedding 模型初始化成功")
                        except Exception as init_e:
                            error_msg = f"DashScopeEmbedding 初始化失败: {str(init_e)}"
                            logging.error(error_msg, exc_info=True)
                            self.embed_error_msg = error_msg
                            self.embed_model = None
                    else:
                        error_msg = "未找到 DashScope API Key"
                        logging.warning(error_msg)
                        self.embed_error_msg = f"{error_msg}。请检查 config/config.json 中的 DASHSCOPE_API_KEY 配置"
                except Exception as e:
                    error_msg = f"DashScopeEmbedding 初始化异常: {str(e)}"
                    logging.error(error_msg, exc_info=True)
                    self.embed_error_msg = error_msg
        else:
            error_msg = f"不支持的嵌入模型提供商: {embed_provider}"
            logging.warning(error_msg)
            self.embed_error_msg = error_msg
        
        Settings.llm = self.llm
        if self.embed_model is not None:
            Settings.embed_model = self.embed_model
        
        self.knowledge_index = None
        self.intent_index = None
        self.feedback_store = FeedbackStore()
        if self.embed_model is not None:
            try:
                logging.info("开始加载或创建知识空间索引...")
                self.knowledge_index = self._load_or_create_index(
                    self.knowledge_space_dir, 
                    persist_dir=self.persist_dir_knowledge,
                    collection_name="knowledge_space"
                )
                logging.info("✅ 知识空间索引加载完成")
                logging.info("开始加载或创建意图空间索引...")
                self.intent_index = self._load_or_create_index(
                    self.intent_space_dir,
                    persist_dir=self.persist_dir_intent,
                    collection_name="intent_space"
                )
                logging.info("✅ 意图空间索引加载完成")
                self.refresh_intent_index()
            except Exception as e:
                error_msg = f"索引加载失败: {str(e)}"
                logging.error(error_msg, exc_info=True)
                self.embed_error_msg = f"{self.embed_error_msg or ''}\n索引加载失败: {str(e)}"
                self.knowledge_index = None
                self.intent_index = None
        else:
            if self.embed_error_msg:
                logging.warning(f"未检测到可用的嵌入模型: {self.embed_error_msg}")
            else:
                logging.warning("未检测到可用的嵌入模型，RAG索引已禁用。启用RAG需安装 dashscope 集成包。")

    def _load_or_create_index(self, documents_dir: str, persist_dir: str = None, collection_name: str = None) -> VectorStoreIndex:
        """
        加载或创建向量索引。
        系统要求使用 Chroma 向量数据库作为存储方式。
        
        Args:
            documents_dir: 文档目录
            persist_dir: 持久化目录（已废弃，仅用于兼容旧接口）
            collection_name: Chroma collection 名称（必需）
        
        Returns:
            VectorStoreIndex: 向量索引对象
        
        Raises:
            RuntimeError: 如果 Chroma 不可用或初始化失败
        """
        # 系统要求使用 Chroma 向量数据库
        if not self.use_chroma or self.chroma_client is None:
            raise RuntimeError("系统要求使用 Chroma 向量存储，但 Chroma 未正确初始化。请检查配置。")
        
        if not collection_name:
            raise ValueError("collection_name 参数是必需的")
        
        return self._load_or_create_index_chroma(documents_dir, collection_name)
    
    def _load_or_create_index_chroma(self, documents_dir: str, collection_name: str) -> VectorStoreIndex:
        """使用 Chroma 向量数据库加载或创建索引"""
        try:
            # 获取或创建 Chroma collection
            try:
                chroma_collection = self.chroma_client.get_collection(name=collection_name)
                logging.info(f"使用现有 Chroma collection: {collection_name} (已有 {chroma_collection.count()} 条数据)")
            except Exception:
                # Collection 不存在，创建新的（Chroma会抛出异常，具体类型可能因版本而异）
                chroma_collection = self.chroma_client.create_collection(name=collection_name)
                logging.info(f"创建新 Chroma collection: {collection_name}")
            
            # 创建 ChromaVectorStore
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            
            # 创建存储上下文
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            # 如果 collection 已有数据，从向量存储加载索引
            if chroma_collection.count() > 0:
                logging.info(f"从 Chroma collection '{collection_name}' 加载索引...")
                index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    embed_model=self.embed_model
                )
                logging.info("索引加载完成（Chroma）。")
                return index
            
            # 创建新索引
            if not os.path.exists(documents_dir) or not os.listdir(documents_dir):
                logging.warning(f"文档目录 '{documents_dir}' 为空或不存在，将创建一个空的索引。")
                from llama_index.core.schema import Document
                documents = [Document(text="这是一个空的占位文档。")]
            else:
                logging.info(f"从 '{documents_dir}' 加载文档并创建新索引（Chroma）...")
                reader = SimpleDirectoryReader(documents_dir)
                documents = reader.load_data()
            
            # 使用 Chroma 向量存储创建索引
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                embed_model=self.embed_model
            )
            logging.info(f"创建新索引完成，已保存到 Chroma collection '{collection_name}'")
            return index
            
        except Exception as e:
            error_msg = f"Chroma 索引操作失败: {e}。系统要求使用向量存储，请检查 Chroma 数据库状态。"
            logging.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg)
    
    def _load_or_create_index_json(self, documents_dir: str, persist_dir: str) -> VectorStoreIndex:
        """
        使用 JSON 文件存储加载或创建索引（已废弃）
        
        注意：此方法已废弃，系统现在仅使用 Chroma 向量存储。
        保留此方法仅用于兼容性，不会被调用。
        """
        # 检查持久化目录是否完整（需要包含关键文件）
        persist_dir_exists = os.path.exists(persist_dir)
        docstore_file = os.path.join(persist_dir, "docstore.json")
        index_file = os.path.join(persist_dir, "index_store.json")
        persist_complete = persist_dir_exists and os.path.exists(docstore_file) and os.path.exists(index_file)
        
        if persist_complete:
            try:
                logging.info(f"从 '{persist_dir}' 加载索引（JSON）...")
                storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
                index = load_index_from_storage(storage_context, embed_model=self.embed_model)
                logging.info("索引加载完成（JSON）。")
                return index
            except Exception as e:
                logging.warning(f"从持久化目录加载索引失败: {e}，将重新创建索引")
                # 如果加载失败，删除不完整的持久化目录
                import shutil
                if os.path.exists(persist_dir):
                    try:
                        shutil.rmtree(persist_dir)
                        logging.info(f"已删除不完整的持久化目录: {persist_dir}")
                    except Exception as rm_e:
                        logging.warning(f"删除持久化目录失败: {rm_e}")
        
        # 创建新索引
        if not os.path.exists(documents_dir) or not os.listdir(documents_dir):
            logging.warning(f"文档目录 '{documents_dir}' 为空或不存在，将创建一个空的索引。")
            # 创建一个虚拟的空文档来初始化一个空索引
            from llama_index.core.schema import Document
            documents = [Document(text="这是一个空的占位文档。")]
        else:
            logging.info(f"从 '{documents_dir}' 加载文档并创建新索引（JSON）...")
            reader = SimpleDirectoryReader(documents_dir)
            documents = reader.load_data()
        
        index = VectorStoreIndex.from_documents(documents)
        logging.info(f"创建新索引完成，持久化到 '{persist_dir}'（JSON）...")
        # 确保持久化目录存在
        os.makedirs(persist_dir, exist_ok=True)
        index.storage_context.persist(persist_dir=persist_dir)
        logging.info("索引持久化完成（JSON）。")
        return index

    def _get_industry_prompt_template(self, show_thinking: bool = False) -> PromptTemplate:
        """获取行业助手的提示词模板"""
        if get_industry_assistant_prompt is not None:
            try:
                industry_prompt = get_industry_assistant_prompt()
                # 将行业助手提示词与LlamaIndex的默认模板格式结合
                thinking_instruction = ""
                if show_thinking:
                    thinking_instruction = """

## 思考过程要求
在回答之前，请先展示你的思考过程，包括：
1. 如何理解用户的问题
2. 如何从参考信息中提取关键信息
3. 如何组织答案的逻辑结构

请按以下格式输出：

**思考过程：**
[你的思考过程]

**回答：**
[你的最终回答]"""
                
                prompt_template_str = f"""{industry_prompt}

## 参考信息
以下是检索到的相关信息：
---------------------
{{context_str}}
---------------------

## 用户问题
{{query_str}}
{thinking_instruction}

## 回答要求
请基于以上参考信息和行业助手的原则，为用户提供专业、准确、有价值的回答。
回答："""
                return PromptTemplate(prompt_template_str)
            except Exception as e:
                logging.warning(f"加载行业助手提示词失败，使用默认模板: {e}")
        
        # 如果加载失败，使用默认模板
        thinking_instruction = ""
        if show_thinking:
            thinking_instruction = "\n\n在回答前，请先展示思考过程，格式：\n**思考过程：**\n[思考内容]\n\n**回答：**\n[回答内容]"
        
        default_template = f"""你是行业助手，由凡梦文化创建的智能问答系统。

请基于以下参考信息回答问题：
---------------------
{{context_str}}
---------------------

问题：{{query_str}}{thinking_instruction}
回答："""
        return PromptTemplate(default_template)
    
    def _get_query_engine(self, index, index_name: str, streaming=True, 
                         similarity_top_k: int = 3, show_thinking: bool = False):
        """
        获取查询引擎的公共方法
        
        Args:
            index: 向量索引对象
            index_name: 索引名称（用于错误提示）
            streaming: 是否使用流式输出
            similarity_top_k: 检索的文档数量
            show_thinking: 是否显示思考过程
        
        Returns:
            配置好的查询引擎
        
        Raises:
            RuntimeError: 当索引或LLM未初始化时
        """
        if index is None:
            error_detail = self.embed_error_msg or "嵌入模型未初始化或索引加载失败"
            raise RuntimeError(f"RAG未启用或嵌入不可用，无法获取{index_name}引擎。原因：{error_detail}")
        
        if self.llm is None:
            error_msg = "LLM未初始化。"
            if hasattr(self, 'llm_error_msg') and self.llm_error_msg:
                error_msg += f" {self.llm_error_msg}"
            elif hasattr(self, 'embed_error_msg') and "OpenAILike" in str(self.embed_error_msg or ""):
                error_msg += " 无法使用非 OpenAI API（如 DeepSeek），因为 OpenAILike 导入失败（可能是 NumPy 版本冲突）。请运行: pip install 'numpy<2'"
            else:
                error_msg += " 请检查配置文件中的 LLM 配置和 API Key。"
            raise RuntimeError(error_msg)
        
        query_engine = index.as_query_engine(
            streaming=streaming, similarity_top_k=similarity_top_k
        )
        
        # 应用行业助手提示词模板
        prompt_template = self._get_industry_prompt_template(show_thinking=show_thinking)
        query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": prompt_template}
        )
        
        return query_engine
    
    def get_knowledge_query_engine(self, streaming=True, similarity_top_k: int = 3, show_thinking: bool = False):
        """获取知识空间的查询引擎"""
        logging.info("获取知识空间查询引擎。")
        return self._get_query_engine(
            self.knowledge_index, 
            "知识空间", 
            streaming, 
            similarity_top_k, 
            show_thinking
        )
        
    def get_intent_query_engine(self, streaming=True, similarity_top_k: int = 1, show_thinking: bool = False):
        """获取意图空间的查询引擎"""
        logging.info("获取意图空间查询引擎。")
        return self._get_query_engine(
            self.intent_index, 
            "意图空间", 
            streaming, 
            similarity_top_k, 
            show_thinking
        )

    def refresh_intent_index(self) -> None:
        """刷新意图空间索引"""
        from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
        if self.embed_model is None:
            logging.warning("嵌入不可用，跳过意图索引刷新")
            return
        
        docs = []
        if os.path.exists(self.intent_space_dir) and os.listdir(self.intent_space_dir):
            reader = SimpleDirectoryReader(self.intent_space_dir)
            docs.extend(reader.load_data())
        docs.extend(self.feedback_store.get_positive_documents())
        if len(docs) == 0:
            from llama_index.core.schema import Document
            docs = [Document(text="")]
        
        # 使用 Chroma 向量存储（系统要求）
        if not self.use_chroma or self.chroma_client is None:
            raise RuntimeError("系统要求使用 Chroma 向量存储，但 Chroma 未正确初始化。请检查配置。")
        
        try:
            # 删除现有 collection（如果存在）
            try:
                self.chroma_client.delete_collection(name="intent_space")
                logging.info("已删除现有 intent_space collection")
            except Exception:
                # Collection 不存在，继续创建
                pass
            
            # 创建新的 collection
            chroma_collection = self.chroma_client.create_collection(name="intent_space")
            
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            self.intent_index = VectorStoreIndex.from_documents(
                docs,
                storage_context=storage_context,
                embed_model=self.embed_model
            )
            logging.info("意图空间索引已刷新（Chroma）")
        except Exception as e:
            error_msg = f"Chroma 刷新失败: {e}。系统要求使用向量存储，请检查 Chroma 数据库状态。"
            logging.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg)

    def refresh_knowledge_index(self) -> None:
        """刷新知识空间索引"""
        from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
        if self.embed_model is None:
            logging.warning("嵌入不可用，跳过知识索引刷新")
            return
        
        docs = []
        if os.path.exists(self.knowledge_space_dir) and os.listdir(self.knowledge_space_dir):
            reader = SimpleDirectoryReader(self.knowledge_space_dir)
            docs.extend(reader.load_data())
        if len(docs) == 0:
            from llama_index.core.schema import Document
            docs = [Document(text="")]
        
        # 使用 Chroma 向量存储（系统要求）
        if not self.use_chroma or self.chroma_client is None:
            raise RuntimeError("系统要求使用 Chroma 向量存储，但 Chroma 未正确初始化。请检查配置。")
        
        try:
            # 删除现有 collection（如果存在）
            try:
                self.chroma_client.delete_collection(name="knowledge_space")
                logging.info("已删除现有 knowledge_space collection")
            except Exception:
                # Collection 不存在，继续创建
                pass
            
            # 创建新的 collection
            chroma_collection = self.chroma_client.create_collection(name="knowledge_space")
            
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            
            self.knowledge_index = VectorStoreIndex.from_documents(
                docs,
                storage_context=storage_context,
                embed_model=self.embed_model
            )
            logging.info("知识空间索引已刷新（Chroma）")
        except Exception as e:
            error_msg = f"Chroma 刷新失败: {e}。系统要求使用向量存储，请检查 Chroma 数据库状态。"
            logging.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg)

