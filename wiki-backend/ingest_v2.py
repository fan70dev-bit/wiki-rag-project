import os, json, re, sqlite3
from kafka import KafkaConsumer
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from core.config import settings

# 初始化
os.environ['HF_ENDPOINT'] = settings.HF_ENDPOINT
conn = sqlite3.connect(settings.DB_PATH)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS articles (id TEXT PRIMARY KEY, title TEXT, full_text TEXT)")
chroma_client = PersistentClient(path=settings.CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="wiki_vectors")
model = SentenceTransformer('BAAI/bge-small-zh-v1.5', local_files_only=True)

def clean_text(text):
    text = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

consumer = KafkaConsumer('wiki-data', bootstrap_servers=['192.168.244.131:9092'], auto_offset_reset='earliest', group_id='wiki_final_v2')

print("🚀 环境变量驱动的入库程序启动...")
count = 0
for message in consumer:
    try:
        article = json.loads(message.value.decode('utf-8'))
        title, content = article.get('title', '未知'), clean_text(article.get('text', ''))
        raw_id = str(article.get('id', count))
        cursor.execute("INSERT OR REPLACE INTO articles VALUES (?, ?, ?)", (raw_id, title, content))
        embedding = model.encode(content[:500], normalize_embeddings=True).tolist()
        collection.add(ids=[raw_id], embeddings=[embedding], metadatas=[{"title": title}])
        count += 1
        if count % 100 == 0:
            print(f"✅ 已存入 {count} 条"); conn.commit()
    except Exception: continue
