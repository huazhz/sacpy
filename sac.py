'''
A simple class that deals with sac files

Written by Z. Duputel, December 2013
'''

import os,sys
import numpy  as np
import shutil as sh
import scipy.signal as signal
from copy     import deepcopy
from datetime import datetime, timedelta


NVHDR = 6
ITIME = 1


def unpack_c(chararray,rm_spaces=True):
    S = ''
    for c in chararray:
        c = c.decode('utf-8')
        if rm_spaces and (c == ' ' or c == ''):
            break
        S+=c
    return S


def pack_c(char,size):
    S = deepcopy(char)
    c_size = len(char)
    for i in range(size-c_size):
        S = S+' '
    return np.array(S,dtype='c')


class SacError(Exception):
    """
    Raised if the SAC file is corrupted
    """
    pass


class sac(object):
    '''
    A simple sac class
    '''
    
    def __init__(self,filename=None):
        '''
        Constructor
        Args:
            * filename: read sac filename (optional)
        '''        
        self.delta  =  -12345.
        self.depmin =  -12345.
        self.depmax =  -12345.
        self.scale  =  -12345.
        self.odelta =  -12345.
        self.b      =  -12345.
        self.e      =  -12345.
        self.o      =  -12345.
        self.a      =  -12345.
        self.internal1 = -12345.
        self.t      = np.ones((10,),dtype='float32')*-12345. 
        self.f      =  -12345.
        self.resp   = np.ones((10,),dtype='float32')*-12345. 
        self.stla   =  -12345.
        self.stlo   =  -12345.
        self.stel   =  -12345. 
        self.stdp   =  -12345. 
        self.evla   =  -12345.
        self.evlo   =  -12345.
        self.evel   =  -12345.
        self.evdp   =  -12345.
        self.mag    =  -12345.
        self.user   = np.ones((10,),dtype='float32')*-12345.
        self.dist   =  -12345.
        self.az     =  -12345.
        self.baz    =  -12345.
        self.gcarc  =  -12345.
        self.internal2 = -12345.
        self.internal3 = -12345.
        self.depmen =  -12345.
        self.cmpaz  =  -12345.
        self.cmpinc =  -12345.
        self.xminimum = -12345.
        self.xmaximum = -12345.
        self.yminimum = -12345.
        self.ymaximum = -12345.
        self.nzyear =  -12345
        self.nzjday =  -12345
        self.nzhour =  -12345
        self.nzmin  =  -12345
        self.nzsec  =  -12345
        self.nzmsec =  -12345
        self.nvhdr  =  NVHDR
        self.norid  =  -12345
        self.nevid  =  -12345
        self.npts   =  -12345
        self.internal4 = -12345
        self.nwfid  = -12345
        self.nxsize = -12345
        self.nysize = -12345
        self.iftype =  ITIME
        self.idep   = -12345
        self.iztype = -12345
        self.iinst  = -12345
        self.istreg = -12345
        self.ievreg = -12345
        self.ievtyp = -12345
        self.iqual  = -12345
        self.isynth = -12345
        self.imagtyp = -12345
        self.imagsrc = -12345
        self.leven  = -12345
        self.lpspol = -12345
        self.lovrok = -12345
        self.lcalda = -12345
        self.kstnm  = '-12345'
        self.kevnm  = '-12345'
        self.khole  = '-12345'
        self.ko     = '-12345'     
        self.ka     = '-12345' 
        self.kt = []
        for i in range(10):
            self.kt.append('-12345')
            self.kf     = '-12345'
        self.kuser  = []
        for i in range(3):
            self.kuser.append('-12345')
        self.kcmpnm = '-12345'
        self.knetwk = '-12345'
        self.kdatrd = '-12345'
        self.kinst  = '-12345'
        self.id     = self.knetwk+'_'+self.kstnm+'_'+self.khole+'_'+self.kcmpnm
        self.depvar =  np.array([])

        # Read sac file if filename is specified
        if filename is not None:
            assert os.path.exists(filename), filename+' not found'
            self.read(filename)

        # Spectrum flag
        self.spec = False

        # All done
        

    def read(self,FILE,npts=None,datflag=True):
        '''
        Read sac file
        Args:
           * FILE: input sac file name
           * npts: number of data points to be read
           * datflag: True: read data, False: read header only
        '''
        # Open file
        fid     = open(FILE,'rb')
        
        # Check endianness
        fid.seek(316,0)
        npts = np.fromfile(fid,'<i4',1)[0]
        fid.seek(0,2)
        fsize = fid.tell()
        if fsize==632+4*npts:
            ftype='<f4'
            itype='<i4'
        elif fsize==632+4*npts.byteswap():
            ftype='>f4'
            itype='>i4'
        else:
            raise SacError("Number of points in header and length of trace inconsistent !")
        
        # Read header
        fid.seek(0,0)
        self.delta     = np.fromfile(fid,ftype,1)[0]
        self.depmin    = np.fromfile(fid,ftype,1)[0]
        self.depmax    = np.fromfile(fid,ftype,1)[0]
        self.scale     = np.fromfile(fid,ftype,1)[0]
        self.odelta    = np.fromfile(fid,ftype,1)[0]
        self.b         = np.fromfile(fid,ftype,1)[0]
        self.e         = np.fromfile(fid,ftype,1)[0]
        self.o         = np.fromfile(fid,ftype,1)[0]
        self.a         = np.fromfile(fid,ftype,1)[0]
        self.internal1 = np.fromfile(fid,ftype, 1)[0]
        self.t         = np.fromfile(fid,ftype,10)
        self.f         = np.fromfile(fid,ftype,1)[0]
        self.resp      = np.fromfile(fid,ftype,10)
        self.stla      = np.fromfile(fid,ftype,1)[0]
        self.stlo      = np.fromfile(fid,ftype,1)[0]
        self.stel      = np.fromfile(fid,ftype,1)[0]
        self.stdp      = np.fromfile(fid,ftype,1)[0]
        self.evla      = np.fromfile(fid,ftype,1)[0]
        self.evlo      = np.fromfile(fid,ftype,1)[0]
        self.evel      = np.fromfile(fid,ftype,1)[0]
        self.evdp      = np.fromfile(fid,ftype,1)[0]
        self.mag       = np.fromfile(fid,ftype,1)[0]
        self.user      = np.fromfile(fid,ftype,  10)
        self.dist      = np.fromfile(fid,ftype,1)[0]
        self.az        = np.fromfile(fid,ftype,1)[0]
        self.baz       = np.fromfile(fid,ftype,1)[0]
        self.gcarc     = np.fromfile(fid,ftype,1)[0]
        self.internal2 = np.fromfile(fid,ftype,1)[0]
        self.internal3 = np.fromfile(fid,ftype,1)[0]
        self.depmen    = np.fromfile(fid,ftype,1)[0]
        self.cmpaz     = np.fromfile(fid,ftype,1)[0]
        self.cmpinc    = np.fromfile(fid,ftype,1)[0]
        self.xminimum  = np.fromfile(fid,ftype,1)[0]
        self.xmaximum  = np.fromfile(fid,ftype,1)[0]
        self.yminimum  = np.fromfile(fid,ftype,1)[0]
        self.ymaximum  = np.fromfile(fid,ftype,1)[0]
        fid.seek(7*4,1)
        self.nzyear    = np.fromfile(fid,itype,1)[0]
        self.nzjday    = np.fromfile(fid,itype,1)[0]
        self.nzhour    = np.fromfile(fid,itype,1)[0]
        self.nzmin     = np.fromfile(fid,itype,1)[0]
        self.nzsec     = np.fromfile(fid,itype,1)[0]
        self.nzmsec    = np.fromfile(fid,itype,1)[0]
        self.nvhdr     = np.fromfile(fid,itype,1)[0]
        self.norid     = np.fromfile(fid,itype,1)[0]
        self.nevid     = np.fromfile(fid,itype,1)[0]
        self.npts      = np.fromfile(fid,itype,1)[0]
        self.internal4 = np.fromfile(fid,itype,1)[0]
        self.nwfid     = np.fromfile(fid,itype,1)[0]
        self.nxsize    = np.fromfile(fid,itype,1)[0]
        self.nysize    = np.fromfile(fid,itype,1)[0]
        fid.seek(4,1);
        self.iftype    = np.fromfile(fid,itype,1)[0]
        self.idep      = np.fromfile(fid,itype,1)[0]
        self.iztype    = np.fromfile(fid,itype,1)[0]
        fid.seek(4,1);
        self.iinst     = np.fromfile(fid,itype,1)[0]
        self.istreg    = np.fromfile(fid,itype,1)[0]
        self.ievreg    = np.fromfile(fid,itype,1)[0]
        self.ievtyp    = np.fromfile(fid,itype,1)[0]
        self.iqual     = np.fromfile(fid,itype,1)[0]
        self.isynth    = np.fromfile(fid,itype,1)[0]
        self.imagtyp   = np.fromfile(fid,itype,1)[0]
        self.imagsrc   = np.fromfile(fid,itype,1)[0]
        fid.seek(8*4,1);
        self.leven     = np.fromfile(fid,itype,1)[0]
        self.lpspol    = np.fromfile(fid,itype,1)[0]
        self.lovrok    = np.fromfile(fid,itype,1)[0]
        self.lcalda    = np.fromfile(fid,itype,1)[0]
        fid.seek(4,1);
        self.kstnm     = unpack_c(np.fromfile(fid,'c',8))
        self.kevnm     = unpack_c(np.fromfile(fid,'c',16),False)
        self.khole     = unpack_c(np.fromfile(fid,'c',8))
        self.ko        = unpack_c(np.fromfile(fid,'c',8))
        self.ka        = unpack_c(np.fromfile(fid,'c',8))
        for i in range(10):
            self.kt[i] = unpack_c(np.fromfile(fid,'c',8))
        self.kf = unpack_c(np.fromfile(fid,'c',8))
        for i in range(3):
            self.kuser[i] = unpack_c(np.fromfile(fid,'c',8))
        self.kcmpnm = unpack_c(np.fromfile(fid,'c',8))
        self.knetwk = unpack_c(np.fromfile(fid,'c',8))
        self.kdatrd = unpack_c(np.fromfile(fid,'c',8))
        self.kinst  = unpack_c(np.fromfile(fid,'c',8))
        self.e = self.b + float(self.npts-1) * self.delta
        if self.khole=='' or self.khole=='-12345':
            self.khole = '--'
        self.id = self.knetwk+'_'+self.kstnm+'_'+self.khole+'_'\
                     +self.kcmpnm                        

        # Don't read waveform
        if not datflag: 
            fid.close()
            # All done
            return

        # Read waveform
        fid.seek(632,0);
        if npts is None or npts < 0 or npts > self.npts:
            npts = self.npts
        else:
            self.npts = int(npts)            
        if self.npts > 0:
            self.depvar = np.fromfile(fid,ftype,self.npts)
        fid.close()

        # Re-assign min/max amplitudes and end time
        self.depmin  = self.depvar.min()
        self.depmax  = self.depvar.max()
        self.e       = self.b + float(self.npts - 1) * self.delta
        
        # All done

        
    def write(self,FILE):
        '''
        Write sac file
        Args:
           * FILE: output sac file name
        '''

        # Check that we are in the time domain
        assert not self.spec, "Can only save seismograms in the time-domain"
        
        # convert to list
        if type(self.depvar)==list:
            self.depvar = np.array(self.depvar)
        
        # Dummy variables
        dumi = np.array(-12345    ,dtype='int32')
        dumf = np.array(-12345.0  ,dtype='float32')
        dumc = np.array('-12345  ',dtype='c')
        
        # Re-assign min/max amplitudes and end time
        self.depmin  = self.depvar.min()
        self.depmax  = self.depvar.max()
        self.e = self.b + float(self.npts - 1) * self.delta

        # Write file
        fid = open(FILE,'wb')
        np.array(self.delta,dtype='float32').tofile(fid)
        np.array(self.depmin,dtype='float32').tofile(fid)
        np.array(self.depmax,dtype='float32').tofile(fid)
        np.array(self.scale,dtype='float32').tofile(fid)
        np.array(self.odelta,dtype='float32').tofile(fid)
        np.array(self.b,dtype='float32').tofile(fid)
        np.array(self.e,dtype='float32').tofile(fid)
        np.array(self.o,dtype='float32').tofile(fid)
        np.array(self.a,dtype='float32').tofile(fid)
        np.array(self.internal1,dtype='float32').tofile(fid)
        np.array(self.t,dtype='float32').tofile(fid)
        np.array(self.f,dtype='float32').tofile(fid)
        np.array(self.resp,dtype='float32').tofile(fid)
        np.array(self.stla,dtype='float32').tofile(fid)
        np.array(self.stlo,dtype='float32').tofile(fid)
        np.array(self.stel,dtype='float32').tofile(fid)
        np.array(self.stdp,dtype='float32').tofile(fid)
        np.array(self.evla,dtype='float32').tofile(fid)
        np.array(self.evlo,dtype='float32').tofile(fid)
        np.array(self.evel,dtype='float32').tofile(fid)
        np.array(self.evdp,dtype='float32').tofile(fid)
        np.array(self.mag,dtype='float32').tofile(fid)
        np.array(self.user,dtype='float32').tofile(fid)
        np.array(self.dist,dtype='float32').tofile(fid)
        np.array(self.az,dtype='float32').tofile(fid)
        np.array(self.baz,dtype='float32').tofile(fid)
        np.array(self.gcarc,dtype='float32').tofile(fid)
        np.array(self.internal2,dtype='float32').tofile(fid)
        np.array(self.internal3,dtype='float32').tofile(fid)
        np.array(self.depmen,dtype='float32').tofile(fid)
        np.array(self.cmpaz,dtype='float32').tofile(fid)
        np.array(self.cmpinc,dtype='float32').tofile(fid)
        np.array(self.xminimum,dtype='float32').tofile(fid)
        np.array(self.xmaximum,dtype='float32').tofile(fid)
        np.array(self.yminimum,dtype='float32').tofile(fid)
        np.array(self.ymaximum,dtype='float32').tofile(fid)  
        for i in range(7):
            dumf.tofile(fid)
        np.array(self.nzyear,dtype='int32').tofile(fid)  
        np.array(self.nzjday,dtype='int32').tofile(fid)  
        np.array(self.nzhour,dtype='int32').tofile(fid)
        np.array(self.nzmin,dtype='int32').tofile(fid)  
        np.array(self.nzsec,dtype='int32').tofile(fid)  
        np.array(self.nzmsec,dtype='int32').tofile(fid)  
        np.array(self.nvhdr,dtype='int32').tofile(fid)  
        np.array(self.norid,dtype='int32').tofile(fid)  
        np.array(self.nevid,dtype='int32').tofile(fid)
        np.array(self.npts,dtype='int32').tofile(fid) 
        np.array(self.internal4,dtype='int32').tofile(fid)  
        np.array(self.nwfid,dtype='int32').tofile(fid)
        np.array(self.nxsize,dtype='int32').tofile(fid)
        np.array(self.nysize,dtype='int32').tofile(fid)
        dumi.tofile(fid)
        np.array(self.iftype,dtype='int32').tofile(fid)
        np.array(self.idep,dtype='int32').tofile(fid)
        np.array(self.iztype,dtype='int32').tofile(fid)
        dumi.tofile(fid)
        np.array(self.iinst,dtype='int32').tofile(fid)
        np.array(self.istreg,dtype='int32').tofile(fid)
        np.array(self.ievreg,dtype='int32').tofile(fid)
        np.array(self.ievtyp,dtype='int32').tofile(fid)
        np.array(self.iqual,dtype='int32').tofile(fid)
        np.array(self.isynth,dtype='int32').tofile(fid)
        np.array(self.imagtyp,dtype='int32').tofile(fid)
        np.array(self.imagsrc,dtype='int32').tofile(fid)
        for i in range(8):
            dumi.tofile(fid)
        np.array(self.leven,dtype='int32').tofile(fid)
        np.array(self.lpspol,dtype='int32').tofile(fid)
        np.array(self.lovrok,dtype='int32').tofile(fid)
        np.array(self.lcalda,dtype='int32').tofile(fid)
        dumi.tofile(fid)
        pack_c(self.kstnm,8).tofile(fid)  
        pack_c(self.kevnm,16).tofile(fid)  
        pack_c(self.khole,8).tofile(fid)
        pack_c(self.ko,8).tofile(fid)
        pack_c(self.ka,8).tofile(fid)
        for i in range(10):
            pack_c(self.kt[i],8).tofile(fid)
        pack_c(self.kf,8).tofile(fid)
        for i in range(3):
            pack_c(self.kuser[i],8).tofile(fid)
        pack_c(self.kcmpnm,8).tofile(fid)
        pack_c(self.knetwk,8).tofile(fid)
        pack_c(self.kdatrd,8).tofile(fid)
        pack_c(self.kinst,8).tofile(fid)

        # Write data
        np.array(self.depvar,dtype='float32').tofile(fid)
        fid.close()
                
        # All done

        
    def rsac(self,FILE,npts=None,datflag=True):
        '''
        Clone of self.read()
        '''
        sys.stderr.write('FutureWarning: sac.rsac will be replaced by sac.read in the future\n')
        self.read(FILE,npts=None,datflag=True)

        # All done

        
    def wsac(self,FILE):
        '''
        Clone of self.write
        '''
        sys.stderr.write('FutureWarning: sac.wsac will be replaced by sac.write in the future\n')
        self.write(FILE)

        # All done

        
    def getnzdatetime(self):
        '''
        Get the reference datetime
        '''
        # Reference datetime
        nzjday = timedelta(int(self.nzjday)-1)
        nzusec = int(self.nzmsec*1e3)
        nztime = datetime(self.nzyear,1,1,self.nzhour,self.nzmin,self.nzsec,nzusec)+nzjday

        # All done
        return nztime


    def setotime(self,otime):
        '''
        Set o 
        Arg:
            * otime: datetime instance
        '''
        # Get nzdatetime
        nztime = self.getnzdatetime()
                
        # Time difference is o
        self.o  = np.float32((otime-nztime).total_seconds())

        # All done

        
    def setarrivaltimes(self,phase_dict):
        '''
        Set t and kt 
        Arg:
          * phase_dict: phase pick dictionary {name: arrival_datetime)                
        '''

        # Get nzdatetime
        nztime = self.getnzdatetime()

        # Loop over phase names and arrival times 
        i = 0
        for pname, ptime in phase_dict.items():

            # Phase name
            assert len(pname)<8, 'phase name %s is too long'%(pname)
            self.kt[i] = pname

            # Arrival time                        
            self.t[i]  = np.float32((ptime-nztime).total_seconds())
            i += 1
                        
        # All done


    def __add__(self, other):
        '''
        Addition operation.         
        other can be:
          - sacpy.sac object
          - list or ndarray
          - real number (float or int)
        '''        

        # Check if the operation can be done
        accepted=(self.__class__,int,float,list,np.ndarray)
        assert isinstance(other,accepted), 'Unsuported type'
        
        # Copy current object
        res  = self.copy()
        flag = False

        # Adding two sac files
        if isinstance(other,self.__class__):
            assert self.npts  == other.npts,  'Header field mismatch: npts'
            assert self.delta == other.delta, 'Header field mismatch: delta'
            assert self.b     == other.b,     'Header field mismatch: b'
            assert self.e     == other.e,     'Header field mismatch: e'          
            res.depvar += other.depvar
            flag = True

        # Adding array or list
        if isinstance(other,(list,np.ndarray)):
            assert len(other)==self.npts, 'Header field mismatch: npts'
            res.depvar += other
            flag = True

        # Adding real number
        if isinstance(other,(int,float)):
            res.depvar += other
            flag = True

        # Re-assign min and max amplitudes
        res.depmin  = res.depvar.min()
        res.depmax  = res.depvar.max()
        
        # Check that operation was done
        assert flag, 'Operation could not be completed'
        
        # All done
        return res

    def __sub__(self, other):
        '''
        Substraction operation.         
        other can be:
          - sacpy.sac object
          - list or ndarray
          - real number (float or int)
        '''        

        # Check if the operation can be done
        accepted=(self.__class__,int,float,list,np.ndarray)
        assert isinstance(other,accepted), 'Unsuported type'
        
        # Copy current object
        res  = self.copy()
        flag = False

        # Adding two sac files
        if isinstance(other,self.__class__):
            assert self.npts  == other.npts,  'Header field mismatch: npts'
            assert self.delta == other.delta, 'Header field mismatch: delta'
            assert self.b     == other.b,     'Header field mismatch: b'
            assert self.e     == other.e,     'Header field mismatch: e'          
            res.depvar -= other.depvar
            flag = True

        # Adding array or list
        if isinstance(other,(list,np.ndarray)):
            assert len(other)==self.npts, 'Header field mismatch: npts'
            res.depvar -= other
            flag = True

        # Adding real number
        if isinstance(other,(int,float)):
            res.depvar -= other
            flag = True

        # Re-assign min and max amplitudes
        res.depmin  = res.depvar.min()
        res.depmax  = res.depvar.max()
        
        # Check that operation was done
        assert flag, 'Operation could not be completed'
        
        # All done
        return res    

    def __mul__(self, other):
        '''
        Multiplication operation.         
        other can be:
          - sacpy.sac object
          - list or ndarray
          - real number (float or int)
        '''        

        # Check if the operation can be done
        accepted=(self.__class__,int,float,list,np.ndarray)
        assert isinstance(other,accepted), 'Unsuported type'
        
        # Copy current object
        res  = self.copy()
        flag = False

        # Adding two sac files
        if isinstance(other,self.__class__):
            assert self.npts  == other.npts,  'Header field mismatch: npts'
            assert self.delta == other.delta, 'Header field mismatch: delta'
            assert self.b     == other.b,     'Header field mismatch: b'
            assert self.e     == other.e,     'Header field mismatch: e'          
            res.depvar *= other.depvar
            flag = True

        # Adding array or list
        if isinstance(other,(list,np.ndarray)):
            assert len(other)==self.npts, 'Header field mismatch: npts'
            res.depvar *= other
            flag = True

        # Adding real number
        if isinstance(other,(int,float)):
            res.depvar *= other
            flag = True

        # Re-assign min and max amplitudes
        res.depmin  = res.depvar.min()
        res.depmax  = res.depvar.max()
        
        # Check that operation was done
        assert flag, 'Operation could not be completed'
        
        # All done
        return res

    
    def integrate(self):
        '''
        Performs integration using the traperoidal rule
        '''

        # Integration
        w  = self.depvar.copy()
        wi = self.depvar.cumsum()
        wi = (2*wi[1:]-(w[0]+w[1:]))*self.delta/2.
        self.depvar = wi.copy()

        # Re-assign b, e, npts, min/max amplitudes
        self.b += self.delta/2.
        self.npts -= 1
        self.e = self.b + float(self.npts - 1) * self.delta
        self.depmin  = self.depvar.min()
        self.depmax  = self.depvar.max()
        
        # All done
        return


    def isempty(self):
        '''
        Check if important attributes are there
        '''    
        if (self.npts < 0) or (self.delta < 0) or (not self.depvar.size):
            return True

        # All done
        return False

        
    def interpolate(self, delta_new):
        '''
        Interpolates data to a new sampling rate (sinc interpolation)
        Args:
            * delta_new: New sampling rate
        '''

        # Check that headers are correct
        assert not self.isempty(), 'Some sac attributes are missing (e.g., npts, delta, depvar)'
        
        # time vectors
        time_old = np.arange(self.npts,dtype='float32')*self.delta # Time vector before interpolation
        npts_new = int(np.floor((self.npts-1)*self.delta/delta_new))
        time_new = np.arange(npts_new,dtype='float32')*delta_new   # Time vector after interpolation

        # Sinc interpolation
        depvar_new = np.zeros((npts_new,),dtype='float32')
        for i in range(npts_new):
            depvar_new[i] = np.dot(self.depvar,np.sinc((time_new[i]-time_old)/self.delta))        
        self.depvar = depvar_new.copy()
        self.npts   = npts_new
        self.delta  = delta_new

        # All done
        return
        

    def decimate(self, dec_fac):
        '''
        Decimates data
        Args:
            * dec_fac: decimation factor
        '''

        #import decimate as decim
        from . import decimate as decim

        # Check that headers are correct
        assert not self.isempty(), 'Some sac attributes are missing (e.g., npts, delta, depvar)'

        # Check decimation factor
        assert dec_fac in decim.FACS, 'Incorrect decimation factor'

        # Init filters
        fir = {2: decim.FIRfilter(decim.FIRDEC2),
               3: decim.FIRfilter(decim.FIRDEC3),
               4: decim.FIRfilter(decim.FIRDEC4),
               5: decim.FIRfilter(decim.FIRDEC5)}

        # Filter cascade
        fir_cascade = decim.FACS[dec_fac]
        for c in fir_cascade:
            assert c>=1 and c<=5, 'Incorrect decimation factor (%d)'%(c)
            if c==1:
                continue
            self.depvar = decim.decimate(self.depvar,fir[c],c)
            self.delta *= np.float32(c)
        self.npts = len(self.depvar)


    def filter(self, freq, order=4, btype='lowpass'):
        '''
        Bandpass filter the data using a butterworth filter
        Args:
            * freq: A scalar or length-2 sequence giving the critical frequencies (in Hz)
            * order:  Order of the filter.
            * btype: {'lowpass', 'highpass', 'bandpass', 'bandstop'}, optional
              (default is 'lowpass')
        '''
        
        # Check that headers are correct
        assert not self.isempty(), 'Some sac attributes are missing (e.g., npts, delta, depvar)'

        # Filter design
        if type(freq) is list:
            freq = np.array(freq)
        Wn = freq * 2. * self.delta # Normalizing frequencies
        sos = signal.butter(order, Wn, btype, output='sos')
        
        # Filter waveform
        depvar = signal.sosfilt(sos, self.depvar)
        self.depvar = depvar.astype('float32')

        # All done
        return

    def pad(self,tmin = None, tmax = None):
        '''
        Padding data with zeros
        if tmin < self.b - self.o (beginning), adding zeros at the beginning
        if tmax > self.e - self.o (end), adding zeros at the end
        '''
        # Check origin time is assigned
        assert self.o != -12345., 'Origin time must be assigned'
        
        # Get trace beginning and end
        self.e = self.b + float(self.npts - 1) * self.delta
        tb = self.b - self.o
        te = self.e - self.o

        # Set the pad width
        nbeg = 0
        nend = 0
        if tmin is not None and tmin < tb:
            nbeg = int(np.ceil((tb-tmin)/self.delta))
        if tmax is not None and tmax > te:
            nend = int(np.ceil((tmax-te)/self.delta))

        # Zero padding
        gout = np.pad(self.depvar,((nbeg,nend),),mode="constant")
        self.npts = len(gout)
        self.b = self.b - nbeg * self.delta
        self.e = self.e + nend * self.delta
        self.depvar = gout.copy()

        # All done
        return

    def fft(self):
        '''
        Compute fourier transform and return the seismogram spectrum
        Output: Seismogram spectrum in the frequency domain (type: seismogram)        
        '''
        spectrum = self.copy()
        spectrum.spec = True
        spectrum.depvar = np.fft.rfft(self.depvar)        
        
        # All done
        return spectrum

    def ifft(self):
        '''
        Compute the inverse fourrier transform and returns the seismogram spectrum
        Output: Seismogram in the time domain (type: seismogram)
        '''
        seis = self.copy()
        seis.spec = False
        seis.depvar=None
        seis.depvar = np.fft.irfft(self.depvar) 
        
        # All done
        return seis

    def freq(self):
        '''
        Returns the frequency vector of the current data
        '''
        freq = np.fft.rfftfreq(self.npts,d=self.delta)
        # All done        
        return freq

    def evalresp(self,PZ):
        '''
        Return frequency response
        Args:
            * PZ: dictionary including 'poles', 'zeros' and 'Const'
        '''
        s = 2.j*np.pi*self.freq()
        resp = np.ones(s.shape,dtype=np.complex128)*PZ['Const']
        for z in PZ['zeros']: resp *= s-z
        for p in PZ['poles']: resp /= s-p
        # All done
        return resp

    def convresp(self,PZ):
        '''
        Convolve with instrument response
        Args:
            * PZ: dictionary including 'poles', 'zeros' and 'Const'        
        '''
        npts = self.npts
        # Trivial dtrend
        self.depvar -= self.depvar[0]+np.arange(npts)*(self.depvar[-1]-self.depvar[0])/(npts-1)
        # Zero padding
        self.pad(tmax=2*self.e-self.b)
        # Evaluate the instrument response from Poles and Zeros
        resp = self.evalresp(PZ)
        # Convolve with the instrument response
        self.depvar = np.fft.irfft(resp*np.fft.rfft(self.depvar))[:npts]
        self.npts = npts
        self.e    = self.b + float(self.npts)*self.delta
        self.depmin = self.depvar.min()
        self.depmax = self.depvar.max()        
        # All done
        return

    def time(self):
        '''
        Returns the time vector of the current data relative to nztime
        '''
        time = np.arange(self.npts)*self.delta + self.b
        return time

    def plot(self,ptype=None,xlog=False,ylog=False,**kwargs):
        '''
        Plot the seismogram or spectrum
        Args: All arguments are optional
            - ptype: plot type can be None, 'amp' for absolute amplitude, 'pha' for the phase, 
                     'real' for the real part or 'imag' for the imaginary part.
            - xlog: if True use a log scale on the x axis
            - ylog: if True use a log scale on the y axis
            - *kwargs* can be used to set line properties in pyplot commands (see help of plt.plot)
        examples:
                s.plot(color='r') or s.plot(color='red') will plot the seismogram with a red line
        Use plt.show() to show the corresponding figure
        '''

        # Import the matplotlib module
        import matplotlib.pyplot as plt

        # Check attributes        
        assert not self.isempty(),'Some attributes are missing (e.g., npts, delta, depvar)'

        # Time or frequency vector
        if self.spec is False: # Time vector
            x = self.time()
            xlabel = 'Time, sec'
        else: # Frequency vector
            x = self.freq()
            xlabel = 'Freq., Hz'  
        # What do we want to plot?
        ylabel = 'Amplitude'        
        if ptype is None and not self.spec: # Standard seismogram plot
            y = self.depvar
        elif (ptype is None and self.spec) or ptype == 'amp':  # Amplitude
            y = np.abs(self.depvar)
        elif ptype == 'pha':     # Phase
            y = np.angle(self.depvar)
            ylabel = 'Phase'            
        elif ptype == 'real': # Real part
            y = np.real(self.depvar)
            ylabel = 'Real part amplitude'
        elif ptype == 'imag':
            y = np.imag(self.depvar)
            ylabel = 'Imag. part amplitude'            
        else:
            print('Error: ptype should be None, amp, pha, real or imag')
            return 1        

        # Do we use log scale?
        plotf = plt.plot  # Default: no log scale
        if xlog and ylog: # loglog scale
            plotf=plt.loglog
        elif xlog:        # x log scale
            plotf=plt.semilogx
        elif ylog:        # y log scale
            plotf=plt.semilogy
        
        # Plot seismogram
        lines = plotf(x,y,**kwargs)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
        # All done
        return lines    
        
    def copy(self):
        '''
        Returns a copy of the sac object
        '''
        # All done
        return deepcopy(self)                

def zero_pad_start(t,sac,t0):
    tmin = t[0]
    dt   = sac.delta
    tpad = np.arange(tmin,t0-dt,-dt)
    if tpad[-1]>t0:
        tpad = np.append(tpad,tpad[-1]-dt)
    tpad = tpad[1:]
    tpad = tpad[::-1]
    tout = np.append(tpad,t)
    gout = np.append(0.0*tpad,sac.depvar)
    # all done
    return tout,gout

