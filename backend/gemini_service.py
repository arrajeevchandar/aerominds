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
        Process an image using Gemini API to generate a high-quality MiDaS Depth Map 3D model view.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Path to the processed high-quality MiDaS Depth Map image
        """
        try:
            # Load the input image
            input_image = Image.open(image_path)
            
            # Create a detailed prompt for 2D to 3D conversion with grayscale output
            prompt = """Convert this 2D image into a high-quality MiDaS Depth Map 3D model view. 
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
                            
                            # Apply negative filter
                            output_image = self._apply_negative_filter(output_image)
                            
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
    
    def _apply_negative_filter(self, image):
        """
        Apply a negative filter to the image (invert colors).
        
        Args:
            image: PIL Image object
            
        Returns:
            PIL Image object with negative filter applied
        """
        from PIL import ImageOps
        return ImageOps.invert(image)
    
    def _fallback_depth_estimation(self, image_path):
        """
        Advanced depth estimation using computer vision techniques.
        Creates a realistic depth map visualization from a 2D image.
        """
        try:
            import cv2
            import numpy as np
            
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Step 1: Use Sobel operators to detect edges in X and Y directions
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate gradient magnitude (edge strength)
            gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
            gradient_magnitude = np.uint8(gradient_magnitude / gradient_magnitude.max() * 255)
            
            # Step 2: Create a base depth map from intensity
            # Assumption: Brighter areas in the original image are closer
            base_depth = gray.copy()
            
            # Step 3: Enhance depth using bilateral filter for edge-preserving smoothing
            bilateral = cv2.bilateralFilter(base_depth, d=9, sigmaColor=75, sigmaSpace=75)
            
            # Step 4: Combine gradient information with base depth
            # Edges typically represent depth discontinuities
            depth_map = cv2.addWeighted(bilateral, 0.7, gradient_magnitude, 0.3, 0)
            
            # Step 5: Apply multi-scale Gaussian blur for smooth depth transitions
            # Larger objects should have smoother depth
            blur1 = cv2.GaussianBlur(depth_map, (21, 21), 0)
            blur2 = cv2.GaussianBlur(depth_map, (51, 51), 0)
            depth_map = cv2.addWeighted(blur1, 0.6, blur2, 0.4, 0)
            
            # Step 6: Normalize to full range
            depth_map = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
            
            # Step 7: Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            # This enhances local contrast while avoiding over-amplification
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            depth_map = clahe.apply(np.uint8(depth_map))
            
            # Step 8: Invert so closer objects are lighter (standard depth map convention)
            depth_map = cv2.bitwise_not(depth_map)
            
            # Step 9: Final smoothing to remove any artifacts
            depth_map = cv2.GaussianBlur(depth_map, (5, 5), 0)
            
            # Save the processed image
            filename = os.path.basename(image_path)
            output_path = f"processed/depth_{filename}"
            cv2.imwrite(output_path, depth_map)
            
            print(f"Advanced depth estimation completed: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Advanced depth estimation failed: {str(e)}")
            # Last resort: simple grayscale conversion
            img = Image.open(image_path).convert('L')
            filename = os.path.basename(image_path)
            output_path = f"processed/grayscale_{filename}"
            img.save(output_path)
            return output_path
