#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int memory(int size)
{
   int *pointer = &size;
   printf("The result if %d", *(++pointer) );// Memory error
}
