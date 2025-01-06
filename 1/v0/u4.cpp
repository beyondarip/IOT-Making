#include <iostream>
#include <iomanip>
using namespace std;

void printNumberDiamond(int n) {
    // Upper half
    int num = 1;
    for(int i = 1; i <= n; i++) {
        // Spaces
        for(int j = 1; j <= n-i; j++) {
            cout << "   ";
        }
        // Left numbers
        for(int j = 1; j <= i; j++) {
            cout << setw(3) << num++;
        }
        // Right numbers
        for(int j = 1; j < i; j++) {
            cout << setw(3) << --num;
        }
        cout << endl;
        num = 1; // Reset for next row
    }
    
    // Lower half
    for(int i = n-1; i >= 1; i--) {
        // Spaces
        for(int j = 1; j <= n-i; j++) {
            cout << "   ";
        }
        // Left numbers
        for(int j = 1; j <= i; j++) {
            cout << setw(3) << num++;
        }
        // Right numbers
        for(int j = 1; j < i; j++) {
            cout << setw(3) << --num;
        }
        cout << endl;
        num = 1; // Reset for next row
    }
}

int main() {
    int n;
    cout << "Masukan Angka Baris (3-9): ";
    cin >> n;
   
    
    if(n >= 3 && n <= 9) {
    
        printNumberDiamond(n);
    } else {
        cout << "Invalid size! Must be between 3-9.\n";
    }
    return 0;
}
