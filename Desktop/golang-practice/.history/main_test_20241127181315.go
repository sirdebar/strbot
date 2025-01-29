package main

import (
	"testing"
)

func TestCanSendMessage(t *testing.T) {
	tests := []struct {
		name     string
		mToSend  messageToSend
		expected bool
	}{
		{
			name: "Valid message",
			mToSend: messageToSend{
				message:   "you have an appointment tomorrow",
				sender:    user{name: "Brenda Halafax", number: 16545550987},
				recipient: user{name: "Sally Sue", number: 19035558973},
			},
			expected: true,
		},
		{
			name: "Missing sender name",
			mToSend: messageToSend{
				message:   "you have an event tomorrow",
				sender:    user{number: 16545550987},
				recipient: user{name: "Suzie Sall", number: 19035558973},
			},
			expected: false,
		},
		{
			name: "Missing recipient number",
			mToSend: messageToSend{
				message:   "you have a birthday tomorrow",
				sender:    user{name: "Jason Bjorn", number: 16545550987},
				recipient: user{name: "Jim Bond"},
			},
			expected: false,
		},
		{
			name: "Empty sender and recipient",
			mToSend: messageToSend{
				message:   "you have a party tomorrow",
				sender:    user{name: "Njorn Halafax"},
				recipient: user{name: "Becky Sue", number: 19035558973},
			},
			expected: false,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			output := canSendMessage(test.mToSend)
			if output != test.expected {
				t.Errorf("Test %q failed. Expected %v, got %v", test.name, test.expected, output)
			}
		})
	}
}
