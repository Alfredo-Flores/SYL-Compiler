import AnalizadorLexico
import AnalizadorSemantico
import CodigoIntermedio

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
        self.op1 = None
        self.op2 = None
        self.operador = None

    def _parsear_bloque(self, base=0):
        desplazamiento = 0
        simbolo = self.scanner.obtener_simbolo()
        valor = self.scanner.obtener_valor_actual()

        # Analizamos la parte de constantes:
        if simbolo == AnalizadorLexico.RESERVADA and valor.lower() == CONST:
            while True:
                simbolo = self.scanner.obtener_simbolo()
                if simbolo == AnalizadorLexico.IDENTIFICADOR:
                    identificador = self.scanner.obtener_valor_actual()
                    simbolo = self.scanner.obtener_simbolo()
                    if simbolo != AnalizadorLexico.IGUAL:
                        self.out.write("Error Sintactico: asignacion de constante esperada (=)\n")
                        self.detener_programa()

                    simbolo = self.scanner.obtener_simbolo()
                    if self.semantico.validar_identificador(simbolo, AnalizadorLexico.NUMERO):
                        self.out.write("Error Sintactico: asignacion de constante a un valor no numerico\n")
                        self.detener_programa()

                    try:
                        self.semantico.agregar_identificador(base, desplazamiento, identificador,
                                                             AnalizadorSemantico.CONSTANTE,
                                                             self.scanner.obtener_valor_actual())
                        desplazamiento += 1

                        self.generador.pila_operandos.append(self.scanner.obtener_valor_actual())
                        self.generador.pila_operandos.append(identificador)
                        self.generador.pila_operadores.append(AnalizadorLexico.ASIGNACION)
                        self.generador.generarCodigo()
                    except:
                        self.out.write("exepcion\n")
                    simbolo = self.scanner.obtener_simbolo()
                    if simbolo == AnalizadorLexico.PUNTO_Y_COMA:
                        simbolo = self.scanner.obtener_simbolo()
                        break
                    elif simbolo != AnalizadorLexico.COMA:
                        self.out.write(
                            "Error Sintactico: Se esperaba punto y coma (;) o coma (,) luego de declaracion de constante\n")
                        self.detener_programa()

                else:
                    self.out.write("Error Sintactico: declaracion de constante no seguida de un identificador\n")
                    self.detener_programa()
                    break

        valor = self.scanner.obtener_valor_actual()
        # Analizamos la parte de Variables:
        if simbolo == AnalizadorLexico.RESERVADA and valor.lower() == VAR:
            while True:
                simbolo = self.scanner.obtener_simbolo()
                if simbolo == AnalizadorLexico.IDENTIFICADOR:
                    identificador = self.scanner.obtener_valor_actual()
                    try:
                        self.semantico.agregar_identificador(base, desplazamiento, identificador,
                                                             AnalizadorSemantico.VARIABLE)
                        desplazamiento += 1
                    except:
                        self.out.write("Error Semantico: Variable Duplicada\n")
                        self.detener_programa()

                else:
                    self.out.write("Error Sintactico: declaracion de variable no seguida de un identificador\n")
                    self.detener_programa()

                simbolo = self.scanner.obtener_simbolo()
                if simbolo == AnalizadorLexico.PUNTO_Y_COMA:
                    simbolo = self.scanner.obtener_simbolo()
                    break
                elif simbolo != AnalizadorLexico.COMA:
                    self.out.write(
                        "Error Sintactico: Se esperaba punto y coma (;) o coma (,) luego de declaracion de variable\n")
                    self.detener_programa()

        # Analizamos la parte de Procedimientos:
        while simbolo == AnalizadorLexico.RESERVADA and self.scanner.obtener_valor_actual().lower() == PROCEDURE:
            simbolo = self.scanner.obtener_simbolo()
            if simbolo != AnalizadorLexico.IDENTIFICADOR:
                self.out.write("Error Sintactico: declaracion de procedimiento no seguida de un identificador\n")
                self.detener_programa()
                continue
            identificador = self.scanner.obtener_valor_actual()
            try:
                self.semantico.agregar_identificador(base, desplazamiento, identificador,
                                                     AnalizadorSemantico.PROCEDIMIENTO)
                desplazamiento += 1
            except:
                self.out.write("identificador largo\n")
                continue

            simbolo = self.scanner.obtener_simbolo()
            if simbolo != AnalizadorLexico.PUNTO_Y_COMA:
                self.out.write(
                    "Error Sintactico: Luego de la identificacion de un procedimiento se esperaba por punto y coma (;)\n")
                self.detener_programa()

            self._parsear_bloque(base + desplazamiento)

            if self.scanner.obtener_tipo_actual() != AnalizadorLexico.PUNTO_Y_COMA:
                self.out.write("Error Sintactico: Luego de definir un procedimiento se esperaba por punto y coma (;)\n")
                self.detener_programa()
                continue
            simbolo = self.scanner.obtener_simbolo()

        # Seguimos el diagrama de proposicion:
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
                if self.semantico.agregar_comodin(identificador, base, desplazamiento):
                    desplazamiento += 1
            simbolo = self.scanner.obtener_simbolo()

        elif valor.lower() == IF:
            simbolo = self.scanner.obtener_simbolo()
            desplazamiento = self._parsear_condicion(base, desplazamiento)
            simbolo = self.scanner.obtener_tipo_actual()

            self.generador.generarSaltoEnFalso()

            if simbolo == AnalizadorLexico.RESERVADA and self.scanner.obtener_valor_actual().lower() == THEN:
                simbolo = self.scanner.obtener_simbolo()
                desplazamiento = self._parsear_proposicion(base, desplazamiento)
                self.generador.rellenarSaltoEnFalso()
            else:
                self.out.write("Error Sintactico: Se esperaba un 'then' luego de la condicion de un 'if'\n")
                self.detener_programa()
        elif valor.lower() == WHILE:
            self.generador.generarSalto()

            simbolo = self.scanner.obtener_simbolo()
            desplazamiento = self._parsear_condicion(base, desplazamiento)
            simbolo = self.scanner.obtener_tipo_actual()

            self.generador.generarSaltoEnFalso()

            if not (simbolo == AnalizadorLexico.RESERVADA and self.scanner.obtener_valor_actual().lower() == DO):
                self.out.write("Error Sintactico: Se esperaba un 'do' luego de la condicion de un 'while'\n")

                if not (simbolo == AnalizadorLexico.RESERVADA and self.scanner.obtener_valor_actual().lower() == THEN):
                    self.detener_programa()
            simbolo = self.scanner.obtener_simbolo()
            desplazamiento = self._parsear_proposicion(base, desplazamiento)
            self.generador.rellenarSaltoEnFalso()
            self.generador.generarSaltoIncondicional()

        elif valor.lower() == BEGIN:
            while True:
                simbolo = self.scanner.obtener_simbolo()
                desplazamiento = self._parsear_proposicion(base, desplazamiento)
                simbolo = self.scanner.obtener_tipo_actual()
                if simbolo == AnalizadorLexico.RESERVADA and self.scanner.obtener_valor_actual().lower() == END:
                    simbolo = self.scanner.obtener_simbolo()
                    break
                elif simbolo != AnalizadorLexico.PUNTO_Y_COMA:
                    self.out.write(
                        "Error Sintactico: Se esperaba un END o punto y coma (;) luego de una proposicion de un Begin\n")
                    if simbolo == AnalizadorLexico.ERROR_LEXICO or simbolo == AnalizadorLexico.EOF:
                        break
                    elif simbolo != AnalizadorLexico.COMA:
                        self.detener_programa()


        elif valor.lower() == WRITE or valor.lower() == WRITELN:
            operador = valor.lower()
            simbolo = self.scanner.obtener_simbolo()
            if simbolo != AnalizadorLexico.ABRIR_PARENTESIS:
                if operador == WRITE:
                    self.out.write("Error Sintactico: Se esperaba un parentesis luego de write \n")
                    self.detener_programa()
                else:
                    return desplazamiento
            simbolo = self.scanner.obtener_simbolo()
            if simbolo == AnalizadorLexico.CADENA:
                valor = self.scanner.obtener_valor_actual()
                simbolo = self.scanner.obtener_simbolo()
            else:
                desplazamiento = self._parsear_expresion(base, desplazamiento)

            while self.scanner.obtener_tipo_actual() == AnalizadorLexico.COMA:
                simbolo = self.scanner.obtener_simbolo()
                if simbolo == AnalizadorLexico.CADENA:
                    # hacemos algo con esto
                    valor = self.scanner.obtener_valor_actual()
                    simbolo = self.scanner.obtener_simbolo()
                else:
                    desplazamiento = self._parsear_expresion(base, desplazamiento)

            if self.scanner.obtener_tipo_actual() != AnalizadorLexico.CERRAR_PARENTESIS:
                self.out.write("Error Sintactico: Se esperaba un cierre de parentesis luego de write \n")
                self.detener_programa()
            simbolo = self.scanner.obtener_simbolo()


        elif valor.lower() == READLN:
            simbolo = self.scanner.obtener_simbolo()
            if simbolo != AnalizadorLexico.ABRIR_PARENTESIS:
                self.out.write("Error Sintactico: Se esperaba un parentesis luego de readln \n")
                self.detener_programa()
            simbolo = self.scanner.obtener_simbolo()
            if simbolo != AnalizadorLexico.IDENTIFICADOR:
                self.out.write("Error Sintactico: Se esperaba identificador dentro de readln \n")
                self.detener_programa()
            identificador = self.scanner.obtener_valor_actual()

            if not self.semantico.lectura_correcta(identificador, base, desplazamiento):
                if self.semantico.agregar_comodin(identificador, base, desplazamiento):
                    desplazamiento += 1

            simbolo = self.scanner.obtener_simbolo()
            while simbolo == AnalizadorLexico.COMA:
                simbolo = self.scanner.obtener_simbolo()
                identificador = self.scanner.obtener_valor_actual()
                if simbolo != AnalizadorLexico.IDENTIFICADOR:
                    self.out.write("Error Sintactico: Se esperaba identificador dentro de readln \n")
                    self.detener_programa()
                simbolo = self.scanner.obtener_simbolo()
            if simbolo != AnalizadorLexico.CERRAR_PARENTESIS:
                self.out.write("Error Sintactico: Se esperaba cierre de parentesis luego de readln \n")
                self.detener_programa()
            simbolo = self.scanner.obtener_simbolo()
        else:
            if simbolo != AnalizadorLexico.IDENTIFICADOR:
                self.out.write(
                    "Error Sintactico: Se esperaba variable en asignacion, se encuentra la palabra reservada: " + self.scanner.obtener_valor_actual() + "\n")
                self.scanner.obtener_simbolo()
                self.detener_programa()
                return desplazamiento
            identificador = self.scanner.obtener_valor_actual()

            if not self.semantico.asignacion_correcta(identificador, base, desplazamiento):
                if self.semantico.agregar_comodin(identificador, base, desplazamiento):
                    desplazamiento += 1

            simbolo = self.scanner.obtener_simbolo()
            if simbolo != AnalizadorLexico.ASIGNACION:
                self.out.write("Error Sintactico: Esperada asignacion luego de variable\n")
                self.detener_programa()
            simbolo = self.scanner.obtener_simbolo()
            desplazamiento = self._parsear_expresion(base, desplazamiento)

            self.generador.pila_operandos.append(identificador)
            self.generador.pila_operadores.append(AnalizadorLexico.ASIGNACION)
            self.generador.generarCodigo()

        return desplazamiento

    def _parsear_condicion(self, base, desplazamiento):
        simbolo = self.scanner.obtener_tipo_actual()
        valor = self.scanner.obtener_valor_actual()
        if valor == ODD:
            simbolo = self.scanner.obtener_simbolo()
            desplazamiento = self._parsear_expresion(base, desplazamiento)
        else:
            self._parsear_expresion(base, desplazamiento)
            simbolo = self.scanner.obtener_tipo_actual()
            comparador = self.scanner.obtener_valor_actual()
            if simbolo == AnalizadorLexico.IGUAL or simbolo == AnalizadorLexico.MAYOR or simbolo == AnalizadorLexico.MAYOR_IGUAL or simbolo == AnalizadorLexico.MENOR or simbolo == AnalizadorLexico.MENOR_IGUAL or simbolo == AnalizadorLexico.DISTINTO:

                if simbolo == AnalizadorLexico.IGUAL:
                    self.generador.pila_operadores.append(AnalizadorLexico.IGUAL)
                elif simbolo == AnalizadorLexico.MAYOR:
                    self.generador.pila_operadores.append(AnalizadorLexico.MAYOR)
                elif simbolo == AnalizadorLexico.MAYOR_IGUAL:
                    self.generador.pila_operadores.append(AnalizadorLexico.MAYOR_IGUAL)
                elif simbolo == AnalizadorLexico.MENOR:
                    self.generador.pila_operadores.append(AnalizadorLexico.MENOR)
                elif simbolo == AnalizadorLexico.DISTINTO:
                    self.generador.pila_operadores.append(AnalizadorLexico.DISTINTO)

                simbolo = self.scanner.obtener_simbolo()
                desplazamiento = self._parsear_expresion(base, desplazamiento)
            else:
                self.out.write("Error Sintactico: Se esperaba simbolo de comparacion en comparacion\n")
                self.detener_programa()
                desplazamiento = self._parsear_expresion(base, desplazamiento)
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
                # self.out.write("Negar\n")
            if operador == AnalizadorLexico.MAS:
                self.generador.pila_operadores.append(AnalizadorLexico.MAS)
                # self.out.write("Mas\n")
            elif operador == AnalizadorLexico.MENOS:
                self.generador.pila_operadores.append(AnalizadorLexico.MENOS)
                # self.out.write("Menos\n")

            simbolo = self.scanner.obtener_tipo_actual()

            if len(self.generador.pila_operandos) > 1 and len(self.generador.pila_operadores) > 0 and \
                    self.generador.pila_operadores[
                        len(self.generador.pila_operadores) - 1] != AnalizadorLexico.ASIGNACION:
                self.generador.generarCodigo()

            if simbolo == AnalizadorLexico.MAS or simbolo == AnalizadorLexico.MENOS:
                operador = simbolo
                simbolo = self.scanner.obtener_simbolo()
            else:
                return desplazamiento

    def _parsear_termino(self, base, desplazamiento):
        operador = None
        banderaSeguimiento = False
        while True:
            desplazamiento = self._parsear_factor(base, desplazamiento)
            if operador == AnalizadorLexico.MULTIPLICAR:
                self.operador = AnalizadorLexico.MULTIPLICAR
                self.generador.pila_operadores.append(AnalizadorLexico.MULTIPLICAR)
                # self.out.write("Multiplicar\n")
            elif operador == AnalizadorLexico.DIVIDIR:
                self.operador = AnalizadorLexico.DIVIDIR
                self.generador.pila_operadores.append(AnalizadorLexico.DIVIDIR)
                # self.out.write("Dividir\n")
            simbolo = self.scanner.obtener_tipo_actual()

            if len(self.generador.pila_operandos) > 1 and len(self.generador.pila_operadores) > 0:
                self.generador.generarCodigo()

            if simbolo == AnalizadorLexico.MULTIPLICAR or simbolo == AnalizadorLexico.DIVIDIR:
                operador = simbolo
                simbolo = self.scanner.obtener_simbolo()
            else:
                return desplazamiento

    def _parsear_factor(self, base, desplazamiento):
        simbolo = self.scanner.obtener_tipo_actual()
        if simbolo == AnalizadorLexico.NUMERO:
            self.generador.pila_operandos.append(self.scanner.obtener_valor_actual())
            simbolo = self.scanner.obtener_simbolo()

        elif simbolo == AnalizadorLexico.IDENTIFICADOR:
            identificador = self.scanner.obtener_valor_actual()
            if not self.semantico.factor_correcto(identificador, base, desplazamiento):
                if self.semantico.agregar_comodin(identificador, base, desplazamiento):
                    desplazamiento += 1
            if self.semantico.obtener_tipo(identificador, base, desplazamiento) == AnalizadorSemantico.CONSTANTE:
                self.generador.pila_operandos.append(identificador)

                # self.out.write("Constante\n")
            else:
                self.generador.pila_operandos.append(identificador)

                # self.out.write("Variable\n")
            simbolo = self.scanner.obtener_simbolo()
        elif simbolo == AnalizadorLexico.ABRIR_PARENTESIS:
            simbolo = self.scanner.obtener_simbolo()
            self._parsear_expresion(base, desplazamiento)
            simbolo = self.scanner.obtener_tipo_actual()
            if simbolo == AnalizadorLexico.CERRAR_PARENTESIS:
                simbolo = self.scanner.obtener_simbolo()
            else:
                self.out.write("Error Sintactico: Cierre de parentesis faltante\n")
                self.detener_programa()
        else:
            valor = self.scanner.obtener_valor_actual()
            self.out.write("Error Sintactico: Simbolo no esperado: " + valor if valor is not None else simbolo + "\n")
        return desplazamiento

    def detener_programa(self):
        print("Ocurrio un error en la compilaion, revise el archivo salida.txt para ver el error")
        exit()

    def parsear_programa(self):
        self._parsear_bloque()
        simbolo = self.scanner.obtener_tipo_actual()
        if simbolo != AnalizadorLexico.PUNTO:
            self.out.write("Error Sintactico: Se esperaba punto (.) de finalizacion de programa\n")
        self.semantico.print_code()
        self.generador.print_code()
