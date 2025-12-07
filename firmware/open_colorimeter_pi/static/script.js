// Auto-refresh state
let autoRefreshInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateStatus();
    refreshMeasurement();
    loadCalibrations();
});

// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');

    // Add active class to clicked button
    event.target.classList.add('active');
}

// Update system status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        // Update sensor status
        const sensorStatus = document.getElementById('sensor-status');
        if (data.sensor_connected) {
            sensorStatus.textContent = '🟢 Sensor Connected';
            sensorStatus.classList.add('connected');
        } else {
            sensorStatus.textContent = '🔴 Sensor Disconnected';
            sensorStatus.classList.remove('connected');
        }

        // Update motor status
        const motorStatus = document.getElementById('motor-status');
        if (data.motor_connected) {
            motorStatus.textContent = '🟢 Motors Connected';
            motorStatus.classList.add('connected');
        } else {
            motorStatus.textContent = '🔴 Motors Disconnected';
            motorStatus.classList.remove('connected');
        }

        // Update blank status
        const blankStatus = document.getElementById('blank-status');
        if (data.is_blanked) {
            blankStatus.textContent = '✓ Blanked';
            blankStatus.classList.add('blanked');
        } else {
            blankStatus.textContent = '⚠ Not Blanked';
            blankStatus.classList.remove('blanked');
        }
    } catch (error) {
        console.error('Status update error:', error);
    }
}

// Refresh measurement
async function refreshMeasurement() {
    try {
        const response = await fetch('/api/measure');
        const data = await response.json();

        if (data.error) {
            console.error('Measurement error:', data.error);
            return;
        }

        // Update basic measurements
        document.getElementById('raw-value').textContent = data.raw.toLocaleString();
        document.getElementById('transmittance-value').textContent = data.transmittance.toFixed(4);
        document.getElementById('absorbance-value').textContent = data.absorbance.toFixed(4);

        // Update calibrated measurements
        const calibratedDiv = document.getElementById('calibrated-measurements');
        calibratedDiv.innerHTML = '';

        if (Object.keys(data.calibrated).length > 0) {
            for (const [name, cal] of Object.entries(data.calibrated)) {
                const box = document.createElement('div');
                box.className = 'calibrated-box';
                box.innerHTML = `
                    <h3>${name}</h3>
                    <div class="calibrated-value">
                        ${cal.value.toFixed(4)} ${cal.units}
                    </div>
                `;
                calibratedDiv.appendChild(box);
            }
        }

        updateStatus();
    } catch (error) {
        console.error('Measurement error:', error);
    }
}

// Blank sensor
async function blankSensor() {
    try {
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = 'Blanking...';

        const response = await fetch('/api/blank', { method: 'POST' });
        const data = await response.json();

        if (data.error) {
            alert('Blanking failed: ' + data.error);
        } else {
            alert('Sensor blanked successfully!');
            refreshMeasurement();
        }

        btn.disabled = false;
        btn.textContent = 'Blank Sensor';
    } catch (error) {
        console.error('Blank error:', error);
        alert('Blanking failed: ' + error);
    }
}

// Toggle auto-refresh
function toggleAutoRefresh() {
    const checkbox = document.getElementById('auto-refresh');
    const label = document.getElementById('auto-refresh-label');

    if (checkbox.checked) {
        // Start auto-refresh every 1 second
        autoRefreshInterval = setInterval(refreshMeasurement, 1000);
        label.textContent = 'On (1s)';
    } else {
        // Stop auto-refresh
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
        label.textContent = 'Off';
    }
}

// Motor control
async function updateMotor(motorNum, value) {
    const throttle = value / 100; // Convert 0-100 to 0.0-1.0

    // Update display
    const motorBox = document.getElementById(`motor-${motorNum}`);
    const valueDisplay = motorBox.querySelector('.motor-value');
    valueDisplay.textContent = `${value}%`;

    // Color code based on direction
    if (value > 0) {
        valueDisplay.style.color = '#10b981'; // Green for forward
    } else if (value < 0) {
        valueDisplay.style.color = '#ef4444'; // Red for reverse
    } else {
        valueDisplay.style.color = '#667eea'; // Blue for stopped
    }

    try {
        const response = await fetch(`/api/motor/${motorNum}/throttle`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ throttle: throttle })
        });

        const data = await response.json();
        if (data.error) {
            console.error('Motor control error:', data.error);
        }
    } catch (error) {
        console.error('Motor control error:', error);
    }
}

async function stopMotor(motorNum) {
    try {
        const response = await fetch(`/api/motor/${motorNum}/stop`, {
            method: 'POST'
        });

        const data = await response.json();
        if (!data.error) {
            // Reset slider
            const motorBox = document.getElementById(`motor-${motorNum}`);
            const slider = motorBox.querySelector('.motor-slider');
            slider.value = 0;

            const valueDisplay = motorBox.querySelector('.motor-value');
            valueDisplay.textContent = '0%';
            valueDisplay.style.color = '#667eea';
        }
    } catch (error) {
        console.error('Stop motor error:', error);
    }
}

function stopAllMotors() {
    for (let i = 1; i <= 4; i++) {
        stopMotor(i);
    }
}

// Load calibrations
async function loadCalibrations() {
    try {
        const response = await fetch('/api/calibrations');
        const calibrations = await response.json();

        const list = document.getElementById('calibrations-list');
        list.innerHTML = '';

        if (calibrations.length === 0) {
            list.innerHTML = '<p>No calibrations loaded. Add calibrations to calibrations.json</p>';
            return;
        }

        calibrations.forEach(cal => {
            const item = document.createElement('div');
            item.className = 'calibration-item';

            let rangeText = '';
            if (cal.range && cal.range.min !== undefined && cal.range.max !== undefined) {
                rangeText = `Range: ${cal.range.min} - ${cal.range.max} ${cal.units}`;
            }

            item.innerHTML = `
                <h3>${cal.name}</h3>
                <div class="calibration-info">
                    Units: ${cal.units}<br>
                    LED: ${cal.led} nm<br>
                    ${rangeText}
                </div>
            `;
            list.appendChild(item);
        });
    } catch (error) {
        console.error('Load calibrations error:', error);
    }
}
