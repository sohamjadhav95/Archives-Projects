async function handleInstruction() {
    const instruction = document.getElementById('instructionInput').value;
    
    const response = await fetch('YOUR_BACKEND_ENDPOINT', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ instruction }),
    });

    const data = await response.json();
    document.getElementById('resultOutput').innerText = data.result; // Display execution result
    document.getElementById('codeOutput').innerText = data.code; // Display generated code
}

// Attach event listener to the button
document.getElementById('executeButton').addEventListener('click', handleInstruction);
