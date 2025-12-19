# ovos-i2c-detection
A small repo containing auto-detection scripts for i2c devices

Currently you can get detection results for the following devices

* Mycroft sj201 sound card
  * v6 - dev kit  `is_sj201_v6`
  * v10 - production unit  `is_sj201_v10`
* Texas Instruments tas5806 audio amp  (Used for sj201_v10 detection)
  * `is_texas_tas5806`
* WM8960 devices
  * `is_wm8960`
  * ReSpeaker 2mic
  * Adafruit 2mic
  * Im sure there are others
* ReSpeaker 4mic
  * `is_respeaker_4mic`
* ReSpeaker 6mic
  * `is_respeaker_6mic`
* Adafruit audio amp (https://www.adafruit.com/product/1752)
  * `is_adafruit_amp`
+ Mycroft Mark 1 device
  + `is_mark_1`
* HiFiBerry DAC Pro (https://www.hifiberry.com/shop/boards/dac2-pro/)
  * `is_hifiberry_dac_pro`
