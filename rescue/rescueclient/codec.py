import opuslib

class OpusCodec:
    def __init__(self, samples = 12000, frames = 240, channels = 1):
        self.frames = frames
        self.encoder = opuslib.Encoder(samples, channels, opuslib.APPLICATION_VOIP)
        self.decoder = opuslib.Decoder(samples, channels)

    def encodeFrames(self, data):
        return self.encoder.encode(data, self.frames)

    def decodeFrames(self, data):
        return self.decoder.decode(data, frame_size = self.frames)




