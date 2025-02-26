from django.contrib import admin
from ckeditor.widgets import CKEditorWidget 
from .models import Heading,Category,Post,PostAnalytics
from django import forms

from apps.media.models import Media


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ##que queremos mostrar en el admin
    list_display=('name','title','parent','slug')
    search_fields=('name','title','description','slug')
    prepopulated_fields={'slug':('name',)}
    list_filter=('parent',)
    ordering=('name',)
    readonly_fields=('id',)
    
    

class HeadingInline(admin.TabularInline):
    model = Heading
    extra = 0
    fields=('title','level','order','slug')
    prepopulated_fields={'slug':('title',)}
    ordering=('order',)


  
class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())    
    class Meta:
        model = Post
        fields= '__all__'
 

class MediaInline(admin.TabularInline):
    model = Heading
    fields=(
            "order",
            "name",
            "size",
            "type",
            "key",
            "media_type",)
    extra = 1
     
        
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form=PostAdminForm
    list_display = ('title', 'status', 'category', 'created_at', 'updated_at', 'thubnail_preview')
    search_fields = ('title', 'description', 'slug', 'content', 'keywords')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'category', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')

    fieldsets = (
        ('General Information', {
            'fields': (
                'title',
                'description',
                'content',
                'keywords',
                'slug',
                'category',
            )
        }),
        ('Status & Dates', {  # ← Aquí eliminé el par extra de paréntesis
            'fields': ('status', 'created_at', 'updated_at'),
        }),     
    )
    inlines = [HeadingInline, MediaInline]



# @admin.register(Heading)
# class HeadingAdmin(admin.ModelAdmin):
#     list_display=('title','post','level','order')
#     search_fields=('title','post__title')
#     list_filter=('level','post')
#     ordering=('post','order',)
#     prepopulated_fields={'slug':('title',)}


@admin.register(PostAnalytics)
class PostAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('post_title','views', 'impressions', 'clicks', 'click_through_rate', 'avg_time_on_page')  # Usar un método en lugar de una relación directa
    search_fields = ('post__title',)  # Esto sí es válido
    readonly_fields = ('views', 'impressions', 'clicks', 'click_through_rate', 'avg_time_on_page',)
    ordering = ('-post__created_at',)

    def post_title(self, obj):
        return obj.post.title

    post_title.short_description = 'Post' 
    