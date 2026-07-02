const STORAGE_KEY = 'elderly-medicine-reminders-v1';
let reminders = loadReminders();

const form = document.getElementById('reminderForm');
const reminderList = document.getElementById('reminderList');
const trackerList = document.getElementById('trackerList');
const currentTimeEl = document.getElementById('currentTime');
const notifyButton = document.getElementById('notifyButton');
const modal = document.getElementById('modal');
const modalContent = document.getElementById('modalContent');
const closeModalButton = document.getElementById('closeModal');
const menuButtons = document.querySelectorAll('.menu-btn');
const sections = {
  home: document.getElementById('homeSection'),
  reminders: document.getElementById('remindersSection'),
  tracker: document.getElementById('trackerSection'),
  careInfo: document.getElementById('careInfoSection'),
  contacts: document.getElementById('contactsSection'),
};

function loadReminders() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Could not load reminders', error);
    return [];
  }
}

function saveReminders() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(reminders));
}

function formatTime(timeValue) {
  const [hours, minutes] = timeValue.split(':');
  const date = new Date();
  date.setHours(Number(hours));
  date.setMinutes(Number(minutes));
  return date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

function formatDate(dateValue) {
  if (!dateValue) return '';
  const [year, month, day] = dateValue.split('-');
  const date = new Date(Number(year), Number(month) - 1, Number(day));
  return date.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' });
}

function renderReminders() {
  if (!reminders.length) {
    reminderList.innerHTML = '<div class="empty-state">No reminders yet. Add one above.</div>';
    return;
  }

  reminderList.innerHTML = reminders
    .map(
      (reminder) => `
        <div class="reminder-item">
          <div>
            <strong>${reminder.name}</strong>
            <div class="reminder-meta">
              ${reminder.dosage} • ${formatTime(reminder.time)}
              ${reminder.instructions ? ` • ${reminder.instructions}` : ''}
              ${reminder.notes ? ` • ${reminder.notes}` : ''}
              ${reminder.refillDate ? ` • Refill: ${formatDate(reminder.refillDate)}` : ''}
              ${reminder.doctorInfo ? ` • ${reminder.doctorInfo}` : ''}
              ${reminder.frequency ? ` • Frequency: ${reminder.frequency}` : ''}
              ${reminder.quantityLeft ? ` • Qty left: ${reminder.quantityLeft}` : ''}
              ${reminder.purpose ? ` • For: ${reminder.purpose}` : ''}
              ${reminder.caregiver ? ` • Caregiver: ${reminder.caregiver}` : ''}
            </div>
          </div>
          <button class="delete-btn" data-id="${reminder.id}" type="button">Remove</button>
        </div>
      `
    )
    .join('');
}

function renderTracker() {
  if (!reminders.length) {
    trackerList.innerHTML = '<div class="empty-state">No reminders to track yet.</div>';
    return;
  }

  const today = new Date().toDateString();
  trackerList.innerHTML = reminders
    .map((reminder) => {
      const takenToday = reminder.lastTakenDate === today;
      return `
        <div class="tracker-item${takenToday ? ' taken' : ''}">
          <div>
            <strong>${reminder.name}</strong>
            <div class="reminder-meta">
              ${formatTime(reminder.time)}${reminder.frequency ? ` • ${reminder.frequency}` : ''}
            </div>
          </div>
          <button class="tracker-btn" data-id="${reminder.id}" type="button">
            ${takenToday ? 'Taken' : 'Mark taken'}
          </button>
        </div>
      `;
    })
    .join('');
}

function addReminder(event) {
  event.preventDefault();

  const reminder = {
    id: Date.now().toString(),
    name: document.getElementById('medName').value.trim(),
    dosage: document.getElementById('dosage').value.trim(),
    time: document.getElementById('reminderTime').value,
    notes: document.getElementById('notes').value.trim(),
    instructions: document.getElementById('instructions').value.trim(),
    refillDate: document.getElementById('refillDate').value,
    doctorInfo: document.getElementById('doctorInfo').value.trim(),
    frequency: document.getElementById('frequency').value.trim(),
    quantityLeft: document.getElementById('quantityLeft').value.trim(),
    purpose: document.getElementById('purpose').value.trim(),
    caregiver: document.getElementById('caregiver').value.trim(),
  };

  if (!reminder.name || !reminder.dosage || !reminder.time) {
    return;
  }

  reminders.push(reminder);
  reminders.sort((a, b) => a.time.localeCompare(b.time));
  saveReminders();
  renderReminders();
  renderTracker();
  form.reset();
}

function deleteReminder(id) {
  reminders = reminders.filter((item) => item.id !== id);
  saveReminders();
  renderReminders();
  renderTracker();
}

function markReminderTaken(id) {
  const today = new Date().toDateString();
  reminders = reminders.map((item) =>
    item.id === id ? { ...item, lastTakenDate: today } : item
  );
  saveReminders();
  renderTracker();
}

function updateClock() {
  currentTimeEl.textContent = new Date().toLocaleTimeString([], {
    hour: 'numeric',
    minute: '2-digit',
  });
}

function getCurrentTimeKey() {
  const now = new Date();
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
}

function showReminderModal(reminder) {
  modalContent.innerHTML = `
    <p><strong>${reminder.name}</strong></p>
    <p>${reminder.dosage}</p>
    <p>${reminder.notes || 'Take it now.'}</p>
  `;
  modal.classList.remove('hidden');

  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification('Medicine reminder', {
      body: `Time to take ${reminder.name} (${reminder.dosage}).`,
    });
  }
}

function checkReminders() {
  const now = new Date();
  const currentTimeKey = getCurrentTimeKey();
  const currentDateKey = now.toDateString();

  reminders.forEach((reminder) => {
    if (reminder.triggeredDate === currentDateKey && reminder.time === currentTimeKey) {
      return;
    }

    if (reminder.time === currentTimeKey) {
      reminder.triggeredDate = currentDateKey;
      saveReminders();
      showReminderModal(reminder);
    }
  });
}

async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    alert('Notifications are not supported in this browser.');
    return;
  }

  const permission = await Notification.requestPermission();
  if (permission === 'granted') {
    notifyButton.textContent = 'Notifications on';
  }
}

function initializeNotificationState() {
  if ('Notification' in window && Notification.permission === 'granted') {
    notifyButton.textContent = 'Notifications on';
  }
}

function showSection(target) {
  Object.entries(sections).forEach(([key, section]) => {
    section.classList.toggle('hidden', key !== target);
  });

  menuButtons.forEach((button) => {
    button.classList.toggle('active', button.dataset.target === target);
  });
}

form.addEventListener('submit', addReminder);
reminderList.addEventListener('click', (event) => {
  const button = event.target.closest('button[data-id]');
  if (!button) return;
  deleteReminder(button.getAttribute('data-id'));
});

trackerList.addEventListener('click', (event) => {
  const button = event.target.closest('.tracker-btn');
  if (!button) return;
  markReminderTaken(button.getAttribute('data-id'));
});

menuButtons.forEach((button) => {
  button.addEventListener('click', () => showSection(button.dataset.target));
});

notifyButton.addEventListener('click', requestNotificationPermission);
closeModalButton.addEventListener('click', () => modal.classList.add('hidden'));
modal.addEventListener('click', (event) => {
  if (event.target === modal) {
    modal.classList.add('hidden');
  }
});

showSection('home');
initializeNotificationState();
updateClock();
renderReminders();
renderTracker();
setInterval(updateClock, 1000);
setInterval(checkReminders, 1000);
