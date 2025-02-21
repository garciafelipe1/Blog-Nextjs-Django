from django.contrib import admin
from ckeditor.widgets import CKEditorWidget 
from .models import Heading,Category,Post
from django import forms


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ##que queremos mostrar en el admin
    list_display=('name','title','parent','slug')
    search_fields=('name','title','description','slug')
    prepopulated_fields={'slug':('name',)}
    list_filter=('parent',)
    ordering=('name',)
    readonly_fields=('id',)
    
    
class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())    
    class Meta:
        model = Post
        fields= '__all__'
 
class HeadingInline(admin.TabularInline):
    model = Heading
    extra = 0
    fields=('title','level','order','slug')
    prepopulated_fields={'slug':('title',)}
    ordering=('order',)
       
        
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form=PostAdminForm
    list_display = ('title', 'status', 'category', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'slug', 'content', 'keywords')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('status', 'category', 'updated_at')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at',)

    fieldsets = (
        ('General Information', {
            'fields': (
                'title',
                'description',
                'content',
                'thumbnail',
                'keywords',
                'slug',
                'category',
            )
        }),
        ('Status & Dates', {  # ← Aquí eliminé el par extra de paréntesis
            'fields': ('status', 'created_at', 'updated_at'),
        }),     
    )
    inlines = [HeadingInline]



# @admin.register(Heading)
# class HeadingAdmin(admin.ModelAdmin):
#     list_display=('title','post','level','order')
#     search_fields=('title','post__title')
#     list_filter=('level','post')
#     ordering=('post','order',)
#     prepopulated_fields={'slug':('title',)}