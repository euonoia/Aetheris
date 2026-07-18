# Quick Start Guide - Dataset Engineering Toolkit

## Installation (One-time setup)

```bash
# Navigate to project
cd ~/Aetheris

# Install dependencies in your Python environment
pip install -r dataset_tools/requirements.txt
# or
source backend/.venv/bin/activate && pip install -r dataset_tools/requirements.txt
```

## Running the Application

```bash
# From Aetheris root directory
python dataset_tools/main.py

# Or directly in dataset_tools folder
cd dataset_tools && python main.py
```

## Typical Workflow (5 minutes)

1. **Launch App**: `python dataset_tools/main.py`

2. **Load Video**: 
   - Click "Browse Video File"
   - Select your .mp4, .avi, .mov, or .mkv file
   - Metadata auto-loads

3. **Configure Extraction**:
   - Choose interval: `1.0` seconds (1 frame/second)
   - Leave blur threshold: `100` (medium quality)
   - Leave duplicate threshold: `0.95` (strict)

4. **Click "Start Extraction"**:
   - Watch progress bar
   - Monitor real-time logs
   - Statistics update in real-time

5. **Results**:
   - Frames saved in: `~/Aetheris/datasets/video_name/`
   - Check `metadata.csv` for details
   - Check `statistics.json` for summary

## Example Extractions

### Extract 1 frame per second from 5-minute video
- Input: 5min video @ 30fps = 9000 frames
- Interval: 1.0 seconds
- Result: ~300 frames extracted
- Time: ~30-60 seconds

### Extract every 30 frames from 10-minute video
- Input: 10min video @ 30fps = 18000 frames  
- Interval: 30 frames
- Result: ~600 frames extracted
- Time: ~60-120 seconds

## Key Settings Reference

| Setting | Recommended | Range | Effect |
|---------|-------------|-------|--------|
| **Interval (seconds)** | 1.0 | 0.1-10 | Lower = more frames, higher = fewer frames |
| **Blur Threshold** | 100 | 50-500 | Higher = stricter, only sharp frames |
| **Duplicate Threshold** | 0.95 | 0.80-1.00 | Higher = stricter, fewer kept |

## Output Files

After extraction, you'll find:

```
~/Aetheris/datasets/video_name/
├── video_name_000001.jpg      ← Extracted frames
├── video_name_000002.jpg
├── ...
├── metadata.csv               ← Frame details (open in Excel)
└── statistics.json            ← Extraction summary (open in text editor)
```

## Troubleshooting

**Video won't load**: Ensure it's MP4, AVI, MOV, or MKV format

**Extraction slow**: That's normal - blur detection is CPU-intensive

**Low number extracted**: Check blur threshold (100 is default, try lower like 50)

**All frames marked as duplicates**: Try lower duplicate threshold (0.90 instead of 0.95)

**Frames look blurry**: Lower blur threshold to 50-75

## Next Steps

1. **Review Extracted Frames**: Check `metadata.csv` for quality metrics
2. **Annotate Dataset**: Use CVAT, Label Studio, or Roboflow
3. **Train Model**: Use frames in YOLOv8 training pipeline
4. **Deploy**: Run inference on traffic cameras

## Support

Check logs: `dataset_tools/logs/extraction.log`

Full documentation: `dataset_tools/README.md`
