from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('login/', views.logins, name='login'),
    path('product/', views.product, name='product'),
    path('cart/',views.cart, name='cart'),
    path('upload/', views.upload_offer, name='upload_offer'),
    path('upload_product/', views.upload_product, name='upload_product'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('logout/', views.logout_user, name='logout'),
    path('send_whatsapp/', views.send_whatsapp_order, name='send_whatsapp'),
]
#+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
