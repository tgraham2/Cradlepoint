#!/usr/bin/env python
from cssh_lib import qp, csshpw
#
class cpssh(object):
    #
    def __init__ (self,myuid,mypw,myip):
        import paramiko
        import time
        print 'starting init cssh'
        self.ip=myip
        self.username=myuid
        self.password=mypw
        self.connected=False
        paramiko.util.log_to_file("paramiko-" + \
                                  time.strftime("%Y-%m-%d-%H%M%S.log"))
        self.cssh_client()
        session=self.cssh_remote_connection()

        if session == False:
          print 'CPSSH: remote session failed'
        else:
          print 'starting shell'
          self.rshell = self.cssh_shell()
          self.connected = True
        print 'end init'
          
    def cssh_client(self):
        ''' create an ssh client '''
        import paramiko
        # Create instance of SSHClient object
        self.rclient = paramiko.SSHClient()

        # Automatically add untrusted hosts
        self.rclient.set_missing_host_key_policy(
                     paramiko.AutoAddPolicy())
  
    
    def cssh_remote_connection(self):
        ''' establish ssh connection for (user,pswd) '''
        # initiate SSH connection
        try:
          self.rc=self.rclient.connect( self.ip, username=self.username, \
          password=self.password, look_for_keys=False, allow_agent=False)

        except:
          print "SSH connection failed to %s" % self.ip
          return False
        else:
          print "SSH connection established to %s" % self.ip
        return True
			
    def cssh_shell (self):
        ''' start  shell for interactive CLI '''
        import time
        # Use invoke_shell to establish an 'interactive session'
        self.rs = self.rclient.invoke_shell()
        time.sleep(1)

        # Strip the initial router prompt
        output = self.rs .recv(1000)

        # See what we have
        outlines=output.split('\n')
        x=outlines[0]
        self.routerid=x[x.find("@")+1:x.find(":")]
        #
        print 'routerid:',self.routerid
      
    def send_serial(self,uid,pwd):
        # uid, pwd for local login to router
        import time
        mywait = .5 ; mybuff = 3072
        # use ssh to send command
        self.rs.send('serial --force\n')
        time.sleep(mywait*6)
        recv = self.rs.recv(mybuff)
        recvlines=recv.split()
        print recvlines
        # display banner and get username prompt:
        self.rs.send('\n')
        time.sleep(mywait*6)
        recv = self.rs.recv(mybuff)
        recvlines=recv.split()
        print "BAN:",recvlines
        if recvlines == []:
            # disconnect rev. telnet
            self.rs.send('\0036x\n')
            self.rs.send('disc')
            self.rs.send('\n')
            time.sleep(mywait)
            recv = self.rs.recv(mybuff)
            self.rs.send('\n')
            time.sleep(mywait)
            recv = self.rs.recv(mybuff)
        foundusername = False
        norouter = False
        for i in range(1,10):
          recvlines=recv.split()
          if [s for s in recvlines if 'name:' in s] <> []:
            foundusername = True
            break
          elif [s for s in recvlines if '@CBA' in s] <> []:
            # no router
            print "No router"
            self.rs.send('\0021')
            time.sleep(mywait)
            self.rs.send('exit\n')
            return("no router")
          else: # no login prompt
            rid = recvlines[-1].strip('>')
            print 'No Login:',rid
            break
          self.rs.send('\n')
          time.sleep(mywait)
        print '1:',recvlines
        #
        if foundusername :
          # login to router
          self.rs.send(uid+'\n')
          time.sleep(mywait*2)
          recv = self.rs.recv(mybuff)
          recvlines=recv.split()
          print '2:',
          for i,s in enumerate(recvlines):
              print "ENUM:",i,s
              
          if '>' in recvlines:
              self.rid = recvlines[0][:-1]
              print 'RID2:',self.rid
          if 'Username: ' in recvlines[-1]:
            self.rs.send('netops\n')
            time.sleep(mywait*2)
            recv = self.rs.recv(mybuff)
            self.rs.send(csshpw('netops')+'\n')
            time.sleep(mywait*2)
          else:
            self.rs.send(pwd+'\n')
            time.sleep(mywait*5)
            recv = self.rs.recv(mybuff)
            print 'PWD:', recv
          self.rs.send('\n')
          recv = self.rs.recv(mybuff)
          recvlines=recv.split()
          print '3:',recvlines
        else:          
          self.rs.send('\n')
          time.sleep(mywait)
          recv = self.rs.recv(mybuff)
          recvlines=recv.split()
          print 'U:',recvlines
        rid = recvlines[-1].strip('>')

        city = rid[0:rid.find('_')]
        office = rid[rid.find('_')+1:]
        office = office[0:office.find('_')]
        office=('00000'+office)[len(office):]
        print city,office
        self.rs.send('exit\n')
        time.sleep(mywait)
        self.rs.send('\0021')
        time.sleep(mywait)
        self.rs.send('exit\n')
        return(rid)

    def close(self):
        ''' close the session '''
        self.rs.close()
        self.connected=False

if __name__ == '__main__':
    x = cpssh('nimda',csshpw('nimda'),'166.157.33.185')
    r = x.send_serial('tgraham',csshpw('tgraham'))
    print "result:",r

