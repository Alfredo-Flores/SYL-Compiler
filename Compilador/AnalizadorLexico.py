ANULADOS = [" ", "\t"]
QUIEBRE = ["#", "\n"]
VACIO = ""
COMILLAS = "'"
COMILLA_ERROR = "\""

PALABRAS_RESERVADAS = ["if", "const", "var", "procedure", "call", "if", "while", "begin", "then", "do", "odd", "end", "write", "writeln", "readln"]

ERROR_LEXICO = "ERROR LEXICO"
IDENTIFICADOR = "IDENTIFICADOR"
RESERVADA = "RESERVADA"
NUMERO = "NUMERO"
ASIGNACION = "ASIGNACION"
MENOR = "MENOR"
MAYOR = "MAYOR"
IGUAL = "IGUAL"
MENOR_IGUAL = "MENOR IGUAL"
MAYOR_IGUAL = "MAYOR IGUAL"
DISTINTO = "DISTINTO"
PUNTO = "PUNTO"
MAS = "MAS"
MENOS = "MENOS"
MULTIPLICAR = "MULTIPLICAR"
PUNTO_Y_COMA = "PUNTO Y COMA"
COMA = "COMA"
DIVIDIR = "DIVIDIR"
ABRIR_PARENTESIS = "ABRIR"
CERRAR_PARENTESIS = "CERRAR"
EOF = "EOF"
CADENA = "CADENA"
ESPECIALES = {"+": MAS, "-": MENOS, "*": MULTIPLICAR, "/": DIVIDIR, ".": PUNTO, ",": COMA, ";": PUNTO_Y_COMA, "=": IGUAL, "(": ABRIR_PARENTESIS, ")": CERRAR_PARENTESIS }	

LARGO_IDENTIFICADOR_MAX = 20
LARGO_NUMERO_MAX = 8
	
class AnalizadorLexico(object):
	
	def __init__(self, program_path, output):
		self._leer_archivo(program_path)
		self.out = output
	
		self.num_linea = 0
		self.quedan_lineas = True
		self._leer_linea()
		self.valor = None
		self.tipo = None
		self.freno = False
		self.cadena_error = False
	
	def _leer_archivo(self, program_path):
		self.lineas = []
		try:
			prog = open(program_path)
		except IOError:
			raise IOError("Archivo de programa no existe, o no se tienen permisos")
		for line in prog:
			self.lineas.append(line)
		prog.close()
	
	def _leer_linea(self):
		if len(self.lineas) == self.num_linea:
			self.quedan_lineas = False
			return
		
		self.linea_actual = self.lineas[self.num_linea]
		self.out.write(self.linea_actual)
		self.linea_actual = self.linea_actual.strip()
		self.num_linea += 1
	
	def obtener_valor_actual(self):
		return self.valor
		
	def _largo(self, esperado, largo, mensaje_error):
		if self.tipo != esperado: 
			raise TypeError("Consultando largo de identificador para un token no identificador")
		if len(self.valor) > largo:
			self.out.write("Error Lexico: " + mensaje_error + "\n")
			return True
		return False
	
	def identificador_largo(self):
		return self._largo(IDENTIFICADOR, LARGO_IDENTIFICADOR_MAX, "Identificador demasiado largo")
	
	def numero_largo(self):
		return self._largo(NUMERO, LARGO_NUMERO_MAX, "Numero demasiado largo")
		
	def obtener_tipo_actual(self):
		return self.tipo
	
	def frenar(self):
		self.freno = True
	
	def error_en_cadena(self):
		if self.cadena_error:
			self.cadena_error = False
			return True
		return False
	
	def obtener_simbolo(self):
		if self.freno:
			self.freno = False
			return self.tipo
			
		while self.quedan_lineas:
			for index, c in enumerate(self.linea_actual):
				if c in ANULADOS: continue
				if c in QUIEBRE: break
				
				if c.isalpha():
					self._obtener_id_o_reservada(index)
					self.tipo = RESERVADA if self.valor.lower() in PALABRAS_RESERVADAS else IDENTIFICADOR
					return self.tipo
				
				if c.isdigit():
					self._obtener_numero(index)
					self.tipo = NUMERO
					return NUMERO
				
				if c == ":":
					self._obtener_asignacion(index)
					if self.valor != None:
						self.tipo = ASIGNACION
					else:
						self.out.write("Error Lexico: Dos puntos (:) sin ser asignacion (:=)\n")
						self.tipo = ERROR_LEXICO
					return self.tipo
				
				if c == "<":
					self._obtener_menoridad(index)
					self.tipo = MENOR_IGUAL if self.valor == "<=" else DISTINTO if self.valor == "<>" else MENOR
					return self.tipo
					
				if c == ">":
					self._obtener_mayoridad(index)
					self.tipo = MAYOR_IGUAL if self.valor == ">=" else MAYOR
					return self.tipo
				
				if c in ESPECIALES:
					self.valor = c
					self.linea_actual = self.linea_actual[index + 1:]
					self.tipo = ESPECIALES[c]
					return self.tipo
				
				if c == COMILLAS or c == COMILLA_ERROR:
					self._obtener_cadena(index)
					if self.valor is None:
						self.out.write("Error Lexico: Cadena no finalizada antes que finalice el archivo\n")
						self.tipo = ERROR_LEXICO
					else:
						self.tipo = CADENA
					return self.tipo
				
				self.out.write("Error Lexico: Caracter no reconocido: " + c + "\n")
				self.linea_actual = self.linea_actual[index + 1:]
				self.tipo = ERROR_LEXICO
				return ERROR_LEXICO
						
			self._leer_linea()
		self.tipo = EOF
		return EOF
	
	def _obtener_completo(self, index, numero = False):
		formado = ""
		for i in range(index, len(self.linea_actual)):
			c = self.linea_actual[i]
			if c in ANULADOS or c in QUIEBRE or (numero and not c.isdigit()) or (not c.isdigit() and not c.isalpha()): break
			formado += c
			index += 1
		self.valor = formado
		self.linea_actual = self.linea_actual[index:]
		
	def _obtener_cadena(self, index):
		formado = ""
		if self.linea_actual[index] == COMILLA_ERROR: 
			self.out.write("Error Lexico: comillas de cadena incorrecta\n")
			self.cadena_error = True
		index += 1
		while self.quedan_lineas:
			for i in range(index, len(self.linea_actual)):
				c = self.linea_actual[i]
				if c == COMILLAS or c == COMILLA_ERROR:
					self.valor = formado
					self.linea_actual = self.linea_actual[i+1:]
					if c == COMILLA_ERROR and not self.cadena_error:
						self.out.write("Error Lexico: comillas de cadena incorrecta\n")
						self.cadena_error = True
					return
					
				formado += c
			self._leer_linea()
			index = 0
		self.valor = None
				
		
	def _obtener_id_o_reservada(self, index):
		self._obtener_completo(index, numero=False)
	
	def _obtener_numero(self, index):
		self._obtener_completo(index, numero=True)
				
	def _obtener_combinaciones(self, index, primero, posibles_segundos):
		c = self.linea_actual[index]
		self.value = None
		if c != primero:
			return
		index += 1
		for i in range(index, len(self.linea_actual)):
			index += 1
			c = self.linea_actual[i]
			if c in ANULADOS: continue
			self.valor = primero + (c if c in posibles_segundos else "")
			if self.valor == primero: index -= 1
			break

		self.linea_actual = self.linea_actual[index:]
	
	def _obtener_menoridad(self, index):
		self._obtener_combinaciones(index, "<", [">", "="])
	
	def _obtener_mayoridad(self, index):
		self._obtener_combinaciones(index, ">", ["="])

	def _obtener_asignacion(self, index):
		self._obtener_combinaciones(index, ":", ["="])
		if self.valor != ":=": self.valor = None
			
if __name__=="__main__":
	output = open("salida.txt", "w")
	import sys
	ruta = sys.argv[1] if len(sys.argv) > 1 else "ejemplo.txt"
	al = AnalizadorLexico(ruta, output)
	while True:
		c = al.obtener_simbolo()
		if c == EOF: break
		print c
	output.close()
