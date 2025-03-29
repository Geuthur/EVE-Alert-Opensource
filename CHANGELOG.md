## [1.0.0] IN DEVELOPMENT

### Changed

- Removed Socket System
  - The Socket System has been removed and we now use Discord Webhook to share Intel.

### Added

- Discord System
  - All alarms are sent to a Discord webhook with the set system name.

## [0.9.0] - 2025-01-08

### Changed

- Setting Manager
  - The settings manager has been refactored to improve the handling and organization of settings.
- Config Mode
  - The configuration mode has been optimized to respond more flexibly to changes.
- Refactor of the entire system
  - The system has been refactored to improve code readability and maintainability.
- Logger System
  - The logger system has been enhanced to capture more detailed information about errors, aiding in better troubleshooting.
- Alert Sound
  - The alert sound will not interrupt the program after an error occurs.

### Fixed

- EveLocal not closing with Window Close:
  - An issue was fixed where the EveLocal window would not properly close when the window's close button was clicked. This fix ensures that the window is now correctly closed when the user attempts to exit.
- Settings not reloaded if changed:
  - A bug where settings were not being reloaded after being modified has been resolved. Now, when changes are made to the settings, they will be properly reloaded, reflecting the new configuration.
- Vision not reloaded if changed:
  - A similar issue was addressed where vision settings (likely related to display or graphical configurations) were not reloaded after changes. This fix ensures that any changes to vision settings are immediately applied and reflected.
- Overlay Window not fitting exactly to the monitor resolution:
  - The overlay window was previously not aligning correctly with the monitor's resolution. This issue has been fixed, ensuring that the overlay window now correctly fits and scales to the screen size, providing a more accurate and consistent user interface.

### Added

- Propertys for each system
  - New properties have been added to manage and configure each system individually. This allows for more flexibility and control over system settings and their states.
- Socket System (Test)
  - A new socket system has been implemented for testing purposes. This enables communication between different components or systems, facilitating data exchange and interactions.
- Cleanup Functions
  - Cleanup functions have been introduced to improve resource management. These functions help remove unnecessary data, free up memory, and ensure the application remains efficient by handling cleanup tasks properly.
- Set changed flag in the menu:
  - The changed flag is now set to True whenever a modification is made to the menu settings. This helps track changes and triggers actions like warnings before exiting without saving.
- Buttons State
  - All buttons now have a state color to indicate when they are pressed. This visual cue helps users easily identify the current state of the buttons, improving the user interface and overall user experience by providing clearer feedback during interaction.
- Message Box System
  - Implemented a single-instance error message box to prevent multiple error windows from opening simultaneously.

## [0.5.0] - 2024-11-29

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
- Background width is not correct

### Added

- Abort Option on Settings with `ESC`
- Faction Detection Scale
- Overlay System

### Removed

- Drop Color Mode Support
- Screenshot Mode

## [0.4.4] - 2024-11-23

### Changed

- print to logger in regionmanager
- Alarm Sound

### Fixed

- Faction Region can't be open if a error occurs [#15](https://github.com/Geuthur/EVE-Alert-Opensource/issues/15)

## [0.4.3] - 2024-10-18

### Added

- Dependency Requirment Info

### Changed

- Requirments
- Moved from PyAudio to sounddevice and soundfile
- Update Preview Video
- Update Window Installer

### Fixed

- Icon Bitmap Error on Linux [#9](https://github.com/Geuthur/EVE-Alert-Opensource/issues/9)

## [0.4.2] - 2024-10-18

### Added

- Window Installation Guide

### Fixed

- Window Installer not working correctly if executed as Admin

## [0.4.1b1] - 2024-05-24

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
