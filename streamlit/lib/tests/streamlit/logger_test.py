# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Logger Unittest."""

from __future__ import annotations

import logging
import unittest
from collections import OrderedDict
from unittest.mock import patch

import pytest
from parameterized import parameterized

from streamlit import config, logger

DUMMY_CONFIG_OPTIONS = OrderedDict()


class LoggerTest(unittest.TestCase):
    """Logger Unittest class."""

    def test_set_log_level_by_constant(self):
        """Test streamlit.logger.set_log_level."""
        data = [
            logging.CRITICAL,
            logging.ERROR,
            logging.WARNING,
            logging.INFO,
            logging.DEBUG,
        ]
        for k in data:
            logger.set_log_level(k)
            assert k == logging.getLogger("streamlit").getEffectiveLevel()

    def test_set_log_level_error(self):
        """Test streamlit.logger.set_log_level."""
        with pytest.raises(SystemExit) as e:
            logger.set_log_level(90)
        assert e.type is SystemExit
        assert e.value.code == 1

    @parameterized.expand(
        [
            ("%(asctime)s.%(msecs)03d %(name)s: %(message)s", None),
            ("%(asctime)s.%(msecs)03d %(name)s: %(message)s", DUMMY_CONFIG_OPTIONS),
            (None, None),
            (None, DUMMY_CONFIG_OPTIONS),
        ]
    )
    def test_setup_log_formatter(self, messageFormat, config_options):
        """Test streamlit.logger.setup_log_formatter."""

        LOGGER = logger.get_logger("test")

        config._set_option("logger.messageFormat", messageFormat, "test")
        config._set_option("logger.level", logging.DEBUG, "test")

        with patch.object(config, "_config_options", new=config_options):
            logger.setup_formatter(LOGGER)
            assert len(LOGGER.handlers) == 1
            if config_options:
                assert LOGGER.handlers[0].formatter._fmt == (
                    messageFormat or "%(message)s"
                )
            else:
                assert LOGGER.handlers[0].formatter._fmt == logger.DEFAULT_LOG_MESSAGE

    def test_init_tornado_logs(self):
        """Test streamlit.logger.init_tornado_logs."""
        logger.init_tornado_logs()
        loggers = [x for x in logger._loggers if "tornado." in x]
        truth = ["tornado.access", "tornado.application", "tornado.general"]
        assert sorted(truth) == sorted(loggers)
