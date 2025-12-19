#from ipykernel.kernelbase import Kernel
from ipykernel.ipkernel import IPythonKernel
import IPython

import logging, sys, time, os, re
import serial, socket, serial.tools.list_ports, select
import websocket  # only for WebSocketConnectionClosedException
from . import device

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# use of argparse for handling the %commands in the cells
import argparse, shlex

from . import connector


#==============================================================================
#
#==============================================================================

class Magic:
    def __init__( self, name, sres, sresSYS, description = None ):
        self._strName = name

        self.sres     = sres
        self.sresSYS  = sresSYS
        
        self._astrAlternativeNames = []
        
        self._argumentParser = argparse.ArgumentParser( prog = name, description = description, add_help = False )

        self._argumentParser.add_argument( '--help',  '-h', action = 'store_true', help = "show this help message" )

        self._mapKnownArguments      = None
        self._aMagicCommandArguments = None
        
    @property
    def name( self ):
        return self._strName

    def addAlternativeName( self, name ):
        self._astrAlternativeNames.append( name )
        
    def getAlternativeNames( self ):
        return self._astrAlternativeNames
        
    def addArgument( self, *args, **kwargs ):
        self._argumentParser.add_argument( *args, **kwargs )
        #f(c=3, **dict(pre_defined_kwargs, b=42))

    def addAction( self, *args, **kwargs ):
        if kwargs.get( 'action' ):
            self._argumentParser.add_argument( *args, **kwargs )
        else:
            self._argumentParser.add_argument( *args, **dict(kwargs, action = 'store_true') )

    def format_usage( self ):
        return re.sub( "\n       ", "\n", re.sub( "usage: ", "", self._argumentParser.format_usage() )) + "    " + self._argumentParser.description + "\n\n"

    def format_help( self ):
        return self._argumentParser.format_help()


    def parse( self, aMagicCommandArguments ):
        self._aMagicCommandArguments = aMagicCommandArguments
        
        try:
            self._mapKnownArguments = self._argumentParser.parse_known_args( aMagicCommandArguments )[0]
        except SystemExit:  # argparse throws these because it assumes you only want to do the command line
            self._mapKnownArguments = None # should be a default one

        return self._mapKnownArguments


    def hasHelpArgument( self ):
        try:
            return self._mapKnownArguments.help
        except:
            return False

    def execute( self, cellcontents, kernel ):
        return None


#==============================================================================
#
#==============================================================================

class Magics:

    #==========================================================================

    class MagicLsMagic( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%lsmagic", sres, sresSYS, description = "list magic commands" )

        def execute( self, cellcontents, kernel ):
            for magic in kernel.magics._mapMagic.values():
                self.sres( magic.format_usage() )
            
            return None

    #==========================================================================

    class MagicSerialConnect( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%serialconnect", sres, sresSYS, description = "connects to a device over USB wire" )
    
            self.addAction  ( '--raw', help = 'Just open connection' )
            self.addArgument( '--port', type = str, default = 0      )
            self.addArgument( '--baud', type = int, default = 115200 )
            self.addArgument( '--verbose', action = 'store_true' )

            self.serialPortConnector = connector.SerialPortConnector( self.sres, self.sresSYS )
        
        def execute( self, cellcontents, kernel ):
            kernel.device.connect(
                self.serialPortConnector,
                portname = self._mapKnownArguments.port,
                baudrate = self._mapKnownArguments.baud,
                verbose  = self._mapKnownArguments.verbose
            )
            
            if kernel.device.isConnected:
                self.sres( f"\n ** Connected to {self.serialPortConnector.description} **\n\n", 32 )
                if not self._mapKnownArguments.raw:
                    if kernel.device.enterPasteMode( verbose = self._mapKnownArguments.verbose ):
                        self.sresSYS( "Ready.\n" )
                    else:
                        self.sres( "Disconnecting [paste mode not working]\n", 31 )
                        kernel.device.disconnect( verbose = self._mapKnownArguments.verbose )
                        self.sresSYS("  (You may need to reset the device)")
                        
                        cellcontents = ""
            else:
                cellcontents = ""
                
            return cellcontents.strip() and cellcontents or None

    #==========================================================================

    class MagicBLEConnect( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%bleconnect", sres, sresSYS, description = "connects to the bleREPL an ESP32 over BLE" )
    
            self.addAction  ( '--raw', help = 'Just open connection' )
            self.addArgument( '--name',    type = str, default = '' )
            self.addArgument( '--address', type = str, default = '' )
            self.addArgument( '--verbose', action = 'store_true'  )

            self.bleConnector = connector.BLEConnector( self.sres, self.sresSYS )
        
        def execute( self, cellcontents, kernel ):
            
            kernel.device.connect(
                self.bleConnector,
                name    = self._mapKnownArguments.name,
                address = self._mapKnownArguments.address
            )

            if kernel.device.isConnected:
                self.sres( f"\n ** Connected to {self.bleConnector.description} **\n\n", 32 )
                
                if not self._mapKnownArguments.raw:
                    if kernel.device.enterPasteMode(verbose=self._mapKnownArguments.verbose):
                        self.sresSYS( "Ready.\n" )
                    else:
                        self.sres( "Disconnecting [paste mode not working]\n", 31 )
                        kernel.device.disconnect( verbose = self._mapKnownArguments.verbose )
                        self.sresSYS( "  (You may need to reset the device)" )
                        
                        cellcontents = ""
            else:
                cellcontents = ""
                
            return cellcontents.strip() and cellcontents or None
            
    #==========================================================================

    # this is the direct socket kind, not attached to a webrepl
    class MagicSocketConnect( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%socketconnect", sres, sresSYS, description = "connects to a socket of a device over wifi" )
    
            self.addAction  ( '--raw', help = 'Just open connection' )
            self.addArgument( 'ipnumber',   type = str )
            self.addArgument( 'portnumber', type = int )

            self.socketConnector = connector.SocketConnector( self.sres, self.sresSYS )
            
        def execute( self, cellcontents, kernel ):
            kernel.device.connect(
                self.socketConnector,
                ipnumber   = self._mapKnownArguments.ipnumber,
                portnumber = self._mapKnownArguments.portnumber
            )


            if kernel.device.isConnected:
                self.sres( f"\n ** Connected to {self.socketConnector.description} **\n\n", 32 )
   
                if self._mapKnownArguments.verbose:
                    self.sres( str(self.socketConnecto) )
                    
                self.sres( "\n" )
                #if not self._mapKnownArguments.raw:
                #    kernel.device.enterPasteMode()
                
            return cellcontents.strip() and cellcontents or None


    #==========================================================================
    
    class MagicWebSocketConnect( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%websocketconnect", sres, sresSYS, description = "connects to the webREPL websocket of an ESP8266 over wifi\n    websocketurl defaults to ws://192.168.4.1:8266 but be sure to be connected" )
    
            self.addAction  ( '--raw', help = 'Just open connection' )
            self.addArgument( 'websocketurl', type = str, default="ws://192.168.4.1:8266", nargs="?" )
            self.addArgument( '--password',   type = str )
            self.addAction  ( '--verbose' )

            self.webSocketConnector = connector.WebSocketConnector( self.sres, self.sresSYS )
        
        def execute( self, cellcontents, kernel ):
            if self._mapKnownArguments.password is None and not self._mapKnownArguments.raw:
                self.sres( self.format_help() )
                return None

            kernel.device.connect(
                self.webSocketConnector,
                websocketurl = self._mapKnownArguments.websocketurl
            )


            if kernel.device.isConnected:
                self.sres( f"\n ** Connected to {self.webSocketConnector.description} **\n\n", 32 )

                if not self._mapKnownArguments.raw:
                    pline = self.webSocketConnector.webSocket.recv()
                    self.sres( pline )
                    
                    if pline == 'Password: ' and self._mapKnownArguments.password is not None:
                        kernel.device.writeBytes( self._mapKnownArguments.password )
                        kernel.device.writeBytes( "\r\n" )
                        res = kernel.device.read_all()
                        self.sres(res)  # '\r\nWebREPL connected\r\n>>> '
                        
                        if not self._mapKnownArguments.raw:
                            if kernel.device.enterPasteMode(self._mapKnownArguments.verbose):
                                self.sresSYS("Ready.\n")
                            else:
                                self.sres("Disconnecting [paste mode not working]\n", 31)
                                kernel.device.disconnect( verbose = self._mapKnownArguments.verbose )
                                self.sres("  (You may need to reset the device)")
                                
                                cellcontents = ""
            else:
                cellcontents = ""
                
            return cellcontents.strip() and cellcontents or None

    #==========================================================================
    
    class MagicDisconnect( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%disconnect", sres, sresSYS, description = "disconnects from web/serial connection" )
    
            self.addAction( '--raw', help = 'Close connection without exiting paste mode' )

            self.addAlternativeName( "%serialdisconnect" )
            
        def execute( self, cellcontents, kernel ):
            kernel.device.disconnect( raw = self._mapKnownArguments.raw, verbose = True )
            return None

    
    #==========================================================================
    
    class MagicRebootDevice( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%rebootdevice", sres, sresSYS, description = "reboots device" )

            self.addAlternativeName( "%reboot" )
        
        def execute( self, cellcontents, kernel ):
        
            # Commands requires a connection
            if not kernel.device.isConnected:
                return cellcontents
                
            kernel.device.sendRebootMessage()
            kernel.device.enterPasteMode   ()
            
            return cellcontents.strip() and cellcontents or None


    #==========================================================================

    class MagicComment( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%comment", sres, sresSYS, description = "print this into output" )

        def execute( self, cellcontents, kernel ):
            if self._aMagicCommandArguments:
                self.sres( " ".join( self._aMagicCommandArguments ), asciigraphicscode = 32 )
            else:
                self.sres( "", asciigraphicscode = 32 )
            
            return cellcontents.strip() and cellcontents or None
            
        
    
    #==========================================================================

    #class MagicSuppressEndcode( Magic ):
    #    def __init__( self ):
    #        super().__init__( "%suppressendcode", description = doesn't send x04 or wait to read after sending the contents of the cell\n    (assists for debugging using %writebytes and %readbytes)" )    
    #
    #    def execute( self, cellcontents, kernel ):
    #        return None

    #==========================================================================

    class MagicWriteBytes( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%writebytes", sres, sresSYS, description = "does serial.write() of the python quoted string given" )
    
            self.addAction  ( '--binary',  '-b' )
            self.addAction  ( '--verbose', '-v' )
            self.addArgument( 'stringtosend', type = str )

            self.addAlternativeName( "%sendbytes" )
        
        def execute( self, cellcontents, kernel ):
            # Commands requires a connection
            if not kernel.device.isConnected:
                return cellcontents

            # (not effectively using the --binary setting)
            if self._mapKnownArguments:
                bytestosend = self._mapKnownArguments.stringtosend.encode().decode("unicode_escape").encode()
                result      = kernel.device.writeBytes( bytestosend )
                
                if self._mapKnownArguments.verbose:
                    self.sres( result, asciigraphicscode = 34 )
            else:
                self.sres( self.format_help() )
                
            return cellcontents.strip() and cellcontents or None

            
            
    #==========================================================================
    
    class MagicReadBytes( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%readbytes", sres, sresSYS, description = "does serial.read_all()" )
    
            self.addAction( '--binary', '-b' )
    
        def execute( self, cellcontents, kernel ):
            # Commands requires a connection
            if not kernel.device.isConnected:
                return cellcontents

            # (not effectively using the --binary setting)
            time.sleep(0.1)   # just give it a moment if running on from a series of values (could use an --expect keyword)

            l = kernel.device.read_all()
            
            if self._mapKnownArguments.binary:
                self.sres( repr(l) )
            elif type(l) == bytes:
                self.sres( l.decode(errors="ignore") )
            else:
                self.sres(l)   # strings come back from webrepl
                
            return cellcontents.strip() and cellcontents or None
    
    #==========================================================================

    class MagicSendToFile( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%sendtofile", sres, sresSYS, description = "send cell contents or file/directory to the microcontroller's file system" )
    
            self.addAction  ( '--append',  '-a' )
            self.addAction  ( '--mkdir',   '-d' )
            self.addAction  ( '--binary',  '-b' )
            self.addAction  ( '--execute', '-x' )
            self.addArgument( '--source', help = "source file", type = str, default = "<<cellcontents>>", nargs = "?" )
            self.addAction  ( '--quiet',   '-q' )
            self.addAction  ( '--QUIET',   '-Q' )
            self.addArgument( 'destinationfilename', type = str, nargs = "?" )

            self.addAlternativeName( "%savetofile" )
            self.addAlternativeName( "%savefile"   )
            self.addAlternativeName( "%sendfile"   )
         
        def execute( self, cellcontents, kernel ):
            if not kernel.device.isConnected:
                return cellcontents

            if self._mapKnownArguments and not (self._mapKnownArguments.source == "<<cellcontents>>" and not self._mapKnownArguments.destinationfilename) and (self._mapKnownArguments.source != None):
                destfn = self._mapKnownArguments.destinationfilename
                
                def doSendToFile( filename, contents) :
                    kernel.device.sendToFile( filename,
                        self._mapKnownArguments.mkdir,
                        self._mapKnownArguments.append,
                        self._mapKnownArguments.binary,
                        self._mapKnownArguments.quiet,
                        contents
                    )

                if self._mapKnownArguments.source == "<<cellcontents>>":
                    filecontents = cellcontents
                    
                    if not self._mapKnownArguments.execute:
                        cellcontents = None
                        
                    doSendToFile( destfn, filecontents )

                else:
                    mode = "rb" if self._mapKnownArguments.binary else "r"
                    
                    if not destfn:
                        destfn = os.path.basename(self._mapKnownArguments.source)
                    elif destfn[-1] == "/":
                        destfn += os.path.basename(self._mapKnownArguments.source)

                    if os.path.isfile( self._mapKnownArguments.source ):
                        filecontents = open(self._mapKnownArguments.source, mode).read()
                        
                        if self._mapKnownArguments.execute:
                            self.sres("Cannot excecute sourced file\n", 31)
                            
                        doSendToFile( destfn, filecontents )

                    elif os.path.isdir(self._mapKnownArguments.source):
                        if self._mapKnownArguments.execute:
                            self.sres( "Cannot excecute folder\n", 31 )
                            
                        for root, dirs, files in os.walk(self._mapKnownArguments.source):
                            for fn in files:
                                skip    = False
                                fp      = os.path.join(root, fn)
                                relpath = os.path.relpath(fp, self._mapKnownArguments.source)
                                
                                if relpath.endswith('.py'):
                                    # Check for compiled copy, skip py if exists
                                    if os.path.exists(fp[:-3] + '.mpy'):
                                        skip = True
                                        
                                if not skip:
                                    destpath     = os.path.join(destfn, relpath).replace('\\', '/')
                                    filecontents = open(os.path.join(root, fn), mode).read()
                                    doSendToFile(destpath, filecontents)
            else:
                self.sres( self.format_help() )
                
            return cellcontents   # allows for repeat %sendtofile in same cell

    #==========================================================================
    
    class MagicIPython( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%%iPython", sres, sresSYS, description = "run the cell contents in local iPython\n    Adds functions micropython_run, micropython_eval, micropython_value to IPython" )

        def execute( self, cellcontents, kernel ):
            # Commands requires a connection
            #if not kernel.device.isConnected:
            #    return cellcontents

            raise MicroPythonExtendedKernel.RunIPythonCellException


    #==========================================================================
    
    class MagicLs( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%ls", sres, sresSYS, description = "list directory of the microcontroller's file system" )
    
            self.addAction  ( '--recurse', '-r' )
            self.addArgument( 'dirname', type = str, nargs = "?" )

        def execute( self, cellcontents, kernel ):
            # Commands requires a connection
            if not kernel.device.isConnected:
                return cellcontents
            
            if self._mapKnownArguments:
                kernel.device.listDirectory( self._mapKnownArguments.dirname or "", self._mapKnownArguments.recurse )
            else:
                self.sres( self.format_help() )
            return None

    #==========================================================================

    class MagicFetchFile( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%fetchfile", sres, sresSYS, description = "fetch (and save) a file from the microcontroller's file system" )
    
            self.addAction  ( '--binary', '-b' )
            self.addAction  ( '--print',  '-p' )
            self.addAction  ( '--load',   '-l' )
            self.addAction  ( '--quiet',  '-q' )
            self.addAction  ( '--QUIET',  '-Q' )
            self.addArgument( 'sourcefilename',      type = str)
            self.addArgument( 'destinationfilename', type = str, nargs = "?" )

            self.addAlternativeName( "%readfile"      )
            self.addAlternativeName( "%fetchfromfile" )
        
        def execute( self, cellcontents, kernel ):
            # Commands requires a connection
            if not kernel.device.isConnected:
                return cellcontents
                
            if self._mapKnownArguments:
                fetchedcontents = kernel.device.fetchFile( self._mapKnownArguments.sourcefilename, self._mapKnownArguments.binary, self._mapKnownArguments.quiet )
                
                if self._mapKnownArguments.print:
                    self.sres( fetchedcontents.decode() if type(fetchedcontents)==bytes else fetchedcontents, clear_output = True )
                    
                if ( self._mapKnownArguments.destinationfilename or (not self._mapKnownArguments.print and not self._mapKnownArguments.load) ) and fetchedcontents:
                    dstfile = self._mapKnownArguments.destinationfilename or os.path.basename(self._mapKnownArguments.sourcefilename)
                    
                    self.sres( "Saving file to {}".format(repr(dstfile)) )
                    fout = open(dstfile, "wb" if self._mapKnownArguments.binary else "w")
                    fout.write(fetchedcontents)
                    fout.close()
                    
                if self._mapKnownArguments.load:
                    fcontents = fetchedcontents.decode() if type(fetchedcontents)==bytes else fetchedcontents
                    
                    if not self._mapKnownArguments.quiet:
                        fcontents = "#%fetchfile {}\n\n{}".format( " ".join(self._aMagicCommandArguments), fcontents )
                        
                    set_next_input_payload = { "source": "set_next_input", "text":fcontents, "replace": True }
                    
                    return set_next_input_payload
                
            else:
                self.sres( self.format_help() )
                
            return None


    #==========================================================================

    class MagicCapture( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%capture", sres, sresSYS, description = "capture output printed by device and save to a file" )
    
            self.addAction  ( '--quiet', '-q' )
            self.addAction  ( '--QUIET', '-Q' )
            self.addArgument( 'outputfilename', type = str )

        def execute( self, cellcontents, kernel ):
            # Commands requires a connection
            if not kernel.device.isConnected:
                return cellcontents
                
            if self._mapKnownArguments:
                self.sres( "Writing output to file {}\n\n".format(self._mapKnownArguments.outputfilename), asciigraphicscode = 32 )
                
                self.srescapturedoutputfile = open(self._mapKnownArguments.outputfilename, "w")
                self.srescapturemode        = (3 if self._mapKnownArguments.QUIET else (2 if self._mapKnownArguments.quiet else 1))
                self.srescapturedlinecount  = 0
            else:
                self.sres( self.format_help() )
                
            return cellcontents

            

    #==========================================================================
    
    class MagicWriteFile( Magic ):
        def __init__( self, sres, sresSYS ):
            super().__init__( "%%writefile", sres, sresSYS, description = "write contents of cell to a file on PC (local file system)" )
    
            self.addAction  ( '--append',  '-a' )
            self.addAction  ( '--execute', '-x' )  # @TODO ???
            self.addArgument( 'destinationfilename', type = str )

            self.addAlternativeName( "%%writetofile" )
            self.addAlternativeName( "%writefile"    )
        
        def execute( self, cellcontents, kernel ):
            # Commands requires a connection
            if not kernel.device.isConnected:
                return cellcontents

            if self._mapKnownArguments:
                if self._mapKnownArguments.append:
                    self.sres( "Appending to {}\n\n".format(self._mapKnownArguments.destinationfilename), asciigraphicscode = 32 )
                    
                    fout = open( self._mapKnownArguments.destinationfilename, ("a") )
                    fout.write( "\n" )
                else:
                    self.sres( "Writing {}\n\n".format(self._mapKnownArguments.destinationfilename), asciigraphicscode = 32 )
                    fout = open( self._mapKnownArguments.destinationfilename, ("w") )
                    
                fout.write(cellcontents)
                fout.close()
            else:
                self.sres( self.format_help() )
                
            if not self._mapKnownArguments.execute:
                return None
                
            return cellcontents # should add in some blank lines at top to get errors right

            
    def __init__( self, sres, sresSYS ):
        self._mapMagic            = {}
        self._mapMagicAlternative = {}
        
        self.add( Magics.MagicLsMagic         ( sres, sresSYS ) )
        self.add( Magics.MagicSerialConnect   ( sres, sresSYS ) )
        self.add( Magics.MagicBLEConnect      ( sres, sresSYS ) )
        self.add( Magics.MagicSocketConnect   ( sres, sresSYS ) )
        self.add( Magics.MagicWebSocketConnect( sres, sresSYS ) )
        self.add( Magics.MagicDisconnect      ( sres, sresSYS ) )
        self.add( Magics.MagicRebootDevice    ( sres, sresSYS ) )
        self.add( Magics.MagicComment         ( sres, sresSYS ) )
        self.add( Magics.MagicWriteBytes      ( sres, sresSYS ) )
        self.add( Magics.MagicReadBytes       ( sres, sresSYS ) )
        self.add( Magics.MagicSendToFile      ( sres, sresSYS ) )
        self.add( Magics.MagicIPython         ( sres, sresSYS ) )
        self.add( Magics.MagicLs              ( sres, sresSYS ) )
        self.add( Magics.MagicFetchFile       ( sres, sresSYS ) )
        self.add( Magics.MagicCapture         ( sres, sresSYS ) )
        self.add( Magics.MagicWriteFile       ( sres, sresSYS ) )

    def add( self, magic ):
        self._mapMagic[ magic.name ] = magic
        
        for strName in magic.getAlternativeNames():
            self._mapMagicAlternative[ strName  ] = magic

    def get( self, strName ):
        return self._mapMagic.get( strName )

    def getAlternative( self, strName ):
        return self._mapMagicAlternative.get( strName )
        
    
#######################################################################################  

# Complete streaming of data to file with a quiet mode (listing number of lines)
# Set this up for pulse reading and plotting in a second jupyter page

# argparse to say --binary in the help for the tag

# 2. Complete the implementation of websockets on ESP32  -- nearly there
# 3. Create the streaming of pulse measurements to a simple javascript frontend and listing
# 4. Try implementing ESP32 webrepl over these websockets using exec()
# 6. Finish debugging the IR codes


# * upgrade picoweb to handle jpg and png and js
# * code that serves a websocket to a browser from picoweb

# then make the websocket from the ESP32 as well
# then make one that serves out sensor data just automatically
# and access and read that from javascript
# and get the webserving of webpages (and javascript) also to happen


# should also handle shell-scripting other commands, like arpscan for mac address to get to ip-numbers

# compress the websocket down to a single straightforward set of code
# take 1-second of data (100 bytes) and time the release of this string 
# to the web-browser


class MicroPythonExtendedKernel(IPythonKernel):
    implementation = 'micropython_extended_kernel'
    implementation_version = "v1"

    banner = "MicroPython extended Jupyter Kernel v0.0.1"

    language_info = {
        'name'           : 'micropython',
        'codemirror_mode': 'python',
        'mimetype'       : 'text/x-python',
        'file_extension' : '.py',
        'pygments_lexer' : 'python',
    }

    #==========================================================================
    
    # @see https://github.com/Carglglz/jupyter_upydevice_kernel
    class RunIPythonCellException( Exception ):
        """
        Raised when a %%iPython cell is hit to tell kernel to forward to ipython
        """

    ## @see https://github.com/Carglglz/jupyter_upydevice_kernel
    #class SyncToLocalCellException(Exception):
    #    """
    #    Raised when a %sync cell is hit to tell kernel to forward device output to ipython
    #    """

    #==========================================================================
    
    def __init__(self, **kwargs):
        super().__init__( **kwargs )
        
        self.silent = False
        self.device = device.Device( self.sres, self.sresSYS )

        self.srescapturemode        = 0     # 0 none, 1 print lines, 2 print on-going line count (--quiet), 3 print only final line count (--QUIET)
        self.srescapturedoutputfile = None  # used by %capture command
        self.srescapturedlinecount  = 0
        self.srescapturedlasttime   = 0     # to control the frequency of capturing reported
        

        self.global_execution_count = 0 # @TODO do not understand what this does

        self.outputBuffer = ""

        self.magics = Magics( self.sres, self.sresSYS )
        
        try:
            self.shell.user_global_ns['micropython_run'] = self.micropythonRun
        except AttributeError:
            logger.exception("Could not set 'micropython_run' in local iPython environment")

        try:
            self.shell.user_global_ns['micropython_eval'] = self.micropythonEval
        except AttributeError:
            logger.exception("Could not set 'micropython_eval' in local iPython environment")

        try:
            self.shell.user_global_ns['micropython_value'] = self.micropythonValue
        except AttributeError:
            logger.exception("Could not set 'micropython_value' in local iPython environment")
    
    #==========================================================================

    def micropythonRun( self, functionName, *kargs, **kwargs ):
        command = "_=" + functionName + '('

        strComma = ''
        for arg in kargs:
            command += strComma + str(arg)  
    
            if not strComma:
                strComma = ","
    
        for arg in kwargs.items():
    
            command += strComma + arg[0] + '=' + repr(arg[1])
    
            if not strComma:
                strComma = ","
        
        command += ')'

        self.runnormalcell( command, bsuppressendcode=False )
        isSilent = self.silent
        self.silent = True
        self.runnormalcell( "print(repr(_))", bsuppressendcode=False )
        self.silent = isSilent
        return eval(self.outputBuffer.strip())

    def micropythonEval( self, command ):
        self.runnormalcell( command, bsuppressendcode=False )

    def micropythonValue( self, variableName ):
        isSilent = self.silent
        self.silent = True
        self.runnormalcell( f"print(repr({variableName}))", bsuppressendcode=False )
        self.silent = isSilent
        return eval(self.outputBuffer.strip())


    #==========================================================================
    
    def interpretMagicCommandLine( self, strMagicCommandLine, cellcontents ):

        #----------------------------------------------------------------------
        # 1) Check for valid syntax:
        
        try:
            aMagicCommand = shlex.split( strMagicCommandLine )
            
        except ValueError as e:
            self.sres( "\n\n***Bad magic command [%s]\n" % str(e), 31 )
            self.sres( strMagicCommandLine )
            return None

        #----------------------------------------------------------------------
        # 2) Check if magic command is known and parse command line:
        
        magic = self.magics.get( aMagicCommand[ 0 ] ) # First entry is magic command name

        if not magic:
            magicAlternative = self.magics.getAlternative( aMagicCommand[ 0 ] ) # First entry is magic command name

            if magicAlternative:
                self.sres( f"Did you mean {magicAlternative.name}\n", 31 )
                return None
            else:
                self.sres( f"Unrecognized magic command line {[strMagicCommandLine]}\n", 31 )
                return cellcontents
        
        magic.parse( aMagicCommand[ 1: ] ) # The second and the following entries are arguments

        #----------------------------------------------------------------------
        # 3) Check if help is requestet:
        
        if magic.hasHelpArgument():
            self.sres( magic.format_help() )
            return None


        #----------------------------------------------------------------------
        # 4) Try execute the magic command:

        return magic.execute( cellcontents, self )


    
    #==========================================================================
          
    def runnormalcell(self, cellcontents, bsuppressendcode):
        cmdlines = cellcontents.splitlines(True)
        r = self.device.read_all()
        if r:
            self.sres('[priorstuff] ')
            self.sres(str(r))
            
        for line in cmdlines:
            if line:
                if line[-2:] == '\r\n':
                    line = line[:-2]
                elif line[-1] == '\n':
                    line = line[:-1]
                self.device.writeLine( line )
                r = self.device.read_all()
                if r:
                    self.sres('[duringwriting] ')
                    self.sres(str(r))
                    
        if not bsuppressendcode:
            self.device.writeBytes( b'\r\x04' )
            self.device.receiveStream( bseekokay=True )

    #==========================================================================
            
    def sendcommand(self, cellcontents):
        bsuppressendcode = False  # can't yet see how to get this signal through
        
        if self.srescapturedoutputfile:
            self.srescapturedoutputfile.close()   # shouldn't normally get here
            self.sres("closing stuck open srescapturedoutputfile\n")
            self.srescapturedoutputfile = None
            
        # extract any %-commands we have here at the start (or ending?), tolerating pure comment lines and white space before the first % (if there's no %-command in there, then no lines at the front get dropped due to being comments)
        while True:
            matchMagicCommandLine = re.match("(?:(?:\s*|(?:\s*#.*\n))*)(%.*)\n?(?:[ \r]*\n)?", cellcontents)
            if not matchMagicCommandLine:
                break
            cellcontents = self.interpretMagicCommandLine(matchMagicCommandLine.group(1), cellcontents[matchMagicCommandLine.end():])   # discards the %command and a single blank line (if there is one) from the cell contents
            if isinstance(cellcontents, dict) and cellcontents.get("source") == "set_next_input":
                return cellcontents # set_next_input_payload:
            if cellcontents is None:
                return None
                
        if not self.device.isConnected:
            self.sres("No serial connected\n", 31)
            self.sres("  %serialconnect, %bleconnect, %websocketconnect, %socketconnect to connect\n")
            self.sres("  %lsmagic to list commands")
            return None
            
        # run the cell contents as normal
        if cellcontents:
            self.runnormalcell(cellcontents, bsuppressendcode)
        return None

   #==========================================================================
        
    # 1=bold, 31=red, 32=green, 34=blue; from http://ascii-table.com/ansi-escape-sequences.php
    def sres(self, output, asciigraphicscode=None, n04count=0, clear_output=False, execute_prompt=False ):
        self.outputBuffer = output
      
        if self.silent:
            return

        if self.srescapturedoutputfile and (n04count == 0) and not asciigraphicscode:
            self.srescapturedoutputfile.write(output)
            self.srescapturedlinecount += len(output.split("\n"))-1
            if self.srescapturemode == 3:            # 0 none, 1 print lines, 2 print on-going line count (--quiet), 3 print only final line count (--QUIET)
                return
                
            # changes the printing out to a lines captured statement every 1second.  
            if self.srescapturemode == 2:  # (allow stderrors to drop through to normal printing
                srescapturedtime = time.time()
                if srescapturedtime < self.srescapturedlasttime + 1:   # update no more frequently than once a second
                    return
                self.srescapturedlasttime = srescapturedtime
                clear_output = True
                output = "{} lines captured".format(self.srescapturedlinecount)

        if clear_output:  # used when updating lines printed
            self.send_response(self.iopub_socket, 'clear_output', {"wait":True})
            
        if asciigraphicscode:
            output = "\x1b[{}m{}\x1b[0m".format(asciigraphicscode, output)

        if execute_prompt:
            output_content = {
                'execution_count': self.global_execution_count,
                'data': {"text/plain": output}, 'metadata': {}
            }
            
            self.send_response(self.iopub_socket, 'execute_result', output_content)
        else:
            stream_content = {'name': ("stdout" if n04count == 0 else "stderr"), 'text': output }
            
            self.send_response(self.iopub_socket, 'stream', stream_content)
                
 
    #==========================================================================
        
    def sresSYS(self, output, clear_output=False):   # system call
        self.sres(output, asciigraphicscode=34, clear_output=clear_output)


 
    #==========================================================================
    # @overwrites IPythonKernel.do_execute
    #==========================================================================
    
    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        self.silent = silent
        if not code.strip():
            return {'status': 'ok', 'execution_count': self.shell.execution_count, 'payload': [], 'user_expressions': {}}

        interrupted = False
        self.global_execution_count += 1
        
        # clear buffer out before executing any commands (except the readbytes one)
        if self.device.isConnected and not re.match("\s*%readbytes|\s*%disconnect|\s*%serialconnect|\s*%bleconnect|\s*websocketconnect", code):
            priorbuffer = None
            try:
                priorbuffer = self.device.read_all()
            except KeyboardInterrupt:
                interrupted = True
            except OSError as e:
                priorbuffer = []
                self.sres("\n\n***Connection broken [%s]\n" % str(e.strerror), 31)
                self.sres("You may need to reconnect")
                self.device.disconnect(raw=True, verbose=True)
                
            except websocket.WebSocketConnectionClosedException as e:
                priorbuffer = []
                self.sres("\n\n***Websocket connection broken [%s]\n" % str(e.strerror), 31)
                self.sres("You may need to reconnect")
                self.device.disconnect(raw=True, verbose=True)
                
            if priorbuffer:
                if type(priorbuffer) == bytes:
                    try:
                        priorbuffer = priorbuffer.decode()
                    except UnicodeDecodeError:
                        priorbuffer = str(priorbuffer)
                
                for pbline in priorbuffer.splitlines():
                    if device.wifimessageignore.match(pbline):
                        continue   # filter out boring wifi status messages
                    if pbline:
                        self.sres('[leftinbuffer] ')
                        self.sres(str([pbline]))
                        self.sres('\n')

        
        set_next_input_payload = None
        
        try:
            if not interrupted:
                set_next_input_payload = self.sendcommand(code)
                self.shell.execution_count += 1
        except KeyboardInterrupt:
            interrupted = True
            
        except MicroPythonExtendedKernel.RunIPythonCellException:
            # Run local cell in regular ipython kernel
            code = code.replace('%%iPython', '')
            
            return super().do_execute(
                code             = code,
                silent           = silent,
                store_history    = store_history,
                user_expressions = user_expressions,
                allow_stdin      = allow_stdin
            )


        except OSError as e:
            self.sres("\n\n***OSError [%s]\n\n" % str(e.strerror))
        #except pexpect.EOF:
        #    self.sres(self.asyncmodule.before + 'Restarting Bash')
        #    self.startasyncmodule()

        if self.srescapturedoutputfile:
            if self.srescapturemode == 2:
                self.send_response(self.iopub_socket, 'clear_output', {"wait":True})
            if self.srescapturemode == 2 or self.srescapturemode == 3:
                output = "{} lines captured.".format(self.srescapturedlinecount)  # finish off by updating with the correct number captured
                stream_content = {'name': "stdout", 'text': output }
                self.send_response(self.iopub_socket, 'stream', stream_content)
                
            self.srescapturedoutputfile.close()
            self.srescapturedoutputfile = None
            self.srescapturemode = 0
            
        if interrupted:
            self.sresSYS("\n\n*** Sending Ctrl-C\n\n")
            if self.device.isConnected:
                self.device.writeBytes( b'\r\x03' )
                interrupted = True
                try:
                    self.device.receiveStream( bseekokay=False, b5secondtimeout=True )
                except KeyboardInterrupt:
                    self.sres("\n\nKeyboard interrupt while waiting response on Ctrl-C\n\n")
                except OSError as e:
                    self.sres("\n\n***OSError while issuing a Ctrl-C [%s]\n\n" % str(e.strerror))
            return {'status': 'abort', 'execution_count': self.global_execution_count}
            
        # everything already gone out with send_response(), but could detect errors (text between the two \x04s

        payload = [set_next_input_payload]  if set_next_input_payload else []   # {"source": "set_next_input", "text": "some cell content", "replace": False}
        
        return {'status': 'ok', 'execution_count': self.global_execution_count, 'payload': payload, 'user_expressions': {}}
                    
    #==========================================================================
    #
    #==========================================================================
