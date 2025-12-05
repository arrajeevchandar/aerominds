import google.generativeai as genai
import os
from PIL import Image
import io
import base64
from dotenv import load_dotenv

class GeminiService:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please add it to .env file.")
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the model for image generation
        # Using gemini-2.0-flash-exp for image generation capabilities
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        print("GeminiService initialized successfully")

    def process_image(self, image_path):
        """
        Process an image using Gemini API to generate a high-quality grayscale 3D model view.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Path to the processed grayscale 3D model image
        """
        try:
            # Load the input image
            input_image = Image.open(image_path)
            
            # Create a detailed prompt for 2D to 3D conversion with grayscale output
            prompt = """Convert this 2D image into a high-quality grayscale 3D model view. 
            Create a depth map visualization where:
            - Lighter areas represent surfaces closer to the camera
            - Darker areas represent surfaces farther from the camera
            - The output should be grayscale (black and white)
            - Maintain smooth transitions between depth levels
            - Preserve important structural details and edges
            - The result should look like a professional 3D depth map suitable for 3D modeling
            
            Generate a clean, high-contrast grayscale depth map that clearly shows the 3D structure of the scene."""
            
            # Generate content using Gemini
            response = self.model.generate_content([prompt, input_image])
            
            # Check if the response contains image data
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                
                # Try to extract image from the response
                # Note: Gemini 2.0 may return text descriptions instead of images
                # We'll need to handle this appropriately
                
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data'):
                            # Found inline image data
                            image_data = part.inline_data.data
                            mime_type = part.inline_data.mime_type
                            
                            # Decode and save the image
                            output_image = Image.open(io.BytesIO(base64.b64decode(image_data)))
                            
                            # Convert to grayscale if not already
                            if output_image.mode != 'L':
                                output_image = output_image.convert('L')
                            
                            # Save the processed image
                            filename = os.path.basename(image_path)
                            output_path = f"processed/gemini_3d_{filename}"
                            output_image.save(output_path)
                            
                            print(f"Successfully processed image: {output_path}")
                            return output_path
            
            # If we get here, the API didn't return an image
            # Fall back to creating a depth map style visualization using the original approach
            print("Warning: Gemini API didn't return an image. Using fallback depth estimation.")
            return self._fallback_depth_estimation(image_path)
            
        except Exception as e:
            print(f"Error processing image with Gemini API: {str(e)}")
            print("Falling back to basic depth estimation")
            return self._fallback_depth_estimation(image_path)
    
    def _fallback_depth_estimation(self, image_path):
        """
        Fallback method using basic image processing to create a depth-like visualization.
        This is used if the Gemini API fails or doesn't return an image.
        """
        try:
            import cv2
            import numpy as np
            
            # Load image
            img = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection to enhance structure
            edges = cv2.Canny(gray, 50, 150)
            
            # Apply Gaussian blur to create smooth depth-like effect
            depth_map = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # Invert if needed to make closer objects lighter
            depth_map = cv2.bitwise_not(depth_map)
            
            # Enhance contrast
            depth_map = cv2.equalizeHist(depth_map)
            
            # Save the processed image
            filename = os.path.basename(image_path)
            output_path = f"processed/depth_{filename}"
            cv2.imwrite(output_path, depth_map)
            
            print(f"Fallback processing completed: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Fallback processing also failed: {str(e)}")
            # Last resort: just copy the original as grayscale
            img = Image.open(image_path).convert('L')
            filename = os.path.basename(image_path)
            output_path = f"processed/grayscale_{filename}"
            img.save(output_path)
            return output_path
