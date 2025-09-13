#include <iostream>
using namespace std;

// Clase Nodo
class Nodo {
public:
    int dato;
    Nodo* izquierdo;
    Nodo* derecho;

    // Constructor
    Nodo(int valor) {
        dato = valor;
        izquierdo = nullptr;
        derecho = nullptr;
    }
};

// Clase 
class ArbolBinario {
public:
    Nodo* raiz;

    // Constructor
    ArbolBinario() {
        raiz = nullptr;
    }

    // Insertar
    void insertar(int valor) {
        raiz = insertarRecursivo(raiz, valor);
    }

    // Imprimir 
    void imprimirArbol() {
        cout << "\nRecorrido en orden (izq - raiz - der): ";
        enOrden(raiz);

        cout << "\nRecorrido preorden (raiz - izq - der): ";
        preOrden(raiz);

        cout << "\nRecorrido postorden (izq - der - raiz): ";
        postOrden(raiz);

        cout << endl;
    }

public:
    Nodo* insertarRecursivo(Nodo* nodo, int valor) {
        if (nodo == nullptr) {
            return new Nodo(valor);
        }
        if (valor < nodo->dato) {
            nodo->izquierdo = insertarRecursivo(nodo->izquierdo, valor);
        } else {
            nodo->derecho = insertarRecursivo(nodo->derecho, valor);
        }
        return nodo;
    }

    void enOrden(Nodo* nodo) {
        if (nodo != nullptr) {
            enOrden(nodo->izquierdo);
            cout << nodo->dato << " ";
            enOrden(nodo->derecho);
        }
    }

    void preOrden(Nodo* nodo) {
        if (nodo != nullptr) {
            cout << nodo->dato << " ";
            preOrden(nodo->izquierdo);
            preOrden(nodo->derecho);
        }
    }

    void postOrden(Nodo* nodo) {
        if (nodo != nullptr) {
            postOrden(nodo->izquierdo);
            postOrden(nodo->derecho);
            cout << nodo->dato << " ";
        }
    }
};

// main con menu
int main() {
    ArbolBinario arbol;
    int opcion, valor;

    do {
        cout << "\n- MENU  \n";
        cout << "1: Insertar un numero\n";
        cout << "2: Imprimir arbol\n";
        cout << "3: Salir\n";
        cout << "Que opcion quiere: ";
        cin >> opcion;

        switch (opcion) {
        case 1:
            cout << "Ingrese numero a insertar: ";
            cin >> valor;
            arbol.insertar(valor);
            break;
        case 2:
            arbol.imprimirArbol();
            break;
        case 3:
            cout << "Adios :D\n";
            break;
        default:
            cout << "EROR!!\n";
        }

    } while (opcion != 3);

    return 0;
}