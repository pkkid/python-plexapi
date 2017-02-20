# -*- coding: utf-8 -*-
import json
import threading
from plexapi import log
from plexapi.exceptions import Unsupported


class PlexNotifier(threading.Thread):
    """ Creates a websocket connection to the Plex Server to optionally recieve
        notifications. These often include messages from Plex about media scans
        as well as updates to currently running Transcode Sessions.

        Parameters:
            server (:class:`~plexapi.server.PlexServer`): PlexServer this notifier is connected to.
            callback (func): Callback function to call on recieved messages.

        NOTE: You need websocket-client installed in order to use this feature.
            >> pip install websocket-client
    """
    key = '/:/websockets/notifications'

    def __init__(self, server, callback=None):
        self._server = server
        self._callback = callback
        self._ws = None
        super(PlexNotifier, self).__init__()

    def run(self):
        """ Starts the PlexNotifier thread. This function should not be called
            directly, instead use :func:`~plexapi.server.PlexServer.startNotifier`.
        """
        # try importing websocket-client package
        try:
            import websocket
        except:
            raise Unsupported('Websocket-client package is required to use this feature.')
        # create the websocket connection
        url = self._server.url(self.key).replace('http', 'ws')
        log.info('Starting PlexNotifier: %s', url)
        self._ws = websocket.WebSocketApp(url,
            on_message=self._onMessage,
            on_error=self._onError)
        self._ws.run_forever()

    def stop(self):
        """ Stop the PlexNotifier thread. """
        log.info('Stopping PlexNotifier.')
        self._ws.close()

    def _onMessage(self, ws, message):
        """ Called when websocket message is recieved. """
        try:
            data = json.loads(message)['NotificationContainer']
            log.debug('Notify: %s', data)
            if self._callback:
                self._callback(data)
        except Exception as err:
            log.error('PlexNotifier Msg Error: %s', err)

    def _onError(self, ws, err):
        """ Called when websocket error is recieved. """
        log.error('PlexNotifier Error: %s' % err)
