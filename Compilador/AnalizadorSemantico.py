
PROCEDIMIENTO = "procedimiento"
VARIABLE = "variable"
CONSTANTE = "constante"
COMODIN = "comodin"

NOMBRE = 0
TIPO = 1
VALOR = 2

class AnalizadorSemantico(object):
	def __init__(self, output):
		self.out = output
		self.tabla = []
		self.cant_variables = 0
	
	def _identificador_existente(self, nombre, base, desplazamiento):
		for i in range(base, base + desplazamiento):
			if self.tabla[i][NOMBRE] == nombre:
				return True
		return False
	
	def agregar_identificador(self, base, desplazamiento, nombre, tipo, valor=None):
		if len(self.tabla) < base + desplazamiento:
			raise ValueError("Base + desplazamiento fuera de rango")
		if self._identificador_existente(nombre, base, desplazamiento):
			raise ValueError("Identificador en uso en este ambiente")
		
		if tipo == VARIABLE:
			valor = self.cant_variables
			self.cant_variables += 1
		
		if len(self.tabla) == base + desplazamiento:
			self.tabla.append((nombre, tipo, valor))
		else:
			self.tabla[base + desplazamiento] = (nombre, tipo, valor)
	
	def _busqueda(self, nombre, base, desplazamiento, tipos_correctos, mensaje_tipo_incorrecto):
		for i in range(base + desplazamiento - 1, -1, -1):
			if self.tabla[i][NOMBRE] == nombre:
				if self.tabla[i][TIPO] in tipos_correctos or self.tabla[i][TIPO] == COMODIN:
					return True
				else:
					self.out.write("Error Semantico: " + mensaje_tipo_incorrecto + "\n")
					return False
		self.out.write("Error Semantico: Identificador no encontrado ("+ nombre +")\n")
		return False
		
	def asignacion_correcta(self, nombre, base, desplazamiento):
		return self._busqueda(nombre, base, desplazamiento, [VARIABLE], "Solo pueden utilizarse variables del lado izquierdo de una asignacion")
	
	def invocacion_procedimiento_correcta(self, nombre, base, desplazamiento):
		return self._busqueda(nombre, base, desplazamiento, [PROCEDIMIENTO], "Solo pueden invocarse procedimientos")
	
	def factor_correcto(self, nombre, base, desplazamiento):
		return self._busqueda(nombre, base, desplazamiento, [VARIABLE, CONSTANTE], "Solo pueden usarse variables o constantes en una expresion")
	
	def lectura_correcta(self, nombre, base, desplazamiento):
		return self._busqueda(nombre, base, desplazamiento, [VARIABLE], "Solo pueden asignarse valores de lecturas en variables")
		
	def agregar_comodin(self, nombre, base, desplazamiento):
		for i in range(base + desplazamiento - 1, -1, -1):
			if self.tabla[i][NOMBRE] == nombre:
				return False
		self.agregar_identificador(base, desplazamiento, nombre, COMODIN)
		return True
	
	def _obtener(self, nombre, base, desplazamiento, elem):
		for i in range(base + desplazamiento - 1, -1, -1):
			if self.tabla[i][NOMBRE] == nombre:
				return self.tabla[i][elem]
	
	def obtener_valor(self, nombre, base, desplazamiento):
		return self._obtener(nombre, base, desplazamiento, VALOR)
				
	def obtener_tipo(self, nombre, base, desplazamiento):
		return self._obtener(nombre, base, desplazamiento, TIPO)
	
	def obtener_cantidad_variables(self):
		return self.cant_variables
	
	def __str__(self):
		return str(self.tabla)
	
	
