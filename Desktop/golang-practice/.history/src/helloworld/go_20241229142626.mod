module helloworld

require github.com/myuser/calculator v0.0.0

require github.com/abadojack/whatlanggo v1.0.1 // indirect

replace github.com/myuser/calculator => ../calculator

go 1.22.4
