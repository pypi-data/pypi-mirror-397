import asyncio
from bleak import BleakClient, BleakScanner
from unsync import unsync
import logging

class BLESerialBase:
    UART_TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E" # Nordic NUS characteristic for TX
    UART_RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E" # Nordic NUS characteristic for RX
    
    def __init__( self ):
        bleak_logger = logging.getLogger("bleak")
        bleak_logger.setLevel(logging.WARNING)
        #pass


class BLESerial( BLESerialBase ):
    def __init__( self, name, address, timeoutSeconds = 3.0 ):
        super().__init__()
        
        self._name           = name if name is not None else ''
        self._address        = address if address is not None else ''
        self._timeoutSeconds = timeoutSeconds
        self._device         = None
        self._aDeviceFound   = []
        self._bleakClient    = None

        self._abyteTXBuffer = bytearray()

    def __del__(self):
        try:
            self.close()
        except:
            pass
    
     #def disconnectedEventListener( self, client ):
     #    pass

    def notifyOnTXEventListener( self, sender, abyteData ):
         self._abyteTXBuffer += abyteData

    @property
    def is_connected( self ):
        try:
            return self._bleakClient.is_connected
        except:
            return False

        
    async def connect( self ):
        self._device = await self.findDevice( name = self._name, address = self._address, timeoutSeconds = self._timeoutSeconds ) # @fuh: , disconnected_callback = self.disconnectedEventListener )
        self._bleakClient = BleakClient( self._device, timeout = self._timeoutSeconds )
        
        print( f"Try: connect to name='{self.name}' address='{self.address}' ..." )
        
        await self._bleakClient.connect()

        print( f"   connected to name='{self.name}' address='{self.address}'" )

        for _ in range( 100 ):
            if self.is_connected:
                break
            
            await asyncio.sleep( 0.02 )
            
        if self.is_connected:
            await self._bleakClient.start_notify( BLESerialBase.UART_TX_UUID, self.notifyOnTXEventListener )
            print( "Added notification handler" )
        else:
            print( "Adding notification handler: failed" )
            #wait for data to be sent from client
        

    
    async def findDevice( self, name, address, timeoutSeconds = 3.0  ):
        if name:    name    = name   .strip()
        if address: address = address.strip()

        device = None

        if address:
            print( f"Scanning for BLE device with address '{address}'..." )

            try:
                device = await BleakScanner.find_device_by_address( device_identifier = address, timeout = timeoutSeconds )
            except BaseException as e:
                pass
                
        if device is None:
            if name:
                print( f"Scanning for BLE device with name '{name}'..." )
    
                try:
                    device = await BleakScanner.find_device_by_name( name = name, timeout = timeoutSeconds )
                except BaseException as e:
                    pass
        
        if device is None: 
            aDevice = await BleakScanner.discover()
            
            self._aDeviceFound = [ f'--name={device.name} --address={device.address}' for device in aDevice ]
            print( "Failed" )
        else:
            print( f"Found: --name='{device.name}' --address='{device.address}'" )

        return device


    async def close( self ):
        try:
            await self._bleakClient.stop_notify( BLESerialBase.UART_TX_UUID )
        except BaseException as e:
            print( e )
            
        try:
            await self._bleakClient.disconnect()
        except BaseException as e:
            print( e )
    
    async def read( self, size=1, timeoutTenthMillis = 20 ):
        """Parameters:	size – Number of bytes to read. If 0: return current buffer, if -1: wait timeoutTenthMillis and return current buffer
        Returns:	Bytes read from the port.
        Return type:	bytes
        """
        # return await self._bleakClient.read_gatt_char( BLESerialBase.UART_TX_UUID )

        if size == -1:
            await asyncio.sleep( 0.01 * timeoutTenthMillis )
            
        elif size > 0:
            if len(self._abyteTXBuffer) < size:
                for _ in range( timeoutTenthMillis ):
                    if len(self._abyteTXBuffer) >= size:
                        break
                    await asyncio.sleep(0.01)

        if self._abyteTXBuffer:
            if size <= 0:
                size = len( self._abyteTXBuffer )
                            
            abyteData = bytes(self._abyteTXBuffer[:size])
    
            self._abyteTXBuffer = self._abyteTXBuffer[ size: ]
            
            return abyteData
        else:
            return b''
    
    async def read_all( self, timeoutMillis = 0 ):
        if timeoutMillis > 0:
            return await self.read( size=-1, timeoutTenthMillis = round(timeoutMillis/10) )
        else:
            return await self.read( size=0 )
            
    async def write( self, aByte ):
        await self._bleakClient.write_gatt_char( BLESerialBase.UART_RX_UUID, aByte )

    @property
    def name( self ):
        try:
            return self._device.name
        except:
            return self._name

    @property
    def address( self ):
        try:
            return self._device.address
        except:
            return self._address


    async def getAvailabeDevicesList( self ):
        if not self._aDeviceFound:
            self._aDeviceFound = await self.findDevice( name = None, address = None, timeoutSeconds = self._timeoutSeconds )
            
        return self._aDeviceFound

        
class BLESerialUnsync( BLESerialBase ):
    def __init__( self, name, address, timeoutSeconds = 3.0 ):
        self.bleSerial = BLESerial( name = name, address = address, timeoutSeconds = timeoutSeconds )


    def __del__(self):
        try:
            del self.bleSerial
        except:
            pass
        
    @property
    def is_connected( self ):
        return self.bleSerial.is_connected
    
    @unsync
    async def unsyncConnect( self ):
        await self.bleSerial.connect()

    def connect( self ):
        unfuture = self.unsyncConnect()
        unfuture.result()
    
    @unsync
    async def unsyncClose( self ):
        await self.bleSerial.close()

    def close( self ):
        unfuture = self.unsyncClose()
        unfuture.result()
    
    @unsync
    async def unsyncRead( self, size = 1, timeoutSeconds = 0.0 ):
        if timeoutSeconds <= 0.0:
            return await self.bleSerial.read( size )
        else:
            try:
                async with asyncio.timeout( timeoutSeconds ):
                    return await self.bleSerial.read( size )
            except TimeoutError:
                return b''
        
    def read( self, size = 1, timeoutSeconds = 0.0  ):
        unfuture = self.unsyncRead( size, timeoutSeconds )
        return unfuture.result()
    
    @unsync
    async def unsyncRead_all( self, timeoutSeconds = 0  ):
        return await self.bleSerial.read_all( timeoutSeconds*1000 )
            #try:
            #    async with asyncio.timeout( timeoutSeconds ):
            #        return await self.bleSerial.read_all( timeoutSeconds * 1000 )
            #except TimeoutError:
            #    return b''
        
    def read_all( self, timeoutSeconds = 0  ):
        unfuture = self.unsyncRead_all( timeoutSeconds )
        return unfuture.result()
    
    @unsync
    async def unsyncWrite( self, aByte ):
        await self.bleSerial.write( aByte )
        #await asyncio.sleep( 0.5 )

    def write( self, aByte ):
        unfuture = self.unsyncWrite( aByte )
        unfuture.result()
    

    @property
    def name( self ):
        return self.bleSerial.name

    @property
    def address( self ):
        return self.bleSerial.address


    @unsync
    async def unsyncGetAvailabeDevicesList( self ):
        return await self.bleSerial.getAvailabeDevicesList()
    
    def getAvailabeDevicesList( self ):
        unfuture = self.unsyncGetAvailabeDevicesList()
        return unfuture.result()
        
