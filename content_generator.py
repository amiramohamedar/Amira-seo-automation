import openai
from openai import OpenAI
import re

def generate_outline(analysis_results, api_key):
    """
    توليد مخطط (Outline) تفصيلي بناءً على تحليل المنافسين.
    """
    try:
        # استخدام العميل الافتراضي المجهز مسبقاً في البيئة
        client = OpenAI()
        keyword = analysis_results['keyword']
        common_headings = analysis_results.get('common_headings', [])
        
        prompt = f"""
        أنت خبير SEO محترف. قم بإنشاء مخطط (Outline) تفصيلي لمقال SEO احترافي.
        
        الكلمة المفتاحية: "{keyword}"
        العناوين الشائعة في المنافسين: {', '.join(common_headings)}
        
        المتطلبات:
        1. عنوان H1 جذاب ومتوافق مع SEO يحتوي على الكلمة المفتاحية.
        2. عناوين فرعية H2 و H3 تغطي الموضوع بعمق (8-12 عنوان H2).
        3. قسم خاص بـ 12 سؤال شائع (FAQs) في النهاية.
        4. المخطط يجب أن يسمح بكتابة مقال طوله 2500+ كلمة.
        5. اللغة: العربية.
        6. تنسيق واضح مع ترقيم للعناوين.
        
        قدم الـ Outline بصيغة منظمة وسهلة القراءة.
        """
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"خطأ في توليد الـ Outline: {str(e)}"

def generate_content(data, api_key):
    """
    توليد مقال احترافي متوافق مع SEO.
    """
    try:
        # استخدام العميل الافتراضي المجهز مسبقاً في البيئة
        client = OpenAI()
        
        # تحضير بيانات الروابط
        anchors_text = ""
        if data.get('anchors'):
            anchors_list = []
            for anchor in data['anchors']:
                if anchor.get('text') and anchor.get('url'):
                    anchors_list.append(f"'{anchor['text']}' -> {anchor['url']}")
            anchors_text = ", ".join(anchors_list)
        
        prompt = f"""
        أنت كاتب محتوى SEO محترف. اكتب مقالاً احترافياً متوافقاً مع معايير SEO الحديثة.
        
        بيانات المقال:
        - الكلمة المفتاحية الرئيسية: "{data['main_keyword']}"
        - الكلمات المفتاحية المرتبطة: {data['related_keywords']}
        - الدومين المستهدف: {data['target_domain']}
        - اللغة: {data['language']}
        - المخطط المقترح:
        {data['outline']}
        
        المتطلبات الصارمة:
        1. الطول الإجمالي: لا يقل عن 2500 كلمة.
        2. الفقرات: كل فقرة تحت H2 لا تقل عن 150 كلمة.
        3. المقدمة: 70-100 كلمة تشمل الكلمة المفتاحية بشكل طبيعي.
        4. مقدمة تمهيدية بعد كل H2: 30-40 كلمة توضح محتوى القسم.
        5. توزيع الكلمات المفتاحية المرتبطة: كل كلمة مرة واحدة فقط بشكل طبيعي.
        6. نصوص الربط: {anchors_text}
        7. التنسيق: استخدم HTML احترافي (H1, H2, H3, p, strong, em, ul, ol, li, a).
        8. عدم ذكر أي منافسين أو مواقع منافسة.
        9. إذا وجد مصطلح تقني عربي، اذكر المصطلح الإنجليزي بجانبه بين قوسين.
        10. في النهاية أضف CTA (دعوة للإجراء) للدومين المستهدف بشكل طبيعي.
        11. أضف Meta Description في النهاية (150-160 حرف) يحتوي على الكلمة المفتاحية.
        12. توزيع الكلمة المفتاحية الرئيسية بشكل طبيعي (كثافة 1-2%).
        
        قدم المقال بصيغة HTML جاهزة للنشر.
        """
        
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "أنت خبير SEO وكاتب محتوى محترف متخصص في إنشاء محتوى عالي الجودة متوافق مع معايير SEO الحديثة."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content
        word_count = len(content.split())
        
        # استخراج Meta Description إذا كانت موجودة
        meta_desc = extract_meta_description(content)
        
        return {
            "html": content,
            "word_count": word_count,
            "title": data['main_keyword'],
            "meta_description": meta_desc
        }
    except Exception as e:
        return {
            "html": f"<p>خطأ في توليد المقال: {str(e)}</p>",
            "word_count": 0,
            "title": data['main_keyword'],
            "meta_description": ""
        }

def extract_meta_description(content):
    """
    استخراج Meta Description من المحتوى.
    """
    try:
        # البحث عن Meta Description في المحتوى
        match = re.search(r'Meta Description[:\s]*([^\n<]+)', content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return ""
    except:
        return ""

def count_keyword_density(content, keyword):
    """
    حساب كثافة الكلمة المفتاحية في المحتوى.
    """
    try:
        words = content.lower().split()
        keyword_lower = keyword.lower()
        keyword_count = sum(1 for word in words if keyword_lower in word)
        total_words = len(words)
        density = (keyword_count / total_words * 100) if total_words > 0 else 0
        return round(density, 2)
    except:
        return 0
