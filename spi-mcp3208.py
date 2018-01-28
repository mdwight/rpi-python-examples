import spidev

class MCP3208():
    # The MCP3208 is a 8 channel 12bit SPI ADC. This code should work with MCP3204.
    # http://ww1.microchip.com/downloads/en/devicedoc/21298c.pdf
    # For single ended port0=CH0  port1=CH1 .... port7=CH7
    # For differential port0=CH0&CH1  port1=CH2&CH3  port2=CH4&CH5  port3=CH6&CH7
    # polarityReverse will swap CH0=IN+/CH1=IN- to CH0=IN-/CH1=IN+
    
    def __init__(self, spibus, spidevice, port, differential=False, polarityReverse=False):
        self.spibus = spibus            # which spi channel should be 0
        self.spidevice = spidevice      # which spi device.    
        dataOut=0x040000                # start bit - bit 18
        if differential:                # set single ended bit
            dataOut+=(port%4)<< 15      # add channel number bits 15,16
            if polarityReverse:     
                dataOut+=0x004000       # add polarity reversal
        else:    
            dataOut+=0x020000           # set single ended bit 17
            dataOut+=(port%8)<< 14      # add channel number bits 14,15,16
            
        # communication with MCP3208 is LSB first so swap around bytes.
        self.dataOut =  [(dataOut&0xFF0000)>>16]  # 3rd byte
        self.dataOut += [(dataOut&0x00FF00)>>8]   # 2rd byte
        self.dataOut += [(dataOut&0x0000FF)>>0]   # 1st byte
    
    def getRaw(self):
        #spi.max_speed_hz=5000
        #spi.mode = 0b01
        spi = spidev.SpiDev()
        spi.open(self.spibus,self.spidevice)
        dataIn=spi.xfer2(self.dataOut)
        spi.close()
        # communication with MCP3208 is LSB first.
        # only take lowest 12bits.
        return ((dataIn[1]&0x0F)<<8)+dataIn[2]
    
    def get(self, multiplier=1):
        value=self.getRaw()             # get 12bit value 
        return multiplier*(value/4095)  # return 


# testing ---

SPI_BUS=0
SPI_CE=0
MCP3208_CH=0        # 0-3 (Differential) 0-7 (Single Ended) see note above
DIFF=False          # 
POLREV=False        # Swap polarity on differential Inputs

a=MCP3208(SPI_BUS,SPI_CE,MCP3208_CH,DIFF,POLREV)
a.get()
'''
