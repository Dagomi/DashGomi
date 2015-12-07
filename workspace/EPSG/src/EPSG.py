'''
Created on Dec 3, 2015
@author: Dagomi
'''
#!/usr/bin/env python
import os
import gi
import psutil
#http://www.bok.net/dash/tears_of_steel/cleartext/stream.mpd
#http://localhost/dash/trik_audio_video/stream.mpd
'''
Need ad the seeking line bar
'''


gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, Gtk, GdkX11 , GstVideo

Gst.init(None)
GObject.threads_init()


class GTK_Main(object):
    
    def __init__(self):
        
        #UI
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("MPEG-DASH Player")
        window.set_default_size(430 , 250)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        
        vbox = Gtk.VBox()
        window.add(vbox)
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 0)
        
        sliders = Gtk.HBox()
        vbox.pack_end(sliders, False, False, 0)
        
        table = Gtk.Table(6, 4, False)
        table.set_col_spacings(25)
        sliders.add(table)
    
        #Labels
        #Sliders
        label_top_left = Gtk.Label(label="Buffer Ocupancy" )
        label_top_right = Gtk.Label(label="Battery Level")
        label_bottom_left = Gtk.Label(label="CPU Load")
        label_bottom_right = Gtk.Label(label="Available Bandwidth")
        
        #Simulations
        self.label_Simulation = Gtk.Label(label="Simulation")
        self.label_Buffer_Sim = Gtk.Label(label="Buffer is 0")
        self.label_Battery_Sim = Gtk.Label(label="Battery is 0")
        self.label_CPU_Sim = Gtk.Label(label="CPU is 0")
        self.label_BW_Sim = Gtk.Label(label="BW is 0")
        
        #Enviorment
        self.label_Real = Gtk.Label(label="Enviorment")
        self.label_Buffer_Real = Gtk.Label(label="Buffer is 0")
        self.label_Battery_Real = Gtk.Label(label="Battery is 0")
        self.label_CPU_Real = Gtk.Label(label="CPU is 0")
        self.label_BW_Real = Gtk.Label(label="BW is 0")


        
        # in the grid:
        # attach the first label in the top left corner   (left_attach,right_attach,top_attach,bottom_attach)
        table.attach(label_top_left, 0, 1, 0, 1)
        table.attach(label_top_right, 1, 2, 0, 1)
        table.attach(label_bottom_left, 0, 1, 3, 4)
        table.attach(label_bottom_right, 1, 2, 3, 4)
        
        table.attach(self.label_Simulation, 2, 3, 0, 1)        
        table.attach(self.label_Buffer_Sim, 2, 3, 1, 2)
        table.attach(self.label_Battery_Sim, 2, 3, 2, 3)
        table.attach(self.label_CPU_Sim, 2, 3, 4, 5)
        table.attach(self.label_BW_Sim, 2, 3, 5, 6)
        
        table.attach(self.label_Real, 3, 4, 0, 1)        
        table.attach(self.label_Buffer_Real, 3, 4, 1, 2)
        table.attach(self.label_Battery_Real, 3, 4, 2, 3)
        table.attach(self.label_CPU_Real, 3, 4, 4, 5)
        table.attach(self.label_BW_Real, 3, 4, 5, 6)
        
        #Togle button Power supply
        PowerSupplyButton = Gtk.CheckButton(" Power Supply ")
        PowerSupplyButton.connect("toggled", self.on_button_power_supply, "1")
        table.attach (PowerSupplyButton, 1, 2, 1, 2)

        #Slider 1 Buffer
        self.Buffer_Sim = Gtk.HScale()
        self.Buffer_Sim.set_range(0, 100)
        self.Buffer_Sim.set_increments(1, 10)
        self.Buffer_Sim.set_digits(0)
        self.Buffer_Sim.set_size_request(50, 35)
        self.Buffer_Sim.connect("value-changed", self.BufferChange)
        table.attach(self.Buffer_Sim, 0, 1, 2, 3)
   
        #Slider 2
        self.CPU_Sim = Gtk.HScale()
        self.CPU_Sim.set_range(0, 100)
        self.CPU_Sim.set_increments(1, 10)
        self.CPU_Sim.set_digits(0)
        self.CPU_Sim.set_size_request(50, 35)
        self.CPU_Sim.connect("value-changed", self.CPUChange)
        table.attach(self.CPU_Sim, 0, 1, 4, 5)
         
        #Slider 3
        self.BW_Sim = Gtk.HScale()
        self.BW_Sim.set_range(0, 100)
        self.BW_Sim.set_increments(1, 10)
        self.BW_Sim.set_digits(0)
        self.BW_Sim.set_size_request(50, 35)
        self.BW_Sim.connect("value-changed", self.BWChange)
        table.attach(self.BW_Sim, 1, 2,4,5)
         
        #Slider 4
        self.Battery_Sim = Gtk.HScale()
        self.Battery_Sim.set_range(0, 100)
        self.Battery_Sim.set_increments(1, 10)
        self.Battery_Sim.set_digits(0)
        self.Battery_Sim.set_size_request(50, 35)
        self.Battery_Sim.connect("value-changed", self.BatteryChange)
        table.attach(self.Battery_Sim, 1, 2, 2, 3)
        
        self.entry = Gtk.Entry()
        hbox.add(self.entry)
        self.button_open = Gtk.Button("Open")
        hbox.pack_start(self.button_open, False, False, 0)
        self.button_open.connect("clicked", self.open_mpd)
        
        self.button_pause = Gtk.Button("Pause")
        hbox.pack_start(self.button_pause, False, False, 0)
        self.button_pause.connect("clicked", self.play_pause)
        
        self.movie_window = Gtk.DrawingArea()
        vbox.add(self.movie_window)
        window.show_all()
        
        self.player()
    
    def player (self):
        #Gstreamer
        self.player = Gst.Pipeline.new("player")
        self.source = Gst.ElementFactory.make("souphttpsrc", "http-src")
        self.dashdemuxer = Gst.ElementFactory.make("dashdemux", "dashdemux")
        
        self.videoqueue = Gst.ElementFactory.make("queue", "video_queue")
        self.videodemuxer = Gst.ElementFactory.make("qtdemux", "videodemuxer")
        self.videodecoder = Gst.ElementFactory.make ("h264parse","video_decoder")
        self.videoconvert = Gst.ElementFactory.make ("avdec_h264","video_convert")
        self.videosink = Gst.ElementFactory.make("autovideosink", "video_sink")

        self.audioqueue = Gst.ElementFactory.make("queue", "audio_queue")
        self.audiodemuxer = Gst.ElementFactory.make("qtdemux", "audio_demuxer")
        self.audiodecoder = Gst.ElementFactory.make("aacparse", "audio_decoder")
        self.audioconv = Gst.ElementFactory.make("faad", "audio_converter")
        self.audiosink = Gst.ElementFactory.make("autoaudiosink", "audio-output")
        
 
        self.player.add(self.source)
        self.player.add(self.dashdemuxer)
        self.player.add(self.videodemuxer)
        self.player.add(self.audiodemuxer)
        self.player.add(self.videodecoder)
        self.player.add(self.audiodecoder)
        self.player.add(self.audioconv)
        self.player.add(self.audiosink)
        self.player.add(self.videosink)
        self.player.add(self.videoqueue)
        self.player.add(self.audioqueue)
        self.player.add(self.videoconvert)
        
        self.source.link(self.dashdemuxer)
        self.dashdemuxer.link(self.videodemuxer)
        self.dashdemuxer.link(self.audiodemuxer)
        
        
        self.videoqueue.link(self.videodecoder)
        self.videodecoder.link(self.videoconvert)
        self.videoconvert.link(self.videosink)
        
        self.audioqueue.link(self.audiodecoder)
        self.audiodecoder.link(self.audioconv)
        self.audioconv.link(self.audiosink)
        
        #Handlers
        self.dashdemuxer.connect("pad-added",self.dashdemuxer_callback)
        self.videodemuxer.connect("pad-added",self.videodemuxer_callback)
        self.audiodemuxer.connect("pad-added",self.audiodemuxer_callback)
        
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)
        
    def open_mpd(self, w):
        self.enviorment()
        if self.button_open.get_label() == "Play":
                self.player.set_state(Gst.State.PLAYING)
        #check button value 
        if self.button_open.get_label() == "Open":
        
            #filepath = self.entry.get_text().strip()
#             filepath = 'http://localhost/dash/normal/stream.mpd'
            filepath = 'http://www.bok.net/dash/tears_of_steel/cleartext/stream.mpd'
            if filepath.startswith("http://"):
                print ('Url OK')
                self.button_open.set_label("Play")
                self.player.get_by_name("http-src").set_property("location", filepath)
                self.player.set_state(Gst.State.PLAYING)
            else:
                print ('Input a valid url')
                self.player.set_state(Gst.State.READY)
                self.button_open.set_label("Open")
                    
        
    def play_pause(self, w):
        print ('Pause')
        self.player.set_state(Gst.State.PAUSED)
        
    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")

    
    def on_sync_message(self, bus, message):
        if message.get_structure().get_name() == 'prepare-window-handle':
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            xid = self.movie_window.get_property('window').get_xid()
            imagesink.set_window_handle(xid)
    
    def dashdemuxer_callback(self, demuxer, pad):
            print ('demuxer_call_bak')
            print('valor %s' % pad.get_name())
            if pad.get_name() == "ghostpad0":
                qv_pad = self.videodemuxer.get_static_pad("sink")
                pad.link(qv_pad)
                print ('link video')
            elif pad.get_name() == "ghostpad1":
                qa_pad = self.audiodemuxer.get_static_pad("sink")
                pad.link(qa_pad)
                print ('link audio')

    def videodemuxer_callback(self, demuxer, pad):
            print ('videodemuxer_callback')
            print('valor %s' % pad.get_name())
            if pad.get_name() == "video_0":
                qv_pad = self.videoqueue.get_static_pad("sink")
                pad.link(qv_pad)
                print ('link video')
            elif pad.get_name() == "audio_0":
                qa_pad = self.audioqueue.get_static_pad("sink")
                pad.link(qa_pad)
                print ('link audio')
    
    def audiodemuxer_callback(self, demuxer, pad):
            print ('audiodemuxer_callback')
            print('valor %s' % pad.get_name())
            if pad.get_name() == "video_0":
                qv_pad = self.videoqueue.get_static_pad("sink")
                pad.link(qv_pad)
                print ('link video')
            elif pad.get_name() == "audio_0":
                qa_pad = self.audioqueue.get_static_pad("sink")
                pad.link(qa_pad)
                print ('link audio')



    '''
    UI
    '''
    def on_button_power_supply(self, button, name):
        if button.get_active():
            state = "on"
        else:
            state = "off"
        print("Button", name, "was turned", state)
        
    def BufferChange(self, event):
        self.label_Buffer_Sim.set_text("Buffer is " + str(int(self.Buffer_Sim.get_value())))
    
    def BatteryChange(self, event):
        self.label_Battery_Sim.set_text("Battery is " + str(int(self.Battery_Sim.get_value())))
    
    def CPUChange(self, event):
        self.label_CPU_Sim.set_text("CPU is " + str(int(self.CPU_Sim.get_value())))
    
    def BWChange(self, event):
        self.label_BW_Sim.set_text("BW is " + str(int(self.BW_Sim.get_value())))        

    def enviormentCPU (self):
        psutil.cpu_times()
        psutil.cpu_percent(interval=0.5)
        
    def enviormentBattery (self):
        BATT_NOW     =   "/sys/class/power_supply/BAT0/charge_now"
        BATT_FULL    =  "/sys/class/power_supply/BAT0/charge_full_design"
        BATT_STATUS  =     "/sys/class/power_supply/BAT0/status"    
    
        full = open(BATT_FULL, 'r')
        full_value = full.read()
        
        now = open(BATT_NOW, 'r')
        now_value = now.read()
        
        status = open(BATT_STATUS, 'r')
        status_value = status.read()
        
        if 'Charging' in  status_value:
            statusBattery = 'Charging'
        
        elif 'Discharging' in status_value:
            statusBattery = 'Discharging'
        
        elif 'Full' in status_value:
            statusBattery = ' Full '
        
        print full_value
        print now_value
        print statusBattery
        
        BatteryLoad = (int(now_value) / ( int(full_value)/100))
          
        print BatteryLoad
        full.close()
        now.close()
        status.close()
        
        


if __name__ == "__main__":
    GTK_Main()# run Python Class
    Gtk.main()# run Ui