from django.conf.urls import patterns, include, url

from django.contrib import admin
import views.plot
import views.plot2
import views.plot_features
import views.upload
import views.configuration
import views.analysis
import views.project

admin.autodiscover()

urlpatterns = patterns('',
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

    url(r'^project/list/', views.project.index, name='project_list'),
    url(r'^project/create/', views.project.create, name='project_create'),
    url(r'^project/store/', views.project.store, name='project_store'),
    url(r'^project/show/', views.project.show, name='project_show'),
    url(r'^project/destroy/', views.project.destroy, name='project_destroy'),

    url(r'^analysis/create/', views.analysis.create, name='analysis_create'),
    url(r'^analysis/store/', views.analysis.store, name='analysis_store'),
    # url(r'^analysis/show/$', views.analysis.show, name='analysis_show'),
    # url(r'^analysis/destroy/$', views.analysis.destroy, name='analysis_destroy')

)
