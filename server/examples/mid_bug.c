int mid( int x, int y, int z )
{
    int m;
    m=z;
    if(y<z){
        if(x<y)
            m=y;
        else if(x<z)
            m=y;  //Bug
    }
    else{
        if(x>y)
            m=y;
        else if(x>z)
            m=x;
    } 
    return m;
}
int max( int x)
{
    return x;
}
