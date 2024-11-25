// Define global template selection functionality
let selectedTemplate = 'modern';

// Global function to get selected template
window.getSelectedTemplate = function() {
    return selectedTemplate || 'modern'; // Fallback to modern if nothing selected
};

// Presentation-specific functionality
document.addEventListener('DOMContentLoaded', function() {
    const templateCards = document.querySelectorAll('.template-card');
    const previewPanel = document.querySelector('.preview-panel');
    const textArea = document.getElementById('presentation-text');
    
    // Template selection handling with error handling
    try {
        templateCards.forEach(card => {
            if (!card.querySelector('.text-center')) {
                console.error('Template card missing text element');
                return;
            }
            // Add click handler
            card.addEventListener('click', function() {
                const template = this.querySelector('.text-center').textContent.trim().toLowerCase();
                setSelectedTemplate(template, this);
                console.log('Selected template:', template); // Debug logging
            });
        });
    } catch (error) {
        console.error('Error initializing template cards:', error);
    }
    
    // Function to update selected template
    function setSelectedTemplate(template, card) {
        // Remove active class from all cards
        templateCards.forEach(c => {
            c.classList.remove('active-template');
            c.querySelector('.tick-icon').style.display = 'none';
        });
        
        // Add active class to selected card
        card.classList.add('active-template');
        card.querySelector('.tick-icon').style.display = 'block';
        
        // Update selected template
        selectedTemplate = template;
        
        // Update preview if text exists
        if (textArea.value) {
            updatePreview(textArea.value, selectedTemplate);
        }
    }
    
    // Initialize template selection
    templateCards.forEach(card => {
        const template = card.querySelector('.text-center').textContent.toLowerCase();
        if (template === selectedTemplate) {
            setSelectedTemplate(template, card);
        }
        
        card.addEventListener('click', function() {
            const template = this.querySelector('.text-center').textContent.toLowerCase();
            setSelectedTemplate(template, this);
        });
    });
    
    // Expose getSelectedTemplate function for other scripts
    window.getSelectedTemplate = function() {
        return selectedTemplate;
    };
    
    // Live preview functionality
    let previewTimeout;
    textArea.addEventListener('input', function() {
        clearTimeout(previewTimeout);
        previewTimeout = setTimeout(() => {
            updatePreview(this.value, selectedTemplate);
        }, 1000);
    });
    
    // Preview update function
    function updatePreview(text, template) {
        if (!text) {
            previewPanel.innerHTML = `
                <h3 class="mb-4">Preview</h3>
                <div class="text-center text-muted">
                    Your video preview will appear here
                </div>`;
            return;
        }
        
        // Create a simple preview
        const slides = text.split('\n\n');
        let previewHTML = '<h3 class="mb-4">Preview</h3><div class="preview-slides">';
        
        slides.forEach((slide, index) => {
            const lines = slide.split('\n');
            const title = lines[0] || 'Slide ' + (index + 1);
            const content = lines.slice(1).join('<br>');
            
            previewHTML += `
                <div class="preview-slide mb-3 p-3 bg-dark">
                    <h5 class="slide-title">${title}</h5>
                    <div class="slide-content">${content}</div>
                </div>`;
        });
        
        previewHTML += '</div>';
        previewPanel.innerHTML = previewHTML;
    }
    
    // Animation effects for UI elements
    function addUIAnimations() {
        // Smooth scroll for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
        
        // Fade in elements on load
        document.querySelectorAll('.editor-panel, .preview-panel').forEach(panel => {
            panel.style.opacity = '0';
            panel.style.transition = 'opacity 0.5s ease-in-out';
            setTimeout(() => {
                panel.style.opacity = '1';
            }, 200);
        });
    }
    
    // Initialize animations
    addUIAnimations();
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to generate
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            document.getElementById('generate-btn').click();
        }
    });
});

// Add custom CSS styles for animations
const style = document.createElement('style');
style.textContent = `
    .preview-slide {
        border-radius: 8px;
        transition: transform 0.2s ease;
    }
    
    .preview-slide:hover {
        transform: scale(1.02);
    }
    
    .active-template {
        border: 2px solid var(--accent);
        transform: scale(1.05);
    }
    
    .preview-slides {
        max-height: 600px;
        overflow-y: auto;
        padding-right: 10px;
    }
    
    .slide-title {
        color: var(--accent);
        margin-bottom: 10px;
    }
    
    .slide-content {
        font-size: 0.9em;
        color: var(--text-muted);
    }
    
    .tick-icon {
        display: none;
        font-size: 1.2em;
        color: var(--accent);
        position: absolute;
        top: 50%;
        right: 10px;
        transform: translateY(-50%);
        transition: opacity 0.2s ease;
    }
    
    .tick-icon.active {
        opacity: 1;
    }
    
    .template-card:hover .tick-icon {
        opacity: 1;
    }
`;
document.head.appendChild(style);
