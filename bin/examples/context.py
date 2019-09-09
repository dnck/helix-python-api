import os
import sys

sys.path.insert(0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
        )
    )

from api import api
from api import results_manager
