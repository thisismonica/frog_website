unsigned int mid( unsigned int x, unsigned int y, int z )
{
    int m;
    m=z;
    if(y<z)
        if(x<y)
            m=y;
        else if(x<z)
            m=y;
        else if(x>y)
            m=y;
        else if(x>z)
            m=x;
    return m;
}
int max( int x)
{
    return x;
}

#include "klee.h"
int main() {
	int a0;
	klee_make_symbolic(&a0,sizeof(a0),"a0");
	int result=max(a0);
	return;
}