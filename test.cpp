
int sum(int a,int b){
    return (a + b);
}
void op(int a,int b){
    if (a<b){
        print("a less than b\n");
    }
    else{
        print("a more or equal than b\n");
    }
}
int main(){
    int mas[10];
    int a, b;
    input(a);
    input(b);
    print("sum: ",sum(a,b),"\n");
    print("subtract: ",a-b,"\n");
    print("divide: ",a/b,"\n");
    print("multiply: ",a*b,"\n");
    print("remainder: ",a%b,"\n");
    print("compare ==: ",a == b,"\n");
    print("compare !=: ",a != b,"\n");
    print("compare >: ",a > b,"\n");
    print("compare <: ",a < b,"\n");
    print("compare >=: ",a >= b,"\n");
    print("compare <=: ",a <= b,"\n");
    print("NOT: ",!1,"\n");
    print("bitwise AND: ",a&b,"\n");
    print("bitwise OR: ",a|b,"\n");
    print("bitwise XOR: ",a^b,"\n");
    op(a,b);
    while (a<b)
    {
        a+=1;
        print("a: ",a,"\n");
    }
    for(int i=0; i<10; i+=1){
        print("i: ",i,"\n");
        mas[i]=(i*2);
    }
    for(int i=0; i<10; i+=1){
        print("mas[",i,"]: ",mas[i],"\n");
    }
}