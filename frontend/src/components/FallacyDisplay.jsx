export default function FallacyDisplay({ fallacies }) {
    const fallacyText = fallacies.map((element, index) => <li key={index}><strong>{element["speaker"]}: {element["fallacy_type"]}</strong></li>)
    return (
        <>
        <h3>Fallacies</h3>
        <ul>{fallacyText}</ul>
        </>
    )
}