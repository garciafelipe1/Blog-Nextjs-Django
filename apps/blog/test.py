from django.test import TestCase
from django.urls import reverse
from .models import Category,Post,PostAnalytics,Heading
from django.core.cache import cache
from django.conf import settings
from rest_framework.test import APIClient
from unittest.mock import patch
from rest_framework.status import HTTP_200_OK
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework import status



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

class PostListViewTest(TestCase):
    
    def setUp(self):
        
        self.client = APIClient()
        cache.clear()
        self.category = Category.objects.create(
            name="API",
            slug="api",
        )
        self.api_key = settings.VALID_API_KEYS[0]
        self.post = Post.objects.create(
            title="Heading Post",
            description="Post for headings",
            content="Headings content",
            slug="heading-post",
            category=self.category,
            status="published",
        )
    
    def tearDown(self):
        cache.clear() 
        
    def test_get_post_list(self):
        url = reverse('post-list')
        response = self.client.get(
            url,
            HTTP_API_KEY=self.api_key,)
        
        
        data = response.json()
        
        self.assertIn('success',data)
        self.assertTrue(data['success'])
        self.assertIn('status',data)
        self.assertEqual(data['status'],200)
        self.assertIn('results',data)
        self.assertEquals(data['count'],1)
        
        results=data['results']
        self.assertEqual(len(results),1)
        
        post_data=results[0]
        self.assertEqual(post_data['id'], str(self.post.id))
        self.assertEqual(post_data['title'], self.post.title)
        self.assertEqual(post_data['description'], self.post.description)
        self.assertIsNone(post_data['thumbnail'], self.post.thumbnail)
        self.assertEqual(post_data['slug'], self.post.slug)
        
        category_data=post_data['category']
        self.assertEqual(category_data['name'],self.category.name)
        self.assertEqual(category_data['slug'],self.category.slug)
        self.assertEqual(post_data['view_count'],0)
        
    

class PostDetailViewTest(TestCase):
    def setUp(self):
        
        self.client = APIClient()
        cache.clear()
        self.category = Category.objects.create(
            name="API",
            slug="api",
        )
        self.api_key = settings.VALID_API_KEYS[0]
        self.post = Post.objects.create(
            title="Heading Post",
            description="Post for headings",
            content="Headings content",
            slug="heading-post",
            category=self.category,
            status="published",
        )
    def tearDown(self):
        cache.clear() 
    
    @patch('apps.blog.tasks.increment_post_views_tasks.delay') 
    def test_get_post_detail_success(self,mock_increment_views):
        
        url = reverse('post-detail') + f"?slug={self.post.slug}"
        response = self.client.get(
            url,
            HTTP_API_KEY=self.api_key,
        )
        
        self.assertEqual(response.status_code,status.HTTP_200_OK)  
        
        data=response.json()
        
        print(data)
        
        self.assertIn('success',data)
        self.assertTrue(data['success'])
        self.assertIn('status',data)
        self.assertEqual(data['status'],200)
        self.assertIn('results',data)
        
        
        
        post_data=data['results']
        print(post_data)
        self.assertEqual(post_data['id'], str(self.post.id))
        self.assertEqual(post_data['title'], self.post.title)
        self.assertEqual(post_data['description'], self.post.description)
        self.assertIsNone(post_data['thumbnail'], self.post.thumbnail)
        self.assertEqual(post_data['slug'], self.post.slug)
        
        category_data=post_data['category']
        self.assertEqual(category_data['name'],self.category.name)
        self.assertEqual(category_data['slug'],self.category.slug)
        self.assertEqual(post_data['view_count'],0)
       
        
        
        mock_increment_views.assert_called_once_with(self.post.slug,'127.0.0.1')
        
        
    @patch('apps.blog.tasks.increment_post_views_tasks.delay')
    def test_get_post_detail_not_found(self, mock_increment_views):
        url = reverse('post-detail') + f"?slug=non-existent-slug"
        response = self.client.get(
            url,
            HTTP_API_KEY=self.api_key,
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  

        data = response.json()

        # Asegurar que la clave 'detail' existe en la respuesta
        self.assertIn('detail', data)

        # Asegurar que el mensaje de error es el esperado
        self.assertEqual(data['detail'], "Post does not exist")

        # Para depuración
        


class PostHeadingsViewTest(TestCase):
    
    
    def setUp(self):
        self.client = APIClient()
        cache.clear()
        self.api_key = settings.VALID_API_KEYS[0]

        self.category = Category.objects.create(
            name="Test Category",
            slug="test-category",
        )

        self.post = Post.objects.create(
            title="Test Post",
            description="Test Post Description",
            content="Test Post Content",
            slug="test-post",
            category=self.category,
            status="published",
        )

        self.heading1 = Heading.objects.create(
            post=self.post,
            title="Test Heading 1",
            slug="test-heading-1",
            level=1,
            order=1,
        )

        self.heading2 = Heading.objects.create(
            post=self.post,
            title="Test Heading 2",
            slug="test-heading-2",
            level=2,
            order=2,    
        )
        
    def tearDown(self):
        cache.clear()  
    
    def test_get_post_headings_success(self):
        url = reverse('post-headings') + f"?slug={self.post.slug}"

        response = self.client.get(
            url,
            HTTP_API_KEY=self.api_key,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 200)
        self.assertIn('results', data)

        results = data['results']
        self.assertEqual(len(results), 2)

        # Verificar el primer heading
        self.assertEqual(results[0]['title'], self.heading1.title)
        self.assertEqual(results[0]['slug'], self.heading1.slug)
        self.assertEqual(results[0]['level'], self.heading1.level)

        # Verificar el segundo heading
        self.assertEqual(results[1]['title'], self.heading2.title)
        self.assertEqual(results[1]['slug'], self.heading2.slug)
        self.assertEqual(results[1]['level'], self.heading2.level)

    def test_get_post_headings_failure(self):
        url = reverse('post-headings') + "?slug=non-existent-slug"

        response = self.client.get(
            url,
            HTTP_API_KEY=self.api_key
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        print("API Response:", data)  # <-- Agrega esto para ver la respuesta real

        self.assertTrue(data['success'])    # Aquí está el problema
        self.assertEqual(data['status'], 200)
        self.assertEqual(len(data['results']), 0)


class IncrementPostClickViewTest(TestCase): 
    def setUp(self):
        self.client = APIClient()
        cache.clear()
        self.api_key = settings.VALID_API_KEYS[0]
        
        # Crear una categoría sin referenciar self.category en sí misma
        self.category = Category.objects.create(name="Analytics Category",slug="analytics-category")
        
        # Suponiendo que tienes un modelo Post y lo creas para usar su slug
        self.post = Post.objects.create(
            title="Test Post",
            description="Test Post Description",
            content="content",
            slug="test-post",
            category=self.category,
            status="published"
        )
            
    def tearDown(self):
        cache.clear()          
        
    def test_increment_post_click_success(self):
        url = reverse('increment-post-clicks')

        response = self.client.post(
            url,
            {"slug": self.post.slug},
            HTTP_API_KEY=self.api_key,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertIn("success", data)
        self.assertTrue(data["success"])
        self.assertIn("status", data)
        self.assertEqual(data["status"], 200)
        self.assertIn("results", data)
        
        result=data['results']
        self.assertIn("message", result)
        self.assertEqual(result["message"], "Click incremented successfully")
        self.assertIn("clicks", result)
        
        self.assertEqual(result["clicks"], 1)
        
        from apps.blog.models import PostAnalytics
        post_analytics = PostAnalytics.objects.get(post=self.post)
        self.assertEqual(post_analytics.clicks, 1)
        
