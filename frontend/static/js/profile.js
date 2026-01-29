// API Base URL
const API_BASE = window.location.origin;

// State
let userProfile = {};
let medications = [];

// Check authentication
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '/signin';
        return false;
    }
    return token;
}

// API Headers
function getHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${checkAuth()}`
    };
}

// Get user initials
function getInitials(name, email) {
    if (name && name.trim()) {
        const parts = name.trim().split(' ');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
    }
    if (email) {
        return email.substring(0, 2).toUpperCase();
    }
    return 'U';
}

// Load user header info
function loadUserHeader() {
    const userEmail = localStorage.getItem('userEmail');
    const userName = localStorage.getItem('userName');
    
    if (userEmail) {
        document.getElementById('userEmail').textContent = userEmail;
        const displayName = userName || userEmail.split('@')[0];
        document.getElementById('userName').textContent = displayName;
        document.getElementById('userInitials').textContent = getInitials(displayName, userEmail);
    }
}

// Navigation handling
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.profile-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all
            navItems.forEach(nav => nav.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));
            
            // Add active class to clicked
            item.classList.add('active');
            const sectionId = item.getAttribute('data-section');
            document.getElementById(sectionId).classList.add('active');
        });
    });
}

// Load profile data
async function loadProfileData() {
    try {
        const response = await fetch(`${API_BASE}/api/profile`, {
            headers: getHeaders()
        });
        
        if (response.ok) {
            userProfile = await response.json();
            populateForm();
        }
    } catch (error) {
        console.error('Load profile error:', error);
    }
}

// Populate forms with existing data
function populateForm() {
    if (!userProfile) return;
    
    // Basic Info
    if (userProfile.basic_info) {
        const basic = userProfile.basic_info;
        document.getElementById('fullName').value = basic.full_name || '';
        document.getElementById('dateOfBirth').value = basic.date_of_birth || '';
        document.getElementById('gender').value = basic.gender || '';
        document.getElementById('bloodType').value = basic.blood_type || '';
        document.getElementById('height').value = basic.height || '';
        document.getElementById('weight').value = basic.weight || '';
        document.getElementById('phone').value = basic.phone || '';
    }
    
    // Medical History
    if (userProfile.medical_history) {
        const medical = userProfile.medical_history;
        
        // Chronic conditions checkboxes
        if (medical.chronic_conditions) {
            medical.chronic_conditions.forEach(condition => {
                const checkbox = document.querySelector(`input[name="chronicConditions"][value="${condition}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }
        
        document.getElementById('pastSurgeries').value = medical.past_surgeries || '';
        document.getElementById('familyHistory').value = medical.family_history || '';
        document.getElementById('otherConditions').value = medical.other_conditions || '';
    }
    
    // Allergies
    if (userProfile.allergies) {
        document.getElementById('drugAllergies').value = userProfile.allergies.drug_allergies || '';
        document.getElementById('foodAllergies').value = userProfile.allergies.food_allergies || '';
        document.getElementById('otherAllergies').value = userProfile.allergies.other_allergies || '';
    }
    
    // Lifestyle
    if (userProfile.lifestyle) {
        const lifestyle = userProfile.lifestyle;
        
        if (lifestyle.exercise_frequency) {
            const exerciseRadio = document.querySelector(`input[name="exerciseFrequency"][value="${lifestyle.exercise_frequency}"]`);
            if (exerciseRadio) exerciseRadio.checked = true;
        }
        
        if (lifestyle.smoking_status) {
            const smokingRadio = document.querySelector(`input[name="smokingStatus"][value="${lifestyle.smoking_status}"]`);
            if (smokingRadio) smokingRadio.checked = true;
        }
        
        if (lifestyle.alcohol_consumption) {
            const alcoholRadio = document.querySelector(`input[name="alcoholConsumption"][value="${lifestyle.alcohol_consumption}"]`);
            if (alcoholRadio) alcoholRadio.checked = true;
        }
        
        document.getElementById('sleepHours').value = lifestyle.sleep_hours || '';
        document.getElementById('dietType').value = lifestyle.diet_type || '';
        
        if (lifestyle.stress_level) {
            document.getElementById('stressLevel').value = lifestyle.stress_level;
            document.getElementById('stressLevelValue').textContent = lifestyle.stress_level;
        }
    }
    
    // Medications
    if (userProfile.medications) {
        medications = userProfile.medications;
        renderMedications();
    }
}

// Save Basic Info
async function saveBasicInfo(formData) {
    try {
        const response = await fetch(`${API_BASE}/api/profile/basic-info`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            alert('✅ Basic information saved successfully!');
            await loadProfileData();
        } else {
            const error = await response.json();
            alert(`❌ Failed to save: ${error.detail}`);
        }
    } catch (error) {
        console.error('Save error:', error);
        alert('❌ Failed to save. Please try again.');
    }
}

// Save Medical History
async function saveMedicalHistory(formData) {
    try {
        const response = await fetch(`${API_BASE}/api/profile/medical-history`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            alert('✅ Medical history saved successfully!');
            await loadProfileData();
        } else {
            const error = await response.json();
            alert(`❌ Failed to save: ${error.detail}`);
        }
    } catch (error) {
        console.error('Save error:', error);
        alert('❌ Failed to save. Please try again.');
    }
}

// Save Allergies
async function saveAllergies(formData) {
    try {
        const response = await fetch(`${API_BASE}/api/profile/allergies`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            alert('✅ Allergies saved successfully!');
            await loadProfileData();
        } else {
            const error = await response.json();
            alert(`❌ Failed to save: ${error.detail}`);
        }
    } catch (error) {
        console.error('Save error:', error);
        alert('❌ Failed to save. Please try again.');
    }
}

// Save Lifestyle
async function saveLifestyle(formData) {
    try {
        const response = await fetch(`${API_BASE}/api/profile/lifestyle`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            alert('✅ Lifestyle information saved successfully!');
            await loadProfileData();
        } else {
            const error = await response.json();
            alert(`❌ Failed to save: ${error.detail}`);
        }
    } catch (error) {
        console.error('Save error:', error);
        alert('❌ Failed to save. Please try again.');
    }
}

// Render Medications
function renderMedications() {
    const medicationsList = document.getElementById('medicationsList');
    
    if (!medications || medications.length === 0) {
        medicationsList.innerHTML = '<div class="empty-state">No medications added yet. Click "Add Medication" to get started.</div>';
        return;
    }
    
    medicationsList.innerHTML = medications.map((med, index) => `
        <div class="medication-item">
            <div class="medication-info">
                <h3>${med.medication_name}</h3>
                <p><strong>Dosage:</strong> ${med.dosage}</p>
                <p><strong>Frequency:</strong> ${med.frequency}</p>
                ${med.prescribed_for ? `<p><strong>For:</strong> ${med.prescribed_for}</p>` : ''}
            </div>
            <div class="medication-actions">
                <button onclick="deleteMedication(${index})">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
            </div>
        </div>
    `).join('');
}

// Add Medication
async function addMedication(formData) {
    try {
        const response = await fetch(`${API_BASE}/api/profile/medications`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            alert('✅ Medication added successfully!');
            await loadProfileData();
            document.getElementById('medicationsForm').style.display = 'none';
            document.getElementById('medicationsForm').reset();
        } else {
            const error = await response.json();
            alert(`❌ Failed to add: ${error.detail}`);
        }
    } catch (error) {
        console.error('Add medication error:', error);
        alert('❌ Failed to add medication. Please try again.');
    }
}

// Delete Medication
async function deleteMedication(index) {
    if (!confirm('Delete this medication?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/profile/medications/${index}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        
        if (response.ok) {
            await loadProfileData();
        } else {
            alert('❌ Failed to delete medication.');
        }
    } catch (error) {
        console.error('Delete medication error:', error);
    }
}

// Initialize forms
function initForms() {
    // Basic Info Form
    document.getElementById('basicInfoForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = {
            full_name: document.getElementById('fullName').value,
            date_of_birth: document.getElementById('dateOfBirth').value,
            gender: document.getElementById('gender').value,
            blood_type: document.getElementById('bloodType').value,
            height: parseInt(document.getElementById('height').value) || null,
            weight: parseInt(document.getElementById('weight').value) || null,
            phone: document.getElementById('phone').value
        };
        saveBasicInfo(formData);
    });
    
    // Medical History Form
    document.getElementById('medicalHistoryForm').addEventListener('submit', (e) => {
        e.preventDefault();
        
        const chronicConditions = Array.from(
            document.querySelectorAll('input[name="chronicConditions"]:checked')
        ).map(cb => cb.value);
        
        const formData = {
            chronic_conditions: chronicConditions,
            past_surgeries: document.getElementById('pastSurgeries').value,
            family_history: document.getElementById('familyHistory').value,
            other_conditions: document.getElementById('otherConditions').value
        };
        saveMedicalHistory(formData);
    });
    
    // Allergies Form
    document.getElementById('allergiesForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = {
            drug_allergies: document.getElementById('drugAllergies').value,
            food_allergies: document.getElementById('foodAllergies').value,
            other_allergies: document.getElementById('otherAllergies').value
        };
        saveAllergies(formData);
    });
    
    // Lifestyle Form
    document.getElementById('lifestyleForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = {
            exercise_frequency: document.querySelector('input[name="exerciseFrequency"]:checked')?.value || null,
            smoking_status: document.querySelector('input[name="smokingStatus"]:checked')?.value || null,
            alcohol_consumption: document.querySelector('input[name="alcoholConsumption"]:checked')?.value || null,
            sleep_hours: parseInt(document.getElementById('sleepHours').value) || null,
            diet_type: document.getElementById('dietType').value,
            stress_level: parseInt(document.getElementById('stressLevel').value)
        };
        saveLifestyle(formData);
    });
    
    // Medications Form
    document.getElementById('addMedicationBtn').addEventListener('click', () => {
        document.getElementById('medicationsForm').style.display = 'block';
    });
    
    document.getElementById('cancelMedicationBtn').addEventListener('click', () => {
        document.getElementById('medicationsForm').style.display = 'none';
        document.getElementById('medicationsForm').reset();
    });
    
    document.getElementById('medicationsForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = {
            medication_name: document.getElementById('medicationName').value,
            dosage: document.getElementById('dosage').value,
            frequency: document.getElementById('frequency').value,
            prescribed_for: document.getElementById('prescribedFor').value
        };
        addMedication(formData);
    });
    
    // Stress level slider
    document.getElementById('stressLevel').addEventListener('input', (e) => {
        document.getElementById('stressLevelValue').textContent = e.target.value;
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadUserHeader();
    initNavigation();
    initForms();
    loadProfileData();
});