import AnalizadorLexico as lexico
import AnalizadorSemantico as semantico
import AnalizadorSintactico as sintactico
import CodigoIntermedio as generador

if __name__ == "__main__":
	output = open("salida.txt", "w")
	ruta = "fuente.syl"
	
	al = lexico.AnalizadorLexico(ruta, output)
	an_sem = semantico.AnalizadorSemantico(output)
	gen_cod = generador.CodigoIntermedio()

	an_sintac = sintactico.AnalizadorSintactico(al, an_sem, gen_cod, output)
	an_sintac.parsear_programa()

	output.close()

	input("\nCompilacion exitosa, revise las tablas y revisa salida.txt para saber si hay alguna anomalia\n\nPresione ENTER para salir\n")

