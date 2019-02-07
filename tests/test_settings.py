
def test_settings_group(plex):
    assert plex.settings.group('general')


def test_settings_get(plex):
    # This is the value since it we havnt set any friendlyname
    # plex just default to computer name but it NOT in the settings.
    assert plex.settings.get('FriendlyName').value == ''


def test_settings_set(plex):
    cd = plex.settings.get('autoEmptyTrash')
    old_value = cd.value
    new_value = not old_value
    cd.set(new_value)
    plex.settings.save()
    plex._settings = None
    assert plex.settings.get('autoEmptyTrash').value == new_value


def test_settings_set_str(plex):
    cd = plex.settings.get('OnDeckWindow')
    new_value = 99
    cd.set(new_value)
    plex.settings.save()
    plex._settings = None
    assert plex.settings.get('OnDeckWindow').value == 99
