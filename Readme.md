# External Kodi Videolibrary Client

[![Check addon](https://github.com/romanvm/kodi.external.library/actions/workflows/check-addon.yml/badge.svg)](https://github.com/romanvm/kodi.external.library/actions/workflows/check-addon.yml)

This addon allows to browse and play videofiles from a medialibrary on a remote Kodi instance with syncing playback status.

## Motivation

Currently, Kodi supports 2 ways of accessing a common medialibrary with syncing playback status:

- Files on network shares with the common MySQL/MariaDB database.
- UPnP/DLNA access.

However, setting up a common MySQL/MariaDB database require some technical knowledge.
Also all Kodi instances that access this database must be of the same major version.
On the other hand, UPnP/DLNA access does not support full medialibrary information
and introduces unnecessary overhead of streaming if files are located on network shares.

This plugin provides an alternative way of accessing a remote Kodi medialibrary and
has the following advantages:

- It's easy to configure. Just enable Web server and Application control in the target Kodi instance
  and set host, port, login and password in the plugin to access it.
- It supports all medialibrary information that can be retrieved and set via JSON-RPC and Python APIs.
- Client and "server" Kodi instances can be of different major versions (but not too different).

By default, files are streamed from the built-in HTTP server of a remote Kodi instance,
but the plugin also supports playing files directly from network shares if the remote Kodi uses 
network shares as media sources.

## Known issues

- "Mark as watched/unwatched" item appears twice in the context menu but only
  the colored one actually works. The other is no-op.
- The plugin also appears in "Programs" section but just displays an information pop-up
  if launched from there.

Those are limitations of the Kodi addon API.

## Installation

Currently, this plugin is being actively developed and no installation files are available.

## Setup

### Remote Kodi

In "**Settings**" > "**Services**" > "**Control**" section enable the built-in web-server and remote control
as shown on the screenshot.

![Control Section](https://raw.githubusercontent.com/romanvm/kodi.external.library/master/screenshots/kodi-webserver-settings.png)

### Plugin Settings

In the first section ("**Access**") enter the host address of your remote Kodi instance.
Also provide the port number, login and password configured on the previous step.

## Credits

The addon icon was borrowed from [Aeon Nox 5: SiLVO](https://github.com/MikeSiLVO/Aeon-Nox-SiLVO) skin.

## License

[GPL v.3](https://www.gnu.org/licenses/gpl-3.0.html)
