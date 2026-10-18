/**
 * Student LLM - Enterprise Academic LMS Frontend Logic & Micro-interactions
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Initialize Lucide Icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // 2. Mobile Sidebar Drawer Toggle
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.getElementById('sidebar');
  const sidebarBackdrop = document.getElementById('sidebarBackdrop');

  const sidebarCloseBtn = document.getElementById('sidebarCloseBtn');

  function openSidebar() {
    sidebar?.classList.add('open');
    sidebarBackdrop?.classList.add('show');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    sidebar?.classList.remove('open');
    sidebarBackdrop?.classList.remove('show');
    document.body.style.overflow = '';
  }

  if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', openSidebar);
  if (sidebarCloseBtn) sidebarCloseBtn.addEventListener('click', closeSidebar);
  if (sidebarBackdrop) sidebarBackdrop.addEventListener('click', closeSidebar);

  document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
    link.addEventListener('click', () => {
      if (window.innerWidth <= 992) closeSidebar();
    });
  });

  // 3. Notification Dropdown Toggle
  const notifToggleBtn = document.getElementById('notifToggleBtn');
  const notifDropdown = document.getElementById('notifDropdown');

  if (notifToggleBtn && notifDropdown) {
    notifToggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      notifDropdown.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!notifDropdown.contains(e.target) && e.target !== notifToggleBtn) {
        notifDropdown.classList.remove('show');
      }
    });
  }

  window.markAllNotificationsRead = async function() {
    try {
      const resp = await fetch('/api/notifications/read', { method: 'POST' });
      const data = await resp.json();
      if (data.success) {
        document.querySelectorAll('.notif-item.unread').forEach(el => el.classList.remove('unread'));
        const badge = document.querySelector('.notification-badge');
        if (badge) badge.style.display = 'none';
        showToast('All notifications marked as read.', 'info');
      }
    } catch (err) {
      console.error(err);
    }
  };

  // 4. Modal Controller
  window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add('show');
      document.body.style.overflow = 'hidden';
      if (window.lucide) lucide.createIcons();
    }
  };

  window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove('show');
      document.body.style.overflow = '';
    }
  };

  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) window.closeModal(modal.id);
    });
  });

  // 5. Toast Notification System
  window.showToast = function(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toastContainer';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let iconName = 'check-circle';
    if (type === 'error') iconName = 'alert-circle';
    if (type === 'info') iconName = 'info';

    toast.innerHTML = `
      <i data-lucide="${iconName}" style="color: ${type === 'success' ? '#10b981' : (type === 'error' ? '#ef4444' : '#4f46e5')}; width: 18px; height: 18px;"></i>
      <span style="font-size: 0.85rem; font-weight: 600; color: #1e293b; flex: 1;">${message}</span>
    `;

    container.appendChild(toast);
    if (window.lucide) lucide.createIcons();

    setTimeout(() => {
      toast.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  };

  // 6. Assignment Status AJAX Toggle
  window.updateAssignmentStatus = async function(assignmentId, newStatus) {
    try {
      const response = await fetch(`/api/assignments/${assignmentId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });

      const result = await response.json();
      if (result.success) {
        showToast(result.message, 'success');
        
        const badgeEl = document.getElementById(`assignment-badge-${assignmentId}`);
        if (badgeEl) {
          badgeEl.className = `badge badge-${newStatus.toLowerCase()}`;
          badgeEl.textContent = newStatus;
        }

        const actionsEl = document.getElementById(`assignment-actions-${assignmentId}`);
        if (actionsEl) {
          if (newStatus === 'Completed') {
            actionsEl.innerHTML = `
              <button class="btn btn-secondary btn-sm" onclick="updateAssignmentStatus(${assignmentId}, 'Pending')">
                <i data-lucide="rotate-ccw" style="width: 14px; height: 14px;"></i> Reopen
              </button>
            `;
          } else {
            actionsEl.innerHTML = `
              <button class="btn btn-primary btn-sm" onclick="updateAssignmentStatus(${assignmentId}, 'Completed')">
                <i data-lucide="check" style="width: 14px; height: 14px;"></i> Complete
              </button>
              <button class="btn btn-secondary btn-sm" onclick="openSubmissionModal(${assignmentId}, 'Assignment')">
                <i data-lucide="upload-cloud" style="width: 14px; height: 14px;"></i> Submit
              </button>
            `;
          }
          if (window.lucide) lucide.createIcons();
        }
      } else {
        showToast(result.message || 'Failed to update assignment', 'error');
      }
    } catch (err) {
      console.error(err);
      showToast('Connection error. Please try again.', 'error');
    }
  };

  // 7. Assignment Submission Modal Trigger & Handler
  window.openSubmissionModal = function(assignmentId, title) {
    document.getElementById('subAssignmentId').value = assignmentId;
    document.getElementById('subModalTitle').textContent = `Submit Work: ${title}`;
    openModal('assignmentSubmitModal');
  };

  window.handleAssignmentSubmit = async function(e) {
    e.preventDefault();
    const assignmentId = document.getElementById('subAssignmentId').value;
    const note = document.getElementById('subNote').value.trim();
    const url = document.getElementById('subUrl').value.trim();

    try {
      const resp = await fetch(`/api/assignments/${assignmentId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: 'Submitted',
          submission_text: note,
          submission_url: url
        })
      });
      const data = await resp.json();
      if (data.success) {
        closeModal('assignmentSubmitModal');
        showToast('Assignment submitted successfully for instructor evaluation!', 'success');
        setTimeout(() => window.location.reload(), 700);
      }
    } catch (err) {
      showToast('Submission error. Please retry.', 'error');
    }
  };

  // 8. Course Progress Fast Updater
  window.incrementLesson = async function(courseId, currentLessons, totalLessons) {
    if (currentLessons >= totalLessons) {
      showToast('Course curriculum is already 100% completed!', 'info');
      return;
    }
    const nextLessons = currentLessons + 1;
    try {
      const response = await fetch(`/api/courses/${courseId}/progress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed_lessons: nextLessons })
      });
      const data = await response.json();
      if (data.success) {
        showToast(`Progress logged: Lesson ${nextLessons}/${totalLessons} completed!`, 'success');
        setTimeout(() => window.location.reload(), 600);
      }
    } catch (e) {
      showToast('Could not update course progress', 'error');
    }
  };

  // 9. Course Syllabus Detail Modal Loader
  window.viewCourseSyllabus = async function(courseId) {
    try {
      const resp = await fetch(`/api/courses/${courseId}/syllabus`);
      const data = await resp.json();
      if (data.success) {
        document.getElementById('sylTitle').textContent = `${data.code}: ${data.title}`;
        document.getElementById('sylInstructor').textContent = `${data.instructor} (${data.instructor_email})`;
        document.getElementById('sylCredits').textContent = `${data.credits} Credit Units • ${data.level}`;
        document.getElementById('sylLocation').textContent = `${data.location} • ${data.schedule}`;
        document.getElementById('sylOutline').innerText = data.syllabus_summary || 'Full curriculum syllabus available on university catalog.';
        openModal('courseSyllabusModal');
      }
    } catch (err) {
      showToast('Could not load course syllabus', 'error');
    }
  };

  // 10. Student LLM AI Assistant Query Engine
  window.askAiAssistant = async function(prefilledQuery = null) {
    const input = document.getElementById('aiQueryInput');
    const query = prefilledQuery || (input ? input.value.trim() : '');
    if (!query) return;

    const chatContainer = document.getElementById('aiChatContainer');
    if (!chatContainer) return;

    // Append User message
    const userMsg = document.createElement('div');
    userMsg.style.cssText = 'background: #4f46e5; color: white; padding: 0.75rem 1rem; border-radius: 12px 12px 2px 12px; margin-bottom: 0.85rem; max-width: 85%; margin-left: auto; font-size: 0.86rem;';
    userMsg.textContent = query;
    chatContainer.appendChild(userMsg);

    // Append Loading skeleton
    const loadingMsg = document.createElement('div');
    loadingMsg.id = 'aiLoadingIndicator';
    loadingMsg.style.cssText = 'background: #f1f5f9; color: #475569; padding: 0.75rem 1rem; border-radius: 12px 12px 12px 2px; margin-bottom: 0.85rem; max-width: 85%; font-size: 0.85rem; font-style: italic;';
    loadingMsg.innerHTML = '<span class="demo-indicator"></span> Consulting academic model...';
    chatContainer.appendChild(loadingMsg);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    if (input) input.value = '';

    try {
      const resp = await fetch('/api/ai-assistant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query })
      });
      const data = await resp.json();
      loadingMsg.remove();

      const aiMsg = document.createElement('div');
      aiMsg.style.cssText = 'background: #ffffff; border: 1px solid #e2e8f0; color: #0f172a; padding: 1rem; border-radius: 12px 12px 12px 2px; margin-bottom: 0.85rem; max-width: 90%; font-size: 0.86rem; line-height: 1.6; box-shadow: 0 1px 3px rgba(0,0,0,0.05);';
      // Simple format conversion for line breaks and bullet points
      aiMsg.innerHTML = data.answer.replace(/\n\n/g, '<br><br>').replace(/•/g, '&bull;');
      chatContainer.appendChild(aiMsg);
      chatContainer.scrollTop = chatContainer.scrollHeight;
    } catch (e) {
      loadingMsg.remove();
      showToast('Could not query AI Copilot', 'error');
    }
  };

  // 11. Resource Viewer Modal Trigger
  window.viewResourceModal = function(title, category, type, readTime, snippet, externalUrl) {
    const modalTitle = document.getElementById('resModalTitle');
    const modalCategory = document.getElementById('resModalCategory');
    const modalType = document.getElementById('resModalType');
    const modalTime = document.getElementById('resModalTime');
    const modalSnippet = document.getElementById('resModalSnippet');
    const modalExternalLink = document.getElementById('resModalExternalLink');

    if (modalTitle) modalTitle.textContent = title;
    if (modalCategory) modalCategory.textContent = category;
    if (modalType) modalType.textContent = type;
    if (modalTime) modalTime.textContent = readTime;
    if (modalSnippet) modalSnippet.textContent = snippet;
    if (modalExternalLink) {
      modalExternalLink.href = externalUrl;
      modalExternalLink.style.display = externalUrl ? 'inline-flex' : 'none';
    }

    openModal('resourceDetailModal');
  };

  // 12. Auto-dismiss flash alerts
  document.querySelectorAll('.flash-alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.4s ease';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });
});
