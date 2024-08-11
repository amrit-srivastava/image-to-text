
import requests
import logging
from celery import shared_task
from django.conf import settings
from .models import GeneratedImage

logger = logging.getLogger(__name__)

@shared_task
def generate_image(prompt, user_id):
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
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        data = response.json()
        image_data = data['artifacts'][0]
        
        image_url = f"https://example.com/images/{image_data['seed']}.png"
        
        # Store the generated image metadata in the database
        GeneratedImage.objects.create(
            user_id=user_id,
            prompt=prompt,
            image_url=image_url,
            width=payload['width'],
            height=payload['height'],
            cfg_scale=payload['cfg_scale'],
            steps=payload['steps'],
            seed=image_data['seed']
        )
        
        logger.info(f"Successfully generated and stored metadata for image with prompt: {prompt[:30]}...")
        return image_url
    except requests.RequestException as e:
        logger.error(f"API request failed for prompt '{prompt[:30]}...': {str(e)}")
        return None
    except KeyError as e:
        logger.error(f"Unexpected API response structure for prompt '{prompt[:30]}...': {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error occurred for prompt '{prompt[:30]}...': {str(e)}")
        return None

@shared_task
def generate_images_parallel(prompts, user_id):
    results = []
    for prompt in prompts:
        try:
            result = generate_image.delay(prompt, user_id)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to create task for prompt '{prompt[:30]}...': {str(e)}")
    return [result.id for result in results]