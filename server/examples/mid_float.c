float mid( float x, float y, float z )
{
    float m;
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
float max( float x)
{
    return x;
}
