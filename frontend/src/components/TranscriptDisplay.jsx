
export default function TranscriptDisplay({ transcript }) {
    // transcript format: [{"speaker": "speaker1", "start": 0:00, "end": 0:25, "transcript": "What's up?"}, ...]
    const transcriptText = transcript.map((element, index) => <li key={index}><strong>{element["speaker"]}</strong>{": " + element["transcript"] + " (" + element["start"].toFixed(2) + "-" + element["end"].toFixed(2) + ")"}</li>)

    return (
        <>
        <h3>Transcript</h3>
        <ul>{transcriptText}</ul>
        </>
    )
}