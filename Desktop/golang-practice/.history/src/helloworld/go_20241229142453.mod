module helloworld

require github.com/myuser/calculator v0.0.0

require (
	golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c // indirect
	rsc.io/quote v1.5.2 // indirect
	rsc.io/sampler v1.3.0 // indirect
	"github.com/abadojack/whatlanggo"
	
	
)

replace github.com/myuser/calculator => ../calculator

go 1.22.4
