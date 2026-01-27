import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict
import time

class CompetitorAnalyzer:
    def __init__(self, openai_api_key: str, model: str = "gpt-4.1-mini"):
        self.api_key = openai_api_key
        self.model = model

    def search_competitors(self, keyword: str, num_results: int = 15) -> List[str]:
        """
        يحاكي البحث عن المنافسين. في بيئة حقيقية، سنستخدم Google Search API.
        هنا سنستخدم محرك بحث متاح أو نعتمد على نتائج محاكاة دقيقة.
        """
        # ملاحظة: في بيئة Manus، يمكننا استخدام أداة البحث المدمجة لجلب روابط حقيقية
        # ولكن ككود برمجي للتطبيق، سنضع هيكلية لجلب الروابط.
        print(f"Searching for competitors for: {keyword}")
        # سنقوم بمحاكاة جلب الروابط حالياً، وفي التطبيق النهائي يمكن دمج Serper أو Google API
        return [f"https://example-competitor-{i}.com/article-about-{keyword}" for i in range(1, num_results + 1)]

    def analyze_url(self, url: str) -> Dict:
        """تحليل محتوى رابط معين لاستخراج العناوين والكلمات المفتاحية"""
        try:
            # في البيئة الحقيقية، قد نحتاج لـ User-Agent لتجنب الحظر
            headers = {'User-Agent': 'Mozilla/5.0'}
            # response = requests.get(url, headers=headers, timeout=10)
            # soup = BeautifulSoup(response.content, 'html.parser')
            
            # محاكاة تحليل المحتوى لغرض العرض في النموذج الأولي
            return {
                "url": url,
                "headings": ["H1: عنوان تجريبي", "H2: مقدمة عن المنتج", "H2: مميزات المنتج"],
                "word_count": 1200,
                "keywords": ["كلمة 1", "كلمة 2"]
            }
        except Exception as e:
            return {"url": url, "error": str(e)}

    def get_competitor_summary(self, keyword: str, competitors_data: List[Dict]) -> str:
        """استخدام OpenAI لتلخيص بيانات المنافسين واستخراج الرؤى"""
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        
        prompt = f"""
        بصفتك خبير SEO، قم بتحليل بيانات المنافسين التالية للكلمة المفتاحية: "{keyword}"
        البيانات: {json.dumps(competitors_data, ensure_ascii=False)}
        
        المطلوب:
        1. استخراج العناوين الرئيسية والفرعية الأكثر تكراراً.
        2. تحديد متوسط طول المحتوى.
        3. استخراج الأسئلة الشائعة التي يغطيها المنافسون.
        4. اقتراح كلمات مفتاحية إضافية بناءً على تحليلهم.
        
        اجعل الإجابة باللغة العربية وبتنسيق منظم.
        """
        
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
