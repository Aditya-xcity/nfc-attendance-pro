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
  
  // Show reports section
  document.getElementById('reportsSection').style.display = 'block';
  await refreshReportsList();
  
  // Initialize camera
  await initializeCamera();
  
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

    // Update last scan and capture photo
    if (data.last_scan && data.last_scan.name) {
      document.getElementById('lastScan').textContent = data.last_scan.name;
      // Capture photo for the scanned student
      capturePhotoForStudent(data.last_scan.name);
    }

    // Store full data for drag operations
    window.currentWaiting = data.waiting;
    window.currentPresent = data.present_list;

    // Render waiting
    const waiting = document.getElementById('waitingList');
    waiting.innerHTML = '';
    data.waiting.forEach((s, idx) => {
      const row = document.createElement('div');
      row.className = 'item';
      row.draggable = true;
      row.dataset.index = idx;
      row.dataset.name = s.name;
      row.dataset.rollNo = s.roll_no || '';
      row.dataset.type = 'waiting';
      row.innerHTML = `<div>${s.name}</div><div class="muted">${s.roll_no || ''}</div>`;
      
      // Drag events
      row.addEventListener('dragstart', handleDragStart);
      row.addEventListener('dragend', handleDragEnd);
      
      waiting.appendChild(row);
    });

    // Make present list a drop zone
    const presentList = document.getElementById('presentList');
    presentList.addEventListener('dragover', handleDragOver);
    presentList.addEventListener('drop', handleDrop);
    presentList.addEventListener('dragleave', handleDragLeave);

    // Render present
    const present = document.getElementById('presentList');
    present.innerHTML = '';
    data.present_list.forEach(s => {
      const row = document.createElement('div');
      row.className = 'item';
      row.draggable = true;
      row.dataset.name = s.name;
      row.dataset.time = s.time || '';
      row.dataset.type = 'present';
      row.innerHTML = `<div>${s.name}</div><div class="muted">${s.time || ''}</div>`;
      
      // Drag events
      row.addEventListener('dragstart', handleDragStart);
      row.addEventListener('dragend', handleDragEnd);
      
      present.appendChild(row);
    });
    
    // Make waiting list a drop zone (for removing from present)
    const waitingList = document.getElementById('waitingList');
    waitingList.addEventListener('dragover', handleDragOver);
    waitingList.addEventListener('drop', handleDrop);
    waitingList.addEventListener('dragleave', handleDragLeave);
  } catch (e) {
    // ignore
  }
}

let draggedElement = null;

function handleDragStart(e) {
  draggedElement = this;
  e.dataTransfer.effectAllowed = 'move';
  e.dataTransfer.setData('text/html', this.innerHTML);
  this.style.opacity = '0.5';
}

function handleDragEnd(e) {
  this.style.opacity = '1';
  const presentList = document.getElementById('presentList');
  presentList.style.background = '';
}

function handleDragOver(e) {
  if (e.preventDefault) {
    e.preventDefault();
  }
  e.dataTransfer.dropEffect = 'move';
  this.style.background = '#1a3a2e';
  return false;
}

function handleDragLeave(e) {
  this.style.background = '';
}

async function handleDrop(e) {
  if (e.stopPropagation) {
    e.stopPropagation();
  }
  
  this.style.background = '';
  
  if (!draggedElement) return;
  
  const name = draggedElement.dataset.name;
  const rollNo = draggedElement.dataset.rollNo;
  const draggedType = draggedElement.dataset.type;
  const dropZone = this.id;
  
  if (!name) return;
  
  // Determine action based on drag direction
  const isLeftToRight = dropZone === 'presentList' && draggedType === 'waiting';
  const isRightToLeft = dropZone === 'waitingList' && draggedType === 'present';
  
  if (!isLeftToRight && !isRightToLeft) return;
  
  // Call appropriate API
  const apiEndpoint = isLeftToRight ? '/api/mark_present_manual' : '/api/remove_attendance';
  
  try {
    const res = await fetch(apiEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        section: CURRENT_SECTION,
        name: name,
        roll_no: rollNo
      })
    });
    
    const data = await res.json();
    
    if (data.success) {
      // Refresh lists immediately
      await refreshLists();
      
      // Show action message
      const action = isLeftToRight ? 'marked as present' : 'removed from attendance';
      console.log(`${name} ${action}`);
    } else {
      alert('Error: ' + (data.message || 'Operation failed'));
    }
  } catch (e) {
    alert('Error: ' + e.message);
  }
  
  return false;
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

      // Refresh reports list
      await refreshReportsList();

      // Reset UI
      SESSION_STARTED = false;
      document.getElementById('setupBox').style.display = 'flex';
      document.getElementById('sessionBox').style.display = 'none';
      document.getElementById('sessionMeta').style.display = 'none';
      document.getElementById('statusBox').style.display = 'none';
      document.getElementById('reportsSection').style.display = 'none';
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

async function refreshReportsList() {
  try {
    const res = await fetch('/api/list_reports', { cache: 'no-store' });
    const data = await res.json();
    
    if (!data.success || !data.reports) {
      document.getElementById('reportsList').innerHTML = '<div style="color:#888;padding:10px">No reports available</div>';
      return;
    }
    
    const reportsList = document.getElementById('reportsList');
    reportsList.innerHTML = '';
    
    if (data.reports.length === 0) {
      reportsList.innerHTML = '<div style="color:#888;padding:10px">No reports generated yet</div>';
      return;
    }
    
    data.reports.forEach(report => {
      const row = document.createElement('div');
      row.style.cssText = 'display:flex;justify-content:space-between;align-items:center;background:#0f0f23;border:1px solid #333355;border-radius:8px;margin-bottom:8px;padding:10px;gap:10px';
      
      const info = document.createElement('div');
      info.style.flex = '1';
      info.innerHTML = `
        <div style="color:#00d4ff;font-weight:700;font-size:13px">${report.filename}</div>
        <div style="color:#888;font-size:11px">${report.type} | ${report.size} bytes | ${report.modified}</div>
      `;
      
      const btn = document.createElement('button');
      btn.className = 'btn';
      btn.style.cssText = 'background:#00ff88;color:#0f0f23;padding:6px 12px;font-size:12px;white-space:nowrap';
      btn.textContent = '📄 Open';
      btn.onclick = () => openReport(report.filename);
      
      row.appendChild(info);
      row.appendChild(btn);
      reportsList.appendChild(row);
    });
  } catch (e) {
    console.error('Error loading reports:', e);
    document.getElementById('reportsList').innerHTML = `<div style="color:#ff6666;padding:10px">Error: ${e.message}</div>`;
  }
}

async function openReport(filename) {
  try {
    const res = await fetch('/api/open_report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ filename })
    });
    
    const data = await res.json();
    
    if (data.success) {
      console.log(data.message);
    } else {
      alert('Error: ' + (data.message || 'Failed to open report'));
    }
  } catch (e) {
    alert('Failed to open report: ' + e.message);
  }
}

async function capturePhotoForStudent(studentName) {
  try {
    const res = await fetch('/api/capture_photo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ student_name: studentName })
    });
    
    const data = await res.json();
    
    if (data.success) {
      // Display the photo
      displayCapturedPhoto(data.photo_url, studentName);
      console.log(`📷 Photo captured: ${studentName}`);
    } else if (data.camera_disabled) {
      // Camera not available
      updateCameraStatus('Camera not available', true);
    }
  } catch (e) {
    console.error('Failed to capture photo:', e.message);
  }
}

function displayCapturedPhoto(photoUrl, studentName) {
  const img = document.getElementById('cameraPhoto');
  const photoInfo = document.getElementById('photoInfo');
  
  // Hide the placeholder and show the photo
  img.src = photoUrl + '?t=' + new Date().getTime();  // Add cache buster
  img.style.display = 'block';
  photoInfo.style.display = 'none';
  
  // Update status
  updateCameraStatus(`📷 ${studentName}`, false);
  
  // Auto-hide after 30 seconds if no new scan
  clearTimeout(window.photoHideTimeout);
  window.photoHideTimeout = setTimeout(() => {
    img.style.display = 'none';
    photoInfo.style.display = 'flex';
    updateCameraStatus('Ready', false);
  }, 30000);
}

function updateCameraStatus(status, isError = false) {
  const statusEl = document.getElementById('cameraStatus');
  if (statusEl) {
    statusEl.textContent = status;
    statusEl.style.color = isError ? '#ff6666' : '#00ff88';
  }
}

async function initializeCamera() {
  // Check if camera is available
  try {
    const res = await fetch('/api/photo_stats');
    const data = await res.json();
    
    if (data.success) {
      updateCameraStatus('Ready', false);
      console.log('📷 Camera system ready');
    } else {
      updateCameraStatus('Offline', true);
    }
  } catch (e) {
    updateCameraStatus('Error', true);
  }
}
