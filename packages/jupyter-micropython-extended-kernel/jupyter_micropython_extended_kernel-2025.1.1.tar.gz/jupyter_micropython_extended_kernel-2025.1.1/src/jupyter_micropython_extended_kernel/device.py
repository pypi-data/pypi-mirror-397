import logging, time, os, re, binascii, subprocess, ast, serial

#==============================================================================
#
#==============================================================================

#serialtimeout      = 0.5
serialtimeoutcount = 10

wifimessageignore = re.compile("(\x1b\[[\d;]*m)?[WI] \(\d+\) (wifi|system_api|modsocket|phy|event|cpu_start|heap_init|network|wpa): ")


#==============================================================================
#
#==============================================================================

# merge uncoming serial stream and break at OK, \x04, >, \r\n, and long delays 
# (must make this a member function so does not have to switch on the type of s)
def yieldserialchunk( connector ):
    #global serialtimeout
    global serialtimeoutcount
    global wifimessageignore
    
    res = []
    n = 0
    
    connector.readInit() # needed for WebSocketConnector
    
    while True:
        try:
            b = connector.read()

        except serial.SerialException as e:
            yield b"\r\n**[ys] "
            yield str(type(e)).encode("utf8")
            yield b"\r\n**[ys] "
            yield str(e).encode("utf8")
            yield b"\r\n\r\n"
            break
            
        if not b:
            if res and (res[0] != 'O' or len(res) > 3):
                yield b''.join(res)
                res.clear()
            else:
                n += 1
                if (n%serialtimeoutcount) == 0:
                    yield b''   # yield a blank line every (serialtimeout*serialtimeoutcount) seconds
                
        elif b == b'K' and len(res) >= 1 and res[-1] == b'O':
            if len(res) > 1:
                yield b''.join(res[:-1])
            yield b'OK'
            res.clear()
        elif b == b'\x04' or b == b'>':
            if res:
                yield b''.join(res)
            yield b
            res.clear()
        else:
            res.append(b)
            if b == b'\n' and len(res) >= 2 and res[-2] == b'\r':
                yield b''.join(res)
                res.clear()


#==============================================================================
#
#==============================================================================

class Device:
    def __init__( self, sres, sresSYS ):
        self.sres      = sres   # two output functions borrowed across
        self.sresSYS   = sresSYS

        self.connector = None

    #==========================================================================

    @property
    def isConnected( self ):
        return self.connector and self.connector.isConnected
    
    #==========================================================================
    
    def read_all( self ):  # usually used to clear the incoming buffer, results are printed out rather than used
        if self.connector:
            return self.connector.read_all()
        else:
            return b''
            
    #==========================================================================

    def connect( self, connector, **kwargs ):
        self.disconnect( verbose = True )
        self.connector = connector
        self.connector.connect( **kwargs )

    #==========================================================================
    
    def disconnect( self, raw = False, verbose = False ):
        if not raw:
            self.exitPasteMode(verbose)   # this doesn't seem to do any good (paste mode is left on disconnect anyway)

        self.workingserialchunk = None
        
        if self.connector:
            if verbose:
                self.sresSYS( f"\nClosing {self.connector.description}\n" )
            self.connector.close()
            self.connector = None
    
   #==========================================================================

    def writeBytes( self, aByte, isVerbose = False ):
        if self.connector:
            self.connector.write( aByte, isVerbose = isVerbose )


    #==========================================================================

    def writeLine( self, line ):
        if self.connector:
            self.connector.write(line.encode("utf8"))
            self.connector.write(b'\r\n')
    
    #==========================================================================
    
    def sendRebootMessage(self):
        if self.connector:
            self.connector.write(b"\x03\r")  # quit any running program
            self.connector.write(b"\x02\r")  # exit the paste mode with ctrl-B
            self.connector.write(b"\x04\r")  # soft reboot code

    

    #==========================================================================
            
    def receiveStream( self, bseekokay, bwarnokaypriors=True, b5secondtimeout=False, bfetchfilecapture_nchunks=0 ):
        n04count = 0
        brebootdetected = False
        res = []
        
        for j in range(2):  # for restarting the chunking when interrupted
            if self.workingserialchunk is None:
                self.workingserialchunk = yieldserialchunk( self.connector )

            indexprevgreaterthansign = -1
            index04line = -1
            
            for i, rline in enumerate( self.workingserialchunk ):
                
                assert rline is not None

                # warning message when we are waiting on an OK
                if bseekokay and bwarnokaypriors and (rline != b'OK') and (rline != b'>') and rline.strip():
                    self.sres("\n[missing-OK]")

                # the main interpreting loop
                if rline == b'OK' and bseekokay:
                    if i != 0 and bwarnokaypriors:
                        self.sres("\n\n[Late OK]\n\n")
                    bseekokay = False

                # one of 2 Ctrl-Ds in the return from execute in paste mode
                elif rline == b'\x04':
                    n04count += 1
                    index04line = i

                # leaving condition where OK...x04...x04...> has been found in paste mode
                elif rline == b'>' and n04count >= 2 and not bseekokay:
                    if n04count != 2:
                        self.sres("[too many x04s %d]" % n04count)
                    break

                elif rline == b'':
                    if b5secondtimeout:
                        self.sres("[Timed out waiting for recognizable response]\n", 31)
                        return False
                    self.sres(".")  # dot holding position to prove it's alive

                elif rline == b'Type "help()" for more information.\r\n':
                    brebootdetected = True
                    self.sres(rline.decode(), n04count=n04count)

                elif rline == b'>':
                    indexprevgreaterthansign = i
                    self.sres('>', n04count=n04count)

                # looks for ">>> "
                elif rline == b' ' and brebootdetected and indexprevgreaterthansign == i-1:
                    self.sres("[reboot detected %d]" % n04count)
                    self.enterPasteMode()  # this is unintentionally recursive, but after a reboot has been seen we need to get into paste mode
                    self.sres(' ', n04count=n04count)
                    break

                # normal processing of the string of bytes that have come in
                else:
                    try:
                        ur = rline.decode()
                    except UnicodeDecodeError:
                        ur = str(rline)
                    if not wifimessageignore.match(ur):
                        if bfetchfilecapture_nchunks:
                            if res and res[-1][-2:] != "\r\n":
                                res[-1] = res[-1] + ur   # need to rejoin strings that have been split on the b"OK" string by the lexical parser
                            else:
                                res.append(ur)
                            if (i%10) == 0 and bfetchfilecapture_nchunks > 0:
                                self.sres( "%d%% fetched\n" % int(len(res)/bfetchfilecapture_nchunks*100 + 0.5), clear_output=True )
                        else:
                            self.sres(ur, n04count=n04count)

            # else on the for-loop, means the generator has ended at a stop iteration
            # this happens with Keyboard interrupt, and generator needs to be rebuilt
            else:  # of the for-command
                self.workingserialchunk = None
                continue

            break   # out of the for loop
        return res if bfetchfilecapture_nchunks else True

    #==========================================================================

    def sendToFile(self, destinationfilename, bmkdir, bappend, bbinary, bquiet, filecontents):
        
        if not self.connector.supportsFileTransfere:
            self.sres( f"File transfers not implemented for {self.connector.id}\n", 31 )
            return

        if not bbinary:
            lines = filecontents.splitlines(True)
            maxlinelength = max(map(len, lines), default=0)
            if maxlinelength > 250:
                self.sres("Line length {} exceeds maximum for line ascii files, try --binary\n".format(maxlinelength), 31)
                return


        if bmkdir:
            dseq = [ d  for d in destinationfilename.split("/")[:-1]  if d]
            if dseq:
                self.connector.write( b'import os\r\n' )
                
                for i in range(len(dseq)):
                    self.connector.write( 'try:  os.mkdir({})\r\n'.format(repr("/".join(dseq[:i+1]))).encode() )
                    self.connector.write( b'except OSError:  pass\r\n' )

        fmodifier = ("a" if bappend else "w")+("b" if bbinary else "")
        
        if bbinary:
            self.connector.write( b"import ubinascii; O6 = ubinascii.a2b_base64\r\n" )
            
        self.connector.write( "O=open({}, '{}')\r\n".format(repr(destinationfilename), fmodifier).encode() )
        self.connector.write( b'\r\x04' )  # intermediate execution
        self.receiveStream( bseekokay=True )
        clear_output = True  # set this to False to help with debugging
        
        if bbinary:
            if type(filecontents) == str:
                filecontents = filecontents.encode()
                
            chunksize = 30
            nchunks = int(len(filecontents)/chunksize)

            for i in range(nchunks+1):
                bchunk = filecontents[i*chunksize:(i+1)*chunksize]
                self.connector.write( b'O.write(O6("' )
                self.connector.write( binascii.b2a_base64(bchunk)[:-1] )
                self.connector.write( b'"))\r\n' )
                
                if (i%10) == 9:
                    self.connector.write( b'\r\x04' )  # intermediate executions
                    self.receiveStream( bseekokay=True )
                    
                    if not bquiet:
                        self.sres("{}%, chunk {}".format(int((i+1)/(nchunks+1)*100), i+1), clear_output=clear_output)
            self.sres("Sent {} bytes in {} chunks to {}.\n".format(len(filecontents), i+1, destinationfilename), clear_output=not bquiet)
            
        else:
            i = -1
            linechunksize = 5

            if bappend:
                self.connector.write( "O.write('\\n')\r\n".encode() )   # avoid line concattenation on appends
                
            for i, line in enumerate(lines):
                self.connector.write( "O.write({})\r\n".format(repr(line)).encode() )
                
                if (i%linechunksize) == linechunksize-1:
                    self.connector.write( b'\r\x04' )  # intermediate executions
                    self.receiveStream( bseekokay=True )
                    
                    if not bquiet:
                        self.sres("{}%, line {}\n".format(int((i+1)/(len(lines)+1)*100), i+1), clear_output=clear_output)
                        
            self.sres( "Sent {} lines ({} bytes) to {}.\n".format(i+1, len(filecontents), destinationfilename), clear_output=(clear_output and not bquiet) )

        self.connector.write( "O.close()\r\n".encode() )
        self.connector.write( "del O\r\n".encode() )
        self.connector.write( b'\r\x04' )
        
        self.receiveStream( bseekokay=True )

    #==========================================================================
    
    def fetchFile( self, sourcefilename, bbinary, bquiet ):

        if not self.connector.supportsFileTransfere:
            self.sres( f"File transfers not implemented for {self.connector.id}\n", 31 )
            return
        
        if not bbinary:
            self.sres( "non-binary mode not implemented, switching to binary" )
            
        if True:
            chunksize = 30
            self.connector.write( b"import sys,os;O7=sys.stdout.write\r\n" )
            self.connector.write( b"import ubinascii;O8=ubinascii.b2a_base64\r\n" )
            self.connector.write( "O=open({},'rb')\r\n".format(repr(sourcefilename)).encode() )
            self.connector.write( b"O9=bytearray(%d)\r\n" % chunksize)
            self.connector.write( "O4=os.stat({})[6]\r\n".format(repr(sourcefilename)).encode() )
            self.connector.write( b"print(O4)\r\n" )
            self.connector.write( b'\r\x04' )   # intermediate execution to get chunk size
            
            chunkres = self.receiveStream( bseekokay=True, bfetchfilecapture_nchunks=-1 )
            
            try:
                nbytes = int("".join(chunkres))
            except ValueError:
                self.sres(str(chunkres))
                return None
                
            self.connector.write( b"O7(O8(O.read(O4%%%d)))\r\n" % chunksize )  # get sub-block
            self.connector.write( b"while O.readinto(O9): O7(O8(O9))\r\n" )
            self.connector.write( b"O.close(); del O,O7,O8,O9,O4\r\n" )
            self.connector.write( b'\r\x04' )
            
            chunks = self.receiveStream( bseekokay=True, bfetchfilecapture_nchunks=nbytes//chunksize+1 )
            rres = [ ]
            
            for ch in chunks:
                try:
                    rres.append(binascii.a2b_base64(ch))
                except binascii.Error as e:
                    self.sres(str(e))
                    self.sres(str([ch]))
                    
            res = b"".join(rres)
            
            if not bquiet:
                self.sres( "Fetched {}={} bytes from {}.\n".format(len(res), nbytes, sourcefilename), clear_output=True )
                
            return res
            
        return None

    #==========================================================================
    
    def listDirectory( self, dirname, recurse ):
        
        if not self.connector.supportsFileTransfere:
            self.sres( f"Listing directory not implemented for {self.connector.id}\n", 31 )
            return
        
        self.sres( "Listing directory '%s'.\n" % (dirname or '/') )

        
        def ssldir(d):
            self.connector.write( b"import os,sys\r\n" )
            self.connector.write( ("for O in os.ilistdir(%s):\r\n" % repr(d)).encode() )
            self.connector.write( b"  sys.stdout.write(repr(O))\r\n" )
            self.connector.write( b"  sys.stdout.write('\\n')\r\n" )
            self.connector.write( b"del O\r\n" )
            self.connector.write( b'\r\x04' )
            
            k = self.receiveStream(bseekokay=True, bfetchfilecapture_nchunks=-1)
            ll = list(map(ast.literal_eval, k))
            ll.sort()
            
            for l in ll:
                if l[1] == 0x4000:
                    self.sres("             %s/\n"%(d+'/'+l[0]).lstrip("/"))
                else:
                    self.sres("%9d    %s\n" % (l[3], (d+'/'+l[0]).lstrip("/")))
                    
            return [ d+"/"+l[0]  for l in ll  if l[1] == 0x4000 ]
            
        ld = ssldir(dirname)
        
        if recurse:
            while ld:
                d = ld.pop(0)
                self.sres("\n%s:\n"%d.lstrip("/"))
                ld.extend(ssldir(d))
                
        return None
        

    #==========================================================================
    # I don't think we ever make a connection and it's still in paste mode 
    # (this is revoked on connection break,
    # but I am trying to use exitPasteMode to make it better)
    
    def enterPasteMode(self, verbose=True):         
        # now sort out connection situation
        if self.connector:
            if self.connector.needsPasteMode:
                time.sleep( 0.2 )               # try to give a moment to connect before issuing the Ctrl-C
                self.connector.write( b'\x03' ) # ctrl-C: kill off running programs
                time.sleep( 0.1 )
                aByte = self.read_all()
                
                if aByte[-6:] == b'\r\n>>> ':
                    if verbose:
                        self.sres( 'repl is in normal command mode\n' )
                        self.sres( '[\\r\\x03\\x03] ' )
                        self.sres( str(aByte) )
                else:
                    if verbose:
                        self.sres( 'normal repl mode not detected ' )
                        self.sres( str(aByte) )
                        self.sres( '\nnot command mode\n' )
                        
                    
                #self.connector.write(b'\r\x02' ) # ctrl-B: leave paste mode if still in it <-- doesn't work as when not in paste mode it reboots the device
                self.connector.write( b'\r\x01' ) # ctrl-A: enter raw REPL
                time.sleep(0.1)
                aByte = self.read_all()
                
                if verbose and aByte:
                    self.sres( '\n[\\r\\x01] ' )
                    self.sres( str(aByte) )
                
                self.connector.write( b'1\x04' )  # single character program "1" to run so receiveStream works
            else:
                self.connector.write( b'1\x04' )  # single character program "1" to run so receiveStream works
                
        return self.receiveStream( bseekokay=True, bwarnokaypriors=False, b5secondtimeout=True )
        

    #==========================================================================
        
    def exitPasteMode( self, verbose ):   # try to make it clean
        if self.connector and self.connector.isConnected and self.connector.needsPasteMode:
            try:
                self.connector.write( b'\r\x03\x02' )    # ctrl-C; ctrl-B to exit paste mode
                time.sleep(0.1)
                aByte = self.read_all()

            except serial.SerialException as e:
                self.sres( f"serial exception on close {e}\n" )
                return
            
            if verbose:
                self.sresSYS( 'attempt to exit paste mode\n' )
                self.sresSYS( '[\\r\\x03\\x02] ' )
                self.sres( str(aByte) )
                