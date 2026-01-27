import requests
import json
import base64

class WordPressHandler:
    def __init__(self, site_url: str, username: str, app_password: str):
        self.site_url = site_url.rstrip('/')
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        self.auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()
        self.headers = {
            'Authorization': f'Basic {self.auth}',
            'Content-Type': 'application/json'
        }

    def post_article(self, title: str, content: str, status: str = 'draft') -> dict:
        """رفع المقال إلى ووردبريس"""
        endpoint = f"{self.api_url}/posts"
        data = {
            'title': title,
            'content': content,
            'status': status
        }
        
        try:
            response = requests.post(endpoint, headers=self.headers, json=data)
            if response.status_code in [200, 201]:
                return {"success": True, "link": response.json().get('link'), "id": response.json().get('id')}
            else:
                return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
