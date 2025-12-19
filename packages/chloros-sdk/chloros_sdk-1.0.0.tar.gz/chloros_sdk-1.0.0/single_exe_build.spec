# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Chloros Single EXE

import os
from pathlib import Path

# Get current directory
current_dir = Path.cwd()

# Collect all data files
datas = [
    # Core application files
    ('main.js', '.'),
    ('preload.js', '.'),
    ('electron-backend.js', '.'),
    ('package.json', '.'),
    
    # Python backend files
    ('api.py', '.'),
    ('backend_server.py', '.'),
    ('tasks.py', '.'),
    ('dynamic_gpu_allocator.py', '.'),
    ('ray_session_manager.py', '.'),
    ('unified_calibration_api.py', '.'),
    ('unicode_patch.py', '.'),
    ('project.py', '.'),
    ('ray_image_import.py', '.'),
    ('debayer.py', '.'),
    
    # UI and assets
    ('ui', 'ui/'),
    ('assets', 'assets/'),
    ('flatFields', 'flatFields/'),
    ('mip', 'mip/'),
    ('renderer', 'renderer/'),
    
    # Configuration files
    ('mapir.config', '.'),
    ('pix4d.config', '.'),
    
    # Required executables and DLLs
    ('exiftool.exe', '.'),
    ('FreeImage.dll', '.'),
    ('FreeImagePlus.dll', '.'),
    ('msvcp100.dll', '.'),
    ('msvcr100.dll', '.'),
    ('msvcr100_clr0400.dll', '.'),
    
    # OpenCV DLLs
    ('opencv_aruco320.dll', '.'),
    ('opencv_aruco320d.dll', '.'),
    ('opencv_calib3d320.dll', '.'),
    ('opencv_core320.dll', '.'),
    ('opencv_core320d.dll', '.'),
    ('opencv_features2d320.dll', '.'),
    ('opencv_ffmpeg410_64.dll', '.'),
    ('opencv_flann320.dll', '.'),
    ('opencv_imgcodecs320.dll', '.'),
    ('opencv_imgproc320.dll', '.'),
]

# Filter existing files only
existing_datas = []
for src, dst in datas:
    src_path = current_dir / src
    if src_path.exists():
        existing_datas.append((str(src_path), dst))
        print(f"✅ Including: {src}")
    else:
        print(f"⚠️ Missing: {src}")

a = Analysis(
    ['single_exe_launcher.py'],
    pathex=[str(current_dir)],
    binaries=[],
    datas=existing_datas,
    hiddenimports=[
        # Core Python modules
        'flask', 'flask_cors', 'werkzeug', 'jinja2',
        'PIL', 'PIL.Image', 'PIL.ImageTk',
        'cv2', 'numpy', 'scipy', 'pandas',
        'skimage', 'skimage.filters', 'skimage.measure',
        'requests', 'json', 'threading', 'queue',
        
        # Ray and distributed computing
        'ray', 'ray._private', 'ray._private.worker',
        'ray._private.services', 'ray._private.utils',
        'ray._raylet', 'ray.util', 'ray.worker',
        'ray.cloudpickle', 'ray.cloudpickle.cloudpickle',
        
        # PyTorch and GPU
        'torch', 'torch.nn', 'torch.cuda',
        
        # Additional dependencies
        'colorama', 'filelock', 'jsonschema', 'pydantic',
        'aiohttp', 'aiohttp.web', 'aioredis', 'redis',
        'prometheus_client', 'grpcio', 'protobuf',
        
        # Scientific computing
        'scipy.special.cython_special', 'scipy.sparse.csgraph._validation',
        'sklearn', 'sklearn.ensemble', 'sklearn.tree',
        
        # Image processing
        'exifread', 'rawpy', 'imageio',
        
        # System modules
        'psutil', 'setproctitle', 'tempfile', 'atexit',
        'webbrowser', 'subprocess', 'shutil',
    ],
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude development tools
        'matplotlib', 'IPython', 'jupyter',
        'pytest', 'setuptools', 'pip',
        'wheel', 'distutils',
    ],
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure)

# Build single executable (no splash screen - Electron will handle it)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Chloros',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed app mode
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='ui/corn_logo_single_256.ico',
    version=None,
)
