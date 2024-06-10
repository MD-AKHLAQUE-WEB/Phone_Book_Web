// Function to handle the delete action
function deleteSelected() {
    // Get all the selected checkboxes
    console.log("Delete button clicked");
    var checkboxes = document.querySelectorAll('input[name="selected_contacts"]:checked');

    // If no checkboxes are selected, show an alert
    if (checkboxes.length === 0) {
        alert("Please select contacts to delete.");
        return;
    }

    // Ask for confirmation before deleting
    if (confirm("Are you sure you want to delete the selected contacts?")) {
        // Create an array to store the IDs of selected contacts
        var selectedIds = [];
        
        // Loop through each selected checkbox and get the ID
        checkboxes.forEach(function(checkbox) {
            selectedIds.push(checkbox.value);
        });

        // Send an AJAX request to delete the selected contacts
        fetch('/delete_contacts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ids: selectedIds })
        })
        .then(function(response) {
            if (response.ok) {
                // Reload the page after successful deletion
                location.reload();
            } else {
                alert("Failed to delete contacts.");
            }
        })
        .catch(function(error) {
            console.error('Error:', error);
            alert("An error occurred while deleting contacts.");
        });
    }
}

// Event listener for the delete button
document.getElementById('delete-selected').addEventListener('click', deleteSelected);


// Function to handle opening the update modal
function openUpdateModal() {
    // Get all the selected rows from the table
    var selectedRows = document.querySelectorAll('input[name="selected_contacts"]:checked');

    // Check if any rows are selected
    if (selectedRows.length === 0) {
        alert("Please select contacts to update.");
        return;
    }

    // Clear the previous data in the modal
    var updateTableBody = document.getElementById('updateTableBody');
    updateTableBody.innerHTML = '';

    // Iterate over the selected rows
    selectedRows.forEach(function(row, index) {
        var rowData = row.parentNode.parentNode.childNodes; // Get the cells of the row        
        var slno = rowData[3].innerText;
        var name = rowData[5].innerText;
        var phone = rowData[7].innerText;
        var email = rowData[9].innerText;

        // Create input fields for each piece of data
        var html = `
            <tr>
                <td>${slno}</td>
                <td><input type="text" class="form-control" value="${name}" id="updateName${index}"></td>
                <td><input type="text" class="form-control" value="${phone}" id="updatePhone${index}"></td>
                <td><input type="text" class="form-control" value="${email}" id="updateEmail${index}"></td>
            </tr>
        `;

        // Append the input fields to the modal's table body
        updateTableBody.innerHTML += html;
    });

    // Open the update modal
    $('#updateModal').modal('show');
}



// Event listener for the "Update Selected" button
document.getElementById('update-selected').addEventListener('click', openUpdateModal);



// Function to handle updating the selected contacts
function updateSelected() {
    // Get all the selected rows from the table
    var selectedRows = document.querySelectorAll('input[name="selected_contacts"]:checked');    

    // Iterate over the selected rows
    selectedRows.forEach(function(row, index) {
        // Get the input fields from the modal for this row
        var nameInput = document.getElementById('updateName' + index);
        var phoneInput = document.getElementById('updatePhone' + index);
        var emailInput = document.getElementById('updateEmail' + index);

        // Check if any of the input fields are empty
        if (nameInput.value.trim() === '' || phoneInput.value.trim() === '' || emailInput.value.trim() === '') {
            alert("Please fill in all fields.");
            return; // Stop further execution
        }

        // Get the ID of the contact from the checkbox value
        var contactId = row.value;

        // Get the updated data for this contact
        var updatedContact = {
            name: nameInput.value.trim(),
            phone: phoneInput.value.trim(),
            email: emailInput.value.trim()
        };

        // Send an AJAX request to update the contact data in Firestore
        fetch('/update_contact/' + contactId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updatedContact)
        })
        .then(function(response) {
            if (response.ok) {
                // Reload the page after successful update of all contacts
                if (index === selectedRows.length - 1) {
                    location.reload();
                }
            } else {
                alert("Failed to update contacts.");
            }
        })
        .catch(function(error) {
            console.error('Error:', error);
            alert("An error occurred while updating contacts.");
        });
    });
}





// Event listener for the "Confirm" button in the update modal
document.getElementById('confirm-update').addEventListener('click', updateSelected);



