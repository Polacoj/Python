import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import logging
from typing import Tuple, Optional
from dataclasses import dataclass

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("procesador_eventos.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class ColumnConfig:
    """Configuración de columnas para procesamiento"""

    EVENTOS_INDICES = [0, 1, 6, 16, 20, 32, 13, 14]  # Base 0
    EVENTOS_NOMBRES = [
        "FECHA",
        "HORA",
        "OPERADOR",
        "TIPO_EVENTO",
        "BARRIO",
        "ORIGEN",
        "GAP",
        "SAE",
    ]

    NARRACION_INDICES = [2, 3, 4]
    NARRACION_NOMBRES = ["OPERADOR", "GAP", "SAE"]

    CMU_SAE_COL = 14
    CMU_ORIGEN_COL = 32
    CMU_MIN_COLS = 33

    GAP_COLS = [13, 14]  # Columnas GAP/SAE a limpiar en eventos
    NARRACION_GAP_COLS = [3, 4]  # Columnas GAP/SAE en narración


class DataCleaner:
    """Limpieza y normalización de datos"""

    @staticmethod
    def normalize_string(s) -> str:
        """Normaliza cadena removiendo acentos y convirtiendo a minúsculas"""
        import unicodedata

        if pd.isna(s):
            return ""
        normalized = unicodedata.normalize("NFKD", str(s).strip().lower())
        return "".join(c for c in normalized if not unicodedata.combining(c))

    @staticmethod
    def stringify_preserve_int(val):
        """Convierte valor a string, preservando enteros sin decimales"""
        if pd.isna(val):
            return ""
        try:
            f = float(val)
            return int(f) if f.is_integer() else int(f)
        except Exception:
            return str(val).strip()

    @staticmethod
    def parse_int_nullable(val):
        """Convierte a entero nullable (pd.NA si no es entero exacto)"""
        if pd.isna(val):
            return pd.NA
        try:
            f = float(val)
            return int(f) if f.is_integer() else pd.NA
        except Exception:
            s = str(val).strip()
            return int(s) if s.isdigit() else pd.NA

    @staticmethod
    def clean_gap_sae_columns(df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """Limpia columnas GAP y SAE eliminando texto después de '/'"""
        df_copy = df.copy()
        for col in columns:
            if col < len(df_copy.columns):
                # Procesar y limpiar valores en un paso
                cleaned_values = (
                    df_copy.iloc[:, col]
                    .fillna("")
                    .astype(str)
                    .str.split("/", n=1)
                    .str[0]
                    .str.strip()
                )
                # Asignar usando el nombre de columna en lugar de iloc para evitar warnings
                col_name = df_copy.columns[col]
                df_copy[col_name] = cleaned_values
        return df_copy


class FileProcessor:
    """Procesador base para archivos Excel"""

    def __init__(self, config: ColumnConfig):
        self.config = config
        self.cleaner = DataCleaner()

    def read_excel_safe(self, path: Path, sheet_name=0) -> Optional[pd.DataFrame]:
        """Lee archivo Excel con manejo de errores"""
        try:
            return pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
        except Exception as e:
            logger.error(f"Error leyendo {path}: {e}")
            raise

    def validate_columns(self, df: pd.DataFrame, required_cols: int, name: str) -> bool:
        """Valida que el DataFrame tenga columnas suficientes"""
        if df.shape[1] < required_cols:
            msg = f"{name} no tiene suficientes columnas. Tiene {df.shape[1]}, se requieren {required_cols}"
            logger.error(msg)
            raise ValueError(msg)
        return True


class NarracionProcessor(FileProcessor):
    """Procesador específico para archivos de narración"""

    def __init__(self):
        super().__init__(ColumnConfig())
        self.cmu_path = Path(__file__).parent / "archivos_xlsx" / "CMU - OCTUBRE.xlsx"

    def select_sheet(self, xls: pd.ExcelFile) -> Optional[int]:
        """Solicita al usuario seleccionar una hoja"""
        hojas = xls.sheet_names
        sheet_list = "\n".join(f"{i} - {h}" for i, h in enumerate(hojas))

        return simpledialog.askinteger(
            "Seleccionar hoja",
            f"Seleccione una hoja:\n\n{sheet_list}",
            minvalue=0,
            maxvalue=len(hojas) - 1,
        )

    def extract_eventos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extrae eventos de la hoja de narración"""
        # Limpiar GAP y SAE
        df = self.cleaner.clean_gap_sae_columns(df, self.config.NARRACION_GAP_COLS)

        # Validar columnas
        max_idx = max(self.config.NARRACION_INDICES)
        self.validate_columns(df, max_idx + 1, "Hoja de narración")

        # Filtrar filas donde columna 5 == "si"
        mask = df.iloc[:, 5].fillna("").astype(str).str.strip().str.lower() == "si"
        df_eventos = (
            df.loc[mask]
            .iloc[:, self.config.NARRACION_INDICES]
            .copy()
            .reset_index(drop=True)
        )
        df_eventos.columns = self.config.NARRACION_NOMBRES

        # Normalizar columnas
        df_eventos["GAP"] = df_eventos["GAP"].apply(self.cleaner.stringify_preserve_int)
        df_eventos["SAE"] = df_eventos["SAE"].apply(self.cleaner.stringify_preserve_int)
        df_eventos["SAE_INT"] = (
            df_eventos["SAE"].apply(self.cleaner.parse_int_nullable).astype("Int64")
        )
        df_eventos["SAE"] = (
            df_eventos["SAE"]
            .fillna("")
            .astype(str)
            .apply(self.cleaner.normalize_string)
        )

        return df_eventos

    def load_cmu_maestro(self) -> pd.DataFrame:
        """Carga el archivo maestro CMU"""
        if not self.cmu_path.exists():
            raise FileNotFoundError(f"No se encuentra el archivo CMU: {self.cmu_path}")

        maestro = self.read_excel_safe(self.cmu_path)
        self.validate_columns(maestro, self.config.CMU_MIN_COLS, "CMU")

        # Preparar columna SAE
        col_sae = maestro.columns[self.config.CMU_SAE_COL]
        maestro["SAE"] = (
            maestro[col_sae].fillna("").astype(str).apply(self.cleaner.normalize_string)
        )

        # Eliminar duplicados
        if maestro["SAE"].duplicated().any():
            logger.warning("CMU tiene SAEs duplicados, manteniendo el primero")
            maestro = maestro.drop_duplicates(subset=["SAE"], keep="first")

        return maestro

    def process(self, file_path: str) -> Tuple[bool, str]:
        """Procesa archivo de narración completo"""
        try:
            # Abrir archivo y seleccionar hoja
            xls = pd.ExcelFile(file_path, engine="openpyxl")
            sheet_idx = self.select_sheet(xls)

            if sheet_idx is None:
                return False, "Selección de hoja cancelada"

            # Leer hoja seleccionada
            df_narracion = pd.read_excel(
                file_path, sheet_name=sheet_idx, engine="openpyxl"
            )

            # Extraer eventos
            df_eventos = self.extract_eventos(df_narracion)

            # Cargar CMU y hacer merge
            maestro = self.load_cmu_maestro()
            col_origen = maestro.columns[self.config.CMU_ORIGEN_COL]

            resultado = df_eventos.merge(
                maestro[["SAE", col_origen]], on="SAE", how="inner"
            )

            if resultado.empty:
                return (
                    False,
                    "No se encontraron coincidencias entre SAE (narración) y SAE (CMU)",
                )

            # Restaurar SAE_INT si existe
            if "SAE_INT" in resultado.columns:
                resultado["SAE"] = resultado["SAE_INT"].astype("Int64")
                resultado = resultado.drop(columns=["SAE_INT"])

            resultado = resultado.rename(columns={col_origen: "ORIGEN"})

            # Guardar resultado
            output_path = Path(file_path).parent / "narracion_origen.xlsx"
            resultado.to_excel(output_path, index=False)

            logger.info(f"Narración procesada exitosamente: {output_path}")
            return True, f"Archivo generado: {output_path}"

        except Exception as e:
            logger.error(f"Error procesando narración: {e}", exc_info=True)
            return False, f"Error: {str(e)}"


class EventosProcessor(FileProcessor):
    """Procesador principal de eventos"""

    def __init__(self):
        super().__init__(ColumnConfig())
        # Importar procesadores especializados
        from contraventores_detenidos import ContraventoresProcessor
        from integrados import IntegradosProcessor
        from colaboradores import ColaboradoresProcessor

        self.contraventores_proc = ContraventoresProcessor()
        self.integrados_proc = IntegradosProcessor()
        self.colaboradores_proc = ColaboradoresProcessor()

    def extract_eventos(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extrae columnas de eventos del DataFrame principal"""
        # Limpiar GAP y SAE
        df = self.cleaner.clean_gap_sae_columns(df, self.config.GAP_COLS)

        # Validar columnas
        max_idx = max(self.config.EVENTOS_INDICES)
        self.validate_columns(df, max_idx + 1, "Archivo de eventos")

        # Extraer columnas
        df_eventos = df.iloc[:, self.config.EVENTOS_INDICES].copy()

        # Renombrar si es necesario
        if "TIPIFICACIÓN" in df_eventos.columns:
            df_eventos.rename(columns={"TIPIFICACIÓN": "TIPO DE EVENTO"}, inplace=True)

        return df_eventos

    def process_specialized(self, df: pd.DataFrame, output_dir: Path) -> dict:
        """Procesa y guarda datos especializados (contraventores, integrados, colaboradores)"""
        results = {}

        processors = {
            "contraventores": (
                self.contraventores_proc,
                "contraventores_detenidos_backup.xlsx",
            ),
            "integrados": (self.integrados_proc, "integrados_backup.xlsx"),
            "colaboradores": (self.colaboradores_proc, "colaboradores_backup.xlsx"),
        }

        for name, (processor, filename) in processors.items():
            try:
                df_result = processor.process_df(df)
                backup_path = output_dir / filename
                df_result.to_excel(backup_path, index=False)
                results[name] = {"df": df_result, "path": backup_path, "error": None}
                logger.info(f"Procesado {name}: {backup_path}")
            except Exception as e:
                results[name] = {"df": None, "path": None, "error": str(e)}
                logger.error(f"Error procesando {name}: {e}", exc_info=True)

        return results

    def create_unified_file(
        self, df_eventos: pd.DataFrame, specialized: dict, output_path: Path
    ):
        """Crea archivo unificado con todos los datos"""
        parts = [df_eventos]

        for name in ["contraventores", "integrados", "colaboradores"]:
            if specialized[name]["df"] is not None:
                parts.append(specialized[name]["df"])

        df_combined = pd.concat(parts, ignore_index=True, sort=False)

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df_combined.to_excel(writer, sheet_name="eventos", index=False)

        logger.info(f"Archivo unificado creado: {output_path}")

    def process(self, file_path: str) -> Tuple[bool, str]:
        """Procesa archivo de eventos completo"""
        try:
            # Leer archivo
            df = self.read_excel_safe(Path(file_path))
            output_dir = Path(file_path).parent

            # Extraer eventos principales
            df_eventos = self.extract_eventos(df)
            backup_eventos = output_dir / "eventos_backup.xlsx"
            df_eventos.to_excel(backup_eventos, index=False)
            logger.info(f"Eventos principales guardados: {backup_eventos}")

            # Procesar especializados
            specialized = self.process_specialized(df, output_dir)

            # Crear archivo unificado
            unified_path = output_dir / "eventos_unificado.xlsx"
            self.create_unified_file(df_eventos, specialized, unified_path)

            # Construir mensaje de resultado
            msg = f"Archivo unificado generado:\n{unified_path}\n\nBackups:\n{backup_eventos}"

            for name in ["contraventores", "integrados", "colaboradores"]:
                if specialized[name]["path"]:
                    msg += f"\n{specialized[name]['path']}"
                else:
                    msg += (
                        f"\n{name.capitalize()}: ERROR - {specialized[name]['error']}"
                    )

            logger.info("Procesamiento de eventos completado exitosamente")
            return True, msg

        except Exception as e:
            logger.error(f"Error procesando eventos: {e}", exc_info=True)
            return False, f"Error al procesar:\n{str(e)}"


class ProcessorGUI:
    """Interfaz gráfica de usuario"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Procesador de Eventos Excel")
        self.root.geometry("800x400")
        self.root.resizable(False, False)

        self.archivo_var = tk.StringVar(value="Ningún archivo seleccionado")
        self.estado_var = tk.StringVar()

        self.eventos_proc = EventosProcessor()
        self.narracion_proc = NarracionProcessor()

        self._create_widgets()

    def _create_widgets(self):
        """Crea los widgets de la interfaz"""
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text="Procesador de Eventos Excel",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=(0, 10))

        ttk.Button(
            frame,
            text="Seleccionar archivo Excel",
            command=self.select_and_process,
        ).pack(pady=10)

        ttk.Button(
            frame,
            text="❌ CERRAR",
            command=self.root.destroy,
            width=50,
        ).pack(side="bottom", pady=5)

        ttk.Label(frame, textvariable=self.archivo_var).pack(pady=5)
        ttk.Label(frame, textvariable=self.estado_var, foreground="green").pack(pady=50)

        ttk.Separator(frame).pack(fill="x", pady=20)

        ttk.Label(
            frame,
            text="Columnas procesadas: FECHA, HORA, OPERADOR, TIPO_EVENTO, BARRIO, ORIGEN, GAP, SAE",
            font=("Segoe UI", 9, "italic"),
            foreground="gray",
        ).pack()

    def select_and_process(self):
        """Selecciona y procesa archivo de eventos"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")],
        )

        if not archivo:
            self.estado_var.set("Selección cancelada")
            return

        self.archivo_var.set(Path(archivo).name)
        self.estado_var.set("Procesando...")
        self.root.update_idletasks()

        ok, mensaje = self.eventos_proc.process(archivo)

        self.estado_var.set(mensaje)
        if ok:
            messagebox.showinfo("Proceso finalizado", mensaje)
            self._ask_process_narracion()
        else:
            messagebox.showerror("Error", mensaje)

    def _ask_process_narracion(self):
        """Pregunta si se desea procesar archivo de narración"""
        if messagebox.askyesno(
            "Procesar narración", "¿Desea procesar un archivo de narración ahora?"
        ):
            archivo = filedialog.askopenfilename(
                title="Seleccionar archivo de narración",
                filetypes=[("Archivos Excel", "*.xlsx *.xls")],
            )

            if archivo:
                self.estado_var.set("Procesando narración...")
                self.root.update_idletasks()

                ok, msg = self.narracion_proc.process(archivo)
                self.estado_var.set(msg)

                if ok:
                    messagebox.showinfo("Narración finalizada", msg)
                else:
                    messagebox.showerror("Error en narración", msg)

    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ProcessorGUI()
    app.run()
