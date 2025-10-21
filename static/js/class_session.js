// static/js/class_session.js - minimal class session logic
let CURRENT_SECTION = null;
let SESSION_STARTED = false;

// Load available sections on page load
window.addEventListener('DOMContentLoaded', async () => {
  await loadSections();
});

async function loadSections() {
  try {
    const res = await fetch('/api/available_sections', { cache: 'no-store' });
    const data = await res.json();
    const sel = document.getElementById('inpSection');
    sel.innerHTML = '';
    (data.sections || []).forEach(sec => {
      const opt = document.createElement('option');
      opt.value = sec; opt.textContent = sec;
      sel.appendChild(opt);
    });
  } catch (e) {}
}

async function startClassSession() {
  const subject = document.getElementById('inpSubject').value.trim();
  const section = document.getElementById('inpSection').value.trim();
  const start = document.getElementById('inpStart').value;
  const end = document.getElementById('inpEnd').value;

  if (!subject || !section) {
    alert('Enter Subject and Section');
    return;
  }
  CURRENT_SECTION = section;

  const res = await fetch('/api/start_class_session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ subject, section, class_start: start, class_end: end })
  });
  const data = await res.json();
  if (!data.success) {
    alert(data.message || 'Failed to start session');
    return;
  }

  // Hide setup, show controls
  document.getElementById('setupBox').style.display = 'none';
  document.getElementById('sessionBox').style.display = 'flex';
  document.getElementById('sessionMeta').style.display = 'block';
  document.getElementById('statusBox').style.display = 'flex';
  document.getElementById('sessionMeta').textContent = `Subject: ${subject} | Section: ${section} | ${start || '—'} - ${end || '—'}`;
  document.getElementById('sessionInfo').textContent = `${subject} - ${section}`;

  SESSION_STARTED = true;
  
  // Clear old data immediately
  document.getElementById('waitingList').innerHTML = '';
  document.getElementById('presentList').innerHTML = '';
  document.getElementById('lastScan').textContent = '—';
  document.getElementById('statTotal').textContent = '0';
  document.getElementById('statPresent').textContent = '0';
  document.getElementById('statAbsent').textContent = '0';
  
  // Prime lists with fresh data
  await refreshLists();

  // Start polling
  setInterval(refreshLists, 2000);
}

async function refreshLists() {
  if (!SESSION_STARTED || !CURRENT_SECTION) return;
  try {
    const res = await fetch(`/api/session_lists?section=${encodeURIComponent(CURRENT_SECTION)}`, { cache: 'no-store' });
    const data = await res.json();

    // Update stats
    document.getElementById('statTotal').textContent = data.total;
    document.getElementById('statPresent').textContent = data.present;
    document.getElementById('statAbsent').textContent = data.absent;

    // Update last scan
    if (data.last_scan && data.last_scan.name) {
      document.getElementById('lastScan').textContent = data.last_scan.name;
    }

    // Render waiting
    const waiting = document.getElementById('waitingList');
    waiting.innerHTML = '';
    data.waiting.forEach(s => {
      const row = document.createElement('div');
      row.className = 'item';
      row.innerHTML = `<div>${s.name}</div><div class="muted">${s.roll_no || ''}</div>`;
      waiting.appendChild(row);
    });

    // Render present
    const present = document.getElementById('presentList');
    present.innerHTML = '';
    data.present_list.forEach(s => {
      const row = document.createElement('div');
      row.className = 'item';
      row.innerHTML = `<div>${s.name}</div><div class="muted">${s.time || ''}</div>`;
      present.appendChild(row);
    });
  } catch (e) {
    // ignore
  }
}

async function resetSession() {
  if (!SESSION_STARTED) {
    alert('No session started');
    return;
  }

  // Confirm reset
  if (!confirm('Reset session? This will mark all students as ABSENT.')) {
    return;
  }

  // Disable button during processing
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = 'Resetting...';

  try {
    const res = await fetch('/api/reset_session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();

    if (data.success) {
      alert('Session reset! All students are now absent.');
      
      // Refresh UI
      await refreshLists();
    } else {
      alert('Error: ' + (data.message || 'Unknown error'));
    }
  } catch (e) {
    alert('Failed to reset session: ' + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Reset Session';
  }
}

async function stopSession() {
  if (!SESSION_STARTED) {
    alert('No session started');
    return;
  }

  // Confirm stop
  if (!confirm('Stop session and export PDF?')) {
    return;
  }

  // Disable button during processing
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = 'Processing...';

  try {
    const res = await fetch('/api/stop_session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();

    if (data.success) {
      // Show success and PDF info
      alert(`Session stopped successfully!\n\nStats:\nTotal: ${data.stats.total}\nPresent: ${data.stats.present}\nAbsent: ${data.stats.absent}\n\nPDF: ${data.pdf_file}`);

      // Reset UI
      SESSION_STARTED = false;
      document.getElementById('setupBox').style.display = 'flex';
      document.getElementById('sessionBox').style.display = 'none';
      document.getElementById('sessionMeta').style.display = 'none';
      document.getElementById('statusBox').style.display = 'none';
      document.getElementById('waitingList').innerHTML = '';
      document.getElementById('presentList').innerHTML = '';
      document.getElementById('lastScan').textContent = '—';
      document.getElementById('statTotal').textContent = '0';
      document.getElementById('statPresent').textContent = '0';
      document.getElementById('statAbsent').textContent = '0';
    } else {
      alert('Error: ' + (data.message || 'Unknown error'));
    }
  } catch (e) {
    alert('Failed to stop session: ' + e.message);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Stop Session & Export PDF';
  }
}
