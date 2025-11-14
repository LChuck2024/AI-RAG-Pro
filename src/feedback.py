import os
import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Iterator
from llama_index.core.schema import Document


class FeedbackStore:
    def __init__(self, db_path: str = "./data/feedback.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self._init_db()
    
    @contextmanager
    def _get_db_connection(self) -> Iterator[sqlite3.Connection]:
        """
        数据库连接上下文管理器
        
        Yields:
            sqlite3.Connection: 数据库连接对象
        
        Example:
            with self._get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(...)
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        # 检查表是否存在
        cur.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='interactions'
        """)
        table_exists = cur.fetchone() is not None
        
        if not table_exists:
            # 创建新表，rating字段允许NULL，created_at不使用DEFAULT（使用Python本地时间）
            cur.execute(
                """
                CREATE TABLE interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    sources TEXT,
                    rating INTEGER,
                    correction TEXT,
                    created_at DATETIME
                )
                """
            )
        else:
            # 表已存在，检查是否需要迁移（rating字段是否为NOT NULL）
            # 获取表结构信息
            cur.execute("PRAGMA table_info(interactions)")
            columns = cur.fetchall()
            rating_not_null = False
            for col in columns:
                if col[1] == 'rating' and col[3] == 1:  # col[3] 是 notnull 标志
                    rating_not_null = True
                    break
            
            # 如果rating字段是NOT NULL，需要迁移
            if rating_not_null:
                logging.info("检测到rating字段为NOT NULL，开始迁移数据库...")
                try:
                    # 创建临时表（不使用DEFAULT CURRENT_TIMESTAMP，使用Python本地时间）
                    cur.execute("""
                        CREATE TABLE interactions_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            question TEXT NOT NULL,
                            answer TEXT NOT NULL,
                            sources TEXT,
                            rating INTEGER,
                            correction TEXT,
                            created_at DATETIME
                        )
                    """)
                    
                    # 复制数据（保持rating值不变，包括NULL）
                    cur.execute("""
                        INSERT INTO interactions_new 
                        (id, question, answer, sources, rating, correction, created_at)
                        SELECT id, question, answer, sources, rating, correction, created_at
                        FROM interactions
                    """)
                    
                    # 删除旧表
                    cur.execute("DROP TABLE interactions")
                    
                    # 重命名新表
                    cur.execute("ALTER TABLE interactions_new RENAME TO interactions")
                    
                    logging.info("数据库迁移完成：rating字段现在允许NULL")
                except Exception as e:
                    logging.error(f"数据库迁移失败: {e}")
                    conn.rollback()
                    raise
        
        conn.commit()
        conn.close()

    def add_interaction(
        self,
        question: str,
        answer: str,
        sources: Optional[str],
        rating: Optional[int] = None,
        correction: Optional[str] = None,
    ) -> int:
        """
        添加问答交互记录
        
        Args:
            question: 用户问题
            answer: 助手回答
            sources: 来源信息
            rating: 评分（None表示无反馈）
            correction: 改进建议
        
        Returns:
            int: 插入的记录ID
        """
        # 使用本地时间（上海时间 UTC+8）
        local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO interactions (question, answer, sources, rating, correction, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (question, answer, sources or "", rating, correction or "", local_time),
            )
            return cur.lastrowid
    
    def add_interaction_without_feedback(
        self,
        question: str,
        answer: str,
        sources: Optional[str] = None,
    ) -> int:
        """
        添加无反馈的问答交互记录（用于统计高频问题）
        
        Args:
            question: 用户问题
            answer: 助手回答
            sources: 来源信息
        
        Returns:
            int: 插入的记录ID
        """
        return self.add_interaction(question, answer, sources, rating=None, correction=None)
    
    def update_interaction_feedback(
        self,
        interaction_id: int,
        rating: int,
        correction: Optional[str] = None,
    ) -> bool:
        """
        更新交互记录的反馈信息
        
        Args:
            interaction_id: 交互记录ID
            rating: 评分
            correction: 改进建议
        
        Returns:
            bool: 是否更新成功
        """
        try:
            with self._get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE interactions SET rating = ?, correction = ? WHERE id = ?",
                    (rating, correction or "", interaction_id),
                )
                return cur.rowcount > 0
        except Exception as e:
            logging.error(f"更新反馈失败: {e}")
            return False

    def get_positive_documents(self, min_rating: int = 1) -> List[Document]:
        """
        获取正面反馈的文档（用于构建意图空间索引）
        
        Args:
            min_rating: 最低评分阈值
        
        Returns:
            List[Document]: 文档列表
        """
        with self._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT question, answer, correction FROM interactions WHERE rating >= ? ORDER BY created_at DESC",
                (min_rating,),
            )
            rows = cur.fetchall()
        
        docs: List[Document] = []
        for q, a, c in rows:
            ans = c if (c is not None and len(c.strip()) > 0) else a
            text = f"Q: {q}\nA: {ans}"
            docs.append(Document(text=text, metadata={"source": "feedback"}))
        return docs
    
    def get_all_feedback(
        self, 
        rating_filter: Optional[int] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[dict]:
        """
        获取所有反馈数据
        
        Args:
            rating_filter: 评分筛选（None=全部，0-5=具体分数）
            limit: 限制返回数量
            offset: 偏移量（用于分页）
        
        Returns:
            List[dict]: 反馈数据列表
        """
        query = "SELECT id, question, answer, sources, rating, correction, created_at FROM interactions"
        params = []
        
        if rating_filter is not None:
            query += " WHERE rating = ?"
            params.append(rating_filter)
        
        query += " ORDER BY created_at DESC"
        
        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        with self._get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
        
        feedbacks = []
        for row in rows:
            feedbacks.append({
                "id": row[0],
                "question": row[1],
                "answer": row[2],
                "sources": row[3],
                "rating": row[4],
                "correction": row[5],
                "created_at": row[6]
            })
        
        return feedbacks
    
    def get_feedback_count(self, rating_filter: Optional[int] = None) -> int:
        """
        获取反馈总数
        
        Args:
            rating_filter: 评分筛选（None=全部，0-5=具体分数，-1=无反馈）
        
        Returns:
            int: 反馈总数
        """
        with self._get_db_connection() as conn:
            cur = conn.cursor()
            
            if rating_filter is not None:
                if rating_filter == -1:  # 无反馈
                    cur.execute("SELECT COUNT(*) FROM interactions WHERE rating IS NULL")
                else:
                    cur.execute("SELECT COUNT(*) FROM interactions WHERE rating = ?", (rating_filter,))
            else:
                cur.execute("SELECT COUNT(*) FROM interactions")
            
            return cur.fetchone()[0]
    
    def delete_feedback(self, feedback_id: int) -> bool:
        """
        删除反馈
        
        Args:
            feedback_id: 反馈ID
        
        Returns:
            bool: 是否删除成功
        """
        try:
            with self._get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM interactions WHERE id = ?", (feedback_id,))
                return cur.rowcount > 0
        except Exception as e:
            logging.error(f"删除反馈失败: {e}")
            return False
    
    def get_frequent_questions(self, min_count: int = 2, limit: int = 20) -> List[dict]:
        """
        获取高频问题（相同或相似问题出现次数多的）
        统计所有问答交互，包括没有反馈的
        
        Args:
            min_count: 最少出现次数
            limit: 返回数量限制
        
        Returns:
            List[dict]: 高频问题列表，包含question, count, avg_rating, feedback_count
        """
        with self._get_db_connection() as conn:
            cur = conn.cursor()
            
            # 统计每个问题出现的次数、平均评分和反馈数量
            cur.execute("""
                SELECT 
                    question,
                    COUNT(*) as count,
                    AVG(rating) as avg_rating,
                    COUNT(rating) as feedback_count,
                    MAX(created_at) as last_asked
                FROM interactions
                GROUP BY question
                HAVING COUNT(*) >= ?
                ORDER BY count DESC, avg_rating DESC
                LIMIT ?
            """, (min_count, limit))
            
            rows = cur.fetchall()
        
        frequent_questions = []
        for row in rows:
            frequent_questions.append({
                "question": row[0],
                "count": row[1],
                "avg_rating": round(row[2], 2) if row[2] else None,
                "feedback_count": row[3],
                "last_asked": row[4]
            })
        
        return frequent_questions
    
    def get_high_quality_qa_pairs(self, min_rating: int = 4, limit: int = 50) -> List[dict]:
        """
        获取优质问答对（评分高或有改进建议的）
        
        Args:
            min_rating: 最低评分
            limit: 返回数量限制
        
        Returns:
            List[dict]: 优质问答对列表
        """
        with self._get_db_connection() as conn:
            cur = conn.cursor()
            
            # 获取评分高的问答对，优先选择有改进建议的
            cur.execute("""
                SELECT 
                    id,
                    question,
                    answer,
                    correction,
                    rating,
                    created_at
                FROM interactions
                WHERE rating >= ?
                ORDER BY 
                    CASE WHEN correction IS NOT NULL AND correction != '' THEN 1 ELSE 2 END,
                    rating DESC,
                    created_at DESC
                LIMIT ?
            """, (min_rating, limit))
            
            rows = cur.fetchall()
        
        qa_pairs = []
        for row in rows:
            # 如果有改进建议，使用改进建议作为答案
            answer = row[3] if (row[3] and len(row[3].strip()) > 0) else row[2]
            qa_pairs.append({
                "id": row[0],
                "question": row[1],
                "answer": answer,
                "original_answer": row[2],
                "correction": row[3],
                "rating": row[4],
                "created_at": row[5],
                "has_correction": bool(row[3] and len(row[3].strip()) > 0)
            })
        
        return qa_pairs

