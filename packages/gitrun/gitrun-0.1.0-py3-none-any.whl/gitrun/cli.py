#!/usr/bin/env python3
"""
واجهة سطر الأوامر لـ gitrun
"""
import sys
import argparse
from gitrun.core import GitRunner
from gitrun.utils import CacheManager


def main():
    parser = argparse.ArgumentParser(
        description='🚀 gitrun - تشغيل سكربتات بايثون مباشرة من GitHub/GitLab',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
أمثلة:
  %(prog)s https://github.com/user/repo
  %(prog)s https://github.com/user/repo --script app.py
  %(prog)s https://github.com/user/repo --branch develop --verbose
  %(prog)s https://gitlab.com/user/project
  %(prog)s https://github.com/user/repo --no-venv  # بدون بيئة افتراضية
  %(prog)s https://github.com/user/repo -- --help  # تمرير --help للسكربت الأصلي

ملاحظة:
  • يتم تثبيت المتطلبات تلقائياً من requirements.txt
  • يتم إنشاء بيئة افتراضية مؤقتة لعزل التثبيتات
  • الملفات المؤقتة تُحذف تلقائياً بعد التشغيل
        """
    )
    
    parser.add_argument(
        'repo',
        help='رابط المستودع (مثال: https://github.com/user/repo)'
    )
    
    parser.add_argument(
        'script_args',
        nargs=argparse.REMAINDER,
        help='Arguments للسكربت الأصلي (استخدم -- لفصلها)'
    )
    
    parser.add_argument(
        '-s', '--script',
        help='اسم السكربت المراد تشغيله (افتراضي: الاكتشاف التلقائي)'
    )
    
    parser.add_argument(
        '-b', '--branch',
        default='main',
        help='فرع المستودع (افتراضي: main)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='عرض معلومات تفصيلية'
    )
    
    parser.add_argument(
        '--no-venv',
        action='store_true',
        help='تشغيل بدون بيئة افتراضية (استخدام البيئة الحالية)'
    )
    
    parser.add_argument(
        '--clear-cache',
        action='store_true',
        help='مسح التخزين المؤقت'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='gitrun 0.1.0'
    )
    
    args = parser.parse_args()
    
    # مسح التخزين المؤقت إذا طُلب
    if args.clear_cache:
        cache = CacheManager()
        cache.clear_cache()
        print("✅ تم مسح التخزين المؤقت")
        return
    
    # فصل arguments الخاصة بنا عن arguments الخاصة بالسكربت
    script_args = args.script_args
    if script_args and script_args[0] == '--':
        script_args = script_args[1:]
    
    # إنشاء وتشغيل GitRunner
    runner = GitRunner(
        repo_url=args.repo,
        branch=args.branch,
        script=args.script,
        verbose=args.verbose,
        use_venv=not args.no_venv
    )
    
    runner.run(script_args)


if __name__ == '__main__':
    main()
