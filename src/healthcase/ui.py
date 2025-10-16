"""
Tkinter-based GUI for Healthcase Symptom Checker.

Provides a user-friendly graphical interface for symptom analysis.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from typing import Dict, Any, Optional
from .logic import SymptomAnalyzer, MockAnalyzer
from .validators import InputValidator
from .exceptions import ValidationError, EmergencyDetectedError, APIError
from .logger import get_logger
from .config import config

logger = get_logger(__name__)


class SymptomCheckerGUI:
    """Tkinter-based GUI for symptom checking."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(config.APP_NAME)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")

        # Initialize data storage
        self.basic_info = {}
        self.symptoms = {}
        self.test_results = {}

        # Loading state
        self.is_loading = False

        # Sample data for testing
        self.sample_data = self._load_sample_data()

        # Setup UI
        self._setup_ui()

        logger.info("GUI initialized")

    def _setup_ui(self):
        """Setup the main UI components."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
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

        # Setup each tab
        self._setup_basic_info_tab()
        self._setup_symptoms_tab()
        self._setup_tests_tab()
        self._setup_analysis_tab()

    def _setup_basic_info_tab(self):
        """Setup basic information tab."""
        frame = self.basic_info_frame

        # Title
        ttk.Label(frame, text="Basic Information", font=('Arial', 14, 'bold')).pack(pady=10)

        # Create form fields
        self.age_var = tk.StringVar()
        self.gender_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.temp_var = tk.StringVar()
        self.duration_var = tk.StringVar()
        self.chronic_var = tk.BooleanVar()

        fields = [
            ("Age:", self.age_var),
            ("Gender (M/F):", self.gender_var),
            ("Weight (kg):", self.weight_var),
            ("Temperature (°C):", self.temp_var),
            ("Duration of symptoms (days):", self.duration_var),
        ]

        for label_text, var in fields:
            ttk.Label(frame, text=label_text).pack(anchor='w', padx=20)
            ttk.Entry(frame, textvariable=var).pack(fill='x', padx=20, pady=(0,10))

        # Chronic diseases checkbox
        ttk.Checkbutton(frame, text="Any chronic diseases?", variable=self.chronic_var).pack(anchor='w', padx=20, pady=(0,10))

        # Sample data buttons
        self._add_sample_buttons(frame, "basic_info", ["viral_fever", "dengue", "hep_a", "tuberculosis", "ckd", "diabetes", "emergency"])

    def _setup_symptoms_tab(self):
        """Setup symptoms tab."""
        frame = self.symptoms_frame

        # Title
        ttk.Label(frame, text="Symptoms", font=('Arial', 14, 'bold')).pack(pady=10)

        # Create scrollable frame
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

        # Additional fields
        ttk.Label(scrollable_frame, text="Fever Duration (days):").pack(anchor='w', padx=20, pady=(10,0))
        self.fever_duration_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.fever_duration_var).pack(fill='x', padx=20, pady=(0,10))

        ttk.Label(scrollable_frame, text="Cough Type (dry/productive):").pack(anchor='w', padx=20, pady=(10,0))
        self.cough_type_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.cough_type_var).pack(fill='x', padx=20, pady=(0,10))

        # Sample data buttons
        self._add_sample_buttons(scrollable_frame, "symptoms", ["viral_fever", "dengue", "hep_a", "tuberculosis", "ckd", "diabetes", "emergency"])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _setup_tests_tab(self):
        """Setup test results tab."""
        frame = self.tests_frame

        # Title
        ttk.Label(frame, text="Test Results", font=('Arial', 14, 'bold')).pack(pady=10)

        # Create scrollable frame
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
        self.boolean_test_vars = {}
        boolean_tests = ["Malaria", "Dengue", "Typhoid"]

        for test in boolean_tests:
            ttk.Label(scrollable_frame, text=f"{test} (positive/negative):").pack(anchor='w', padx=20, pady=(5,0))
            var = tk.StringVar()
            self.boolean_test_vars[test] = var
            ttk.Entry(scrollable_frame, textvariable=var).pack(fill='x', padx=20, pady=(0,5))

        # Sample data buttons
        self._add_sample_buttons(scrollable_frame, "tests", ["viral_fever", "dengue", "hep_a", "tuberculosis", "ckd", "diabetes", "emergency"])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _setup_analysis_tab(self):
        """Setup analysis tab."""
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

        self.analyze_button = ttk.Button(button_frame, text="Analyze", command=self._analyze)
        self.analyze_button.pack(side='left', padx=(0,10))

        ttk.Button(button_frame, text="Clear", command=self._clear_all).pack(side='left', padx=(0,10))
        ttk.Button(button_frame, text="Exit", command=self.root.quit).pack(side='right')

    def _add_sample_buttons(self, frame: ttk.Frame, data_type: str, sample_types: list):
        """Add sample data buttons to a frame."""
        sample_frame = ttk.Frame(frame)
        sample_frame.pack(fill='x', padx=20, pady=(10,0))
        ttk.Label(sample_frame, text="Quick Fill:").pack(side='left')

        for sample_type in sample_types:
            display_name = sample_type.replace('_', ' ').title()
            btn = ttk.Button(sample_frame, text=display_name,
                           command=lambda st=sample_type, dt=data_type: self._load_sample_data_for_tab(dt, st))
            btn.pack(side='left', padx=(5,0))

    def _load_sample_data_for_tab(self, data_type: str, sample_type: str):
        """Load sample data for a specific tab."""
        if data_type == "basic_info":
            self._load_sample_basic_info(sample_type)
        elif data_type == "symptoms":
            self._load_sample_symptoms(sample_type)
        elif data_type == "tests":
            self._load_sample_tests(sample_type)

    def _load_sample_basic_info(self, sample_type: str):
        """Load sample basic info data."""
        data = self.sample_data[sample_type]["basic_info"]
        self.age_var.set(str(data["age"]) if data["age"] else "")
        self.gender_var.set(data["gender"] if data["gender"] else "")
        self.weight_var.set(str(data["weight"]) if data["weight"] else "")
        self.temp_var.set(str(data["temperature"]) if data["temperature"] else "")
        self.duration_var.set(data["duration"] if data["duration"] else "")
        self.chronic_var.set(data["chronic_diseases"])

    def _load_sample_symptoms(self, sample_type: str):
        """Load sample symptoms data."""
        data = self.sample_data[sample_type]["symptoms"]
        for symptom, var in self.symptom_vars.items():
            var.set(data.get(symptom, False))

        self.fever_duration_var.set(str(data.get("fever_duration", "")) if data.get("fever_duration") else "")
        self.cough_type_var.set(data.get("cough_type", "") if data.get("cough_type") else "")

    def _load_sample_tests(self, sample_type: str):
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

    def _collect_basic_info(self):
        """Collect basic information from form."""
        try:
            age = InputValidator.validate_age(self.age_var.get())
            gender = InputValidator.validate_gender(self.gender_var.get())
            weight = InputValidator.validate_weight(self.weight_var.get())
            temperature = InputValidator.validate_temperature(self.temp_var.get())
            duration = InputValidator.validate_duration(self.duration_var.get())
            chronic_diseases = self.chronic_var.get()

            self.basic_info = {
                "age": age,
                "gender": gender,
                "weight": weight,
                "temperature": temperature,
                "duration": duration,
                "chronic_diseases": chronic_diseases,
            }
        except ValidationError as e:
            raise ValidationError(f"Basic info validation failed: {e}")

    def _collect_symptoms(self):
        """Collect symptoms from form."""
        self.symptoms = {}
        for symptom, var in self.symptom_vars.items():
            self.symptoms[symptom] = var.get()

        # Additional details
        try:
            fever_duration = InputValidator.validate_age(self.fever_duration_var.get())
            self.symptoms["fever_duration"] = fever_duration
        except ValidationError:
            self.symptoms["fever_duration"] = None

        cough_type = InputValidator.validate_cough_type(self.cough_type_var.get())
        self.symptoms["cough_type"] = cough_type

    def _collect_test_results(self):
        """Collect test results from form."""
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

    def _analyze(self):
        """Perform symptom analysis."""
        if self.is_loading:
            return

        try:
            # Collect all data
            self._collect_basic_info()
            self._collect_symptoms()
            self._collect_test_results()

            user_data = {
                "basic_info": self.basic_info,
                "symptoms": self.symptoms,
                "test_results": self.test_results,
            }

            # Check for emergency
            emergency = SymptomAnalyzer.check_emergency(user_data)
            if emergency.is_emergency:
                self._show_emergency_alert(emergency)
                return

            # Start analysis
            self._start_analysis(user_data)

        except ValidationError as e:
            messagebox.showerror("Validation Error", f"Invalid input: {e}")
        except Exception as e:
            logger.error(f"Analysis setup failed: {e}")
            messagebox.showerror("Error", f"Failed to start analysis: {e}")

    def _show_emergency_alert(self, emergency):
        """Show emergency alert dialog."""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"⚠️ EMERGENCY ALERT: Based on your symptoms, seek immediate medical attention!\n\n")
        self.output_text.insert(tk.END, f"Reasons: {', '.join(emergency.reasons)}\n\n")
        self.output_text.insert(tk.END, "Please call emergency services or go to the nearest hospital.\n\n")
        self.output_text.insert(tk.END, "Analysis skipped due to emergency symptoms.")

        messagebox.showwarning("Emergency Alert",
                             f"Emergency symptoms detected!\n\nReasons: {', '.join(emergency.reasons)}\n\nPlease seek immediate medical attention!")

    def _start_analysis(self, user_data: Dict[str, Any]):
        """Start analysis in background thread."""
        self.is_loading = True
        self.analyze_button.config(state='disabled')
        self.loading_label.config(text="🔄 Analyzing symptoms... Please wait.")
        self.output_text.delete(1.0, tk.END)
        self.root.update()

        # Run analysis in separate thread
        analysis_thread = threading.Thread(target=self._perform_analysis, args=(user_data,))
        analysis_thread.start()

    def _perform_analysis(self, user_data: Dict[str, Any]):
        """Perform analysis in background thread."""
        try:
            analysis = ""
            for chunk in SymptomAnalyzer.analyze_symptoms(user_data):
                analysis += chunk
                # Update UI incrementally
                self.root.after(0, lambda: self._update_streaming_text(analysis))

            # Final update
            self.root.after(0, lambda: self._finalize_analysis(analysis))

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self.root.after(0, lambda: self._show_analysis_error(str(e)))

    def _update_streaming_text(self, text: str):
        """Update streaming text in UI."""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def _finalize_analysis(self, analysis: str):
        """Finalize analysis display."""
        self._stop_loading()
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, analysis)

    def _show_analysis_error(self, error_msg: str):
        """Show analysis error in UI."""
        self._stop_loading()
        messagebox.showerror("Analysis Error", f"Failed to get analysis: {error_msg}")

    def _stop_loading(self):
        """Stop loading state."""
        self.is_loading = False
        self.analyze_button.config(state='normal')
        self.loading_label.config(text="")
        self.root.update()

    def _clear_all(self):
        """Clear all form data and output."""
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

    def _load_sample_data(self) -> Dict[str, Dict]:
        """Load sample data for testing."""
        return {
            "viral_fever": {
                "basic_info": {"age": 25, "gender": "M", "weight": 70.0, "temperature": 38.5, "duration": "3", "chronic_diseases": False},
                "symptoms": {"fever": True, "fatigue": True, "cough": False, "headache": True, "body_pain": True, "nausea": False, "vomiting": False, "diarrhea": False, "rash": False, "sore_throat": True, "shortness_of_breath": False, "chest_pain": False, "confusion": False, "recent_travel": False, "medication": False, "appetite_change": True, "urine_change": False, "weight_loss": False, "night_sweats": False, "exposure": False, "fever_duration": 3, "cough_type": None},
                "test_results": {"WBC": 6500, "Platelets": 180000, "Hemoglobin": 14.0, "Blood_Sugar": 90, "ALT": 25, "Creatinine": 0.8, "Malaria": False, "Dengue": False, "Typhoid": False}
            },
            "dengue": {
                "basic_info": {"age": 30, "gender": "F", "weight": 60.0, "temperature": 39.2, "duration": "5", "chronic_diseases": False},
                "symptoms": {"fever": True, "fatigue": True, "cough": False, "headache": True, "body_pain": True, "nausea": True, "vomiting": False, "diarrhea": False, "rash": True, "sore_throat": False, "shortness_of_breath": False, "chest_pain": False, "confusion": False, "recent_travel": True, "medication": False, "appetite_change": True, "urine_change": False, "weight_loss": False, "night_sweats": False, "exposure": False, "fever_duration": 5, "cough_type": None},
                "test_results": {"WBC": 3000, "Platelets": 80000, "Hemoglobin": 12.5, "Blood_Sugar": 95, "ALT": 45, "Creatinine": 0.9, "Malaria": False, "Dengue": True, "Typhoid": False}
            },
            "hep_a": {
                "basic_info": {"age": 35, "gender": "M", "weight": 75.0, "temperature": 38.0, "duration": "7", "chronic_diseases": False},
                "symptoms": {"fever": True, "fatigue": True, "cough": False, "headache": False, "body_pain": False, "nausea": True, "vomiting": True, "diarrhea": True, "rash": False, "sore_throat": False, "shortness_of_breath": False, "chest_pain": False, "confusion": False, "recent_travel": True, "medication": False, "appetite_change": True, "urine_change": True, "weight_loss": True, "night_sweats": False, "exposure": False, "fever_duration": 7, "cough_type": None},
                "test_results": {"WBC": 5500, "Platelets": 150000, "Hemoglobin": 13.5, "Blood_Sugar": 85, "ALT": 120, "Creatinine": 0.9, "Malaria": False, "Dengue": False, "Typhoid": False}
            },
            "tuberculosis": {
                "basic_info": {"age": 40, "gender": "F", "weight": 55.0, "temperature": 37.8, "duration": "30", "chronic_diseases": False},
                "symptoms": {"fever": True, "fatigue": True, "cough": True, "headache": False, "body_pain": False, "nausea": False, "vomiting": False, "diarrhea": False, "rash": False, "sore_throat": False, "shortness_of_breath": True, "chest_pain": True, "confusion": False, "recent_travel": False, "medication": False, "appetite_change": True, "urine_change": False, "weight_loss": True, "night_sweats": True, "exposure": True, "fever_duration": 30, "cough_type": "productive"},
                "test_results": {"WBC": 8000, "Platelets": 200000, "Hemoglobin": 11.0, "Blood_Sugar": 95, "ALT": 30, "Creatinine": 0.8, "Malaria": False, "Dengue": False, "Typhoid": False}
            },
            "ckd": {
                "basic_info": {"age": 55, "gender": "M", "weight": 85.0, "temperature": 36.8, "duration": "90", "chronic_diseases": True},
                "symptoms": {"fever": False, "fatigue": True, "cough": False, "headache": False, "body_pain": False, "nausea": True, "vomiting": True, "diarrhea": False, "rash": False, "sore_throat": False, "shortness_of_breath": True, "chest_pain": False, "confusion": False, "recent_travel": False, "medication": True, "appetite_change": True, "urine_change": True, "weight_loss": True, "night_sweats": False, "exposure": False, "fever_duration": None, "cough_type": None},
                "test_results": {"WBC": 7000, "Platelets": 180000, "Hemoglobin": 9.5, "Blood_Sugar": 140, "ALT": 35, "Creatinine": 3.2, "Malaria": False, "Dengue": False, "Typhoid": False}
            },
            "diabetes": {
                "basic_info": {"age": 50, "gender": "F", "weight": 90.0, "temperature": 36.5, "duration": "180", "chronic_diseases": True},
                "symptoms": {"fever": False, "fatigue": True, "cough": False, "headache": False, "body_pain": False, "nausea": False, "vomiting": False, "diarrhea": False, "rash": False, "sore_throat": False, "shortness_of_breath": False, "chest_pain": False, "confusion": False, "recent_travel": False, "medication": True, "appetite_change": True, "urine_change": True, "weight_loss": True, "night_sweats": False, "exposure": False, "fever_duration": None, "cough_type": None},
                "test_results": {"WBC": 6500, "Platelets": 200000, "Hemoglobin": 12.0, "Blood_Sugar": 280, "ALT": 40, "Creatinine": 1.1, "Malaria": False, "Dengue": False, "Typhoid": False}
            },
            "emergency": {
                "basic_info": {"age": 45, "gender": "M", "weight": 80.0, "temperature": 40.5, "duration": "2", "chronic_diseases": True},
                "symptoms": {"fever": True, "fatigue": True, "cough": False, "headache": True, "body_pain": True, "nausea": False, "vomiting": False, "diarrhea": False, "rash": False, "sore_throat": False, "shortness_of_breath": True, "chest_pain": True, "confusion": True, "recent_travel": False, "medication": True, "appetite_change": False, "urine_change": False, "weight_loss": False, "night_sweats": False, "exposure": False, "fever_duration": 2, "cough_type": None},
                "test_results": {}
            }
        }


def main():
    """Main GUI entry point."""
    root = tk.Tk()
    app = SymptomCheckerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()