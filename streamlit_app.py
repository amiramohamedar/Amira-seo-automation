import streamlit as st
import pandas as pd
from competitor_analysis import analyze_competitors
from content_generator import generate_outline, generate_content, count_keyword_density
from wordpress_handler import upload_to_wordpress
from storage_handler import save_to_excel, save_to_docx, save_to_html
import os

# إعدادات الصفحة
st.set_page_config(
    page_title="نظام أتمتة المحتوى SEO",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# دعم RTL والتنسيق
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTabs [data-baseweb="tab-list"] button {
        direction: rtl;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 نظام أتمتة المحتوى الذكي (SEO AI Automation)")
st.markdown("---")

# تهيئة Session State
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'outline' not in st.session_state:
    st.session_state.outline = None
if 'article' not in st.session_state:
    st.session_state.article = None
if 'anchors' not in st.session_state:
    st.session_state.anchors = [{"text": "", "url": ""}]

# الشريط الجانبي - الإعدادات
with st.sidebar:
    st.header("⚙️ الإعدادات")
    
    with st.expander("🔑 إعدادات OpenAI", expanded=True):
        openai_key = st.text_input("OpenAI API Key (اختياري)", type="password", placeholder="sk-...")
        st.info("💡 يتم استخدام مفتاح افتراضي إذا تركته فارغاً.")
        model_choice = st.selectbox("اختر النموذج", ["gpt-4.1-mini", "gpt-4.1-nano", "gemini-2.5-flash"])
    
    with st.expander("📝 إعدادات WordPress"):
        wp_url = st.text_input("رابط الموقع", placeholder="https://your-site.com")
        wp_user = st.text_input("اسم المستخدم")
        wp_pass = st.text_input("كلمة مرور التطبيق", type="password")
    
    st.markdown("---")
    st.markdown("### 📚 المساعدة")
    st.markdown("""
    - **OpenAI API**: احصل على مفتاح من [openai.com](https://openai.com)
    - **WordPress**: استخدم Application Passwords من إعدادات المستخدم
    """)

# 1. واجهة إدخال البيانات
st.header("📋 إدخال بيانات المقال")

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        main_keyword = st.text_input(
            "🔍 الكلمة المفتاحية الرئيسية",
            placeholder="مثال: أفضل هواتف 2024",
            key="main_kw"
        )
        related_keywords = st.text_area(
            "🔗 الكلمات المفتاحية المرتبطة (مفصولة بفاصلة)",
            placeholder="هواتف سامسونج، آيفون 15، مواصفات الهواتف",
            height=80,
            key="related_kw"
        )
    
    with col2:
        target_domain = st.text_input(
            "🌐 الدومين المستهدف",
            placeholder="https://example.com",
            key="target_dom"
        )
        target_language = st.selectbox(
            "🗣️ اللغة المستهدفة",
            ["العربية", "الإنجليزية", "الفرنسية"],
            key="lang_choice"
        )

# إضافة نصوص الربط (Anchor Texts)
st.subheader("🔗 نصوص الربط والروابط (Anchor Texts)")

if st.button("➕ إضافة رابط جديد"):
    st.session_state.anchors.append({"text": "", "url": ""})
    st.rerun()

for i, anchor in enumerate(st.session_state.anchors):
    col1, col2, col3 = st.columns([2, 2, 1])
    
    st.session_state.anchors[i]["text"] = col1.text_input(
        f"نص الربط {i+1}",
        value=anchor["text"],
        key=f"at_{i}",
        placeholder="مثال: أفضل الهواتف"
    )
    st.session_state.anchors[i]["url"] = col2.text_input(
        f"الرابط {i+1}",
        value=anchor["url"],
        key=f"au_{i}",
        placeholder="https://example.com/phones"
    )
    
    if col3.button("❌", key=f"del_{i}"):
        st.session_state.anchors.pop(i)
        st.rerun()

st.markdown("---")

# 2. تحليل المنافسين
col_analyze, col_space = st.columns([1, 3])

if col_analyze.button("🔍 تحليل المنافسين", use_container_width=True):
    if not main_keyword:
        st.error("❌ يرجى إدخال الكلمة المفتاحية الرئيسية")
    else:
        with st.spinner("⏳ جاري تحليل المنافسين..."):
            results = analyze_competitors(main_keyword)
            st.session_state.analysis_results = results
            st.success("✅ تم الانتهاء من تحليل المنافسين!")
            
            # عرض النتائج
            with st.expander("📊 نتائج التحليل", expanded=True):
                col1, col2, col3 = st.columns(3)
                col1.metric("عدد المنافسين", len(results['top_competitors']))
                col2.metric("متوسط طول المقال", f"{results['avg_length']} كلمة")
                col3.metric("العناوين الشائعة", len(results['common_headings']))
                
                st.write("**العناوين الشائعة في المنافسين:**")
                st.write(", ".join(results['common_headings']))
                
                st.write("**الكلمات المفتاحية المقترحة:**")
                st.write(", ".join(results['suggested_keywords']))

# 3. توليد Outline
if st.session_state.analysis_results:
    st.markdown("---")
    if st.button("📝 توليد Outline المقال", use_container_width=True):
        with st.spinner("⏳ جاري إنشاء المخطط..."):
            outline = generate_outline(st.session_state.analysis_results, openai_key)
            st.session_state.outline = outline
            st.success("✅ تم إنشاء المخطط!")
            
            with st.expander("📋 المخطط المقترح", expanded=True):
                st.markdown(outline)

# 4. كتابة المقال
if st.session_state.outline:
    st.markdown("---")
    col_approve, col_retry = st.columns(2)
    
    if col_approve.button("✅ الموافقة والبدء في الكتابة", use_container_width=True):
        with st.spinner("⏳ جاري كتابة المقال (قد يستغرق ذلك بضع دقائق)..."):
            content_data = {
                "main_keyword": main_keyword,
                "related_keywords": related_keywords,
                "anchors": [a for a in st.session_state.anchors if a['text'] and a['url']],
                "target_domain": target_domain,
                "language": target_language,
                "outline": st.session_state.outline
            }
            article = generate_content(content_data, openai_key)
            st.session_state.article = article
            st.success("✅ تم توليد المقال بنجاح!")
    
    if col_retry.button("🔄 إعادة محاولة الـ Outline", use_container_width=True):
        st.session_state.outline = None
        st.rerun()

# 5. عرض المقال والإحصائيات
if st.session_state.article:
    st.markdown("---")
    st.header("📄 معاينة المقال")
    
    # الإحصائيات
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📊 عدد الكلمات", st.session_state.article.get('word_count', 0))
    col2.metric("🔍 كثافة الكلمة المفتاحية", f"{count_keyword_density(st.session_state.article.get('html', ''), main_keyword)}%")
    col3.metric("🔗 عدد الروابط", len([a for a in st.session_state.anchors if a['text'] and a['url']]))
    col4.metric("✅ الحالة", "جاهز للنشر")
    
    # عرض المحتوى
    with st.expander("📖 المحتوى الكامل", expanded=True):
        st.markdown(st.session_state.article.get("html", ""), unsafe_allow_html=True)
    
    # Meta Description
    if st.session_state.article.get("meta_description"):
        with st.expander("📝 Meta Description"):
            st.write(st.session_state.article["meta_description"])
    
    st.markdown("---")
    
    # خيارات الحفظ والنشر
    st.header("💾 خيارات الحفظ والنشر")
    
    col1, col2, col3 = st.columns(3)
    
    # رفع إلى WordPress
    if col1.button("📤 رفع إلى WordPress", use_container_width=True):
        if wp_url and wp_user and wp_pass:
            with st.spinner("⏳ جاري الرفع إلى WordPress..."):
                status = upload_to_wordpress(wp_url, wp_user, wp_pass, st.session_state.article)
                st.info(status)
        else:
            st.warning("⚠️ يرجى إكمال إعدادات WordPress في الشريط الجانبي")
    
    # حفظ الملفات
    if col2.button("💾 حفظ الملفات", use_container_width=True):
        excel_path = save_to_excel(st.session_state.article, main_keyword)
        docx_path = save_to_docx(st.session_state.article, main_keyword)
        html_path = save_to_html(st.session_state.article, main_keyword)
        
        if excel_path and docx_path and html_path:
            st.success("✅ تم حفظ الملفات بنجاح!")
            
            # عرض أزرار التحميل
            col_excel, col_docx, col_html = st.columns(3)
            
            with open(excel_path, "rb") as f:
                col_excel.download_button(
                    "📊 تحميل Excel",
                    f,
                    file_name=f"{main_keyword}.xlsx",
                    use_container_width=True
                )
            
            with open(docx_path, "rb") as f:
                col_docx.download_button(
                    "📄 تحميل Word",
                    f,
                    file_name=f"{main_keyword}.docx",
                    use_container_width=True
                )
            
            with open(html_path, "rb") as f:
                col_html.download_button(
                    "🌐 تحميل HTML",
                    f,
                    file_name=f"{main_keyword}.html",
                    use_container_width=True
                )
    
    # نسخ إلى الحافظة
    if col3.button("📋 نسخ المحتوى", use_container_width=True):
        st.success("✅ تم نسخ المحتوى إلى الحافظة!")
        st.code(st.session_state.article.get("html", ""))

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; margin-top: 30px;'>
    <p>نظام أتمتة المحتوى الذكي | إصدار 1.1</p>
    <p>مع التركيز على جودة المحتوى ومعايير SEO الحديثة</p>
</div>
""", unsafe_allow_html=True)
