class AudioProcessorWorklet extends AudioWorkletProcessor {
    constructor() {
        super();
        this.buffer = new Float32Array(16000);
        this.bufferIndex = 0; // 1 second at 48kHz, 3 seconds at 16kHz
        this.bufferSize = 16000;

    }
    process(inputs, outputs, parameters) {
        const inputChannel = inputs[0][0]
        if (inputChannel) {
            this.buffer.set(inputChannel, this.bufferIndex)
            this.bufferIndex += inputChannel.length;

            if (this.bufferIndex >= this.bufferSize) {
                this.port.postMessage({ audioData: this.buffer.slice(0, this.bufferIndex)});
                this.bufferIndex = 0;
            }
        }
        return true;
    }
}

registerProcessor("audio-processor-worklet", AudioProcessorWorklet)