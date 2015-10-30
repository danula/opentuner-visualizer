__author__ = 'madawa'

from visualizer.forms.ConfigurationForm import ConfigurationForm
from opentuner.resultsdb.models import Configuration
from opentuner.resultsdb.connect import connect
import constants

def config(request, config_id):
    if(request.method == 'GET'):
        engine,Session=connect("sqlite:///"+constants.database_url)
        session=Session()
        session.query.

