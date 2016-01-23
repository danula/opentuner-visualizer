from django.conf.urls import patterns, include, url

from django.contrib import admin
import views.plot
import views.plot2
import views.plot_features
import views.upload
import views.configuration

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'visualizer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.plot.index, name='plot'),
    url(r'^plot/$', views.plot.index, name='plot'),
    url(r'^plot/index/', views.plot.index, name='plot'),
    url(r'^plot/update/', views.plot.update, name='plot_update'),
    url(r'^plot/config/(?P<points_id>[0-9]*[,[0-9]*]*)', views.plot.config, name='detail'),
    url(r'^plot/config3/(?P<points_id1>[0-9]*[,[0-9]*]*)/(?P<points_id2>[0-9]*[,[0-9]*]*)', views.plot.config3, name='detail'),
    url(r'^plot/highlight_flag/', views.plot.highlight_flag, name='highlight_flag'),
    url(r'^plot/get_flags/', views.plot.get_flags, name='get_flags'),

    url(r'^plot2/$', views.plot2.index, name='plot2'),
    url(r'^plot2/index/', views.plot2.index, name='plot2'),
    url(r'^plot2/update/', views.plot2.update, name='plot2_update'),
    url(r'^plot2/config/(?P<points_id>[0-9]*[,[0-9]*]*)', views.plot2.config, name='detail'),


    url(r'^plot3/$', views.plot_features.index, name='plot3'),

    url(r'^upload/index/', views.upload.index, name='upload'),
    url(r'^upload/upload_files/', views.upload.upload_files, name='upload_files'),
    url(r'^upload/$', views.upload.index, name='upload'),

    url(r'^config/(?P<config_id>[0-9]*)', views.configuration.index, name='configuration'),
)
