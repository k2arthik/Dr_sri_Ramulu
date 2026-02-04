import os
import django
import uuid
import datetime

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from utils.dynamodb import save_blog

def seed_blogs():
    samples = [
        {
            'title': 'The Importance of Regular Cardiac Checkups',
            'slug': 'importance-of-cardiac-checkups',
            'body': '''
<p>Maintaining a healthy heart is a lifelong commitment. Regular cardiac checkups are essential for early detection of potential issues.</p>
<h2>Why Checkups Matter</h2>
<ul>
    <li>Early detection of hypertension.</li>
    <li>Monitoring cholesterol levels.</li>
    <li>Assessing overall cardiovascular risk.</li>
</ul>
<p>Don't wait for symptoms to appear. Schedule your checkup today.</p>
''',
            'thumbnail': 'https://plus.unsplash.com/premium_photo-1673322194344-96ae4b2c1294?q=80&w=2070&auto=format&fit=crop',
            'draft': False,
            'category': 'Cardiology',
            'meta_description': 'Learn why regular heart checkups are vital for long-term health and early disease prevention.'
        },
        {
            'title': 'Healthy Diet for a Stronger Heart',
            'slug': 'healthy-diet-stronger-heart',
            'body': '''
<p>What you eat significantly impacts your heart health. A balanced diet rich in fruits, vegetables, and whole grains can lower your risk of heart disease.</p>
<blockquote>"Let food be thy medicine and medicine be thy food."</blockquote>
<p>Incorporate more Omega-3 fatty acids and reduce processed sugar intake for better cardiovascular outcomes.</p>
''',
            'thumbnail': 'https://plus.unsplash.com/premium_photo-1663852297267-827c73e7529e?q=80&w=2070&auto=format&fit=crop',
            'draft': False,
            'category': 'Lifestyle',
            'meta_description': 'Discover the best foods for heart health and how a balanced diet can protect your cardiovascular system.'
        },
        {
            'title': 'Modern Advancements in Interventional Cardiology',
            'slug': 'advancements-interventional-cardiology',
            'body': '''
<p>Interventional cardiology has seen remarkable progress in recent years. Procedures like TAVR and advanced stenting have revolutionized patient care.</p>
<p>These minimally invasive techniques lead to faster recovery times and better long-term results for patients with complex heart conditions.</p>
''',
            'thumbnail': 'https://images.unsplash.com/photo-1576091160550-2173dba999ef?q=80&w=2070&auto=format&fit=crop',
            'draft': False,
            'category': 'Technology',
            'meta_description': 'Exploring the latest breakthroughs in minimally invasive heart procedures and their benefits for patients.'
        }
    ]

    for sample in samples:
        print(f"Adding blog: {sample['title']}...")
        blog_data = {
            'id': str(uuid.uuid4()),
            'datetime': datetime.datetime.now().isoformat(),
            **sample
        }
        save_blog(blog_data)
    
    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_blogs()
