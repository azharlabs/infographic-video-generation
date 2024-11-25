document.addEventListener('DOMContentLoaded', function() {
    const editor = document.getElementById('presentation-text');
    const csvUpload = document.getElementById('csv-upload');
    const generateBtn = document.getElementById('generate-btn');
    const progressBar = document.querySelector('.progress-bar');
    const previewPanel = document.querySelector('.preview-panel');

    let currentStep = 0;
    const totalSteps = 3;
    let csvFile = null;

    function updateProgress(step) {
        const progress = (step / totalSteps) * 100;
        progressBar.style.width = `${progress}%`;
    }

    function showError(message) {
        previewPanel.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <h4 class="alert-heading">Error</h4>
                <p>${message}</p>
            </div>
        `;
    }

    function showLoading(step) {
        previewPanel.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">${step}</p>
            </div>
        `;
    }

    function showSuccess(message) {
        previewPanel.innerHTML = `
            <div class="alert alert-success" role="alert">
                <h4 class="alert-heading">Success</h4>
                <p>${message}</p>
            </div>
        `;
    }

    // Handle CSV file selection with validation
    csvUpload.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            // Validate file type
            if (!file.name.toLowerCase().endsWith('.csv')) {
                showError('Please select a valid CSV file');
                csvUpload.value = '';
                csvFile = null;
                return;
            }

            // Validate file size (10MB limit)
            if (file.size > 10 * 1024 * 1024) {
                showError('CSV file size should be less than 10MB');
                csvUpload.value = '';
                csvFile = null;
                return;
            }

            csvFile = file;
            console.log('CSV file selected:', csvFile.name);
            showSuccess(`CSV file "${csvFile.name}" loaded successfully`);
        } else {
            csvFile = null;
            previewPanel.innerHTML = `
                <h3 class="mb-4">Preview</h3>
                <div class="text-center text-muted">
                    Your video preview will appear here
                </div>
            `;
        }
    });

    generateBtn.addEventListener('click', async function() {
        const text = editor.value.trim();

        if (!text) {
            showError('Please enter some text for the presentation.');
            return;
        }

        generateBtn.disabled = true;

        try {
            // Step 1: Enhance text
            currentStep = 1;
            updateProgress(currentStep);
            showLoading('Enhancing text with AI...');

            // Create FormData object
            const formData = new FormData();
            formData.append('text', text);

            // Add CSV file if selected
            if (csvFile) {
                formData.append('csv_file', csvFile);
                console.log('Appending CSV file to form data:', csvFile.name);
            }

            // Log FormData contents for debugging
            for (let pair of formData.entries()) {
                console.log('FormData entry -', pair[0] + ':', (pair[1] instanceof File ? pair[1].name : 'text content'));
            }

            const response = await fetch('/enhance', {
                method: 'POST',
                body: formData
            });

            const contentType = response.headers.get('content-type');
            if (!response.ok) {
                const errorText = contentType && contentType.includes('application/json') 
                    ? (await response.json()).error 
                    : await response.text();
                throw new Error(errorText || 'Failed to enhance text');
            }

            const enhancedText = await response.json();

            // Step 2: Generate PPTX
            currentStep = 2;
            updateProgress(currentStep);
            showLoading('Generating frames...');

            const selectedTemplate = document.querySelector('.template-card.selected');
            const templateName = selectedTemplate ? 
                selectedTemplate.querySelector('.text-center').textContent.toLowerCase() : 
                'modern';

            const pptxResponse = await fetch('/generate-pptx', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    text: enhancedText.text,
                    template: templateName
                })
            });

            if (!pptxResponse.ok) {
                const error = await pptxResponse.json();
                throw new Error(error.error || 'Failed to generate frames');
            }

            const pptxData = await pptxResponse.json();

            // Step 3: Convert to video
            currentStep = 3;
            updateProgress(currentStep);
            showLoading('Creating video...');

            const videoResponse = await fetch('/convert-video', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({pptx_path: pptxData.pptx_path})
            });

            if (!videoResponse.ok) {
                const error = await videoResponse.json();
                throw new Error(error.error || 'Failed to convert to video');
            }

            // Show preview
            const videoData = await videoResponse.json();
            previewPanel.innerHTML = `
                <h3 class="mb-4">Preview</h3>
                <div class="video-container mb-3">
                    <video controls class="w-100">
                        <source src="${videoData.video_url}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                </div>
                <div class="d-flex justify-content-between">
                    <a href="${videoData.video_url}" download class="btn btn-primary">
                        <i class="fas fa-download"></i> Download Video
                    </a>
                </div>
                <div class="mt-3 text-center text-success">
                    <i class="fas fa-check-circle"></i> Generation completed successfully!
                </div>
            `;

            // Reset progress
            updateProgress(totalSteps);

        } catch (error) {
            console.error('Generation error:', error);
            showError(error.message || 'An unexpected error occurred');
            updateProgress(0);
        } finally {
            generateBtn.disabled = false;
            // Reset CSV file after processing
            csvFile = null;
            csvUpload.value = '';
        }
    });

    // Add template selection functionality
    const templateCards = document.querySelectorAll('.template-card');
    templateCards.forEach(card => {
        card.addEventListener('click', function() {
            templateCards.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');

            // Show selected template name
            const templateName = this.querySelector('.text-center').textContent;
            showSuccess(`Selected template: ${templateName}`);
        });
    });

    // Initial setup
    // Select the first template by default if none is selected
    if (!document.querySelector('.template-card.selected')) {
        templateCards[0]?.classList.add('selected');
    }
});