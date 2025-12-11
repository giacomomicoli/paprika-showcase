"""
Storyboard Streaming Routes

API endpoints for storyboard generation with real-time progress streaming.
"""
import json
from flask import Blueprint, Response, request, stream_with_context, jsonify
from pydantic import ValidationError

from app.models import StoryboardRequest, FrameEditRequest, FrameEditResponse
from app.services import StreamingStoryboardService, ImageGenerationService, PDFGenerator

storyboard_stream_bp = Blueprint('storyboard_stream', __name__, url_prefix='/storyboard')


@storyboard_stream_bp.route('/generate-stream', methods=['POST'])
def generate_storyboard_stream():
    """
    Generate a complete storyboard with Server-Sent Events for real-time progress.
    
    Request Body:
        user_description (str): The text description of the video sequence
    
    Returns:
        Server-Sent Events stream with progress updates and final result
    """
    try:
        # Parse and validate request body
        data = request.get_json()
        if not data:
            return Response(
                f"data: {json.dumps({'type': 'error', 'message': 'Request body is required'})}\n\n",
                mimetype='text/event-stream'
            )
        
        # Validate using Pydantic model
        storyboard_request = StoryboardRequest(**data)
        
        def generate():
            service = StreamingStoryboardService()
            
            for event in service.generate_complete_storyboard_stream(
                storyboard_request.user_description
            ):
                yield f"data: {json.dumps(event)}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except ValidationError as e:
        error_response = json.dumps({
            'type': 'error',
            'message': 'Validation error',
            'details': str(e.errors())
        })
        return Response(
            f"data: {error_response}\n\n",
            mimetype='text/event-stream'
        )
    
    except (ValueError, TypeError, KeyError) as e:
        error_response = json.dumps({
            'type': 'error',
            'message': f'Invalid request: {str(e)}'
        })
        return Response(
            f"data: {error_response}\n\n",
            mimetype='text/event-stream'
        )


@storyboard_stream_bp.route('/edit-frame', methods=['POST'])
def edit_frame():
    """
    Edit a single frame in an existing storyboard.
    
    Request Body:
        session_id (str): The session ID of the storyboard
        frame_number (int): The frame number to edit (1-based)
        edit_instructions (str): Instructions for how to edit the frame
        storyboard_context (str): The original storyboard description for context
    
    Returns:
        JSON response with success status and updated frame path
    """
    try:
        # Parse and validate request body
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        # Validate using Pydantic model
        edit_request = FrameEditRequest(**data)
        
        # Initialize services
        image_service = ImageGenerationService()
        pdf_generator = PDFGenerator()
        
        # Delete existing PDF since we're modifying the storyboard
        image_service.delete_pdf(edit_request.session_id)
        
        # Edit the frame
        edited_frame_path = image_service.edit_frame(
            session_id=edit_request.session_id,
            frame_number=edit_request.frame_number,
            edit_instructions=edit_request.edit_instructions,
            storyboard_context=edit_request.storyboard_context
        )
        
        # Regenerate PDF with updated frames
        frame_paths = image_service.get_session_frame_paths(edit_request.session_id)
        pdf_path = pdf_generator.create_storyboard_pdf(
            image_paths=frame_paths,
            session_id=edit_request.session_id
        )
        
        response = FrameEditResponse(
            success=True,
            message=f'Frame {edit_request.frame_number} edited successfully',
            frame_number=edit_request.frame_number,
            image_path=edited_frame_path,
            pdf_regenerated=True
        )
        
        return jsonify(response.model_dump())
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': 'Validation error',
            'details': str(e.errors())
        }), 400
    
    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 404
    
    except (ValueError, IOError, OSError) as e:
        return jsonify({
            'success': False,
            'message': f'Frame edit failed: {str(e)}'
        }), 500
