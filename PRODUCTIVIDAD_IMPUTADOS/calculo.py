import pandas as pd
import logging
from typing import Dict, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CalculadorPuntajes:
    # ====================================================================
    # SECCIÓN: CONFIGURACIÓN DE PUNTAJES BASE
    # ====================================================================
    # Define los puntajes base según el tipo de evento.
    # Estos valores se usan como base para el cálculo final.
    # ====================================================================
    def __init__(self):
        # Diccionarios para cálculos de puntaje
        self.puntaje_gral = {
            "INTERVENCION DESTACADA": 0.5,
            "ROBO/HURTO": 1.25,
            "DELITO": 0.5,
            "CONTRAVENCION": 0.25,
        }

        # ====================================================================
        # SECCIÓN: CONFIGURACIÓN DE MULTIPLICADORES POR BARRIO
        # ====================================================================
        # Define el multiplicador que se aplica según el barrio.
        # Los barrios con mayor riesgo/complejidad tienen multiplicadores
        # más altos (0.75), mientras que otros tienen multiplicadores
        # menores (0, 0.25, 0.50).
        # ====================================================================
        self.puntajes_barrio = {
            "balvanera": 0,
            "barracas": 0,
            "constitucion": 0,
            "flores": 0.25,
            "liniers": 0.50,
            "nueva pompeya": 0.25,
            "retiro": 0.25,
            "villa lugano": 0.50,
            "caballito": 0.50,
            "mataderos": 0.50,
            "monserrat": 0.50,
            "almagro": 0.50,
            "boedo": 0.50,
            "chacarita": 0.50,
            "floresta": 0.50,
            "la boca": 0.50,
            "la paternal": 0.50,
            "palermo": 0.50,
            "parque avellaneda": 0.50,
            "parque chacabuco": 0.50,
            "parque patricios": 0.50,
            "recoleta": 0.50,
            "saavedra": 0.50,
            "san nicolas": 0.50,
            "san telmo": 0.50,
            "villa crespo": 0.50,
            "villa luro": 0.50,
            "villa riachuelo": 0.50,
            "villa soldati": 0.50,
            "agronomia": 0.75,
            "belgrano": 0.75,
            "coghlan": 0.75,
            "colegiales": 0.75,
            "monte castro": 0.75,
            "nuñez": 0.75,
            "parque chas": 0.75,
            "puerto madero": 0.75,
            "san cristobal": 0.75,
            "velez sarsfield": 0.75,
            "versalles": 0.75,
            "villa del parque": 0.75,
            "villa devoto": 0.75,
            "villa general mitre": 0.75,
            "villa ortuzar": 0.75,
            "villa pueyrredon": 0.75,
            "villa real": 0.75,
            "subte": 0.75,
            "villa santa rita": 0.75,
            "villa urquiza": 0.75,
        }

    def _validar_dataframe(self, df: pd.DataFrame) -> bool:
        """
        Valida que el DataFrame tenga las columnas necesarias.

        Args:
            df: DataFrame a validar

        Returns:
            bool: True si el DataFrame es válido, False en caso contrario
        """
        if df.empty:
            logger.error("DataFrame vacío")
            return False

        columnas_requeridas = ["TIPO DE EVENTO", "BARRIO"]
        for col in columnas_requeridas:
            if col not in df.columns:
                logger.error(f"Falta columna requerida: {col}")
                logger.error(f"Columnas disponibles: {list(df.columns)}")
                return False

        return True

    def _calcular_puntaje_individual(self, fila) -> float:
        """
        Calcula el puntaje para una fila individual del DataFrame.

        Fórmula de cálculo:
        - Si es CONTRAVENCION: puntaje = puntaje_base
        - Si NO es CONTRAVENCION: puntaje = puntaje_base + (puntaje_base * multiplicador_barrio)

        Args:
            fila: Fila del DataFrame con columnas 'TIPO DE EVENTO' y 'BARRIO'

        Returns:
            float: Puntaje calculado

        Example:
            >>> # Para un DELITO (0.5) en Belgrano (0.75):
            >>> # puntaje = 0.5 + (0.5 * 0.75) = 0.875
        """
        try:
            tipo_evento = str(fila["TIPO DE EVENTO"]).strip()
            barrio = str(fila["BARRIO"]).strip().lower()

            # Puntaje base según tipo de evento
            puntaje_base = self.puntaje_gral.get(tipo_evento, 0)

            # Puntaje adicional por barrio
            puntaje_barrio = self.puntajes_barrio.get(barrio, 0)

            # Aplicar fórmula según reglas:
            # Si es CONTRAVENCION: solo puntaje base (sin multiplicar por barrio)
            # Si no es CONTRAVENCION: puntaje base + (puntaje base * puntaje_barrio)
            if tipo_evento == "CONTRAVENCION":
                return puntaje_base
            else:
                return puntaje_base + (puntaje_base * puntaje_barrio)

        except Exception as e:
            logger.error(f"Error calculando puntaje para fila: {e}")
            return 0.0

    def _crear_formula_explicativa(self, fila) -> str:
        """Crea una fórmula explicativa para una fila."""
        try:
            tipo_evento = str(fila["TIPO DE EVENTO"]).strip()
            barrio = str(fila["BARRIO"]).strip().lower()

            if tipo_evento not in self.puntaje_gral:
                return f"Tipo de evento no reconocido: {tipo_evento}"

            puntaje_base = self.puntaje_gral[tipo_evento]
            puntaje_barrio = self.puntajes_barrio.get(barrio, 0)

            if tipo_evento == "CONTRAVENCION":
                return f"= {puntaje_base} (solo puntaje base - contravención)"
            else:
                return f"= ({puntaje_base} * {puntaje_barrio:.2f}) + {puntaje_base}"

        except Exception as e:
            logger.error(f"Error creando fórmula: {e}")
            return "Error en fórmula"

    def calcular_puntajes_dataframe(self, df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Calcula puntajes para todo un DataFrame.

        Este método:
        1. Valida el DataFrame de entrada
        2. Calcula el puntaje para cada fila
        3. Agrega columnas con información del cálculo:
           - PUNTAJE: puntaje final calculado
           - P. EVENTO: puntaje base del evento
           - P. BARRIO: multiplicador del barrio
           - FORMULA: explicación del cálculo

        Args:
            df: DataFrame con columnas 'TIPO DE EVENTO' y 'BARRIO'

        Returns:
            DataFrame con columnas adicionales de puntaje o None si hay error
        """
        try:
            # Validar DataFrame
            if not self._validar_dataframe(df):
                logger.error("DataFrame no válido para cálculo de puntajes")
                return None

            # Crear copia para no modificar el original
            df_resultado = df.copy()

            logger.info(f"Calculando puntajes para {len(df_resultado)} registros")

            # Aplicar cálculos
            df_resultado["PUNTAJE"] = df_resultado.apply(
                self._calcular_puntaje_individual, axis=1
            )
            df_resultado["P. EVENTO"] = df_resultado.apply(
                lambda fila: self.puntaje_gral.get(
                    str(fila["TIPO DE EVENTO"]).strip(), 0
                ),
                axis=1,
            )
            df_resultado["P. BARRIO"] = df_resultado.apply(
                lambda fila: self.puntajes_barrio.get(str(fila["BARRIO"]).strip(), 0),
                axis=1,
            )
            df_resultado["FORMULA"] = df_resultado.apply(
                self._crear_formula_explicativa, axis=1
            )

            logger.info(
                f"Cálculo completado. Puntaje total: {df_resultado['PUNTAJE'].sum():.2f}"
            )

            return df_resultado

        except Exception as e:
            logger.error(f"Error en calcular_puntajes_dataframe: {e}")
            return None

    def generar_resumen(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Genera un resumen estadístico del DataFrame con puntajes.

        Returns:
            dict: Resumen con estadísticas como:
                - total_registros
                - puntaje_promedio
                - puntaje_total
                - distribucion_eventos
                - top_operadores (si existe columna OPERADOR)
                - top_grupos (si existe columna GRUPO)
        """
        try:
            if df.empty or "PUNTAJE" not in df.columns:
                return {"error": "DataFrame sin puntajes calculados"}

            resumen = {
                "total_registros": len(df),
                "puntaje_promedio": float(df["PUNTAJE"].mean()),
                "puntaje_total": float(df["PUNTAJE"].sum()),
                "puntaje_minimo": float(df["PUNTAJE"].min()),
                "puntaje_maximo": float(df["PUNTAJE"].max()),
                "distribucion_eventos": df["TIPO DE EVENTO"].value_counts().to_dict(),
                "top_barrios": df["BARRIO"].value_counts().head(10).to_dict(),
            }

            # Calcular top operadores si existe la columna
            if "OPERADOR" in df.columns:
                top_operadores = (
                    df.groupby("OPERADOR")["PUNTAJE"]
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                )
                resumen["top_operadores"] = top_operadores.round(3).to_dict()

            # Calcular top grupo si existe la columna (para SISEP)
            if "GRUPO" in df.columns and "OPERADOR" not in df.columns:
                top_grupos = (
                    df.groupby("GRUPO")["PUNTAJE"]
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                )
                resumen["top_grupos"] = top_grupos.round(3).to_dict()

            return resumen

        except Exception as e:
            logger.error(f"Error generando resumen: {e}")
            return {"error": f"Error generando resumen: {str(e)}"}

    def guardar_con_puntajes(
        self, df: pd.DataFrame, ruta_salida: str
    ) -> Optional[pd.DataFrame]:
        """
        Guarda el DataFrame con puntajes en un archivo Excel.

        Args:
            df: DataFrame a guardar
            ruta_salida: Ruta donde guardar el archivo

        Returns:
            DataFrame con puntajes o None si hay error
        """
        try:
            # Calcular puntajes primero
            df_con_puntajes = self.calcular_puntajes_dataframe(df)

            if df_con_puntajes is None:
                logger.error("No se pudo calcular puntajes para el DataFrame")
                return None

            # Reordenar columnas para mejor presentación
            columnas = list(df_con_puntajes.columns)
            nuevas_columnas = ["P. EVENTO", "P. BARRIO", "FORMULA", "PUNTAJE"]

            # Mover las columnas nuevas al final
            columnas_ordenadas = [col for col in columnas if col not in nuevas_columnas]
            columnas_ordenadas.extend(
                [col for col in nuevas_columnas if col in columnas]
            )

            # Crear DataFrame con columnas ordenadas
            df_ordenado = df_con_puntajes[columnas_ordenadas]

            # Guardar
            df_ordenado.to_excel(ruta_salida, index=False, engine="openpyxl")
            logger.info(f"Archivo guardado exitosamente en: {ruta_salida}")

            return df_ordenado

        except Exception as e:
            logger.error(f"Error guardando archivo {ruta_salida}: {e}")
            return None
