import instructor
from instructor.exceptions import InstructorRetryException
import openai
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Optional
from dotenv import load_dotenv
import sys
from pathlib import Path
import logging
import json 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from src.schemas.poadcast import Poadcast

load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable not set.")

SCRIPTER_MODEL = os.getenv("SCRIPTER_MODEL", "gemini-2.5-flash-preview-05-20")

prompt_dir = Path(__file__).parent / "prompts"
env = Environment(loader=FileSystemLoader(prompt_dir), autoescape=select_autoescape())

client = openai.OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def call_gemini_for_json_string(system_prompt: str, user_prompt: str) -> Optional[str]:
    """
    Calls the Gemini model to get a raw JSON string as a text response.
    """
    try:
        logger.info("Calling Gemini API for a raw JSON string...")
        response = client.chat.completions.create(
            model=SCRIPTER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.0,
            top_p=1.0,
            max_tokens=8000
        )
        logger.info("Gemini API call successful.")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling raw Gemini API: {e}")
        return None

def generate_script(source_text: str, return_object: bool = False) -> Optional:
    """
    Generates a podcast script by manually parsing a JSON string from the API.
    """
    try:
        system_template = env.get_template("system_prompt.jinja2")
        user_template = env.get_template("user_prompt.jinja2")
        system_prompt_rendered = system_template.render()
        user_prompt_rendered = user_template.render(source_text=source_text)

        logger.info("Generating podcast script...")
        
        json_string = call_gemini_for_json_string(
            system_prompt=system_prompt_rendered,
            user_prompt=user_prompt_rendered,
        )

        if not json_string:
            logger.error("API did not return any content.")
            return None

        try:
            if json_string.strip().startswith("```json"):
                json_string = json_string.strip()[7:-3]
            
            parsed_json = json.loads(json_string)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from API response: {e}")
            logger.error(f"Received malformed string: {json_string}")
            return None

        poadcast_data = Poadcast.model_validate(parsed_json)
        
        if return_object:
            return poadcast_data

        script_parts = [f"{poadcast_data.title}\n"]
        if poadcast_data.summary:
            script_parts.append(f"{poadcast_data.summary}\n")
        for segment in poadcast_data.script_segments:
            if segment.segment_title:
                script_parts.append(f"{segment.segment_title}\n")
            for paragraph in segment.paragraphs:
                script_parts.append(paragraph.text)
        
        logger.info("Script formatted.")
        return "\n".join(script_parts)

    except Exception as e:
        logger.error(f"Failed to generate script during validation or formatting: {e}")
        return None