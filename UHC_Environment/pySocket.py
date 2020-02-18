import os
import ctypes
import sys

class BCVTBPySocket:
    def __init__(self, ):
        self.Clib = None
        
        self.sockfd = -1             # Socket File descriptor
        self.flaWri = 0              # 0 = Normal operation, flag to write to the socket stream
        self.flaRea = 0              # 0 = Normal operation, flag read from the socket stream
        self.simTimWri = 0           # Simulation Time write to socket
        self.simTimRea = 0           # Simulation Time wite to socket
        
        self.nDblWri = 1             # number of variables to write to socket
        self.dblValWri = None        # DATA WRITE FROM THE SOCKET
        
        self.nDblRea = 1             # number of double variables to read from socket
        self.dblValRea = None        # DATA READ FROM THE SOCKET
        self.nIntRea = 1             # number of int variables to read from socket
        self.intValRea = None        # DATA READ FROM THE SOCKET
        self.nBooRea = 1             # number of bool variables to read from socket
        self.booValRea = None        # DATA READ FROM THE SOCKET


        #  Get the C lib instance as soon as the class is init
        self.getClib()

    def getClib(self,):
        so_file = ''
        # Search for file path
        for fname in os.listdir():
            if 'so' in fname.split('.'):
                so_file = os.path.abspath(fname)
                break
        
        # Calling the C lib in Python
        print("Opening the C Lib: ", so_file)
        if so_file != '':
            self.Clib = ctypes.CDLL(so_file)
        else:
            print("Error: Could not find the .SO file -- Place the Clib file in same folder as pySocket")
            sys.exit(1)

    

    def establishClientSocket(self,):
        # Defining the arg type for C Lin I/O
        self.Clib.establishclientsocket.argtypes = [ctypes.c_char_p]
        self.Clib.establishclientsocket.restype  = ctypes.c_int

        print("Establishing Socket Connection ...")
        for fname in os.listdir():
            if 'socket.cfg' in fname:
                socketConfFile = b'socket.cfg'
                break
        if socketConfFile != '':
            # Calling function
            self.sockfd = self.Clib.establishclientsocket(socketConfFile)
        else:
            print("Error: Could not find socket.cfg")
            self.sockfd = -100



    def exchangedoubleswithsocket(self, dataWrite):

        retVal = -1

        # Defining the variable type
        sockfd = ctypes.c_int(self.sockfd)
        flaWri = ctypes.c_int(self.flaWri)
        flaRea = ctypes.c_int(self.flaRea)
        simTimRea = ctypes.c_double(self.simTimRea)
        simTimWri = ctypes.c_double(self.simTimWri)
        nDblWri = ctypes.c_int(self.nDblWri)
        dblValWri = (ctypes.c_double*nDblWri.value)()
        nDblRea = ctypes.c_int(self.nDblRea)
        dblValRea = (ctypes.c_double*nDblRea.value)()
        
        # Wrap the write data to C variable
        if len(dataWrite) == nDblWri.value:
            for i in range(nDblWri.value):
                dblValWri[i] = dataWrite[i]


            # Defining the arg type for the input fun1 
            self.Clib.exchangedoubleswithsocket.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                                            ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_double),
                                                            ctypes.c_double*nDblWri.value, ctypes.POINTER(ctypes.c_double), ctypes.c_double*nDblRea.value]
            self.Clib.exchangedoubleswithsocket.restype  = ctypes.c_int
            
            #print("Calling the exchangedoubleswithsocket ...")
            # Return Value from the function
            retVal = self.Clib.exchangedoubleswithsocket(ctypes.byref(sockfd), ctypes.byref(flaWri), ctypes.byref(flaRea),
                                                        ctypes.byref(nDblWri), ctypes.byref(nDblRea), ctypes.byref(simTimWri),
                                                        dblValWri, ctypes.byref(simTimRea), dblValRea)
            self.flaRea = flaRea.value
            self.nDblRea = nDblRea.value
            self.simTimRea = simTimRea.value
            self.dblValRea = dblValRea
            
        else:
            print("Error: The write data length different from defined nDblWri.")        
        
        return retVal


    def sendclientmessage(self, flag):
        # Defining the variable type
        sockfd   = ctypes.c_int(self.sockfd)
        flaWrite = ctypes.c_int(flag)
        
        # Defining the arg type for the input fun13
        self.Clib.sendclientmessage.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
        self.Clib.sendclientmessage.restype  = ctypes.c_int

        print("Sending Close Socket Flag to BCVTB ...")
        return self.Clib.sendclientmessage(ctypes.byref(sockfd), ctypes.byref(flaWrite))
    

    def readfromsocket(self, ):
        # Defining the variable type
        sockfd = ctypes.c_int(self.sockfd)
        flaRea = ctypes.c_int(self.flaRea)
        nDblRea = ctypes.c_int(self.nDblRea)
        nIntRea = ctypes.c_int(self.nIntRea)
        nBooRea = ctypes.c_int(self.nBooRea)
        simTimRea = ctypes.c_double(self.simTimRea)
        dblValRea = (ctypes.c_double*nDblRea.value)()
        intValRea = (ctypes.c_int*nIntRea.value)()
        booValRea = (ctypes.c_int*nBooRea.value)()

        # Defining the arg type for the input fun
        self.Clib.readfromsocket.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                             ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
                                             ctypes.POINTER(ctypes.c_double),
                                             ctypes.c_double*nDblRea.value, ctypes.c_int*nIntRea.value, ctypes.c_int*nBooRea.value]
        self.Clib.readfromsocket.restype  = ctypes.c_int

        print("Reading from the Socket on BCVTB ...")
        self.Clib.readfromsocket(ctypes.byref(sockfd), ctypes.byref(flaRea),
                                 ctypes.byref(nDblRea), ctypes.byref(nIntRea), ctypes.byref(nBooRea),
                                 ctypes.byref(simTimRea),
                                 dblValRea, intValRea, booValRea)
        
        self.flaRea = flaRea.value
        self.nDblRea = nDblRea.value
        self.simTimRea = simTimRea.value
        self.dblValRea = dblValRea


    def closeipc(self,):
        # Defining the variable type
        sockfd = ctypes.c_int(self.sockfd)

        # Defining the arg type for the input fun13
        self.Clib.closeipc.argtypes = [ctypes.POINTER(ctypes.c_int)]
        self.Clib.closeipc.restype  = ctypes.c_int

        print("Calling the closeipc ...")
        return self.Clib.closeipc(ctypes.byref(sockfd))


if __name__ == "__main__":
    ps = BCVTBPySocket()