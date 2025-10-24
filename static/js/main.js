// Custom JavaScript for Blue Article

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            var target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Search functionality
    var searchInput = document.querySelector('input[name="q"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            var query = this.value.trim();
            if (query.length > 2) {
                // You can implement live search here
                console.log('Searching for:', query);
            }
        });
    }

    // Article view tracking
    var articleId = document.querySelector('[data-article-id]');
    if (articleId) {
        var id = articleId.getAttribute('data-article-id');
        trackArticleView(id);
    }

    // Copy to clipboard functionality
    var copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var text = this.getAttribute('data-copy-text');
            navigator.clipboard.writeText(text).then(function() {
                showToast('Copiado para a área de transferência!', 'success');
            });
        });
    });
});

// Track article view
function trackArticleView(articleId) {
    fetch('/api/track-view/' + articleId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    }).catch(function(error) {
        console.log('Error tracking view:', error);
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    var toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    var toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-' + type + ' border-0';
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    var bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Create toast container if it doesn't exist
function createToastContainer() {
    var container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// Download tracking
function trackDownload(articleId) {
    fetch('/api/track-download/' + articleId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    }).then(function(response) {
        if (response.ok) {
            showToast('Download iniciado!', 'success');
        }
    }).catch(function(error) {
        console.log('Error tracking download:', error);
    });
}

// Confirm delete
function confirmDelete(message = 'Tem certeza que deseja deletar este item?') {
    return confirm(message);
}

// Auto-save draft (for article forms)
function autoSaveDraft() {
    var form = document.querySelector('form');
    if (!form) return;
    
    var formData = new FormData(form);
    var data = {};
    for (var pair of formData.entries()) {
        data[pair[0]] = pair[1];
    }
    
    localStorage.setItem('article_draft', JSON.stringify(data));
    showToast('Rascunho salvo automaticamente', 'info');
}

// Load draft
function loadDraft() {
    var draft = localStorage.getItem('article_draft');
    if (draft) {
        var data = JSON.parse(draft);
        for (var field in data) {
            var element = document.querySelector('[name="' + field + '"]');
            if (element) {
                element.value = data[field];
            }
        }
        showToast('Rascunho carregado', 'info');
    }
}

// Clear draft
function clearDraft() {
    localStorage.removeItem('article_draft');
}

// Initialize auto-save for article forms
document.addEventListener('DOMContentLoaded', function() {
    var articleForm = document.querySelector('form[action*="add_article"], form[action*="edit_article"]');
    if (articleForm) {
        // Load draft on page load
        loadDraft();
        
        // Auto-save every 30 seconds
        setInterval(autoSaveDraft, 30000);
        
        // Clear draft on successful submit
        articleForm.addEventListener('submit', function() {
            setTimeout(clearDraft, 1000);
        });
    }
});

// Search suggestions (if you want to implement)
function getSearchSuggestions(query) {
    if (query.length < 2) return;
    
    fetch('/api/search-suggestions?q=' + encodeURIComponent(query))
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            showSearchSuggestions(data);
        })
        .catch(function(error) {
            console.log('Error getting suggestions:', error);
        });
}

function showSearchSuggestions(suggestions) {
    // Implement search suggestions UI here
    console.log('Suggestions:', suggestions);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        var searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals/alerts
    if (e.key === 'Escape') {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }
});
