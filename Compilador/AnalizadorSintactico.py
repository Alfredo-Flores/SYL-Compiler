import AnalizadorLexico
import AnalizadorSemantico

CONST = "const"
VAR = "var"
PROCEDURE = "procedure"
CALL = "call"
IF = "if"
WHILE = "while"
BEGIN = "begin"
THEN = "then"
DO = "do"
ODD = "odd"
END = "end"
WRITE = "write"
WRITELN = "writeln"
READLN = "readln"

class AnalizadorSintactico(object):
	
	def __init__(self, scanner, semantico, generador, output):
		self.out = output
		self.scanner = scanner
		self.semantico = semantico
		self.generador = generador
	
	def _parsear_bloque(self, base = 0):
		self.generador.marcar_bloque()
		desplazamiento = 0
		simbolo = self.scanner.obtener_simbolo()
		valor = self.scanner.obtener_valor_actual()
		#Analizamos la parte de constantes:
		if simbolo == AnalizadorLexico.RESERVADA and valor.lower() == CONST:
			while True:
				simbolo = self.scanner.obtener_simbolo()
				if simbolo == AnalizadorLexico.IDENTIFICADOR:
					identificador = self.scanner.obtener_valor_actual()
					if self.scanner.identificador_largo():
						self.generador = self.generador.no_generar()
									
					simbolo = self.scanner.obtener_simbolo()
					if simbolo != AnalizadorLexico.IGUAL:
						self.out.write("Error Sintactico: asignacion de constante esperada (=)\n")
						self.scanner.frenar()
						self.generador = self.generador.no_generar()
						
					simbolo = self.scanner.obtener_simbolo()
					if simbolo == AnalizadorLexico.NUMERO:
						if self.scanner.numero_largo():
							self.generador = self.generador.no_generar()
					else:
						self.out.write("Error Sintactico: asignacion de constante a un valor no numerico\n")
						self.generador = self.generador.no_generar()
						self.scanner.frenar()
					
					try:
						self.semantico.agregar_identificador(base,desplazamiento, identificador, AnalizadorSemantico.CONSTANTE, self.scanner.obtener_valor_actual())
						desplazamiento += 1
					except:
						self.generador = self.generador.no_generar()
													
					simbolo = self.scanner.obtener_simbolo()
					if simbolo == AnalizadorLexico.PUNTO_Y_COMA:
						simbolo = self.scanner.obtener_simbolo()
						break
					elif simbolo != AnalizadorLexico.COMA:
						self.out.write("Error Sintactico: Se esperaba punto y coma (;) o coma (,) luego de declaracion de constante\n")
						self.generador = self.generador.no_generar()
						self.scanner.frenar()
						
				else:
					self.out.write("Error Sintactico: declaracion de constante no seguida de un identificador\n")
					break
					
		valor = self.scanner.obtener_valor_actual()
		if simbolo == AnalizadorLexico.RESERVADA and valor.lower() == VAR:
			while True:
				simbolo = self.scanner.obtener_simbolo()
				if simbolo == AnalizadorLexico.IDENTIFICADOR:
					identificador = self.scanner.obtener_valor_actual()
					if self.scanner.identificador_largo():
						self.generador = self.generador.no_generar()
					try:
						self.semantico.agregar_identificador(base,desplazamiento, identificador, AnalizadorSemantico.VARIABLE)
						desplazamiento += 1
					except:
						self.generador = self.generador.no_generar()
				else: 
					self.out.write("Error Sintactico: declaracion de variable no seguida de un identificador\n")
					self.generador = self.generador.no_generar()
					
				simbolo = self.scanner.obtener_simbolo()
				if simbolo == AnalizadorLexico.PUNTO_Y_COMA:
					simbolo = self.scanner.obtener_simbolo()
					break
				elif simbolo != AnalizadorLexico.COMA:
					self.out.write("Error Sintactico: Se esperaba punto y coma (;) o coma (,) luego de declaracion de variable\n")
					self.generador = self.generador.no_generar()
					self.scanner.frenar()
					
		while simbolo == AnalizadorLexico.RESERVADA and self.scanner.obtener_valor_actual().lower() == PROCEDURE:
			simbolo = self.scanner.obtener_simbolo()
			if simbolo != AnalizadorLexico.IDENTIFICADOR:
				self.out.write("Error Sintactico: declaracion de procedimiento no seguida de un identificador\n")
				continue
			identificador = self.scanner.obtener_valor_actual()
			if self.scanner.identificador_largo():
				self.generador = self.generador.no_generar()
			try: 
				self.semantico.agregar_identificador(base,desplazamiento, identificador, AnalizadorSemantico.PROCEDIMIENTO, len(self.generador))
				desplazamiento += 1
			except:
				self.generador = self.generador.no_generar()
				continue
			
			simbolo = self.scanner.obtener_simbolo()
			if simbolo != AnalizadorLexico.PUNTO_Y_COMA:
				self.out.write("Error Sintactico: Luego de la identificacion de un procedimiento se esperaba por punto y coma (;)\n")
				self.generador = self.generador.no_generar()
				self.scanner.frenar()
				#continue
			self._parsear_bloque(base + desplazamiento) 
			self.generador.agregar_return()
			if self.scanner.obtener_tipo_actual() != AnalizadorLexico.PUNTO_Y_COMA:
				self.out.write("Error Sintactico: Luego de definir un procedimiento se esperaba por punto y coma (;)\n")
				self.generador = self.generador.no_generar()
				continue
			simbolo = self.scanner.obtener_simbolo()
			
		self.generador.corregir_bloque()
		self._parsear_proposicion(base, desplazamiento)
			
	def _parsear_proposicion(self, base, desplazamiento):
		simbolo = self.scanner.obtener_tipo_actual()
		if simbolo != AnalizadorLexico.IDENTIFICADOR and simbolo != AnalizadorLexico.RESERVADA:
			return desplazamiento
		
		valor = self.scanner.obtener_valor_actual()
		if valor.lower() == END:
			return desplazamiento
		
		if valor.lower() == CALL:
			simbolo = self.scanner.obtener_simbolo()
			identificador = self.scanner.obtener_valor_actual()
			
			if not self.semantico.invocacion_procedimiento_correcta(identificador, base, desplazamiento):
				self.generador = self.generador.no_generar()
				if self.semantico.agregar_comodin(identificador, base, desplazamiento):
					desplazamiento += 1
			self.generador.call(self.semantico.obtener_valor(identificador, base, desplazamiento))
			simbolo = self.scanner.obtener_simbolo()
			
		elif valor.lower() == IF:
			simbolo = self.scanner.obtener_simbolo()
			desplazamiento = self._parsear_condicion(base, desplazamiento)
			simbolo = self.scanner.obtener_tipo_actual()
			if simbolo == AnalizadorLexico.RESERVADA and self.scanner.obtener_valor_actual().lower() == THEN:
				simbolo = self.scanner.obtener_simbolo()
				desplazamiento = self._parsear_proposicion(base, desplazamiento)
				self.generador.corregir_condicion()
			else:
				self.out.write("Error Sintactico: Se esperaba un 'then' luego de la condicion de un 'if'\n")
				self.generador = self.generador.no_generar()
				self.scanner.frenar()
		elif valor.lower() == WHILE:
			self.generador.recordar_while()
			simbolo = self.scanner.obtener_simbolo()
			desplazamiento = self._parsear_condicion(base, desplazamiento)
			simbolo = self.scanner.obtener_tipo_actual()
			if not (simbolo == AnalizadorLexico.RESERVADA and self.scanner.obtener_valor_actual().lower() == DO):
				self.out.write("Error Sintactico: Se esperaba un 'do' luego de la condicion de un 'while'\n")
				self.generador = self.generador.no_generar()
				if not (simbolo == AnalizadorLexico.RESERVADA and self.scanner.obtener_valor_actual().lower() == THEN):
					self.scanner.frenar()
			simbolo = self.scanner.obtener_simbolo()
			desplazamiento = self._parsear_proposicion(base, desplazamiento)
			self.generador.salto_while()
			self.generador.corregir_condicion()
			
			
		elif valor.lower() == BEGIN:
			while True:
				simbolo = self.scanner.obtener_simbolo()
				desplazamiento = self._parsear_proposicion(base, desplazamiento)
				simbolo = self.scanner.obtener_tipo_actual()
				if simbolo == AnalizadorLexico.RESERVADA and self.scanner.obtener_valor_actual().lower() == END:
					simbolo = self.scanner.obtener_simbolo()
					break
				elif simbolo != AnalizadorLexico.PUNTO_Y_COMA:
					self.out.write("Error Sintactico: Se esperaba un END o punto y coma (;) luego de una proposicion de un Begin\n")
					self.generador = self.generador.no_generar()
					if simbolo == AnalizadorLexico.ERROR_LEXICO or simbolo == AnalizadorLexico.EOF:
						break
					elif simbolo != AnalizadorLexico.COMA:
						self.scanner.frenar()
					
					
		elif valor.lower() == WRITE or valor.lower() == WRITELN:
			operador = valor.lower()
			simbolo = self.scanner.obtener_simbolo()
			if simbolo != AnalizadorLexico.ABRIR_PARENTESIS:
				if operador == WRITE:
					self.out.write("Error Sintactico: Se esperaba un parentesis luego de write \n")
					self.generador = self.generador.no_generar()
					self.scanner.frenar()
				else:
					self.generador.writeln()
					return desplazamiento
			simbolo = self.scanner.obtener_simbolo()
			if simbolo == AnalizadorLexico.CADENA:
				if self.scanner.error_en_cadena():
					self.generador = self.generador.no_generar()
				valor = self.scanner.obtener_valor_actual()
				self.generador.write(valor)
				simbolo = self.scanner.obtener_simbolo()
			else:
				desplazamiento = self._parsear_expresion(base, desplazamiento)
				self.generador.write()
				
				
			while self.scanner.obtener_tipo_actual() == AnalizadorLexico.COMA:
				simbolo = self.scanner.obtener_simbolo()
				if simbolo == AnalizadorLexico.CADENA:
					#hacemos algo con esto
					valor = self.scanner.obtener_valor_actual()
					self.generador.write(valor)
					simbolo = self.scanner.obtener_simbolo()
				else:
					desplazamiento = self._parsear_expresion(base, desplazamiento)
					self.generador.write()
				
			if self.scanner.obtener_tipo_actual() != AnalizadorLexico.CERRAR_PARENTESIS:
				self.out.write("Error Sintactico: Se esperaba un cierre de parentesis luego de write \n")
				self.generador = self.generador.no_generar()
			if operador == WRITELN: self.generador.writeln()
			simbolo = self.scanner.obtener_simbolo()	
			
		elif valor.lower() == READLN:
			simbolo = self.scanner.obtener_simbolo()
			if simbolo != AnalizadorLexico.ABRIR_PARENTESIS:
				self.out.write("Error Sintactico: Se esperaba un parentesis luego de readln \n")
				self.generador = self.generador.no_generar()
				self.scanner.frenar()
			simbolo = self.scanner.obtener_simbolo()
			if simbolo != AnalizadorLexico.IDENTIFICADOR:
				self.out.write("Error Sintactico: Se esperaba identificador dentro de readln \n")
				
			identificador = self.scanner.obtener_valor_actual()
			
			if not self.semantico.lectura_correcta(identificador, base, desplazamiento):
				if self.semantico.agregar_comodin(identificador, base, desplazamiento):
					desplazamiento += 1
				self.generador = self.generador.no_generar()
			
			self.generador.readln(self.semantico.obtener_valor(identificador, base, desplazamiento))
			
			simbolo = self.scanner.obtener_simbolo()
			while simbolo == AnalizadorLexico.COMA:
				simbolo = self.scanner.obtener_simbolo()
				identificador = self.scanner.obtener_valor_actual()
				if simbolo != AnalizadorLexico.IDENTIFICADOR:
					self.out.write("Error Sintactico: Se esperaba identificador dentro de readln \n")
					self.generador = self.generador.no_generar()
					self.scanner.frenar()
				self.generador.readln(self.semantico.obtener_valor(identificador, base, desplazamiento))
				simbolo = self.scanner.obtener_simbolo()
			if simbolo != AnalizadorLexico.CERRAR_PARENTESIS:
				self.out.write("Error Sintactico: Se esperaba cierre de parentesis luego de readln \n")
				self.generador = self.generador.no_generar()
				self.scanner.frenar()
			simbolo = self.scanner.obtener_simbolo()
		else:
			if simbolo != AnalizadorLexico.IDENTIFICADOR:
				self.out.write("Error Sintactico: Se esperaba variable en asignacion, se encuentra la palabra reservada: " + self.scanner.obtener_valor_actual() + "\n")
				self.scanner.obtener_simbolo()
				return desplazamiento 
			identificador = self.scanner.obtener_valor_actual()
			
			if not self.semantico.asignacion_correcta(identificador, base, desplazamiento):
				if self.semantico.agregar_comodin(identificador, base, desplazamiento):
					desplazamiento += 1
				self.generador = self.generador.no_generar()
			
			simbolo = self.scanner.obtener_simbolo()
			if simbolo != AnalizadorLexico.ASIGNACION:
				self.out.write("Error Sintactico: Esperada asignacion luego de variable\n")
				self.generador = self.generador.no_generar()
				
			simbolo = self.scanner.obtener_simbolo()
			desplazamiento = self._parsear_expresion(base, desplazamiento)
			self.generador.asignar(self.semantico.obtener_valor(identificador, base, desplazamiento))
			
		return desplazamiento
		
	def _parsear_condicion(self, base, desplazamiento):
		simbolo = self.scanner.obtener_tipo_actual()
		valor = self.scanner.obtener_valor_actual()
		if valor == ODD:
			simbolo = self.scanner.obtener_simbolo()
			desplazamiento = self._parsear_expresion(base, desplazamiento)
			self.generador.odd()
		else:
			self._parsear_expresion(base, desplazamiento)
			simbolo = self.scanner.obtener_tipo_actual()
			comparador = self.scanner.obtener_valor_actual()
			if simbolo == AnalizadorLexico.IGUAL or simbolo == AnalizadorLexico.MAYOR or simbolo == AnalizadorLexico.MAYOR_IGUAL or simbolo == AnalizadorLexico.MENOR or simbolo == AnalizadorLexico.MENOR_IGUAL or simbolo == AnalizadorLexico.DISTINTO:
				simbolo = self.scanner.obtener_simbolo()
				desplazamiento = self._parsear_expresion(base, desplazamiento)
			else:
				self.out.write("Error Sintactico: Se esperaba simbolo de comparacion en comparacion\n")
				self.generador = self.generador.no_generar()
				desplazamiento = self._parsear_expresion(base, desplazamiento)
			self.generador.comparar(comparador)
		return desplazamiento		
					
	def _parsear_expresion(self, base, desplazamiento):
		operador = None
		negar = False
		simbolo = self.scanner.obtener_tipo_actual()
		if simbolo == AnalizadorLexico.MAS or simbolo == AnalizadorLexico.MENOS:
			if simbolo == AnalizadorLexico.MENOS:
				negar = True
			simbolo = self.scanner.obtener_simbolo()
		while True:
			desplazamiento = self._parsear_termino(base, desplazamiento)
			
			if negar:
				negar = False
				self.generador.negar()
			if operador == AnalizadorLexico.MAS:
				self.generador.sumar()
			elif operador == AnalizadorLexico.MENOS:
				self.generador.restar()
			
			simbolo = self.scanner.obtener_tipo_actual()
			if simbolo == AnalizadorLexico.MAS or simbolo == AnalizadorLexico.MENOS:
				operador = simbolo
				simbolo = self.scanner.obtener_simbolo()
			else:
				return desplazamiento
				
	def _parsear_termino(self, base, desplazamiento):
		operador = None
		while True:
			desplazamiento = self._parsear_factor(base, desplazamiento)
			if operador == AnalizadorLexico.MULTIPLICAR:
				self.generador.multiplicar()
			elif operador == AnalizadorLexico.DIVIDIR:
				self.generador.dividir()
			simbolo = self.scanner.obtener_tipo_actual()
			if simbolo == AnalizadorLexico.MULTIPLICAR or simbolo == AnalizadorLexico.DIVIDIR:
				operador = simbolo
				simbolo = self.scanner.obtener_simbolo()
			else:
				return desplazamiento
				
	def _parsear_factor(self, base, desplazamiento):
		simbolo = self.scanner.obtener_tipo_actual()
		if simbolo == AnalizadorLexico.NUMERO:
			if self.scanner.numero_largo():
				self.generador = self.generador.no_generar()
			self.generador.factor_numero(self.scanner.obtener_valor_actual())
			simbolo = self.scanner.obtener_simbolo()
		elif simbolo == AnalizadorLexico.IDENTIFICADOR:
			identificador = self.scanner.obtener_valor_actual()
			if not self.semantico.factor_correcto(identificador, base, desplazamiento):
				if self.semantico.agregar_comodin(identificador, base, desplazamiento):
					desplazamiento += 1
				self.generador = self.generador.no_generar()
			if self.semantico.obtener_tipo(identificador, base, desplazamiento) == AnalizadorSemantico.CONSTANTE:
				self.generador.factor_numero(self.semantico.obtener_valor(identificador, base, desplazamiento))
			else: #Variable
				self.generador.factor_variable(self.semantico.obtener_valor(identificador, base, desplazamiento))
			simbolo = self.scanner.obtener_simbolo()			
		elif simbolo == AnalizadorLexico.ABRIR_PARENTESIS:
			simbolo = self.scanner.obtener_simbolo()
			self._parsear_expresion(base, desplazamiento)
			simbolo = self.scanner.obtener_tipo_actual()
			if simbolo == AnalizadorLexico.CERRAR_PARENTESIS:
				simbolo = self.scanner.obtener_simbolo()
			else:
				self.out.write("Error Sintactico: Cierre de parentesis faltante\n")
				self.generador = self.generador.no_generar()
				#self.scanner.frenar()
		else:
			valor = self.scanner.obtener_valor_actual()
			self.out.write("Error Sintactico: Simbolo no esperado: " + valor if valor is not None else simbolo + "\n")
			self.generador = self.generador.no_generar()
		return desplazamiento
			
	def parsear_programa(self):
		self._parsear_bloque()
		simbolo = self.scanner.obtener_tipo_actual()
		if simbolo != AnalizadorLexico.PUNTO:
			self.out.write("Error Sintactico: Se esperaba punto (.) de finalizacion de programa\n")
			self.generador = self.generador.no_generar()
		self.generador.finalizar(self.semantico.obtener_cantidad_variables())
		
