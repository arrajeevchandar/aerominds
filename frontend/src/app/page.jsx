"use client";

import { useState } from "react";
import Viewer3D from "@/components/Viewer3D";
import styles from "./brutalist.module.css";

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
        <main className={styles.container}>
            {/* Navigation */}
            <nav className={styles.nav}>
                <div className={styles.logo}>
                    <span>●</span>
                    <span>▼</span>
                    <span>▲</span>
                    <span>✖</span>
                </div>
                <div className={styles.navLinks}>
                    <button className={styles.navLink}>Home</button>
                    <button className={styles.navLink}>History</button>
                    <button className={styles.navLink}>Buildings</button>
                    <button className={styles.navLink}>About Us</button>
                </div>
                <div className={styles.socials}>
                    {/* Placeholder for social icons if needed */}
                </div>
            </nav>

            {/* Hero Section */}
            <section className={styles.hero}>
                <h1 className={styles.heroTitle}>AEROMINDS</h1>
            </section>

            {/* Cards Grid */}
            <div className={styles.cardGrid}>
                {/* Card 1: Upload & Controls (Black Theme) */}
                <div className={styles.card}>
                    <div className={styles.arrow}>↗</div>
                    <div className={styles.uploadSection}>
                        <h2 className={styles.cardTitle}>UPLOAD IMAGERY</h2>
                        <p className={styles.cardText}>
                            RAW, DRONE-CAPTURED IMAGERY REVEALS THE TRUE NATURE OF TERRAIN.
                        </p>

                        <div className="flex flex-col gap-4 mt-4">
                            <input
                                type="file"
                                accept="image/*"
                                onChange={handleFileChange}
                                className={styles.fileInput}
                            />
                            {previewUrl && (
                                <div className="relative aspect-video w-full overflow-hidden border border-gray-700">
                                    <img
                                        src={previewUrl}
                                        alt="Preview"
                                        className="object-cover w-full h-full grayscale hover:grayscale-0 transition-all"
                                    />
                                </div>
                            )}
                        </div>

                        <button
                            onClick={handleUpload}
                            disabled={!selectedFile || loading}
                            className={styles.actionButton}
                        >
                            {loading ? "PROCESSING..." : "GENERATE 3D MODEL"}
                        </button>
                    </div>
                </div>

                {/* Card 2: 3D Viewer (Light Theme) */}
                <div className={`${styles.card} ${styles.cardLight}`}>
                    <div className={styles.arrow}>↗</div>
                    <h2 className={styles.cardTitle}>3D VISUALIZATION</h2>
                    <p className={styles.cardText}>
                        EXPLORE THE RECONSTRUCTED MODEL IN THREE DIMENSIONS.
                    </p>
                    <div className={styles.viewerContainer}>
                        {depthUrl && previewUrl ? (
                            <Viewer3D imageUrl={previewUrl} depthUrl={depthUrl} />
                        ) : (
                            <div className="flex items-center justify-center h-full text-center p-4">
                                <p className="font-mono text-sm">WAITING FOR INPUT DATA...</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Card 3: Info (Light Theme) */}
                <div className={`${styles.card} ${styles.cardLight}`}>
                    <div className={styles.arrow}>↗</div>
                    <h2 className={styles.cardTitle}>THE PROJECT</h2>
                    <p className={styles.cardText}>
                        EXPERIENCE THE POWERFUL CAPABILITIES OF AERIAL RECONSTRUCTION.
                        <br /><br />
                        JOIN US ON A JOURNEY THROUGH DIGITAL TWINS AND PHOTOGRAMMETRY.
                    </p>
                    <div className="mt-auto text-4xl font-black opacity-20">
                        ”
                    </div>
                </div>
            </div>
        </main>
    );
}
