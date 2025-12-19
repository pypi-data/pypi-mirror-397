#==============================================================================
#
#==============================================================================

class Connector:
    def __init__( self, strId, sres, sresSYS ):
        self._strId  = strId
        self.sres    = sres    # two output functions borrowed across
        self.sresSYS = sresSYS
        

    @property
    def id( self ):
        return self._strId

    @property
    def description( self ):
        return self._strId

    @property
    def needsPasteMode( self ):
        return True

    @property
    def supportsFileTransfere( self ):
        return True
    
    def connect( self, **kwargs ):
        pass

    @property
    def isConnected( self ):
        return False
        
    def read( self ):
        return b''

    def readInit( self ):
        pass

    def read_all( self ):
        return b''

    def write( self, aByte, isVerbose = False ):
        return 0
        
    def close( self ):
        pass





#==============================================================================

import serial
import sys
from . import serialports


class SerialPortConnector( Connector ):
    TIMEOUT_SECONDS = 0.5
    
    def __init__( self, sres, sresSYS ):
        super().__init__( "SerialPort", sres, sresSYS )

        self.serialPort = None
        self.strPort    = self.getDefaultPort    ()
        self.iBaudrate  = self.getDefaultBaudrate()

    @property
    def description( self ):
        return f"{self._strId}: port={self.strPort} baudrate={self.iBaudrate}"

    def getDefaultPort( self ):
        if sys.platform == "linux":
            return "/dev/ttyUSB0"
        elif sys.platform == "win32":
            return "COM4"
        else: # Mac OSX, etc...
            return "/dev/cu.SLAB_USBtoUART"

    def getDefaultBaudrate( self ):
        return 115200

    
    # this should take account of the operating system
    def guessSerialPort( self ):
        aStrPort = serialports.COMPorts.findPortsByDescription( bQuiet = True )
        
        if not aStrPort:
            aStrPort = serialports.COMPorts.findPortsAvailable()
    
        return aStrPort
    
    def connect( self, **kwargs ):
        self.strPort   = kwargs.get( 'portname' )
        self.iBaudrate = kwargs.get( 'baudrate' )
        verbose        = kwargs.get( 'verbose' )
        
        if not self.iBaudrate:
            self.iBaudrate = self.getDefaultBaudrate()
        
        self.close()
        
        if not self.strPort:
            aStrPort = self.guessSerialPort()
            
            if aStrPort:
                self.strPort = aStrPort[ 0 ]

                if len(aStrPort) > 1:
                    self.sres( "Found serial ports: {}\nUsing port{}".format(", ".join(aStrPort), self.strPort) )
            else:
                self.sresSYS( "No possible ports found" )

                self.strPort = self.getDefaultPort()
 
        self.sresSYS( f"Connecting to --port={self.strPort} --baud={self.iBaudrate} " )
        
        try:
            self.serialPort = serial.Serial( self.strPort, self.iBaudrate, timeout = SerialPortConnector.TIMEOUT_SECONDS )
            
        except serial.SerialException as e:
            self.sres( e.strerror )
            self.sres("\n")
            
            aStrPort = self.guessSerialPort()
            
            if aStrPort:
                self.sresSYS( "\nTry one of these ports as --port= \n  {}".format("\n  ".join(aStrPort)) )
            else:
                self.sresSYS( "\nAre you sure your ESP-device is plugged in?" )
            return

        for i in range(5001):
            if self.serialPort.isOpen():
                break
                
            time.sleep(0.01)
            
        if verbose:
            self.sresSYS(" [connected]")
            
        self.sres("\n")

        if verbose:
            self.sres( str(self.serialPort) )
            self.sres("\n")

        if i != 0 and verbose:
            self.sres( "Waited {} seconds for isOpen()\n".format(i*0.01) )

    
    @property
    def isConnected( self ):
        return self.serialPort and self.serialPort.isOpen()
        
    def read( self ):
        return self.serialPort.read()

    def read_all( self ):
        return self.serialPort.read_all()        

    def write( self, aByte, isVerbose = False ):
        iBytesWritten = self.serialPort.write( aByte )
        
        if isVerbose == True:
            self.sres( f'{self.name}.write {iBytesWritten} bytes to {self.serialPort.port} at baudrate {self.serialPort.baudrate}\n' )
        
        return iBytesWritten
        
    def close( self ):
        if self.serialPort:
            try:
                self.serialPort.close()
            except BaseException:
                pass
            
        self.serialPort = None


#==============================================================================

from . import bleserial

class BLEConnector( Connector ):
    TIMEOUT_SECONDS = 0

    
    def __init__( self, sres, sresSYS ):
        super().__init__( "BLE device", sres, sresSYS )

        self.bleSerial = None
        self.name      = ""
        self.address   = ""
        
    @property
    def description( self ):
        return f"{self._strId}: {self.name} @ {self.address}"

    def connect( self, **kwargs ):
        self.name    = kwargs.get( 'name'    )
        self.address = kwargs.get( 'address' )
        
        self.close()

        self.sresSYS( f"Connecting to {self.description}\n" )
        
        try:
            self.bleSerial = bleserial.BLESerialUnsync( self.name, self.address )            
            self.bleSerial.connect()

            self.name    = self.bleSerial.name
            self.address = self.bleSerial.address
            
        except BaseException as e:
            self.sres( f"BLE Exception when connecting to {self.description}' {str(e)}\n" )
            
            aAvailabeDevice = None
            
            try:
                aAvailabeDevice = self.bleSerial.getAvailabeDevicesList()
            except BaseException as e:
                print( e )
            
            self.close()
            
            if aAvailabeDevice:
                self.sresSYS( "\nTry one of these devices:\n{}\n".format( '\n  '.join(aAvailabeDevice) ) )
            else:
                self.sresSYS( "\nAre you sure your ESP-device is plugged in and started with a BLE-REPL?" )
                

    @property
    def isConnected( self ):
        return self.bleSerial and self.bleSerial.is_connected
        
    def read( self ):
        return self.bleSerial.read( timeoutSeconds = BLEConnector.TIMEOUT_SECONDS )

    def read_all( self ):
        return self.bleSerial.read_all(timeoutSeconds = BLEConnector.TIMEOUT_SECONDS ) #  0.1 )

    def write( self, aByte, isVerbose = False ):
        iBytesWritten = self.bleSerial.write( aByte )
        
        if isVerbose == True:
            self.sres( f'{self.name} : write {iBytesWritten} bytes to BLE device {self.description}\n' )
        
        return iBytesWritten

    def close( self ):
        if self.bleSerial:
            try:
                self.bleSerial.close()
            except BaseException:
                pass
            
        self.bleSerial = None


#==============================================================================

import socket
import select

class SocketConnector( Connector ):

    TIMEOUT_SECONDS = 0.5
    
    def __init__( self, sres, sresSYS ):
        super().__init__( "Socket", sres, sresSYS )
        
        self.socket     = None
        self.socketFile = None
        self.ipAddress  = ""
        self.iPort      = ""
        
    @property
    def description( self ):
        return f"{self._strId}: {self.ipAddress}:{self.iPort}"

    @property
    def needsPasteMode( self ):
        return False # @TODO, dont understand why

    @property
    def supportsFileTransfere( self ):
        return False
    
    
    def connect( self, **kwargs ):
        self.ipAddress  = kwargs.get( 'ipnumber'   )
        self.iPort      = kwargs.get( 'portnumber' )
        
        self.close()
        
        self.sresSYS( f"Connecting to {self.description}\n" )

        try:
            self.socket = socket.socket()
            
            self.sres( "preconnect\n" )
            self.socket.connect( socket.getaddrinfo( self.ipAddress, self.iPort )[0][-1] )
            
            self.sres( "Doing makefile\n" )
            self.socketFile = self.socket.makefile( 'rwb', 0 )
            
        except OSError as e:
            self.sres( f"Socket OSError {e}" )
        except ConnectionRefusedError as e:
            self.sres( f"Socket ConnectionRefusedError {e}" )

        if self.socketFile is None:
            self.close()

    @property
    def isConnected( self ):
        return self.socketFile is not None
        
    def read( self ):
        r,w,e = select.select( [self.socketFile], [], [], SocketConnector.TIMEOUT_SECONDS )
        
        if r:
            return self.socketFile._sock.recv(1)
        else:
            return b''

    def read_all( self ):
        res = []
        
        while True:
            r,w,e = select.select( [self.socketFile._sock],[],[],0 )
            if not r:
                break
            res.append( self.socketFile._sock.recv(1000) )
            
            self.sres( "Selected socket {}  {}\n".format(len(res), len(res[-1])) )
            
        return b"".join(res)

    
    def write( self, aByte, isVerbose = False ):
        iBytesWritten = self.socketFile.write( aByte )
        
        if isVerbose == True:
            self.sres( f'{self.name}: write {iBytesWritten} bytes to {self.description}\n' )
        
        return iBytesWritten

    
    def close( self ):
        if self.socketFile is not None:
            try:
                self.socketFile.close()
            except BaseException:
                pass
            
        self.socketFile = None

        if self.socket is not None:
            try:
                self.socket.close()
            except BaseException:
                pass
            
        self.socket = None

#==============================================================================

import websocket  # the old non async one

class WebSocketConnector( Connector ):
    TIMEOUT_SECONDS = 0.5
    
    def __init__( self, sres, sresSYS ):
        super().__init__( "WebSocket", sres, sresSYS )

        self.webSocket    = None
        self.webSocketUrl = ""

        self.aByteResultBuffer = b""
        self.iResultBufferLen  = 0
    
    @property
    def description( self ):
        return f'{self._strId}: url={self.webSocketUrl}'

    def connect( self, **kwargs ):
        self.webSocketUrl = kwargs.get( 'websocketurl' )
        
        self.close()
        
        self.sresSYS( f"Connecting to Websocket ({self.webSocketUrl})\n" )
        
        try:
            webSocketNew = websocket.create_connection( self.webSocketUrl, 5 )
            webSocketNew.settimeout( WebSocketConnector.TIMEOUT_SECONDS )

            self.webSocket = webSocketNew
        except socket.timeout:
            self.sres( f"Websocket Timeout after 5 seconds {self.webSocketUrl}\n" )
        except ValueError as e:
            self.sres( f"WebSocket ValueError {e}\n" )
        except ConnectionResetError as e:
            self.sres( f"WebSocket ConnectionError {e}\n" )
        except OSError as e:
            self.sres( f"WebSocket OSError {e}\n" )
        except websocket.WebSocketException as e:
            self.sres( f"WebSocketException {e}\n" )
        

    @property
    def isConnected( self ):
        # ws.recv()
        # return ws.connected
        return self.webSocket is not None
        
    def read( self ):
        # websocket (break down to individual bytes)
        if self.iResultBufferLen >= len(self.aByteResultBuffer):
            r,w,e = select.select([self.webSocket], [], [], WebSocketConnector.TIMEOUT_SECONDS )
            
            if r:
                self.aByteResultBuffer = self.webSocket.recv()  # this comes as batches of strings, which beed to be broken to characters
                
                if type(self.aByteResultBuffer) == str:
                    self.aByteResultBuffer = self.aByteResultBuffer.encode("utf8")   # handle fact that strings come back from this interface
            else:
                self.aByteResultBuffer = b''
                
            self.iResultBufferLen = 0
            
        if len(self.aByteResultBuffer) > 0:
            b = self.aByteResultBuffer[self.iResultBufferLen:self.iResultBufferLen+1]
            self.iResultBufferLen += 1
            return b
        else:
            return b''

    def readInit( self ):
        self.aByteResultBuffer = b""
        self.iResultBufferLen  = 0

    
    def read_all( self ):
        res = []
        
        while True:
            r,w,e = select.select([self.webSocket],[],[],0.2)  # add a timeout to the webrepl, which can be slow
            if not r:
                break
            res.append(self.webSocket.recv())
            
        return "".join(res) # this is returning a text array, not bytes
                            # though a binary frame can be stipulated according to websocket.ABNF.OPCODE_MAP
                            # fix this when we see it

    def write( self, aByte, isVerbose = False ):
        iBytesWritten = self.webSocket.send( aByte )
        
        if isVerbose == True:
            self.sres( f'{self.name}: write {iBytesWritten} bytes to {self.description}\n' ) # don't worry; it always includes more bytes than you think
        
        return iBytesWritten

    
    def close( self ):
        if self.webSocket:
            try:
                self.webSocket.close()
            except BaseException:
                pass
            
        self.webSocket = None
        
