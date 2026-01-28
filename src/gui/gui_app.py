"""
Interfaz gráfica interactiva con Tkinter para el proyecto de transcripción de audio.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys

# Agregar ruta para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from audio import load_audio, record_audio
from transcription import transcribe_audio
from output import copy_to_clipboard, save_to_txt
from audio.recorder import AudioRecorder


class AudioTranscriptionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎙️ Automatización de Audio - Transcripción")
        self.root.geometry("625x753")
        self.root.resizable(False, False)
        
        # Variables de control
        self.is_recording = False
        self.recording_duration = tk.IntVar(value=30)
        self.transcription_text = ""
        self.audio_recorder = None
        self.recording_thread = None
        
        # Configurar estilos
        self.setup_styles()
        
        # Crear la interfaz
        self.create_widgets()
        
    def setup_styles(self):
        """Configurar estilos de la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores personalizados
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Heading.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Info.TLabel', font=('Helvetica', 10))
        
    def create_widgets(self):
        """Crear los widgets de la interfaz."""
        # Marco principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="🎙️ AUTOMATIZACIÓN DE AUDIO", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').grid(row=1, column=0, columnspan=2, sticky='ew', pady=5)
        
        # ===== SECCIÓN 1: TRANSCRIBIR ARCHIVO =====
        file_frame = ttk.LabelFrame(main_frame, text="📁 Opción 1: Transcribir Archivo", padding="10")
        file_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Label(file_frame, text="Selecciona un archivo de audio:", style='Info.TLabel').grid(row=0, column=0, sticky='w')
        
        self.file_path_var = tk.StringVar(value="Ningún archivo seleccionado")
        file_path_label = ttk.Label(file_frame, textvariable=self.file_path_var, foreground="gray")
        file_path_label.grid(row=1, column=0, sticky='w', padx=(20, 0))
        
        ttk.Button(file_frame, text="Seleccionar archivo", command=self.select_file).grid(row=2, column=0, sticky='ew', pady=(5, 0))
        ttk.Button(file_frame, text="Transcribir archivo", command=self.transcribe_file).grid(row=3, column=0, sticky='ew', pady=5)
        
        # ===== SECCIÓN 2: GRABAR Y TRANSCRIBIR =====
        record_frame = ttk.LabelFrame(main_frame, text="🎤 Opción 2: Grabar y Transcribir", padding="10")
        record_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Label(record_frame, text="Modo de grabación:", style='Info.TLabel').grid(row=0, column=0, sticky='w')
        
        # Opciones de grabación
        mode_frame = ttk.Frame(record_frame)
        mode_frame.grid(row=1, column=0, sticky='ew', pady=(5, 10))
        
        self.record_mode = tk.StringVar(value="duration")
        ttk.Radiobutton(mode_frame, text="Duración fija (segundos):", variable=self.record_mode, value="duration", command=self._update_record_mode).pack(side='left')
        ttk.Radiobutton(mode_frame, text="Control manual (START/STOP)", variable=self.record_mode, value="manual", command=self._update_record_mode).pack(side='left', padx=20)
        
        # Frame para duración fija
        self.duration_frame = ttk.Frame(record_frame)
        self.duration_frame.grid(row=2, column=0, sticky='w', pady=(5, 0))
        
        spinbox_frame = ttk.Frame(self.duration_frame)
        spinbox_frame.pack(side='left')
        
        ttk.Spinbox(spinbox_frame, from_=5, to=300, textvariable=self.recording_duration, width=5).pack(side='left')
        ttk.Label(spinbox_frame, text="segundos", style='Info.TLabel').pack(side='left', padx=5)
        
        # Botones para duración fija
        self.duration_button = ttk.Button(self.duration_frame, text="Grabar", command=self.start_recording_duration)
        self.duration_button.pack(side='left', padx=10)
        
        # Frame para control manual
        self.manual_frame = ttk.Frame(record_frame)
        self.manual_frame.grid(row=2, column=0, sticky='ew', pady=(5, 0))
        
        self.start_button = ttk.Button(self.manual_frame, text="🔴 Iniciar Grabación", command=self.start_recording_manual, style='Accent.TButton')
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(self.manual_frame, text="⏹️ Detener Grabación", command=self.stop_recording_manual, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        # Etiqueta de estado de grabación
        self.recording_status_var = tk.StringVar(value="")
        ttk.Label(record_frame, textvariable=self.recording_status_var, foreground="blue").grid(row=3, column=0, sticky='w', padx=(20, 0))
        
        # Ocultar frame manual por defecto
        self.manual_frame.grid_remove()
        
        # ===== SECCIÓN 3: RESULTADO DE TRANSCRIPCIÓN =====
        result_frame = ttk.LabelFrame(main_frame, text="📝 Resultado de Transcripción", padding="10")
        result_frame.grid(row=4, column=0, columnspan=2, sticky='nsew', pady=10)
        
        # Texto con scroll
        self.result_text = scrolledtext.ScrolledText(result_frame, height=10, width=70, wrap=tk.WORD)
        self.result_text.grid(row=0, column=0, columnspan=2, sticky='nsew', pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # Botones para el resultado
        button_frame = ttk.Frame(result_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky='ew')
        
        ttk.Button(button_frame, text="📋 Copiar al portapapeles", command=self.copy_to_clipboard).pack(side='left', padx=5)
        ttk.Button(button_frame, text="💾 Guardar como archivo", command=self.save_to_file).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🗑️ Limpiar", command=self.clear_text).pack(side='left', padx=5)
        
        # ===== SECCIÓN 4: BOTONES GENERALES =====
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Button(footer_frame, text="ℹ️ Acerca de", command=self.show_about).pack(side='left', padx=5)
        ttk.Button(footer_frame, text="❌ Salir", command=self.on_closing).pack(side='right', padx=5)
        
        # Configurar peso de filas para responsividad
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Manejar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def select_file(self):
        """Seleccionar un archivo de audio."""
        file_types = [
            ("Archivos de audio", "*.wav *.mp3 *.m4a *.flac *.ogg *.mp4"),
            ("Todos los archivos", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="Selecciona un archivo de audio",
            filetypes=file_types
        )
        
        if file_path:
            self.file_path_var.set(os.path.basename(file_path))
            self.selected_file = file_path
    
    def transcribe_file(self):
        """Transcribir un archivo de audio seleccionado."""
        if not hasattr(self, 'selected_file'):
            messagebox.showwarning("Advertencia", "Por favor, selecciona un archivo primero.")
            return
        
        if not os.path.isfile(self.selected_file):
            messagebox.showerror("Error", "El archivo no existe.")
            return
        
        # Ejecutar en un hilo separado para no bloquear la interfaz
        thread = threading.Thread(target=self._transcribe_file_thread, daemon=True)
        thread.start()
    
    def _transcribe_file_thread(self):
        """Hilo para transcribir archivo sin bloquear la GUI."""
        try:
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            
            # Verificar si es MP4
            if self.selected_file.lower().endswith('.mp4'):
                self.result_text.insert(tk.END, "⏳ Detectado archivo MP4, convirtiendo a WAV...\n")
            else:
                self.result_text.insert(tk.END, "⏳ Cargando archivo de audio...\n")
            
            self.result_text.update()
            
            # Cargar audio (esto convertirá MP4 si es necesario)
            audio_preparado = load_audio(self.selected_file)
            
            self.result_text.insert(tk.END, "⏳ Transcribiendo...\n")
            self.result_text.update()
            
            # Transcribir
            self.transcription_text = transcribe_audio(audio_preparado)
            
            if self.transcription_text:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, self.transcription_text)
                messagebox.showinfo("Éxito", "✅ Transcripción completada")
            else:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "❌ No se pudo transcribir el archivo. Verifica que contenga audio válido.")
                messagebox.showerror("Error", "❌ No se pudo obtener transcripción.")
                
        except Exception as e:
            error_msg = f"❌ Error durante la transcripción:\n{str(e)}"
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, error_msg)
            messagebox.showerror("Error", error_msg)
            print(f"Error en transcripción: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.result_text.config(state='normal')
    
    def start_recording(self):
        """Iniciar grabación de audio."""
        duration = self.recording_duration.get()
        
        if duration < 5 or duration > 300:
            messagebox.showwarning("Advertencia", "La duración debe estar entre 5 y 300 segundos.")
            return
        
        # Ejecutar en un hilo separado
        thread = threading.Thread(target=self._recording_thread, args=(duration,), daemon=True)
        thread.start()
    
    def _recording_thread(self, duration):
        """Hilo para grabar sin bloquear la GUI."""
        try:
            self.is_recording = True
            self.recording_status_var.set(f"⏹️ Grabando... ({duration}s)")
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"⏹️ Grabando {duration} segundos de audio...\n")
            self.result_text.update()
            
            # Grabar
            audio_grabado = record_audio(duration=duration)
            
            if not audio_grabado:
                messagebox.showerror("Error", "❌ Error durante la grabación.")
                self.recording_status_var.set("")
                self.duration_button.config(state='normal')
                return
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "⏳ Transcribiendo audio grabado...\n")
            self.result_text.update()
            
            # Transcribir
            try:
                self.transcription_text = transcribe_audio(audio_grabado)
                
                if self.transcription_text:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, self.transcription_text)
                    messagebox.showinfo("Éxito", "✅ Grabación y transcripción completadas")
                else:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, "❌ No se pudo transcribir el audio grabado. Asegúrate de haber hablado claramente.")
                    messagebox.showerror("Error", "❌ No se pudo obtener transcripción del audio grabado.")
            except Exception as trans_error:
                error_msg = f"❌ Error al transcribir:\n{str(trans_error)}"
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, error_msg)
                messagebox.showerror("Error de Transcripción", error_msg)
                print(f"Error en transcripción: {trans_error}")
                import traceback
                traceback.print_exc()
            
            self.recording_status_var.set("")
            
        except Exception as e:
            error_msg = f"❌ Error durante la grabación:\n{str(e)}"
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, error_msg)
            messagebox.showerror("Error", error_msg)
            print(f"Error en grabación: {e}")
            import traceback
            traceback.print_exc()
            self.recording_status_var.set("")
        finally:
            self.is_recording = False
            self.result_text.config(state='normal')
            self.duration_button.config(state='normal')
    
    def copy_to_clipboard(self):
        """Copiar el texto transcrito al portapapeles."""
        text = self.result_text.get(1.0, tk.END).strip()
        
        if not text:
            messagebox.showwarning("Advertencia", "No hay texto para copiar.")
            return
        
        try:
            copy_to_clipboard(text)
            messagebox.showinfo("Éxito", "✅ Texto copiado al portapapeles")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al copiar: {str(e)}")
    
    def save_to_file(self):
        """Guardar el texto transcrito en un archivo."""
        text = self.result_text.get(1.0, tk.END).strip()
        
        if not text:
            messagebox.showwarning("Advertencia", "No hay texto para guardar.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                save_to_txt(text, file_path)
                messagebox.showinfo("Éxito", f"✅ Archivo guardado en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"❌ Error al guardar: {str(e)}")
    
    def clear_text(self):
        """Limpiar el área de texto."""
        self.result_text.delete(1.0, tk.END)
        self.transcription_text = ""
    
    def show_about(self):
        """Mostrar información acerca de la aplicación."""
        about_text = """
🎙️ Automatización de Audio - Transcripción

Versión: 2.0
Descripción: Aplicación para transcribir archivos de audio
o grabar y transcribir en tiempo real usando Whisper AI.

Funcionalidades:
• Transcribir archivos de audio (.wav, .mp3, .m4a, .flac, .ogg)
• Grabar audio con duración fija
• Grabar audio con control manual (START/STOP)
• Copiar transcripciones al portapapeles
• Guardar transcripciones en archivos .txt

Tecnologías:
• OpenAI Whisper (transcripción)
• Tkinter (interfaz gráfica)
• SoundDevice (grabación)
• SoundFile (procesamiento de audio)
        """
        messagebox.showinfo("Acerca de", about_text)
    
    def _update_record_mode(self):
        """Actualizar visibilidad de frames según el modo seleccionado."""
        if self.record_mode.get() == "duration":
            self.duration_frame.grid()
            self.manual_frame.grid_remove()
        else:
            self.duration_frame.grid_remove()
            self.manual_frame.grid()
    
    def start_recording_duration(self):
        """Iniciar grabación de audio con duración fija."""
        duration = self.recording_duration.get()
        
        if duration < 5 or duration > 300:
            messagebox.showwarning("Advertencia", "La duración debe estar entre 5 y 300 segundos.")
            return
        
        self.duration_button.config(state='disabled')
        
        # Ejecutar en un hilo separado
        thread = threading.Thread(target=self._recording_thread, args=(duration,), daemon=True)
        thread.start()
    
    def _recording_thread(self, duration):
        """Hilo para grabar sin bloquear la GUI."""
        try:
            self.is_recording = True
            self.recording_status_var.set(f"⏹️ Grabando... ({duration}s)")
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"⏹️ Grabando {duration} segundos de audio...\n")
            self.result_text.update()
            
            # Grabar
            audio_grabado = record_audio(duration=duration)
            
            if not audio_grabado:
                messagebox.showerror("Error", "❌ Error durante la grabación.")
                self.recording_status_var.set("")
                self.duration_button.config(state='normal')
                return
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "⏳ Transcribiendo audio grabado...\n")
            self.result_text.update()
            
            # Transcribir
            try:
                self.transcription_text = transcribe_audio(audio_grabado)
                
                if self.transcription_text:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, self.transcription_text)
                    messagebox.showinfo("Éxito", "✅ Grabación y transcripción completadas")
                else:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, "❌ No se pudo transcribir el audio grabado. Asegúrate de haber hablado claramente.")
                    messagebox.showerror("Error", "❌ No se pudo obtener transcripción del audio grabado.")
            except Exception as trans_error:
                error_msg = f"❌ Error al transcribir:\n{str(trans_error)}"
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, error_msg)
                messagebox.showerror("Error de Transcripción", error_msg)
                print(f"Error en transcripción: {trans_error}")
                import traceback
                traceback.print_exc()
            
            self.recording_status_var.set("")
            
        except Exception as e:
            error_msg = f"❌ Error durante la grabación:\n{str(e)}"
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, error_msg)
            messagebox.showerror("Error", error_msg)
            print(f"Error en grabación: {e}")
            import traceback
            traceback.print_exc()
            self.recording_status_var.set("")
        finally:
            self.is_recording = False
            self.result_text.config(state='normal')
            self.duration_button.config(state='normal')
    
    def start_recording_manual(self):
        """Iniciar grabación manual (sin límite de tiempo)."""
        self.audio_recorder = AudioRecorder()
        self.audio_recorder.start_recording()
        
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.recording_status_var.set("🔴 Grabando... (presiona DETENER para finalizar)")
        
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "🔴 Grabando audio en tiempo real...\nPresiona 'Detener Grabación' cuando termines.\n")
        self.result_text.update()
    
    def stop_recording_manual(self):
        """Detener grabación manual y transcribir."""
        if not self.audio_recorder:
            messagebox.showerror("Error", "No hay grabación activa.")
            return
        
        self.stop_button.config(state='disabled')
        self.start_button.config(state='normal')
        self.recording_status_var.set("⏳ Procesando audio grabado...")
        
        # Detener grabación
        audio_grabado = self.audio_recorder.stop_recording()
        self.audio_recorder = None
        
        if not audio_grabado:
            messagebox.showerror("Error", "❌ Error durante la grabación. No se capturó audio.")
            self.recording_status_var.set("")
            return
        
        # Transcribir en un hilo separado
        thread = threading.Thread(target=self._transcribe_manual_recording, args=(audio_grabado,), daemon=True)
        thread.start()
    
    def _transcribe_manual_recording(self, audio_path):
        """Transcribir el audio grabado manualmente."""
        try:
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "⏳ Transcribiendo audio grabado...\n")
            self.result_text.update()
            
            # Transcribir
            try:
                self.transcription_text = transcribe_audio(audio_path)
                
                if self.transcription_text:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, self.transcription_text)
                    messagebox.showinfo("Éxito", "✅ Grabación y transcripción completadas")
                else:
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, "❌ No se pudo transcribir el audio grabado. Asegúrate de haber hablado claramente.")
                    messagebox.showerror("Error", "❌ No se pudo obtener transcripción del audio grabado.")
            except Exception as trans_error:
                error_msg = f"❌ Error al transcribir:\n{str(trans_error)}"
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, error_msg)
                messagebox.showerror("Error de Transcripción", error_msg)
                print(f"Error en transcripción: {trans_error}")
                import traceback
                traceback.print_exc()
            
            self.recording_status_var.set("")
            
        except Exception as e:
            error_msg = f"❌ Error durante la grabación:\n{str(e)}"
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, error_msg)
            messagebox.showerror("Error", error_msg)
            print(f"Error en grabación: {e}")
            import traceback
            traceback.print_exc()
            self.recording_status_var.set("")
        finally:
            self.result_text.config(state='normal')
    
    def start_recording(self):
        """Iniciar grabación de audio (DEPRECATED - se mantiene para compatibilidad)."""
        duration = self.recording_duration.get()
        
        if duration < 5 or duration > 300:
            messagebox.showwarning("Advertencia", "La duración debe estar entre 5 y 300 segundos.")
            return
        
        # Ejecutar en un hilo separado
        thread = threading.Thread(target=self._recording_thread, args=(duration,), daemon=True)
        thread.start()
    
    def on_closing(self):
        """Manejar el cierre de la aplicación."""
        # Detener cualquier grabación en curso
        if hasattr(self, 'audio_recorder') and self.audio_recorder:
            if self.audio_recorder.is_recording:
                self.audio_recorder.is_recording = False
                if self.audio_recorder.thread:
                    self.audio_recorder.thread.join(timeout=1)
        
        # Cerrar la aplicación
        self.root.quit()
        self.root.destroy()


def main():
    """Función principal para iniciar la GUI."""
    root = tk.Tk()
    app = AudioTranscriptionGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
