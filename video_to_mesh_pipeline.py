"""
Video to 3D Mesh Pipeline
A comprehensive automation script that converts drone video files into 3D meshes
using OpenCV, COLMAP, and Open3D.

Author: Senior Computer Vision Engineer
Date: 2025-12-05
"""

import cv2
import os
import subprocess
import shutil
import logging
from pathlib import Path
import open3d as o3d
import numpy as np


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoTo3DMesh:
    """
    Main class for converting video files to 3D meshes using photogrammetry.
    """
    
    def __init__(self, video_path, output_dir="./output", frames_per_second=2):
        """
        Initialize the pipeline.
        
        Args:
            video_path (str): Path to input video file
            output_dir (str): Directory for output files
            frames_per_second (int): Frame extraction rate
        """
        self.video_path = Path(video_path)
        self.output_dir = Path(output_dir)
        self.fps = frames_per_second
        
        # Create directory structure
        self.images_dir = self.output_dir / "images"
        self.colmap_dir = self.output_dir / "colmap"
        self.sparse_dir = self.colmap_dir / "sparse"
        self.dense_dir = self.colmap_dir / "dense"
        self.database_path = self.colmap_dir / "database.db"
        
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories for the pipeline."""
        for directory in [self.images_dir, self.colmap_dir, self.sparse_dir, self.dense_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        logger.info("Created directory structure")
    
    def extract_frames(self):
        """
        Extract frames from video at specified FPS using OpenCV.
        
        Returns:
            int: Number of frames extracted
        """
        try:
            logger.info(f"Opening video: {self.video_path}")
            cap = cv2.VideoCapture(str(self.video_path))
            
            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {self.video_path}")
            
            # Get video properties
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / video_fps
            
            logger.info(f"Video FPS: {video_fps}, Total frames: {total_frames}, Duration: {duration:.2f}s")
            
            # Calculate frame interval
            frame_interval = int(video_fps / self.fps)
            frame_count = 0
            saved_count = 0
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Save frame at specified interval
                if frame_count % frame_interval == 0:
                    frame_filename = self.images_dir / f"frame_{saved_count:06d}.jpg"
                    cv2.imwrite(str(frame_filename), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    saved_count += 1
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Extracted {saved_count} frames to {self.images_dir}")
            return saved_count
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {str(e)}")
            raise
    
    def run_colmap_feature_extraction(self):
        """
        Run COLMAP feature extraction.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Running COLMAP feature extraction...")
            
            cmd = [
                "colmap", "feature_extractor",
                "--database_path", str(self.database_path),
                "--image_path", str(self.images_dir),
                "--ImageReader.single_camera", "1",
                "--ImageReader.camera_model", "RADIAL",
                "--SiftExtraction.use_gpu", "1"
            ]
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info("Feature extraction completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Feature extraction failed: {e.stderr}")
            raise
        except FileNotFoundError:
            logger.error("COLMAP not found. Please ensure COLMAP is installed and in PATH")
            raise
    
    def run_colmap_matching(self):
        """
        Run COLMAP exhaustive matching.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Running COLMAP exhaustive matching...")
            
            cmd = [
                "colmap", "exhaustive_matcher",
                "--database_path", str(self.database_path),
                "--SiftMatching.use_gpu", "1"
            ]
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info("Matching completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Matching failed: {e.stderr}")
            raise
    
    def run_colmap_mapper(self):
        """
        Run COLMAP mapper for sparse reconstruction.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Running COLMAP mapper (sparse reconstruction)...")
            
            # Create model directory
            model_dir = self.sparse_dir / "0"
            model_dir.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                "colmap", "mapper",
                "--database_path", str(self.database_path),
                "--image_path", str(self.images_dir),
                "--output_path", str(self.sparse_dir)
            ]
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info("Sparse reconstruction completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Mapper failed: {e.stderr}")
            raise
    
    def run_colmap_undistorter(self):
        """
        Run COLMAP image undistorter.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Running COLMAP image undistorter...")
            
            # Use the first (and likely only) sparse model
            sparse_model = self.sparse_dir / "0"
            
            cmd = [
                "colmap", "image_undistorter",
                "--image_path", str(self.images_dir),
                "--input_path", str(sparse_model),
                "--output_path", str(self.dense_dir),
                "--output_type", "COLMAP"
            ]
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info("Image undistortion completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Undistorter failed: {e.stderr}")
            raise
    
    def run_colmap_patch_match(self):
        """
        Run COLMAP patch match stereo for dense reconstruction.
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Running COLMAP patch match stereo (dense reconstruction)...")
            
            cmd = [
                "colmap", "patch_match_stereo",
                "--workspace_path", str(self.dense_dir),
                "--workspace_format", "COLMAP",
                "--PatchMatchStereo.geom_consistency", "true"
            ]
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info("Dense reconstruction completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Patch match stereo failed: {e.stderr}")
            raise
    
    def run_colmap_fusion(self):
        """
        Run COLMAP stereo fusion to generate point cloud.
        
        Returns:
            Path: Path to fused point cloud
        """
        try:
            logger.info("Running COLMAP stereo fusion...")
            
            fused_ply = self.dense_dir / "fused.ply"
            
            cmd = [
                "colmap", "stereo_fusion",
                "--workspace_path", str(self.dense_dir),
                "--workspace_format", "COLMAP",
                "--input_type", "geometric",
                "--output_path", str(fused_ply)
            ]
            
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info(f"Stereo fusion completed successfully. Output: {fused_ply}")
            return fused_ply
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Stereo fusion failed: {e.stderr}")
            raise
    
    def post_process_and_mesh(self, point_cloud_path, output_mesh_path):
        """
        Post-process point cloud and generate mesh using Open3D.
        
        Args:
            point_cloud_path (Path): Path to input point cloud
            output_mesh_path (Path): Path to save output mesh
            
        Returns:
            Path: Path to output mesh
        """
        try:
            logger.info(f"Loading point cloud from {point_cloud_path}")
            pcd = o3d.io.read_point_cloud(str(point_cloud_path))
            
            # Get initial point cloud info
            num_points_initial = len(pcd.points)
            logger.info(f"Initial point cloud has {num_points_initial} points")
            
            # Remove statistical outliers (noise reduction)
            logger.info("Removing statistical outliers...")
            pcd_filtered, ind = pcd.remove_statistical_outlier(
                nb_neighbors=20,
                std_ratio=2.0
            )
            
            num_points_filtered = len(pcd_filtered.points)
            logger.info(f"Filtered point cloud has {num_points_filtered} points "
                       f"({num_points_initial - num_points_filtered} outliers removed)")
            
            # Estimate normals for surface reconstruction
            logger.info("Estimating normals...")
            pcd_filtered.estimate_normals(
                search_param=o3d.geometry.KDTreeSearchParamHybrid(
                    radius=0.1,
                    max_nn=30
                )
            )
            
            # Orient normals consistently
            pcd_filtered.orient_normals_consistent_tangent_plane(k=15)
            
            # Poisson surface reconstruction
            logger.info("Running Poisson surface reconstruction...")
            mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
                pcd_filtered,
                depth=9,
                width=0,
                scale=1.1,
                linear_fit=False
            )
            
            # Remove low-density vertices (cleanup)
            logger.info("Cleaning up mesh...")
            densities = np.asarray(densities)
            density_threshold = np.quantile(densities, 0.1)
            vertices_to_remove = densities < density_threshold
            mesh.remove_vertices_by_mask(vertices_to_remove)
            
            # Get mesh statistics
            num_vertices = len(mesh.vertices)
            num_triangles = len(mesh.triangles)
            logger.info(f"Final mesh has {num_vertices} vertices and {num_triangles} triangles")
            
            # Save mesh
            o3d.io.write_triangle_mesh(str(output_mesh_path), mesh)
            logger.info(f"Mesh saved to {output_mesh_path}")
            
            return output_mesh_path
            
        except Exception as e:
            logger.error(f"Post-processing and meshing failed: {str(e)}")
            raise
    
    def run_full_pipeline(self, output_mesh_name="output_mesh.ply"):
        """
        Run the complete pipeline from video to mesh.
        
        Args:
            output_mesh_name (str): Name of output mesh file
            
        Returns:
            Path: Path to final mesh file
        """
        try:
            logger.info("=" * 80)
            logger.info("STARTING VIDEO TO 3D MESH PIPELINE")
            logger.info("=" * 80)
            
            # Step 1: Extract frames
            logger.info("\n[1/7] Extracting frames from video...")
            num_frames = self.extract_frames()
            
            if num_frames < 3:
                raise ValueError(f"Not enough frames extracted ({num_frames}). Need at least 3 frames.")
            
            # Step 2: Feature extraction
            logger.info("\n[2/7] Extracting features...")
            self.run_colmap_feature_extraction()
            
            # Step 3: Feature matching
            logger.info("\n[3/7] Matching features...")
            self.run_colmap_matching()
            
            # Step 4: Sparse reconstruction
            logger.info("\n[4/7] Running sparse reconstruction...")
            self.run_colmap_mapper()
            
            # Step 5: Image undistortion
            logger.info("\n[5/7] Undistorting images...")
            self.run_colmap_undistorter()
            
            # Step 6: Dense reconstruction
            logger.info("\n[6/7] Running dense reconstruction...")
            self.run_colmap_patch_match()
            
            # Step 7: Stereo fusion
            logger.info("\n[7/7] Fusing stereo reconstruction...")
            point_cloud_path = self.run_colmap_fusion()
            
            # Step 8: Post-processing and mesh generation
            logger.info("\n[FINAL] Post-processing and generating mesh...")
            output_mesh_path = self.output_dir / output_mesh_name
            final_mesh = self.post_process_and_mesh(point_cloud_path, output_mesh_path)
            
            logger.info("=" * 80)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info(f"Final mesh saved to: {final_mesh}")
            logger.info("=" * 80)
            
            return final_mesh
            
        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"PIPELINE FAILED: {str(e)}")
            logger.error("=" * 80)
            raise


def main():
    """
    Main entry point for the script.
    """
    # Configuration
    INPUT_VIDEO = "input_video.mp4"
    OUTPUT_DIR = "./output"
    OUTPUT_MESH = "output_mesh.ply"
    FRAMES_PER_SECOND = 2
    
    # Check if input video exists
    if not os.path.exists(INPUT_VIDEO):
        logger.error(f"Input video not found: {INPUT_VIDEO}")
        logger.info("Please place your video file as 'input_video.mp4' in the current directory")
        return
    
    try:
        # Initialize and run pipeline
        pipeline = VideoTo3DMesh(
            video_path=INPUT_VIDEO,
            output_dir=OUTPUT_DIR,
            frames_per_second=FRAMES_PER_SECOND
        )
        
        final_mesh = pipeline.run_full_pipeline(output_mesh_name=OUTPUT_MESH)
        
        logger.info("\n" + "=" * 80)
        logger.info("SUCCESS!")
        logger.info(f"Your 3D mesh is ready: {final_mesh}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"\nFailed to process video: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
