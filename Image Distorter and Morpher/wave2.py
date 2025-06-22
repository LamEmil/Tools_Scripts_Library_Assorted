# Advanced Image Distorter and Morpher
#
# This script combines the original wave distortion functionality with advanced
# image morphing techniques inspired by professional computer graphics methods.
#
# Key Features:
# 1. Multi-Tabbed Interface: Separate workspaces for single-image distortion and two-image morphing.
# 2. Advanced Distortion:
#    - Classic 'Wave' distortion (Sinusoidal, Triangle).
#    - New 'Liquid Noise' distortion using Perlin noise for organic, fluid effects.
# 3. Feature-Based Image Morphing:
#    - Load a source and a destination image.
#    - Interactively click to add corresponding control points.
#    - Uses Delaunay Triangulation to warp the images.
#    - Generates a smooth video morphing the source into the destination.
# 4. Backend Improvements:
#    - Uses OpenCV for more efficient image processing and video creation.
#    - All processing is threaded to keep the UI responsive.
#
# Required Libraries:
# You must install the following packages to run this script:
# pip install opencv-python numpy scipy Pillow opensimplex imageio imageio-ffmpeg

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from scipy.spatial import Delaunay
from PIL import Image, ImageTk
import threading
import imageio
from opensimplex import OpenSimplex
import os

# --- CORE DISTORTION AND MORPHING LOGIC ---

# --- 1. Waveform and Noise Functions ---

def sinusoidal_wave(coords, period, shift):
    """Generates a sinusoidal wave value from -1 to 1."""
    if period == 0: return 0
    return np.sin(2 * np.pi * (coords / period + shift))

def triangle_wave(coords, period, shift):
    """Generates a triangle wave value from -1 to 1."""
    if period == 0: return 0
    return 4 * np.abs(((coords / period) + shift) % 1 - 0.5) - 1

WAVE_FUNCTIONS = {"Sinusoidal": sinusoidal_wave, "Triangle": triangle_wave}

# --- 2. Single Image Distortion Effects ---

def apply_wave_effect(image_array, params):
    """Applies wave distortion using cv2.remap for efficiency."""
    height, width, _ = image_array.shape
    x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))

    wave_func_h = WAVE_FUNCTIONS[params['shape_h']]
    y_displacement = params['amp_h'] * wave_func_h(x_coords, params['period_h'], params['shift_h'])

    wave_func_v = WAVE_FUNCTIONS[params['shape_v']]
    x_displacement = params['amp_v'] * wave_func_v(y_coords, params['period_v'], params['shift_v'])

    map_x = (x_coords + x_displacement).astype(np.float32)
    map_y = (y_coords + y_displacement).astype(np.float32)

    # Use OpenCV's remap for mapping, which is generally faster
    distorted_image = cv2.remap(image_array, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    return distorted_image

def apply_liquid_noise_effect(image_array, params):
    """Applies a fluid-like distortion using Simplex noise, with smooth looping."""
    height, width, _ = image_array.shape
    x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))

    # Initialize noise generator
    noise_gen = OpenSimplex(seed=params['seed'])

    # Get parameters
    scale = params['noise_scale']
    if scale == 0: scale = 1 # Avoid division by zero
    speed = params['noise_speed']
    amplitude = params['noise_amp']
    t = params['shift']  # t in [0, 1)

    # For smooth looping, use a circular path in noise space
    loop_radius = 1000.0  # Large enough to avoid self-intersection
    angle = 2 * np.pi * t
    z = loop_radius * np.cos(angle)
    w = loop_radius * np.sin(angle)

    vectorized_noise4 = np.vectorize(lambda x, y, z, w: noise_gen.noise4(x, y, z, w))

    # Generate two layers of noise for x and y displacement
    x_noise = vectorized_noise4(x_coords / scale, y_coords / scale, z, w)
    y_noise = vectorized_noise4(x_coords / scale, y_coords / scale, z + 100, w + 100)  # Offset for different field

    x_displacement = amplitude * x_noise
    y_displacement = amplitude * y_noise

    map_x = (x_coords + x_displacement).astype(np.float32)
    map_y = (y_coords + y_displacement).astype(np.float32)

    distorted_image = cv2.remap(image_array, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    return distorted_image


# --- 3. Two-Image Morphing ---

def get_affine_transform(src_tri, dst_tri):
    """Calculates the affine transform matrix from a source to a destination triangle."""
    pts_src = np.float32(src_tri).reshape(3, 2)
    pts_dst = np.float32(dst_tri).reshape(3, 2)
    return cv2.getAffineTransform(pts_src, pts_dst)

def warp_triangle(img, src_tri, dst_tri):
    """Warps a single triangle from a source image to its destination position."""
    # Find bounding box for the destination triangle
    x, y, w, h = cv2.boundingRect(np.float32([dst_tri]))
    
    # Crop the source and create a mask for the destination
    src_rect = cv2.boundingRect(np.float32([src_tri]))
    src_cropped = img[src_rect[1]:src_rect[1] + src_rect[3], src_rect[0]:src_rect[0] + src_rect[2]]

    # Adjust triangle coordinates to be relative to their bounding boxes
    src_tri_rel = src_tri - np.array([src_rect[0], src_rect[1]])
    dst_tri_rel = dst_tri - np.array([x, y])

    # Get the affine transform
    warp_mat = get_affine_transform(src_tri_rel, dst_tri_rel)
    
    # Warp the source triangle
    warped_tri = cv2.warpAffine(src_cropped, warp_mat, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)

    # Create a mask to isolate the warped triangle
    mask = np.zeros((h, w, 4), dtype=np.uint8)
    cv2.fillConvexPoly(mask, np.int32(dst_tri_rel), (255, 255, 255, 255))

    # Apply mask
    warped_tri_masked = cv2.bitwise_and(warped_tri, mask)

    return (x, y, w, h), warped_tri_masked

def generate_morph_frame(img1, img2, points1, points2, intermediate_points, delaunay_tri, alpha):
    """Generates a single frame of the morph sequence."""
    
    # Create blank images for the warped source and destination
    img1_warped = np.zeros(img1.shape, dtype=np.uint8)
    img2_warped = np.zeros(img2.shape, dtype=np.uint8)

    # For each triangle in the mesh, warp it from both source and destination to the intermediate shape
    for tri_indices in delaunay_tri.simplices:
        src_tri = points1[tri_indices]
        dst_tri = points2[tri_indices]
        inter_tri = intermediate_points[tri_indices]

        # --- Warp source image triangle to intermediate shape ---
        bbox1, warped1 = warp_triangle(img1, src_tri, inter_tri)
        x, y, w, h = bbox1
        roi1 = img1_warped[y:y+h, x:x+w]
        # Create mask from alpha channel and its inverse
        mask1 = warped1[:,:,-1]
        mask1_inv = cv2.bitwise_not(mask1)
        # Black-out the area of triangle in the ROI and add the warped triangle
        roi1_bg = cv2.bitwise_and(roi1, roi1, mask=mask1_inv)
        warped1_fg = cv2.bitwise_and(warped1, warped1, mask=mask1)
        img1_warped[y:y+h, x:x+w] = cv2.add(roi1_bg, warped1_fg)


        # --- Warp destination image triangle to intermediate shape ---
        bbox2, warped2 = warp_triangle(img2, dst_tri, inter_tri)
        x, y, w, h = bbox2
        roi2 = img2_warped[y:y+h, x:x+w]
        # Create mask from alpha channel and its inverse
        mask2 = warped2[:,:,-1]
        mask2_inv = cv2.bitwise_not(mask2)
        # Black-out the area of triangle in the ROI and add the warped triangle
        roi2_bg = cv2.bitwise_and(roi2, roi2, mask=mask2_inv)
        warped2_fg = cv2.bitwise_and(warped2, warped2, mask=mask2)
        img2_warped[y:y+h, x:x+w] = cv2.add(roi2_bg, warped2_fg)
        
    # Blend the two fully warped images
    morphed_frame = cv2.addWeighted(img1_warped, 1 - alpha, img2_warped, alpha, 0.0)
    
    return morphed_frame

# --- GUI APPLICATION CLASS ---

class AdvancedImageAnimator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Image Animator")
        self.geometry("1200x800")
        
        # --- App-wide Variables ---
        self.output_filename = tk.StringVar(value="animation.mp4")
        self.num_frames = tk.IntVar(value=60)
        self.duration_ms = tk.IntVar(value=40)
        self.progress_bar = None
        self.status_label = None
        self.ffmpeg_path = tk.StringVar(value="")

        # --- Morphing Specific Variables ---
        self.morph_img1_path = ""
        self.morph_img2_path = ""
        self.morph_img1_orig = None
        self.morph_img2_orig = None
        self.morph_img1_tk = None
        self.morph_img2_tk = None
        self.morph_points1 = []
        self.morph_points2 = []
        
        self.create_widgets()

    def create_widgets(self):
        # Main notebook for different modes
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Create the two main tabs
        distort_frame = ttk.Frame(notebook)
        morph_frame = ttk.Frame(notebook)
        notebook.add(distort_frame, text='Advanced Distortion')
        notebook.add(morph_frame, text='Image Morphing')

        # Populate the tabs
        self.create_distort_tab(distort_frame)
        self.create_morph_tab(morph_frame)
        
        # Style
        style = ttk.Style(self)
        style.configure("Accent.TButton", foreground="white", background="#007ACC", font=("Arial", 12, "bold"))
        style.configure("Red.TButton", foreground="white", background="#C00000")

    # --- Distortion Tab UI ---
    def create_distort_tab(self, parent):
        main_pane = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Left Pane (Controls) ---
        controls_frame = ttk.Frame(main_pane, width=500)
        main_pane.add(controls_frame, weight=2)
        
        # Distortion Type
        self.distort_type = tk.StringVar(value="Wave")
        distort_type_frame = ttk.LabelFrame(controls_frame, text="Distortion Type", padding=10)
        distort_type_frame.pack(fill=tk.X, pady=5)
        
        self.wave_controls_frame = self.create_wave_controls(controls_frame)
        self.liquid_controls_frame = self.create_liquid_controls(controls_frame)
        
        def toggle_controls():
            if self.distort_type.get() == "Wave":
                self.wave_controls_frame.pack(fill=tk.X, expand=True, pady=5)
                self.liquid_controls_frame.pack_forget()
            else:
                self.wave_controls_frame.pack_forget()
                self.liquid_controls_frame.pack(fill=tk.X, expand=True, pady=5)
        
        ttk.Radiobutton(distort_type_frame, text="Wave", variable=self.distort_type, value="Wave", command=toggle_controls).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(distort_type_frame, text="Liquid Noise", variable=self.distort_type, value="Liquid", command=toggle_controls).pack(side=tk.LEFT, padx=10)

        # --- Right Pane (Settings & Generate) ---
        settings_pane = ttk.Frame(main_pane)
        main_pane.add(settings_pane, weight=1)
        
        self.create_common_settings_panel(settings_pane, self.start_distort_generation)
        toggle_controls() # Initial call to set correct controls visibility
        
    def create_wave_controls(self, parent):
        frame = ttk.Frame(parent)
        # Horizontal Wave Parameters
        self.amp_h = tk.DoubleVar(value=20.0)
        self.period_h = tk.DoubleVar(value=100.0)
        self.shift_speed_h = tk.DoubleVar(value=1.0)
        self.shape_h = tk.StringVar(value="Sinusoidal")
        # Vertical Wave Parameters
        self.amp_v = tk.DoubleVar(value=0.0)
        self.period_v = tk.DoubleVar(value=100.0)
        self.shift_speed_v = tk.DoubleVar(value=0.0)
        self.shape_v = tk.StringVar(value="Sinusoidal")
        
        self.create_wave_control_frame(frame, "Horizontal Wave (Affects Y-Axis)", 
                                       self.amp_h, self.period_h, self.shift_speed_h, self.shape_h)
        self.create_wave_control_frame(frame, "Vertical Wave (Affects X-Axis)", 
                                       self.amp_v, self.period_v, self.shift_speed_v, self.shape_v)
        return frame
        
    def create_liquid_controls(self, parent):
        frame = ttk.Frame(parent)
        main_frame = ttk.LabelFrame(frame, text="Liquid Noise Controls", padding=(10, 10))
        main_frame.pack(fill=tk.X, expand=True, pady=5)
        
        self.noise_amp = tk.DoubleVar(value=30.0)
        self.noise_scale = tk.DoubleVar(value=150.0)
        self.noise_speed = tk.DoubleVar(value=1.0)
        self.noise_seed = tk.IntVar(value=0)

        def add_slider(label, var, from_, to):
            f = ttk.Frame(main_frame)
            f.pack(fill=tk.X, expand=True, pady=2)
            ttk.Label(f, text=label, width=15).pack(side=tk.LEFT)
            ttk.Scale(f, from_=from_, to=to, orient='horizontal', variable=var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            ttk.Entry(f, textvariable=var, width=8).pack(side=tk.LEFT)

        add_slider("Amplitude:", var=self.noise_amp, from_=0, to=200)
        add_slider("Noise Scale:", var=self.noise_scale, from_=10, to=500)
        add_slider("Evolution Speed:", var=self.noise_speed, from_=-3, to=3)
        add_slider("Seed:", var=self.noise_seed, from_=0, to=100)
        return frame
        
    def create_wave_control_frame(self, parent, title, amp_var, period_var, shift_speed_var, shape_var):
        """Helper function to create a set of controls for one wave axis."""
        main_frame = ttk.LabelFrame(parent, text=title, padding=(10, 10))
        main_frame.pack(fill=tk.X, expand=True, pady=5)
        
        shape_frame = ttk.Frame(main_frame)
        shape_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(shape_frame, text="Shape:").pack(side=tk.LEFT)
        ttk.Radiobutton(shape_frame, text="Sinusoidal", variable=shape_var, value="Sinusoidal").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(shape_frame, text="Triangle", variable=shape_var, value="Triangle").pack(side=tk.LEFT, padx=10)

        def add_slider(label, var, from_, to):
            f = ttk.Frame(main_frame)
            f.pack(fill=tk.X, expand=True, pady=2)
            ttk.Label(f, text=label, width=18).pack(side=tk.LEFT)
            ttk.Scale(f, from_=from_, to=to, orient='horizontal', variable=var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            ttk.Entry(f, textvariable=var, width=8).pack(side=tk.LEFT)

        add_slider("Amplitude:", var=amp_var, from_=0, to=200)
        add_slider("Wavelength:", var=period_var, from_=1, to=500)
        add_slider("Phase Shift Speed:", var=shift_speed_var, from_=-5, to=5)

    def create_common_settings_panel(self, parent, generate_command):
        # File I/O
        self.distort_image_path = tk.StringVar()
        input_frame = ttk.LabelFrame(parent, text="1. Select Image", padding=10)
        input_frame.pack(fill=tk.X, pady=5, padx=5)
        self.distort_input_label = ttk.Label(input_frame, text="No file selected.")
        self.distort_input_label.pack(fill=tk.X)
        ttk.Button(input_frame, text="Browse...", command=self.browse_distort_file).pack(fill=tk.X, pady=(5,0))

        # Animation Settings
        anim_frame = ttk.LabelFrame(parent, text="2. Animation Settings", padding=10)
        anim_frame.pack(fill=tk.X, pady=5, padx=5)
        tk.Label(anim_frame, text="Number of Frames:").grid(row=0, column=0, sticky='w')
        ttk.Entry(anim_frame, textvariable=self.num_frames).grid(row=0, column=1, sticky='ew')
        tk.Label(anim_frame, text="Frame Duration (ms):").grid(row=1, column=0, sticky='w')
        ttk.Entry(anim_frame, textvariable=self.duration_ms).grid(row=1, column=1, sticky='ew')
        anim_frame.columnconfigure(1, weight=1)

        # Output
        output_frame = ttk.LabelFrame(parent, text="3. Output File (.mp4, .gif, .ewebm)", padding=10)
        output_frame.pack(fill=tk.X, pady=5, padx=5)
        ttk.Entry(output_frame, textvariable=self.output_filename).pack(fill=tk.X)

        # FFmpeg Path Selection
        ffmpeg_frame = ttk.LabelFrame(parent, text="FFmpeg Executable (Optional)", padding=10)
        ffmpeg_frame.pack(fill=tk.X, pady=5, padx=5)
        ttk.Entry(ffmpeg_frame, textvariable=self.ffmpeg_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(ffmpeg_frame, text="Browse...", command=self.browse_ffmpeg_path).pack(side=tk.LEFT, padx=5)

        # Generate Button & Progress
        self.generate_button = ttk.Button(parent, text="Generate Animation", command=generate_command, style="Accent.TButton")
        self.generate_button.pack(fill=tk.X, ipady=8, pady=10, padx=5)
        
        if not self.status_label:
            self.status_label = ttk.Label(self, text="")
            self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=2)
        if not self.progress_bar:
            self.progress_bar = ttk.Progressbar(self, orient='horizontal', mode='determinate')
            self.progress_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

    def browse_distort_file(self):
        filepath = filedialog.askopenfilename(title="Select an Image or Video", filetypes=[("Image/Video Files", "*.png *.jpg *.jpeg *.mp4 *.avi *.mov *.webm")])
        if filepath:
            self.distort_image_path.set(filepath)
            self.distort_input_label.config(text=filepath.split('/')[-1])

    def browse_ffmpeg_path(self):
        path = filedialog.askopenfilename(title="Select ffmpeg executable")
        if path:
            self.ffmpeg_path.set(path)

    def set_ffmpeg_path(self):
        path = self.ffmpeg_path.get()
        if path:
            try:
                import imageio_ffmpeg
                imageio_ffmpeg.get_ffmpeg_exe = lambda: path
            except ImportError:
                try:
                    imageio.plugins.ffmpeg.download = lambda: path
                except Exception:
                    pass
            os.environ['IMAGEIO_FFMPEG_EXE'] = path

    # --- Morph Tab UI ---
    def create_morph_tab(self, parent):
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=5)
        
        # Action buttons
        ttk.Button(top_frame, text="Load Source Image", command=lambda: self.load_morph_image(1)).pack(side=tk.LEFT, padx=10)
        ttk.Button(top_frame, text="Load Destination Image", command=lambda: self.load_morph_image(2)).pack(side=tk.LEFT, padx=10)
        self.generate_morph_button = ttk.Button(top_frame, text="Generate Morph Animation", command=self.start_morph_generation, style="Accent.TButton")
        self.generate_morph_button.pack(side=tk.RIGHT, padx=10)
        ttk.Button(top_frame, text="Clear All Points", command=self.clear_all_points, style="Red.TButton").pack(side=tk.RIGHT, padx=10)
        
        # Info label
        info_text = "Instructions: 1. Load both images. 2. Click a feature on the left image, then the corresponding feature on the right. Repeat. 3. Generate."
        ttk.Label(parent, text=info_text, wraplength=800, justify=tk.CENTER).pack(fill=tk.X, pady=5)

        # Paned window for the two image canvases
        canvas_pane = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        canvas_pane.pack(fill=tk.BOTH, expand=True)

        self.morph_canvas1 = tk.Canvas(canvas_pane, bg='grey')
        self.morph_canvas2 = tk.Canvas(canvas_pane, bg='grey')
        canvas_pane.add(self.morph_canvas1, weight=1)
        canvas_pane.add(self.morph_canvas2, weight=1)
        
        self.morph_canvas1.bind("<Button-1>", lambda e: self.add_point(e, 1))
        self.morph_canvas2.bind("<Button-1>", lambda e: self.add_point(e, 2))

    def load_morph_image(self, canvas_num):
        filepath = filedialog.askopenfilename(title=f"Select Image {canvas_num}")
        if not filepath: return

        try:
            # Use OpenCV to load, ensuring it can be processed later
            # BGR to RGBA conversion for Tkinter and processing
            img_bgr = cv2.imread(filepath, cv2.IMREAD_COLOR)
            if img_bgr is None:
                raise ValueError("Could not read image file.")
            img_rgba = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGBA)
            
            canvas = self.morph_canvas1 if canvas_num == 1 else self.morph_canvas2
            
            # Resize for display
            disp_h = canvas.winfo_height()
            if disp_h < 50: disp_h = 500 # Default if not drawn yet
            aspect_ratio = img_rgba.shape[1] / img_rgba.shape[0]
            disp_w = int(disp_h * aspect_ratio)

            img_resized_rgba = cv2.resize(img_rgba, (disp_w, disp_h), interpolation=cv2.INTER_AREA)

            # Convert to PhotoImage for Tkinter
            img_pil = Image.fromarray(img_resized_rgba)
            img_tk = ImageTk.PhotoImage(image=img_pil)

            if canvas_num == 1:
                self.morph_img1_path = filepath
                self.morph_img1_orig = img_rgba
                self.morph_img1_tk = img_tk
                self.morph_img1_display_size = (disp_w, disp_h)
            else:
                self.morph_img2_path = filepath
                self.morph_img2_orig = img_rgba
                self.morph_img2_tk = img_tk
                self.morph_img2_display_size = (disp_w, disp_h)
            
            canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            canvas.config(scrollregion=canvas.bbox(tk.ALL))
            self.clear_all_points()

        except Exception as e:
            messagebox.showerror("Error", f"Could not load image: {e}")

    def add_point(self, event, canvas_num):
        if len(self.morph_points1) != len(self.morph_points2) and canvas_num == 1:
            messagebox.showwarning("Waiting", "Please select the corresponding point on the right image.")
            return
        if len(self.morph_points1) == len(self.morph_points2) and canvas_num == 2:
            messagebox.showwarning("Waiting", "Please select a new point on the left image first.")
            return

        canvas = self.morph_canvas1 if canvas_num == 1 else self.morph_canvas2
        
        # Get original image and display size
        orig_img_shape = self.morph_img1_orig.shape if canvas_num == 1 else self.morph_img2_orig.shape
        display_size = self.morph_img1_display_size if canvas_num == 1 else self.morph_img2_display_size
        
        # Scale click coordinates from display size to original image size
        scale_x = orig_img_shape[1] / display_size[0]
        scale_y = orig_img_shape[0] / display_size[1]
        
        x_orig = event.x * scale_x
        y_orig = event.y * scale_y
        
        point_list = self.morph_points1 if canvas_num == 1 else self.morph_points2
        point_list.append(np.array([x_orig, y_orig]))

        # Draw point on canvas with a "point" tag
        color = "cyan" if len(self.morph_points1) != len(self.morph_points2) else "lime green"
        canvas.create_oval(event.x - 3, event.y - 3, event.x + 3, event.y + 3, fill=color, outline="black", tags="point")
        
        # If a pair is complete, change the color of all points
        if len(self.morph_points1) == len(self.morph_points2):
            self.morph_canvas1.itemconfigure("point", fill="lime green")
            self.morph_canvas2.itemconfigure("point", fill="lime green")
        
    def clear_all_points(self):
        self.morph_points1.clear()
        self.morph_points2.clear()
        # Redraw images to clear points
        if self.morph_img1_tk: self.morph_canvas1.create_image(0, 0, anchor=tk.NW, image=self.morph_img1_tk)
        if self.morph_img2_tk: self.morph_canvas2.create_image(0, 0, anchor=tk.NW, image=self.morph_img2_tk)

    # --- Generation Logic (Threaded) ---

    def reset_ui_state(self):
        """Schedules UI reset to run on the main thread."""
        self.after(0, lambda: [
            self.generate_button.config(state=tk.NORMAL),
            self.generate_morph_button.config(state=tk.NORMAL),
            self.status_label.config(text=""),
            self.progress_bar.config(value=0)
        ])

    def start_distort_generation(self):
        if not self.distort_image_path.get():
            messagebox.showerror("Error", "Please select an input image or video first.")
            return
        self.generate_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        filepath = self.distort_image_path.get()
        if filepath.lower().endswith(('.mp4', '.avi', '.mov', '.webm')):
            threading.Thread(target=self.run_video_distort_process, daemon=True).start()
        else:
            threading.Thread(target=self.run_distort_process, daemon=True).start()

    def run_video_distort_process(self):
        try:
            cap = cv2.VideoCapture(self.distort_image_path.get())
            if not cap.isOpened():
                messagebox.showerror("Error", "Could not open video file.")
                self.reset_ui_state()
                return
            effect_func = apply_liquid_noise_effect if self.distort_type.get() == "Liquid" else apply_wave_effect
            params = {}
            if self.distort_type.get() == "Wave":
                params = {
                    'amp_h': self.amp_h.get(), 'period_h': self.period_h.get(), 'shape_h': self.shape_h.get(),
                    'shift_speed_h': self.shift_speed_h.get(),
                    'amp_v': self.amp_v.get(), 'period_v': self.period_v.get(), 'shape_v': self.shape_v.get(),
                    'shift_speed_v': self.shift_speed_v.get()
                }
            else:
                params = {
                    'noise_amp': self.noise_amp.get(), 'noise_scale': self.noise_scale.get(),
                    'noise_speed': self.noise_speed.get(), 'seed': self.noise_seed.get()
                }
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            output_path = self.output_filename.get()
            if not output_path.lower().endswith(('.mp4', '.mkv', '.avi', '.gif', '.webm', '.webp')):
                output_path += '.mp4'
            frames = []
            i = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                current_params = params.copy()
                progress = i / frame_count
                if effect_func == apply_wave_effect:
                    current_params['shift_h'] = progress * params['shift_speed_h']
                    current_params['shift_v'] = progress * params['shift_speed_v']
                else:
                    current_params['shift'] = progress
                distorted_array_rgba = effect_func(frame_rgba, current_params)
                distorted_array_rgb = cv2.cvtColor(distorted_array_rgba, cv2.COLOR_RGBA2RGB)
                frames.append(distorted_array_rgb)
                cv2.imshow('Distorted Video Preview', cv2.cvtColor(distorted_array_rgb, cv2.COLOR_RGB2BGR))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                self.after(0, self.progress_bar.config, {'value': i + 1})
                i += 1
            cap.release()
            cv2.destroyAllWindows()
            # Save video
            if output_path.lower().endswith('.gif'):
                imageio.mimsave(output_path, frames, format='GIF', duration=1/fps)
            elif output_path.lower().endswith('.webp'):
                imageio.mimsave(output_path, frames, format='WEBP', duration=1/fps)
            elif output_path.lower().endswith('.webm'):
                with imageio.get_writer(output_path, fps=fps, codec='vp9', format='webm', quality=8) as writer:
                    for frame in frames:
                        writer.append_data(frame)
            else:
                with imageio.get_writer(output_path, fps=fps, codec='libx264', quality=8, pixelformat='yuv420p') as writer:
                    for frame in frames:
                        writer.append_data(frame)
            self.after(0, self.status_label.config, {'text': "Saving complete!"})
            messagebox.showinfo("Success!", f"Distorted video saved to:\n{output_path}")
        except Exception as e:
            messagebox.showerror("An Error Occurred", f"Failed to process video.\n\nError: {e}")
        finally:
            self.reset_ui_state()
            
    def run_distort_process(self):
        self.set_ffmpeg_path()
        try:
            image_bgr = cv2.imread(self.distort_image_path.get(), cv2.IMREAD_COLOR)
            image_rgba = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGBA) # Work in RGBA

            num_frames = self.num_frames.get()
            duration_ms = self.duration_ms.get()
            fps = 1000 / duration_ms if duration_ms > 0 else 25
            output_path = self.output_filename.get()
            # Convert .ewebm to .webm for compatibility
            if output_path.lower().endswith('.ewebm'):
                output_path = output_path[:-6] + '.webm'
            if not output_path.lower().endswith(('.mp4', '.mkv', '.avi', '.gif', '.webm', '.webp')):
                output_path += '.mp4'

            effect_func = apply_liquid_noise_effect
            params = {}
            if self.distort_type.get() == "Wave":
                effect_func = apply_wave_effect
                params = {
                    'amp_h': self.amp_h.get(), 'period_h': self.period_h.get(), 'shape_h': self.shape_h.get(),
                    'shift_speed_h': self.shift_speed_h.get(),
                    'amp_v': self.amp_v.get(), 'period_v': self.period_v.get(), 'shape_v': self.shape_v.get(),
                    'shift_speed_v': self.shift_speed_v.get()
                }
            else: # Liquid
                params = {
                    'noise_amp': self.noise_amp.get(), 'noise_scale': self.noise_scale.get(),
                    'noise_speed': self.noise_speed.get(), 'seed': self.noise_seed.get()
                }

            self.progress_bar['maximum'] = num_frames

            is_gif = output_path.lower().endswith('.gif')
            is_webm = output_path.lower().endswith('.webm')
            is_webp = output_path.lower().endswith('.webp')
            frames = []
            for i in range(num_frames):
                self.after(0, self.status_label.config, {'text': f"Processing frame {i+1}/{num_frames}..."})
                progress = i / num_frames
                current_params = params.copy()
                if effect_func == apply_wave_effect:
                    current_params['shift_h'] = progress * params['shift_speed_h']
                    current_params['shift_v'] = progress * params['shift_speed_v']
                else: # Liquid
                    current_params['shift'] = progress
                distorted_array_rgba = effect_func(image_rgba, current_params)
                distorted_array_rgb = cv2.cvtColor(distorted_array_rgba, cv2.COLOR_RGBA2RGB)
                frames.append(distorted_array_rgb)
                self.after(0, self.progress_bar.config, {'value': i + 1})

            if is_gif:
                imageio.mimsave(output_path, frames, format='GIF', duration=duration_ms/1000)
            elif is_webp:
                imageio.mimsave(output_path, frames, format='WEBP', duration=duration_ms/1000)
            elif is_webm:
                with imageio.get_writer(output_path, fps=fps, codec='vp9', format='webm', quality=8) as writer:
                    for frame in frames:
                        writer.append_data(frame)
            else:
                with imageio.get_writer(output_path, fps=fps, codec='libx264', quality=8, pixelformat='yuv420p') as writer:
                    for frame in frames:
                        writer.append_data(frame)

            self.after(0, self.status_label.config, {'text': "Saving complete!"})
            messagebox.showinfo("Success!", f"Animation successfully saved to:\n{output_path}")

        except Exception as e:
            messagebox.showerror("An Error Occurred", f"Failed to generate video.\n\nError: {e}")
        finally:
            self.reset_ui_state()
            
    def start_morph_generation(self):
        if not (self.morph_img1_orig is not None and self.morph_img2_orig is not None):
            messagebox.showerror("Error", "Please load both a source and destination image.")
            return
        if len(self.morph_points1) < 3:
            messagebox.showerror("Error", "Please define at least 3 corresponding points.")
            return
        if len(self.morph_points1) != len(self.morph_points2):
            messagebox.showerror("Error", "The number of points on each image must be equal.")
            return
        
        self.generate_morph_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        threading.Thread(target=self.run_morph_process, daemon=True).start()

    def run_morph_process(self):
        self.set_ffmpeg_path()
        try:
            # Prepare data for morphing
            num_frames = self.num_frames.get()
            duration_ms = self.duration_ms.get()
            fps = 1000 / duration_ms if duration_ms > 0 else 25
            output_path = self.output_filename.get()

            # Convert .ewebm to .webm for compatibility
            if output_path.lower().endswith('.ewebm'):
                output_path = output_path[:-6] + '.webm'

            # Ensure images are the same size
            h1, w1, _ = self.morph_img1_orig.shape
            h2, w2, _ = self.morph_img2_orig.shape
            if h1 != h2 or w1 != w2:
                messagebox.showinfo("Info", "Images have different sizes. Destination image will be resized to match the source.")
                img2_resized = cv2.resize(self.morph_img2_orig, (w1, h1), interpolation=cv2.INTER_AREA)
            else:
                img2_resized = self.morph_img2_orig.copy()

            points1 = np.array(self.morph_points1)
            points2 = np.array(self.morph_points2)

            # Add boundary points to prevent edge artifacts
            h, w, _ = self.morph_img1_orig.shape
            boundary_pts = np.array([[0,0], [w-1,0], [0,h-1], [w-1,h-1], [w//2, 0], [w//2, h-1], [0, h//2], [w-1, h//2]])
            points1 = np.concatenate((points1, boundary_pts))
            points2 = np.concatenate((points2, boundary_pts))

            # Perform Delaunay triangulation on the average of the points
            avg_points = (points1 + points2) / 2
            delaunay_tri = Delaunay(avg_points)

            self.progress_bar['maximum'] = num_frames

            is_gif = output_path.lower().endswith('.gif')
            is_webm = output_path.lower().endswith('.webm')
            is_webp = output_path.lower().endswith('.webp')
            frames = []
            for i in range(num_frames):
                self.after(0, self.status_label.config, {'text': f"Morphing frame {i+1}/{num_frames}..."})
                alpha = i / num_frames
                
                # Calculate intermediate points
                intermediate_points = (1 - alpha) * points1 + alpha * points2
                
                # Generate the frame
                morphed_frame_rgba = generate_morph_frame(
                    self.morph_img1_orig, img2_resized, points1, points2, 
                    intermediate_points, delaunay_tri, alpha
                )
                
                # Convert final RGBA frame to RGB for the video writer
                morphed_frame_rgb = cv2.cvtColor(morphed_frame_rgba, cv2.COLOR_RGBA2RGB)
                frames.append(morphed_frame_rgb)
                self.after(0, self.progress_bar.config, {'value': i + 1})

            if is_gif:
                imageio.mimsave(output_path, frames, format='GIF', duration=duration_ms/1000)
            elif is_webp:
                imageio.mimsave(output_path, frames, format='WEBP', duration=duration_ms/1000)
            elif is_webm:
                with imageio.get_writer(output_path, fps=fps, codec='vp9', format='webm', quality=10) as writer:
                    for frame in frames:
                        writer.append_data(frame)
            else:
                with imageio.get_writer(output_path, fps=fps, codec='libx264', quality=10, pixelformat='yuv444p') as writer:
                    for frame in frames:
                        writer.append_data(frame)

            self.after(0, self.status_label.config, {'text': "Morphing complete!"})
            messagebox.showinfo("Success!", f"Morphing animation saved to:\n{output_path}")

        except Exception as e:
            messagebox.showerror("An Error Occurred", f"Failed to generate morph.\n\nError: {e}")
        finally:
            self.reset_ui_state()

if __name__ == "__main__":
    app = AdvancedImageAnimator()
    app.mainloop()
