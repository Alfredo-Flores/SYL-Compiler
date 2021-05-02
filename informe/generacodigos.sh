for i in 0 1 2 3 4 5 6 7 8 9
do
	`./../Compilador/comPiLad0r.py Archivos/BIEN-0$i.PL0 text/BIEN-0$i`
	`objdump -M intel -D text/BIEN-0$i > text/BIEN-0$i.txt`
	`hexdump text/BIEN-0$i > hexa/BIEN-0$i.txt`
	`rm text/BIEN-0$i`
done
