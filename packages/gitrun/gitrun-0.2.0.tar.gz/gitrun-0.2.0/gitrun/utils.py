#!/usr/bin/env python3
"""
gitrun Utilities & Cache Manager
===============================

أدوات مساعدة ومدير تخزين مؤقت ذكي لتحسين الأداء
Helper utilities and smart cache manager to improve performance by avoiding repeated downloads
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any


class CacheManager:
    """
    مدير تخزين مؤقت ذكي للملفات المجلوبة من GitHub/GitLab
    Smart cache manager for files fetched from remote repositories

    يخزن الملفات محليًا في ~/.gitrun/cache مع صلاحية زمنية (TTL)
    Caches files locally with time-to-live (TTL) to reduce network requests
    """

    def __init__(self, ttl: int = 3600):  # 1 hour default TTL
        """
        تهيئة مدير التخزين المؤقت

        Args:
            ttl (int): مدة الصلاحية بالثواني (افتراضي: ساعة) / Cache validity in seconds (default: 1 hour)
        """
        self.cache_dir = Path.home() / '.gitrun' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / 'metadata.json'
        self.ttl = ttl
        self.metadata: Dict[str, Any] = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """تحميل بيانات وصفية من ملف JSON / Load metadata from JSON file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ فشل تحميل بيانات التخزين المؤقت (سيتم إعادة إنشائها)\n"
                      f"    Warning: Failed to load cache metadata (will be recreated): {e}")
                return {}
        return {}

    def _save_metadata(self):
        """حفظ البيانات الوصفية إلى ملف JSON / Save metadata to JSON file"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"⚠️ فشل حفظ بيانات التخزين المؤقت\n"
                  f"    Warning: Failed to save cache metadata: {e}")

    def get_cache_key(self, owner: str, repo: str, branch: str, filename: str) -> str:
        """
        إنشاء مفتاح تخزين فريد بناءً على تفاصيل الملف
        Generate a unique cache key based on repository and file details
        """
        key_str = f"{owner.lower()}/{repo.lower()}/{branch}/{filename}"
        return hashlib.sha256(key_str.encode('utf-8')).hexdigest()[:16]

    def is_valid(self, key: str) -> bool:
        """التحقق من صلاحية العنصر المخزن / Check if cached item is still valid"""
        if key not in self.metadata:
            return False
        cache_time = self.metadata[key].get('timestamp', 0)
        return (time.time() - cache_time) < self.ttl

    def get_cached(self, key: str) -> Optional[str]:
        """
        جلب محتوى من التخزين المؤقت إذا كان صالحًا
        Retrieve cached content if valid and exists
        """
        if not self.is_valid(key):
            return None

        cache_file = self.cache_dir / f"{key}.cache"
        if cache_file.exists():
            try:
                return cache_file.read_text(encoding='utf-8')
            except IOError as e:
                print(f"⚠️ فشل قراءة الملف المخزن مؤقتًا\n"
                      f"    Warning: Failed to read cached file: {e}")
        return None

    def set_cache(self, key: str, content: str):
        """
        حفظ محتوى في التخزين المؤقت مع تحديث البيانات الوصفية
        Cache content and update metadata
        """
        cache_file = self.cache_dir / f"{key}.cache"
        try:
            cache_file.write_text(content, encoding='utf-8')

            self.metadata[key] = {
                'timestamp': time.time(),
                'size': len(content),
                'display_size': display_size(len(content))
            }
            self._save_metadata()

            if os.getenv('GITRUN_VERBOSE'):  # فقط في وضع verbose
                print(f"💾 تم تخزين الملف مؤقتًا ({display_size(len(content))})\n"
                      f"    Cached file ({display_size(len(content))})")
        except IOError as e:
            print(f"⚠️ فشل حفظ الملف في التخزين المؤقت\n"
                  f"    Warning: Failed to cache file: {e}")

    def clear_cache(self):
        """مسح التخزين المؤقت بالكامل / Clear all cached files and metadata"""
        try:
            for file in self.cache_dir.glob("*.cache"):
                file.unlink()
            if self.metadata_file.exists():
                self.metadata_file.unlink()
            self.metadata.clear()
            print("🧹 تم مسح التخزين المؤقت بالكامل / Cache cleared successfully")
        except Exception as e:
            print(f"⚠️ فشل مسح التخزين المؤقت\n"
                  f"    Warning: Failed to clear cache: {e}")


def get_file_hash(content: str) -> str:
    """
    إنشاء هاش MD5 لمحتوى الملف (للمقارنة أو التحقق)
    Generate MD5 hash of file content
    """
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def display_size(bytes_size: int) -> str:
    """
    تحويل حجم البايت إلى وحدة مقروءة (KB, MB, ...)
    Convert bytes to human-readable format
    """
    if bytes_size == 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"
