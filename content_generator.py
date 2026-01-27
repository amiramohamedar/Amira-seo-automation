from openai import OpenAI
import json
from typing import List, Dict

class ContentGenerator:
    def __init__(self, api_key: str, model: str = "gpt-4.1-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_outline(self, main_keyword: str, related_keywords: List[str], analysis_summary: str) -> str:
        prompt = f"""
        بناءً على تحليل المنافسين التالي:
        {analysis_summary}
        
        قم بإنشاء Outline مفصل لمقال SEO احترافي حول: "{main_keyword}"
        الكلمات المفتاحية المرتبطة: {", ".join(related_keywords)}
        
        المتطلبات:
        - عنوان H1 جذاب.
        - تقسيم المحتوى إلى H2 و H3 بشكل منطقي وشامل.
        - يجب أن يغطي الـ Outline محتوى لا يقل عن 2500 كلمة.
        - إضافة قسم لـ 12 سؤال شائع (FAQs) في النهاية.
        - اللغة: العربية.
        
        أخرج الـ Outline بتنسيق Markdown واضح.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def generate_article_section(self, section_title: str, context: str, requirements: Dict) -> str:
        """توليد جزء معين من المقال لضمان الطول والجودة"""
        prompt = f"""
        اكتب فقرة مفصلة لعنوان: "{section_title}"
        السياق العام للمقال: {context}
        
        المتطلبات الصارمة:
        - طول الفقرة لا يقل عن 150 كلمة.
        - إذا كان العنوان H2، ابدأ بمقدمة تمهيدية (30-40 كلمة) تشرح ما سيتم تناوله.
        - استخدم تنسيق HTML (p, strong, ul, li).
        - ادمج الكلمات المفتاحية التالية بشكل طبيعي: {requirements.get('keywords', [])}
        - ادمج روابط الـ Anchor Text التالية: {requirements.get('anchors', [])}
        - إذا وجد مصطلح تقني، اذكر المصطلح الإنجليزي بجانبه.
        - اللغة: العربية.
        - لا تذكر أي منافسين.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def generate_full_article(self, outline: str, main_keyword: str, related_keywords: List[str], anchors: List[Dict], target_domain: str) -> str:
        """
        توليد المقال كاملاً من خلال تقسيم الـ Outline إلى أجزاء لتجاوز حدود الـ Token وضمان الطول (2500+ كلمة).
        """
        # في النسخة الكاملة، سنقوم بتقسيم الـ Outline وتوليد كل قسم على حدة
        # هنا سنضع المنطق الأساسي
        full_content = ""
        
        # 1. توليد المقدمة (70-100 كلمة)
        intro_prompt = f"اكتب مقدمة مقال SEO عن {main_keyword} بطول 70-100 كلمة تحتوي على الكلمة المفتاحية الرئيسية بشكل طبيعي. استخدم HTML."
        intro_res = self.client.chat.completions.create(model=self.model, messages=[{"role": "user", "content": intro_prompt}])
        full_content += intro_res.choices[0].message.content + "\n\n"
        
        # 2. محاكاة توليد الأقسام (في التطبيق الفعلي سنمر على كل عنوان في الـ Outline)
        # سنقوم هنا بطلب توليد المقال كاملاً مع التأكيد على الطول، أو تقسيمه برمجياً.
        
        final_prompt = f"""
        اكتب مقالاً كاملاً بناءً على الـ Outline التالي:
        {outline}
        
        المتطلبات:
        - الطول الإجمالي: 2500 كلمة على الأقل.
        - الكلمة المفتاحية الرئيسية: {main_keyword} (توزيع طبيعي، ذكرها في H2 مرة على الأقل).
        - الكلمات المرتبطة: {related_keywords} (كل واحدة مرة واحدة).
        - روابط Anchor Text: {anchors} (كل واحد مرة واحدة بتنسيق <a href="URL">Anchor</a>).
        - 12 سؤال FAQ في النهاية (H3 للأسئلة).
        - CTA في النهاية لموقع {target_domain}.
        - تنسيق HTML كامل.
        - اللغة: العربية.
        """
        
        # ملاحظة: لتوليد 2500 كلمة فعلياً، يفضل استخدام GPT-4 مع تقسيم المهام.
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": final_prompt}]
        )
        return full_content + response.choices[0].message.content
