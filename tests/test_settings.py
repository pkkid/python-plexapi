
def test_settings_group(plex):
    assert plex.settings.group('general')


def test_settings_get(plex):
    # This is the value since it we havnt set any friendlyname
    # plex just default to computer name but it NOT in the settings.
    assert plex.settings.get('FriendlyName').value == ''


def test_settings_set(plex):
    cd = plex.settings.get('collectUsageData')
    old_value = cd.value
    cd.set(not old_value)
    plex.settings.save()
    delattr(plex, '_settings')
    assert plex.settings.get('collectUsageData').value == (not old_value)
