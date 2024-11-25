# AI-Powered infographic Generator

An advanced infographic generation system that leverages AI to create dynamic infographics with animations, video conversion capabilities, and RAG-based content enhancement.

## 🚀 Features

- **Smart Content Generation**: Uses RAG (Retrieval Augmented Generation) for enhanced content creation
- **Dynamic Animations**: Automatically generates relevant animations for slides
- **Video Conversion**: Converts infographics to video format
- **Multiple Template Styles**: Supports various infographic templates
- **CSV Data Integration**: Processes CSV data for data-driven infographics
- **Memory Efficient**: Optimized for handling large datasets

## 🛠️ Tech Stack

- **Python 3.8+**
- **OpenAI GPT-4**: For content generation and enhancement
- **LlamaIndex**: For RAG implementation
- **python-pptx**: For infographic generation
- **MoviePy**: For video processing
- **Matplotlib**: For animation generation
- **Pandas**: For data processing
- **ImageMagick**: For image processing
- **NumPy**: For numerical operations

## 📋 Prerequisites

1. Python 3.8 or higher
2. ImageMagick installed on your system
3. OpenAI API key
4. Sufficient system memory (recommended 8GB+)

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/azharlabs/infographic-video-generation.git
cd infographic-video-generation
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file with your OpenAI API key and other configurations
```

## 📝 Usage

### 1. RAG-Based Content Processing

```python
from utils.csv_rag import EnhancedDocumentRAG

# Initialize RAG system
rag = EnhancedDocumentRAG(
    documents_path="path/to/documents",
    model_name="gpt-4",
    chunk_size=1024
)

# Process content
context = rag.retrieve_context("your query")
response = rag.generate_comprehensive_response(query="your query")
```

### 2. infographic Generation

```python
from utils.pptx_generator import create_infographic

# Generate infographic
content = """
Title Slide
• Point 1
• Point 2
• Point 3

Second Slide
• Another point
• More information
"""

prs = create_presentation(
    content=content,
    template_name="modern"
)

```

### 3. Animation Generation

```python
from utils.animation_generator import generate_slide_animation

# Generate animation for a slide
animation_path = generate_slide_animation(
    "Content for animation generation"
)
```

### 4. Video Conversion

```python
from utils.video_converter import convert_to_video

# Convert PPTX to video
convert_to_video(
    "infographic.pptx",
    "output_video.mp4"
)
```

## 🎨 Available Templates

- modern
- professional
- minimal
- gradient
- corporate
- creative
- dynamic
- clean
- dark
- tech

## 🔄 Processing Flow

1. **Content Input**: Raw text or CSV data input
2. **RAG Processing**: 
   - Document chunking
   - Embedding generation
   - Context retrieval
3. **infographic Generation**:
   - Template application
   - Slide creation
   - Content formatting
4. **Animation Integration**:
   - Dynamic animation generation
   - GIF creation
   - Slide integration
5. **Video Conversion**:
   - Slide processing
   - Transition effects
   - Final video compilation

## 💾 Memory Management

The system implements several memory optimization techniques:
- Batch processing for large datasets
- Garbage collection after processing
- Efficient chunking strategies
- Memory monitoring and cleanup

## ⚠️ Known Limitations

- Maximum infographic size depends on available system memory
- Video conversion requires significant processing power
- Some animations may be resource-intensive
- ImageMagick must be properly configured

## 🔍 Troubleshooting

### Common Issues:

1. **Memory Errors**:
   - Reduce batch_size in RAG processing
   - Increase chunk_overlap
   - Free system memory

2. **Animation Generation Fails**:
   - Verify ImageMagick installation
   - Check system resources
   - Reduce animation complexity

3. **Video Conversion Issues**:
   - Ensure sufficient disk space
   - Check codec availability
   - Verify file permissions

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- LlamaIndex team for RAG capabilities
- MoviePy contributors
- Python-PPTX maintainers
