# -*- coding:utf8 -*-
from channels import Channel, Group
from channels.test import ChannelTestCase

class TestCase(ChannelTestCase):
    def test_first(self):
        # This goes onto an in-memory channel, not the real backend.
        Group('gateway-abcde').send({"text": {"name":"xujl"}})