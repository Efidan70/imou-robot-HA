# Imou Robot Vacuum for Home Assistant

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Efidan70&repository=imou-robot-ha&category=integration)

Control your **Imou robot vacuum** (built for the **RV-L11-A**) from Home Assistant, through the official
**Imou Open Platform** API. No Imou Life app login or password is shared with this integration.

> **Unofficial.** This project is not affiliated with, endorsed by or supported by Imou or Dahua.
> It talks to the **Imou cloud**: the robot is *not* controlled locally, and it stops working if the cloud does.

## What you get

| Type | Entities |
| --- | --- |
| **Vacuum** | Start, pause, stop, return to dock, suction level, live status |
| **Sensors** | Battery, status, cleaned area, cleaning time, Wi-Fi signal, brush / dust box / sensor usage hours, error code |
| **Numbers** | Water level, suction power, voice volume |
| **Switches** | Indicator light, resume cleaning after charging, auto empty dust bin, carpet boost, do not disturb *(experimental)* |
| **Buttons** | Locate robot, empty dust bin *(experimental)* |
| **Binary sensors** | Charging, mop attached, cloud connection |

All entities appear under **one device**. Updates are faster while the robot is cleaning (every 60 s), slower when it is idle (every 5 minutes) and
slower still when nothing has changed for a while (up to 15 minutes). After errors the integration backs off automatically.

**Not available:** the floor map, cleaning schedule and room-by-room cleaning. The Imou cloud does not expose
these in a readable form.

## Installation (HACS)

1. In HACS choose **⋮ → Custom repositories**, add `https://github.com/Efidan70/imou-robot-ha`, category **Integration**.
2. Search for **Imou Robot Vacuum**, click **Download**, then **restart Home Assistant Core**.
3. Go to **Settings → Devices & services → Add integration → Imou Robot Vacuum**.

## Get your App ID and App Secret

1. Register for free at <https://open.imoulife.com> and sign in to the **Console**.
2. Under **My App → Application Information** copy your **App ID**, **App Secret** and note the **data center**
   (Europe = Frankfurt, Asia = Singapore, Americas = Oregon).
3. Under **Products & Services → Device Access Service** click **Add Device** and add your robot with its serial number.
4. Enter these in Home Assistant when the integration asks. The secret is stored only in your Home Assistant.

Imou gives **30,000 free API calls per month**. The integration protects that quota:

* One update costs **one** API call (the access token is cached for days).
* Updates slow down automatically while the robot is idle and nothing changes.
* A **monthly budget** (default 15,000 calls, changeable in the options) acts as a hard ceiling: updates are
  spread over the month and never go faster than the budget allows. At the limit it checks once an hour.
* The diagnostic sensor **API calls this month** shows your usage.

**Why polling?** The Imou cloud is the only way to reach this robot: it has no open network ports, so there is no local
API. Imou's message push can notify about alarms and online status but, as far as we know, not about vacuum property
changes, so polling stays the only option.

## Troubleshooting

* **"App ID or App Secret not accepted"** – check the data center and that you copied the secret completely.
* **The robot does not appear in the list** – type its serial number manually; make sure it was added in step 3.
* **A button or switch marked experimental does nothing** – please open an issue with your Home Assistant log
  (`Settings → System → Logs`, filter on `imou`).
* **Other models** – other Imou robots may work if they use the same thing-model; the action `imou_robot.dump`
  writes the model to the log so it can be compared.

## Privacy

Your credentials are stored in Home Assistant's config entries only. The integration sends requests solely to the
Imou Open Platform host you select.

## Contributing

Issues and pull requests are welcome. Tests run on GitHub Actions (`hassfest`, HACS validation and unit tests).

## License

[MIT](LICENSE)
