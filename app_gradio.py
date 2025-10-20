import gradio as gr
import numpy as np
import torch
import logging
import time
from kokoro.pipeline import KPipeline
from script_generator.script_generator import generate_script

logging.basicConfig(level=logging.INFO)

tts_instance = None
kokoro_available = False
SAMPLE_RATE = 24000

try:
    start_time = time.time()
    logging.info("Initializing Kokoro KPipeline...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts_instance = KPipeline(lang_code='a', device=device, repo_id='hexgrad/Kokoro-82M')
    kokoro_available = True
    end_time = time.time()
    logging.info(f"Kokoro KPipeline initialized successfully on device '{device}' in {end_time - start_time:.2f} seconds.")
except Exception as e:
    logging.error(f"Failed to initialize Kokoro KPipeline: {e}", exc_info=True)

voice_options = [
    'af_alloy', 'af_aoede', 'af_bella', 'af_heart', 'af_jessica',
    'af_kore', 'af_nicole', 'af_nova', 'af_river', 'af_sarah', 'af_sky',
    'am_echo', 'bf_alice', 'bm_daniel', 'jf_gongitsune', 'zm_yunxi'
]

def prepare_audio_for_gradio(samples: np.ndarray, sample_rate: int):
    if samples is None or samples.size == 0:
        return None
    if samples.dtype != np.float32:
        samples = samples.astype(np.float32)
    if samples.ndim > 1:
        samples = samples.squeeze()
    max_val = np.max(np.abs(samples))
    if max_val > 1.0:
        samples = samples / max_val
    return (sample_rate, samples)

def generate_podcast_dialogue(text, host_voice, guest_voice):
    if not kokoro_available or tts_instance is None:
        yield None, "Error: TTS Service initialization failed."
        return
    if not text or not text.strip():
        yield None, "Error: Please enter some source text."
        return

    try:
        yield None, "Status: Generating script..."
        script_object = generate_script(text, return_object=True)
        if not script_object:
             yield None, "Error: Script generation failed. Check terminal logs."
             return
        
        voice_map = {
            "Host": host_voice,
            "Guest": guest_voice
        }

        full_audio_chunks = []
        total_paragraphs = sum(len(seg.paragraphs) for seg in script_object.script_segments)
        current_paragraph = 0

        for segment in script_object.script_segments:
            for paragraph in segment.paragraphs:
                current_paragraph += 1
                speaker = paragraph.speaker
                paragraph_text = paragraph.text
                
                selected_voice = voice_map.get(speaker)
                
                if not selected_voice:
                    logging.warning(f"Unknown speaker '{speaker}' found in script. Skipping.")
                    continue

                status_update = f"Status: Synthesizing paragraph {current_paragraph}/{total_paragraphs} (Speaker: {speaker})"
                logging.info(status_update)
                yield None, status_update
                
                synthesis_generator = tts_instance(text=paragraph_text, voice=selected_voice)
                
                for item in synthesis_generator:
                    if hasattr(item, 'output') and hasattr(item.output, 'audio') and item.output.audio is not None:
                        audio_tensor = item.output.audio
                        chunk_samples = audio_tensor.detach().cpu().numpy()
                        full_audio_chunks.append(chunk_samples)
                        yield prepare_audio_for_gradio(chunk_samples, SAMPLE_RATE), status_update

        if not full_audio_chunks:
            yield None, "Error: No audio was generated from the script."
            return

        final_audio = np.concatenate(full_audio_chunks)
        final_status = f"Status: Finished! Total paragraphs: {total_paragraphs}."
        logging.info(final_status)
        yield prepare_audio_for_gradio(final_audio, SAMPLE_RATE), final_status

    except Exception as e:
        error_message = f"An error occurred: {e}"
        logging.error(error_message, exc_info=True)
        yield None, error_message

with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="sky")) as demo:
    gr.Markdown("## ✨ Conversational Podcast Generator ✨")
    gr.Markdown("Enter source text, assign voices to the Host and Guest, and generate a two-person podcast!")
    
    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(label="Source Text", lines=10, placeholder="Paste the article or text you want to convert into a podcast...")
            with gr.Row():
                host_voice_dd = gr.Dropdown(label="Host Voice", choices=voice_options, value=voice_options[0])
                guest_voice_dd = gr.Dropdown(label="Guest Voice", choices=voice_options, value=voice_options[8])
            submit_button = gr.Button("🎙️ Generate Podcast", variant="primary")
        
        with gr.Column(scale=1):
            status_indicator = gr.Markdown("Status: Ready")
            audio_output = gr.Audio(label="Podcast Output", autoplay=True, streaming=True)

    submit_button.click(
        fn=generate_podcast_dialogue,
        inputs=[text_input, host_voice_dd, guest_voice_dd],
        outputs=[audio_output, status_indicator]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)