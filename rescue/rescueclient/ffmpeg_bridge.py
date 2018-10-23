# -*- coding: utf-8 -*-
import os
import signal
import subprocess as sp
import threading


class FfmpegBridge():
    def __init__(self, sm):
        self.lock = threading.Lock();
        FFMPEG_BIN = "ffmpeg"
        FFPLAY_BIN = "ffplay"
        rtpAddress = 'rtp://' + sm.multicastIp + ':' + str(sm.multicastPort)
        print(rtpAddress)
        self.video_command = [FFMPEG_BIN,
                              '-i', '/dev/video0']
        self.audio_send_command = [FFMPEG_BIN,
                                   '-f', 'alsa',
                                   '-i', 'default',
                                   '-c:a', 'libopus',
                                   '-b:a', '12k',
                                   '-ac', '1',
                                   '-f', 'rtp',
                                   rtpAddress]
        self.audio_recv_command = [FFPLAY_BIN,
                                   '-protocol_whitelist', 'rtp,udp,tcp,file',
                                   '-nodisp',
                                   'res/opus_audio_stream.sdp']
        self.beep_command = [FFPLAY_BIN,
                             '-autoexit',
                             '-nodisp',
                             '-i', 'res/sound/beep.wav']
        self.button_command = [FFPLAY_BIN,
                             '-autoexit',
                             '-nodisp',
                             '-i', 'res/sound/button.wav']
        print(self.audio_send_command)

    def playBeep(self):
        threading.Thread(target=sp.call, kwargs={'args': self.beep_command}).start()
        print('y')

    def playButton(self):
        thread = threading.Thread(target=sp.call, kwargs={'args': self.button_command})
        thread.start()

    def sendAudioStream(self):
        self.ffmpegSubprocess = sp.Popen(' '.join(self.audio_send_command), stdout=sp.PIPE, stderr=sp.PIPE, shell=True, preexec_fn=os.setsid)
        out, err =sp.communicate()
        print(out)

    def playAudioStream(self):
        self.ffplaySubprocess = sp.Popen(' '.join(self.audio_recv_command), stdout=sp.PIPE, stderr=sp.PIPE, shell=True, preexec_fn=os.setsid)

    def stopSendingAudioStream(self):
        os.killpg(os.getpgid(self.ffmpegSubprocess.pid), signal.SIGTERM)

    def stopPlayingAudioStream(self):
        os.killpg(os.getpgid(self.ffplaySubprocess.pid), signal.SIGTERM)



