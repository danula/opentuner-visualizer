from django.conf.urls import patterns, include, url

from django.contrib import admin
import views.plot
import views.plot2
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
    url(r'^plot/highlight_flag/', views.plot.highlight_flag, name='highlight_flag'),
    url(r'^plot/get_flags/', views.plot.get_flags, name='get_flags'),

    url(r'^plot2/$', views.plot2.index, name='plot'),
    url(r'^plot2/index/', views.plot2.index, name='plot'),
    url(r'^plot2/update/', views.plot2.update, name='plot_update'),
    url(r'^plot2/config/(?P<points_id>[0-9]*[,[0-9]*]*)', views.plot2.config, name='detail')
)
