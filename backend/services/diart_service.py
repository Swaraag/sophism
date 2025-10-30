from diart import SpeakerDiarization
from diart.sources import WebSocketAudioSource
from diart.inference import StreamingInference

pipeline = SpeakerDiarization()
source = WebSocketAudioSource(pipeline.config.sample_rate, "localhost", 7007)
inference = StreamingInference(pipeline, source)
inference.attach_hooks(lambda ann_wav: source.send(ann_wav[0].to_rttm()))
prediction = inference()