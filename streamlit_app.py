import streamlit as st
import pandas as pd
from competitor_analysis import CompetitorAnalyzer
from content_generator import ContentGenerator
from wordpress_handler import WordPressHandler
from storage_handler import StorageHandler
import json
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="نظام أتمتة المحتوى الذكي", layout="wide")

# دعم RTL عبر CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [data-testid="stSidebar"], .stMarkdown {
        direction: RTL;
        text-align: right;
        font-family: 'Tajawal', sans-serif;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    .main-header {
        text-align: center;
        color: #2E4053;
        padding: 20px;
        background-color: #F4F6F7;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>🚀 نظام أتمتة المحتوى و SEO الاحترافي</h1></div>', unsafe_allow_html=True)

# شريط جانبي للإعدادات
with st.sidebar:
    st.header("⚙️ الإعدادات")
    openai_key = st.text_input("OpenAI API Key", type="password")
    model_choice = st.selectbox("اختر النموذج", ["gpt-4.1-mini", "gpt-4.1-nano"])
    
    st.divider()
    st.header("🌐 إعدادات WordPress")
    wp_url = st.text_input("رابط الموقع")
    wp_user = st.text_input("اسم المستخدم")
    wp_pass = st.text_input("كلمة مرور التطبيق", type="password")
    
    st.divider()
    st.header("📁 إعدادات Google Drive")
    drive_folder_id = st.text_input("Folder ID")

# واجهة إدخال البيانات
st.subheader("📝 إدخال بيانات المنتج")
col1, col2 = st.columns(2)

with col1:
    main_keyword = st.text_input("الكلمة المفتاحية الرئيسية")
    related_keywords = st.text_area("الكلمات المفتاحية المرتبطة (مفصولة بفواصل)")
    target_language = st.selectbox("اللغة المستهدفة", ["العربية", "الإنجليزية"])

with col2:
    target_domain = st.text_input("الدومين المستهدف (Target Domain)")
    anchors_input = st.text_area("نصوص الربط والروابط (Anchor Text | URL) - سطر لكل زوج")

# معالجة نصوص الربط
anchors = []
if anchors_input:
    for line in anchors_input.split('\n'):
        if '|' in line:
            text, url = line.split('|')
            anchors.append({"text": text.strip(), "url": url.strip()})

# الحالة (Session State)
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'outline' not in st.session_state:
    st.session_state.outline = None
if 'article' not in st.session_state:
    st.session_state.article = None

# الأزرار الرئيسية
if st.button("🔍 تحليل المنافسين"):
    if not openai_key or not main_keyword:
        st.error("يرجى إدخال مفتاح API والكلمة المفتاحية")
    else:
        with st.spinner("جاري تحليل المنافسين..."):
            analyzer = CompetitorAnalyzer(openai_key, model_choice)
            # محاكاة البحث والتحليل
            urls = analyzer.search_competitors(main_keyword)
            # في الواقع سنقوم بتحليل كل URL، هنا سنستخدم عينة
            sample_data = [{"url": u, "headings": ["H2: مميزات المنتج"], "word_count": 1500} for u in urls[:5]]
            summary = analyzer.get_competitor_summary(main_keyword, sample_data)
            st.session_state.analysis_result = summary
            st.success("تم التحليل بنجاح!")

if st.session_state.analysis_result:
    st.info("📊 ملخص تحليل المنافسين")
    st.markdown(st.session_state.analysis_result)
    
    if st.button("📝 توليد Outline"):
        with st.spinner("جاري إنشاء الـ Outline..."):
            gen = ContentGenerator(openai_key, model_choice)
            related_list = [k.strip() for k in related_keywords.split(',')]
            outline = gen.generate_outline(main_keyword, related_list, st.session_state.analysis_result)
            st.session_state.outline = outline

if st.session_state.outline:
    st.subheader("📋 الـ Outline المقترح")
    st.markdown(st.session_state.outline)
    
    col_out1, col_out2 = st.columns(2)
    with col_out1:
        if st.button("✅ الموافقة والبدء في الكتابة"):
            with st.spinner("جاري كتابة المقال (قد يستغرق ذلك دقائق لضمان الطول والجودة)..."):
                gen = ContentGenerator(openai_key, model_choice)
                related_list = [k.strip() for k in related_keywords.split(',')]
                article = gen.generate_full_article(st.session_state.outline, main_keyword, related_list, anchors, target_domain)
                st.session_state.article = article
    with col_out2:
        if st.button("🔄 إعادة المحاولة"):
            st.session_state.outline = None
            st.rerun()

if st.session_state.article:
    st.divider()
    st.subheader("📄 المقال النهائي")
    
    # عرض إحصائيات سريعة
    word_count = len(st.session_state.article.split())
    st.success(f"تم توليد المقال بنجاح! عدد الكلمات التقريبي: {word_count}")
    
    tab1, tab2 = st.tabs(["معاينة المحتوى", "كود HTML"])
    with tab1:
        st.markdown(st.session_state.article, unsafe_allow_html=True)
    with tab2:
        st.code(st.session_state.article, language="html")
    
    st.divider()
    st.subheader("💾 خيارات الحفظ والرفع")
    
    col_save1, col_save2, col_save3 = st.columns(3)
    
    storage = StorageHandler()
    
    with col_save1:
        if st.button("📤 الرفع إلى WordPress"):
            if wp_url and wp_user and wp_pass:
                wp = WordPressHandler(wp_url, wp_user, wp_pass)
                res = wp.post_article(main_keyword, st.session_state.article)
                if res['success']:
                    st.success(f"تم الرفع بنجاح! الرابط: {res['link']}")
                    # حفظ في إكسيل
                    log_data = [{
                        "الكلمة المفتاحية": main_keyword,
                        "الرابط": res['link'],
                        "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "الحالة": "تم الرفع"
                    }]
                    storage.save_to_excel(log_data)
                else:
                    st.error(f"خطأ في الرفع: {res['error']}")
            else:
                st.warning("يرجى إدخال بيانات ووردبريس في الشريط الجانبي")
                
    with col_save2:
        docx_path = storage.save_to_docx(main_keyword, st.session_state.article)
        with open(docx_path, "rb") as f:
            st.download_button("📥 تحميل ملف Word", f, file_name=f"{main_keyword}.docx")
            
    with col_save3:
        if st.button("☁️ الرفع إلى Google Drive"):
            if drive_folder_id:
                drive_link = storage.upload_to_drive(docx_path, drive_folder_id)
                st.success(f"تم الرفع لـ Drive: {drive_link}")
            else:
                st.warning("يرجى إدخال Folder ID")
