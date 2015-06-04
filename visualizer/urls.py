from django.conf.urls import patterns, include, url

from django.contrib import admin
import views.plot
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'visualizer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^plot/', views.plot.index, name='plot'),
    url(r'^plot_update/', views.plot.update, name='plot_update'),
    url(r'^plot/(?P<point_id>[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)', views.plot.config, name='detail')
)
