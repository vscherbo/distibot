import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)

while True:
    try:

        adc = spi.xfer2([0, 0])
        print ">>>" + str(adc)
        data = ((adc[0] & 0x0f)*(2**7)) + (adc[1] >> 1)
        voltage = ((float(data) / 4096) * 4.887) * 2
        print "ADC Value = " + str(data)
        print "Analog Value = " + str(voltage) + " V"

        time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        spi.close()
        raise
