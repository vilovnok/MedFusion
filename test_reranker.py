
import torch
from transformers import AutoModelForSequenceClassification, AutoConfig
from optimum.exporters.onnx import export
from pathlib import Path

# Кастомная ONNX-конфигурация
class CustomOnnxConfig:
    def __init__(self, config):
        self.config = config

    @property
    def inputs(self):
        return {
            "input_ids": {0: "batch", 1: "sequence"},
            "attention_mask": {0: "batch", 1: "sequence"},
        }

    @property
    def outputs(self):
        return {
            "logits": {0: "batch", 1: "sequence"},
        }

    @property
    def is_transformers_support_available(self):
        return True

    @property
    def is_torch_support_available(self):
        return True

    @property
    def values_override(self):
        return {}

    def generate_dummy_inputs(self, framework="pt", **input_shapes):
        batch_size = input_shapes.get("batch_size", 1)
        sequence_length = input_shapes.get("sequence_length", 1024)
        return {
            "input_ids": torch.ones((batch_size, sequence_length), dtype=torch.long),
            "attention_mask": torch.ones((batch_size, sequence_length), dtype=torch.long),
        }

    def rename_ambiguous_inputs(self, dummy_inputs):
        return dummy_inputs

    def patch_model_for_export(self, model, model_kwargs=None):
        class DummyContextManager:
            def __enter__(self):
                return model

            def __exit__(self, exc_type, exc_value, traceback):
                pass

        return DummyContextManager()

    def ordered_inputs(self, model):
        return {
            "input_ids": {0: "batch", 1: "sequence"},
            "attention_mask": {0: "batch", 1: "sequence"},
        }

    def fix_dynamic_axes(self, output, device, input_shapes, dtype):
        return {
            "input_ids": {0: "batch", 1: "sequence"},
            "attention_mask": {0: "batch", 1: "sequence"},
            "logits": {0: "batch", 1: "sequence"},
        }

# Настройки
model_name = "jinaai/jina-reranker-v2-base-multilingual"
output_path = "./jina-reranker-v2-base-multilingual"

# Загружаем модель и её конфигурацию
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, torch_dtype="auto", trust_remote_code=True
)
config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)

# Создаём директорию для сохранения
onnx_output_dir = Path(output_path)
onnx_output_dir.mkdir(parents=True, exist_ok=True)

# Экспорт модели в ONNX с указанием явного типа FP32
export(
    model=model.float(),  # Приводим все веса модели к float32
    config=CustomOnnxConfig(config),
    opset=12,
    output=onnx_output_dir / "model.onnx"
)

print(f"Модель успешно экспортирована в {onnx_output_dir}")


import torch
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Настройки
model_name = "jinaai/jina-reranker-v2-base-multilingual"
onnx_model_path = "./jina-reranker-v2-base-multilingual/model.onnx"

# Загрузка PyTorch-модели
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, torch_dtype="auto", trust_remote_code=True
)
model.eval()

# Загрузка токенайзера
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

# Пример входных данных
query = "Organic skincare products for sensitive skin"
documents = [
    "Organic skincare for sensitive skin with aloe vera and chamomile.",
    "New makeup trends focus on bold colors and innovative techniques",
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

# --- 1. Проверка PyTorch-модели ---
with torch.no_grad():
    torch_outputs = model(**inputs)
    torch_logits = torch_outputs.logits
    print("PyTorch модель (логиты):")
    print(torch_logits)

# --- 2. Проверка ONNX-модели ---
# Создаем сессию для ONNX-модели
session = ort.InferenceSession(onnx_model_path)

# Подготовка входов для ONNX
onnx_inputs = {
    "input_ids": inputs["input_ids"].numpy(),
    "attention_mask": inputs["attention_mask"].numpy(),
}

# Выполнение инференса
onnx_outputs = session.run(None, onnx_inputs)
onnx_logits = onnx_outputs[0]  # Первый выход ONNX соответствует логитам
print("\nONNX модель (логиты):")
print(onnx_logits)

# --- 3. Сравнение результатов ---
# Преобразуем PyTorch логиты в float32
torch_logits_fp32 = torch_logits.to(dtype=torch.float32).numpy()

# Сравниваем логиты
if np.allclose(torch_logits_fp32, onnx_logits, atol=1e-4):
    print("\nРезультаты PyTorch и ONNX моделей совпадают!")
else:
    print("\nРезультаты PyTorch и ONNX моделей отличаются.")