import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Medication Reminder",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .reminder-card {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
        margin: 10px 0;
    }
    .reminder-card.taken {
        background-color: #e8f5e9;
        border-left-color: #2e7d32;
    }
    .warning-card {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
    }
    .contact-card {
        background-color: #fff9c4;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Data storage file
STORAGE_FILE = Path('medication_data.json')

def load_reminders():
    """Load reminders from storage file."""
    if STORAGE_FILE.exists():
        try:
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_reminders(reminders):
    """Save reminders to storage file."""
    with open(STORAGE_FILE, 'w') as f:
        json.dump(reminders, f, indent=2, default=str)

def generate_id():
    """Generate unique ID for reminders."""
    return int(datetime.now().timestamp() * 1000)

def format_time(time_obj):
    """Format time object to readable string."""
    if isinstance(time_obj, str):
        return time_obj
    return time_obj.strftime("%I:%M %p") if time_obj else "N/A"

def is_medicine_due(reminder, current_time):
    """Check if medicine is due now."""
    try:
        reminder_time = datetime.strptime(reminder['time'], "%H:%M").time()
        return reminder_time.hour == current_time.hour
    except:
        return False

# Initialize session state
if 'reminders' not in st.session_state:
    st.session_state.reminders = load_reminders()

if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Home"

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("💊 Medication Reminder")
    st.markdown("Simple and clear reminders for daily medicine.")

with col2:
    current_time = datetime.now()
    st.metric("Current Time", current_time.strftime("%I:%M %p"))

# Navigation tabs
tabs = st.tabs(["🏠 Home", "💬 Reminders", "📊 Tracker", "📋 Care Info", "☎️ Contacts"])

# ==================== HOME TAB ====================
with tabs[0]:
    st.header("Welcome")
    st.markdown("""
    Use this menu to view reminders, helpful care details, and emergency contacts in one place.
    
    **Features:**
    - 📝 Add and manage medication reminders
    - 🔔 Set specific times and frequencies
    - ✅ Track when you've taken your medicine
    - 📞 Store important emergency contacts
    - 💬 Keep care instructions and notes
    """)
    
    # Check for overdue medicines
    current_time = datetime.now()
    overdue = []
    for reminder in st.session_state.reminders:
        if is_medicine_due(reminder, current_time) and not reminder.get('lastTakenDate') == current_time.strftime("%Y-%m-%d"):
            overdue.append(reminder)
    
    if overdue:
        st.warning(f"⏰ **{len(overdue)} medicine(s) due now!**")
        for med in overdue:
            st.info(f"💊 **{med['name']}** - {med['dosage']} at {med['time']}")

# ==================== REMINDERS TAB ====================
with tabs[1]:
    st.header("Medication Reminders")
    
    # Form to add new reminder
    with st.form("reminder_form"):
        st.subheader("Add New Reminder")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            med_name = st.text_input("Medicine Name", placeholder="e.g., Aspirin")
            med_time = st.time_input("Time to take", value=datetime.now().time())
        
        with col2:
            dosage = st.text_input("Dosage", placeholder="e.g., 1 tablet, 500mg")
            frequency = st.selectbox("Frequency", ["Daily", "Twice daily", "Three times daily", "Every other day", "Weekly"])
        
        with col3:
            instructions = st.text_input("Instructions", placeholder="e.g., With food, Before bed")
            purpose = st.text_input("Purpose/Condition", placeholder="e.g., Pain relief, Blood pressure")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            notes = st.text_area("Additional Notes", height=60)
            refill_date = st.date_input("Refill Date (optional)", value=None)
        
        with col2:
            doctor_info = st.text_input("Doctor Info", placeholder="e.g., Dr. Smith")
            quantity_left = st.number_input("Quantity Left", min_value=0, step=1)
        
        with col3:
            caregiver = st.text_input("Caregiver Name", placeholder="Who helps you?")
        
        if st.form_submit_button("➕ Add Reminder", use_container_width=True):
            if med_name and med_time:
                new_reminder = {
                    'id': generate_id(),
                    'name': med_name,
                    'time': med_time.strftime("%H:%M"),
                    'dosage': dosage,
                    'frequency': frequency,
                    'instructions': instructions,
                    'purpose': purpose,
                    'notes': notes,
                    'refillDate': str(refill_date) if refill_date else None,
                    'doctorInfo': doctor_info,
                    'quantityLeft': int(quantity_left) if quantity_left else None,
                    'caregiver': caregiver,
                    'lastTakenDate': None
                }
                st.session_state.reminders.append(new_reminder)
                save_reminders(st.session_state.reminders)
                st.success(f"✅ {med_name} reminder added!")
                st.rerun()
            else:
                st.error("Please fill in at least the Medicine Name and Time")
    
    st.divider()
    
    # Display reminders
    st.subheader("Your Reminders")
    if not st.session_state.reminders:
        st.info("No reminders yet. Add one above!")
    else:
        for idx, reminder in enumerate(st.session_state.reminders):
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"### {reminder['name']}")
                    details = []
                    details.append(f"⏰ {reminder['time']}")
                    if reminder['dosage']:
                        details.append(f"📏 {reminder['dosage']}")
                    if reminder['frequency']:
                        details.append(f"📅 {reminder['frequency']}")
                    if reminder['purpose']:
                        details.append(f"🎯 For: {reminder['purpose']}")
                    if reminder['instructions']:
                        details.append(f"📝 {reminder['instructions']}")
                    if reminder['notes']:
                        details.append(f"📌 {reminder['notes']}")
                    if reminder['doctorInfo']:
                        details.append(f"👨‍⚕️ {reminder['doctorInfo']}")
                    if reminder['quantityLeft'] is not None:
                        details.append(f"📦 Qty left: {reminder['quantityLeft']}")
                    if reminder['refillDate']:
                        details.append(f"🔄 Refill: {reminder['refillDate']}")
                    if reminder['caregiver']:
                        details.append(f"👥 Caregiver: {reminder['caregiver']}")
                    
                    st.caption(" • ".join(details))
                
                with col2:
                    if st.button("🗑️ Remove", key=f"delete_{reminder['id']}", use_container_width=True):
                        st.session_state.reminders.pop(idx)
                        save_reminders(st.session_state.reminders)
                        st.success("Removed!")
                        st.rerun()

# ==================== TRACKER TAB ====================
with tabs[2]:
    st.header("Medicine Tracker")
    st.markdown("Mark when you've taken your medicine today")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    if not st.session_state.reminders:
        st.info("No reminders to track yet.")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            for reminder in st.session_state.reminders:
                taken_today = reminder.get('lastTakenDate') == today
                
                with st.container(border=True):
                    st.markdown(f"### {reminder['name']}")
                    st.caption(f"⏰ {reminder['time']} • {reminder.get('dosage', 'N/A')}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(
                            "✅ Taken" if taken_today else "Mark Taken",
                            key=f"taken_{reminder['id']}",
                            use_container_width=True,
                            disabled=taken_today
                        ):
                            reminder['lastTakenDate'] = today
                            save_reminders(st.session_state.reminders)
                            st.success(f"Great! {reminder['name']} marked as taken.")
                            st.rerun()
                    
                    with col_b:
                        if taken_today:
                            st.caption("✅ Taken today")
                        else:
                            st.caption("⏳ Not taken yet")
        
        with col2:
            st.subheader("Today's Summary")
            total = len(st.session_state.reminders)
            taken = sum(1 for r in st.session_state.reminders if r.get('lastTakenDate') == today)
            
            st.metric("Medicines", total)
            st.metric("Taken Today", taken)
            
            if total > 0:
                progress = taken / total
                st.progress(progress, text=f"{int(progress * 100)}% Complete")
            
            if taken == total and total > 0:
                st.success("🎉 Great job! All medicines taken today!")

# ==================== CARE INFO TAB ====================
with tabs[3]:
    st.header("Care Information")
    
    st.subheader("📋 General Care Tips")
    st.markdown("""
    **Taking Your Medicine Safely:**
    - Always take your medicine at the same time each day
    - Keep your medicines in a cool, dry place away from sunlight
    - Never skip doses without consulting your doctor
    - Keep a list of all your medicines and bring it to doctor visits
    - Report any side effects to your doctor immediately
    
    **Storage Tips:**
    - Store medicines in original containers with labels
    - Keep away from moisture and extreme temperatures
    - Never store medicines in the bathroom
    - Keep out of reach of children and pets
    
    **When to Call Your Doctor:**
    - If you experience unusual side effects
    - If you feel no improvement
    - If you miss several doses
    - If you develop allergic reactions
    """)
    
    st.subheader("🍽️ Food & Medicine Interactions")
    st.markdown("""
    Some medicines should be taken with food, others on an empty stomach. 
    Always check the label or ask your pharmacist about:
    - What to eat or avoid with your medicine
    - When to take it relative to meals
    - Which beverages are safe (avoid grapefruit juice with many medicines)
    """)
    
    st.subheader("⚠️ Medication Side Effects")
    st.markdown("""
    Common mild side effects may include:
    - Nausea or upset stomach
    - Headache or dizziness
    - Sleepiness or insomnia
    
    **Seek immediate medical help if you experience:**
    - Severe allergic reactions
    - Chest pain or difficulty breathing
    - Severe headaches or vision changes
    - Uncontrolled bleeding
    """)

# ==================== CONTACTS TAB ====================
with tabs[4]:
    st.header("Emergency Contacts")
    
    contacts_file = Path('contacts.json')
    
    # Load existing contacts
    if contacts_file.exists():
        try:
            contacts = json.load(open(contacts_file))
        except:
            contacts = {}
    else:
        contacts = {}
    
    # Display contacts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📞 Your Contacts")
        
        default_contacts = {
            'doctor': {'name': 'Primary Care Doctor', 'phone': ''},
            'pharmacy': {'name': 'Pharmacy', 'phone': ''},
            'emergency': {'name': 'Emergency (911)', 'phone': '911'},
            'caregiver': {'name': 'Caregiver', 'phone': ''},
            'hospital': {'name': 'Nearest Hospital', 'phone': ''},
            'poison_control': {'name': 'Poison Control', 'phone': '1-800-222-1222'}
        }
        
        for key, default_info in default_contacts.items():
            if key not in contacts:
                contacts[key] = default_info
        
        for key, contact in contacts.items():
            with st.container(border=True):
                st.markdown(f"### {contact['name']}")
                if contact['phone']:
                    st.caption(f"📱 {contact['phone']}")
                    st.button(f"Call {contact['name']}", key=f"call_{key}", disabled=True)
                else:
                    st.caption("Phone number not set")
    
    with col2:
        st.subheader("✏️ Edit Contacts")
        
        with st.form("contacts_form"):
            st.markdown("Update your important contact information:")
            
            doctor_name = st.text_input("Doctor Name", value=contacts.get('doctor', {}).get('name', ''))
            doctor_phone = st.text_input("Doctor Phone", value=contacts.get('doctor', {}).get('phone', ''))
            
            pharmacy_name = st.text_input("Pharmacy Name", value=contacts.get('pharmacy', {}).get('name', ''))
            pharmacy_phone = st.text_input("Pharmacy Phone", value=contacts.get('pharmacy', {}).get('phone', ''))
            
            caregiver_name = st.text_input("Caregiver Name", value=contacts.get('caregiver', {}).get('name', ''))
            caregiver_phone = st.text_input("Caregiver Phone", value=contacts.get('caregiver', {}).get('phone', ''))
            
            hospital_name = st.text_input("Hospital Name", value=contacts.get('hospital', {}).get('name', ''))
            hospital_phone = st.text_input("Hospital Phone", value=contacts.get('hospital', {}).get('phone', ''))
            
            if st.form_submit_button("💾 Save Contacts", use_container_width=True):
                contacts_data = {
                    'doctor': {'name': doctor_name, 'phone': doctor_phone},
                    'pharmacy': {'name': pharmacy_name, 'phone': pharmacy_phone},
                    'caregiver': {'name': caregiver_name, 'phone': caregiver_phone},
                    'hospital': {'name': hospital_name, 'phone': hospital_phone},
                    'emergency': contacts.get('emergency', {'name': 'Emergency (911)', 'phone': '911'}),
                    'poison_control': contacts.get('poison_control', {'name': 'Poison Control', 'phone': '1-800-222-1222'})
                }
                
                with open(contacts_file, 'w') as f:
                    json.dump(contacts_data, f, indent=2)
                
                st.success("✅ Contacts saved!")
                st.rerun()

# Sidebar with quick info
with st.sidebar:
    st.markdown("---")
    st.subheader("📊 Quick Stats")
    total_reminders = len(st.session_state.reminders)
    today = datetime.now().strftime("%Y-%m-%d")
    taken_today = sum(1 for r in st.session_state.reminders if r.get('lastTakenDate') == today)
    
    st.metric("Total Reminders", total_reminders)
    st.metric("Taken Today", taken_today)
    
    st.markdown("---")
    st.markdown("**💡 Tip:** Set reminders for consistent times each day for best results.")
