"g++.exe" -Wall  -Wmaybe-uninitialized -O -ansi -pedantic -shared et1255.cpp -o libet1255.so -lsetupapi 
"g++.exe" -c et1255_dll_test.cpp
"g++.exe" -o et1255_dll_test.exe et1255_dll_test.o libet1255.so