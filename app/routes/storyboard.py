"""
Storyboard Routes

API endpoints for storyboard generation.
"""
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.models import StoryboardRequest
from app.services import StoryboardService

storyboard_bp = Blueprint('storyboard', __name__, url_prefix='/storyboard')


@storyboard_bp.route('/generate', methods=['POST'])
def generate_storyboard():
    """
    Generate a complete storyboard with sequential images and PDF.
    
    Request Body:
        user_description (str): The text description of the video sequence
    
    Returns:
        JSON response with generation status and PDF path
    
    Raises:
        400: If request validation fails
        500: If storyboard generation fails
    """
    try:
        # Parse and validate request body
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate using Pydantic model
        storyboard_request = StoryboardRequest(**data)
        
        # Generate complete storyboard using service
        service = StoryboardService()
        response = service.generate_complete_storyboard(
            storyboard_request.user_description
        )
        
        # Return response based on success
        status_code = 200 if response.success else 500
        return jsonify(response.model_dump()), status_code
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation error', 
            'details': e.errors()
        }), 400
    
    except (ValueError, TypeError, KeyError) as e:
        return jsonify({'error': f'Invalid request: {str(e)}'}), 400
    
    except (IOError, OSError) as e:
        return jsonify({'error': f'Service error: {str(e)}'}), 500
