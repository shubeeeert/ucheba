import os, json, time
from openai import OpenAI
from google.colab import userdata

class LLMMarketingEngine:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=userdata.get('OPENROUTER_API_KEY')
        )
        self.model = "google/gemma-4-31b-it:free"

    def generate(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                top_p=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            raise e

def clean_and_parse_json(raw_text):
    start = raw_text.find('{')
    end = raw_text.rfind('}') + 1
    if start == -1 or end == 0:
        raise ValueError("JSON не найден в ответе модели.")
    return json.loads(raw_text[start:end])

def safe_generate_with_retry(engine, messages, retries=3):
    for attempt in range(retries):
        try:
            raw = engine.generate(messages)
            return clean_and_parse_json(raw)
        except Exception as e:
            print(f"[Attempt {attempt+1}] Ошибка: {e}")
            if attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
            else:
                raise

def run_pipeline(product, budget, timeline):
    builder = MarketingPlanPromptBuilder()
    engine = LLMMarketingEngine()
    
    print(f"\nГенерация плана для: {product} (Бюджет: {budget})")
    messages = builder.set_product(product).set_budget(budget).set_timeline(timeline).build_prompt()
    
    plan_json = safe_generate_with_retry(engine, messages)
    
    # Сохранение JSON
    filename_json = f"plan_{product.replace(' ', '_').lower()}.json"
    with open(filename_json, 'w', encoding='utf-8') as f:
        json.dump(plan_json, f, ensure_ascii=False, indent=2)
        
    # Генерация текстового отчета
    with open(filename_json.replace('.json', '.txt'), 'w', encoding='utf-8') as txt:
        txt.write(f"МАРКЕТИНГОВЫЙ ПЛАН: {plan_json['title']}\n")
        txt.write("="*50 + "\n")
        for slide in plan_json['slides']:
            txt.write(f"\n[СЛАЙД {slide['slide']}] {slide['topic']}\n")
            txt.write("• " + "\n• ".join(slide['points']) + "\n")
            txt.write(f"Примечание спикера: {slide['speaker_notes']}\n")
            
    print(f"Успешно сохранено в {filename_json} и {filename_json.replace('.json', '.txt')}")
    return plan_json

# Пример запуска
# run_pipeline("Кофейня 'Зерно'", "300 000 ?", "1.5 месяца")