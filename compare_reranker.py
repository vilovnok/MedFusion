import time
import torch
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Настройки
model_name = "jinaai/jina-reranker-v2-base-multilingual"
onnx_model_path = "./jina-reranker-v2-base-multilingual/model.onnx"

# Загрузка PyTorch-модели
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, torch_dtype="auto", trust_remote_code=True,
)
model.eval()

# Загрузка токенайзера
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

# Пример входных данных
query = "Organic skincare products for sensitive skin"
documents = [
    "Organic skincare for sensitive skin with aloe vera and chamomile.",
    "New makeup trends focus on bold colors and innovative techniques",
    "Bio-Hautpflege für empfindliche Haut mit Aloe Vera und Kamille",
]

# Создаем пары (query, document)
sentence_pairs = [[query, doc] for doc in documents]

# Токенизация
inputs = tokenizer(
    sentence_pairs,
    padding=True,
    truncation=True,
    max_length=1024,
    return_tensors="pt",
)

# --- PyTorch Inference ---
start_time = time.time()
with torch.no_grad():
    for _ in range(10):  # Повторяем 10 раз для усреднения
        torch_logits = model(**inputs).logits
torch_time = (time.time() - start_time) / 10
print(f"PyTorch среднее время вывода: {torch_time:.6f} секунд")

# --- ONNX Inference ---
# Создаем сессию для ONNX-модели
session = ort.InferenceSession(onnx_model_path)

# Подготовка входов для ONNX
onnx_inputs = {
    "input_ids": inputs["input_ids"].numpy(),
    "attention_mask": inputs["attention_mask"].numpy(),
}

start_time = time.time()
for _ in range(10):  # Повторяем 10 раз для усреднения
    onnx_outputs = session.run(None, onnx_inputs)
onnx_time = (time.time() - start_time) / 10
print(f"ONNX среднее время вывода: {onnx_time:.6f} секунд")

# --- Сравнение ---
speedup = torch_time / onnx_time
print(f"ONNX быстрее PyTorch в {speedup:.2f} раз.")
