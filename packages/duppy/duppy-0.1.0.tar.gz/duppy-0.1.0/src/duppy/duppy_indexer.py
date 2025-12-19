#!/usr/bin/python
''' Here for organization, not decoupling.

    TODO: do a proper 'output or not' thing - the newline printing assumes sameline() which makes no sense when you hand along nothing
'''

import time,os,stat,sys

class Indexer(object):
    """ Some useful data collection around os.walk().
        Also the (quite mininal) base class of the things below.

        TODO: allow ignoring dirs by absolute path
    """
    
    def __init__(self, ignore_dirnames=(), verbose=False, print_callback=None, same_device=False):
        if print_callback==None:
            def do_nothing(x):
                pass
            self.print_callback = do_nothing
        else:
            self.print_callback = print_callback
        
        self.inodes            = {}
        self.minlen            = 1
        self.maxlen            = None
        self.persize           = {}
        self.startdevice       = None
        self.same_device       = same_device
        
        self.follow_sym        = False
        self.ignore_dirnames   = ignore_dirnames
        self.verbose           = verbose
        self.nfiles            = 0
        
        self.last_feedback     = time.time()
        #self.feedback_interval = 0.33 # seconds
        self.feedback_interval = 0.008 # seconds
        
        
    def add(self, fn, recursive=True):
        """ imitation of os.walk, except that it
            takes some stat information immediately (primarily the size),
            is smarter about symlinks and hardlinks (because we need that to be safe),
            can do filtering at each step (TODO: make that configurable)
        """
        fn = os.path.abspath(fn)
        if not os.access(fn,os.R_OK):
            self.print_callback('')
            self.print_callback('  could not access %r\n'%fn)

        else:
            mode, inode, device, numhardlinks, uid,gid, size, atime, mtime, ctime = os.lstat(fn)

            # ignore everything not a directory or regular file
            isdir = stat.S_ISDIR(mode)
            isreg = stat.S_ISREG(mode)
            islnk = stat.S_ISLNK(mode)
            
            if  not isdir  and  not isreg  and  not islnk:
                if self.verbose:
                    self.print_callback('')
                    self.print_callback('  ignoring special file (%s)'%fn)
                    sys.stderr.write('\n')
                    return


            # Argument with self: if the original was a symlink, the strict interpretation is to not follow it 
            #   and record the device it is on (may be more correct around multiple arguments)
            # though the more practical is often "start at the device that poitns to" (in which case this would go after the S_ISLNK block)
            if self.same_device:
                if self.startdevice == None: # first add
                    self.startdevice = device
                else: # not the first add
                    if self.startdevice != device:
                        print("Not crossing devices onto %r"%fn)
                        return

            if islnk:
                if not self.follow_sym:
                    if self.verbose >= 2:
                        self.print_callback('')
                        self.print_callback('  ignoring symlink   %s'%fn) #Use self.print_callback for the line clearning
                        sys.stderr.write('\n')               # but do skip to the next line
                    return
                else:
                    if self.verbose:
                        self.print_callback('')
                        self.print_callback('  following symlink %s\n'%fn)
                        #sys.stderr.write('\n')               # but do skip to the next line
                    #basic version, which follows symlinks
                    mode, inode, device, numhardlinks, uid,gid, size, atime, mtime, ctime = os.stat(fn) 




            if self.verbose:
                now = time.time()
                if now - self.last_feedback > self.feedback_interval:
                    self.last_feedback = now
                    self.print_callback( '%6d included,  scanning for files... %s'%(self.nfiles,fn))

            if isdir:
                if (device,inode) in self.inodes: #although I don't think directory hardlinks are always allowed
                    self.inodes[(device,inode)].append(fn) # that's not universal, so I'm being safe.
                    if self.verbose:
                        self.print_callback('')
                        self.print_callback('  ignoring duplicate hardlinks to directory (from %s)'%fn)
                        sys.stderr.write('\n')
                        
                else:
                    #if self.verbose: sys.stderr.write("[dir: %s]\n"%fn)
                    self.inodes[(device,inode)] = [fn]                    
                    if recursive:
                        for rfn in sorted(os.listdir(fn)): #more or less imitating os.walk()
                            frfn=os.path.join(fn,rfn)
                            if rfn in self.ignore_dirnames:
                                if self.verbose>=2:
                                    self.print_callback('')
                                    self.print_callback('  ignoring directory  %r by basename'%frfn)
                                    sys.stderr.write('\n')
                                continue
                            else:
                                self.add(frfn)
            elif isreg:
                if size<self.minlen:
                    if self.verbose >= 3  and  size == 0:
                        self.print_callback('')
                        self.print_callback('  ignoring empty file %r'%fn)
                        sys.stderr.write('\n')                        
                    elif self.verbose >= 3:  #  and  self.minlen < 100000:  #people that hand large values to -s may not want to see thousands of 'ignoring small file' messages              
                        self.print_callback('')
                        self.print_callback('  ignoring small file %r\n'%fn)
                        sys.stderr.write('\n')                        
                    sys.stderr.flush()
                    return
                if self.maxlen!=None:
                    #print size,self.maxlen
                    if size > self.maxlen:
                        if self.verbose >=2:
                            self.print_callback('')
                            self.print_callback('  ignoring large file %r\n'%fn)
                        return
                
                if (device,inode) in self.inodes:
                    self.inodes[(device,inode)].append(fn)
                    if self.verbose>=1:
                        self.print_callback('')
                        self.print_callback('  ignoring duplicate hardlinks to file (from %s)'%fn)
                        sys.stderr.write('\n')
                else:
                    self.inodes[(device,inode)] = [fn]                    
                    #self.inodes.add( (device,inode) )
                    self.nfiles+=1
                    if size not in self.persize:
                        self.persize[size]=[]
                    self.persize[size].append(fn)
            #implied: ignoring things not directories or regular files


            
