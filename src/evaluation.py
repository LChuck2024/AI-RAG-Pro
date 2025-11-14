"""
评估指标模块
用于计算和展示问答系统的评估指标
"""
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class EvaluationMetrics:
    """评估指标数据类"""
    # 检索质量指标
    retrieval_count: int = 0  # 检索到的文档数量
    max_similarity_score: float = 0.0  # 最高相似度分数
    avg_similarity_score: float = 0.0  # 平均相似度分数
    min_similarity_score: float = 0.0  # 最低相似度分数
    
    # 回答质量指标
    answer_length: int = 0  # 回答长度（字符数）
    answer_word_count: int = 0  # 回答词数
    
    # 检索策略指标
    used_intent_space: bool = False  # 是否使用了意图空间快速匹配
    intent_score: float = 0.0  # 意图空间相似度分数
    
    # 来源信息
    source_count: int = 0  # 来源数量
    has_sources: bool = False  # 是否有来源信息
    
    # 新增评估指标
    confidence: float = 0.0  # 置信度（0-1）
    precision: float = 0.0  # 精确率（0-1）
    recall: float = 0.0  # 召回率（0-1）
    f1_score: float = 0.0  # F1分数（0-1）


def calculate_metrics(
    answer: str,
    src_nodes: List[Any],
    used_intent_space: bool = False,
    intent_score: float = 0.0,
    similarity_threshold: float = 0.7  # 相似度阈值，用于计算精确率和召回率
) -> EvaluationMetrics:
    """
    计算评估指标
    
    Args:
        answer: 生成的回答
        src_nodes: 检索到的源节点列表
        used_intent_space: 是否使用了意图空间
        intent_score: 意图空间相似度分数
        similarity_threshold: 相似度阈值，用于判断文档是否相关（默认0.7）
    
    Returns:
        EvaluationMetrics: 评估指标对象
    """
    # 计算检索质量指标
    retrieval_count = len(src_nodes)
    similarity_scores = []
    
    for node in src_nodes:
        score = getattr(node, "score", None)
        if score is not None:
            similarity_scores.append(float(score))
    
    if similarity_scores:
        max_similarity_score = max(similarity_scores)
        avg_similarity_score = sum(similarity_scores) / len(similarity_scores)
        min_similarity_score = min(similarity_scores)
    else:
        max_similarity_score = 0.0
        avg_similarity_score = 0.0
        min_similarity_score = 0.0
    
    # 计算回答质量指标
    answer_length = len(answer)
    answer_word_count = len(answer.split())
    
    # 来源信息
    source_count = retrieval_count
    has_sources = retrieval_count > 0
    
    # 计算置信度（Confidence）
    # 如果使用了意图空间且意图分数较高，使用意图分数；否则使用最高相似度分数
    # 如果都没有，基于回答质量估算（通用助手模式）
    if used_intent_space and intent_score > 0:
        confidence = min(intent_score, 1.0)  # 确保不超过1.0
    elif max_similarity_score > 0:
        confidence = min(max_similarity_score, 1.0)  # 确保不超过1.0
    else:
        # 通用助手模式：基于回答质量估算置信度
        # 考虑因素：回答长度、完整性（是否有实际内容）
        if answer_length > 0:
            # 基于回答长度和完整性估算，范围在0.5-0.8之间
            # 回答越长且越完整，置信度越高
            length_factor = min(answer_length / 500.0, 1.0)  # 500字符为基准
            completeness_factor = 1.0 if answer_word_count > 10 else 0.7  # 至少10个词才算完整
            confidence = 0.5 + 0.3 * length_factor * completeness_factor
        else:
            confidence = 0.0
    
    # 计算精确率（Precision）
    # 精确率 = 超过阈值的相关文档数 / 总检索文档数
    if retrieval_count > 0 and similarity_scores:
        relevant_docs = sum(1 for score in similarity_scores if score >= similarity_threshold)
        precision = relevant_docs / retrieval_count
    else:
        precision = 0.0
    
    # 计算召回率（Recall）
    # 召回率 = 检索到的相关文档数 / 所有相关文档数
    # 由于不知道总共有多少相关文档，我们使用以下策略：
    # 1. 如果使用了意图空间且分数高，认为召回率高
    # 2. 否则基于平均相似度估算：如果平均相似度高，认为召回率较高
    if used_intent_space and intent_score >= 0.8:
        # 意图匹配成功，认为召回率较高
        recall = min(intent_score, 1.0)
    elif avg_similarity_score > 0:
        # 基于平均相似度估算召回率
        # 如果平均相似度高，说明检索到的文档质量好，召回率可能较高
        # 使用平均相似度作为召回率的估算值
        recall = min(avg_similarity_score, 1.0)
    else:
        recall = 0.0
    
    # 计算F1分数（F1 Score）
    # F1 = 2 * (Precision * Recall) / (Precision + Recall)
    if precision + recall > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0
    
    return EvaluationMetrics(
        retrieval_count=retrieval_count,
        max_similarity_score=max_similarity_score,
        avg_similarity_score=avg_similarity_score,
        min_similarity_score=min_similarity_score,
        answer_length=answer_length,
        answer_word_count=answer_word_count,
        used_intent_space=used_intent_space,
        intent_score=intent_score,
        source_count=source_count,
        has_sources=has_sources,
        confidence=confidence,
        precision=precision,
        recall=recall,
        f1_score=f1_score
    )


def format_metrics_display(metrics: EvaluationMetrics, rag_enabled: bool = True) -> Dict[str, Any]:
    """
    格式化评估指标用于展示
    
    Args:
        metrics: 评估指标对象
        rag_enabled: 是否启用了RAG
    
    Returns:
        Dict: 格式化后的指标字典
    """
    if not rag_enabled:
        return {
            "回答长度": f"{metrics.answer_length} 字符",
            "回答词数": f"{metrics.answer_word_count} 词"
        }
    
    display_metrics = {
        "检索质量": {
            "检索文档数": metrics.retrieval_count,
            "最高相似度": f"{metrics.max_similarity_score:.3f}" if metrics.max_similarity_score > 0 else "N/A",
            "平均相似度": f"{metrics.avg_similarity_score:.3f}" if metrics.avg_similarity_score > 0 else "N/A",
            "最低相似度": f"{metrics.min_similarity_score:.3f}" if metrics.min_similarity_score > 0 else "N/A"
        },
        "回答质量": {
            "回答长度": f"{metrics.answer_length} 字符",
            "回答词数": f"{metrics.answer_word_count} 词"
        },
        "检索策略": {
            "使用意图空间": "✅ 是" if metrics.used_intent_space else "❌ 否",
            "意图相似度": f"{metrics.intent_score:.3f}" if metrics.intent_score > 0 else "N/A"
        },
        "评估指标": {
            "置信度": f"{metrics.confidence:.3f}" if metrics.confidence > 0 else "N/A",
            "精确率": f"{metrics.precision:.3f}" if metrics.precision > 0 else "N/A",
            "召回率": f"{metrics.recall:.3f}" if metrics.recall > 0 else "N/A",
            "F1分数": f"{metrics.f1_score:.3f}" if metrics.f1_score > 0 else "N/A"
        }
    }
    
    return display_metrics

