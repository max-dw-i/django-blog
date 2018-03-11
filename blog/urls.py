from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # if the url is '', use urls.py in blog_app (that's what include() does)
    path('', include('blog_app.urls')),
    path('accounts/', include('accounts.urls')),
]
