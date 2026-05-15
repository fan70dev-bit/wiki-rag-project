import os
import sqlite3
import json
import re
from kafka import KafkaConsumer
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

# 1. 环境配置
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
DB_PATH = "/data/fan70_env/wiki_v2.db"
CHROMA_PATH = "/data/fan70_env/chroma_v2"

# 2. 初始化数据库
print("🛠️ 正在初始化双引擎数据库...")
# SQLite 负责完整存储
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS articles 
                  (id TEXT PRIMARY KEY, title TEXT, full_text TEXT)''')
conn.commit()

# ChromaDB 负责向量索引
chroma_client = PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="wiki_vectors")

# 3. 加载模型
print("🧠 正在唤醒本地翻译官 (bge-small)...")
model = SentenceTransformer('BAAI/bge-small-zh-v1.5', local_files_only=True)

# 4. 数据清洗函数 (ETL 的关键)
def clean_text(text):
    # 替换掉 Wiki 的特殊标签、多余换行和空格
    text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text) # 清理 [[A|B]] 标签
    text = re.sub(r'\{\{[^\}]*\}\}', '', text) # 清理 {{...}} 模板
    text = re.sub(r'\n+', '\n', text) # 多个换行变一个
    return text.strip()

# 5. 启动 Kafka 消费者 (使用新 group_id 确保从头开始)
consumer = KafkaConsumer(
    'wiki-data',
    bootstrap_servers=['192.168.244.131:9092'],
    auto_offset_reset='earliest',
    group_id='wiki_final_v2', # 换个名字，从第 0 条重新读
    consumer_timeout_ms=10000 # 10秒没数据自动停止
)

print("\n🚀 推土机 2.0 启动！正在执行清洗入库...")
count = 0
try:
    for message in consumer:
        try:
            article = json.loads(message.value.decode('utf-8'))
            raw_id = str(article.get('id', count))
            title = article.get('title', '未知标题')
            content = clean_text(article.get('text', ''))
            
            if len(content) < 20: continue

            # A. 完整原文存入 SQLite
            cursor.execute("INSERT OR REPLACE INTO articles VALUES (?, ?, ?)", (raw_id, title, content))
            
            # B. 算向量 (取前 500 字做特征即可，不影响点开看全文)
            summary = content[:500]
            embedding = model.encode(summary, normalize_embeddings=True).tolist()
            
            # C. 向量存入 ChromaDB
            collection.add(
                ids=[raw_id],
                embeddings=[embedding],
                metadatas=[{"title": title}]
            )
            
            count += 1
            if count % 100 == 0:
                print(f"✨ 已清洗并入库 {count} 条数据... (当前: 《{title}》)")
                conn.commit()
            
            # 为了演示，我们先跑 10000 条，你可以随时改为更多
            if count >= 10000: break

        except Exception as e:
            continue
finally:
    conn.commit()
    conn.close()
    print(f"✅ 任务完成！共处理 {count} 条干净数据。")
