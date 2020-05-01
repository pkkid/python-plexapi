
from plexapi.gdm import GDM


def test_gdm(plex):
    gdm = GDM()

    gdm_enabled = plex.settings.get("GdmEnabled")

    gdm.scan(timeout=2)
    if gdm_enabled:
        assert len(gdm.entries)
    else:
        assert not len(gdm.entries)
