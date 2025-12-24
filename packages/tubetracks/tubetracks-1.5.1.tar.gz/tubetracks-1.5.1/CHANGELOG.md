# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.1] - 2025-12-19

### Fixed
- Fixed PyPI metadata validation errors for package publication
- Replaced invalid `license` and `license-files` fields with standard License classifier
- Corrected invalid `Environment :: X11 :: Tk` classifier to valid `Topic :: Desktop Environment`
- Ensured full compatibility with PyPI's legacy upload server metadata requirements

### Changed
- Simplified GitHub Actions workflow for PyPI publishing
- Modernized workflow to use `actions/checkout@v4` and `actions/setup-python@v5`
- Updated metadata parsing to use Python 3.11+ `tomllib`
- Streamlined build and publish process with current best practices

### Added
- PyPI version badge to README
- PyPI downloads badge to README
- Converted all relative links in README to absolute GitHub URLs for better PyPI page display

## [1.5.0] - 2025-12-10

### Added
- Initial stable release
- Multi-platform plugin system supporting 9+ platforms (YouTube, TikTok, Instagram, SoundCloud, Spotify, Twitch, Dailymotion, Vimeo, Reddit)
- Advanced quality control with 4 preset levels (low, medium, high, best)
- Multiple audio format support (MP3, M4A, FLAC, WAV, OGG)
- Playlist and batch processing capabilities
- Desktop GUI application with Tkinter
- Configuration file support with INI format
- Download archive for preventing duplicate downloads
- Real-time progress tracking with Rich terminal output
- Proxy and rate limiting support
- Cookie-based authentication
- Comprehensive error handling with automatic retry logic
- Metadata embedding (ID3 tags, artwork)
- Comprehensive test suite
- Makefile for easy project management
- Detailed documentation and plugin API guide

### Features
- **Multi-Platform Support**: Download from YouTube, TikTok, Instagram, SoundCloud, Spotify, Twitch, Dailymotion, Vimeo, and Reddit
- **Quality Presets**: 128 kbps, 192 kbps, 320 kbps, and original quality options
- **Format Support**: MP3, M4A, FLAC, WAV, OGG with FFmpeg integration
- **Batch Processing**: Download multiple URLs from files with configurable error handling
- **Desktop GUI**: User-friendly Tkinter application for all platforms
- **Configuration Management**: Flexible INI-based configuration system
- **Download History**: Prevent re-downloading the same content
- **Network Features**: Proxy, rate limiting, and cookie support
- **Plugin Architecture**: Extensible system for adding new platforms

### System Requirements
- Python 3.8 or higher
- FFmpeg (latest stable version)
- Dependencies: yt-dlp >= 2024.0.0, rich >= 13.0.0

## [0.1.0] - Pre-release
- Development version with core functionality

[1.5.1]: https://github.com/jomardyan/TubeTracks/releases/tag/v1.5.1
[1.5.0]: https://github.com/jomardyan/TubeTracks/releases/tag/v1.5.0
