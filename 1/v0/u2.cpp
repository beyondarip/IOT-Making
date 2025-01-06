#include <iostream>
#include <iomanip>
using namespace std;

void holowDiamond(int n) {
    // Upper half
    for(int i = 1; i <= n; i++) {
        for(int j = 1; j <= n-i; j++)
            cout << "  ";
        for(int j = 1; j <= 2*i-1; j++) {
            if(j == 1 || j == 2*i-1)
                cout << "* ";
            else
                cout << "  ";
        }
        cout << endl;
    }
    // Lower half
    for(int i = n-1; i >= 1; i--) {
        for(int j = 1; j <= n-i; j++)
            cout << "  ";
        for(int j = 1; j <= 2*i-1; j++) {
            if(j == 1 || j == 2*i-1)
                cout << "* ";
            else
                cout << "  ";
        }
        cout << endl;
    }
}

void numberPattern(int n) {
    int num = 1;
    for(int i = 1; i <= n; i++) {
        for(int j = 1; j <= n-i; j++)
            cout << "   ";
        for(int j = 1; j <= i; j++) {
            cout << setw(3) << num;
            num = (num % 9) + 1;
        }
        for(int j = i-1; j >= 1; j--) {
            cout << setw(3) << num;
            num = (num % 9) + 1;
        }
        cout << endl;
    }
}

void multiplicationTriangle(int n) {
    for(int i = 1; i <= n; i++) {
        for(int j = 1; j <= i; j++) {
            if(j == 1 || j == i || i == n)
                cout << setw(4) << i*j;
            else
                cout << "   ";
        }
        cout << endl;
    }
}

int main() {
    int choice, n;
    
    do {
        cout << "\nUAS PRAKTIKUM ALGORITMA\n";
        cout << "======================\n";
        cout << "1. Hollow Diamond\n";
        cout << "2. Number Pattern Pyramid\n";
        cout << "3. Hollow Multiplication Triangle\n";
        cout << "4. Exit\n";
        cout << "Choose pattern (1-4): ";
        cin >> choice;

        if(choice >= 1 && choice <= 3) {
            cout << "Enter size (3-9): ";
            cin >> n;
            
            if(n >= 3 && n <= 9) {
                cout << "\nOutput:\n";
                switch(choice) {
                    case 1: holowDiamond(n); break;
                    case 2: numberPattern(n); break;
                    case 3: multiplicationTriangle(n); break;
                }
            } else {
                cout << "Error: Size must be between 3-9!\n";
            }
        }
    } while(choice != 4);
    return 0;
}