package main

import (
	"bufio"
	"fmt"
	"os"
	"github.com/abadojack/whatlanggo"
)

func main() {
	type Info struct {
		Password int
		PublicKey int
		SecretKey int
	}

	users := make(map[string]Info)

	users["Bobby"] = Info{Password: Qwerty123}

	fmt.Println()

}

