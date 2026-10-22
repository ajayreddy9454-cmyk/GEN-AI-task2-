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
      <span style="font-size: 0.85rem; font-weight: 600; color: var(--text-main); flex: 1;">${message}</span>
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
    userMsg.style.cssText = 'background: var(--primary); color: white; padding: 0.75rem 1rem; border-radius: 12px 12px 2px 12px; margin-bottom: 0.85rem; max-width: 85%; margin-left: auto; font-size: 0.86rem;';
    userMsg.textContent = query;
    chatContainer.appendChild(userMsg);

    // Append Loading skeleton
    const loadingMsg = document.createElement('div');
    loadingMsg.id = 'aiLoadingIndicator';
    loadingMsg.style.cssText = 'background: var(--bg-subtle); color: var(--text-muted); border: 1px solid var(--border-light); padding: 0.75rem 1rem; border-radius: 12px 12px 12px 2px; margin-bottom: 0.85rem; max-width: 85%; font-size: 0.85rem; font-style: italic;';
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
      aiMsg.style.cssText = 'background: var(--bg-surface); border: 1px solid var(--border-light); color: var(--text-main); padding: 1rem; border-radius: 12px 12px 12px 2px; margin-bottom: 0.85rem; max-width: 90%; font-size: 0.86rem; line-height: 1.6; box-shadow: var(--shadow-sm);';
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

  // ==========================================================================
  // 13. Dynamic Theme Management System
  // ==========================================================================
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const themeDropdown = document.getElementById('themeDropdown');

  if (themeToggleBtn && themeDropdown) {
    themeToggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      themeDropdown.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!themeDropdown.contains(e.target) && e.target !== themeToggleBtn) {
        themeDropdown.classList.remove('show');
      }
    });
  }

  window.switchTheme = function(themeName) {
    document.documentElement.setAttribute('data-theme', themeName);
    localStorage.setItem('student_llm_theme', themeName);

    // Update active state in dropdown
    document.querySelectorAll('.theme-option-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-theme') === themeName);
    });

    // Update dot preview
    const dot = document.getElementById('activeThemeDot');
    if (dot) {
      if (themeName === 'cosmic') dot.style.background = 'linear-gradient(135deg, #6366f1, #38bdf8)';
      else if (themeName === 'emerald') dot.style.background = 'linear-gradient(135deg, #10b981, #f59e0b)';
      else if (themeName === 'sunset') dot.style.background = 'linear-gradient(135deg, #f43f5e, #f59e0b)';
      else if (themeName === 'light') dot.style.background = 'linear-gradient(135deg, #4f46e5, #ffffff)';
    }

    if (themeDropdown) themeDropdown.classList.remove('show');
    showToast(`Theme switched to ${themeName.charAt(0).toUpperCase() + themeName.slice(1)}!`, 'info');
  };

  // Restore saved theme on startup
  const savedTheme = localStorage.getItem('student_llm_theme') || 'cosmic';
  window.switchTheme(savedTheme);

  // ==========================================================================
  // 14. Placement Drives Interactive Logic
  // ==========================================================================
  let currentActiveDriveId = null;

  window.openDriveDetailsModal = async function(driveId) {
    currentActiveDriveId = driveId;
    try {
      const resp = await fetch(`/api/drives/${driveId}`);
      const data = await resp.json();
      if (data.success) {
        document.getElementById('ddLogoBadge').textContent = data.logo_badge;
        document.getElementById('ddLogoBadge').style.background = `linear-gradient(135deg, ${data.logo_color} 0%, #1e1b4b 100%)`;
        document.getElementById('ddCompany').textContent = data.company_name;
        document.getElementById('ddRoleTitle').textContent = data.role_title;
        document.getElementById('ddPackage').textContent = data.package_lpa;
        document.getElementById('ddDriveDate').textContent = data.drive_date;
        document.getElementById('ddMinGpa').textContent = `${data.min_gpa} / 10.0`;
        document.getElementById('ddLocation').textContent = data.location;
        document.getElementById('ddDescription').textContent = data.job_description;
        document.getElementById('ddRoundsDetail').textContent = data.rounds_detail;

        const applyBtn = document.getElementById('ddModalApplyBtn');
        if (applyBtn) {
          if (data.app_status) {
            applyBtn.innerHTML = `<i data-lucide="check-check" style="width: 16px; height: 16px;"></i> ${data.app_status}`;
            applyBtn.disabled = true;
            applyBtn.className = 'btn btn-success';
          } else {
            applyBtn.innerHTML = `<i data-lucide="send" style="width: 16px; height: 16px;"></i> Apply for Drive`;
            applyBtn.disabled = false;
            applyBtn.className = 'btn btn-primary';
          }
        }

        openModal('driveDetailsModal');
        if (window.lucide) lucide.createIcons();
      }
    } catch (e) {
      showToast('Could not fetch drive details', 'error');
    }
  };

  window.openApplyModal = function(driveId, companyName, roleTitle, pkg) {
    currentActiveDriveId = driveId;
    const driveInput = document.getElementById('applyDriveId');
    const modalTitle = document.getElementById('applyModalTitle');
    if (driveInput) driveInput.value = driveId;
    if (modalTitle) modalTitle.textContent = `Apply to ${companyName} (${roleTitle})`;
    openModal('applyDriveModal');
  };

  window.triggerApplyFromDetails = function() {
    closeModal('driveDetailsModal');
    const company = document.getElementById('ddCompany')?.textContent || 'Company';
    const role = document.getElementById('ddRoleTitle')?.textContent || 'Position';
    const pkg = document.getElementById('ddPackage')?.textContent || '';
    if (currentActiveDriveId) {
      openApplyModal(currentActiveDriveId, company, role, pkg);
    }
  };

  window.handleDriveApplicationSubmit = async function(event) {
    event.preventDefault();
    const driveId = document.getElementById('applyDriveId').value;
    const resumeLink = document.getElementById('applyResumeUrl').value;
    const coverNote = document.getElementById('applyCoverNote').value;

    try {
      const resp = await fetch(`/api/drives/${driveId}/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resume_link: resumeLink, cover_note: coverNote })
      });
      const res = await resp.json();
      if (res.success) {
        closeModal('applyDriveModal');
        showToast(res.message, 'success');

        // Update card in DOM
        const badge = document.getElementById(`drive-badge-${driveId}`);
        if (badge) {
          badge.className = 'badge badge-submitted';
          badge.textContent = '📨 Applied (Today)';
        }

        const btn = document.getElementById(`apply-btn-${driveId}`);
        if (btn) {
          btn.outerHTML = `<button class="btn btn-success btn-sm" disabled style="opacity: 0.9;"><i data-lucide="check-check" style="width: 14px; height: 14px;"></i> Applied</button>`;
          if (window.lucide) lucide.createIcons();
        }
      }
    } catch (err) {
      showToast('Submission error, please try again', 'error');
    }
  };

  // ==========================================================================
  // 15. Attendance Tracker Actions
  // ==========================================================================
  window.quickMarkForCourse = function(courseId, courseCode, courseTitle) {
    const sel = document.getElementById('attCourseSelect');
    if (sel) sel.value = courseId;
    const modalTitle = document.getElementById('markModalTitle');
    if (modalTitle) modalTitle.textContent = `Record Attendance for ${courseCode}`;
    openModal('markAttendanceModal');
  };

  window.handleAttendanceSubmit = async function(event) {
    event.preventDefault();
    const courseId = document.getElementById('attCourseSelect').value;
    const status = document.getElementById('attStatusSelect').value;
    const sessionDate = document.getElementById('attDateInput').value;
    const sessionTopic = document.getElementById('attTopicInput').value;
    const remarks = document.getElementById('attRemarksInput').value;

    try {
      const resp = await fetch('/api/attendance/mark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          course_id: courseId,
          status: status,
          session_date: sessionDate,
          session_topic: sessionTopic,
          remarks: remarks
        })
      });

      const res = await resp.json();
      if (res.success) {
        closeModal('markAttendanceModal');
        showToast(res.message, 'success');

        // Update banner stats dynamically
        if (res.overview) {
          const bannerPct = document.getElementById('bannerOverallPct');
          if (bannerPct) bannerPct.textContent = `${res.overview.overall_pct}%`;
          const bannerCount = document.getElementById('bannerClassesCount');
          if (bannerCount) bannerCount.textContent = `${res.overview.attended_classes}/${res.overview.total_classes}`;
          const bannerBunks = document.getElementById('bannerSafeBunks');
          if (bannerBunks) bannerBunks.textContent = `+${res.overview.safe_bunks} classes`;
        }

        // Add new row to table
        const tbody = document.getElementById('attendanceTableBody');
        if (tbody) {
          const courseText = document.getElementById('attCourseSelect').selectedOptions[0]?.text || 'Course';
          const newRow = document.createElement('tr');
          newRow.style.animation = 'slideInDown 0.3s ease';
          newRow.innerHTML = `
            <td style="white-space: nowrap; font-size: 0.82rem; font-weight: 600; color: var(--text-muted);">
              <i data-lucide="calendar" style="width: 12px; height: 12px; vertical-align: middle;"></i> ${sessionDate}
            </td>
            <td>
              <span class="course-code" style="font-size: 0.72rem;">${courseText.split(' - ')[0]}</span>
              <div style="font-size: 0.8rem; font-weight: 600; color: var(--text-main); margin-top: 2px;">${courseText.split(' - ')[1] || ''}</div>
            </td>
            <td style="font-size: 0.85rem; color: var(--text-body);">${sessionTopic}</td>
            <td>
              <span class="badge ${status === 'Present' ? 'badge-completed' : (status === 'Late' ? 'badge-submitted' : 'badge-overdue')}">
                <i data-lucide="${status === 'Present' ? 'check-circle' : (status === 'Late' ? 'clock' : 'x-circle')}" style="width: 11px; height: 11px;"></i> ${status}
              </span>
            </td>
            <td style="font-size: 0.8rem; color: var(--text-muted);">${remarks || 'Recorded via portal'}</td>
          `;
          tbody.prepend(newRow);
          if (window.lucide) lucide.createIcons();
        }
      }
    } catch (err) {
      showToast('Could not save attendance', 'error');
    }
  };

  // ==========================================================================
  // 16. Feedback & Reviews Hub Logic
  // ==========================================================================
  window.setFeedbackRating = function(rating) {
    const hidden = document.getElementById('fbRatingVal');
    if (hidden) hidden.value = rating;

    const stars = document.querySelectorAll('#starRatingSelector .star-btn');
    stars.forEach((star, idx) => {
      star.classList.toggle('active', idx < rating);
    });

    const label = document.getElementById('starRatingText');
    if (label) {
      const descriptions = [
        '1.0 - Needs Major Improvement',
        '2.0 - Below Academic Standards',
        '3.0 - Satisfactory / Average',
        '4.0 - Very Good Experience',
        '5.0 - Exceptional Quality'
      ];
      label.textContent = descriptions[rating - 1] || `${rating}.0 Stars`;
    }
  };

  window.handleCategoryChange = function(cat) {
    const targetInput = document.getElementById('fbTargetName');
    if (targetInput) {
      if (cat === 'Course Curriculum') targetInput.value = 'CS-401 Deep Learning';
      else if (cat === 'Placement & Career Drives') targetInput.value = 'Google Campus Drive';
      else if (cat === 'Faculty Guidance') targetInput.value = 'Dr. Katherine Vance';
      else if (cat === 'LMS Platform') targetInput.value = 'Student LLM Platform';
      else if (cat === 'Campus Facilities') targetInput.value = 'Innovation Studio 3 GPU Labs';
    }
  };

  window.handleFeedbackFormSubmit = async function(event) {
    event.preventDefault();
    const category = document.getElementById('fbCategorySelect').value;
    const targetName = document.getElementById('fbTargetName').value;
    const rating = document.getElementById('fbRatingVal').value;
    const reviewTitle = document.getElementById('fbReviewTitle').value;
    const reviewText = document.getElementById('fbReviewText').value;
    const isAnonymous = document.getElementById('fbIsAnonymous').checked ? 1 : 0;

    try {
      const resp = await fetch('/api/feedback/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          category,
          target_name: targetName,
          rating,
          review_title: reviewTitle,
          review_text: reviewText,
          is_anonymous: isAnonymous
        })
      });

      const res = await resp.json();
      if (res.success) {
        showToast(res.message, 'success');
        document.getElementById('fbReviewTitle').value = '';
        document.getElementById('fbReviewText').value = '';

        // Prepend to feed
        const feed = document.getElementById('feedbackFeed');
        if (feed) {
          const author = isAnonymous ? 'Anonymous Student' : 'Ajay Reddy';
          const card = document.createElement('div');
          card.className = 'card feedback-card hover-glow';
          card.style.animation = 'slideInDown 0.35s ease';
          card.innerHTML = `
            <div class="feedback-card-header">
              <div style="display: flex; gap: 0.65rem; align-items: center;">
                <div class="avatar-circle">${author[0]}</div>
                <div>
                  <div style="display: flex; align-items: center; gap: 0.45rem;">
                    <span class="feedback-author">${author}</span>
                    ${!isAnonymous ? '<span class="badge badge-completed" style="font-size: 0.65rem; padding: 0.1rem 0.4rem;"><i data-lucide="shield-check" style="width: 10px; height: 10px;"></i> Verified Student</span>' : ''}
                  </div>
                  <div class="feedback-date">Just now</div>
                </div>
              </div>
              <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.25rem;">
                <div class="star-display">
                  ${'<i data-lucide="star" class="star-icon filled"></i>'.repeat(parseInt(rating))}
                  ${'<i data-lucide="star" class="star-icon empty"></i>'.repeat(5 - parseInt(rating))}
                </div>
                <span class="badge badge-accent-glow" style="font-size: 0.7rem;">${category}</span>
              </div>
            </div>
            <div class="feedback-target-tag">
              <i data-lucide="tag" style="width: 12px; height: 12px;"></i>
              <span>Target: <strong>${targetName}</strong></span>
            </div>
            <h3 class="feedback-title">${reviewTitle}</h3>
            <p class="feedback-body">${reviewText}</p>
            <div class="feedback-card-footer">
              <button class="helpful-btn" style="cursor: default;">
                <i data-lucide="thumbs-up" style="width: 14px; height: 14px;"></i>
                <span>Helpful (0)</span>
              </button>
              <span style="font-size: 0.74rem; color: var(--text-subtle);">
                Sentiment: <strong style="color: var(--success);">Positive</strong>
              </span>
            </div>
          `;
          feed.prepend(card);
          if (window.lucide) lucide.createIcons();

          const counter = document.getElementById('totalReviewsCounter');
          if (counter) counter.textContent = parseInt(counter.textContent || 0) + 1;
        }
      }
    } catch (err) {
      showToast('Could not submit feedback', 'error');
    }
  };

  window.upvoteFeedback = async function(feedbackId) {
    try {
      const resp = await fetch(`/api/feedback/${feedbackId}/upvote`, { method: 'POST' });
      const data = await resp.json();
      if (data.success) {
        const countEl = document.getElementById(`upvote-count-${feedbackId}`);
        if (countEl) {
          countEl.textContent = data.upvotes;
          countEl.parentElement.style.transform = 'scale(1.15)';
          setTimeout(() => countEl.parentElement.style.transform = '', 200);
        }
        showToast('Feedback upvoted as helpful!', 'info');
      }
    } catch (e) {
      console.error(e);
    }
  };
});
