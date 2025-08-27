// A simple script to handle UI interactions and API calls for the symptom tracker app.

document.addEventListener('DOMContentLoaded', () => {
    // Get all necessary DOM elements
    const addRecordForm = document.getElementById('add-record-form');
    const dateTypeSelect = document.getElementById('date-type');
    const customDateFields = document.getElementById('custom-date-fields');
    const viewRecordsButton = document.getElementById('view-records');
    const deleteAllRecordsButton = document.getElementById('delete-all-records');
    const recordsTableContainer = document.getElementById('records-table-container');
    const recordsPlaceholder = document.getElementById('records-placeholder');
    const addStatusSpan = document.getElementById('add-status');

    // Show/hide custom date input based on dropdown selection
    dateTypeSelect.addEventListener('change', (event) => {
        if (event.target.value === 'custom') {
            customDateFields.classList.remove('hidden');
        } else {
            customDateFields.classList.add('hidden');
        }
    });

    // Handle form submission for adding a new record
    addRecordForm.addEventListener('submit', async (event) => {
        event.preventDefault();

        // Collect data from the form
        const name = document.getElementById('name').value;
        const dateType = document.getElementById('date-type').value;
        const customDate = document.getElementById('custom-date').value;
        const symptoms = document.getElementById('symptoms').value.split(',').map(s => s.trim()).filter(s => s !== '');
        const hazards = document.getElementById('hazards').value.split(',').map(h => h.trim()).filter(h => h !== '');

        let date;
        if (dateType === 'current') {
            date = new Date().toISOString();
        } else {
            date = new Date(customDate).toISOString();
        }

        // Use URLSearchParams to build the query string for the fetch request
        const params = new URLSearchParams();
        params.append('name', name);
        params.append('date', date);
        params.append('symptoms', JSON.stringify(symptoms)); // Convert array to JSON string
        params.append('hazards', JSON.stringify(hazards)); // Convert array to JSON string

        try {
            // Make the fetch call to the FastAPI endpoint
            const response = await fetch(`/add_record?${params.toString()}`, {
                method: 'POST',
            });
            if (response.ok) {
                console.log("Record added successfully.");
                addStatusSpan.classList.remove('hidden');
                setTimeout(() => addStatusSpan.classList.add('hidden'), 3000);
                addRecordForm.reset(); // Reset form fields
                viewRecords(); // Refresh the table to show the new record
            } else {
                console.error("Failed to add record.");
            }
        } catch (error) {
            console.error("Error adding record:", error);
        }
    });

    // Handle the View All Records button click
    viewRecordsButton.addEventListener('click', () => {
        viewRecords();
    });

    // Handle the Delete All Records button click
    deleteAllRecordsButton.addEventListener('click', async () => {
        const confirmed = confirm("Are you sure you want to delete all records? This action cannot be undone.");
        if (confirmed) {
            try {
                const response = await fetch('/delete_all_records', {
                    method: 'POST',
                });
                if (response.ok) {
                    console.log("All records deleted.");
                    viewRecords(); // Refresh the table to show it's empty
                } else {
                    console.error("Failed to delete all records.");
                }
            } catch (error) {
                console.error("Error deleting all records:", error);
            }
        }
    });

    // Function to fetch and display records
    async function viewRecords() {
        try {
            // Because the view_records() function in main.py prints to the console,
            // we will need an API endpoint to return the records to the UI.
            // A new endpoint needs to be added to app.py. Let's assume a GET endpoint exists
            // that returns a JSON representation of the DataFrame.
            const response = await fetch('/view_records'); // Assume this new endpoint exists
            if (response.ok) {
                const records = await response.json();
                renderRecordsTable(records);
            } else {
                // If the endpoint doesn't exist, we'll log an error and show a message
                console.warn("'/view_records' endpoint not found. Cannot display records in the UI. Please add a GET endpoint in app.py that returns the dataframe data.");
                recordsPlaceholder.textContent = "Records cannot be viewed. Please update app.py with a '/view_records' endpoint that returns JSON data.";
                recordsTableContainer.innerHTML = ''; // Clear any old table
            }
        } catch (error) {
            console.error("Error fetching records:", error);
        }
    }

    // Function to dynamically create and populate the records table
    function renderRecordsTable(records) {
        if (!records || records.length === 0) {
            recordsPlaceholder.textContent = "No records to display.";
            recordsTableContainer.innerHTML = '';
            return;
        }

        recordsPlaceholder.classList.add('hidden');
        let tableHTML = `<table class="records-table w-full border-collapse"><thead><tr><th>Index</th><th>Name</th><th>Date</th>`;

        // Dynamically add symptom and hazard columns
        const allKeys = new Set();
        records.forEach(record => {
            Object.keys(record).forEach(key => allKeys.add(key));
        });

        const excludedKeys = new Set(['name', 'date', 'index']);
        const dynamicHeaders = Array.from(allKeys).filter(key => !excludedKeys.has(key)).sort();
        dynamicHeaders.forEach(key => {
            tableHTML += `<th>${key.charAt(0).toUpperCase() + key.slice(1)}</th>`;
        });

        tableHTML += `<th>Actions</th></tr></thead><tbody>`;

        // Populate table rows
        records.forEach((record, index) => {
            tableHTML += `<tr class="hover:bg-gray-50"><td>${index}</td><td>${record.name}</td><td>${new Date(record.date).toLocaleString()}</td>`;

            dynamicHeaders.forEach(key => {
                const cellValue = record[key] ? '✅' : '❌';
                tableHTML += `<td>${cellValue}</td>`;
            });

            tableHTML += `<td><button class="remove-record-btn bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded text-sm" data-index="${index}">Remove</button></td></tr>`;
        });

        tableHTML += `</tbody></table>`;
        recordsTableContainer.innerHTML = tableHTML;

        // Add event listeners to dynamically created 'Remove' buttons
        document.querySelectorAll('.remove-record-btn').forEach(button => {
            button.addEventListener('click', async (event) => {
                const index = event.target.dataset.index;
                try {
                    const response = await fetch(`/remove_record?idx=${index}`, {
                        method: 'POST',
                    });
                    if (response.ok) {
                        console.log(`Record at index ${index} removed.`);
                        viewRecords(); // Refresh the table
                    } else {
                        console.error(`Failed to remove record at index ${index}.`);
                    }
                } catch (error) {
                    console.error("Error removing record:", error);
                }
            });
        });
    }

    // Initial load: view records to show current state
    viewRecords();
});
