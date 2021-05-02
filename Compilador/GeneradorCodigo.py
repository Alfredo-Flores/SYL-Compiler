import os
import stat
import header_fix

BYTES_POR_VARIABLE = 4
COMPLEMENTO = 2**32 
POS_RUTINA_SALIDA = 768
POS_RUTINA_IMPR_NUMEROS = 400
POS_RUTINA_IMPR_CADENA = 368
POS_RUTINA_SALTO_LINEA = 384
POS_RUTINA_LECTURA = 784
EDI = 0xbf
EDI_INICIAL = [0x0, 0x0,0x0, 0x0]
PUSH_EAX = 0x50
MOV_EAX_CONS = [0xb8]
MOV_ECX_CONS = [0xb9]
MOV_EDX_CONS = [0xba]
MOV_EAX_VAR = [0x8B, 0x87]
POP_EAX = 0x58
POP_EBX = 0x5B
IMUL_EBX = [0xF7, 0xEB]
DIVISION = [0x93, 0x99, 0xF7, 0xFB] #93 99?
NEG_EAX = [0xF7, 0xD8]
ADD = [0x01, 0xD8]
SUB = [0x93, 0x29, 0xD8] #no se para que el 93
JMP = [0xe9]
MOV_VAR = [0x89, 0x87]
ODD = [0xA8, 0x01, 0x7B, 0x05]
CMP_EAX_EBX = [0x39, 0xc3]
COD_CMP = lambda x: [{"<": 0x7c, ">": 0x7f, "=": 0x74, ">=": 0x7d, "<=": 0x7e, "<>": 0x75}[x]] + [0x05]
CALL = [0xe8]
RETURN = 0xc3

POSICION_FILESIZE = 68
POSICION_MEMORYSIZE = 72
POSICION_SIZE = 201
TAM_HEADER = 224

def traduce(hexas):
	return reduce(lambda x,y: x + chr(y) ,hexas, "")
	
def endian(numero):
	hexa = str(hex(numero))[2:]
	hexa = reduce(lambda x,y: x+y, ["0" for i in range(8 - len(hexa))], "") + hexa
	hexa = [hexa[i*2] + hexa[i*2 +1] for i in range(4)]
	hexa.reverse()
	return map(lambda x: int(x, 16), hexa)
	
def salto(adonde, donde_estoy):
	return COMPLEMENTO + adonde - donde_estoy

class GeneradorLinux(object):
	def __init__(self, ruta_ejec):
		self.ruta = ruta_ejec
		self.ejecutable = open(ruta_ejec, "w")
		self.buffer = ""
		self.stack = []
		self.stack_while = []
		self.stack_bloques = []
		self._agregar_header()
		self._edi_inicial()
	
	
	def _flush(self):
		self.ejecutable.write(self.buffer)
		#self.buffer = ""
	
	def _agregar_header(self):
		self.buffer += header_fix.HEADER
	
	def _edi_inicial(self):
		self.pos_edi = len(self.buffer) - 1
		self.buffer += traduce([EDI] + EDI_INICIAL)
	
	def no_generar(self):
		self.ejecutable.close()
		os.remove(self.ruta)
		return GeneradorNulo()
	
	def finalizar(self, cant_variables):
		#Pongo jum de salida de prograa
		self.buffer += traduce(JMP + endian(salto(POS_RUTINA_SALIDA ,len(self.buffer) + 5)))
		#Modifico el edi
		self.buffer = self.buffer[:self.pos_edi + 1] + traduce([EDI] + endian(header_fix.VIRTUAL_ADDRESS + len(self.buffer))) + self.buffer[self.pos_edi + 6:]
		#agrego los 0s para cada variable
		self.buffer += traduce([0 for i in range(cant_variables * BYTES_POR_VARIABLE)])
		#Pongo en filesize y memory size el valor del tam del archivo
		self.buffer = self.buffer[0: POSICION_FILESIZE] + traduce(endian(len(self))) + self.buffer[POSICION_FILESIZE + 4:]
		self.buffer = self.buffer[0: POSICION_MEMORYSIZE] + traduce(endian(len(self))) + self.buffer[POSICION_MEMORYSIZE + 4:]
		#Pongo en size el tam de la porcion text
		self.buffer = self.buffer[0: POSICION_SIZE] + traduce(endian(len(self) - TAM_HEADER)) + self.buffer[POSICION_SIZE + 4:]
		#guardo
		self._flush()
		self.ejecutable.close()
		st = os.stat(self.ruta)
		os.chmod(self.ruta, st.st_mode | stat.S_IEXEC)
	
	def _push_eax(self):
		self.buffer += chr(PUSH_EAX)
		
	def _pop_eax(self):
		#Optimizacion de push-pop
		if ord(self.buffer[-1]) == PUSH_EAX:
			self.buffer = self.buffer[:-1]
		else:
			self.buffer += chr(POP_EAX)
	
	def factor_numero(self, valor):
		valor = int(valor)
		self.buffer += traduce(MOV_EAX_CONS + endian(valor))
		self._push_eax()
	
	def factor_variable(self, num_var):
		self.buffer += traduce(MOV_EAX_VAR + endian(BYTES_POR_VARIABLE * num_var))
		self._push_eax()
		
	def multiplicar(self):
		self._pop_eax()
		self.buffer += traduce([POP_EBX] + IMUL_EBX)
		self._push_eax()
		
	def dividir(self):
		self._pop_eax()
		self.buffer += traduce([POP_EBX] + DIVISION)
		self._push_eax()
		
	def negar(self):
		self._pop_eax()
		self.buffer += traduce(NEG_EAX)
		self._push_eax()
	
	def sumar(self):
		self._pop_eax()
		self.buffer += traduce([POP_EBX] + ADD)
		self._push_eax()
	
	def restar(self):
		self._pop_eax()
		self.buffer += traduce([POP_EBX] + SUB)
		self._push_eax()
	
	def asignar(self, numero_var):
		self._pop_eax()
		self.buffer += traduce(MOV_VAR + endian(BYTES_POR_VARIABLE * numero_var))
	
	def write(self, valor=None):
		if valor is None:
			#Valor desde expresion
			self._pop_eax()
			self.buffer += traduce(CALL + endian(salto(POS_RUTINA_IMPR_NUMEROS,(len(self.buffer) + 5))))
		else:
			#Valor desde cadena
			offset = 20
			self.buffer += traduce(MOV_ECX_CONS + endian(header_fix.ADDR - 0xe0 + len(self.buffer) + offset)) #revisar
			self.buffer += traduce(MOV_EDX_CONS + endian(len(valor)))
			self.buffer += traduce(CALL + endian(salto(POS_RUTINA_IMPR_CADENA, len(self.buffer) + 5)))
			self.buffer += traduce(JMP + endian(len(valor) + 1))
			self.buffer += valor + chr(0)		
	
	def writeln(self):
		self.buffer += traduce(CALL + endian(salto(POS_RUTINA_SALTO_LINEA ,(len(self.buffer) + 5))))
		
	def odd(self):
		self._pop_eax()
		self.buffer += traduce (ODD)
		self.buffer += traduce(JMP + [0x0, 0x0, 0x0, 0x0])
		self.stack.append(len(self.buffer))
	
	def comparar(self, comparador):
		self._pop_eax()
		self.buffer += traduce([POP_EBX] + CMP_EAX_EBX + COD_CMP(comparador))
		self.buffer += traduce(JMP + [0x0, 0x0, 0x0, 0x0])
		self.stack.append(len(self.buffer))
	
	def corregir_condicion(self):
		long_ult = self.stack.pop()
		long_actual = len(self.buffer)
		distancia = long_actual - long_ult
		self.buffer = self.buffer[0: long_ult - 5] + traduce(JMP + endian(distancia)) + self.buffer[long_ult:]
	
	def recordar_while(self):
		self.stack_while.append(len(self.buffer))
	
	def salto_while(self):
		pos_while = self.stack_while.pop()
		self.buffer += traduce(JMP + endian(salto(pos_while, len(self.buffer) + 5)))
		
	def readln(self, numero_var):
		self.buffer += traduce(CALL + endian(salto(POS_RUTINA_LECTURA ,len(self.buffer) + 5)))
		self.buffer += traduce(MOV_VAR + endian(BYTES_POR_VARIABLE * numero_var))
	
	def call(self, posicion):
		self.buffer += traduce(CALL + endian(salto(posicion, len(self.buffer) + 5)))
	
	def marcar_bloque(self):
		self.buffer += traduce(JMP + [0x0 for i in range(4)])
		self.stack_bloques.append(len(self))
	
	def corregir_bloque(self):
		pos_bloque = self.stack_bloques.pop()
		distancia = len(self.buffer) - int(pos_bloque)
		#optimizacion de saltos de distancia 0
		if distancia == 0:
			self.buffer = self.buffer[0: pos_bloque - 5] + self.buffer[pos_bloque + 5:]
		else:
			self.buffer = self.buffer[0: pos_bloque - 4] + traduce(endian(distancia)) + self.buffer[pos_bloque:]
	
	def agregar_return(self):
		self.buffer += traduce([RETURN])
	
	def __len__(self):
		return len(self.buffer)
		
	def __str__(self):
		return reduce(lambda x,y: x + " " + y, map(lambda x: hex(ord(x))[2:], self.buffer), "")



class GeneradorNulo(object):
	def __init__(self): pass	
	def no_generar(self): return self
	def factor_numero(self, valor): pass 
	def factor_variable(self, num_var): pass
	def multiplicar(self): pass
	def dividir(self): pass
	def negar(self): pass
	def sumar(self): pass
	def restar(self): pass
	def asignar(self, numero_var): pass
	def write(self, valor=None): pass
	def writeln(self, valor=None): pass		
	def odd(self): pass	
	def comparar(self, comparador): pass	
	def corregir_condicion(self): pass	
	def recordar_while(self): pass
	def salto_while(self): pass		
	def readln(self, numero_var): pass	
	def call(self, posicion): pass
	def marcar_bloque(self): pass
	def corregir_bloque(self): pass
	def agregar_return(self): pass
	def __len__(self): return 0
	def finalizar(self, cant_variables):
		print "No se genero archivo ejecutable por encontrarse al menos un error"
