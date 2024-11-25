import re
import os
import logging
from openai import OpenAI
import matplotlib

matplotlib.use('Agg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI()


def extract_code_block(content: str) -> str:
    """Extract code block from Claude's response."""
    code_pattern = r"```python\n(.*?)```"
    matches = re.findall(code_pattern, content, re.DOTALL)
    return matches[0] if matches else ""


def generate_slide_animation(content: str, max_retries: int = 3) -> str:
    """Generate matplotlib animation based on the content and return the file path"""

    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                              'static', 'animations')
    os.makedirs(output_dir, exist_ok=True)

    # Generate unique filename
    import uuid
    gif_path = os.path.join(output_dir,
                            f'animation_{uuid.uuid4().hex[:8]}.gif')

    animation_prompt = f"""You are a Python animation code generator. Based on this text: "{content}", generate ONLY a complete, runnable matplotlib animation code that:
1. Creates a relevant animated visualization
2. Uses proper titles and labels
3. Saves as GIF
4. No explanations, just code
5. Save animation to the specified file path

Example of expected format:
```python
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Setup the figure and data
fig, ax = plt.subplots(figsize=(10, 6))
data = [10, 20, 30, 40, 50]
x = np.arange(len(data))

def animate(frame):
    ax.clear()
    new_data = [d + frame for d in data]
    ax.bar(x, new_data)
    ax.set_title('Sample Animation')
    ax.set_ylim(0, 100)
    return ax,

anim = animation.FuncAnimation(fig, animate, frames=30, interval=100)
writer = animation.PillowWriter(fps=15)
anim.save('{gif_path}', writer=writer)
plt.close()
```

Note: save the git in this path only `{gif_path}`

Follow this exact structure but create an appropriate visualization for: {content}. Return ONLY the code, no explanations."""

    # try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role":
            "system",
            "content":
            "You are a code generator. Output only executable Python code, no explanations."
        }, {
            "role": "user",
            "content": animation_prompt
        }],
        max_tokens=1500,
        temperature=0.7)

    # Safely extract code from response
    if not response or not response.choices or not response.choices[0].message:
        logger.error("Invalid response from OpenAI API")
        raise ValueError("Failed to get valid response from OpenAI")

    content = response.choices[0].message.content
    if not content:
        logger.error("Empty response content from OpenAI API")
        raise ValueError("Empty response from OpenAI")

    animation_code = content.strip().replace("```python",
                                             "").replace("```", "")
    print(animation_code)
    # Setup execution environment with the gif_path
    exec_globals = {
        'plt': plt,
        'animation': animation,
        'np': np,
        'gif_path': gif_path
    }

    # Execute the code
    exec(animation_code, exec_globals)

    # Close all figures to prevent memory leaks
    plt.close('all')

    # Verify the file was created
    if os.path.exists(gif_path):
        return gif_path
    else:
        raise FileNotFoundError(
            f"Animation file was not created at {gif_path}")

    # except Exception as e:
    #     logger.error(f"Error creating animation: {str(e)}")
    #     # Create a fallback static image
    #     try:
    #         fig, ax = plt.subplots(figsize=(8, 6))
    #         ax.text(0.5,
    #                 0.5,
    #                 "Animation Generation Failed",
    #                 horizontalalignment='center',
    #                 verticalalignment='center')
    #         ax.axis('off')

    #         # Save to file instead of BytesIO
    #         fallback_path = gif_path.replace('.gif', '_fallback.png')
    #         plt.savefig(fallback_path)
    #         plt.close()

    #         return fallback_path if os.path.exists(fallback_path) else ""

    #     except Exception as fallback_error:
    #         logger.error(
    #             f"Fallback image creation failed: {str(fallback_error)}")
    #         return ""


def create_animations_for_content(content: str, output_dir: str) -> list:
    """Create animations for each section of content with proper cleanup"""
    animations = []
    temp_files = []
    sections = content.split('\n\n')

    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        for i, section in enumerate(sections):
            if section.strip():
                animation_path = generate_slide_animation(section)

                if animation_path and os.path.exists(animation_path):
                    animations.append(animation_path)
                    temp_files.append(animation_path)
                else:
                    logger.warning(
                        f"Failed to create animation for section {i}")

        return animations

    except Exception as e:
        logger.error(f"Error in animation creation process: {str(e)}")
        # Clean up any partially created files
        for file in temp_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    logger.debug(f"Cleaned up temporary file: {file}")
            except Exception as cleanup_error:
                logger.warning(
                    f"Failed to clean up file {file}: {str(cleanup_error)}")
        return []
