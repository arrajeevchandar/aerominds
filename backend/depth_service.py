import torch
import cv2
import numpy as np
import os

class DepthService:
    def __init__(self):
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        print(f"Using device: {self.device}")
        
        # Load DPT Large model (High Accuracy)
        self.model_type = "DPT_Large"
        self.model = torch.hub.load("intel-isl/MiDaS", self.model_type)
        self.model.to(self.device)
        self.model.eval()
        
        # Load transform
        midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
        self.transform = midas_transforms.dpt_transform

    def process_image(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        input_batch = self.transform(img).to(self.device)
        
        with torch.no_grad():
            prediction = self.model(input_batch)
            
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()
            
        depth_map = prediction.cpu().numpy()
        
        # Apply Bilateral Filter to smooth noise while keeping edges sharp
        # d: Diameter of each pixel neighborhood
        # sigmaColor: Filter sigma in the color space
        # sigmaSpace: Filter sigma in the coordinate space
        depth_map = cv2.bilateralFilter(depth_map, d=5, sigmaColor=75, sigmaSpace=75)
        
        # Normalize depth map for visualization/displacement
        depth_min = depth_map.min()
        depth_max = depth_map.max()
        
        if depth_max - depth_min > 1e-5:
            depth_map = (depth_map - depth_min) / (depth_max - depth_min)
        else:
            depth_map = np.zeros_like(depth_map)
            
        depth_map = (depth_map * 255).astype(np.uint8)
        
        filename = os.path.basename(image_path)
        output_path = f"processed/depth_{filename}"
        cv2.imwrite(output_path, depth_map)
        
        return output_path
