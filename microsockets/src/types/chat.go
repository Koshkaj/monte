package types

type ChatChangeRoomInput struct {
	RoomName string `json:"room_name"`
}

type ChatMessageInput struct { // incomming message from user
	// UserStruct
	UserID  string `json:"user_id"`
	Message string `json:"message"`
	// RoomID 	int `json:"room_id"`
	RoomName string `json:"room_name"`
}

type ChatMessageOutput struct { // outgoing message to other people in the channel
	// UserStruct
	Message  string `json:"message"`
	RoomName string `json:"room_name"`
}
