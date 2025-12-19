#!/usr/bin/env python3
"""
أدوات مساعدة لـ gitrun
"""
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any


class CacheManager:
    """مدير ذكي للتخزين المؤقت"""
    
    def __init__(self, ttl: int = 3600):  # TTL ساعة واحدة افتراضياً
        self.cache_dir = Path.home() / '.gitrun' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / 'metadata.json'
        self.ttl = ttl
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """تحميل بيانات وصفية للتخزين المؤقت"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_metadata(self):
        """حفظ البيانات الوصفية"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2)
        except IOError:
            pass
    
    def get_cache_key(self, owner: str, repo: str, branch: str, filename: str) -> str:
        """إنشاء مفتاح فريد للتخزين المؤقت"""
        key_str = f"{owner}/{repo}/{branch}/{filename}"
        return hashlib.sha256(key_str.encode()).hexdigest()[:16]
    
    def is_valid(self, key: str) -> bool:
        """التحقق من صلاحية العنصر المخزن"""
        if key not in self.metadata:
            return False
        
        cache_time = self.metadata[key].get('timestamp', 0)
        current_time = time.time()
        
        return (current_time - cache_time) < self.ttl
    
    def get_cached(self, key: str) -> Optional[str]:
        """جلب محتوى من التخزين المؤقت"""
        if not self.is_valid(key):
            return None
        
        cache_file = self.cache_dir / f"{key}.cache"
        if cache_file.exists():
            try:
                return cache_file.read_text(encoding='utf-8')
            except IOError:
                return None
        return None
    
    def set_cache(self, key: str, content: str):
        """حفظ محتوى في التخزين المؤقت"""
        cache_file = self.cache_dir / f"{key}.cache"
        
        try:
            cache_file.write_text(content, encoding='utf-8')
            
            # تحديث البيانات الوصفية
            self.metadata[key] = {
                'timestamp': time.time(),
                'size': len(content)
            }
            self._save_metadata()
        except IOError:
            pass
    
    def clear_cache(self):
        """مسح التخزين المؤقت بالكامل"""
        if self.cache_dir.exists():
            for file in self.cache_dir.glob("*.cache"):
                file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
            self.metadata = {}


def get_file_hash(content: str) -> str:
    """إنشاء هاش لمحتوى الملف"""
    return hashlib.md5(content.encode()).hexdigest()


def display_size(bytes_size: int) -> str:
    """عرض الحجم بتنسيق مقروء"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"
