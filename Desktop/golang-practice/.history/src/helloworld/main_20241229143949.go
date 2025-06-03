package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	type Info struct {
		Password string
		PublicKey int
		SecretKey int
	}

	users := make(map[string]Info)

	users["Bobby"] = Info{Password: "Qwerty123", PublicKey: 123, SecretKey: 8812346381}



	fmt.Println()
}

func authorize(u *users, ) {
	var name string
	fmt.Println("Hello! To authorize enter name:")
	fmt.Scan(&name)
	value, exists := 
}

