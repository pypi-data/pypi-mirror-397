from datetime import datetime
from typing import Optional, Literal
import pytz
import requests
import os
os.path.abspath(__file__)
from .lohn_und_gehalt import DatevLohnUndGehalt
from .lodas import DatevLodas
from .hr_exchange import DatevHrExchange
from functools import cached_property


class Datev:
    def __init__(self, system_type: Optional[Literal['source', 'target']] = None, debug: bool = False, sandbox: bool = False):
        self.system_type = system_type
        self.debug = debug
        self.sandbox = sandbox

    @cached_property
    def lodas(self) -> DatevLodas:
        # runs only on the first access to `self.lodas`
        return DatevLodas(system_type=self.system_type)

    @cached_property
    def lohn_und_gehalt(self) -> DatevLohnUndGehalt:
        # runs only on the first access to `self.lohn_und_gehalt`
        return DatevLohnUndGehalt(system_type=self.system_type, debug=self.debug)

    @cached_property
    def hr_exchange(self) -> DatevHrExchange:
        # runs only on the first access to `self.hr_exchange`
        return DatevHrExchange(system_type=self.system_type, debug=self.debug, sandbox=self.sandbox)
