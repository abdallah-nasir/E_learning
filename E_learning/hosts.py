from django_hosts import patterns, host
from django.conf import settings

host_patterns = patterns('',
    host(r'localhost:8000', settings.ROOT_URLCONF, name='www'),
    host(r'kemet.localhost:8000', 'E_learning.kemet_urls', name='kemet'),   
    # host(r'maps', 'maps.urls', name='maps'),
)
