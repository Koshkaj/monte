package types

type WebsocketInputData interface {
	PlaceBetRouletteInput | CoinflipCreateGameInput | CoinflipAcceptChallengeInput | CoinflipCancelGameInput
}

type WebsocketInputMessage struct {
	Type   string `json:"type"`
	Action string `json:"action"`
	Data   any    `json:"data"`
}

type WebsocketOutputMessage struct {
	Type string `json:"type"`
	Data any    `json:"data"`
}

type WebsocketErrorMessage struct {
	Error string `json:"error"`
}
