import warnings
from importlib.resources import files
import aramis_exporter.models
import aramis_exporter.client
import aramis_exporter.exporter
import aramis_exporter.constants
import aramis_exporter.utils

warnings.warn("To use the 'aramis exporter' module must be installed on a Zeiss GOM Aramis system. It is only \n \
                  possible to use the modules directly from the Aramis Professional scripting editor.")

# package information
__version__ = "1.4.0"