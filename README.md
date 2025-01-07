# Eve Online Alert

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Geuthur/EVE-Alert-Opensource/main.svg)](https://results.pre-commit.ci/latest/github/Geuthur/EVE-Alert-Opensource/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Python package](https://github.com/Geuthur/EVE-Alert-Opensource/actions/workflows/python-package.yml/badge.svg)](https://github.com/Geuthur/EVE-Alert-Opensource/actions/workflows/python-package.yml)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/W7W810Q5J4)

EVE Alert - Check every 1-3 seconds if the Local has an Enemy or Neutral in System and play a sound if someone is there!

- [EVE Alert](#evealert)
  - [Features](#features)
  - [Download](#step1)
  - [Detection](#detection)
  - [Socket System](#socket)
    - [Server - Main Program](#server)
    - [Client - Listener](#client)
  - [Showcase](#showcase)
  - [Donation](#donation)
  - [Terms](#terms)
  - [Contributing](#contributing)

## Features<a name="features"></a>

- Play Sound on Local Detection
- Easy-Use Interface
- Start/Stop System
- Monitoring Region in real-time (also possible to stream via Discord for friends)
- Faction Spawn Detection - Now you can set a Faction Spawn Detection and it will play a sound if a faction is in Site (can also used for other thing like active modules or something)
- The Socket System allows you to have one server and multiple clients that can connect to it to receive alarms.

## Upcoming Features

- Discord Webhook support

### Download Version<a name="step1"></a>

Go to [the releases page](https://github.com/Geuthur/EVE-Alert-Opensource/releases) to download the latest version.

## Detection<a name="detection"></a>

- Neutral: ![Neutral](https://i.imgur.com/SdjoIs6.png)
- Enemys: ![Red](https://i.imgur.com/O0VTT69.png)

If you want more, simply add more images to the "img/" folder with naming image_1, image_2, image_3, etc.\
Note: If you have different UI Scaling you need to add these images to the img folder like the `image_1_90%`

## Server Usage<a name="server"></a>

> [!NOTE]
> **This Version is for Single User!**

The server is responsible for sending messages to the connected clients. It can send two types of messages: Normal and Alarm. When an Alarm message is sent, all connected clients will receive it and can take appropriate actions, such as playing a sound.

- Simply launch Server.exe, and a menu will appear. You can configure all your settings there. Afterward, click on "Start."
- If the Alert doesn't respond to the local chat, you can reduce the detection accuracy or double-check if you've set the region correctly.
- If both settings are 100% accurate and your interface is not blurred, make a new screenshot from your neutral symbol and try it with your own image
- You can edit all images & sounds by yourself only the name must be the same

Optional:

- Activate Socket Server for Broadcast Mode
- Mute Alarm for Just Broadcast

## Client Usage<a name="client"></a>

> [!NOTE]
> To Use the Client Version you need at least 1 Active Server!

- The client program can be used to connect to a socket server and continuously receives messages. The messages can be in one of two states: Normal or Alarm.
- When the client receives an Alarm message, it plays a sound.

## Showcase<a name="showcase"></a>

https://github.com/Geuthur/EVE-Alert-Opensource/evealert/docs/videos/detection.mp4

## Donation<a name="donation"></a>

I know it is simple Script, but if you want to support me here:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/W7W810Q5J4)

## Terms<a name="terms"></a>

> [!CAUTION]
> This is an open-source project without any guarantees. Use it at your own risk.
> Please ensure that you comply with EVE Online's terms of use and policies. The use of bots or automation may violate the game's terms of service.

## Contributing<a name="contributing"></a>

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
