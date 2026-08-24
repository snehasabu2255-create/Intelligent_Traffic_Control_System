const evtSource = new EventSource("/api/state_stream");

const elements = {
    activePhase: document.getElementById('active-phase'),
    phaseDesc: document.getElementById('phase-desc'),
    timeRemaining: document.getElementById('time-remaining'),
    roads: ['South', 'North', 'West', 'East']
};

evtSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    updateDashboard(data);
};

function updateDashboard(data) {
    // Update global controller state
    elements.activePhase.textContent = data.active_phase;
    elements.phaseDesc.textContent = data.phase_description;
    elements.timeRemaining.textContent = data.time_remaining + 's';

    elements.roads.forEach(road => {
        // Update stats
        if (data.counts && data.counts[road] !== undefined) {
            document.getElementById(`count-${road}`).textContent = data.counts[road];
        }
        
        if (data.densities && data.densities[road] !== undefined) {
            const density = data.densities[road];
            const densityEl = document.getElementById(`density-${road}`);
            densityEl.textContent = density;
            densityEl.className = `badge density-${density}`;
        }
        
        if (data.allocated_times && data.allocated_times[road] !== undefined) {
            document.getElementById(`allocated-${road}`).textContent = data.allocated_times[road] + 's';
        }
        
        // Update Signals
        if (data.signals && data.signals[road]) {
            const sig = data.signals[road];
            
            const timerEl = document.getElementById(`timer-${road}`);
            if (sig.red) {
                timerEl.innerHTML = `<span style="color: #ef4444; font-size: 1.2rem;">RED</span>`;
            } else {
                timerEl.innerHTML = `${sig.timer}<span style="color: #fb923c;">s</span>`;
            }
            
            // Toggle bulb active classes
            document.getElementById(`${road}-red`).classList.toggle('active', sig.red);
            document.getElementById(`${road}-yellow`).classList.toggle('active', sig.yellow);
            document.getElementById(`${road}-green_s`).classList.toggle('active', sig.green_s);
            document.getElementById(`${road}-green_r`).classList.toggle('active', sig.green_r);
        }
    });
}

// Error handling
evtSource.onerror = function(err) {
    console.error("EventSource failed:", err);
    elements.activePhase.textContent = "Connection Lost";
    elements.phaseDesc.textContent = "Attempting to reconnect...";
};

// Handle Image Upload
async function handleUpload(event, roadName) {
    const file = event.target.files[0];
    if (!file) return;

    // Show local preview immediately
    const previewImg = document.getElementById(`preview-${roadName}`);
    previewImg.src = URL.createObjectURL(file);
    previewImg.style.display = 'block';

    // Upload to backend
    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch(`/upload/${roadName}`, {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        if (result.success) {
            console.log(`${roadName} uploaded successfully. Count: ${result.count}`);
            // To fetch the annotated image, we append a timestamp to bust the cache
            previewImg.src = `/video/${roadName}?t=${new Date().getTime()}`;
            document.getElementById(`close-${roadName}`).style.display = 'block';
        } else {
            alert(`Error uploading image: ${result.error}`);
        }
    } catch (error) {
        console.error('Error uploading image:', error);
        alert('Failed to communicate with server.');
    }
}

async function removeImage(roadName) {
    try {
        const response = await fetch(`/reset/${roadName}`, { method: 'POST' });
        if (response.ok) {
            document.getElementById(`preview-${roadName}`).style.display = 'none';
            document.getElementById(`preview-${roadName}`).src = '';
            document.getElementById(`upload-${roadName}`).value = '';
            document.getElementById(`close-${roadName}`).style.display = 'none';
        }
    } catch (error) {
        console.error('Error resetting image:', error);
    }
}
