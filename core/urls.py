from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
		path('register/',views.RegisterView.as_view(),name='index'),
		path('dashboard/',views.DashboardView.as_view(),name='dashboard'),
		path('logout',views.logout_user,name='logout'),
		path('transact/',views.TransactionView.as_view(),name='transact'),
		path('profile/',views.ProfileView.as_view(),name='profile'),
		path('profile/edit',views.EditProfileView.as_view(),name='edit-profile'),
		
		# path('payment/',views.payment,name='payment'),
		path('success/',views.success,name='success'),
		path('',views.login_user,name='login')
		# path('logout',views.logout_user,name='logout'),
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)