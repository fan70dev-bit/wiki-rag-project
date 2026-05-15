import sqlite3
import os
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

DB_PATH = "/data/fan70_env/wiki_v2.db"
CHROMA_PATH = "/data/fan70_env/chroma_v2"

class WikiDBManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.chroma_client = PersistentClient(path=CHROMA_PATH)
        self.collection = self.chroma_client.get_collection(name="wiki_vectors")
        os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
        self.model = SentenceTransformer('BAAI/bge-small-zh-v1.5', local_files_only=True)

    def search_by_title(self, query, page=1, size=10):
        offset = (page - 1) * size
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM articles WHERE title LIKE ?", (f'%{query}%',))
        total = cursor.fetchone()[0]
        
        cursor.execute(
            "SELECT id, title, SUBSTR(full_text, 1, 200) as summary FROM articles WHERE title LIKE ? LIMIT ? OFFSET ?",
            (f'%{query}%', size, offset)
        )
        rows = [dict(row) for row in cursor.fetchall()]
        for row in rows:
            row['match_rate'] = "100.00%"
        return rows, total

    def search_by_vector(self, query, page=1, size=10):
        query_vector = self.model.encode(query, normalize_embeddings=True).tolist()
        raw_results = self.collection.query(query_embeddings=[query_vector], n_results=100)
        
        filtered_ids = []
        distance_map = {}
        
        # 🚀 降低严格度，将阈值放宽至 1.10
        threshold = 1.10 
        
        print(f"\n--- 🛰️ 向量检索阈值实时监控 (当前阈值: {threshold}) ---")
        for i in range(len(raw_results['ids'][0])):
            distance = raw_results['distances'][0][i]
            title = raw_results['metadatas'][0][i]['title']
            doc_id = raw_results['ids'][0][i]
            
            status = "✅" if distance < threshold else "❌"
            print(f"{status} [{title}] 距离: {distance:.4f}")

            if distance < threshold: 
                filtered_ids.append(doc_id)
                # 计算匹配度百分比
                distance_map[doc_id] = f"{(1 - distance/2):.2%}"
        
        total = len(filtered_ids)
        start = (page - 1) * size
        paged_ids = filtered_ids[start:start+size]
        
        if not paged_ids: return [], total
        
        placeholders = ','.join(['?'] * len(paged_ids))
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT id, title, SUBSTR(full_text, 1, 200) as summary FROM articles WHERE id IN ({placeholders})", paged_ids)
        
        id_sort_map = {str(id): i for i, id in enumerate(paged_ids)}
        rows = [dict(row) for row in cursor.fetchall()]
        
        for row in rows:
            row['match_rate'] = distance_map.get(str(row['id']), "未知")
            
        rows.sort(key=lambda x: id_sort_map.get(str(x['id']), 999))
        
        return rows, total

    def get_full_article(self, article_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT title, full_text FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

wiki_manager = WikiDBManager()
