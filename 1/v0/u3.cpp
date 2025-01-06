#include <iostream>
#include <iomanip>
using namespace std;

void multiplicationPyramid(int n) {
    for (int i = 1; i <= n; ++i) {
        // Print spaces
        for (int j = 0; j < n - i; ++j) {
            cout << "   ";
        }
        // Print numbers
        for (int j = 1; j <= i; ++j) {
            int result = i * j;
            cout << setw(2) << result << " ";
        }
        // Print reverse numbers
        for (int j = i - 1; j > 0; --j) {
            int result = i * j;
            cout << setw(2) << result << " ";
        }
        cout << endl;
    }
}

void alternatingTable(int n) {
    for (int i = 1; i <= n; ++i) {
        for (int j = 1; j <= n; ++j) {
            int result;
            if (i % 2 == 0) {
                // Even rows: descending
                result = i * (n - j + 1);
            } else {
                // Odd rows: ascending
                result = i * j;
            }
            cout << setw(3) << result << " ";
        }
        cout << endl;
    }
}

void spiralMultiplication(int n) {
    int matrix[10][10] = {0}; // Adjusted size for simplicity
    int left = 0, right = n - 1, top = 0, bottom = n - 1;
    int num = 1;

    while (left <= right && top <= bottom) {
        // Top row
        for (int i = left; i <= right; ++i) {
            matrix[top][i] = num * top;
            ++num;
        }
        ++top;

        // Right column
        for (int i = top; i <= bottom; ++i) {
            matrix[i][right] = num * right;
            ++num;
        }
        --right;

        if (top <= bottom) {
            // Bottom row
            for (int i = right; i >= left; --i) {
                matrix[bottom][i] = num * bottom;
                ++num;
            }
            --bottom;
        }

        if (left <= right) {
            // Left column
            for (int i = bottom; i >= top; --i) {
                matrix[i][left] = num * left;
                ++num;
            }
            ++left;
        }
    }

    // Print matrix
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            cout << setw(4) << matrix[i][j] << " ";
        }
        cout << endl;
    }
}

void mainMenu() {
   
        int choice = 2;
    

        int n;
        cout << "Masukkan ukuran : ";
        cin >> n;

        if (n < 3 || n > 9) {
            cout << "Ukuran harus antara 3-9" << endl;
            
        }

        cout << "\nHasil:" << endl;
        switch (choice) {
            case 1:
                multiplicationPyramid(n);
                break;
            case 2:
                alternatingTable(n);
                break;
            case 3:
                spiralMultiplication(n);
                break;
            default:
                cout << "Pilihan tidak valid!" << endl;
        }
  
}

int main() {
    mainMenu();
    return 0;
}
