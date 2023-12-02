# External Kodi Videolibrary Client

[![Check addon](https://github.com/romanvm/kodi.external.library/actions/workflows/check-addon.yml/badge.svg)](https://github.com/romanvm/kodi.external.library/actions/workflows/check-addon.yml)

This addon allows to browse and play videofiles from a medialibrary on a remote Kodi instance with syncing playback status.

## Motivation

Currently, Kodi supports 2 ways having a common medialibrary with syncing playback status:

- Files on network shares with the common MySQL/MariaDB database.
- UPnP/DLNA access.

However, setting up MySQL/MariaDB database require some technical knowledge and UPnP/DLNA access does not support full medialibrary information and introduces unnecessary overhead of streaming if files are located on network shares.

This plugin provides an alternative way of accessing a remote Kodi medialibrary and is easy to configure. It supports full medialibrary info that can be set in a video plugin.

By default, files are streamed from the built-in HTTP server of a remote Kodi instance, but the plugin also supports playing files directly from network shares if the remote Kodi uses network shares as media sources.

## Installation

Currently, this plugin is being actively developed and no installation files are available.
