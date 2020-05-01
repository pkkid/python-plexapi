
from plexapi.gdm import GDM


def test_gdm():
    gdm = GDM()

    gdm.scan(timeout=2)
    assert len(gdm.entries)



