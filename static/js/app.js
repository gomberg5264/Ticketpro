document.addEventListener('DOMContentLoaded', () => {
    const ticketForm = document.getElementById('ticket-form');
    const ticketList = document.getElementById('ticket-list');
    const clearTicketsBtn = document.getElementById('clear-tickets');

    if (ticketForm) {
        ticketForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(ticketForm);
            const ticketData = {
                title: formData.get('title'),
                description: formData.get('description'),
                priority: formData.get('priority')
            };

            try {
                console.log('Submitting ticket:', ticketData);
                const response = await fetch('/submit_ticket', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(ticketData)
                });
                const result = await response.json();
                if (response.ok) {
                    console.log('Ticket submitted successfully:', result);
                    location.reload();
                } else {
                    console.error('Error submitting ticket:', result.error);
                    alert(`Error: ${result.error}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while submitting the ticket');
            }
        });
    }

    if (ticketList) {
        ticketList.addEventListener('click', async (e) => {
            if (e.target.classList.contains('close-ticket')) {
                const ticketId = e.target.dataset.ticketId;
                try {
                    console.log('Closing ticket:', ticketId);
                    const response = await fetch(`/close_ticket/${ticketId}`, {
                        method: 'POST'
                    });
                    const result = await response.json();
                    if (response.ok) {
                        console.log('Ticket closed successfully:', result);
                        location.reload();
                    } else {
                        console.error('Error closing ticket:', result.error);
                        alert(`Error: ${result.error}`);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('An error occurred while closing the ticket');
                }
            }
        });
    }

    if (clearTicketsBtn) {
        clearTicketsBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to clear all tickets?')) {
                try {
                    console.log('Clearing all tickets');
                    const response = await fetch('/clear_tickets', {
                        method: 'POST'
                    });
                    const result = await response.json();
                    if (response.ok) {
                        console.log('All tickets cleared successfully:', result);
                        location.reload();
                    } else {
                        console.error('Error clearing tickets:', result.error);
                        alert(`Error: ${result.error}`);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('An error occurred while clearing tickets');
                }
            }
        });
    }
});
