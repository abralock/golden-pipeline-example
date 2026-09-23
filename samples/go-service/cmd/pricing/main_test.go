package main

import (
	"bytes"
	"testing"
)

func TestRun(t *testing.T) {
	var buf bytes.Buffer
	if err := run(&buf, 10000); err != nil || buf.String() != "total: 9000 cents\n" {
		t.Fatalf("got %q, %v", buf.String(), err)
	}
}

func TestRunRejectsNegative(t *testing.T) {
	if err := run(&bytes.Buffer{}, -1); err == nil {
		t.Fatal("expected error for negative subtotal")
	}
}
