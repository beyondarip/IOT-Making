#include <iostream>
#include <iomanip>
using namespace std;

void generateTriangle1(int n) {
    // Pattern 1: Number Triangle with row multiplication
    for(int i = 1; i <= n; i++) {
        for(int j = 1; j <= i; j++) {
            cout << setw(4) << i*j;
        }
        cout << endl;
    }
}

void generateTriangle2(int n) {
    // Pattern 2: Alternating odd/even numbers
    int num = 1;
    for(int i = 1; i <= n; i++) {
        for(int j = 1; j <= i; j++) {
            cout << setw(4) << num;
            num += 2;
        }
        cout << endl;
    }
}

void generateTriangle3(int n) {
    // Pattern 3: Reverse number triangle
    for(int i = n; i >= 1; i--) {
        // Print spaces
        for(int s = n-i; s > 0; s--) {
            cout << "    ";
        }
        // Print numbers
        for(int j = 1; j <= i; j++) {
            cout << setw(4) << j;
        }
        cout << endl;
    }
}

int main() {
    int choice, size;
    
    do {
        cout << "\nUAS PRAKTIKUM ALGORITMA PEMROGRAMAN 1\n";
        cout << "====================================\n";
        cout << "1. Pola Segitiga Perkalian\n";
        cout << "2. Pola Segitiga Bilangan Ganjil\n";
        cout << "3. Pola Segitiga Terbalik\n";
        cout << "4. Keluar\n";
        cout << "Pilih pola (1-4): ";
        cin >> choice;

        if(choice >= 1 && choice <= 3) {
            cout << "Masukkan ukuran (3-9): ";
            cin >> size;
            
            if(size >= 3 && size <= 9) {
                cout << "\nHasil:\n";
                switch(choice) {
                    case 1: generateTriangle1(size); break;
                    case 2: generateTriangle2(size); break;
                    case 3: generateTriangle3(size); break;
                }
            } else {
                cout << "Error: Ukuran harus antara 3-9!\n";
            }
        }
    } while(choice != 4);

    return 0;
}