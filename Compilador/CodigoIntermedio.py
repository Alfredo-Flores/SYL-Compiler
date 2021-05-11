import AnalizadorLexico

class CodigoIntermedio:
    def __init__(self):
        self.cuadruplos = []
        self.tempVarCount = 0
        self.pila_operadores = []
        self.pila_operandos = []
        self.pila_saltos = []

    def generateCode(self, operation, arg1, arg2, result):
        code = list([operation, arg1, arg2, result])
        self.cuadruplos.append(code)

    def print_code(self):
        listaFinal = []
        for linea, cuadruplo in enumerate(self.cuadruplos):
            listaFinal.append([linea, cuadruplo[0],  cuadruplo[1],  cuadruplo[2], cuadruplo[3]])

        header = ("No.", "Operador", "Operando 1", "Operando 2", "Resultado")
        widths = [len(cell) for cell in header]
        for row in listaFinal:
            for i, cell in enumerate(row):
                widths[i] = max(len(str(cell)), widths[i])

        formatted_row = ' '.join('{:%d}' % width for width in widths)

        print(formatted_row.format(*header))
        for row in listaFinal:
            print(formatted_row.format(*row))


    def generarCodigo(self):
        indice_operador = len(self.pila_operadores) - 1
        indice_operando = len(self.pila_operandos) - 1

        if self.pila_operadores[indice_operador] == AnalizadorLexico.ASIGNACION:
            self.generateCode(self.pila_operadores[indice_operador], self.pila_operandos[indice_operando - 1], '', self.pila_operandos[indice_operando])
            self.pila_operadores.pop()
            self.pila_operandos.pop()
            self.pila_operandos.pop()

        elif self.pila_operadores[indice_operador] in [AnalizadorLexico.MAS, AnalizadorLexico.MENOS, AnalizadorLexico.MULTIPLICAR, AnalizadorLexico.DIVIDIR, AnalizadorLexico.IGUAL, AnalizadorLexico.MAYOR, AnalizadorLexico.MAYOR_IGUAL, AnalizadorLexico.MENOR, AnalizadorLexico.MENOR_IGUAL, AnalizadorLexico.DISTINTO]:
            self.tempVarCount += 1
            temp = 'R' + str(self.tempVarCount)

            self.generateCode(self.pila_operadores[indice_operador], self.pila_operandos[indice_operando - 1], self.pila_operandos[indice_operando], temp)

            self.pila_operadores.pop()
            self.pila_operandos.pop()
            self.pila_operandos.pop()

            self.pila_operandos.append(temp)

    def generarSaltoEnFalso(self):
        indice_operando = len(self.pila_operandos) - 1

        self.generateCode("SF", self.pila_operandos[indice_operando], '', '')

        self.pila_operandos.pop()

    def rellenarSaltoEnFalso(self):
        cuadruplo_actual = len(self.cuadruplos)

        indexes = [i for i, cuadruplo in enumerate(self.cuadruplos) if cuadruplo[0] == "SF" and cuadruplo[3] == '']

        self.cuadruplos[indexes[-1]][3] = cuadruplo_actual

    def generarSalto(self):
        self.pila_saltos.append(len(self.cuadruplos))

    def generarSaltoIncondicional(self):
        self.generateCode("SI", '', '', self.pila_saltos[-1])