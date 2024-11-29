## \[0.5.0\] - 2024-11-29

### Changed

- Settings for Regions now have a visual interface
- Setting Region now work per `Marquee Selection`
- Enemy & Faction now work seperately

### Fixed

- Faction Region can't be open if a error occurs [#15](https://github.com/Geuthur/EVE-Alert-Opensource/issues/15)
- In some Cases Multiple Monitors not work [#15](https://github.com/Geuthur/EVE-Alert-Opensource/issues/15) (Testing)
- Vision System not work if Detection Scale is Zero or below
- Images with Alpha Channel triggers Error [#15](https://github.com/Geuthur/EVE-Alert-Opensource/issues/15)
- It is not possible to switch Windows recognition off/on during sound playback
- Overlapping Overlay when F1 and F2 was pressed

### Added

- Abort Option on Settings with `ESC`
- Faction Detection Scale
- Overlay System

### Removed

- Drop Color Mode Support
- Screenshot Mode

## \[0.4.4\] - 2024-11-23

### Changed

- print to logger in regionmanager
- Alarm Sound

### Fixed

- Faction Region can't be open if a error occurs [#15](https://github.com/Geuthur/EVE-Alert-Opensource/issues/15)

## \[0.4.3\] - 2024-10-18

### Added

- Dependency Requirment Info

### Changed

- Requirments
- Moved from PyAudio to sounddevice and soundfile
- Update Preview Video
- Update Window Installer

### Fixed

- Icon Bitmap Error on Linux [#9](https://github.com/Geuthur/EVE-Alert-Opensource/issues/9)

## \[0.4.2\] - 2024-10-18

### Added

- Window Installation Guide

### Fixed

- Window Installer not working correctly if executed as Admin

## \[0.4.1b1\] - 2024-05-24

### Added

- Cooldown Function with optional cooldowns
- Log Message Function
- Status Icon for Running Alert
- Log Textfield

### Fixed

- Program Blocking on some situations
- Alert Text appears after Error
- Performance Issues

### Changed

- Moved AlertAgent to Async
- AlertAgent now started via seperate Thread
- save_settings function moved to SettingsManager
- Moved Play Sound to one Function

### Removed

- Socket Functions, Maybe Later i will Implemend this..
- Log System Label
- Unused Code

## Full Changelog

https://github.com/geuthur/aa-ledger/compare/v0.4.0...v0.4.1
