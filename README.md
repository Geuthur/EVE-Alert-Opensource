# Eve Online Alert

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Geuthur/EVE-Alert-Opensource/main.svg)](https://results.pre-commit.ci/latest/github/Geuthur/EVE-Alert-Opensource/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python package](https://github.com/Geuthur/EVE-Alert-Opensource/actions/workflows/python-package.yml/badge.svg)](https://github.com/Geuthur/EVE-Alert-Opensource/actions/workflows/python-package.yml)

EVE Alert - Check every 1-3 seconds if the Local has an Enemy or Neutral in System and play a sound if someone is there!

- [EVE Alert](#evealert)
  - [Features](#features)
  - [Usage](#usage)
  - [Detection](#detection)
    - [Image Detection](#imagedetection)
    - [Color Detection](#colordetection)
    - [Detection Mode](#detectionmode)
  - [Resolution](#resolution)
  - [Showcase](#showcase)
  - [Donation](#donation)
  - [Terms](#terms)
  - [Contributing](#contribute)

## Features<a name="features"></a>

- Play Sound on Local Detection
- Easy-Use Interface
- Start/Stop System
- Monitoring Region on Picture Mode in real-time (also possible to stream via Discord for friends)
- Color Detection Mode - If Picture Mode not working for you simply use the Color Detection Mode (needs more ressources)
- Faction Spawn Detection - Now you can set a Faction Spawn Detection and it will play a sound if a faction is in Site

## Usage<a name="usage"></a>

- Simply launch Alert.exe, and a menu will appear. You can configure all your settings there. Afterward, click on "Start."
- If the Alert doesn't respond to the local chat, you can reduce the detection accuracy or double-check if you've set the region correctly.
- If both settings are 100% accurate and your interface is not blurred, make sure that your neutral symbol looks like this:
- You can edit all images & sounds by yourself only the name must be the same

## Detection<a name="detection"></a>

### Image Detection<a name="imagedetection"></a>

- Neutral:    ![Neutral](https://i.imgur.com/SdjoIs6.png)
- Enemys:     ![Red](https://i.imgur.com/O0VTT69.png)

If you want more, simply add more images to the "img/" folder with naming image_1, image_2, image_3, etc.

### Color Detection<a name="colordetection"></a>

- Neutral: ![Neutral](https://i.imgur.com/L7hy58Y.png)

- Enemys:     ![Red](https://i.imgur.com/O0VTT69.png)

- The Color Mode alert react to all RED Colors

- You Symbols must look like the upove icons to work.

### Detection Modes<a name="detectionmode"></a>

![ingame](https://github.com/Geuthur/EVE-Alert/assets/761682/78e24aec-780a-4d70-95c9-60de480dbb75)
![no detection](https://github.com/Geuthur/EVE-Alert/assets/761682/aa21ac7d-4413-40be-8c16-43d598600820)
![ingame2](https://github.com/Geuthur/EVE-Alert/assets/761682/fc097678-bb3f-4198-b186-d753c0bf5c11)
![detection](https://github.com/Geuthur/EVE-Alert/assets/761682/e1b8bc65-f647-4b32-a8b6-690bdc2d5305)

Ingame / No Detection (Vision Window) / Ingame RED Local / Detection (Vision Window)

## Resolution<a name="resolution"></a>

> \[!NOTE\]
> Resolution Scaling can be a issue

![Window](https://i.imgur.com/e0X2sGM.png)

![EVE](https://i.imgur.com/08hxzIj.png)

## Showcase<a name="showcase"></a>

https://github.com/Geuthur/EVE-Alert/assets/761682/0161a9c6-0656-4952-9a3c-7b27532ee2aa

## Donation<a name="donation"></a>

I know it is simple Script, but if you want to support me here:
https://www.paypal.com/paypalme/HellRiderZ

## Terms<a name="terms"></a>

> \[!CAUTION\]
> This is an open-source project without any guarantees. Use it at your own risk.
> Please ensure that you comply with EVE Online's terms of use and policies. The use of bots or automation may violate the game's terms of service.

## Contributing<a name="contribute"></a>

Contributions are welcome! If you would like to contribute to this project and optimize the code, follow these steps:

1. Fork the repository by clicking on the "Fork" button at the top right corner of this page.
1. Clone your forked repository to your local machine.
1. Make the necessary changes and improvements to the code.
1. Commit your changes and push them to your forked repository.
1. Submit a pull request by clicking on the "New pull request" button on the original repository's page.

Please ensure that your contributions adhere to the following guidelines:

- Follow the existing code style and conventions.
- Clearly describe the changes you have made in your pull request.
- Test your changes thoroughly before submitting the pull request.

By contributing to this project, you agree to release your contributions under the MIT License.
