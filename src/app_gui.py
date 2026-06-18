import os
import threading
import subprocess
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.audio_processor import AudioProcessor


class AppGUI(ctk.CTk):
    """
    Clase principal de la interfaz gráfica para el reductor de ruido.
    Proporciona los componentes visuales y maneja los eventos de usuario.
    """

    def __init__(self) -> None:
        super().__init__()

        self.title("Reductor de Ruido con IA")
        self.geometry("650x450")
        self.resizable(False, False)

        self.audio_processor = AudioProcessor()
        self.selected_files: tuple = ()
        self.preview_thread: threading.Thread | None = None
        self.is_previewing = False

        self._build_ui()

    def _build_ui(self) -> None:
        # Layout principal (2 columnas)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ====== Frame Izquierdo (Selección de Archivo) ======
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.title_label = ctk.CTkLabel(
            self.left_frame, text="Limpieza de\nAudio y Video", font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(pady=(30, 20))

        self.file_label = ctk.CTkLabel(
            self.left_frame, text="Ningún archivo seleccionado", text_color="gray", wraplength=250
        )
        self.file_label.pack(pady=(10, 20))

        self.select_btn = ctk.CTkButton(
            self.left_frame, text="Seleccionar Archivo(s)", command=self._select_file
        )
        self.select_btn.pack(pady=10)

        # ====== Frame Derecho (Configuraciones y Preview) ======
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.settings_label = ctk.CTkLabel(
            self.right_frame, text="⚙️ Configuraciones", font=ctk.CTkFont(size=16, weight="bold")
        )
        self.settings_label.pack(pady=(20, 10))

        self.slider_label = ctk.CTkLabel(
            self.right_frame, text="Fuerza del Filtro: 100 dB\n(100 = Limpieza Total)"
        )
        self.slider_label.pack(pady=(5, 5))

        self.atten_slider = ctk.CTkSlider(
            self.right_frame, from_=0, to=100, number_of_steps=100, command=self._on_slider_change
        )
        self.atten_slider.set(100)
        self.atten_slider.pack(pady=(0, 15))

        self.postprocess_var = ctk.BooleanVar(value=True)
        self.postprocess_check = ctk.CTkCheckBox(
            self.right_frame, text="Mejorar Voz (Normalizar y EQ)", variable=self.postprocess_var
        )
        self.postprocess_check.pack(pady=(0, 20))

        self.preview_btn = ctk.CTkButton(
            self.right_frame, text="▶ Vista Previa (1er Archivo)", command=self._toggle_preview, state="disabled", fg_color="#1f538d", hover_color="#14375e"
        )
        self.preview_btn.pack(pady=10)

        # ====== Frame Inferior (Acciones Generales) ======
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        self.process_btn = ctk.CTkButton(
            self.bottom_frame, 
            text="Procesar Selección", 
            command=self._start_processing, 
            state="disabled", 
            fg_color="green", 
            hover_color="darkgreen",
            width=300,
            height=40
        )
        self.process_btn.pack(pady=(5, 10))

        self.progress_bar = ctk.CTkProgressBar(self.bottom_frame, mode="determinate", width=400)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.bottom_frame, text="", text_color="orange")
        self.status_label.pack(pady=5)

    def _on_slider_change(self, value: float) -> None:
        self.slider_label.configure(text=f"Fuerza del Filtro: {int(value)} dB\n(100 = Limpieza Total)")

    def _select_file(self) -> None:
        filetypes = [
            ("Archivos Multimedia", "*.mp4 *.mkv *.mov *.avi *.mp3 *.wav *.flac *.aac *.ogg"),
            ("Todos los archivos", "*.*")
        ]
        file_paths = filedialog.askopenfilenames(title="Selecciona los archivos", filetypes=filetypes)
        
        if file_paths:
            self.selected_files = file_paths
            if len(self.selected_files) == 1:
                file_name = os.path.basename(self.selected_files[0])
                self.file_label.configure(text=f"Archivo:\n{file_name}", text_color="white")
            else:
                self.file_label.configure(text=f"{len(self.selected_files)} archivos seleccionados", text_color="white")
                
            self.process_btn.configure(state="normal")
            self.preview_btn.configure(state="normal")
            self.status_label.configure(text="")

    def _toggle_preview(self) -> None:
        if not self.selected_files:
            return
            
        if self.is_previewing:
            self.audio_processor.stop_preview()
            self._set_preview_state(False)
        else:
            self._set_preview_state(True)
            self.preview_thread = threading.Thread(target=self._run_preview, daemon=True)
            self.preview_thread.start()

    def _set_preview_state(self, is_active: bool) -> None:
        self.is_previewing = is_active
        if is_active:
            self.preview_btn.configure(text="■ Detener Preview", fg_color="#c83232", hover_color="#8c2323")
            self.process_btn.configure(state="disabled")
            self.status_label.configure(text="Reproduciendo vista previa... (Ajusta el slider si lo necesitas)", text_color="cyan")
        else:
            self.preview_btn.configure(text="▶ Vista Previa (1er Archivo)", fg_color="#1f538d", hover_color="#14375e")
            self.process_btn.configure(state="normal")
            self.status_label.configure(text="")

    def _run_preview(self) -> None:
        try:
            val = self.atten_slider.get()
            do_post = self.postprocess_var.get()
            first_file = self.selected_files[0]
            self.audio_processor.preview_audio(first_file, atten_lim_db=val, apply_postprocess=do_post) # type: ignore
        except Exception as e:
            self.status_label.configure(text=f"Error en preview: {str(e)}", text_color="red")
        finally:
            self._set_preview_state(False)

    def _start_processing(self) -> None:
        if not self.selected_files:
            return

        self.select_btn.configure(state="disabled")
        self.process_btn.configure(state="disabled")
        self.preview_btn.configure(state="disabled")
        self.atten_slider.configure(state="disabled")
        self.postprocess_check.configure(state="disabled")
        
        self.status_label.configure(
            text=f"Procesando 0 de {len(self.selected_files)} archivos...", 
            text_color="orange"
        )
        
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(5, 0))

        threading.Thread(target=self._process_task, daemon=True).start()

    def _process_task(self) -> None:
        total = len(self.selected_files)
        val = self.atten_slider.get()
        do_post = self.postprocess_var.get()
        first_output_path = None
        has_error = False

        for i, input_file in enumerate(self.selected_files):
            try:
                self.status_label.configure(text=f"Procesando {i+1} de {total}: {os.path.basename(input_file)}")
                
                name, ext = os.path.splitext(input_file)
                if self.audio_processor.is_video_file(input_file):
                    output_path = f"{name}_limpio{ext}"
                else:
                    output_path = f"{name}_limpio.wav"

                if first_output_path is None:
                    first_output_path = output_path

                self.audio_processor.process_file(input_file, output_path, atten_lim_db=val, apply_postprocess=do_post)
                
                # Actualizar barra de progreso determinada
                progress = (i + 1) / total
                self.progress_bar.set(progress)

            except Exception as e:
                has_error = True
                self._update_gui_after_process(success=False, msg=f"Error en {os.path.basename(input_file)}: {str(e)}")
                return # Salir del bucle si hay error

        if not has_error:
            msg = f"¡Completado!\nSe procesaron {total} archivos exitosamente."
            self._update_gui_after_process(success=True, msg=msg)
            
            if first_output_path:
                try:
                    subprocess.Popen(f'explorer /select,"{os.path.normpath(first_output_path)}"')
                except Exception:
                    pass

    def _update_gui_after_process(self, success: bool, msg: str) -> None:
        self.progress_bar.pack_forget()
        
        self.select_btn.configure(state="normal")
        self.process_btn.configure(state="normal")
        self.preview_btn.configure(state="normal")
        self.atten_slider.configure(state="normal")
        self.postprocess_check.configure(state="normal")
        
        if success:
            self.status_label.configure(text="Proceso Finalizado", text_color="green")
            messagebox.showinfo("Proceso Terminado", msg)
        else:
            self.status_label.configure(text="Proceso interrumpido.", text_color="red")
            messagebox.showerror("Error de Procesamiento", msg)
