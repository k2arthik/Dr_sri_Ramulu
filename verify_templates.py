import os
import django
from django.conf import settings
from django.template import Template, Context, TemplateSyntaxError

# Setup minimal django
if not settings.configured:
    settings.configure(
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['templates/html'],
            'OPTIONS': {
                'libraries': {
                    'custom_tags': 'project.templatetags.custom_tags',
                    'static': 'django.templatetags.static',
                    'django_browser_reload': 'django_browser_reload.templatetags.django_browser_reload',
                    'tailwind_tags': 'tailwind.templatetags.tailwind_tags',
                }
            }
        }],
        INSTALLED_APPS=['django.contrib.staticfiles', 'blog', 'inquiry', 'user', 'project', 'tailwind', 'django_browser_reload'],
        STATIC_URL='/static/',
        BASE_DIR=os.getcwd(),
        PROJECT_TITLE="Test",
        ANALYTICS_TAG_ID="TEST",
    )
    django.setup()

def check_template(path):
    print(f"Checking {path}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            Template(f.read())
        print("OK")
    except TemplateSyntaxError as e:
        print(f"ERROR: {e}")
    except Exception as e:
        print(f"OTHER ERROR: {e}")

if __name__ == "__main__":
    check_template('templates/html/home.html')
    check_template('templates/html/base.html')
