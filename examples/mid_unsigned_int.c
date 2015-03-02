unsigned int mid( unsigned int x, unsigned int y, unsigned int z )
{
    unsigned int m;
    m=z;
    if(y<z){
        if(x<y)
            m=y;
        else if(x<z)
            m=y;
    }
    else{
	 if(x>y)
            m=y;
        else if(x>z)
            m=x;
    }
    return m;
}
