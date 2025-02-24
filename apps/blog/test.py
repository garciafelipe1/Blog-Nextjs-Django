from django.test import TestCase

from .models import Category,Post,PostAnalytics,Heading

#MODELS TEST
class CategoryModelTest(TestCase):
    def setUp(self):
        self.category=Category.objects.create(
            name="Tech",
            title="Technology",
            description="Tech blog",
            slug="tech",
            
        )
    def test_category_created(self):
        self.assertEqual(str(self.category),"Tech")
        self.assertEqual(self.category.title,"Technology")


class PostModelTest(TestCase):
    def setUp(self):
        self.category=Category.objects.create(
            name="Tech",
            title="Technology",
            description="description test",
            slug="tech", 
        )
        
        self.post=Post.objects.create(
            title="POST 1",
            description="test post",
            content="content for the post",
            thumbnail=None,
            keywords="keywords, test",
            slug="post-1",
            category=self.category,
            status="published",
        )
    def test_post_creation(self):
        self.assertEqual(str(self.post),"POST 1")
        self.assertEqual(self.post.category.name,"Tech")
    
    def test_post_published_manager(self):
        self.assertTrue(Post.postobjects.filter(status="published").exists())
        
class PostAnalyticsModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Analytics",
            slug="analytics", 
        )
        
        self.post = Post.objects.create(
            title="Analytics Post",
            description="Post for analytics",
            content="Analytics content",
            slug="analytics-post",
            category=self.category,
        )
        
        self.analytics = PostAnalytics.objects.create(
            post=self.post,
        )
    
    def test_click_through_rate_updated(self):
        self.analytics.increment_click()
        self.analytics.increment_impressions()
        self.analytics.refresh_from_db()
        self.assertEqual(self.analytics.click_through_rate, 100)


class HeadingModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Headings",
            slug="headings",
        )
        self.post = Post.objects.create(
            title="Heading Post",
            description="Post for headings",
            content="Headings content",
            slug="heading-post",
            category=self.category,
        )
        self.heading = Heading.objects.create(
            post=self.post,
            title="Heading 1",
            slug="heading-1",
            level=1,
            order=1,
        )

    def test_heading_creation(self):
        """Verifica que el heading se crea correctamente"""
        self.assertEqual(self.heading.title, "Heading 1")
        self.assertEqual(self.heading.slug, "heading-1")
        self.assertEqual(self.heading.level, 1)
        self.assertEqual(self.heading.order, 1)
        self.assertEqual(self.heading.post, self.post)
            
            
#VIEWS TEST

