package main

import (
	"fmt"
)

func main() {
	type Info struct {
		Password string
		PublicKey int
		SecretKey int
	}

	users := make(map[string]Info)

	users["Bobby"] = Info{Password: "Qwerty123", PublicKey: 123, SecretKey: 8812346381}

	authorize(users)
}

func authorize(users map[string]Info) {
	var name string
	var pw string

	fmt.Println("Hello! To authorize enter name:")
	fmt.Scan(&name)

	userInfo, exists := i[name]
	if !exists {
		panic("User not found!")
	}
}


