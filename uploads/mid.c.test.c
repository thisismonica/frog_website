int mid( int x, int y, int z )
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
int min( int x)
{
    return x;
}
#include "klee.h"
#include "ansi_prefix.PPCEABI.bare.h"
int main() {
	int a0;
	klee_make_symbolic(&a0,sizeof(a0),"a0");
	int a1;
	klee_make_symbolic(&a1,sizeof(a1),"a1");
	int a2;
	klee_make_symbolic(&a2,sizeof(a2),"a2");
	int result=mid(a0,a1,a2);
	return;
}