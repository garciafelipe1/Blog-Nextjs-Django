from rest_framework import serializers

from .models import Post,Category,Heading



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields="__all__"

class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields=['name','slug']
    
    

class PostSerializer(serializers.ModelSerializer):
    category=CategorySerializer()
    class Meta:
        model=Post
        fields="__all__"
    

class PostListSerializer(serializers.ModelSerializer):
    category=CategoryListSerializer()
    
    class Meta:
        model=Post
        fields=[
            "id",
            "title",
            "description",
            "thumbnail",
            "slug",
            "category",
        ]    
    
class HeadingSerializer(serializers.ModelSerializer):
    class Meta:
        model=Heading
        fields=[
            "title",
            "slug",
            "level",
            "order",
        ]
 
 
