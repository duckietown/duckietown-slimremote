__version__ = '2018.8.6'

import logging
logging.basicConfig()
logger = logging.getLogger('duckietown-slimremote')
logger.setLevel(logging.DEBUG)
logger.info('duckietown-slimremote %s' % __version__)
