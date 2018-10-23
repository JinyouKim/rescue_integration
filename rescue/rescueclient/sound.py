import sounddevice as sd
import soundfile as sf
import queue
import sys

class StopException(Exception):
    def __init__(self, msg='init_error_msg'):
        self.msg = msg
    def __str__(self):
        return self.msg

class SoundManager():
    def __init__(self, inputDeviceName='default', outputDeviceName = 'default'):
        self.inputDeviceName = inputDeviceName
        self.outputDeviceName = outputDeviceName
        self.inputQ = queue.Queue()
        self.outputQ = queue.Queue(maxsize=2048)
        self.samples = 12000
        self.channels = 1
        self.mapping = [c-1 for c in [1]]
        self.inputStream = None
        self.outputStream = None

    def callbackInput(self, inputData, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        self.inputQ.put(inputData)
    
    def callbackOutput(self, outputData, frames, time, status):
        if status.output_underflow:
            print('underflow', file=sys.stderr)
            return
            raise sd.CallbackAbort
        assert not status
        try:
            data = self.outputQ.get()
        except queue.Empty:
            print('buffer is empry', file=sys.stderr)
            return
            raise sd.CallbackAbort
        if len(data) < len(outputData):
            outputData[:len(data)] = data
            outputData[len(data):] = b'\x00' * (len(outputData) - len(data))
        else:
            outputData[:] = data

    def startRecord(self):
        self.inputStream = sd.InputStream(channels=self.channels, samplerate=self.samples, device=self.inputDeviceName, dtype='int16', blocksize=240, callback=self.callbackInput, latency='high')
        self.inputStream.start()

    def stopRecord(self):
        self.inputStream.stop()

    def startPlay(self):
        self.outputStream = sd.RawOutputStream(channels=self.channels, samplerate=self.samples, device=self.outputDeviceName, dtype='int16', blocksize=240, callback=self.callbackOutput)
        self.outputStream.start()
	
    def stopPlay(self):
        self.outputStream.stop()
	
    def getInputFrame(self):
        return self.inputQ.get()

    def pushFrame(self, data):
        self.outputQ.put(data, timeout= 160 * 2048 / self.samples)

    def playRing(self):
        data, fs = sf.read("res/sound/ring.wav")
        sd.play(data, fs, device=self.outputDeviceName, loop = True)
        
    def stopRing(self):
        sd.stop()


if __name__ == "__main__":
    sm = SoundManager()
    sm.playRing()

    while True:
        print(sm.inputQ.get())

