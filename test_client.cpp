#include <iostream>
#include <cstdlib>

int main() {
    std::cout << "--- Resetting Engine via C++ System Call ---" << std::endl;
    system("curl -X DELETE http://127.0.0.1:8000/reset");

    std::cout << "\n--- Sending Tx1 waiting for Tx2 ---" << std::endl;
    system("curl -X POST http://127.0.0.1:8000/request-lock -H \"Content-Type: application/json\" -d \"{\\\"requester\\\": \\\"Tx1\\\", \\\"holder\\\": \\\"Tx2\\\"}\"");

    std::cout << "\n--- Sending Tx2 waiting for Tx3 ---" << std::endl;
    system("curl -X POST http://127.0.0.1:8000/request-lock -H \"Content-Type: application/json\" -d \"{\\\"requester\\\": \\\"Tx2\\\", \\\"holder\\\": \\\"Tx3\\\"}\"");

    std::cout << "\n--- Sending Tx3 waiting for Tx1 (Triggers Deadlock) ---" << std::endl;
    system("curl -X POST http://127.0.0.1:8000/request-lock -H \"Content-Type: application/json\" -d \"{\\\"requester\\\": \\\"Tx3\\\", \\\"holder\\\": \\\"Tx1\\\"}\"");

    return 0;
}