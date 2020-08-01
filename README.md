# WoTmod DispersionIndicator

## contents

- [Lateset Release](../../releases/latest)
- [Screenshot](#Screenshot)
- [Parameters](#Parameters)

## Screenshot

### while view
![image](https://user-images.githubusercontent.com/11075065/56848251-91a72b80-6921-11e9-95c3-e0d9cd63726a.png)

### convergence time of gun's dispersion
![image](https://user-images.githubusercontent.com/11075065/56848277-e9de2d80-6921-11e9-8ea0-99af434f7dfb.png)

### angle of hull
![image](https://user-images.githubusercontent.com/11075065/56848288-09755600-6922-11e9-9422-d164fe511836.png)

### customize (config-full.json)
![shot_055](https://user-images.githubusercontent.com/11075065/72655895-f5efab00-39da-11ea-9d06-1a2fdc74a61b.jpg)


## Parameters

### update on event `updatePing`

information about health of client and network

| name        | description     |
| ----------- | --------------- |
| `currTime`  | timestamp       |
| `ping`      | Ping            |
| `fps`       | FPS             |
| `fpsReplay` | FPS on replay   |
| `latency`   | latency         |

### update on event `updateDispersionAngle`

information about dispersion angle

| name                    | description                            |
| ----------------------- | -------------------------------------- |
| `dAngleAiming`          | dispersion angle                       |
| `dAngleIdeal`           | dispersion angle for ideal             |
| `turretRotationSpeed`   | rotation speed of turret               |
| `additiveFactor`        | additive shot dispersionFactor factor  |
| `shotDispersionAngle`   | gun parameter of shot dispertion angle |
| `shotFactor`            | normal / afterShot / afterShotInBurst  |
| `aimingStartTime`       | timestamp of start aiming              |
| `aimingStartFactor`     | aiming factor on start aiming          |
| `multFactor`            | aiming factor by gunner skill          |
| `factorsTurretRotation` | aiming factor by turret rotation       |
| `factorsMovement`       | aiming factor by vehicle movement      |
| `factorsRotation`       | aiming factor by vehicle rotation      |
| `aimingTime`            | aiming time                            |
| `aimingFactor`          | `dAngleAiming` / `shotDispersionAngle` |
| `modifiedAimingFactor`  | `aimingFactor` / `multFactor`          |
| `scoreDispersion`       | score of current dispertsion           |
| `aimingTimeConverging`  | time until aiming converges            |

information about vehicle direction

| name                    | description                            |
| ----------------------- | -------------------------------------- |
| `vehicleYaw`            | vehicle yaw                            |
| `vehiclePitch`          | vehicle pith                           |
| `vehicleRoll`           | vehicle roll                           |
| `vehicleRYaw`           | vehicle yaw against camera direction   |
| `turretYaw`             | turret yaw                             |
| `gunPitch`              | gun pitch                              |
| `vehicleSpeed`          | vehicle speed                          |
| `vehicleRSpeed`         | vehicle rotation speed                 |
| `engineRPM`             | engine RPM                             |
| `engineRelativeRPM`     | engine relative RPM                    |

information about target position

| name             | description                              |
| ---------------- | ---------------------------------------- |
| `shotPosX`       | gun position X                           |
| `shotPosY`       | gun position Y                           |
| `shotPosZ`       | gun position Z                           |
| `shotDistance`   | shot distance (between target and gun)   |
| `shotDistanceH`  | horizontal componet of shot distance     |
| `shotDistanceV`  | vertical component of shot distance      |
| `vehiclePosX`    | vehicle position X                       |
| `vehiclePosY`    | vehicle position Y                       |
| `vehiclePosZ`    | vehicle position Z                       |
| `distance`       | distance between target and vehicle      |
| `distanceH`      | horizontal componet of distance          |
| `distanceV`      | vertical componet of distance            |
| `targetPosX`     | target position X                        |
| `targetPosY`     | target position Y                        |
| `targetPosZ`     | target position Z                        |

information about shell speed

| name             | description                              |
| ---------------- | ---------------------------------------- |
| `shotSpeed`      | shell speed                              |
| `shotSpeedH`     | horizontal component of shell velocity   |
| `shotSpeedV`     | vertical component of shell velocity     |
| `shotGravity`    | gravity acceleration acting on the shell |
| `flightTime`     | `shotDistanceH` / `shotSpeedH`           |


### on event `updatePenetrationArmor`

information about target armor

| name                     | description                         |
| ------------------------ | ----------------------------------- |
| `targetVehicleName`      | vehicle name on target              |
| `targetHitAngleCos`      | angle of incidence on target        |
| `targetArmor`            | armor thickness on target           |
| `targetArmorKind`        | kind of armor on target             |
| `targetPenetrationArmor` | effective armor thickness on target |
| `piercingMultiplier`     | factor of piercing                  |
| `piercingPercent`        | score of piercing                   |


### others

other parameters

| name                     | description                         |
| ------------------------ | ----------------------------------- |
| `localDateTime`          | date and time (local)               |
| `eventTime`              | timestamp on event                  |
| `eventName`              | event name                          |
| `arenaName`              | arena name                          |
| `vehicleName`            | player vehicle name                 |
| `playerTeam`             | player team id                      |
