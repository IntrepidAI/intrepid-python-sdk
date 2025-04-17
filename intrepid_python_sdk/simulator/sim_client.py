import asyncio
from centrifuge import Client, SubscriptionEventHandler, PublicationContext
import numpy as np
import logging
# import signal
# import sys
# import time
# from functools import partial
from typing import List
import logging
# from .entity import WorldEntity, Entity
# from .vehicle import Vehicle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


