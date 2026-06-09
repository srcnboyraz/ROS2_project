from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep

# Pin atamaları (BCM numarası)
enable = DigitalOutputDevice(17)   # R_EN + L_EN birlikte
rpwm   = PWMOutputDevice(18)       # ileri yön PWM
lpwm   = PWMOutputDevice(27)       # geri yön PWM

def dur():
    rpwm.value = 0
    lpwm.value = 0

try:
    enable.on()                    # köprüyü etkinleştir
    print("İLERİ - %30 hız")
    lpwm.value = 0
    rpwm.value = 0.3               # 0.0-1.0 arası hız
    sleep(2)

    dur()
    sleep(1)

    print("GERİ - %30 hız")
    rpwm.value = 0
    lpwm.value = 0.3
    sleep(2)

    dur()
    print("Test bitti.")

finally:
    dur()
    enable.off()                   # her durumda güvenli kapat