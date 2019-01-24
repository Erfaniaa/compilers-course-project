//global variable
int glob = 0;

//function signature
function void sig_func(int y);

function int no_sig_func() {
    int y = 47;
    return y;
}

//function overloading
function int no_sig_func(int y) {
    y += 47;
    return y;
}

//main function
function void main(){
    //local arrays and simple variables
    int a = 2, b, c[5], d[] = {1, 2, 3};
    b = 3;
    char ch = 'z';
    double t;
    do {
        if (1 + 2 < 5) {
            ++a;
        }
        //a complex boolean expression
        else if ((2 * a > b - 10) and ((1 == 1) or (100 - b * 2 != 10 * (a - 2)))) {
            ++a;
        }

        /* a loop in another loop */
        for (int i = 0; i < 10; i++) {
            ++b;
            break;
        }

        if(a>4){
            ++a;
        }

        a = call no_sig_func(b);
        switch (a){
            case 2:
                ++b;
            case 3:
                glob=3;
                break;
            default:
                --b;
        }
        while(b>5){
            --b;
            continue;
        }
        if(a<0){
            --b;
        }
    } while (a * 2 > 1);
}

function void sig_func(int x){
    glob = x;
    if(glob>5){
        --glob;
    }
    return;
    ++glob;

}
