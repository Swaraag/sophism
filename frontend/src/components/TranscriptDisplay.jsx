
export default function TranscriptDisplay({ transcript }) {
    // transcript format: [{"speaker": "speaker1", "start": 0:00, "end": 0:25, "transcript": "What's up?"}, ...]
    const transcriptText = transcript.map((element, index) => <li key={index}>{element["speaker"] + ": " + element["transcript"] + " (" + element["start"].toFixed(2) + "-" + element["end"].toFixed(2) + ")"}</li>)

    return (
        <ul>{transcriptText}</ul>
    )
}