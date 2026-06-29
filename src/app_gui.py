import os
import threading
import subprocess
import torch
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.audio_processor import AudioProcessor

# Modo y Tema por defecto
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AppGUI(ctk.CTk):
    """
    Interfaz gráfica re-imaginada para el reductor de ruido.
    Estilo Sidebar con pestañas modernas.
    """

    def __init__(self) -> None:
        super().__init__()

        self.title("AI Multimedia Enhancer")
        self.geometry("850x500")
        self.resizable(False, False)

        self.audio_processor = AudioProcessor()
        self.selected_files: tuple = ()
        self.preview_thread: threading.Thread | None = None
        self.is_previewing = False
        self.cancel_requested = False

        self._build_ui()

    def _build_ui(self) -> None:
        # Layout principal 1x2 (Sidebar y Main)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # =========================================================
        # ====== BARRA LATERAL (SIDEBAR) ==========================
        # =========================================================
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # Spacer

        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, text="✨ AI Enhancer", font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 10))

        self.file_label = ctk.CTkLabel(
            self.sidebar_frame, text="Ningún archivo\nseleccionado", text_color="gray", wraplength=200
        )
        self.file_label.grid(row=1, column=0, padx=20, pady=(10, 20))

        self.select_btn = ctk.CTkButton(
            self.sidebar_frame, text="Seleccionar Archivos", command=self._select_file, height=40, corner_radius=20
        )
        self.select_btn.grid(row=2, column=0, padx=20, pady=10)
        
        self.preview_btn = ctk.CTkButton(
            self.sidebar_frame, text="▶ Vista Previa Audio", command=self._toggle_preview, state="disabled", 
            fg_color="#1f538d", hover_color="#14375e", height=40, corner_radius=20
        )
        self.preview_btn.grid(row=3, column=0, padx=20, pady=10)

        self.status_label = ctk.CTkLabel(self.sidebar_frame, text="", text_color="orange", wraplength=200)
        self.status_label.grid(row=5, column=0, padx=20, pady=(10, 5))

        self.process_btn = ctk.CTkButton(
            self.sidebar_frame, text="PROCESAR", command=self._start_processing, state="disabled", 
            fg_color="#1aa55e", hover_color="#147c46", height=45, font=ctk.CTkFont(size=15, weight="bold"), corner_radius=20
        )
        self.process_btn.grid(row=6, column=0, padx=20, pady=(10, 20))

        # =========================================================
        # ====== ÁREA PRINCIPAL (2 COLUMNAS LADO A LADO) ============
        # =========================================================
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1, minsize=275)
        self.main_frame.grid_columnconfigure(1, weight=1, minsize=275)

        # Columna Izquierda: Ajustes de Audio
        self.audio_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        self.audio_frame.grid(row=0, column=0, padx=(0, 7), pady=(0, 10), sticky="nsew")
        
        # Columna Derecha: Ajustes de Video
        self.video_frame = ctk.CTkFrame(self.main_frame, corner_radius=15)
        self.video_frame.grid(row=0, column=1, padx=(7, 0), pady=(0, 10), sticky="nsew")

        self._build_audio_section()
        self._build_video_section()
        
        # Barra de progreso inferior
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, mode="determinate", height=10, corner_radius=5)
        self.progress_bar.set(0)

    def _build_audio_section(self) -> None:
        self.audio_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.audio_frame, text="🎧 Ajustes de Audio", font=ctk.CTkFont(size=17, weight="bold")).pack(pady=(15, 10))
        
        # Fuerza reducción de ruido
        self.slider_label = ctk.CTkLabel(self.audio_frame, text="Fuerza del Filtro: 100 dB (Limpieza Total)", font=ctk.CTkFont(size=12))
        self.slider_label.pack(pady=(5, 2))
        self.atten_slider = ctk.CTkSlider(self.audio_frame, from_=0, to=100, number_of_steps=100, command=self._on_slider_change, height=15)
        self.atten_slider.set(100)
        self.atten_slider.pack(pady=(0, 10), padx=20, fill="x")

        # Ganancia de voz adicional
        self.gain_label = ctk.CTkLabel(self.audio_frame, text="Ganancia de Voz: +0.0 dB (Original)", font=ctk.CTkFont(size=12))
        self.gain_label.pack(pady=(5, 2))
        self.audio_gain_slider = ctk.CTkSlider(self.audio_frame, from_=0, to=10, number_of_steps=20, command=self._on_gain_change, height=15)
        self.audio_gain_slider.set(0)
        self.audio_gain_slider.pack(pady=(0, 10), padx=20, fill="x")

        # Checkbox Mejorar voz
        self.postprocess_var = ctk.BooleanVar(value=True)
        self.postprocess_check = ctk.CTkCheckBox(self.audio_frame, text="Mejorar Voz (EQ + Normalizar)", variable=self.postprocess_var, font=ctk.CTkFont(size=12), corner_radius=5)
        self.postprocess_check.pack(pady=5, anchor="w", padx=25)

        # Checkbox Post-Filtro DeepFilterNet
        self.post_filter_var = ctk.BooleanVar(value=False)
        self.post_filter_check = ctk.CTkCheckBox(self.audio_frame, text="Reducción Ultra (Post-Filtro)", variable=self.post_filter_var, font=ctk.CTkFont(size=12), corner_radius=5)
        self.post_filter_check.pack(pady=5, anchor="w", padx=25)
        
        # Bitrate de salida
        ctk.CTkLabel(self.audio_frame, text="Bitrate de Audio:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(12, 2))
        self.audio_bitrate_var = ctk.StringVar(value="192k")
        self.audio_bitrate_menu = ctk.CTkOptionMenu(
            self.audio_frame, variable=self.audio_bitrate_var,
            values=["128k (Básico)", "192k (Normal)", "320k (Estudio)"],
            corner_radius=10, height=28
        )
        self.audio_bitrate_menu.pack(pady=(0, 10), padx=20, fill="x")

        # Formato de salida de audio
        ctk.CTkLabel(self.audio_frame, text="Formato de Audio:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(5, 2))
        self.audio_format_var = ctk.StringVar(value="WAV")
        self.audio_format_menu = ctk.CTkOptionMenu(
            self.audio_frame, variable=self.audio_format_var,
            values=["WAV (Sin pérdida)", "MP3 (Comprimido)", "FLAC (Fidelidad)"],
            corner_radius=10, height=28
        )
        self.audio_format_menu.pack(pady=(0, 15), padx=20, fill="x")

    def _build_video_section(self) -> None:
        self.video_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.video_frame, text="🎬 Ajustes de Video (IA)", font=ctk.CTkFont(size=17, weight="bold")).pack(pady=(15, 10))

        # Checkbox activar GPU
        cuda_available = torch.cuda.is_available()
        text_gpu = "Activar Mejora por GPU (RealESRGAN)" if cuda_available else "Activar Mejora por CPU (Muy Lento)"
        self.enhance_video_var = ctk.BooleanVar(value=False)
        self.enhance_video_check = ctk.CTkCheckBox(
            self.video_frame, text=text_gpu, 
            variable=self.enhance_video_var, command=self._toggle_video_options, font=ctk.CTkFont(size=12), corner_radius=5
        )
        self.enhance_video_check.pack(pady=8)

        # Resolución
        ctk.CTkLabel(self.video_frame, text="Resolución Deseada:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(8, 2))
        self.video_resolution_var = ctk.StringVar(value="1080p (Super-Sampling)")
        self.video_resolution_menu = ctk.CTkOptionMenu(
            self.video_frame, variable=self.video_resolution_var,
            values=["1080p (Super-Sampling)", "x2 (Doble Resolución)", "Ambas (Guardar 1080p y x2)"],
            state="disabled", corner_radius=10, height=28
        )
        self.video_resolution_menu.pack(pady=(0, 8), padx=20, fill="x")

        # Calidad de Video (CRF)
        ctk.CTkLabel(self.video_frame, text="Calidad de Video:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(5, 2))
        self.video_crf_var = ctk.StringVar(value="Alta (CRF 18)")
        self.video_crf_menu = ctk.CTkOptionMenu(
            self.video_frame, variable=self.video_crf_var,
            values=["Máxima (CRF 14)", "Alta (CRF 18)", "Balanceada (CRF 23)"],
            state="disabled", corner_radius=10, height=28
        )
        self.video_crf_menu.pack(pady=(0, 8), padx=20, fill="x")

        # Fotogramas por Segundo (FPS)
        ctk.CTkLabel(self.video_frame, text="Fotogramas por Segundo (FPS):", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(5, 2))
        self.video_fps_var = ctk.StringVar(value="Original")
        self.video_fps_menu = ctk.CTkOptionMenu(
            self.video_frame, variable=self.video_fps_var,
            values=["Original", "30 FPS", "60 FPS (Fluido)"],
            state="disabled", corner_radius=10, height=28
        )
        self.video_fps_menu.pack(pady=(0, 8), padx=20, fill="x")

        # Preset
        ctk.CTkLabel(self.video_frame, text="Perfil de Compresión:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(5, 2))
        self.video_preset_var = ctk.StringVar(value="fast")
        self.video_preset_menu = ctk.CTkOptionMenu(
            self.video_frame, variable=self.video_preset_var,
            values=["ultrafast (Más rápido)", "fast (Balanceado)", "slow (Mejor, lento)"],
            state="disabled", corner_radius=10, height=28
        )
        self.video_preset_menu.pack(pady=(0, 8), padx=20, fill="x")

        # Formato de salida de video
        ctk.CTkLabel(self.video_frame, text="Formato de Video:", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(5, 2))
        self.video_format_var = ctk.StringVar(value="MP4")
        self.video_format_menu = ctk.CTkOptionMenu(
            self.video_frame, variable=self.video_format_var,
            values=["MP4 (Estándar)", "MKV (Matroska)"],
            state="disabled", corner_radius=10, height=28
        )
        self.video_format_menu.pack(pady=(0, 15), padx=20, fill="x")

    def _on_slider_change(self, value: float) -> None:
        self.slider_label.configure(text=f"Fuerza del Filtro: {int(value)} dB (Limpieza Total)")

    def _on_gain_change(self, value: float) -> None:
        self.gain_label.configure(text=f"Ganancia de Voz: +{value:.1f} dB")

    def _toggle_video_options(self) -> None:
        state = "normal" if self.enhance_video_var.get() else "disabled"
        self.video_resolution_menu.configure(state=state)
        self.video_crf_menu.configure(state=state)
        self.video_preset_menu.configure(state=state)
        self.video_format_menu.configure(state=state)
        self.video_fps_menu.configure(state=state)

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
                self.file_label.configure(text=f"Archivo:\n{file_name[:25]}{'...' if len(file_name) > 25 else ''}", text_color="white")
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
            self.status_label.configure(text="Reproduciendo vista previa...", text_color="#1aa55e")
        else:
            self.preview_btn.configure(text="▶ Vista Previa Audio", fg_color="#1f538d", hover_color="#14375e")
            self.process_btn.configure(state="normal")
            self.status_label.configure(text="")

    def _run_preview(self) -> None:
        try:
            val = self.atten_slider.get()
            do_post = self.postprocess_var.get()
            post_filt = self.post_filter_var.get()
            gain_db = self.audio_gain_slider.get()
            first_file = self.selected_files[0]
            self.audio_processor.preview_audio(
                first_file, 
                atten_lim_db=val, 
                apply_postprocess=do_post, 
                post_filter=post_filt, 
                audio_gain=gain_db
            )
        except Exception as e:
            self.after(0, lambda err=str(e): self.status_label.configure(text=f"Error en preview: {err}", text_color="red"))
        finally:
            self.after(0, lambda: self._set_preview_state(False))

    def _request_cancel(self) -> None:
        self.cancel_requested = True
        self.status_label.configure(text="Cancelando proceso...", text_color="red")
        self.process_btn.configure(state="disabled")

    def _start_processing(self) -> None:
        if not self.selected_files:
            return

        self.select_btn.configure(state="disabled")
        self.preview_btn.configure(state="disabled")
        self.atten_slider.configure(state="disabled")
        self.audio_gain_slider.configure(state="disabled")
        self.postprocess_check.configure(state="disabled")
        self.post_filter_check.configure(state="disabled")
        self.enhance_video_check.configure(state="disabled")
        self.video_resolution_menu.configure(state="disabled")
        self.video_crf_menu.configure(state="disabled")
        self.video_preset_menu.configure(state="disabled")
        self.video_format_menu.configure(state="disabled")
        self.video_fps_menu.configure(state="disabled")
        self.audio_bitrate_menu.configure(state="disabled")
        self.audio_format_menu.configure(state="disabled")
        
        # Configurar botón como Cancelar
        self.cancel_requested = False
        self.process_btn.configure(
            text="CANCELAR", 
            fg_color="#c83232", 
            hover_color="#8c2323", 
            command=self._request_cancel,
            state="normal"
        )
        
        self.status_label.configure(
            text=f"Procesando 0 de {len(self.selected_files)} archivos...", 
            text_color="orange"
        )
        
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        threading.Thread(target=self._process_task, daemon=True).start()

    def _process_task(self) -> None:
        total = len(self.selected_files)
        val = self.atten_slider.get()
        do_post = self.postprocess_var.get()
        post_filt = self.post_filter_var.get()
        gain_db = self.audio_gain_slider.get()
        enhance_vid = self.enhance_video_var.get()
        vid_res = self.video_resolution_var.get()
        
        raw_bitrate = self.audio_bitrate_var.get().split()[0]
        raw_preset = self.video_preset_var.get().split()[0]
        raw_fps = self.video_fps_var.get()
        
        crf_map = {
            "Máxima (CRF 14)": "14",
            "Alta (CRF 18)": "18",
            "Balanceada (CRF 23)": "23"
        }
        raw_crf = crf_map.get(self.video_crf_var.get(), "18")
        
        # Formatos seleccionados
        audio_fmt = self.audio_format_var.get().split()[0].lower()
        video_fmt = self.video_format_var.get().split()[0].lower()
        
        first_output_path = None
        has_error = False
        output_path = None
        cancel_fn = lambda: self.cancel_requested

        for i, input_file in enumerate(self.selected_files):
            try:
                if self.cancel_requested:
                    raise KeyboardInterrupt("Proceso cancelado por el usuario")

                self.after(0, lambda lbl=f"Procesando {i+1} de {total}: {os.path.basename(input_file)[:15]}...": self.status_label.configure(text=lbl))
                
                name, ext = os.path.splitext(input_file)
                if self.audio_processor.is_video_file(input_file):
                    output_path = f"{name}_limpio.{video_fmt}"
                else:
                    output_path = f"{name}_limpio.{audio_fmt}"

                if first_output_path is None:
                    first_output_path = output_path

                # Callback para reportar progreso acumulado global en la UI
                def make_progress_callback(file_idx):
                    def progress_cb(current, total_val):
                        file_progress = current / total_val if total_val > 0 else 0.0
                        global_progress = (file_idx + file_progress) / total
                        self.after(0, lambda: self.progress_bar.set(global_progress))
                    return progress_cb

                self.audio_processor.process_file(
                    input_file, 
                    output_path, 
                    atten_lim_db=val, 
                    apply_postprocess=do_post,
                    enhance_video=enhance_vid,
                    video_resolution=vid_res,
                    audio_bitrate=raw_bitrate,
                    video_preset=raw_preset,
                    post_filter=post_filt,
                    audio_gain=gain_db,
                    audio_format=audio_fmt,
                    video_crf=raw_crf,
                    video_format=video_fmt,
                    progress_callback=make_progress_callback(i),
                    video_fps=raw_fps,
                    cancel_check=cancel_fn
                )

                # Reportar 100% de este archivo al finalizar
                self.after(0, lambda idx=i: self.progress_bar.set((idx + 1) / total))

            except KeyboardInterrupt:
                has_error = True
                if output_path:
                    base_clean, ext_clean = os.path.splitext(output_path)
                    for path_to_clean in [output_path, f"{base_clean}_1080p{ext_clean}", f"{base_clean}_x2{ext_clean}"]:
                        if os.path.exists(path_to_clean):
                            try: os.remove(path_to_clean)
                            except Exception: pass
                self.after(0, lambda: self._update_gui_after_process(success=False, msg="Procesamiento cancelado por el usuario."))
                return

            except Exception as e:
                has_error = True
                self.after(0, lambda m=f"Error en {os.path.basename(input_file)}: {str(e)}": self._update_gui_after_process(success=False, msg=m))
                return 

        if not has_error:
            msg = f"¡Completado!\nSe procesaron {total} archivos exitosamente."
            self.after(0, lambda m=msg: self._update_gui_after_process(success=True, msg=m))
            
            if first_output_path:
                try:
                    target_path = first_output_path
                    if not os.path.exists(target_path):
                        # Caso especial: opción "Ambas"
                        base, ext = os.path.splitext(first_output_path)
                        fallback_path = f"{base}_1080p{ext}"
                        if os.path.exists(fallback_path):
                            target_path = fallback_path
                        else:
                            fallback_path = f"{base}_x2{ext}"
                            if os.path.exists(fallback_path):
                                target_path = fallback_path
                    
                    if os.path.exists(target_path):
                        subprocess.Popen(["explorer", f"/select,{os.path.normpath(target_path)}"])
                    else:
                        folder = os.path.dirname(first_output_path)
                        if os.path.exists(folder):
                            subprocess.Popen(["explorer", os.path.normpath(folder)])
                except Exception:
                    pass

    def _update_gui_after_process(self, success: bool, msg: str) -> None:
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.grid_forget()
        
        self.select_btn.configure(state="normal")
        self.preview_btn.configure(state="normal")
        self.atten_slider.configure(state="normal")
        self.audio_gain_slider.configure(state="normal")
        self.postprocess_check.configure(state="normal")
        self.post_filter_check.configure(state="normal")
        self.enhance_video_check.configure(state="normal")
        self.audio_bitrate_menu.configure(state="normal")
        self.audio_format_menu.configure(state="normal")
        self._toggle_video_options()
        
        # Restaurar botón de procesar
        self.process_btn.configure(
            text="PROCESAR", 
            fg_color="#1aa55e", 
            hover_color="#147c46", 
            command=self._start_processing,
            state="normal" if len(self.selected_files) > 0 else "disabled"
        )
        
        if success:
            self.status_label.configure(text="Proceso Finalizado", text_color="green")
            messagebox.showinfo("Proceso Terminado", msg)
        else:
            self.status_label.configure(text="Proceso interrumpido.", text_color="red")
            messagebox.showerror("Error de Procesamiento", msg)
