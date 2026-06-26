package cache

import "context"

type Store interface {
    Put(ctx context.Context, key string, value []byte) error
    Get(ctx context.Context, key string) ([]byte, error)
}

type MemoryStore struct {
    data map[string][]byte
}

func NewMemoryStore() *MemoryStore {
    return &MemoryStore{data: map[string][]byte{}}
}

func (m *MemoryStore) Put(key string, value []byte) error {
    m.data[key] = value
    return nil
}

func (m *MemoryStore) Get(ctx context.Context, key string) ([]byte, error) {
    return m.data[key], nil
}
