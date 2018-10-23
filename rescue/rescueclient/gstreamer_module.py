import sys, os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, Gobject, Gtk

class GstreamerModule:
    def __init__(self):
        self.streamer = Gst.Pipeline.new('streamer')
        

