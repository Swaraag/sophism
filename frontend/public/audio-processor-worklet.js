class AudioProcessorWorklet extends AudioWorkletProcessor {
    constructor() {
        super();
    }
    process(inputs, outputs, parameters) {
        if (inputs[0][0]) {
            this.port.postMessage({ audioData: inputs[0][0]})
        }
        return true;
    }
}

registerProcessor("audio-processor-worklet", AudioProcessorWorklet)