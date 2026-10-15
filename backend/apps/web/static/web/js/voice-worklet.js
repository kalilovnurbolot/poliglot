// Runs on the audio thread: turns microphone audio (usually 44.1/48 kHz float)
// into 16 kHz signed 16-bit PCM chunks of 100 ms, the format the voice service expects.
const TARGET_RATE = 16000;
const CHUNK_SAMPLES = TARGET_RATE / 10;

class PcmDownsampler extends AudioWorkletProcessor {
  constructor() {
    super();
    this.ratio = sampleRate / TARGET_RATE;
    this.position = 0;
    this.sum = 0;
    this.count = 0;
    this.chunk = new Int16Array(CHUNK_SAMPLES);
    this.length = 0;
  }

  process(inputs) {
    const samples = inputs[0][0];
    if (!samples) return true;
    for (let i = 0; i < samples.length; i++) {
      // Averaging each window of input samples is a cheap low-pass filter before decimation.
      this.sum += samples[i];
      this.count++;
      if (++this.position < this.ratio) continue;
      this.position -= this.ratio;
      const value = Math.max(-1, Math.min(1, this.sum / this.count));
      this.sum = 0;
      this.count = 0;
      this.chunk[this.length++] = value * 0x7fff;
      if (this.length === CHUNK_SAMPLES) {
        this.port.postMessage(this.chunk.buffer, [this.chunk.buffer]);
        this.chunk = new Int16Array(CHUNK_SAMPLES);
        this.length = 0;
      }
    }
    return true;
  }
}

registerProcessor("pcm-downsampler", PcmDownsampler);
