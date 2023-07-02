package core

import (
	"context"
	"encoding/json"
	"sync"

	"github.com/google/uuid"
	"github.com/gorilla/websocket"
	"github.com/redis/go-redis/v9"
	"gitlab.com/montecsgo/microsockets/types"
)

type WebsocketConnection struct {
	ID     uuid.UUID
	PubSub *redis.PubSub
	Conn   *websocket.Conn

	mu           *sync.RWMutex
	SubscribedTo []string
}

func (c *WebsocketConnection) Subscribe(topic string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	for _, t := range c.SubscribedTo {
		if t == topic { // already subscribed
			return
		}
	}
	c.SubscribedTo = append(c.SubscribedTo, topic)
	c.PubSub.Subscribe(context.Background(), topic)
}

func (c *WebsocketConnection) Unsubscribe(topic string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	for i, t := range c.SubscribedTo {
		if t == topic {
			c.SubscribedTo = append(c.SubscribedTo[:i], c.SubscribedTo[i+1:]...)
			c.PubSub.Unsubscribe(context.Background(), topic)
			break
		}
	}
}

func (c *WebsocketConnection) UnsubscribeAll() {
	c.mu.Lock()
	defer c.mu.Unlock()
	for _, t := range c.SubscribedTo {
		c.PubSub.Unsubscribe(context.Background(), t)
	}
	c.SubscribedTo = []string{}
}

func (c *WebsocketConnection) SubscribedChannels() []string {
	c.mu.RLock()
	defer c.mu.RUnlock()
	topics := make([]string, len(c.SubscribedTo))
	copy(topics, c.SubscribedTo)

	return topics
}

func (c *WebsocketConnection) ListenForMessages() {
	ch := c.PubSub.Channel()
	for msg := range ch {
		// TODO: if msg.Payload == better.id (chemive socketze sxvanairad gamovgzavno)
		c.Conn.WriteMessage(websocket.TextMessage, []byte(msg.Payload))
	}
}

func (c *WebsocketConnection) HandleWebsocketError(errorMessage string) {
	data, _ := json.Marshal(&types.WebsocketErrorMessage{
		Error: errorMessage,
	})
	c.Conn.WriteMessage(websocket.TextMessage, data)
}

func NewWebSocketConnection(id uuid.UUID, pubsub *redis.PubSub, conn *websocket.Conn) *WebsocketConnection {
	return &WebsocketConnection{
		ID:           id,
		PubSub:       pubsub,
		Conn:         conn,
		mu:           &sync.RWMutex{},
		SubscribedTo: []string{},
	}
}
