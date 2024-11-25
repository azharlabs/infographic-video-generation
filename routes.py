from flask import jsonify, request, render_template, url_for
from app import app
from utils.openai_helper import enhance_text
from utils.pptx_generator import create_presentation
from utils.video_converter import convert_to_video
from utils.animation_generator import create_animations_for_content
from utils.csv_rag import EnhancedDocumentRAG
import os
import logging
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/enhance', methods=['POST'])
def enhance():
    # Enhanced debug logging
    logger.info("Request Content-Type: %s", request.content_type)
    logger.info("Form data keys: %s", list(request.form.keys()))
    logger.info("Files keys: %s", list(request.files.keys()))

    text = request.form.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        csv_file = request.files.get('csv_file')
        if csv_file and csv_file.filename:
            logger.info(f"Processing CSV file: {csv_file.filename}")

            # Validate CSV file
            if not csv_file.filename.lower().endswith('.csv'):
                return jsonify(
                    {'error':
                     'Invalid file type. Please upload a CSV file'}), 400

            # Create temporary directory for CSV processing
            temp_dir = tempfile.mkdtemp()
            try:
                csv_path = os.path.join(temp_dir, 'input.csv')
                csv_file.save(csv_path)
                logger.info(f"Saved CSV to: {csv_path}")

                try:
                    # Initialize and use RAG system
                    rag_system = EnhancedDocumentRAG(documents_path=temp_dir,
                                                     chunk_size=1024,
                                                     chunk_overlap=20,
                                                     batch_size=100,
                                                     max_workers=4)

                    # Generate enhanced response
                    enhanced = rag_system.generate_comprehensive_response(
                        query=text, max_chunk_tokens=24000)

                    print("enhanced======================>", enhanced)

                    if not enhanced:
                        raise ValueError(
                            "Failed to generate enhanced response")

                    logger.info("Successfully processed with RAG system")
                    return jsonify({'text': enhanced})

                except Exception as e:
                    logger.error(f"RAG processing error: {str(e)}")
                    return jsonify(
                        {'error':
                         f'Failed to process CSV data: {str(e)}'}), 500

            finally:
                # Clean up temporary directory
                try:
                    shutil.rmtree(temp_dir)
                    logger.info("Cleaned up temporary directory")
                except Exception as e:
                    logger.error(
                        f"Error cleaning up temporary directory: {str(e)}")

        else:
            # Use regular enhancement if no CSV
            enhanced = enhance_text(text)
            print("enhanced======================>", enhanced)
            return jsonify({'text': enhanced})

    except Exception as e:
        logger.error(f"Text enhancement error: {str(e)}")
        return jsonify({'error': f'Failed to enhance text: {str(e)}'}), 500


@app.route('/generate-pptx', methods=['POST'])
def generate_pptx():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json()
    text = data.get('text')
    print("generate text============================", text)
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    template = data.get('template', 'modern').lower().strip()
    if template not in [
            'modern', 'professional', 'minimal', 'gradient', 'corporate',
            'creative', 'dynamic', 'clean', 'dark', 'tech', 'elegant',
            'future', 'nature', 'business'
    ]:
        template = 'modern'  # Fallback to modern if invalid template
    logger.info(f"Using template: {template}")

    try:
        # Create animations for each section
        animations = create_animations_for_content(text,
                                                   app.config['UPLOAD_FOLDER'])

        # Generate PPTX with animations
        prs = create_presentation(text, template, animations)

        # Generate unique filename
        filename = f'presentation_{os.urandom(4).hex()}.pptx'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save PPTX
        prs.save(output_path)

        # Clean up animation files
        for anim_path in animations:
            try:
                if os.path.exists(anim_path):
                    os.remove(anim_path)
            except Exception as e:
                logger.warning(f"Failed to clean up animation: {str(e)}")

        # Return URL-safe path for static file
        return jsonify({
            'pptx_path':
            output_path,
            'pptx_url':
            url_for('static', filename=f'uploads/{filename}')
        })
    except Exception as e:
        logger.error(f"PPTX generation error: {str(e)}")
        return jsonify({'error': 'Failed to generate frames'}), 500


@app.route('/convert-video', methods=['POST'])
def convert():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json()
    pptx_path = data.get('pptx_path')
    if not pptx_path:
        return jsonify({'error': 'No PPTX path provided'}), 400

    # Validate input path
    try:
        pptx_path = os.path.abspath(pptx_path)
        if not os.path.exists(pptx_path):
            return jsonify({'error': 'PPTX file not found'}), 404

        # Validate path is within allowed directory
        if not pptx_path.startswith(
                os.path.abspath(app.config['UPLOAD_FOLDER'])):
            return jsonify({'error': 'Invalid file path'}), 403

        # Check file size
        file_size = os.path.getsize(pptx_path)
        max_size = app.config['MAX_CONTENT_LENGTH']
        if file_size > max_size:
            return jsonify({
                'error':
                f'File too large. Maximum size is {max_size/1024/1024}MB'
            }), 413

        # Generate unique filename for video
        video_filename = f"{os.path.splitext(os.path.basename(pptx_path))[0]}_{os.urandom(4).hex()}.mp4"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)

        try:
            success = convert_to_video(pptx_path, video_path)

            if success and os.path.exists(video_path):
                # Verify video file size
                if os.path.getsize(video_path) < 1000:  # Minimum size check
                    raise ValueError("Generated video file is too small")

                # Return URL-safe path for static file
                return jsonify({
                    'video_path':
                    video_path,
                    'video_url':
                    url_for('static', filename=f'uploads/{video_filename}'),
                    'message':
                    'Video generated successfully'
                })

            return jsonify({
                'error':
                'Video conversion failed',
                'details':
                'The conversion process completed but no video was generated'
            }), 500

        except ValueError as e:
            logger.error(f"Validation error during conversion: {str(e)}")
            return jsonify({
                'error': 'Invalid file format or content',
                'details': str(e)
            }), 422

        except RuntimeError as e:
            logger.error(f"Runtime error during conversion: {str(e)}")
            return jsonify({
                'error': 'Conversion process failed',
                'details': str(e)
            }), 500

        except Exception as e:
            logger.error(f"Unexpected error during conversion: {str(e)}",
                         exc_info=True)
            return jsonify({
                'error': 'An unexpected error occurred',
                'details': str(e)
            }), 500

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Failed to process request',
            'details': str(e)
        }), 500
