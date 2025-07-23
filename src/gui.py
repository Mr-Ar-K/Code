import tkinter as tk
from tkinter import ttk, Menu, messagebox, Frame, Scrollbar, LabelFrame, filedialog
import os
import traceback
import threading
from stope_calculations import calculate_stope_design, summarize_results
from input_validation import validate_inputs
from report_generator import generate_pdf_report, generate_summary_text
from stability_analysis import determine_stope_type, calculate_stope_dimensions, assess_stability
from cost_estimation import estimate_mining_costs

# Indian Mining Constants
INDIAN_ORE_TYPES = ["generic", "gold", "copper", "iron", "zinc", "lead", "bauxite", "chromite"]
DGMS_SAFETY_FACTOR_MIN = 1.5

class MiningStopeDesignApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Mining Stope Design Tool - Indian Standards")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Create main frame for better organization
        main_frame = Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_menu_bar()
        self._create_header(main_frame)
        self._create_tabs(main_frame)
        self._create_footer(main_frame)

    def _create_menu_bar(self):
        menu_bar = Menu(self.root)
        
        file_menu = Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Design", command=self._clear_inputs)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        help_menu = Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="DGMS Guidelines", command=self._show_dgms_guidelines)
        help_menu.add_command(label="About", command=self._show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)

    def _create_header(self, parent):
        header_frame = Frame(parent, bg="#1a5276", padx=10, pady=10)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(
            header_frame, 
            text="Mining Stope Design Tool - Indian Standards", 
            font=("Arial", 16, "bold"),
            bg="#1a5276",
            fg="white"
        )
        title_label.pack(pady=5)
        
        subtitle_label = tk.Label(
            header_frame, 
            text="Compliant with DGMS, MMR and IBM guidelines", 
            font=("Arial", 10, "italic"),
            bg="#1a5276",
            fg="white"
        )
        subtitle_label.pack()

    def _create_tabs(self, parent):
        self.tab_control = ttk.Notebook(parent)
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        self.input_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.input_tab, text="Design Input")
        
        self.results_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.results_tab, text="Results")
        
        self.visualization_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.visualization_tab, text="Visualizations")
        
        self._setup_input_form()
        self._setup_results_area()
        self._setup_visualization_area()

    def _setup_input_form(self):
        input_frame = LabelFrame(self.input_tab, text="Input Parameters", font=("Arial", 12, "bold"), padx=10, pady=10, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.entries = {}
        
        input_left = Frame(input_frame, bg="#f0f0f0")
        input_left.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        input_right = Frame(input_frame, bg="#f0f0f0")
        input_right.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)
        
        fields_left = [
            ('ore_thickness', 'Ore Body Thickness (m):', "0.3-100"),
            ('dip_angle', 'Dip Angle (degrees):', "0-70"),
            ('rqd', 'Rock Quality Designation (%):', "25-100"),
        ]
        
        for i, (field, label, tooltip) in enumerate(fields_left):
            field_frame = Frame(input_left, bg="#f0f0f0")
            field_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(field_frame, text=label, width=25, anchor='w', bg="#f0f0f0").pack(side=tk.LEFT)
            entry = ttk.Entry(field_frame, width=15)
            entry.pack(side=tk.LEFT, padx=5)
            self.entries[field] = entry
            
            tk.Label(field_frame, text=f"Range: {tooltip}", font=("Arial", 8), fg="gray", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        fields_right = [
            ('mining_depth', 'Mining Depth (m):', "5-2000"),
        ]
        
        for i, (field, label, tooltip) in enumerate(fields_right):
            field_frame = Frame(input_right, bg="#f0f0f0")
            field_frame.pack(fill=tk.X, pady=5)
            
            tk.Label(field_frame, text=label, width=25, anchor='w', bg="#f0f0f0").pack(side=tk.LEFT)
            entry = ttk.Entry(field_frame, width=15)
            entry.pack(side=tk.LEFT, padx=5)
            self.entries[field] = entry
            
            tk.Label(field_frame, text=f"Range: {tooltip}", font=("Arial", 8), fg="gray", bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        ore_frame = Frame(input_right, bg="#f0f0f0")
        ore_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(ore_frame, text="Ore Type:", width=25, anchor='w', bg="#f0f0f0").pack(side=tk.LEFT)
        self.ore_type_var = tk.StringVar()
        ore_type_combo = ttk.Combobox(ore_frame, textvariable=self.ore_type_var, width=15)
        ore_type_combo['values'] = INDIAN_ORE_TYPES
        ore_type_combo.set("generic")
        ore_type_combo.pack(side=tk.LEFT, padx=5)
        self.entries['ore_type'] = self.ore_type_var
        
        notes_frame = LabelFrame(self.input_tab, text="Additional Notes", font=("Arial", 12, "bold"), padx=10, pady=10, bg="#f0f0f0")
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.notes_text = tk.Text(notes_frame, width=50, height=5)
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        
        button_frame = Frame(self.input_tab, bg="#f0f0f0", pady=5)
        button_frame.pack(fill=tk.X, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Calculate Design (DGMS Compliant)",
            command=self._calculate,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Clear Inputs",
            command=self._clear_inputs
        ).pack(side=tk.LEFT, padx=5)

    def _setup_results_area(self):
        result_frame = LabelFrame(self.results_tab, text="Results (DGMS Compliant Analysis)", font=("Arial", 12, "bold"), padx=10, pady=10, bg="#f0f0f0")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        text_frame = Frame(result_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_y = Scrollbar(text_frame)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollbar_x = Scrollbar(text_frame, orient='horizontal')
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.results_text = tk.Text(
            text_frame,
            wrap=tk.NONE,
            height=15,
            width=80,
            font=("Courier New", 10),
            yscrollcommand=scrollbar_y.set,
            xscrollcommand=scrollbar_x.set
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_y.config(command=self.results_text.yview)
        scrollbar_x.config(command=self.results_text.xview)
        
        self.results_text.tag_configure("heading", font=("Arial", 11, "bold"))
        self.results_text.tag_configure("subheading", font=("Arial", 10, "bold"))
        self.results_text.tag_configure("normal", font=("Courier New", 10))
        self.results_text.tag_configure("inr", foreground="blue", font=("Arial", 12, "bold"))
        self.results_text.tag_configure("warning", foreground="red")
        self.results_text.tag_configure("compliant", foreground="green")
        self.results_text.tag_configure("noncompliant", foreground="red")
        
        export_frame = Frame(self.results_tab, bg="#f0f0f0", pady=5)
        export_frame.pack(fill=tk.X, padx=5)
        
        ttk.Button(
            export_frame,
            text="Export PDF Report (DGMS Format)",
            command=self._export_pdf_report
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="Export Summary Text",
            command=self._export_summary_text
        ).pack(side=tk.LEFT, padx=5)

    def _setup_visualization_area(self):
        viz_frame = Frame(self.visualization_tab, bg="#f0f0f0", padx=10, pady=10)
        viz_frame.pack(fill=tk.BOTH, expand=True)
        
        self.viz_notebook = ttk.Notebook(viz_frame)
        self.viz_notebook.pack(fill=tk.BOTH, expand=True)
        
        self.stability_viz_tab = ttk.Frame(self.viz_notebook)
        self.viz_notebook.add(self.stability_viz_tab, text="Stability Analysis")
        
        self.cost_viz_tab = ttk.Frame(self.viz_notebook)
        self.viz_notebook.add(self.cost_viz_tab, text="Cost Breakdown")
        
        self.stability_frame = ttk.Frame(self.stability_viz_tab)
        self.stability_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            self.stability_frame,
            text="Stability visualization will appear here after calculation.",
            font=("Arial", 12),
            anchor=tk.CENTER
        ).pack(fill=tk.BOTH, expand=True)
        
        self.cost_frame = ttk.Frame(self.cost_viz_tab)
        self.cost_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            self.cost_frame,
            text="Cost visualization will appear here after calculation.",
            font=("Arial", 12),
            anchor=tk.CENTER
        ).pack(fill=tk.BOTH, expand=True)

    def _create_footer(self, parent):
        footer_frame = Frame(parent, bg="#1a5276", padx=10, pady=10)
        footer_frame.pack(fill=tk.X, padx=5, pady=5)

        footer_label = tk.Label(
            footer_frame,
            text="© 2025 Mining Stope Design Tool - All Rights Reserved",
            font=("Arial", 10, "italic"),
            bg="#1a5276",
            fg="white"
        )
        footer_label.pack()

    def _get_inputs(self):
        inputs = {}
        for field, entry in self.entries.items():
            if field == 'ore_type':
                inputs[field] = entry.get()
            else:
                inputs[field] = entry.get()
        return inputs

    def _calculate(self):
        self.results_text.delete(1.0, tk.END)
        inputs = self._get_inputs()
        validation = validate_inputs(inputs)
        
        if validation['valid']:
            results = calculate_stope_design(validation['data'])
            self._show_results(results, validation.get('warnings', []))
            self._update_visualizations(results)
        else:
            self._show_error(validation['message'])

    def _show_results(self, results, warnings=None):
        self.results_text.delete(1.0, tk.END)

        if warnings and len(warnings) > 0:
            self.results_text.insert(tk.END, "DGMS REGULATORY WARNINGS:\n", "heading")
            for warning in warnings:
                self.results_text.insert(tk.END, f"• {warning}\n", "warning")
            self.results_text.insert(tk.END, "\n")

        if 'error' in results:
            self.results_text.insert(tk.END, "ERROR:\n", "heading")
            self.results_text.insert(tk.END, f"{results['error']}\n", "warning")
            return

        self.results_text.insert(tk.END, "STOPE DESIGN RESULTS\n", "heading")
        self.results_text.insert(tk.END, f"Stope Type: {results['stope_type']}\n\n")
        
        self.results_text.insert(tk.END, "DIMENSIONS:\n", "subheading")
        for key, value in results['dimensions'].items():
            if key in ['rmr', 'q_value', 'stability_number', 'stope_type']:
                # These are dimensionless values - no units
                self.results_text.insert(tk.END, f"  {key.replace('_', ' ').title()}: {value}\n")
            elif key == 'volume':
                # Volume needs cubic meters
                self.results_text.insert(tk.END, f"  {key.replace('_', ' ').title()}: {value} m³\n")
            else:
                # Physical dimensions need meters
                self.results_text.insert(tk.END, f"  {key.replace('_', ' ').title()}: {value} m\n")
        
        self.results_text.insert(tk.END, "\nSTABILITY ANALYSIS:\n", "subheading")
        
        stability = results['stability']
        safety_factor = stability.get('safety_factor', 'N/A')
        dgms_compliant = stability.get('dgms_compliant', False)
        
        sf_tag = "compliant" if dgms_compliant else "noncompliant"
        compliance_text = "✓ DGMS Compliant" if dgms_compliant else "✗ Below DGMS Minimum"
        
        self.results_text.insert(tk.END, f"  Safety Factor: {safety_factor} ({compliance_text})\n", sf_tag)
        
        for key, value in stability.items():
            if key not in ['safety_factor', 'dgms_compliant']:
                self.results_text.insert(tk.END, f"  {key.replace('_', ' ').title()}: {value}\n")
        
        costs = results['costs']
        self.results_text.insert(tk.END, "\nCOST ANALYSIS:\n", "subheading")
        
        if 'total' in costs:
            total_inr = costs['total']
            self.results_text.insert(tk.END, f"  Total Cost: INR {total_inr:,.2f}\n", "inr")
        
        self.results_text.insert(tk.END, "\n  Cost Breakdown:\n")
        exclude_keys = ['total']
        for key, value in costs.items():
            if key not in exclude_keys:
                self.results_text.insert(tk.END, f"    - {key.replace('_', ' ').title()}: INR {value:,.2f}\n")
        
        notes = self.notes_text.get(1.0, tk.END).strip()
        if notes:
            self.results_text.insert(tk.END, "\nADDITIONAL NOTES:\n", "subheading")
            self.results_text.insert(tk.END, f"  {notes}\n")
        
        self.results_text.insert(tk.END, "\nFor detailed visualizations, see the Visualizations tab.\n")

    def _update_visualizations(self, results):
        """Enhanced visualization update with multiple views"""
        # Clear existing visualizations
        for widget in self.stability_frame.winfo_children():
            widget.destroy()
        for widget in self.cost_frame.winfo_children():
            widget.destroy()

        # Add new visualization tabs for enhanced views
        if not hasattr(self, 'viz_detailed_notebook'):
            self.viz_detailed_notebook = ttk.Notebook(self.visualization_tab)
            self.viz_detailed_notebook.pack(fill=tk.BOTH, expand=True)

            # Create sub-tabs for different visualization types
            self.viz_3d_tab = ttk.Frame(self.viz_detailed_notebook)
            self.viz_detailed_notebook.add(self.viz_3d_tab, text="3D Views")

            self.viz_sections_tab = ttk.Frame(self.viz_detailed_notebook)
            self.viz_detailed_notebook.add(self.viz_sections_tab, text="Sections")

            self.viz_plan_tab = ttk.Frame(self.viz_detailed_notebook)
            self.viz_detailed_notebook.add(self.viz_plan_tab, text="Plan View")

            self.viz_analysis_tab = ttk.Frame(self.viz_detailed_notebook)
            self.viz_detailed_notebook.add(self.viz_analysis_tab, text="Analysis")

        # Clear all sub-tabs
        for tab in [self.viz_3d_tab, self.viz_sections_tab, self.viz_plan_tab, self.viz_analysis_tab]:
            for widget in tab.winfo_children():
                widget.destroy()

        # Display enhanced visualizations
        visualization_files = [
            ('reports/stope_3d_isometric.png', self.viz_3d_tab, "3D Isometric View"),
            ('reports/stope_cross_sections.png', self.viz_sections_tab, "Cross Sections"),
            ('reports/stope_plan_view.png', self.viz_plan_tab, "Plan Layout"),
            ('reports/safety_factor_gauge.png', self.viz_analysis_tab, "Safety Analysis"),
            ('reports/stress_strength_comparison.png', self.viz_analysis_tab, "Stress Analysis")
        ]

        for file_path, parent_tab, description in visualization_files:
            if os.path.exists(file_path):
                self._display_enhanced_image(file_path, parent_tab, description)
            else:
                ttk.Label(
                    parent_tab,
                    text=f"{description} not available.",
                    font=("Arial", 10),
                    foreground="orange"
                ).pack(pady=20)

    def _display_enhanced_image(self, image_path, parent_frame, description):
        """Display image with enhanced formatting and description"""
        try:
            from PIL import Image, ImageTk
            # Create frame for image and description
            img_frame = ttk.Frame(parent_frame)
            img_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            # Add description label
            desc_label = ttk.Label(
                img_frame,
                text=description,
                font=("Arial", 12, "bold"),
                foreground="navy"
            )
            desc_label.pack(pady=(0, 10))
            # Load and display image
            img = Image.open(image_path)
            # Calculate optimal size maintaining aspect ratio
            max_width = 800
            max_height = 600
            img_width, img_height = img.size
            if img_width > max_width or img_height > max_height:
                ratio = min(max_width/img_width, max_height/img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                img = img.resize((new_width, new_height), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            # Create scrollable frame for large images
            canvas = tk.Canvas(img_frame, highlightthickness=0)
            scrollbar_v = ttk.Scrollbar(img_frame, orient="vertical", command=canvas.yview)
            scrollbar_h = ttk.Scrollbar(img_frame, orient="horizontal", command=canvas.xview)
            scrollable_frame = ttk.Frame(canvas)
            canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            # Add image to scrollable frame
            img_label = ttk.Label(scrollable_frame, image=tk_img)
            img_label.image = tk_img  # Keep reference
            img_label.pack()
            # Update scroll region
            scrollable_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Pack scrollbars and canvas
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar_v.pack(side="right", fill="y")
            scrollbar_h.pack(side="bottom", fill="x")
        except Exception as e:
            print(f"Error displaying enhanced image {image_path}: {e}")
            error_label = ttk.Label(
                parent_frame,
                text=f"Error loading {description}: {str(e)}",
                font=("Arial", 10),
                foreground="red"
            )
            error_label.pack(pady=20)

    def _show_error(self, message):
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "ERROR:\n", "heading")
        self.results_text.insert(tk.END, message + "\n", "warning")
        messagebox.showerror("Input Error", message)

    def _export_pdf_report(self):
        def run_pdf_export():
            from datetime import datetime
            inputs = self._get_inputs()
            validation = validate_inputs(inputs)
            if validation['valid']:
                results = calculate_stope_design(validation['data'])
                notes = self.notes_text.get(1.0, tk.END).strip()
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                folder = f"reports/report_{timestamp}"
                os.makedirs(folder, exist_ok=True)
                filepath = f"{folder}/stope_report.pdf"
                try:
                    generate_pdf_report(results, filepath, notes)
                    self.root.after(0, lambda: self.results_text.insert(tk.END, f"\nPDF report exported automatically to: {filepath}\n", "compliant"))
                except Exception as e:
                    self.root.after(0, lambda e=e: self._show_error(f"PDF export failed: {e}"))
            else:
                self.root.after(0, lambda: self._show_error(validation['message']))
        threading.Thread(target=run_pdf_export, daemon=True).start()

    def _export_summary_text(self):
        from datetime import datetime
        inputs = self._get_inputs()
        validation = validate_inputs(inputs)
        if validation['valid']:
            results = calculate_stope_design(validation['data'])
            notes = self.notes_text.get(1.0, tk.END).strip()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            folder = f"reports/report_{timestamp}"
            os.makedirs(folder, exist_ok=True)
            filepath = f"{folder}/stope_summary.txt"
            try:
                generate_summary_text(results, filepath, notes)
                self.results_text.insert(tk.END, f"\nSummary text exported automatically to: {filepath}\n", "compliant")
            except Exception as e:
                self._show_error(f"Summary export failed: {e}")
        else:
            self._show_error(validation['message'])

    def _clear_inputs(self):
        for field, entry in self.entries.items():
            if field == 'ore_type':
                self.ore_type_var.set("generic")
            else:
                entry.delete(0, tk.END)
        self.results_text.delete(1.0, tk.END)
        self.notes_text.delete(1.0, tk.END)

    def _show_dgms_guidelines(self):
        guidelines = (
            "DGMS Guidelines for Underground Mining:\n\n"
            "1. Safety Factor: Minimum 1.5 (DGMS Tech. Circular No. 3 of 2019)\n"
            "2. Minimum pillar width: 3.0 meters\n"
            "3. Minimum Rock Quality Designation (RQD): 25%\n"
            "4. Maximum allowable dip angle: 70 degrees\n"
            "5. Ventilation requirements per DGMS Circular No. 01 of 2011\n"
            "6. Strata control as per MMR 2011 Regulation 111\n\n"
            "All designs must comply with the Metalliferous Mines Regulations (MMR) "
            "and Indian Bureau of Mines (IBM) standards."
        )
        
        popup = tk.Toplevel(self.root)
        popup.title("DGMS Guidelines")
        popup.geometry("600x400")
        
        text = tk.Text(popup, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        text.insert(tk.END, guidelines)
        text.config(state=tk.DISABLED)

    def _show_about(self):
        about_text = (
            "Mining Stope Design Tool - Indian Standards Edition\n\n"
            "Version: 2.0 (April 2025)\n\n"
            "This application implements stope design calculations following "
            "Indian mining standards including DGMS, MMR, and IBM guidelines.\n\n"
            "All costs are displayed in Indian Rupees (INR)."
        )
        
        messagebox.showinfo("About", about_text)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MiningStopeDesignApp()
    app.run()
