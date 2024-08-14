import requests
import logging
import time
from celery import shared_task, group
from django.conf import settings
from .models import GeneratedImage

logger = logging.getLogger(__name__)

@shared_task
def generate_single_image(prompt, user_id):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.STABILITY_API_KEY}",
    }
    
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
    }
    
    max_retries = 3
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            artifact = data['artifacts'][0]
            image_url = f"data:image/png;base64,{artifact['base64']}"
            
            generated_image = GeneratedImage.objects.create(
                user_id=user_id,
                prompt=prompt,
                image_url=image_url,
                width=payload['width'],
                height=payload['height'],
                cfg_scale=payload['cfg_scale'],
                steps=payload['steps'],
                seed=artifact['seed']
            )
            
            logger.info(f"Successfully generated and stored metadata for image with prompt: {prompt[:30]}...")
            return image_url

        except requests.RequestException as e:
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    logger.warning(f"Rate limit hit. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error("Max retries reached. Unable to generate image due to rate limiting.")
                    return None
            else:
                logger.error(f"API request failed: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Unexpected error occurred: {str(e)}")
            return None

    logger.error("Failed to generate image after multiple attempts.")
    return None

@shared_task
def generate_images_parallel(prompts, user_id):
    # Create a group of tasks, one for each prompt
    job = group(generate_single_image.s(prompt, user_id) for prompt in prompts[:3])
    
    # Execute the group of tasks
    result = job.apply_async()
    
    # Wait for all tasks to complete and get the results
    image_urls = result.get()
    
    # Filter out any None results (failed generations)
    return [url for url in image_urls if url is not None]