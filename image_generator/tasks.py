# image_generator/tasks.py

import requests
import logging
from celery import shared_task
from django.conf import settings
from .models import GeneratedImage

logger = logging.getLogger(__name__)

@shared_task
def generate_images_parallel(prompts, user_id):
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.STABILITY_API_KEY}",
    }
    
    payload = {
        "text_prompts": [{"text": prompt} for prompt in prompts[:3]],  # Limit to first 3 prompts
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for i, artifact in enumerate(data['artifacts']):
            image_url = f"data:image/png;base64,{artifact['base64']}"
            
            generated_image = GeneratedImage.objects.create(
                user_id=user_id,
                prompt=prompts[i],
                image_url=image_url,
                width=payload['width'],
                height=payload['height'],
                cfg_scale=payload['cfg_scale'],
                steps=payload['steps'],
                seed=artifact['seed']
            )
            
            results.append(image_url)
            logger.info(f"Successfully generated and stored metadata for image with prompt: {prompts[i][:30]}...")
        
        return results
    except requests.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        return []