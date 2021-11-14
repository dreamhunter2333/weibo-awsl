import logging

from awsl.awsl import WbAwsl

logging.basicConfig(
    format="%(asctime)s: %(levelname)s: %(name)s: %(message)s",
    level=logging.INFO
)

awsl = WbAwsl()
awsl.start()
