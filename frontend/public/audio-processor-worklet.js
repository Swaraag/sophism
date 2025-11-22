class AudioProcessorWorklet extends AudioWorkletProcessor {
    constructor() {
        super();
        this.bufferSize = 240000; // 3 second at 16kHz
        this.buffer = new Float32Array(this.bufferSize);
        this.bufferIndex = 0; 
        

    }
    process(inputs, outputs, parameters) {
        const inputChannel = inputs[0][0]
        if (inputChannel) {
            this.buffer.set(inputChannel, this.bufferIndex)
            this.bufferIndex += inputChannel.length;

            if (this.bufferIndex >= this.bufferSize) {
                console.log(`Sending ${this.bufferIndex} samples to backend`);
                this.port.postMessage({ audioData: this.buffer.slice(0, this.bufferIndex)});
                this.bufferIndex = 0;
            }
        }
        return true;
    }
}

registerProcessor("audio-processor-worklet", AudioProcessorWorklet)