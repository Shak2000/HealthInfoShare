document.addEventListener('DOMContentLoaded', () => {
    const addRecordForm = document.getElementById('addRecordForm');
    const patientNameInput = document.getElementById('patientName');
    const symptomsInput = document.getElementById('symptoms');
    const hazardsInput = document.getElementById('hazards');
    const recordsTableBody = document.getElementById('recordsTableBody');
    const viewRecordsBtn = document.getElementById('viewRecordsBtn');
    const deleteAllBtn = document.getElementById('deleteAllBtn');
    const statusMessage = document.getElementById('statusMessage');
    const dateOptionRadios = document.querySelectorAll('input[name="dateOption"]');
    const customDateFields = document.getElementById('customDateFields');
    const yearInput = document.getElementById('year');
    const monthInput = document.getElementById('month');
    const dayInput = document.getElementById('day');
    const hourInput = document.getElementById('hour');
    const minuteInput = document.getElementById('minute');
    const secondInput = document.getElementById('second');

    // Show/hide custom date fields based on radio button selection
    dateOptionRadios.forEach(radio => {
        radio.addEventListener('change', (event) => {
            if (event.target.value === 'custom') {
                customDateFields.classList.remove('hidden');
            } else {
                customDateFields.classList.add('hidden');
            }
        });
    });

    // Helper function to show a temporary status message
    function showStatus(message, isError = false) {
        statusMessage.textContent = message;
        statusMessage.className = `mt-4 text-center text-sm font-medium ${isError ? 'text-red-600' : 'text-green-600'}`;
        setTimeout(() => {
            statusMessage.textContent = '';
        }, 5000);
    }

    // Function to fetch and render records from the server
    async function fetchAndRenderRecords() {
        try {
            const response = await fetch('/api/records');
            if (!response.ok) {
                throw new Error('Failed to fetch records.');
            }
            const data = await response.json();
            const records = data;

            // Clear existing table body
            recordsTableBody.innerHTML = '';

            if (records.length === 0) {
                const row = document.createElement('tr');
                row.innerHTML = `<td colspan="4" class="text-center py-4 text-gray-500">No records found.</td>`;
                recordsTableBody.appendChild(row);
                return;
            }

            // Create a set of all unique keys to build a full header
            const allKeys = new Set();
            records.forEach(record => {
                Object.keys(record).forEach(key => allKeys.add(key));
            });

            // Rebuild the table header dynamically
            const tableHead = document.querySelector('#recordsTable thead tr');
            tableHead.innerHTML = `
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Index</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
            `;
            const dynamicKeys = Array.from(allKeys).filter(key => key !== 'name' && key !== 'date' && key !== 'index');
            dynamicKeys.sort(); // Sort dynamically added columns alphabetically
            dynamicKeys.forEach(key => {
                const th = document.createElement('th');
                th.className = "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider";
                th.textContent = key.charAt(0).toUpperCase() + key.slice(1);
                tableHead.insertBefore(th, tableHead.lastElementChild);
            });

            const actionsTh = document.createElement('th');
            actionsTh.className = "px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider";
            actionsTh.textContent = "Actions";
            tableHead.appendChild(actionsTh);

            // Render each record as a table row
            records.forEach((record, index) => {
                const row = document.createElement('tr');
                row.className = 'hover:bg-gray-50 transition-colors duration-200';

                // Add index and static columns
                let rowHtml = `
                    <td data-label="Index" class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${index}</td>
                    <td data-label="Name" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${record.name}</td>
                    <td data-label="Date" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${new Date(record.date).toLocaleString()}</td>
                `;

                // Add dynamic columns
                dynamicKeys.forEach(key => {
                    const value = record[key] === true ? 'Yes' : 'No';
                    rowHtml += `<td data-label="${key.charAt(0).toUpperCase() + key.slice(1)}" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${value}</td>`;
                });

                // Add actions button
                rowHtml += `
                    <td data-label="Actions" class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button class="remove-btn text-red-600 hover:text-red-900" data-index="${index}">Remove</button>
                    </td>
                `;

                row.innerHTML = rowHtml;
                recordsTableBody.appendChild(row);
            });
        } catch (error) {
            console.error('Error:', error);
            showStatus('Failed to load records. Please try again.', true);
        }
    }

    // Add event listener for form submission
    addRecordForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        const name = patientNameInput.value;
        const dateOption = document.querySelector('input[name="dateOption"]:checked').value;
        let recordDate;

        if (dateOption === 'current') {
            recordDate = new Date().toISOString();
        } else {
            const year = yearInput.value;
            const month = monthInput.value;
            const day = dayInput.value;
            const hour = hourInput.value || 0;
            const minute = minuteInput.value || 0;
            const second = secondInput.value || 0;

            try {
                recordDate = new Date(year, month - 1, day, hour, minute, second).toISOString();
            } catch (e) {
                showStatus('Invalid custom date. Please check your inputs.', true);
                return;
            }
        }

        const symptoms = symptomsInput.value.split(',').map(s => s.trim()).filter(s => s.length > 0);
        const hazards = hazardsInput.value.split(',').map(h => h.trim()).filter(h => h.length > 0);

        try {
            const response = await fetch('/api/add_record', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    date: recordDate,
                    symptoms: symptoms,
                    hazards: hazards
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Failed to add record.');
            }

            // Clear the form and update the table
            addRecordForm.reset();
            fetchAndRenderRecords();
            showStatus('Record added successfully!');
        } catch (error) {
            console.error('Error:', error);
            showStatus(error.message, true);
        }
    });

    // Event listener for view records button
    viewRecordsBtn.addEventListener('click', () => {
        fetchAndRenderRecords();
    });

    // Event listener for remove button (delegated to the table body)
    recordsTableBody.addEventListener('click', async (event) => {
        if (event.target.classList.contains('remove-btn')) {
            const index = event.target.dataset.index;
            try {
                const response = await fetch('/api/remove_record', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ index: parseInt(index) }),
                });

                if (!response.ok) {
                    throw new Error('Failed to remove record.');
                }

                fetchAndRenderRecords();
                showStatus('Record removed successfully!');
            } catch (error) {
                console.error('Error:', error);
                showStatus('Failed to remove record.', true);
            }
        }
    });

    // Event listener for delete all button
    deleteAllBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to delete all records? This cannot be undone.')) {
            try {
                const response = await fetch('/api/delete_all_records', {
                    method: 'POST'
                });

                if (!response.ok) {
                    throw new Error('Failed to delete all records.');
                }

                fetchAndRenderRecords();
                showStatus('All records have been deleted!');
            } catch (error) {
                console.error('Error:', error);
                showStatus('Failed to delete all records.', true);
            }
        }
    });

    // Initial load of records when the page loads
    fetchAndRenderRecords();
});
