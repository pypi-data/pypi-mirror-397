#!/usr/bin/env python3
"""
gitrun Core Engine
==================

تشغيل سكربتات بايثون ودفاتر Jupyter مباشرة من GitHub/GitLab بدون تنزيل كامل
مع اكتشاف ذكي للفرع الافتراضي، دعم بيئة افتراضية معزولة، وتخزين مؤقت ذكي

Run Python scripts and Jupyter notebooks directly from GitHub/GitLab
with smart default branch detection, isolated virtual environments, and intelligent caching.
"""

import os
import sys
import tempfile
import shutil
import subprocess
import requests
from typing import Optional, List, Tuple
from urllib.parse import urlparse
import venv
import platform

from gitrun.utils import CacheManager  # مدير التخزين المؤقت الذكي


class GitRunner:
    """
    المحرك الرئيسي لـ gitrun
    Main engine for executing remote Python code safely and efficiently
    """

    SUPPORTED_PLATFORMS = {
        'github': {
            'raw_template': 'https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}',
            'api_template': 'https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={ref}'
        },
        'gitlab': {
            'raw_template': 'https://gitlab.com/{owner}/{repo}/-/raw/{ref}/{path}',
            'api_template': 'https://gitlab.com/api/v4/projects/{owner}%2F{repo}/repository/files/{path}?ref={ref}'
        }
    }

    def __init__(
        self,
        repo_url: str,
        branch: Optional[str] = None,
        script: Optional[str] = None,
        verbose: bool = False,
        use_venv: bool = True
    ):
        """
        تهيئة GitRunner

        Parameters:
            repo_url (str): رابط المستودع / Repository URL
            branch (Optional[str]): الفرع (اختياري - يُكتشف تلقائيًا) / Branch (auto-detected if None)
            script (Optional[str]): ملف محدد للتشغيل / Specific file to run
            verbose (bool): وضع التفاصيل / Verbose mode
            use_venv (bool): استخدام بيئة افتراضية / Use isolated venv
        """
        self.repo_url = repo_url.rstrip('/')
        self.branch = branch  # May be None → auto-detect
        self.script = script
        self.verbose = verbose
        self.use_venv = use_venv
        self.temp_dir = tempfile.mkdtemp(prefix='gitrun_')

        self.platform, self.owner, self.repo = self._parse_repo_url()

        # Smart branch resolution - التحديد الذكي للفرع
        self._resolve_branch()

        # تهيئة مدير التخزين المؤقت / Initialize cache manager
        self.cache = CacheManager(ttl=3600)  # ساعة واحدة صلاحية
        if self.verbose:
            print("💾 التخزين المؤقت مفعّل / Cache enabled (~/.gitrun/cache)")

        if self.verbose:
            print(f"🌿 الفرع المستخدم / Using branch: {self.branch}")
            print(f"🔍 المستودع / Repository: {self.owner}/{self.repo} ({self.platform})")
            print(f"📁 المجلد المؤقت / Temp directory: {self.temp_dir}")

    def _parse_repo_url(self) -> Tuple[str, str, str]:
        """تحليل رابط المستودع واستخراج المنصة والمالك والاسم"""
        parsed = urlparse(self.repo_url)
        host = parsed.netloc.lower()
        path_parts = parsed.path.strip('/').split('/')

        if 'github' in host:
            platform = 'github'
        elif 'gitlab' in host:
            platform = 'gitlab'
        else:
            raise ValueError(f"المنصة غير مدعومة / Unsupported platform: {host}")

        if len(path_parts) < 2:
            raise ValueError("رابط المستودع غير صحيح / Invalid repository URL")

        owner = path_parts[0]
        repo = path_parts[1].removesuffix('.git')
        return platform, owner, repo

    def _get_default_branch(self) -> str:
        """جلب الفرع الافتراضي من GitHub API مع fallback آمن"""
        if self.platform != 'github':
            return 'master'  # GitLab fallback

        try:
            api_url = f'https://api.github.com/repos/{self.owner}/{self.repo}'
            if self.verbose:
                print(f"🔍 جلب الفرع الافتراضي / Fetching default branch from: {api_url}")
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                default_branch = response.json().get('default_branch')
                if default_branch:
                    if self.verbose:
                        print(f"✅ الفرع الافتراضي / Default branch: {default_branch}")
                    return default_branch
        except Exception as e:
            if self.verbose:
                print(f"⚠️ فشل جلب الفرع الافتراضي / Failed to fetch default branch: {e}")

        if self.verbose:
            print("🔄 استخدام الفرع الاحتياطي master / Falling back to 'master'")
        return 'master'

    def _resolve_branch(self):
        """تحديد الفرع النهائي بذكاء كامل - Smart branch resolution"""
        if self.branch:
            test_url = f'https://api.github.com/repos/{self.owner}/{self.repo}/contents?ref={self.branch}'
            try:
                if requests.head(test_url, timeout=5).status_code == 200:
                    if self.verbose:
                        print(f"✅ الفرع المحدد موجود / Specified branch '{self.branch}' exists")
                    return
            except:
                pass
            print(f"⚠️ الفرع '{self.branch}' غير موجود، جاري استخدام الفرع الافتراضي...\n"
                  f"    Warning: Branch '{self.branch}' not found, using default branch...")

        # Auto-detect default branch
        self.branch = self._get_default_branch()

    def _get_raw_url(self, path: str = '') -> str:
        """إنشاء رابط خام للملف / Generate raw file URL"""
        template = self.SUPPORTED_PLATFORMS[self.platform]['raw_template']
        return template.format(owner=self.owner, repo=self.repo, ref=self.branch, path=path)

    def _fetch_file(self, filename: str) -> Optional[str]:
        """جلب محتوى ملف مع دعم التخزين المؤقت الذكي / Fetch file with smart caching"""
        # إنشاء مفتاح الكاش الفريد
        cache_key = self.cache.get_cache_key(self.owner, self.repo, self.branch, filename)

        # جرب جلب من الكاش أولاً
        cached_content = self.cache.get_cached(cache_key)
        if cached_content is not None:
            if self.verbose:
                print(f"✅ تم جلب '{filename}' من التخزين المؤقت / Cached hit for '{filename}'")
            return cached_content

        # لو مش موجود في الكاش → جلب من الإنترنت
        url = self._get_raw_url(filename)
        if self.verbose:
            print(f"📥 جلب من الإنترنت / Downloading: {url}")

        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                content = response.text
                # حفظ في الكاش للاستخدام المستقبلي
                self.cache.set_cache(cache_key, content)
                if self.verbose:
                    print(f"💾 تم حفظ '{filename}' في التخزين المؤقت / Cached '{filename}'")
                return content
            else:
                if self.verbose:
                    print(f"⚠️ فشل جلب الملف (HTTP {response.status_code})")
                return None
        except Exception as e:
            if self.verbose:
                print(f"⚠️ خطأ في الاتصال أثناء جلب '{filename}' / Network error: {e}")
            return None

    def _setup_virtualenv(self) -> Tuple[str, str]:
        """إنشاء بيئة افتراضية معزولة"""
        if not self.use_venv:
            return sys.executable, f"{sys.executable} -m pip"

        venv_dir = os.path.join(self.temp_dir, "venv")
        if self.verbose:
            print(f"🔧 إنشاء بيئة افتراضية / Creating virtual environment: {venv_dir}")
        venv.create(venv_dir, with_pip=True)

        if platform.system() == "Windows":
            python_path = os.path.join(venv_dir, "Scripts", "python.exe")
            pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
        else:
            python_path = os.path.join(venv_dir, "bin", "python")
            pip_path = os.path.join(venv_dir, "bin", "pip")

        return python_path, pip_path

    def install_requirements(self, python_path: str, pip_path: str):
        """تثبيت requirements.txt إن وجد"""
        content = self._fetch_file('requirements.txt')
        if not content:
            if self.verbose:
                print("ℹ️ لا يوجد requirements.txt / No requirements.txt found")
            return

        req_path = os.path.join(self.temp_dir, 'requirements.txt')
        with open(req_path, 'w', encoding='utf-8') as f:
            f.write(content)

        if self.verbose:
            print("📦 تثبيت المتطلبات / Installing requirements...")
        result = subprocess.run(
            [pip_path, "install", "-r", req_path],
            capture_output=not self.verbose,
            text=True,
            cwd=self.temp_dir
        )

        if result.returncode == 0:
            print("✅ تم تثبيت المتطلبات بنجاح / Requirements installed successfully")
        else:
            print("⚠️ فشل تثبيت بعض المتطلبات (نستمر) / Some requirements failed (continuing anyway)")

    def _list_root_files(self) -> List[str]:
        """جلب قائمة الملفات في جذر المستودع"""
        try:
            if self.platform == 'github':
                api_url = f'https://api.github.com/repos/{self.owner}/{self.repo}/contents?ref={self.branch}'
                if self.verbose:
                    print(f"📂 جلب محتويات الجذر / Fetching root contents: {api_url}")
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    return [item['name'] for item in response.json()]
        except Exception as e:
            if self.verbose:
                print(f"⚠️ فشل جلب الملفات / Failed to list files: {e}")
        return []

    def detect_main_script(self) -> Tuple[str, str]:
        """اكتشاف الملف الرئيسي تلقائيًا (notebook أو script)"""
        root_files = self._list_root_files()
        if self.verbose:
            print(f"📂 الملفات في الجذر / Root files: {root_files}")

        # User-specified script
        if self.script:
            script_type = 'notebook' if self.script.endswith('.ipynb') else 'script'
            return self.script, script_type

        # Preferred Jupyter notebooks
        notebooks = [f for f in root_files if f.endswith('.ipynb')]
        common_notebooks = ['demo.ipynb', 'main.ipynb', 'example.ipynb', 'tutorial.ipynb', 'index.ipynb']
        for nb in common_notebooks:
            if nb in notebooks:
                return nb, 'notebook'
        if notebooks:
            return notebooks[0], 'notebook'

        # Common Python scripts
        common_scripts = ['main.py', 'app.py', 'run.py', 'cli.py', 'index.py', 'script.py', 'start.py', 'train.py']
        for script in common_scripts:
            if script in root_files:
                return script, 'script'

        # Any Python file
        py_files = [f for f in root_files if f.endswith('.py')]
        if py_files:
            return py_files[0], 'script'

        raise FileNotFoundError("لم أجد ملف قابل للتشغيل تلقائيًا / No executable file found automatically")

    def run_script(self, python_path: str, user_args: List[str] = None):
        """تنزيل وتشغيل الملف المكتشف"""
        if user_args is None:
            user_args = []

        script_name, script_type = self.detect_main_script()

        content = self._fetch_file(script_name)
        if content is None:
            raise FileNotFoundError(f"لم أستطع جلب الملف / Could not fetch file: {script_name}")

        script_path = os.path.join(self.temp_dir, script_name)
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"🚀 تشغيل / Running: {script_name} من / from {self.owner}/{self.repo} (فرع / branch: {self.branch})")

        if script_type == 'notebook':
            print("📓 تم اكتشاف دفتر Jupyter — تثبيت jupyterlab وفتحه...\n"
                  "    Detected Jupyter Notebook — Installing jupyterlab and launching...")
            subprocess.run([python_path, '-m', 'pip', 'install', 'jupyterlab>=4.0.0'], cwd=self.temp_dir, check=False)
            cmd = [python_path, '-m', 'jupyter', 'lab', script_name]
        else:
            cmd = [python_path, script_path] + user_args

        if self.verbose:
            print(f"⚡ الأمر المستخدم / Command: {' '.join(cmd)}")

        subprocess.run(cmd, cwd=self.temp_dir, check=False)

    def cleanup(self):
        """تنظيف المجلد المؤقت بعد الانتهاء"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            if self.verbose:
                print(f"🧹 تم تنظيف المجلد المؤقت / Cleaned up temporary directory")

    def run(self, user_args: List[str] = None):
        """الدالة الرئيسية لتشغيل العملية كاملة"""
        if user_args is None:
            user_args = []

        try:
            python_path, pip_path = self._setup_virtualenv()
            self.install_requirements(python_path, pip_path)
            self.run_script(python_path, user_args)
        except KeyboardInterrupt:
            print("\n⏹️ تم إيقاف التشغيل بواسطة المستخدم / Interrupted by user")
        except FileNotFoundError as e:
            print(f"💥 {e}")
            print("💡 تلميح / Hint: هذا المستودع قد يحتاج تنزيل يدوي:")
            print(f"   git clone {self.repo_url}")
            print(f"   cd {self.repo.split('/')[-1]}")
            print("   jupyter lab   # إذا كان دفتر Jupyter")
            sys.exit(1)
        except Exception as e:
            print(f"💥 خطأ غير متوقع / Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            self.cleanup()
