# -*- coding: utf-8 -*-
from .payloads import SONOS_RESOURCES


def test_sonos_resources(mocked_account, requests_mock):
    requests_mock.get("https://sonos.plex.tv/resources", text=SONOS_RESOURCES)

    speakers = mocked_account.sonos_speakers()
    assert len(speakers) == 3

    speaker1 = mocked_account.sonos_speaker("Speaker 1")
    assert speaker1.machineIdentifier == "RINCON_12345678901234567:1234567891"

    speaker3 = mocked_account.sonos_speaker_by_id("RINCON_12345678901234567:1234567893")
    assert speaker3.title == "Speaker 3"
