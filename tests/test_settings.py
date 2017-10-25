
def test_settings_group(plex):
    assert plex.settings.group('general')


def test_settings_get(plex):
    # This is the value since it we havnt set any friendlyname
    # plex just default to computer name but it NOT in the settings.
    assert plex.settings.get('FriendlyName').value == ''


def test_settings_get(plex):
    cd = plex.settings.get('collectUsageData')
    cd.set(False)
    # Save works but since we reload asap the data isnt changed.
    # or it might be our caching that does this. ## TODO
    plex.settings.save()
