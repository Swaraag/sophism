import { useState } from 'react';
export default function FallacyDisplay({ fallacies }) {
    let [expandedFallacies, updateExpandedFallacies] = useState(new Set());
    const addFallacy = (fallacy) => {
        updateExpandedFallacies(expandedFallacies => new Set(expandedFallacies).add(fallacy));
    }
    const removeFallacy = (fallacy) => {
        updateExpandedFallacies(expandedFallacies => {
            const newSet = new Set(expandedFallacies)
            newSet.delete(fallacy);
            return newSet
        });
    };

    function fallacyClicked(event) {
        // .closest() ensures that even clicking a child of the list element ends up finding the right item
        const clickedItem = event.target.closest('li');
        if (clickedItem) {
            const itemKey = Number(clickedItem.dataset.key);
            if (expandedFallacies.has(itemKey)) {
                removeFallacy(itemKey);
            }
            else {
                addFallacy(itemKey);
            }

        }
    }

    return (
        <>
        <h3>Fallacies</h3>
        <ul onClick={fallacyClicked}>
            {fallacies.map((element, index) => 
                <li key={index} data-key={index} data-is-expanded={expandedFallacies.has(index)}>
                    <div className="fallacy-header">
                        <strong>{element["speaker"]}: {element["fallacy_type"]}</strong>
                    </div>
                    {expandedFallacies.has(index) && (
                    <div className="fallacy-details">
                        <strong>Statement: </strong>{element["statement"]}<br/>
                        <strong>Explanation:</strong> {element["explanation"]}<br/>
                        <strong>Confidence:</strong> {element["confidence"]}<br/>
                    </div>
                    )}
                </li>
                )
            }
        </ul>
        </>
    )
}