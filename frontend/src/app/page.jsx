"use client";

import { useState } from "react";
import Viewer3D from "@/components/Viewer3D";

export default function Home() {
    const [selectedFile, setSelectedFile] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [depthUrl, setDepthUrl] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            setSelectedFile(file);
            setPreviewUrl(URL.createObjectURL(file));
            setDepthUrl(null); // Reset depth map when new file is selected
        }
    };

    const handleUpload = async () => {
        if (!selectedFile) return;

        setLoading(true);
        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            console.log("Attempting upload to http://127.0.0.1:8000/upload");
            const response = await fetch("http://127.0.0.1:8000/upload", {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                console.log("Upload successful:", data);
                // Ensure URLs are also using 127.0.0.1 if backend returns localhost
                const depthUrl = data.depth_map_url.replace("localhost", "127.0.0.1");
                setDepthUrl(depthUrl);
            } else {
                console.error("Upload failed with status:", response.status);
                alert(`Upload failed: Server returned ${response.status}`);
            }
        } catch (error) {
            console.error("Error uploading file:", error);
            alert(`Network Error: Failed to reach the server. Make sure the backend is running on port 8000.\nDetails: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="flex min-h-screen flex-col items-center p-8 bg-black text-white">
            <h1 className="text-4xl font-bold mb-8 bg-gradient-to-r from-blue-500 to-purple-500 bg-clip-text text-transparent">
                Drone 3D Scene Reconstruction
            </h1>

            <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Control Panel */}
                <div className="flex flex-col gap-6 p-6 bg-gray-900 rounded-xl border border-gray-800">
                    <h2 className="text-2xl font-semibold">1. Upload Image</h2>
                    <div className="flex flex-col gap-4">
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleFileChange}
                            className="block w-full text-sm text-gray-400
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-600 file:text-white
                hover:file:bg-blue-700
                cursor-pointer"
                        />
                        {previewUrl && (
                            <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-gray-700">
                                <img
                                    src={previewUrl}
                                    alt="Preview"
                                    className="object-cover w-full h-full"
                                />
                            </div>
                        )}
                        <button
                            onClick={handleUpload}
                            disabled={!selectedFile || loading}
                            className={`py-3 px-6 rounded-lg font-semibold transition-all ${!selectedFile || loading
                                ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                                : "bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-blue-500/25"
                                }`}
                        >
                            {loading ? "Processing..." : "Generate 3D Model"}
                        </button>
                    </div>
                </div>

                {/* 3D Viewer Panel */}
                <div className="flex flex-col gap-6 p-6 bg-gray-900 rounded-xl border border-gray-800 md:col-span-2 lg:col-span-1 lg:col-start-2 lg:row-start-1 lg:row-span-2">
                    <h2 className="text-2xl font-semibold">2. 3D View</h2>
                    <div className="w-full aspect-square bg-black rounded-lg border border-gray-800 flex items-center justify-center overflow-hidden relative">
                        {depthUrl && previewUrl ? (
                            <Viewer3D imageUrl={previewUrl} depthUrl={depthUrl} />
                        ) : (
                            <div className="text-gray-600 text-center p-4">
                                <p>Upload and process an image to view the 3D model</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </main>
    );
}
