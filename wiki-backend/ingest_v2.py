import os, json, re, sqlite3, time
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

print("🚀 真实流速遥测驱动的入库程序启动...")
count = 0

# 🚀 物理流速测量引脚
msg_counter = 0
last_flush_time = time.time()

for message in consumer:
    try:
        # 实时处理计数递增
        msg_counter += 1
        
        # 时钟窗口触发：每过 1.0 秒，清算这一秒内的绝对处理吞吐率
        current_time = time.time()
        if current_time - last_flush_time >= 1.0:
            elapsed = current_time - last_flush_time
            throughput = int(msg_counter / elapsed)
            try:
                # 写入共享共享内存文件桥梁
                with open("/tmp/kafka_throughput.txt", "w") as f:
                    f.write(str(throughput))
            except Exception:
                pass
            # 计数器原子重置，进入下一秒的洪峰统计
            msg_counter = 0
            last_flush_time = current_time

        # 核心 RAG 数据落库业务不变
        article = json.loads(message.value.decode('utf-8'))
        title, content = article.get('title', '未知'), clean_text(article.get('text', ''))
        raw_id = str(article.get('id', count))
        cursor.execute("INSERT OR REPLACE INTO articles VALUES (?, ?, ?)", (raw_id, title, content))
        embedding = model.encode(content[:500], normalize_embeddings=True).tolist()
        collection.add(ids=[raw_id], embeddings=[embedding], metadatas=[{"title": title}])
        
        count += 1
        if count % 100 == 0:
            print(f"✅ 已存入 {count} 条")
            conn.commit()
    except Exception: 
        continue
