# Dataset Engineering Toolkit

A standalone research tool for preparing raw CCTV and dashcam videos into clean, organized datasets suitable for YOLOv8 transfer learning.

## Overview

This toolkit automates the transformation of raw video files into high-quality datasets for computer vision model training. It's specifically designed for the Aetheris Traffic Monitoring System but can be used with any video dataset.

### Workflow

```
Raw CCTV Video
    ↓
Frame Extraction (configurable intervals)
    ↓
Blur Detection & Removal (Laplacian variance)
    ↓
Duplicate Detection & Removal (histogram comparison)
    ↓
Metadata Generation (CSV + JSON statistics)
    ↓
Dataset Organization (automatic folder structure)
    ↓
Annotation (CVAT / Label Studio / Roboflow)
    ↓
YOLO Dataset
    ↓
Transfer Learning
    ↓
Production Model
```

## Features

### ✅ Frame Extraction
- Extract frames from MP4, AVI, MOV, MKV videos
- Configurable extraction intervals:
  - Every X seconds
  - Every X frames
- Automatic filename generation (e.g., `video_000001.jpg`)
- Video metadata display:
  - Resolution
  - FPS (frames per second)
  - Duration
  - Total frames
  - Codec

### ✅ Blur Detection
- **Method**: Laplacian variance
- Automatic detection of blurry frames
- Configurable blur threshold (50-500)
- Blur scores recorded in metadata
- Automatic removal of blurry images
- Improves model training quality

### ✅ Duplicate Detection
- **Method**: Histogram comparison (SSIM-based)
- Detects near-duplicate consecutive frames
- Configurable similarity threshold (0.80-1.00)
- Automatic removal of duplicates
- Reduces redundancy in dataset

### ✅ Metadata Generation
- **CSV Export**: `metadata.csv` with all frame information
- **JSON Report**: `statistics.json` with extraction summary
- Columns tracked:
  - Filename
  - Frame number
  - Frame index
  - Time in seconds
  - Blur score
  - Duplicate status
  - Keep/remove status

### ✅ Dataset Organization
- Automatic folder structure creation
- Support for custom categories:
  - Morning
  - Afternoon
  - Rain
  - Night
- Train/validation/test split folders
- Ready for annotation tools

### ✅ User Interface
- Modern desktop application (CustomTkinter)
- Dark theme
- Real-time progress tracking
- Live extraction logs
- Statistics dashboard
- Video metadata display
- Responsive layout

## Installation

### Prerequisites
- Python 3.8+
- pip or conda

### Setup

1. Clone or navigate to the repository:
```bash
cd Aetheris/dataset_tools
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or with conda:
```bash
conda create -n dataset_tools python=3.10
conda activate dataset_tools
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
# Method 1: Direct execution
python main.py

# Method 2: Module execution
python -m dataset_tools

# Method 3: From project root
cd ..
python dataset_tools/main.py
```

### Step-by-Step Workflow

#### 1. Select Video File
- Click "Browse Video File"
- Choose your MP4, AVI, MOV, or MKV file
- Metadata automatically loads

#### 2. Choose Output Folder
- Click "Select Output Folder"
- Default: `~/Aetheris/datasets/`
- Frames extracted to: `output_folder/video_name/`

#### 3. Configure Extraction
- **Interval Type**: Choose "seconds" or "frames"
- **Interval Value**: 
  - Seconds: 1.0 (one frame per second)
  - Frames: 30 (every 30th frame)

#### 4. Set Quality Thresholds
- **Blur Threshold**: 50-500 (default: 100)
  - Lower = more permissive (keep more blurry frames)
  - Higher = stricter (only very sharp frames)
  
- **Duplicate Threshold**: 0.80-1.00 (default: 0.95)
  - Lower = detect more duplicates
  - Higher = only remove identical frames

#### 5. Enable Processing
- ✓ Enable Blur Detection (recommended)
- ✓ Enable Duplicate Detection (recommended)

#### 6. Start Extraction
- Click "Start Extraction"
- Monitor progress bar
- View real-time logs
- Check statistics as they update

#### 7. Review Results
- Frames saved in output folder
- `metadata.csv`: Frame-by-frame details
- `statistics.json`: Extraction summary
- `raw_frames/`: Organized frames by category

## Configuration

### File: `config.py`

Customize toolkit behavior by editing `config.py`:

```python
# Default extraction settings
DEFAULT_EXTRACTION_INTERVAL_FRAMES = 30
DEFAULT_EXTRACTION_INTERVAL_SECONDS = 1.0

# Blur detection
BLUR_THRESHOLD = 100.0  # Laplacian variance threshold
BLUR_THRESHOLD_MIN = 50.0
BLUR_THRESHOLD_MAX = 500.0

# Duplicate detection
DUPLICATE_THRESHOLD = 0.95  # Similarity threshold (0-1)
DUPLICATE_THRESHOLD_MIN = 0.80
DUPLICATE_THRESHOLD_MAX = 1.00

# Output quality
JPEG_QUALITY = 95  # 0-100, higher = better quality

# Dataset categories
DEFAULT_CATEGORIES = ["morning", "afternoon", "rain", "night"]
```

## Understanding the Metrics

### Blur Detection
**Laplacian Variance Method**:
- Calculates sharpness by detecting edges
- Lower scores = blurrier images (more edge blurring)
- Higher scores = sharper images (more edge definition)

Example:
- Blur score < 100: Likely blurry (remove)
- Blur score 100-200: Medium sharpness (keep most)
- Blur score > 200: Very sharp (keep all)

### Duplicate Detection
**Histogram Comparison**:
- Compares frame-to-frame histograms
- Detects frames that are nearly identical
- Useful for video recorded at high FPS

Example:
- Similarity 0.99: Nearly identical (remove)
- Similarity 0.80: Similar but different (keep)
- Similarity 0.50: Very different (keep)

## Output Structure

```
output_folder/
├── video_name/                    # Frame extraction folder
│   ├── raw_frames/
│   │   ├── morning/               # Category folders
│   │   ├── afternoon/
│   │   ├── rain/
│   │   └── night/
│   ├── video_name_000001.jpg      # Extracted frames
│   ├── video_name_000002.jpg
│   ├── ...
│   ├── metadata.csv               # Frame metadata
│   └── statistics.json            # Extraction report
```

### metadata.csv Example
```csv
filename,frame_number,frame_index,time_seconds,blur_score,is_duplicate,kept
video_000001.jpg,1,0,0.00,245.1,False,True
video_000002.jpg,2,30,1.00,187.4,False,True
video_000003.jpg,3,60,2.00,75.2,False,False
video_000004.jpg,4,90,3.00,250.3,True,False
```

### statistics.json Example
```json
{
  "video_filename": "video.mp4",
  "total_extracted": 180,
  "kept_frames": 165,
  "removed_frames": 15,
  "blurred_frames": 8,
  "duplicate_frames": 7,
  "average_blur_score": 187.45,
  "extraction_time_seconds": 45.23,
  "generated_at": "2026-07-18T14:30:00"
}
```

## Logging

Logs are automatically saved to `dataset_tools/logs/extraction.log`:

```
2026-07-18 14:30:00 - dataset_tools.frame_extractor.extractor - INFO - Video metadata extracted: 5400 frames, 30.0 fps, 1920x1080, duration 180.00s
2026-07-18 14:30:02 - dataset_tools.frame_extractor.extractor - INFO - Extracted frame 1: video_000001.jpg
2026-07-18 14:30:03 - dataset_tools.blur_detector.detector - INFO - Blur detection complete: 165 kept, 15 removed (threshold: 100.0)
```

## Best Practices

### Optimal Settings by Use Case

**Traffic Monitoring (Aetheris)**:
- Interval: 1 second
- Blur Threshold: 100-150 (medium-high quality)
- Duplicate Threshold: 0.95 (remove very similar frames)

**General Object Detection**:
- Interval: 0.5-1.0 seconds
- Blur Threshold: 80-120
- Duplicate Threshold: 0.90-0.95

**High-Precision Tasks**:
- Interval: 0.2 seconds
- Blur Threshold: 150-200 (only very sharp)
- Duplicate Threshold: 0.98 (strict)

### Quality Tips

1. **Extract at sufficient intervals**: Too sparse = insufficient data; too dense = too many duplicates
2. **Set appropriate blur threshold**: Too low = noisy data; too high = missing sharp frames
3. **Enable duplicate detection**: Reduces redundancy and training time
4. **Check metadata.csv**: Review before annotation to catch issues
5. **Validate statistics**: Ensure extracted count matches expectations

## Integration with Training Pipeline

After dataset extraction and annotation, use the dataset with YOLOv8:

```python
from ultralytics import YOLO

# Load a pretrained model
model = YOLO('yolov8n.pt')

# Train on extracted dataset
results = model.train(
    data='datasets/barangay178_v1/data.yml',
    epochs=100,
    imgsz=640,
    device=0,
)
```

## Troubleshooting

### Video Not Recognized
- Ensure video format is MP4, AVI, MOV, or MKV
- Check file isn't corrupted: `ffprobe video_file`
- Verify file has read permissions

### Extraction Very Slow
- Check CPU usage (blur detection is CPU-intensive)
- Reduce interval value (extract fewer frames)
- Disable blur/duplicate detection temporarily

### Out of Memory
- Use smaller output folders
- Extract smaller intervals
- Process video in segments

### Corrupted Extracted Frames
- Check disk space (may be full)
- Verify output folder permissions
- Restart extraction

## Architecture

### Modular Design

```
dataset_tools/
├── config.py                      # Configuration
├── main.py                        # Entry point
├── frame_extractor/              
│   └── extractor.py              # Frame extraction engine
├── blur_detector/
│   └── detector.py               # Blur detection (Laplacian)
├── duplicate_detector/
│   └── detector.py               # Duplicate detection (histogram)
├── metadata/
│   └── generator.py              # Metadata & report generation
├── dataset_organizer/
│   └── organizer.py              # Dataset organization
├── ui/
│   ├── app.py                    # Main application UI
│   └── components.py             # Reusable UI components
├── utils/
│   ├── logging_utils.py          # Logging configuration
│   └── file_utils.py             # File validation & helpers
└── logs/                         # Auto-generated logs
```

### Key Components

**FrameExtractor**: Extracts frames at specified intervals
**BlurDetector**: Detects blurry frames using Laplacian variance
**DuplicateDetector**: Removes near-duplicate frames
**MetadataGenerator**: Generates CSV and JSON reports
**DatasetOrganizer**: Creates folder structure and organizes frames
**DatasetToolkitApp**: Modern CustomTkinter UI

## Code Quality

✅ Type hints throughout  
✅ Comprehensive logging  
✅ Object-oriented design  
✅ SOLID principles  
✅ Error handling  
✅ Modular architecture  
✅ Beginner-friendly comments  

## Performance Characteristics

| Operation | Time |
|-----------|------|
| Frame extraction (1000 frames) | ~10-30 seconds |
| Blur detection (1000 frames) | ~20-40 seconds |
| Duplicate detection (1000 frames) | ~15-30 seconds |
| Metadata generation | ~1-2 seconds |

*Varies based on frame resolution, CPU speed, and disk I/O*

## Future Enhancements

- [ ] Batch processing multiple videos
- [ ] Grayscale/color frame extraction options
- [ ] Custom blur detection algorithms (LoG, VarianceLaplacian)
- [ ] Advanced duplicate detection (deep learning)
- [ ] Dataset augmentation (rotation, flip, brightness)
- [ ] Web UI with Flask
- [ ] API for headless operation
- [ ] GPU acceleration for blur/duplicate detection
- [ ] Multi-threaded frame extraction
- [ ] Video frame preview in UI

## Support & Documentation

For issues, questions, or contributions:
1. Check logs in `dataset_tools/logs/extraction.log`
2. Review `config.py` for configuration options
3. See examples in output `metadata.csv` and `statistics.json`

## License

Part of the Aetheris Traffic Monitoring System  
©2026 Aetheris Project

## Authors

Developed for automated dataset preparation in the Aetheris project.
