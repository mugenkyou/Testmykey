const form = document.getElementById('verifyForm');
const button = document.getElementById('verifyButton');
const result = document.getElementById('result');
const serviceSelect = document.getElementById('service');

// Service-specific field requirements
const serviceFields = {
    twitter: ['api_secret'],
    spotify: ['client_secret'],
    azure: ['client_secret', 'tenant_id'],
    supabase: ['supabase_url']
};

// Show/hide additional fields based on service selection
serviceSelect.addEventListener('change', () => {
    // Hide all additional fields first
    document.querySelectorAll('.additional-fields').forEach(fields => {
        fields.style.display = 'none';
    });

    // Show fields for selected service
    const service = serviceSelect.value;
    if (service in serviceFields) {
        const fieldsDiv = document.getElementById(`${service}-fields`);
        if (fieldsDiv) {
            fieldsDiv.style.display = 'block';
        }
    }
});

function getResultClass(status) {
    return status === 'valid' ? 'success' : 'error';
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData(form);
    button.disabled = true;
    button.innerHTML = '<span class="loading"></span>Verifying...';
    result.style.display = 'none';

    try {
        const response = await fetch('/verify', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        result.style.display = 'block';
        result.className = getResultClass(data.status);
        result.textContent = data.status === 'valid' ? 'API Key Active' : 'API Key Inactive';
    } catch (error) {
        result.style.display = 'block';
        result.className = 'error';
        result.textContent = 'API Key Invalid';
    } finally {
        button.disabled = false;
        button.innerHTML = 'Verify API Key';
    }
}); 