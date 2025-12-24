#!/usr/bin/env python3
"""
gitrun - Command Line Interface
تشغيل سكربتات بايثون ودفاتر Jupyter مباشرة من GitHub/GitLab بدون تنزيل كامل
Run Python scripts and Jupyter notebooks directly from GitHub/GitLab without full cloning
"""

import sys
import argparse
from gitrun.core import GitRunner  # تأكد من المسار الصحيح حسب هيكل مجلدك


def create_parser() -> argparse.ArgumentParser:
    """إنشاء parser للأوامر مع وصف ثنائي اللغة"""
    parser = argparse.ArgumentParser(
        prog="gitrun",
        description=(
            "gitrun: شغّل سكربتات بايثون أو دفاتر Jupyter من GitHub/GitLab مباشرة\n"
            "gitrun: Run Python scripts or Jupyter notebooks directly from GitHub/GitLab\n"
            "\n"
            "يدعم تلقائيًا: micrograd, nanoGPT, llm.c وغيرها\n"
            "Automatically supports: micrograd, nanoGPT, llm.c and more"
        ),
        epilog=(
            "أمثلة / Examples:\n"
            "  gitrun https://github.com/karpathy/micrograd                 # يفتح demo.ipynb تلقائيًا\n"
            "  gitrun https://github.com/karpathy/nanoGPT                   # يشغل train.py\n"
            "  gitrun https://github.com/user/repo --script app.py          # تشغيل ملف محدد\n"
            "  gitrun https://github.com/user/repo -v                       # وضع التفاصيل\n"
            "  gitrun https://github.com/user/repo --no-venv                # بدون بيئة افتراضية"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        'repo',
        help="رابط المستودع (GitHub أو GitLab) / Repository URL"
    )

    parser.add_argument(
        '-s', '--script',
        help="اسم الملف المراد تشغيله (مثل main.py أو demo.ipynb) / Specific script/notebook to run"
    )

    parser.add_argument(
        '-b', '--branch',
        default=None,  # مهم جدًا: None عشان الاكتشاف التلقائي يشتغل
        help="فرع المستودع (اختياري - يُكتشف تلقائيًا إذا لم يُحدد) / Branch name (optional - auto-detected if not provided)"
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="عرض معلومات تفصيلية أثناء التشغيل / Enable verbose output"
    )

    parser.add_argument(
        '--no-venv',
        action='store_true',
        help="تشغيل بدون إنشاء بيئة افتراضية معزولة / Run without isolated virtual environment"
    )

    parser.add_argument(
        '--version',
        action='version',
        version='gitrun 0.2.0',  # مطابق لـ pyproject.toml
        help="عرض رقم الإصدار / Show version number"
    )

    # الـ extra arguments للسكربت الأصلي
    parser.add_argument(
        'extra_args',
        nargs='*',
        help=argparse.SUPPRESS  # مخفي في --help لأنه للـ script الأصلي فقط
    )

    return parser


def main():
    """الدالة الرئيسية لتشغيل gitrun"""
    parser = create_parser()
    args = parser.parse_args()

    # إنشاء وتشغيل GitRunner مع الخيارات
    runner = GitRunner(
        repo_url=args.repo,
        branch=args.branch,        # ممكن يكون None → اكتشاف تلقائي
        script=args.script,
        verbose=args.verbose,
        use_venv=not args.no_venv
    )

    try:
        runner.run(args.extra_args)
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف البرنامج بواسطة المستخدم (Interrupted by user)")
        sys.exit(1)
    except Exception as e:
        if args.verbose:
            raise  # إظهار التتبع الكامل في وضع verbose
        print(f"💥 خطأ غير متوقع: {e} (Unexpected error: {e})", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
