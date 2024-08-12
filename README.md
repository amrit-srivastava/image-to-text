# Text-to-Image Generator

This Django project utilizes the Stability AI API to generate images based on text prompts. It features a web interface where users can input prompts, generate images, and view their previously generated images.

## Features

- User authentication (signup, login, logout)
- Generate up to 3 images simultaneously using text prompts
- View history of generated images
- Asynchronous image generation using Celery and Redis

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.8+
- pip (Python package manager)
- Redis server
- Stability AI API key

## Local Setup

Follow these steps to set up the project locally:

1. Clone the repository:
   ```
   git clone https://github.com/amrit-srivastava/image-to-text.git
   cd image-to-text
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add the following:
   ```
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   STABILITY_API_KEY=your_stability_ai_api_key
   ```

5. Run database migrations:
   ```
   python manage.py migrate
   ```

6. Start the Redis server:
   ```
   redis-server
   ```

7. Start the Celery worker:
   ```
   celery -A text_to_image_project worker --loglevel=info
   ```

8. Run the Django development server:
   ```
   python manage.py runserver
   ```

9. Access the application at `http://localhost:8000`

## Usage

1. Sign up for an account or log in if you already have one.
2. On the home page, enter up to 3 text prompts for image generation.
3. Click "Generate Images" to create images based on your prompts.
4. View your generated images on the home page.

## Configuration

You can adjust the following settings in `text_to_image_project/settings.py`:

- `STABILITY_API_KEY`: Your Stability AI API key.
- `STABILITY_API_RATE_LIMIT`: Configure the rate limiting for API requests.
- `CELERY_BROKER_URL`: Set the URL for your Celery broker (default is Redis).

## Troubleshooting

- If you encounter rate limiting issues, adjust the `STABILITY_API_RATE_LIMIT` settings.
- Ensure Redis is running before starting the Celery worker.
- Check the console and Celery logs for any error messages.

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Stability AI](https://stability.ai/) for providing the image generation API.
- [Django](https://www.djangoproject.com/) web framework.
- [Celery](https://docs.celeryproject.org/) for asynchronous task processing.
