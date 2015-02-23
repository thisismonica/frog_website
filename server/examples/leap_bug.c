int isLeapYear(int year)
{
    if ( year%400 == 0)
    {
        printf("%d is a leap year.\n", year);
        return 1;
    }

    if ( year%100 == 0)
    {
        printf("%d is not a leap year.\n", year);
        return 0;
    }

    if ( year%4 == 0 )
    {
        printf("%d is a leap year.\n", year);
        return 1;
    }

    else
    {
        printf("%d is not a leap year.\n", year);
        return 0;
    }
}