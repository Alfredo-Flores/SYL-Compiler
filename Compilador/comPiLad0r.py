#!/usr/bin/python
import sys
import AnalizadorLexico as lexico
import AnalizadorSemantico as semantico
import AnalizadorSintactico as sintactico

if __name__ == "__main__":
	output = open("salida.txt", "w")
	ruta = "Archivos/BIEN-00.PL0"
	ejec = "ejec"
	
	al = lexico.AnalizadorLexico(ruta, output)
	an_sem = semantico.AnalizadorSemantico(output)
	an_sintac = sintactico.AnalizadorSintactico(al, an_sem, output)
	an_sintac.parsear_programa()

	# respuesta = str(input("Quieres ver el Analisis Lexico? (S/N)"))
	# if respuesta[0].lower() == 's':
	# 	alALT = lexico.AnalizadorLexico(ruta, output)
	# 	while True:
	# 		c = alALT.obtener_simbolo()
	# 		if c == lexico.EOF: break
	# 		print(c)
	#
	# respuesta = str(input("Quieres ver el Analisis Sintactico? (S/N)"))






	output.close()
