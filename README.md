# Eve Online Alert

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Geuthur/EVE-Alert-Opensource/main.svg)](https://results.pre-commit.ci/latest/github/Geuthur/EVE-Alert-Opensource/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python package](https://github.com/Geuthur/EVE-Alert-Opensource/actions/workflows/python-package.yml/badge.svg)](https://github.com/Geuthur/EVE-Alert-Opensource/actions/workflows/python-package.yml)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/W7W810Q5J4)

EVE Alert - Check every 1-3 seconds if the Local has an Enemy or Neutral in System and play a sound if someone is there!

- [EVE Alert](#evealert)
  - [Features](#features)
  - [Usage](#usage)
  - [Installation](#installation)
    - [Download](#step1)
    - [Install Python](#step2)
    - [Make Build](#step3)
  - [Detection](#detection)
    - [Image Detection](#imagedetection)
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
- Monitoring Region in real-time (also possible to stream via Discord for friends)
- Faction Spawn Detection - Now you can set a Faction Spawn Detection and it will play a sound if a faction is in Site (can also used for other thing like active modules or something)

## Usage<a name="usage"></a>

- Simply launch Alert.exe, and a menu will appear. You can configure all your settings there. Afterward, click on "Start."
- If the Alert doesn't respond to the local chat, you can reduce the detection accuracy or double-check if you've set the region correctly.
- If both settings are 100% accurate and your interface is not blurred, make a new screenshot from your neutral symbol and try it with your own image
- You can edit all images & sounds by yourself only the name must be the same

## Installation<a name="installation"></a>

To create an executable program, you need to download a release version and then run it through the installer in an environment.
You also need a Python Version installed on Windows or Linux

### Download Version<a name="step1"></a>

Go to [the releases page](https://github.com/Geuthur/EVE-Alert-Opensource/releases) to download the latest version.

### Install Python<a name="step2"></a>

> \[!CAUTION\]
> This Script only works with Python `3.10`, `3.11`, `3.12`

You need Python for <a href="#step3">Step 3</a>
Here is a Guide to install Python

Windows User:

Install `Python` you can download it from [Python Download](https://www.python.org/downloads/)

Linux User:

On Linux Python is automaticly installed you can update it with

```bash
sudo apt update
```

### Make Build<a name="step3"></a>

> \[!NOTE\]
> Ensure you have read/write permissions to this directory

Windows:

```cmd
installer_window.bat
```

Linux:

```bash
./installer_linux.sh
```

Now you will find a folder called dist/ where the finished executable program is located.

## Detection<a name="detection"></a>

### Image Detection<a name="imagedetection"></a>

- Neutral:    ![Neutral](https://i.imgur.com/SdjoIs6.png)
- Enemys:     ![Red](https://i.imgur.com/O0VTT69.png)

If you want more, simply add more images to the "img/" folder with naming image_1, image_2, image_3, etc.

## Resolution<a name="resolution"></a>

> \[!NOTE\]
> Resolution Scaling can be a issue

![Window](https://i.imgur.com/e0X2sGM.png)

![EVE](https://i.imgur.com/08hxzIj.png)

## Showcase<a name="showcase"></a>

https://github.com/Geuthur/EVE-Alert-Opensource/evealert/docs/videos/detection.mp4

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
