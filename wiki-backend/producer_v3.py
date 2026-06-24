import os
import json
from kafka import KafkaProducer

ROOT = "/data/wiki_corpus/wiki_zh_2019/wiki_zh"

producer = KafkaProducer(
    bootstrap_servers=["192.168.244.131:9092"],
    value_serializer=lambda v:
        json.dumps(
            v,
            ensure_ascii=False
        ).encode("utf-8")
)

count = 0

print("🚀 开始读取 Wikipedia 并发送至 Kafka...")

for folder in sorted(os.listdir(ROOT)):
    folder_path = os.path.join(ROOT, folder)

    if not os.path.isdir(folder_path):
        continue

    print(f"📂 处理目录：{folder}")

    for filename in sorted(os.listdir(folder_path)):
        filepath = os.path.join(folder_path, filename)

        with open(
            filepath,
            "r",
            encoding="utf-8"
        ) as f:

            for line in f:
                try:
                    article = json.loads(line)

                    raw_id = str(
                        article.get(
                            "id",
                            count
                        )
                    )

                    title = article.get(
                        "title",
                        ""
                    )

                    text = article.get(
                        "text",
                        ""
                    )

                    producer.send(
                        "wiki-data",
                        {
                            "id": raw_id,
                            "title": title,
                            "text": text
                        }
                    )

                    count += 1

                    if count % 1000 == 0:
                        print(
                            f"📤 已发送 {count} 篇 "
                            f"| 当前：{title}"
                        )

                except Exception:
                    continue

producer.flush()

print(
    f"🎉 全部发送完成，共发送 {count} 篇文章"
)