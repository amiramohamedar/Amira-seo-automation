import pandas as pd
from docx import Document
from docx.shared import Inches
import os
from datetime import datetime

class StorageHandler:
    def __init__(self, base_path: str = "exports"):
        self.base_path = base_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)

    def save_to_excel(self, data: list, filename: str = "products_log.xlsx"):
        """حفظ البيانات في ملف إكسيل"""
        path = os.path.join(self.base_path, filename)
        df = pd.DataFrame(data)
        if os.path.exists(path):
            existing_df = pd.read_excel(path)
            df = pd.concat([existing_df, df], ignore_index=True)
        df.to_excel(path, index=False)
        return path

    def save_to_docx(self, title: str, content_html: str, filename: str = None):
        """حفظ المحتوى في ملف Word"""
        if not filename:
            filename = f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        path = os.path.join(self.base_path, filename)
        
        doc = Document()
        doc.add_heading(title, 0)
        
        # ملاحظة: تحويل HTML إلى Docx بشكل بسيط
        # في النسخة المتقدمة يمكن استخدام BeautifulSoup لتنسيق الفقرات والعناوين
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content_html, 'html.parser')
        
        for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
            if element.name == 'h1':
                doc.add_heading(element.get_text(), level=1)
            elif element.name == 'h2':
                doc.add_heading(element.get_text(), level=2)
            elif element.name == 'h3':
                doc.add_heading(element.get_text(), level=3)
            elif element.name == 'li':
                doc.add_paragraph(element.get_text(), style='List Bullet')
            else:
                doc.add_paragraph(element.get_text())
                
        doc.save(path)
        return path

    def upload_to_drive(self, file_path: str, folder_id: str, credentials_json: str = None):
        """
        رفع الملفات إلى Google Drive.
        يتطلب إعداد OAuth2 أو Service Account.
        """
        # هذا الجزء يتطلب إعدادات مسبقة من المستخدم (Credentials)
        # سنضع الهيكل الأساسي
        return f"https://drive.google.com/mock-link-for-{os.path.basename(file_path)}"
