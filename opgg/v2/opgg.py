import os
import json
import logging
import requests
import traceback
import fake_useragent

from datetime import datetime
from typing import Literal

from opgg.v2.params import Region



class OPGG:
    """
    ### OPGG.py

    Copyright (c) 2023-2024, ShoobyDoo

    License: BSD-3-Clause, See LICENSE for more details.
    """

    __author__ = 'ShoobyDoo'
    __license__ = 'BSD-3-Clause'

    def __init__(self) -> None:
        # Bypass API URL
        # todo: https://lol-web-api.op.gg/api/v1.0/internal/bypass/summoners/v2/na/autocomplete?gameName=Doomlad&tagline=NA1
        self.BYPASS_API_URL = "https://lol-web-api.op.gg/api/v1.0/internal/bypass"

        self._ua = fake_useragent.UserAgent()
        self._headers = {
            "User-Agent": self._ua.random()
        }

        # ===== SETUP START =====
        logging.root.name = 'OPGG.py'

        if not os.path.exists('./logs'):
            logging.info("Creating logs directory...")
            os.mkdir('./logs')
        else:
            # remove empty log files
            for file in os.listdir('./logs'):
                if os.stat(f"./logs/{file}").st_size == 0 and file != f'opgg_{datetime.now().strftime("%Y-%m-%d")}.log':
                    logging.info(f"Removing empty log file: {file}")
                    os.remove(f"./logs/{file}")

        logging.basicConfig(
            filename=f'./logs/opgg_{datetime.now().strftime("%Y-%m-%d")}.log',
            filemode='a+',
            format='[%(asctime)s][%(name)s->%(module)s:%(lineno)-10d][%(levelname)-7s] : %(message)s',
            datefmt='%d-%b-%y %H:%M:%S',
            level=logging.INFO
        )
        # ===== SETUP END =====

        # allow the user to interact with the logger
        self._logger = logging.getLogger("OPGG.py")

        self.logger.info(
            f"OPGG.__init__(BYPASS_API_URL={self.BYPASS_API_URL}, " \
            f"headers={self._headers})"
        )

        # at object creation, setup and query the cache
        # self._cacher = Cacher()
        # self._cacher.setup()

    @property
    def logger(self) -> logging.Logger:
        """
        A `Logger` object representing the logger instance.

        The logging level is set to `INFO` by default.
        """
        return self._logger

    @property
    def headers(self) -> dict:
        """
        A `dict` representing the headers to send with the request.
        """
        return self._headers

    @headers.setter
    def headers(self, value: dict) -> None:
        self._headers = value


    def search(self, query: str, region: Region):
        pass