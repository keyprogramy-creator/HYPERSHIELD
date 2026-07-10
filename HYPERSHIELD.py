import tkinter as tk
import math
import random
import sys

class DSQHyperShieldGame:
    def __init__(self, root, width, height):
        self.root = root
        self.width = width
        self.height = height
        self.fov = 600
        self.cx = width // 2
        self.cy = height // 2
        
        # Game States
        self.game_started = False  # Track if we are on the start screen
        self.paused = False
        self.game_over = False
        self.score = 0
        self.winning_score = 100  # Stays at 100 for that great 3-minute game hook!
        
        # ANTI-CHEAT SHIELD MECHANICS
        self.shield_energy = 100.0
        self.max_shield_energy = 100.0
        self.shield_depleted = False
        
        # Core visual metrics
        self.core_radius = 25
        
        # Constant-Time Threat Array Architecture
        self.max_threats = 6 
        self.threats = [] 
        for _ in range(self.max_threats):
            self.threats.append([0.0, 0.0, 0.0, 0.0, False, 0])
            
        # Canvas Setup
        self.canvas = tk.Canvas(root, width=width, height=height, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Engine Math Matrix Components
        self.vertices, self.edges = self.generate_flat_mesh()
        self.click_intensity = 0.0
        self.target_intensity = 0.0
        self.mouse_spatial_offset = (0.0, 0.0)
        
        # Interactions Bindings
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        root.bind("<Escape>", self.toggle_pause_menu)
        
        # Initialize by showing the start screen first
        self.draw_start_screen()

    def project_vertex(self, x, y, z, intensity, mouse_offset):
        mx, my = mouse_offset
        dx = x - mx
        dy = y - my
        radius_sq = (dx**2 + dy**2)
        
        warp_factor = 1.0 / (1.0 + radius_sq * intensity)
        hx = mx + (dx * warp_factor)
        hy = my + (dy * warp_factor)
        hz = z + (radius_sq * intensity * 1.5)
        
        if hz <= 0.1: hz = 0.1
            
        screen_x = int(self.cx + (hx * self.fov) / hz)
        screen_y = int(self.cy + (hy * self.fov) / hz)
        return screen_x, screen_y

    def generate_flat_mesh(self):
        vertices = []
        x_range = [-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0]
        y_range = [-4.0, -2.0, 0.0, 2.0, 4.0]
        z_flat = 4.0
        
        vertex_map = {}
        idx = 0
        for x in x_range:
            for y in y_range:
                vertices.append((x, y, z_flat))
                vertex_map[(x, y)] = idx
                idx += 1
                
        edges = []
        for y in y_range:
            for i in range(len(x_range) - 1):
                edges.append((vertex_map[(x_range[i], y)], vertex_map[(x_range[i+1], y)]))
        for x in x_range:
            for j in range(len(y_range) - 1):
                edges.append((vertex_map[(x, y_range[j])], vertex_map[(x, y_range[j+1])]))
                
        return vertices, edges

    def spawn_threat(self, index, custom_delay=None):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        
        if side == 'top':
            x = random.uniform(-6.0, 6.0)
            y = -4.0
        elif side == 'bottom':
            x = random.uniform(-6.0, 6.0)
            y = 4.0
        elif side == 'left':
            x = -6.0
            y = random.uniform(-4.0, 4.0)
        else:
            x = 6.0
            y = random.uniform(-4.0, 4.0)
            
        angle = math.atan2(0.0 - y, 0.0 - x) + random.uniform(-0.15, 0.15)
        speed = random.uniform(0.025, 0.045)
        delay = custom_delay if custom_delay is not None else random.randint(30, 120)
        
        self.threats[index] = [x, y, math.cos(angle)*speed, math.sin(angle)*speed, False, delay]

    def spawn_initial_threats(self):
        for i in range(self.max_threats):
            self.spawn_threat(i, custom_delay=i * 45)

    def draw_start_screen(self):
        """Renders the custom purple splash screen."""
        self.canvas.delete("all")
        
        # Main Title (Purple with space characters acting as the asteroid emojis)
        self.canvas.create_text(self.cx, self.cy - 80, text="☄ HYPERSHIELD ☄", fill="#9333EA", font=("Arial", 36, "bold"), tags="start_menu")
        
        # Subtitle Instructions (Vibrant Purple)
        self.canvas.create_text(self.cx, self.cy, text="GOAL: DEFEND YOUR BASE BY PUSHING THEM OUTWARDS WITH INWARD FORCE!", 
                                fill="#A855F7", font=("Arial", 14, "bold"), tags="start_menu")
        
        # Interactive Start Button
        btn_frame = tk.Frame(self.root, bg="black")
        self.canvas.create_window(self.cx, self.cy + 90, window=btn_frame, tags="start_menu")
        
        start_btn = tk.Button(btn_frame, text="INITIALIZE CORE", bg="#9333EA", fg="white", activebackground="#A855F7", activeforeground="white",
                              font=("Arial", 14, "bold"), bd=0, padx=20, pady=8, command=self.start_game)
        start_btn.pack()

    def start_game(self):
        """Clears the start screen menu and initializes the active engine loop."""
        self.canvas.delete("start_menu")
        self.game_started = True
        self.spawn_initial_threats()
        self.update_game()

    def on_press(self, event):
        if not self.game_started or self.paused or self.game_over or self.shield_depleted: return
        self.target_intensity = 2.4
        self.update_mouse_offset(event.x, event.y)

    def on_drag(self, event):
        if not self.game_started or self.paused or self.game_over or self.shield_depleted: return
        self.update_mouse_offset(event.x, event.y)

    def on_release(self, event):
        if not self.game_started or self.paused or self.game_over: return
        self.target_intensity = 0.0

    def update_mouse_offset(self, px, py):
        self.mouse_spatial_offset = (
            (px - self.cx) / (self.fov / 4.0),
            (py - self.cy) / (self.fov / 4.0)
        )

    def toggle_pause_menu(self, event=None):
        if not self.game_started or self.game_over: return
        if not self.paused:
            self.paused = True
            self.draw_popup_card("GAME PAUSED", "DO YOU WANT TO QUIT?")
        else:
            self.resume_game()

    def draw_popup_card(self, title, subtitle):
        self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#000000", stipple="gray50", tags="ui_card")
        box_w, box_h = 450, 250
        x1, y1 = self.cx - box_w//2, self.cy - box_h//2
        x2, y2 = self.cx + box_w//2, self.cy + box_h//2
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#111111", outline="#9333EA", width=2, tags="ui_card")
        
        self.canvas.create_text(self.cx, self.cy - 70, text=title, fill="#9333EA", font=("Arial", 22, "bold"), tags="ui_card")
        self.canvas.create_text(self.cx, self.cy - 30, text=subtitle, fill="white", font=("Arial", 13), tags="ui_card")
        
        button_frame = tk.Frame(self.root, bg="#111111")
        self.canvas.create_window(self.cx, self.cy + 40, window=button_frame, tags="ui_card")
        
        if self.game_over:
            retry_btn = tk.Button(button_frame, text="PLAY AGAIN", bg="#9333EA", fg="white", font=("Arial", 12, "bold"), bd=0, padx=15, pady=5, command=self.reset_game)
            retry_btn.pack(side="left", padx=15)
            exit_btn = tk.Button(button_frame, text="EXIT", bg="#374151", fg="white", font=("Arial", 12, "bold"), bd=0, padx=15, pady=5, command=self.exit_engine)
            exit_btn.pack(side="right", padx=15)
        else:
            yes_btn = tk.Button(button_frame, text="YES", bg="#9333EA", fg="white", font=("Arial", 12, "bold"), bd=0, padx=15, pady=5, command=self.exit_engine)
            yes_btn.pack(side="left", padx=15)
            no_btn = tk.Button(button_frame, text="NO", bg="#374151", fg="white", font=("Arial", 12, "bold"), bd=0, padx=15, pady=5, command=self.resume_game)
            no_btn.pack(side="right", padx=15)

    def resume_game(self):
        self.canvas.delete("ui_card")
        self.paused = False
        self.target_intensity = 0.0
        self.update_game()

    def reset_game(self):
        self.canvas.delete("ui_card")
        self.score = 0
        self.shield_energy = 100.0
        self.shield_depleted = False
        self.click_intensity = 0.0
        self.target_intensity = 0.0
        self.game_over = False
        self.paused = False
        self.spawn_initial_threats()
        self.update_game()

    def exit_engine(self):
        self.root.destroy()
        sys.exit()

    def update_game(self):
        if not self.game_started or self.paused or self.game_over: return
        
        # ENERGY SYSTEM TICK
        if self.target_intensity > 0.0 and not self.shield_depleted:
            self.shield_energy -= 0.65  
            if self.shield_energy <= 0:
                self.shield_energy = 0
                self.shield_depleted = True
                self.target_intensity = 0.0  
        else:
            self.shield_energy += 0.35  
            if self.shield_energy >= self.max_shield_energy:
                self.shield_energy = self.max_shield_energy
                self.shield_depleted = False  

        self.click_intensity += (self.target_intensity - self.click_intensity) * 0.12
        self.canvas.delete("all")
        
        # Render Structural Matrix Layout
        projected_points = []
        for vertex in self.vertices:
            x, y, z = vertex
            pt = self.project_vertex(x, y, z, self.click_intensity, self.mouse_spatial_offset)
            projected_points.append(pt)
            
        for edge in self.edges:
            p1, p2 = edge
            x1, y1 = projected_points[p1]
            x2, y2 = projected_points[p2]
            self.canvas.create_line(x1, y1, x2, y2, fill="#3B0764", width=2)
            
        # Handle Central Core Shield Node
        core_pt = self.project_vertex(0, 0, 4.0, self.click_intensity, self.mouse_spatial_offset)
        cx, cy = core_pt
        self.canvas.create_oval(cx - self.core_radius, cy - self.core_radius, cx + self.core_radius, cy + self.core_radius, fill="", outline="#9333EA", width=3)
        self.canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill="#9333EA")

        # Processing Threat Simulation Array
        mx, my = self.mouse_spatial_offset
        for i in range(self.max_threats):
            tx, ty, vx, vy, active, delay = self.threats[i]
            
            if not active:
                if delay > 0:
                    self.threats[i][5] -= 1  
                    continue
                else:
                    self.threats[i][4] = True  
                    active = True

            dx = tx - mx
            dy = ty - my
            radius_sq = (dx**2 + dy**2)
            warp = 1.0 / (1.0 + radius_sq * self.click_intensity)
            
            applied_gravity_x = (vx * warp) + (dx * (1.0 - warp) * 0.02)
            applied_gravity_y = (vy * warp) + (dy * (1.0 - warp) * 0.02)
            
            tx += applied_gravity_x
            ty += applied_gravity_y
            self.threats[i][0] = tx
            self.threats[i][1] = ty
            
            t_screen = self.project_vertex(tx, ty, 4.0, self.click_intensity, self.mouse_spatial_offset)
            tsx, tsy = t_screen
            self.canvas.create_rectangle(tsx - 8, tsy - 8, tsx + 8, tsy + 8, fill="#EF4444", outline="white", width=1)
            
            # World Coordinates Collision Check
            dist_to_core_world = math.sqrt(tx**2 + ty**2)
            if dist_to_core_world <= 0.35:
                self.game_over = True
                self.draw_popup_card("CORE BREACHED", f"YOUR SYSTEM COLLAPSED. FINAL SCORE: {self.score}")
                return
                
            # Boundary Bounds Scoring
            if tx < -7.5 or tx > 7.5 or ty < -5.5 or ty > 5.5:
                self.score += 1
                if self.score >= self.winning_score:
                    self.game_over = True
                    self.draw_popup_card("SYSTEM SECURED", "YOU WIN! SPACE GRID EQUILIBRIUM RESTORED.")
                    return
                self.spawn_threat(i)

        # Interface Text & Custom Stamina UI Bars
        self.canvas.create_text(80, 40, text=f"SCORE: {self.score} / {self.winning_score}", fill="white", font=("Arial", 14, "bold"))
        self.canvas.create_text(self.width - 120, 40, text="ESC: PAUSE MENU", fill="#6B7280", font=("Arial", 11, "bold"))
        
        # Energy Bar UI Calculation
        bar_x1, bar_y1 = self.width // 2 - 100, 30
        bar_x2, bar_y2 = self.width // 2 + 100, 45
        energy_pct = self.shield_energy / self.max_shield_energy
        fill_x = bar_x1 + (200 * energy_pct)
        
        bar_color = "#EF4444" if self.shield_depleted else "#A855F7"
        
        self.canvas.create_rectangle(bar_x1, bar_y1, bar_x2, bar_y2, outline="#374151", width=2)
        self.canvas.create_rectangle(bar_x1 + 2, bar_y1 + 2, fill_x - 2, bar_y2 - 2, fill=bar_color, outline="")
        self.canvas.create_text(self.width // 2, 55, text="SHIELD MATRIX ENERGY", fill="white", font=("Arial", 8, "bold"))
        
        self.canvas.after(16, self.update_game)

# Primary Initialization Block
root = tk.Tk()
root.attributes("-fullscreen", True)

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

game_app = DSQHyperShieldGame(root, screen_w, screen_h)
root.mainloop()
