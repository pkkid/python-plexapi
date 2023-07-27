ACCOUNT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<user id="12345" uuid="1234567890" username="testuser" title="Test User" email="testuser@email.com" friendlyName="Test User" locale="" confirmed="1" joinedAt="946730096" emailOnlyAuth="0" hasPassword="1" protected="0" thumb="https://plex.tv/users/1234567890abcdef/avatar?c=12345" authToken="faketoken" mailingListStatus="unsubscribed" mailingListActive="0" scrobbleTypes="" country="CA" subscriptionDescription="" restricted="0" anonymous="" home="1" guest="0" homeSize="2" homeAdmin="1" maxHomeSize="15" rememberExpiresAt="1680893707" adsConsent="" adsConsentSetAt="" adsConsentReminderAt="" experimentalFeatures="0" twoFactorEnabled="1" backupCodesCreated="1">
  <subscription active="1" subscribedAt="2023-03-24 00:00:00 UTC" status="Active" paymentService="" plan="lifetime">
    <features>
      <feature id="companions_sonos"/>
    </features>
  </subscription>
  <profile autoSelectAudio="0" defaultAudioLanguage="en" defaultSubtitleLanguage="en" autoSelectSubtitle="0" defaultSubtitleAccessibility="0" defaultSubtitleForced="0"/>
  <entitlements>
    <entitlement id="all"/>
  </entitlements>
  <roles>
    <role id="plexpass"/>
  </roles>
  <subscriptions>
  </subscriptions>
  <services>
  </services>
</user>
"""

SONOS_RESOURCES = """<MediaContainer size="3">
  <Player title="Speaker 1" machineIdentifier="RINCON_12345678901234561:1234567891" deviceClass="speaker" product="Sonos" platform="Sonos" platformVersion="56.0-76060" protocol="plex" protocolVersion="1" protocolCapabilities="timeline,playback,playqueues,provider-playback" lanIP="192.168.1.11"/>
  <Player title="Speaker 2 + 1" machineIdentifier="RINCON_12345678901234562:1234567892" deviceClass="speaker" product="Sonos" platform="Sonos" platformVersion="56.0-76060" protocol="plex" protocolVersion="1" protocolCapabilities="timeline,playback,playqueues,provider-playback" lanIP="192.168.1.12"/>
  <Player title="Speaker 3" machineIdentifier="RINCON_12345678901234563:1234567893" deviceClass="speaker" product="Sonos" platform="Sonos" platformVersion="56.0-76060" protocol="plex" protocolVersion="1" protocolCapabilities="timeline,playback,playqueues,provider-playback" lanIP="192.168.1.13"/>
</MediaContainer>
"""

SERVER_RESOURCES = """<MediaContainer size="3">
<StatisticsResources timespan="6" at="1609708609" hostCpuUtilization="0.000" processCpuUtilization="0.207" hostMemoryUtilization="64.946" processMemoryUtilization="3.665"/>
<StatisticsResources timespan="6" at="1609708614" hostCpuUtilization="5.000" processCpuUtilization="0.713" hostMemoryUtilization="64.939" processMemoryUtilization="3.666"/>
<StatisticsResources timespan="6" at="1609708619" hostCpuUtilization="10.000" processCpuUtilization="4.415" hostMemoryUtilization="64.281" processMemoryUtilization="3.669"/>
</MediaContainer>
"""

SERVER_TRANSCODE_SESSIONS = """<MediaContainer size="1">
<TranscodeSession key="qucs2leop3yzm0sng4urq1o0" throttled="0" complete="0" progress="1.2999999523162842" size="73138224" speed="6.4000000953674316" duration="6654989" remaining="988" context="streaming" sourceVideoCodec="h264" sourceAudioCodec="dca" videoDecision="transcode" audioDecision="transcode" protocol="dash" container="mp4" videoCodec="h264" audioCodec="aac" audioChannels="2" transcodeHwRequested="1" transcodeHwDecoding="dxva2" transcodeHwDecodingTitle="Windows (DXVA2)" transcodeHwEncoding="qsv" transcodeHwEncodingTitle="Intel (QuickSync)" transcodeHwFullPipeline="0" timeStamp="1611533677.0316164" maxOffsetAvailable="84.000667334000667" minOffsetAvailable="0" height="720" width="1280" />
</MediaContainer>
"""

MYPLEX_INVITE = """<MediaContainer friendlyName="myPlex" identifier="com.plexapp.plugins.myplex" machineIdentifier="xxxxxxxxxx" size="1">
<Invite id="12345" createdAt="1635126033" friend="1" home="1" server="1" username="testuser" email="testuser@email.com" thumb="https://plex.tv/users/1234567890abcdef/avatar?c=12345" friendlyName="testuser">
<Server name="testserver" numLibraries="2"/>
</Invite>
</MediaContainer>
"""
