# Souce:
#    https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
#    @author: https://stackoverflow.com/users/2826801/malcolm-who
#    @author: <a href="mailto:a.fuchs@fosbos-rosenheim.de">Alfred Fuchs</a>

import serial.tools.list_ports


class COMPorts:
    #@classmethod
    @staticmethod
    def getAllPorts( bVerbose = False ):
        class PortData:
            def __init__(self, serialPort ):
                self.serialPort  = serialPort

            @property
            def device(self):
                return self.serialPort.device
                
            @property
            def description(self):
                return self.serialPort.description.split("(")[0].strip() # Windows: remove " (COMX)" at the end of the description

            def toHex( self, num ):
                try:    return "0x" + f"{num:x}".upper()
                except: return str(num)
                
            def __str__( self ):
                return "Port: " + str(self.serialPort) \
                    + "\n    description    : " + str(self.serialPort.description) \
                    + "\n    device         : " + str(self.serialPort.device) \
                    + "\n    vid            : " + str(self.serialPort.vid) + " = " + self.toHex( self.serialPort.vid ) \
                    + "\n    pid            : " + str(self.serialPort.pid) + " = " + self.toHex( self.serialPort.pid ) \
                    + "\n    hwid           : " + str(self.serialPort.hwid) \
                    + "\n    interface      : " + str(self.serialPort.interface) \
                    + "\n    location       : " + str(self.serialPort.location) \
                    + "\n    manufacturer   : " + str(self.serialPort.manufacturer) \
                    + "\n    name           : " + str(self.serialPort.name) \
                    + "\n    product        : " + str(self.serialPort.product) \
                    + "\n    serial_number  : " + str(self.serialPort.serial_number) \
                    + "\n    usb_description: " + str(self.serialPort.usb_description) \
                    + "\n    usb_info       : " + str(self.serialPort.usb_info)

        
        aPort     = list(serial.tools.list_ports.comports())
        aPortData = []
        
        for port in aPort:
            portData = PortData( port )
            aPortData.append( portData )
            
            if bVerbose == True:
                print( portData )
        
        return aPortData

    @staticmethod
    def findPortsByDescription( strDescriptionContains: str = "cp210", bVerbose = False, bQuiet = False ):
        astrDevice = []
        
        for portData in COMPorts.getAllPorts( bVerbose = bVerbose ):
            if strDescriptionContains in portData.description.lower():
                astrDevice.append( portData.device )
                if bQuiet == False:
                    print( f"Found port '{portData.device}', description contains `{strDescriptionContains}`: '{portData.description}'" )
            elif bVerbose == True:
                print( f"No match: Port '{portData.device}', description does not contain `{strDescriptionContains}`: '{portData.description}'" )
                
        if len( astrDevice ) > 0:
            return astrDevice
        else:
            print( f"No port found whose description contains '{strDescriptionContains}'." )
            return None

    @staticmethod
    def findPortsAvailable():
        aPort = list(serial.tools.list_ports.grep(""))
        aPort.sort( key = lambda port: (port.hwid == "n/a", port.device) )  # n/a could be good evidence that the port is non-existent
        aStrPort = [port.device for port in aPort]
        return aStrPort
    
    @staticmethod
    def findPort():
        astrPort = COMPorts.findPortsByDescription()
        if astrPort:
            strPort = astrPort[0]
            print( "MicroPython-USB kernel connect string:" )
            print( f"%serialconnect --port={strPort} --baud=115200" )


if __name__ == "__main__":
  #aStrPort = COMPorts.findPortsByDescription( bVerbose = True )
  aPort = COMPorts.getAllPorts( bVerbose = True )
    
  if aPort:
      for port in aPort:
          print(port.device)
          print("    ", port.description)