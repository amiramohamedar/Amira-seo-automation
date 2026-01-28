import requests
import base64

def upload_to_wordpress(url, user, password, article):
    """
    يرفع المقال إلى WordPress كمسودة.
    """
    endpoint = f"{url.rstrip('/')}/wp-json/wp/v2/posts"
    
    # تشفير بيانات الاعتماد (Application Password)
    credentials = f"{user}:{password}"
    token = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "title": article["title"],
        "content": article["html"],
        "status": "draft"
    }
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 201:
            return f"✅ تم رفع المقال بنجاح كمسودة! رابط المقال: {response.json().get('link')}"
        else:
            return f"❌ فشل الرفع: {response.text}"
    except Exception as e:
        return f"❌ خطأ في الاتصال: {str(e)}"
