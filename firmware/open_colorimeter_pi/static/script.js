// Auto-refresh state
let autoRefreshInterval = null;
let deviceConfig = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadConfiguration();
    updateStatus();
    refreshMeasurement();
    loadCalibrations();
    loadConfigFiles();
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

    // Load data when switching to specific tabs
    if (tabName === 'calibrations') {
        loadCalibrationsEditor();
    } else if (tabName === 'config') {
        loadConfigFiles();
    }
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

        // Update solenoid status
        const solenoidStatus = document.getElementById('solenoid-status');
        if (data.solenoid_connected) {
            solenoidStatus.textContent = '🟢 Solenoids Connected';
            solenoidStatus.classList.add('connected');
        } else {
            solenoidStatus.textContent = '🔴 Solenoids Disconnected';
            solenoidStatus.classList.remove('connected');
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

// Solenoid control
async function toggleSolenoid(solenoidNum, state) {
    const solenoidBox = document.getElementById(`solenoid-${solenoidNum}`);
    const valueDisplay = solenoidBox.querySelector('.motor-value');

    try {
        const response = await fetch(`/api/solenoid/${solenoidNum}/set`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state: state })
        });

        const data = await response.json();
        if (data.error) {
            console.error('Solenoid control error:', data.error);
            return;
        }

        // Update display
        if (state) {
            valueDisplay.textContent = 'ON';
            valueDisplay.style.color = '#10b981'; // Green for ON
        } else {
            valueDisplay.textContent = 'OFF';
            valueDisplay.style.color = '#2F80ED'; // Blue for OFF
        }
    } catch (error) {
        console.error('Solenoid control error:', error);
    }
}

async function turnOffAllSolenoids() {
    for (let i = 1; i <= 8; i++) {
        const solenoidBox = document.getElementById(`solenoid-${i}`);
        const checkbox = solenoidBox.querySelector('input[type="checkbox"]');

        checkbox.checked = false;
        await toggleSolenoid(i, false);
    }
}

// Load device configuration
async function loadConfiguration() {
    try {
        const response = await fetch('/api/mappings');
        deviceConfig = await response.json();

        // Update motor names
        if (deviceConfig.motors) {
            for (let i = 1; i <= 4; i++) {
                const motorBox = document.getElementById(`motor-${i}`);
                if (motorBox && deviceConfig.motors[i]) {
                    const heading = motorBox.querySelector('h3');
                    if (heading) {
                        heading.textContent = deviceConfig.motors[i].name;
                        if (deviceConfig.motors[i].description) {
                            heading.title = deviceConfig.motors[i].description;
                        }
                    }
                }
            }
        }

        // Update solenoid names
        if (deviceConfig.solenoids) {
            for (let i = 1; i <= 8; i++) {
                const solenoidBox = document.getElementById(`solenoid-${i}`);
                if (solenoidBox && deviceConfig.solenoids[i]) {
                    const heading = solenoidBox.querySelector('h3');
                    if (heading) {
                        heading.textContent = deviceConfig.solenoids[i].name;
                        if (deviceConfig.solenoids[i].description) {
                            heading.title = deviceConfig.solenoids[i].description;
                        }
                    }
                }
            }
        }

        // Load saved sequences into dropdown
        loadSequenceList();
    } catch (error) {
        console.error('Load configuration error:', error);
    }
}

// Sequence management functions
let savedSequences = {};

async function loadSequenceList() {
    try {
        const response = await fetch('/api/sequences');
        savedSequences = await response.json();

        const select = document.getElementById('sequence-select');
        if (!select) return;

        // Clear existing options except the first one
        select.innerHTML = '<option value="">-- Select a sequence --</option>';

        // Add sequences (templates first, then user sequences)
        const templates = [];
        const userSequences = [];

        for (const [name, seq] of Object.entries(savedSequences)) {
            if (seq.template) {
                templates.push([name, seq]);
            } else {
                userSequences.push([name, seq]);
            }
        }

        // Add templates first
        for (const [name, seq] of templates) {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name + ' (Template)';
            if (seq.description) {
                option.title = seq.description;
            }
            select.appendChild(option);
        }

        // Add user sequences
        for (const [name, seq] of userSequences) {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            if (seq.description) {
                option.title = seq.description;
            }
            select.appendChild(option);
        }
    } catch (error) {
        console.error('Error loading sequences:', error);
    }
}

function loadSequence() {
    const select = document.getElementById('sequence-select');
    const textarea = document.getElementById('sequence-input');
    const selectedName = select.value;

    if (!selectedName || !savedSequences) {
        alert('Please select a sequence');
        return;
    }

    const sequence = savedSequences[selectedName];
    if (sequence && sequence.commands) {
        textarea.value = sequence.commands.join('\n');
    }
}

async function saveSequence() {
    const select = document.getElementById('sequence-select');
    const textarea = document.getElementById('sequence-input');
    const selectedName = select.value;
    const content = textarea.value.trim();

    if (!selectedName) {
        alert('Please select a sequence to update, or use "Save As..." to create a new one');
        return;
    }

    if (!content) {
        alert('Please enter some commands first');
        return;
    }

    // Check if this is a template
    if (savedSequences[selectedName] && savedSequences[selectedName].template) {
        alert('Templates cannot be modified. Please use "Save As..." to create a new sequence based on this template.');
        return;
    }

    try {
        // Parse commands
        const commands = content.split('\n').map(line => line.trim()).filter(line => line !== '');

        // Update the selected sequence
        if (savedSequences[selectedName]) {
            savedSequences[selectedName].commands = commands;
        } else {
            alert('Selected sequence not found');
            return;
        }

        // Save sequences
        const response = await fetch('/api/sequences/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: savedSequences })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error saving sequence: ' + data.error);
        } else {
            alert(`Sequence "${selectedName}" updated successfully!`);
        }
    } catch (error) {
        alert('Error saving sequence: ' + error.message);
    }
}

async function saveSequenceAs() {
    const textarea = document.getElementById('sequence-input');
    const content = textarea.value.trim();

    if (!content) {
        alert('Please enter some commands first');
        return;
    }

    const name = prompt('Enter a name for this sequence:');
    if (!name) return;

    const description = prompt('Enter a description (optional):') || '';

    try {
        // Parse commands
        const commands = content.split('\n').map(line => line.trim()).filter(line => line !== '');

        // Add to sequences
        savedSequences[name] = {
            description: description,
            commands: commands
        };

        // Save sequences
        const response = await fetch('/api/sequences/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: savedSequences })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error saving sequence: ' + data.error);
        } else {
            alert(`Sequence "${name}" saved successfully!`);
            loadSequenceList();
            // Select the newly saved sequence
            document.getElementById('sequence-select').value = name;
        }
    } catch (error) {
        alert('Error saving sequence: ' + error.message);
    }
}

async function deleteSequence() {
    const select = document.getElementById('sequence-select');
    const selectedName = select.value;

    if (!selectedName) {
        alert('Please select a sequence to delete');
        return;
    }

    // Check if this is a template
    if (savedSequences[selectedName] && savedSequences[selectedName].template) {
        alert('Templates cannot be deleted.');
        return;
    }

    if (!confirm(`Are you sure you want to delete "${selectedName}"?`)) {
        return;
    }

    try {
        // Remove from sequences
        if (savedSequences[selectedName]) {
            delete savedSequences[selectedName];
        }

        // Save sequences
        const response = await fetch('/api/sequences/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: savedSequences })
        });

        const data = await response.json();

        if (data.error) {
            alert('Error deleting sequence: ' + data.error);
        } else {
            alert(`Sequence "${selectedName}" deleted successfully!`);
            loadSequenceList();
            select.value = '';
        }
    } catch (error) {
        alert('Error deleting sequence: ' + error.message);
    }
}

// Sequence execution
let sequenceRunning = false;

async function executeSequence() {
    if (sequenceRunning) {
        alert('Sequence already running!');
        return;
    }

    const sequenceText = document.getElementById('sequence-input').value;
    const lines = sequenceText.split('\n').filter(line => line.trim() !== '');

    if (lines.length === 0) {
        alert('Please enter at least one command');
        return;
    }

    sequenceRunning = true;
    const statusDiv = document.getElementById('sequence-status');
    const progressDiv = document.getElementById('sequence-progress');
    statusDiv.style.display = 'block';
    progressDiv.innerHTML = 'Starting sequence...\n';

    try {
        for (let i = 0; i < lines.length && sequenceRunning; i++) {
            const line = lines[i].trim();
            progressDiv.innerHTML += `\n[${i + 1}/${lines.length}] ${line}\n`;

            // Check for single-word commands (blank, measure)
            if (line.toLowerCase() === 'blank') {
                progressDiv.innerHTML += `  🔘 Blanking sensor...\n`;
                try {
                    const response = await fetch('/api/blank', { method: 'POST' });
                    const data = await response.json();
                    if (data.error) {
                        progressDiv.innerHTML += `  ❌ Blank failed: ${data.error}\n`;
                    } else {
                        progressDiv.innerHTML += `  ✓ Sensor blanked (value: ${data.blank_value})\n`;
                    }
                } catch (error) {
                    progressDiv.innerHTML += `  ❌ Blank error: ${error}\n`;
                }
                continue;
            }

            // Check for measure command (with or without test name)
            if (line.toLowerCase().startsWith('measure')) {
                const measureParts = line.split(' ').map(p => p.trim());
                const testName = measureParts.length > 1 ? measureParts.slice(1).join(' ') : null;

                if (testName) {
                    // Specific test measurement
                    progressDiv.innerHTML += `  📊 Measuring ${testName}...\n`;

                    // Check if test is configured
                    if (deviceConfig && deviceConfig.tests && deviceConfig.tests[testName]) {
                        const test = deviceConfig.tests[testName];
                        progressDiv.innerHTML += `  🔄 Using sensor ${test.sensor}, calibration: ${test.calibration}\n`;
                        // TODO: Switch multiplexer to sensor ${test.sensor} when hardware is ready
                    } else {
                        progressDiv.innerHTML += `  ⚠ Test "${testName}" not configured, using current sensor\n`;
                    }
                } else {
                    // Generic measurement
                    progressDiv.innerHTML += `  📊 Taking measurement...\n`;
                }

                try {
                    const response = await fetch('/api/measure');
                    const data = await response.json();
                    if (data.error) {
                        progressDiv.innerHTML += `  ❌ Measurement failed: ${data.error}\n`;
                    } else {
                        progressDiv.innerHTML += `  ✓ Raw: ${data.raw}, Abs: ${data.absorbance.toFixed(4)}\n`;

                        // Show specific test result or all results
                        if (testName && data.calibrated && data.calibrated[testName]) {
                            const cal = data.calibrated[testName];
                            progressDiv.innerHTML += `  ✅ ${testName}: ${cal.value} ${cal.units}\n`;
                        } else if (data.calibrated && Object.keys(data.calibrated).length > 0) {
                            // Show all calibrated values
                            for (const [name, cal] of Object.entries(data.calibrated)) {
                                progressDiv.innerHTML += `  ✓ ${name}: ${cal.value} ${cal.units}\n`;
                            }
                        }
                    }
                } catch (error) {
                    progressDiv.innerHTML += `  ❌ Measurement error: ${error}\n`;
                }
                continue;
            }

            // Parse command (motor, solenoid, wait)
            const parts = line.split(',').map(p => p.trim());
            if (parts.length !== 2) {
                progressDiv.innerHTML += `  ⚠ Invalid format, skipping\n`;
                continue;
            }

            const [deviceName, value] = parts;

            // Check for wait command
            if (deviceName.toLowerCase() === 'wait') {
                const seconds = parseFloat(value);
                if (isNaN(seconds)) {
                    progressDiv.innerHTML += `  ⚠ Invalid wait time\n`;
                    continue;
                }
                progressDiv.innerHTML += `  ⏳ Waiting ${seconds} seconds...\n`;
                await sleep(seconds * 1000);
                progressDiv.innerHTML += `  ✓ Wait complete\n`;
                continue;
            }

            // Find device in configuration
            const motorNum = findMotorByName(deviceName);
            const solenoidNum = findSolenoidByName(deviceName);

            if (motorNum !== null) {
                // Motor command
                const seconds = parseFloat(value);
                if (isNaN(seconds)) {
                    progressDiv.innerHTML += `  ⚠ Invalid motor time\n`;
                    continue;
                }

                const throttle = seconds > 0 ? 1.0 : -1.0;
                const duration = Math.abs(seconds);

                progressDiv.innerHTML += `  🔄 Motor ${motorNum}: ${throttle > 0 ? 'forward' : 'reverse'} for ${duration}s\n`;

                // Start motor
                await fetch(`/api/motor/${motorNum}/throttle`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ throttle: throttle })
                });

                // Wait for duration
                await sleep(duration * 1000);

                // Stop motor
                await fetch(`/api/motor/${motorNum}/stop`, { method: 'POST' });
                progressDiv.innerHTML += `  ✓ Motor ${motorNum} stopped\n`;

            } else if (solenoidNum !== null) {
                // Solenoid command
                const state = value.toLowerCase() === 'on';
                progressDiv.innerHTML += `  💧 Solenoid ${solenoidNum}: ${state ? 'ON' : 'OFF'}\n`;

                await fetch(`/api/solenoid/${solenoidNum}/set`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ state: state })
                });
                progressDiv.innerHTML += `  ✓ Complete\n`;

            } else {
                progressDiv.innerHTML += `  ⚠ Device not found: "${deviceName}"\n`;
            }
        }

        progressDiv.innerHTML += `\n✅ Sequence complete!\n`;
    } catch (error) {
        progressDiv.innerHTML += `\n❌ Error: ${error}\n`;
        console.error('Sequence error:', error);
    } finally {
        sequenceRunning = false;
    }
}

function stopSequence() {
    if (sequenceRunning) {
        sequenceRunning = false;
        const progressDiv = document.getElementById('sequence-progress');
        progressDiv.innerHTML += `\n🛑 Sequence stopped by user\n`;
    }
}

function findMotorByName(name) {
    if (!deviceConfig || !deviceConfig.motors) return null;
    for (let num = 1; num <= 4; num++) {
        if (deviceConfig.motors[num] && deviceConfig.motors[num].name === name) {
            return num;
        }
    }
    return null;
}

function findSolenoidByName(name) {
    if (!deviceConfig || !deviceConfig.solenoids) return null;
    for (let num = 1; num <= 8; num++) {
        if (deviceConfig.solenoids[num] && deviceConfig.solenoids[num].name === name) {
            return num;
        }
    }
    return null;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
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

// Config editor functions
async function loadConfigFiles() {
    try {
        const response = await fetch('/api/config/load');
        const data = await response.json();

        if (data.error) {
            showConfigStatus('Error loading files: ' + data.error, 'error');
            return;
        }

        // Load into editors with pretty formatting
        const mappingsEditor = document.getElementById('mappings-editor');
        const sequencesEditor = document.getElementById('sequences-editor');
        const calibrationsEditor = document.getElementById('calibrations-editor');

        if (mappingsEditor) {
            mappingsEditor.value = JSON.stringify(data.mappings, null, 2);
        }

        if (sequencesEditor) {
            sequencesEditor.value = JSON.stringify(data.sequences, null, 2);
        }

        if (calibrationsEditor) {
            calibrationsEditor.value = JSON.stringify(data.calibrations, null, 2);
        }
    } catch (error) {
        console.error('Load config files error:', error);
        showConfigStatus('Error loading files: ' + error, 'error');
    }
}

async function saveMappings() {
    const editor = document.getElementById('mappings-editor');
    const content = editor.value;

    try {
        // Validate JSON
        const parsed = JSON.parse(content);

        // Save to server
        const response = await fetch('/api/mappings/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: parsed })
        });

        const data = await response.json();

        if (data.error) {
            showConfigStatus('Error saving mappings: ' + data.error, 'error');
        } else {
            showConfigStatus('✓ Mappings saved successfully! Reload page to see changes.', 'success');
            // Reload device config in memory
            loadConfiguration();
        }
    } catch (error) {
        showConfigStatus('Invalid JSON: ' + error.message, 'error');
    }
}

async function saveSequencesConfig() {
    const editor = document.getElementById('sequences-editor');
    const content = editor.value;

    try {
        // Validate JSON
        const parsed = JSON.parse(content);

        // Save to server
        const response = await fetch('/api/sequences/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: parsed })
        });

        const data = await response.json();

        if (data.error) {
            showConfigStatus('Error saving sequences: ' + data.error, 'error');
        } else {
            showConfigStatus('✓ Sequences saved successfully!', 'success');
            // Reload sequences list
            loadSequenceList();
        }
    } catch (error) {
        showConfigStatus('Invalid JSON: ' + error.message, 'error');
    }
}

async function saveCalibrations() {
    const editor = document.getElementById('calibrations-editor');
    const content = editor.value;

    try {
        // Validate JSON
        const parsed = JSON.parse(content);

        // Save to server
        const response = await fetch('/api/calibrations/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: parsed })
        });

        const data = await response.json();

        if (data.error) {
            showConfigStatus('Error saving: ' + data.error, 'error');
        } else {
            showConfigStatus('✓ Calibrations saved successfully!', 'success');
            // Reload calibrations list
            loadCalibrations();
        }
    } catch (error) {
        showConfigStatus('Invalid JSON: ' + error.message, 'error');
    }
}

function showConfigStatus(message, type) {
    const statusDiv = document.getElementById('config-status');
    const messageDiv = document.getElementById('config-message');

    statusDiv.style.display = 'block';
    messageDiv.innerHTML = message;

    if (type === 'error') {
        statusDiv.style.background = '#fee';
        statusDiv.style.borderLeft = '4px solid #ef4444';
        messageDiv.style.color = '#dc2626';
    } else {
        statusDiv.style.background = '#f0f9ff';
        statusDiv.style.borderLeft = '4px solid #2F80ED';
        messageDiv.style.color = '#2F80ED';
    }

    // Auto-hide after 5 seconds
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}

function showCalibrationsStatus(message, type) {
    const statusDiv = document.getElementById('calibrations-status');
    const messageDiv = document.getElementById('calibrations-message');

    statusDiv.style.display = 'block';
    messageDiv.innerHTML = message;

    if (type === 'error') {
        statusDiv.style.background = '#fee';
        statusDiv.style.borderLeft = '4px solid #ef4444';
        messageDiv.style.color = '#dc2626';
    } else {
        statusDiv.style.background = '#f0f9ff';
        statusDiv.style.borderLeft = '4px solid #2F80ED';
        messageDiv.style.color = '#2F80ED';
    }

    // Auto-hide after 5 seconds
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 5000);
}

// Load calibrations into editor on Calibrations tab
async function loadCalibrationsEditor() {
    try {
        const response = await fetch('/api/config/load');
        const data = await response.json();

        if (data.error) {
            showCalibrationsStatus('Error loading calibrations: ' + data.error, 'error');
            return;
        }

        const calibrationsEditor = document.getElementById('calibrations-editor-tab');
        if (calibrationsEditor) {
            calibrationsEditor.value = JSON.stringify(data.calibrations, null, 2);
        }
    } catch (error) {
        console.error('Load calibrations editor error:', error);
        showCalibrationsStatus('Error loading calibrations: ' + error, 'error');
    }
}

// Save calibrations from Calibrations tab
async function saveCalibrationsFromTab() {
    const editor = document.getElementById('calibrations-editor-tab');
    const content = editor.value;

    try {
        // Validate JSON
        const parsed = JSON.parse(content);

        // Save to server
        const response = await fetch('/api/calibrations/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: parsed })
        });

        const data = await response.json();

        if (data.error) {
            showCalibrationsStatus('Error saving: ' + data.error, 'error');
        } else {
            showCalibrationsStatus('✓ Calibrations saved successfully!', 'success');
            // Reload calibrations list
            loadCalibrations();
        }
    } catch (error) {
        showCalibrationsStatus('Invalid JSON: ' + error.message, 'error');
    }
}
