#!/usr/bin/env python

# FestivalDS - Text to speech tango device server using festival

# Copyright 2013-2019 by CELLS / ALBA Synchrotron, Cerdanyola del Valles, Spain

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import PyTango
import sys
import os
import time
import threading


# managed by bumpversion do not edit manually
__version = '1.0.0'


#==================================================================
#   FestivalDS Class Description:
#
#
#=================================================================

def trace(msg):
  print '%s: %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), msg)

def os_cmd(cmd,term=True):
    trace( 'os:> %s'%cmd)
    if term and not cmd.strip().endswith('&'): cmd+=' &'
    os.system(cmd)

def Sequence(repeat, beep_cmd, festival_cmd):
    trace( 'In Sequence Thread ...')
    ev = threading.Event()
    for i in xrange(repeat):
        os_cmd(beep_cmd, term=False)
        ev.wait(0.5)
    os_cmd(festival_cmd, term=False)

class FestivalDS(PyTango.Device_4Impl):

#--------- Add you global variables here --------------------------

#------------------------------------------------------------------
#	Device constructor
#------------------------------------------------------------------
    def __init__(self,cl, name):
        PyTango.Device_4Impl.__init__(self,cl,name)
        FestivalDS.init_device(self)

#------------------------------------------------------------------
#	Device destructor
#------------------------------------------------------------------
    def delete_device(self):
        trace("[Device delete_device method] for device"+self.get_name())
        if self.thread and self.thread.is_alive(): self.thread.join(10.)


#------------------------------------------------------------------
#	Device initialization
#------------------------------------------------------------------
    def init_device(self):
        trace("In "+ self.get_name()+ "::init_device()")
        self.thread = None
        self.set_state(PyTango.DevState.ON)
        self.get_device_properties(self.get_device_class())
        

#------------------------------------------------------------------
#	Always excuted hook method
#------------------------------------------------------------------
    def always_executed_hook(self):
        trace("In "+ self.get_name()+ "::always_excuted_hook()")

#==================================================================
#
#	FestivalDS read/write attribute methods
#
#==================================================================
#------------------------------------------------------------------
#	Read Attribute Hardware
#------------------------------------------------------------------
    def read_attr_hardware(self,data):
        trace("In "+ self.get_name()+ "::read_attr_hardware()")

    ### Commands ###
    def Play(self,text):
        trace( 'In %s.Play(%s)'%(self.get_name(),text))
        out = self.Cmd_Festival % text
        os_cmd(out)

    def Beep(self):
        trace( 'In %s.Beep()'%self.get_name())
        if not os.path.isfile(self.Beep_Path):
            raise Exception('Wav file not set')
        os_cmd(self.Cmd_Play % self.Beep_Path)

    def PopUp(self,argin):
        if len(argin) == 1:
            title, text, period = argin[0], '', 0
        else:
            title = argin[0]
            text = argin[1] if len(argin)>1 else ''
            period = int(argin[2]) if len(argin)>2 else 0
        command = self.Cmd_PopUp % (self.Display, title, 1000*(period or 60))
        if (self.Icon is not None) and (os.path.isfile(self.Icon)):
            command += " -i %s" % self.Icon
        if text: command+=' "%s"'%text.replace('<br/>','\n').replace('<p>','\n').replace('</p>','\n').replace('<br>','\n')
        os_cmd(command)
        return title #command
     
    def Play_Sequence(self, text):
        trace( 'In %s.Play_Sequence(%s)'%(self.get_name(), text))
        beep = self.Cmd_Play % self.Beep_Path
        speech = self.Cmd_Festival % text
        self.thread = threading.Thread(
            target=Sequence, args=(self.Default_Repeat_Times, beep, speech))
        self.thread.start()        



#==================================================================
#
#	FestivalDS command methods
#
#==================================================================

#==================================================================
#
#	FestivalDSClass class definition
#
#==================================================================
class FestivalDSClass(PyTango.DeviceClass):

	#	Class Properties
    class_property_list = {
        }


    #	Device Properties
    device_property_list = {
        'Beep_Path':
            [PyTango.DevString,
            "",
            None ],
        'Default_Repeat_Times':
            [PyTango.DevShort,
            "",
            1 ],
        'Display':
            [PyTango.DevString,
            "Display to show popup mesages",
            [':0'] ],
        'Icon':
            [PyTango.DevString,
            "Icon for notifications",
            None ],
        'Cmd_Festival':
            [PyTango.DevString,
            "System command to play festival speech",
            "echo \"%s\" | padsp festival --tts" ],
        'Cmd_Play':
            [PyTango.DevString,
            "System command to play a sound",
            "padsp aplay %s" ],
        'Cmd_PopUp':
            [PyTango.DevString,
            "System command to show pop ups",
            "DISPLAY=%s sudo -u operator notify-send \"%s\" -u critical -t %d" ],
        }
		



	#	Command definitions
    cmd_list = {    
    'Play' : 
            [[PyTango.DevString, "Play a given Text; requires Festival library"], 
            [PyTango.DevVoid, ""]], 
    'Beep' : 
            [[PyTango.DevVoid, "Force a Beep Sound; requires Festival library "], 
            [PyTango.DevVoid, ""]], 
    'Play_Sequence' : 
            [[PyTango.DevString, "Force a Beep Sound with a given speech;  requires Festival library"], 
            [PyTango.DevVoid, ""]], 
    'PopUp' : 
            [[PyTango.DevVarStringArray, "PopUp(title,text,[seconds]); Shows a system pop-up; requires libnotify-tools package"], 
            [PyTango.DevString, ""]],             
        }


	#	Attribute definitions
    attr_list = {
        }


#------------------------------------------------------------------
#	FestivalDSClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name);
        print "In FestivalDSClass  constructor"

#==================================================================
#
#	FestivalDS class main method
#
#==================================================================
def main():
    try:
        py = PyTango.Util(sys.argv)
        py.add_TgClass(FestivalDSClass,FestivalDS,'FestivalDS')

        U = PyTango.Util.instance()
        U.server_init()
        U.server_run()

    except PyTango.DevFailed,e:
        print '-------> Received a DevFailed exception:',e
    except Exception,e:
        print '-------> An unforeseen exception occured....',e


if __name__ == '__main__':
    main()
