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

    // Handle CSV file selection
    csvUpload.addEventListener('change', function(e) {
        csvFile = e.target.files[0];
        if (csvFile) {
            console.log('CSV file selected:', csvFile.name);
        }
    });

    generateBtn.addEventListener('click', async function() {
        const text = editor.value;

        if (!text) {
            showError('Please enter some text for the presentation.');
            return;
        }

        generateBtn.disabled = true;

        try {
            // Step 1: Enhance text
            currentStep = 1;
            updateProgress(currentStep);
            showLoading('Enhancing text...');

            // Create FormData object
            const formData = new FormData();
            formData.append('text', text);

            // Add CSV file if selected
            if (csvFile) {
                formData.append('csv_file', csvFile);
                console.log('Appending CSV file to form data:', csvFile.name);
            }

            const response = await fetch('/enhance', {
                method: 'POST',
                body: formData // FormData automatically sets the correct Content-Type
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to enhance text');
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
            showLoading('Converting to video...');

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
                        Download Video
                    </a>
                </div>
            `;

        } catch (error) {
            console.error('Generation error:', error);
            showError(error.message || 'An unexpected error occurred');
            updateProgress(0);
        } finally {
            generateBtn.disabled = false;
        }
    });

    // Add template selection functionality
    const templateCards = document.querySelectorAll('.template-card');
    templateCards.forEach(card => {
        card.addEventListener('click', function() {
            templateCards.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
        });
    });
});