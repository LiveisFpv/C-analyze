
int sum(int a,int b){
    return (a + b);
}
void op(int a,int b){
    if (a<b){
        print("a less than b");
    }
    else{
        print("a more or equal than b");
    }
}
int main(){
    int mas[10];
    int a, b;
    input(a);
    input(b);
    print("sum:",sum(a,b));
    print("subtract:",a-b);
    print("divide:",a/b);
    print("multiply:",a*b);
    print("remainder:",a%b);
    print("compare ==:",a == b);
    print("compare !=:",a != b);
    print("compare >:",a > b);
    print("compare <:",a < b);
    print("compare >=:",a >= b);
    print("compare <=:",a <= b);
    print("NOT:",!1);
    print("bitwise AND:",a&b);
    print("bitwise OR:",a|b);
    print("bitwise XOR:",a^b);
    op(a,b);
    while (a<b)
    {
        a+=1;
        print("a: ",a);
    }
    for(int i=0; i<10; i+=1){
        print("i: ",i);
        mas[i]=(i*2);
    }
    for(int i=0; i<10; i+=1){
        print("mas[",i,"]:",mas[i]);
    }
}