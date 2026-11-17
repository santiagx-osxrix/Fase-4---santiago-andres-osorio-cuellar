"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Curso: Programación 213023 - Fase 4 (Prácticas Simuladas)
Estudiante: Santiago Andrés Osorio Cuéllar
Institución: Universidad Nacional Abierta y a Distancia - UNAD
Sede: Pitalito, Huila
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime

# Configuración del sistema de registros (Logs) para almacenar eventos y errores en archivo
logging.basicConfig(
    filename='errores_sistema.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)


# ==========================================
# EXCEPCIONES PERSONALIZADAS Y ENCADENADAS
# ==========================================
class ErrorSistemaFJ(Exception):
    """Clase base para excepciones personalizadas del sistema Software FJ."""
    pass


class ClienteInvalidoError(ErrorSistemaFJ):
    """Excepción lanzada cuando los datos del cliente no cumplen las validaciones."""
    pass


class ServicioNoDisponibleError(ErrorSistemaFJ):
    """Excepción lanzada cuando un servicio presenta fallas, parámetros erróneos o no está disponible."""
    pass


class ReservaInvalidaError(ErrorSistemaFJ):
    """Excepción lanzada cuando una operación de reserva falla (estado, duración, etc.)."""
    pass


# ==========================================
# CLASES ABSTRACTAS Y ENTIDADES BASE (OOP)
# ==========================================
class EntidadBase(ABC):
    """Clase abstracta que representa entidades generales del sistema."""
    
    @abstractmethod
    def obtener_detalles(self) -> str:
        """Método abstracto para retornar detalles textuales de la entidad."""
        pass


class Cliente(EntidadBase):
    """Clase Cliente con validaciones robustas y encapsulación de datos personales."""
    
    def __init__(self, identificacion: str, nombre: str, correo: str, telefono: str):
        self.__identificacion = ""
        self.__nombre = ""
        self.__correo = ""
        self.__telefono = ""
        
        # Validación rigurosa al instanciar mediante métodos encapsulados
        self.set_identificacion(identificacion)
        self.set_nombre(nombre)
        self.set_correo(correo)
        self.set_telefono(telefono)

    def set_identificacion(self, identificacion: str):
        if not identificacion or not identificacion.strip():
            raise ClienteInvalidoError("La identificación del cliente no puede estar vacía.")
        if not identificacion.isdigit():
            raise ClienteInvalidoError(f"Identificación inválida '{identificacion}': debe contener solo dígitos.")
        self.__identificacion = identificacion.strip()

    def get_identificacion(self) -> str:
        return self.__identificacion

    def set_nombre(self, nombre: str):
        if not nombre or len(nombre.strip()) < 3:
            raise ClienteInvalidoError("El nombre del cliente debe tener al menos 3 caracteres.")
        self.__nombre = nombre.strip()

    def get_nombre(self) -> str:
        return self.__nombre

    def set_correo(self, correo: str):
        if not correo or "@" not in correo or "." not in correo:
            raise ClienteInvalidoError(f"Correo electrónico inválido: '{correo}'.")
        self.__correo = correo.strip()

    def get_correo(self) -> str:
        return self.__correo

    def set_telefono(self, telefono: str):
        if not telefono or not telefono.isdigit() or len(telefono) < 7:
            raise ClienteInvalidoError(f"Teléfono inválido: '{telefono}'. Debe ser numérico de al menos 7 dígitos.")
        self.__telefono = telefono.strip()

    def get_telefono(self) -> str:
        return self.__telefono

    def obtener_detalles(self) -> str:
        return f"Cliente [ID: {self.__identificacion}, Nombre: {self.__nombre}, Correo: {self.__correo}, Teléfono: {self.__telefono}]"


class Servicio(ABC):
    """Clase abstracta Servicio que implementa polimorfismo para distintos tipos de servicios."""
    
    def __init__(self, codigo_servicio: str, descripcion_base: str, tarifa_base: float):
        self._codigo_servicio = codigo_servicio
        self._descripcion_base = descripcion_base
        self._tarifa_base = tarifa_base

    @abstractmethod
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        """Método abstracto polimórfico para calcular costos según reglas del servicio."""
        pass

    @abstractmethod
    def obtener_detalles(self) -> str:
        """Método abstracto para describir el servicio."""
        pass


# ==========================================
# SERVICIOS ESPECIALIZADOS (HERENCIA Y POLIMORFISMO)
# ==========================================
class ReservaSala(Servicio):
    """Servicio especializado para reservas de salas de reuniones o conferencias."""
    
    def __init__(self, codigo_servicio: str, capacidad: int, tarifa_base: float):
        super().__init__(codigo_servicio, "Reserva de Sala", tarifa_base)
        self.capacidad = capacidad

    # Método sobrecargado mediante argumentos opcionales / valores por defecto para cálculo de costos
    def calcular_costo(self, duracion: float, descuento_porcentaje: float = 0.0, incluir_impuesto: bool = True) -> float:
        try:
            if duracion <= 0:
                raise ServicioNoDisponibleError("La duración de la reserva de sala debe ser mayor a cero horas.")
            
            subtotal = self._tarifa_base * duracion
            if descuento_porcentaje < 0 or descuento_porcentaje > 100:
                raise ServicioNoDisponibleError("El porcentaje de descuento no es válido (0-100).")
            
            subtotal = subtotal * (1 - (descuento_porcentaje / 100))
            
            if incluir_impuesto:
                subtotal = subtotal * 1.19  # IVA 19%
            return round(subtotal, 2)
        except Exception as e:
            logging.error(f"Error calculando costo en ReservaSala: {e}")
            raise

    def obtener_detalles(self) -> str:
        return f"Servicio [Código: {self._codigo_servicio}, Tipo: {self._descripcion_base}, Capacidad: {self.capacidad} personas, Tarifa Base: ${self._tarifa_base}]"


class AlquilerEquipo(Servicio):
    """Servicio especializado para alquiler de equipos tecnológicos."""
    
    def __init__(self, codigo_servicio: str, tipo_equipo: str, tarifa_base: float):
        super().__init__(codigo_servicio, "Alquiler de Equipo", tarifa_base)
        self.tipo_equipo = tipo_equipo

    def calcular_costo(self, duracion: float, seguro_adicional: bool = False, tarifa_seguro: float = 15000.0) -> float:
        try:
            if duracion <= 0:
                raise ServicioNoDisponibleError("Las horas de alquiler de equipo deben ser mayores a cero.")
            
            costo = self._tarifa_base * duracion
            if seguro_adicional:
                costo += tarifa_seguro
            return round(costo, 2)
        except Exception as e:
            logging.error(f"Error calculando costo en AlquilerEquipo: {e}")
            raise

    def obtener_detalles(self) -> str:
        return f"Servicio [Código: {self._codigo_servicio}, Tipo: {self._descripcion_base}, Equipo: {self.tipo_equipo}, Tarifa Base: ${self._tarifa_base}]"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado para asesorías técnicas o empresariales."""
    
    def __init__(self, codigo_servicio: str, area_especialidad: str, tarifa_base: float):
        super().__init__(codigo_servicio, "Asesoría Especializada", tarifa_base)
        self.area_especialidad = area_especialidad

    def calcular_costo(self, duracion: float, complejidad_alta: bool = False) -> float:
        try:
            if duracion <= 0:
                raise ServicioNoDisponibleError("La duración de la asesoría debe ser positiva.")
            
            multiplicador = 1.35 if complejidad_alta else 1.0
            costo = self._tarifa_base * duracion * multiplicador
            return round(costo, 2)
        except Exception as e:
            logging.error(f"Error calculando costo en AsesoriaEspecializada: {e}")
            raise

    def obtener_detalles(self) -> str:
        return f"Servicio [Código: {self._codigo_servicio}, Tipo: {self._descripcion_base}, Área: {self.area_especialidad}, Tarifa Base: ${self._tarifa_base}]"


# ==========================================
# CLASE RESERVA (INTEGRACIÓN Y GESTIÓN)
# ==========================================
class Reserva:
    """Clase Reserva que integra cliente, servicio, duración y estado con manejo de excepciones."""
    
    contador_reservas = 1000

    def __init__(self, cliente: Cliente, servicio: Servicio, duracion: float, **kwargs):
        Reserva.contador_reservas += 1
        self.id_reserva = f"RES-{Reserva.contador_reservas}"
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Creada"
        self.costo_total = 0.0
        self.fecha_creacion = datetime.now()
        
        # Parámetros opcionales para sobrecarga de costos
        self.kwargs = kwargs

    def procesar_reserva(self):
        """Procesa y valida la reserva aplicando estructuras try/except/else/finally."""
        print(f"\n[Procesando] Iniciando procesamiento de reserva {self.id_reserva}...")
        logging.info(f"Iniciando procesamiento de reserva {self.id_reserva} para cliente {self.cliente.get_identificacion()}.")
        
        try:
            if self.duracion <= 0:
                raise ReservaInvalidaError("La duración especificada para la reserva es inválida.")
            
            # Cálculo del costo total utilizando el polimorfismo del servicio
            if isinstance(self.servicio, ReservaSala):
                desc = self.kwargs.get("descuento", 0.0)
                imp = self.kwargs.get("impuesto", True)
                self.costo_total = self.servicio.calcular_costo(self.duracion, descuento_porcentaje=desc, incluir_impuesto=imp)
            elif isinstance(self.servicio, AlquilerEquipo):
                seguro = self.kwargs.get("seguro", False)
                self.costo_total = self.servicio.calcular_costo(self.duracion, seguro_adicional=seguro)
            elif isinstance(self.servicio, AsesoriaEspecializada):
                comp = self.kwargs.get("complejidad", False)
                self.costo_total = self.servicio.calcular_costo(self.duracion, complejidad_alta=comp)
            else:
                # Encadenamiento de excepciones ante un servicio desconocido
                raise ReservaInvalidaError("Tipo de servicio no reconocido en el sistema.") from TypeError("Servicio base no válido")
                
        except (ServicioNoDisponibleError, ReservaInvalidaError) as ex:
            self.estado = "Fallida"
            mensaje_error = f"Error operativo al procesar la reserva {self.id_reserva}: {ex}"
            print(f"[X] {mensaje_error}")
            logging.error(mensaje_error)
            raise ReservaInvalidaError(mensaje_error) from ex
        else:
            self.estado = "Confirmada"
            mensaje_exito = f"Reserva {self.id_reserva} confirmada exitosamente. Costo Total: ${self.costo_total:,.2f}"
            print(f"[Éxito] {mensaje_exito}")
            logging.info(mensaje_exito)
        finally:
            print(f"[Finalización] Auditoría de cierre para intento de reserva {self.id_reserva}. Estado actual: {self.estado}")
            logging.info(f"Cierre de ciclo de procesamiento para {self.id_reserva}. Estado final: {self.estado}")

    def cancelar_reserva(self):
        """Cancela una reserva activa de forma controlada."""
        if self.estado == "Confirmada":
            self.estado = "Cancelada"
            print(f"[Cancelada] La reserva {self.id_reserva} ha sido cancelada correctamente.")
            logging.info(f"Reserva {self.id_reserva} cancelada por solicitud del usuario.")
        else:
            print(f"[Aviso] La reserva {self.id_reserva} no se puede cancelar porque su estado es: {self.estado}")
            logging.warning(f"Intento fallido de cancelación para reserva {self.id_reserva} en estado {self.estado}.")


# ==========================================
# SIMULACIÓN DE 10 OPERACIONES COMPLETAS
# ==========================================
def ejecutar_simulacion():
    print("==================================================")
    print(" INICIO DE SIMULACIÓN DE 10 OPERACIONES - SOFTWARE FJ")
    print(" Estudiante: Santiago Andrés Osorio Cuéllar")
    print("==================================================")
    
    operaciones_exitosas = 0
    operaciones_fallidas = 0

    # Operación 1: Creación de cliente válido y servicio de sala exitoso
    print("\n--- Operación 1: Cliente válido y Reserva de Sala ---")
    try:
        c1 = Cliente("1085300123", "Carlos Pérez", "carlos.perez@email.com", "3112345678")
        s1 = ReservaSala("SAL-01", 15, 50000.0)
        r1 = Reserva(c1, s1, 3.0, descuento=10.0, impuesto=True)
        r1.procesar_reserva()
        operaciones_exitosas += 1
    except Exception as e:
        print(f"Excepción capturada en simulación: {e}")
        operaciones_fallidas += 1

    # Operación 2: Intento de cliente con identificación inválida (Excepción controlada)
    print("\n--- Operación 2: Cliente con identificación inválida ---")
    try:
        c2 = Cliente("1085ABC", "Ana Gómez", "ana@email.com", "3201234567")
        operaciones_exitosas += 1
    except ClienteInvalidoError as cie:
        print(f"[Excepción Controlada Capturada]: {cie}")
        logging.warning(f"Operación 2 rechazada correctamente por validación de cliente: {cie}")
        operaciones_fallidas += 1

    # Operación 3: Alquiler de equipo tecnológico con éxito
    print("\n--- Operación 3: Alquiler de equipo tecnológico ---")
    try:
        c3 = Cliente("98765432", "María Rodríguez", "maria.rodriguez@email.com", "3159876543")
        s2 = AlquilerEquipo("EQ-05", "Portátil Core i7", 25000.0)
        r3 = Reserva(c3, s2, 5.0, seguro=True)
        r3.procesar_reserva()
        operaciones_exitosas += 1
    except Exception as e:
        print(f"Excepción capturada: {e}")
        operaciones_fallidas += 1

    # Operación 4: Asesoría especializada con complejidad alta
    print("\n--- Operación 4: Asesoría especializada con complejidad alta ---")
    try:
        c4 = Cliente("1122334455", "Luis Torres", "luis.torres@email.com", "3184567890")
        s3 = AsesoriaEspecializada("ASE-02", "Arquitectura Cloud Python", 80000.0)
        r4 = Reserva(c4, s3, 2.5, complejidad=True)
        r4.procesar_reserva()
        operaciones_exitosas += 1
    except Exception as e:
        print(f"Excepción capturada: {e}")
        operaciones_fallidas += 1

    # Operación 5: Reserva con duración negativa (Fallo controlado)
    print("\n--- Operación 5: Reserva con duración negativa (Error simulado) ---")
    try:
        c5 = Cliente("1020304050", "Sofia Castro", "sofia.castro@email.com", "3101112233")
        s4 = ReservaSala("SAL-02", 10, 40000.0)
        r5 = Reserva(c5, s4, -2.0)
        r5.procesar_reserva()
        operaciones_exitosas += 1
    except ReservaInvalidaError as rie:
        print(f"[Excepción Controlada Capturada]: {rie}")
        logging.warning(f"Operación 5 rechazada por duración inválida: {rie}")
        operaciones_fallidas += 1

    # Operación 6: Cliente con correo electrónico inválido
    print("\n--- Operación 6: Cliente con correo electrónico inválido ---")
    try:
        c6 = Cliente("5544332211", "Pedro Infante", "pedro-correo-sin-arroba", "3127778899")
        operaciones_exitosas += 1
    except ClienteInvalidoError as cie:
        print(f"[Excepción Controlada Capturada]: {cie}")
        logging.warning(f"Operación 6 rechazada por correo inválido: {cie}")
        operaciones_fallidas += 1

    # Operación 7: Alquiler de equipo sin seguro adicional
    print("\n--- Operación 7: Alquiler de equipo estándar sin seguro ---")
    try:
        c7 = Cliente("7788990011", "Lucia Méndez", "lucia.mendez@email.com", "3145556677")
        s5 = AlquilerEquipo("EQ-09", "Proyector Láser 4K", 35000.0)
        r7 = Reserva(c7, s5, 4.0, seguro=False)
        r7.procesar_reserva()
        operaciones_exitosas += 1
    except Exception as e:
        print(f"Excepción capturada: {e}")
        operaciones_fallidas += 1

    # Operación 8: Asesoría especializada con duración cero (ServicioNoDisponibleError)
    print("\n--- Operación 8: Asesoría con duración cero (Error simulado) ---")
    try:
        c8 = Cliente("3322114455", "Jorge Eliécer", "jorge.eliecer@email.com", "3178889900")
        s6 = AsesoriaEspecializada("ASE-08", "Ciberseguridad Ofensiva", 90000.0)
        r8 = Reserva(c8, s6, 0.0, complejidad=False)
        r8.procesar_reserva()
        operaciones_exitosas += 1
    except Exception as e:
        print(f"[Excepción Controlada Capturada]: {e}")
        operaciones_fallidas += 1

    # Operación 9: Cancelación exitosa de una reserva previa
    print("\n--- Operación 9: Cancelación de una reserva confirmada ---")
    try:
        c9 = Cliente("2233445566", "Andrea Valdés", "andrea.valdes@email.com", "3193334455")
        s7 = ReservaSala("SAL-03", 8, 45000.0)
        r9 = Reserva(c9, s7, 2.0)
        r9.procesar_reserva()
        r9.cancelar_reserva()
        operaciones_exitosas += 1
    except Exception as e:
        print(f"Excepción capturada: {e}")
        operaciones_fallidas += 1

    # Operación 10: Cliente con teléfono inválido (caracteres no numéricos)
    print("\n--- Operación 10: Cliente con teléfono inválido ---")
    try:
        c10 = Cliente("9988776655", "Gabriel García", "gabriel@email.com", "312ABC5566")
        operaciones_exitosas += 1
    except ClienteInvalidoError as cie:
        print(f"[Excepción Controlada Capturada]: {cie}")
        logging.warning(f"Operación 10 rechazada por teléfono inválido: {cie}")
        operaciones_fallidas += 1

    print("\n==================================================")
    print(" RESUMEN DE LA SIMULACIÓN - SOFTWARE FJ")
    print(f" Operaciones Exitosas (Completadas): {operaciones_exitosas}")
    print(f" Operaciones con Errores Controlados (Capturadas): {operaciones_fallidas}")
    print(" Sistema operativo y estable. Registros guardados en 'errores_sistema.log'.")
    print("==================================================")


if __name__ == "__main__":
    ejecutar_simulacion()
    