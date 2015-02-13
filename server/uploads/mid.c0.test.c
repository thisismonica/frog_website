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
	unsigned int a0;
	klee_make_symbolic(&a0,sizeof(a0),"a0");
	unsigned int a1;
	klee_make_symbolic(&a1,sizeof(a1),"a1");
	int a2;
	klee_make_symbolic(&a2,sizeof(a2),"a2");
	unsigned int result=mid(a0,a1,a2);
	return;
}