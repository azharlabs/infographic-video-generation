import re
from openai import OpenAI
import matplotlib
# Use Agg backend to avoid tkinter issues
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os
import logging
from matplotlib.animation import PillowWriter

logger = logging.getLogger(__name__)

def extract_code_block(content: str) -> str:
    """Extract code block from Claude's response."""
    code_pattern = r"```python\n(.*?)```"
    matches = re.findall(code_pattern, content, re.DOTALL)
    return matches[0] if matches else ""

def create_animation(prompt, output_path):
    """Generate matplotlib animation based on the prompt"""
    try:
        API_KEY = os.getenv('OPENAI_API_KEY')
        if not API_KEY:
            logger.error("OpenAI API key not found")
            return None
            
        client = OpenAI(api_key=API_KEY)
        
        animation_prompt = f"""You are a Python animation code generator. Based on this text: "{prompt}", generate ONLY a complete, runnable matplotlib animation code that:
        1. Creates a relevant animated visualization
        2. Uses proper titles and labels
        3. Saves as GIF
        4. No explanations, just code
        5. Always save GIF as '{output_path}'

        Follow this exact structure but create an appropriate visualization for: {prompt}. Return ONLY the code, no explanations."""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a code generator. Output only executable Python code, no explanations."},
                {"role": "user", "content": animation_prompt}
            ],
            max_tokens=1500,
            temperature=0.7
        )
        
        animation_code = response.choices[0].message.content.strip().replace("```python", "").replace("```", "")
        
        # Create a clean namespace for execution
        exec_globals = {
            'plt': plt,
            'animation': animation,
            'np': np,
            'PillowWriter': PillowWriter,
            'output_path': output_path
        }
        
        # Ensure proper cleanup
        try:
            exec(animation_code, exec_globals)
            plt.close('all')  # Clean up all figures
            logger.info(f"Animation created successfully: {output_path}")
            return output_path
        finally:
            plt.close('all')  # Ensure cleanup even if there's an error
            
    except Exception as e:
        logger.error(f"Error creating animation: {str(e)}")
        # Create a simple error animation
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, "Animation Generation Failed", 
                horizontalalignment='center', verticalalignment='center')
        ax.axis('off')
        plt.savefig(output_path)
        plt.close()
        return output_path
