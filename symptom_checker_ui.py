import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import threading
from dotenv import load_dotenv
from openai import OpenAI
import markdown
from symptom_checker import get_symptom_analysis, check_emergency

load_dotenv()

class SymptomCheckerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Healthcare Symptom Checker")
        self.root.geometry("800x700")

        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Create tabs
        self.basic_info_frame = ttk.Frame(self.notebook)
        self.symptoms_frame = ttk.Frame(self.notebook)
        self.tests_frame = ttk.Frame(self.notebook)
        self.analysis_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.basic_info_frame, text='Basic Info')
        self.notebook.add(self.symptoms_frame, text='Symptoms')
        self.notebook.add(self.tests_frame, text='Test Results')
        self.notebook.add(self.analysis_frame, text='Analysis')

        # Initialize data storage
        self.basic_info = {}
        self.symptoms = {}
        self.test_results = {}

        # Loading state
        self.is_loading = False

        # Sample data from test file
        self.sample_data = self.load_sample_data()

        # Setup each tab
        self.setup_basic_info_tab()
        self.setup_symptoms_tab()
        self.setup_tests_tab()
        self.setup_analysis_tab()

    def setup_basic_info_tab(self):
        frame = self.basic_info_frame

        # Title
        ttk.Label(frame, text="Basic Information", font=('Arial', 14, 'bold')).pack(pady=10)

        # Age
        ttk.Label(frame, text="Age:").pack(anchor='w', padx=20)
        self.age_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.age_var).pack(fill='x', padx=20, pady=(0,10))

        # Gender
        ttk.Label(frame, text="Gender (M/F):").pack(anchor='w', padx=20)
        self.gender_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.gender_var).pack(fill='x', padx=20, pady=(0,10))

        # Weight
        ttk.Label(frame, text="Weight (kg):").pack(anchor='w', padx=20)
        self.weight_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.weight_var).pack(fill='x', padx=20, pady=(0,10))

        # Temperature
        ttk.Label(frame, text="Temperature (°C):").pack(anchor='w', padx=20)
        self.temp_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.temp_var).pack(fill='x', padx=20, pady=(0,10))

        # Duration
        ttk.Label(frame, text="Duration of symptoms (days):").pack(anchor='w', padx=20)
        self.duration_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.duration_var).pack(fill='x', padx=20, pady=(0,10))

        # Chronic diseases
        ttk.Label(frame, text="Any chronic diseases?").pack(anchor='w', padx=20)
        self.chronic_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Yes", variable=self.chronic_var).pack(anchor='w', padx=40, pady=(0,10))

        # Sample data buttons
        sample_frame = ttk.Frame(frame)
        sample_frame.pack(fill='x', padx=20, pady=(10,0))
        ttk.Label(sample_frame, text="Quick Fill:").pack(side='left')
        ttk.Button(sample_frame, text="Viral Fever", command=lambda: self.load_sample_basic_info("viral_fever")).pack(side='left', padx=(5,0))
        ttk.Button(sample_frame, text="Dengue", command=lambda: self.load_sample_basic_info("dengue")).pack(side='left', padx=(5,0))
        ttk.Button(sample_frame, text="Emergency", command=lambda: self.load_sample_basic_info("emergency")).pack(side='left', padx=(5,0))

    def setup_symptoms_tab(self):
        frame = self.symptoms_frame

        # Title
        ttk.Label(frame, text="Symptoms", font=('Arial', 14, 'bold')).pack(pady=10)

        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Symptom checkboxes
        self.symptom_vars = {}
        symptoms_list = [
            "fever", "fatigue", "cough", "headache", "body_pain", "nausea",
            "vomiting", "diarrhea", "rash", "sore_throat", "shortness_of_breath",
            "chest_pain", "confusion", "recent_travel", "medication", "appetite_change",
            "urine_change", "weight_loss", "night_sweats", "exposure"
        ]

        for symptom in symptoms_list:
            var = tk.BooleanVar()
            self.symptom_vars[symptom] = var
            ttk.Checkbutton(scrollable_frame, text=symptom.replace('_', ' ').title(),
                          variable=var).pack(anchor='w', padx=20, pady=2)

        # Additional fields for fever duration and cough type
        ttk.Label(scrollable_frame, text="Fever Duration (days):").pack(anchor='w', padx=20, pady=(10,0))
        self.fever_duration_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.fever_duration_var).pack(fill='x', padx=20, pady=(0,10))

        ttk.Label(scrollable_frame, text="Cough Type (dry/productive):").pack(anchor='w', padx=20, pady=(10,0))
        self.cough_type_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.cough_type_var).pack(fill='x', padx=20, pady=(0,10))

        # Sample data buttons
        sample_frame = ttk.Frame(scrollable_frame)
        sample_frame.pack(fill='x', padx=20, pady=(10,0))
        ttk.Label(sample_frame, text="Quick Fill:").pack(side='left')
        ttk.Button(sample_frame, text="Viral Fever", command=lambda: self.load_sample_symptoms("viral_fever")).pack(side='left', padx=(5,0))
        ttk.Button(sample_frame, text="Dengue", command=lambda: self.load_sample_symptoms("dengue")).pack(side='left', padx=(5,0))
        ttk.Button(sample_frame, text="Emergency", command=lambda: self.load_sample_symptoms("emergency")).pack(side='left', padx=(5,0))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_tests_tab(self):
        frame = self.tests_frame

        # Title
        ttk.Label(frame, text="Test Results", font=('Arial', 14, 'bold')).pack(pady=10)

        # Create canvas and scrollbar
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Test result entries
        self.test_vars = {}
        tests_list = [
            "WBC", "Platelets", "Hemoglobin", "Blood_Sugar", "ALT", "Creatinine"
        ]

        for test in tests_list:
            ttk.Label(scrollable_frame, text=f"{test}:").pack(anchor='w', padx=20, pady=(5,0))
            var = tk.StringVar()
            self.test_vars[test] = var
            ttk.Entry(scrollable_frame, textvariable=var).pack(fill='x', padx=20, pady=(0,5))

        # Boolean tests
        boolean_tests = ["Malaria", "Dengue", "Typhoid"]
        self.boolean_test_vars = {}

        for test in boolean_tests:
            ttk.Label(scrollable_frame, text=f"{test} (positive/negative):").pack(anchor='w', padx=20, pady=(5,0))
            var = tk.StringVar()
            self.boolean_test_vars[test] = var
            ttk.Entry(scrollable_frame, textvariable=var).pack(fill='x', padx=20, pady=(0,5))

        # Sample data buttons
        sample_frame = ttk.Frame(scrollable_frame)
        sample_frame.pack(fill='x', padx=20, pady=(10,0))
        ttk.Label(sample_frame, text="Quick Fill:").pack(side='left')
        ttk.Button(sample_frame, text="Viral Fever", command=lambda: self.load_sample_tests("viral_fever")).pack(side='left', padx=(5,0))
        ttk.Button(sample_frame, text="Dengue", command=lambda: self.load_sample_tests("dengue")).pack(side='left', padx=(5,0))
        ttk.Button(sample_frame, text="Emergency", command=lambda: self.load_sample_tests("emergency")).pack(side='left', padx=(5,0))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def setup_analysis_tab(self):
        frame = self.analysis_frame

        # Title
        ttk.Label(frame, text="Analysis Results", font=('Arial', 14, 'bold')).pack(pady=10)

        # Loading indicator
        self.loading_label = ttk.Label(frame, text="", font=('Arial', 12))
        self.loading_label.pack(pady=(0,10))

        # Output text area
        self.output_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=20)
        self.output_text.pack(fill='both', expand=True, padx=20, pady=(0,10))

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', padx=20, pady=(0,10))

        self.analyze_button = ttk.Button(button_frame, text="Analyze", command=self.analyze)
        self.analyze_button.pack(side='left', padx=(0,10))
        ttk.Button(button_frame, text="Clear", command=self.clear_all).pack(side='left', padx=(0,10))
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side='right')

    def collect_basic_info(self):
        try:
            age = int(self.age_var.get()) if self.age_var.get() else None
        except ValueError:
            age = None

        gender = self.gender_var.get().strip().upper() if self.gender_var.get().strip() else None
        if gender not in ["M", "F"]:
            gender = None

        try:
            weight = float(self.weight_var.get()) if self.weight_var.get() else None
        except ValueError:
            weight = None

        try:
            temperature = float(self.temp_var.get()) if self.temp_var.get() else None
        except ValueError:
            temperature = None

        duration = self.duration_var.get().strip() if self.duration_var.get().strip() else None
        chronic_diseases = self.chronic_var.get()

        self.basic_info = {
            "age": age,
            "gender": gender,
            "weight": weight,
            "temperature": temperature,
            "duration": duration,
            "chronic_diseases": chronic_diseases,
        }

    def collect_symptoms(self):
        self.symptoms = {}
        for symptom, var in self.symptom_vars.items():
            self.symptoms[symptom] = var.get()

        # Additional details
        try:
            fever_duration = int(self.fever_duration_var.get()) if self.fever_duration_var.get() else None
            self.symptoms["fever_duration"] = fever_duration
        except ValueError:
            self.symptoms["fever_duration"] = None

        cough_type = self.cough_type_var.get().strip().lower() if self.cough_type_var.get().strip() else None
        if cough_type in ["dry", "productive"]:
            self.symptoms["cough_type"] = cough_type
        else:
            self.symptoms["cough_type"] = None

    def collect_test_results(self):
        self.test_results = {}

        # Numeric tests
        for test, var in self.test_vars.items():
            value = var.get().strip()
            if value:
                try:
                    self.test_results[test] = float(value)
                except ValueError:
                    self.test_results[test] = None
            else:
                self.test_results[test] = None

        # Boolean tests
        for test, var in self.boolean_test_vars.items():
            value = var.get().strip().lower()
            if value in ["positive", "negative"]:
                self.test_results[test] = (value == "positive")
            else:
                self.test_results[test] = None

    def analyze(self):
        if self.is_loading:
            return

        # Collect all data
        self.collect_basic_info()
        self.collect_symptoms()
        self.collect_test_results()

        user_data = {
            "basic_info": self.basic_info,
            "symptoms": self.symptoms,
            "test_results": self.test_results,
        }

        # Check for emergency
        emergency = check_emergency(self.symptoms, self.basic_info)

        if emergency:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "⚠️ EMERGENCY ALERT: Based on your symptoms, seek immediate medical attention!\n\n")
            self.output_text.insert(tk.END, "Please call emergency services or go to the nearest hospital.\n\n")
            self.output_text.insert(tk.END, "Analysis skipped due to emergency symptoms.")
            messagebox.showwarning("Emergency Alert", "Emergency symptoms detected! Please seek immediate medical attention.")
            return

        # Start loading
        self.start_loading()

        # Run analysis in separate thread
        analysis_thread = threading.Thread(target=self.perform_analysis, args=(user_data,))
        analysis_thread.start()

    def start_loading(self):
        self.is_loading = True
        self.analyze_button.config(state='disabled')
        self.loading_label.config(text="🔄 Analyzing symptoms... Please wait.")
        self.output_text.delete(1.0, tk.END)
        self.root.update()

    def stop_loading(self):
        self.is_loading = False
        self.analyze_button.config(state='normal')
        self.loading_label.config(text="")
        self.root.update()

    def perform_analysis(self, user_data):
        try:
            analysis = get_symptom_analysis(user_data)
            # Convert markdown to HTML-like text for display
            html_content = markdown.markdown(analysis, extensions=['extra', 'codehilite'])
            # Simple HTML to text conversion for ScrolledText
            plain_text = self.html_to_plain_text(html_content)

            # Update UI in main thread
            self.root.after(0, lambda: self.display_analysis(plain_text))
        except Exception as e:
            self.root.after(0, lambda: self.display_error(str(e)))

    def html_to_plain_text(self, html):
        """Convert basic HTML to plain text for ScrolledText"""
        import re

        # Remove HTML tags but keep structure
        text = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'\n\1\n' + '='*50 + '\n', html)
        text = re.sub(r'<h[1-6][^>]*>(.*?)</h[1-6]>', r'\n\1\n' + '-'*30 + '\n', text)
        text = re.sub(r'<strong[^>]*>(.*?)</strong>', r'\1', text)  # Remove ** markers
        text = re.sub(r'<em[^>]*>(.*?)</em>', r'\1', text)  # Remove * markers
        text = re.sub(r'<li[^>]*>(.*?)</li>', r'• \1\n', text)
        text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n\n', text)
        text = re.sub(r'<br[^>]*>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)  # Remove remaining tags

        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        return text.strip()

    def display_analysis(self, analysis):
        self.stop_loading()
        self.output_text.insert(tk.END, analysis)

    def display_error(self, error_msg):
        self.stop_loading()
        messagebox.showerror("Error", f"Failed to get analysis: {error_msg}")

    def load_sample_data(self):
        """Load sample data from test file."""
        return {
            "viral_fever": {
                "basic_info": {
                    "age": 25,
                    "gender": "M",
                    "weight": 70.0,
                    "temperature": 38.5,
                    "duration": "3",
                    "chronic_diseases": False
                },
                "symptoms": {
                    "fever": True,
                    "fatigue": True,
                    "cough": False,
                    "headache": True,
                    "body_pain": True,
                    "nausea": False,
                    "vomiting": False,
                    "diarrhea": False,
                    "rash": False,
                    "sore_throat": True,
                    "shortness_of_breath": False,
                    "chest_pain": False,
                    "confusion": False,
                    "recent_travel": False,
                    "medication": False,
                    "appetite_change": True,
                    "urine_change": False,
                    "weight_loss": False,
                    "night_sweats": False,
                    "exposure": False,
                    "fever_duration": 3,
                    "cough_type": None
                },
                "test_results": {
                    "WBC": 6500,
                    "Platelets": 180000,
                    "Hemoglobin": 14.0,
                    "Blood_Sugar": 90,
                    "ALT": 25,
                    "Creatinine": 0.8,
                    "Malaria": False,
                    "Dengue": False,
                    "Typhoid": False
                }
            },
            "dengue": {
                "basic_info": {
                    "age": 30,
                    "gender": "F",
                    "weight": 60.0,
                    "temperature": 39.2,
                    "duration": "5",
                    "chronic_diseases": False
                },
                "symptoms": {
                    "fever": True,
                    "fatigue": True,
                    "cough": False,
                    "headache": True,
                    "body_pain": True,
                    "nausea": True,
                    "vomiting": False,
                    "diarrhea": False,
                    "rash": True,
                    "sore_throat": False,
                    "shortness_of_breath": False,
                    "chest_pain": False,
                    "confusion": False,
                    "recent_travel": True,
                    "medication": False,
                    "appetite_change": True,
                    "urine_change": False,
                    "weight_loss": False,
                    "night_sweats": False,
                    "exposure": False,
                    "fever_duration": 5,
                    "cough_type": None
                },
                "test_results": {
                    "WBC": 3000,
                    "Platelets": 80000,
                    "Hemoglobin": 12.5,
                    "Blood_Sugar": 95,
                    "ALT": 45,
                    "Creatinine": 0.9,
                    "Malaria": False,
                    "Dengue": True,
                    "Typhoid": False
                }
            },
            "emergency": {
                "basic_info": {
                    "age": 45,
                    "gender": "M",
                    "weight": 80.0,
                    "temperature": 40.5,
                    "duration": "2",
                    "chronic_diseases": True
                },
                "symptoms": {
                    "fever": True,
                    "fatigue": True,
                    "cough": False,
                    "headache": True,
                    "body_pain": True,
                    "nausea": False,
                    "vomiting": False,
                    "diarrhea": False,
                    "rash": False,
                    "sore_throat": False,
                    "shortness_of_breath": True,
                    "chest_pain": True,
                    "confusion": True,
                    "recent_travel": False,
                    "medication": True,
                    "appetite_change": False,
                    "urine_change": False,
                    "weight_loss": False,
                    "night_sweats": False,
                    "exposure": False,
                    "fever_duration": 2,
                    "cough_type": None
                },
                "test_results": {}
            }
        }

    def load_sample_basic_info(self, sample_type):
        """Load sample basic info data."""
        data = self.sample_data[sample_type]["basic_info"]
        self.age_var.set(str(data["age"]) if data["age"] else "")
        self.gender_var.set(data["gender"] if data["gender"] else "")
        self.weight_var.set(str(data["weight"]) if data["weight"] else "")
        self.temp_var.set(str(data["temperature"]) if data["temperature"] else "")
        self.duration_var.set(data["duration"] if data["duration"] else "")
        self.chronic_var.set(data["chronic_diseases"])

    def load_sample_symptoms(self, sample_type):
        """Load sample symptoms data."""
        data = self.sample_data[sample_type]["symptoms"]
        for symptom, var in self.symptom_vars.items():
            var.set(data.get(symptom, False))

        self.fever_duration_var.set(str(data.get("fever_duration", "")) if data.get("fever_duration") else "")
        self.cough_type_var.set(data.get("cough_type", "") if data.get("cough_type") else "")

    def load_sample_tests(self, sample_type):
        """Load sample test results data."""
        data = self.sample_data[sample_type]["test_results"]

        # Numeric tests
        for test, var in self.test_vars.items():
            value = data.get(test)
            var.set(str(value) if value is not None else "")

        # Boolean tests
        for test, var in self.boolean_test_vars.items():
            value = data.get(test)
            if value is True:
                var.set("positive")
            elif value is False:
                var.set("negative")
            else:
                var.set("")

    def clear_all(self):
        # Clear basic info
        self.age_var.set("")
        self.gender_var.set("")
        self.weight_var.set("")
        self.temp_var.set("")
        self.duration_var.set("")
        self.chronic_var.set(False)

        # Clear symptoms
        for var in self.symptom_vars.values():
            var.set(False)
        self.fever_duration_var.set("")
        self.cough_type_var.set("")

        # Clear tests
        for var in self.test_vars.values():
            var.set("")
        for var in self.boolean_test_vars.values():
            var.set("")

        # Clear output
        self.output_text.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SymptomCheckerUI(root)
    root.mainloop()