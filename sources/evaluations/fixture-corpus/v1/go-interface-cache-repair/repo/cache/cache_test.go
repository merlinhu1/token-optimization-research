package cache

import (
    "context"
    "testing"
)

func TestMemoryStoreImplementsStore(t *testing.T) {
    var store Store = NewMemoryStore()
    if err := store.Put(context.Background(), "alpha", []byte("one")); err != nil {
        t.Fatalf("put failed: %v", err)
    }
    got, err := store.Get(context.Background(), "alpha")
    if err != nil {
        t.Fatalf("get failed: %v", err)
    }
    if string(got) != "one" {
        t.Fatalf("got %q", string(got))
    }
}
