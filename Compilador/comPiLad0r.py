import AnalizadorLexico as lexico
import AnalizadorSemantico as semantico
import AnalizadorSintactico as sintactico
import CodigoIntermedio as generador

if __name__ == "__main__":
	output = open("salida.txt", "w")
	ruta = "Archivos/BIEN-00.syl"
	
	al = lexico.AnalizadorLexico(ruta, output)
	an_sem = semantico.AnalizadorSemantico(output)
	gen_cod = generador.CodigoIntermedio()

	an_sintac = sintactico.AnalizadorSintactico(al, an_sem, gen_cod, output)
	an_sintac.parsear_programa()

	output.close()
