#include <stdio.h>
int main() {
	double x;
	scanf("%lf", &x);
	if (x < 0) {printf("1"); x = -x;}
	else printf("0");
	int ax = (int) x; // целая часть x
	double bx = x - ax; // дробная часть x
	int j, k;
	int i = 1;
	int e = 15; 
	if (ax > 0) {
	    for (; i*2 <= ax && e<30; i*=2) e++;
	    j = 25 - e;
	    k = i / 2;
	} else {
	    for(; bx < 1 && e > 0; bx*=2) e--;
	    j = 10;
	    bx -= (int) bx;
	}
	for (i = 16; i>0; i/=2) printf("%d", e/i%2);
	if (ax>0) for(i=10; k>0 && i>0;k/=2, i--) printf("%d", ax/k%2);
    for (; j>0; j--) {
        bx = bx * 2;
        ax = (int) bx;
        printf("%d", ax);
        bx = bx - ax;
    }
  return 0;
}