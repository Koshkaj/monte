package api

import (
	"encoding/json"
	"fmt"

	"github.com/google/uuid"
	"github.com/gorilla/websocket"
	"github.com/labstack/echo"
	"golang.org/x/net/context"

	"gitlab.com/montecsgo/microsockets/core"
	"gitlab.com/montecsgo/microsockets/types"
	"gitlab.com/montecsgo/microsockets/utils"

	pbCoinflip "gitlab.com/montecsgo/microsockets/grpc/coinflip"
	pbRoulette "gitlab.com/montecsgo/microsockets/grpc/roulette"
)

const (
	SUBSCRIBE_COINFLIP   = "sub/coinflip"
	UNSUBSCRIBE_COINFLIP = "unsub/coinflip"
	INTERRACT_COINFLIP   = "intr/coinflip"

	SUBSCRIBE_CHAT   = "sub/chat"
	UNSUBSCRIBE_CHAT = "unsub/chat"
	INTERRACT_CHAT   = "intr/chat"

	SUBSCRIBE_ROULETTE   = "sub/roulette"
	UNSUBSCRIBE_ROULETTE = "unsub/roulette"
	INTERRACT_ROULETTE   = "intr/roulette"

	SUBSCRIBE_NOTIFICATIONS = "sub/notifications"
	INTERRACT_NOTIFICATIONS = "intr/notifications"
	// Frontendi treulobs cookiedan current accoutns, agzavnis steamze da mere agzavnis am eventze ^
)

func (s *Server) handleRCWebsocket(c echo.Context) error {

	var upgrader = websocket.Upgrader{
		ReadBufferSize:  1024,
		WriteBufferSize: 1024,
	}
	conn, err := upgrader.Upgrade(c.Response(), c.Request(), nil)
	if err != nil {
		return err
	}
	defer conn.Close()

	pubsub := s.Redis.Subscribe(c.Request().Context(), "monte-server") // mtavari topici sadac server counts davtrekavt
	defer pubsub.Close()

	conID := uuid.New()
	wsConnection := core.NewWebSocketConnection(conID, pubsub, conn)

	go func() {
		wsConnection.ListenForMessages()
	}()

	// TODO: reconectis handleri ari dasamatebeli

	s.addServerConnection(context.Background(), conID, conn.RemoteAddr().String()) // roca daemata connectioni, davapablishot ro vigac shemovida

	connectionCount, _ := s.countServerConnections(context.Background())
	s.Redis.Publish(c.Request().Context(), "monte-server", connectionCount)

	for {
		_, p, err := conn.ReadMessage()
		if err != nil {
			if websocket.IsCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure, websocket.CloseNoStatusReceived, websocket.CloseNormalClosure) {
				wsConnection.UnsubscribeAll()
				s.removeServerConnection(context.Background(), conID)
				connectionCount, _ := s.countServerConnections(context.Background())
				s.Redis.Publish(c.Request().Context(), "monte-server", connectionCount) // Todo Shevcvalo counti jsonze
				return nil
			}
			return err
		}
		var message types.WebsocketInputMessage
		err = json.Unmarshal(p, &message)
		if err != nil {
			wsConnection.HandleWebsocketError("invalid json")
			continue
		}
		// type should exist
		if message.Type == "" {
			wsConnection.HandleWebsocketError("event type should be supplied")
			continue
		}

		switch message.Type {
		case "ping":
			wsConnection.Conn.WriteMessage(websocket.TextMessage, []byte("pong"))

		case SUBSCRIBE_NOTIFICATIONS:
			wsConnection.Subscribe(fmt.Sprintf("notifications:%s", conID)) // steam64id conId is nacvlad
			wsConnection.Conn.WriteMessage(websocket.TextMessage, []byte("init"))
			// 1. clienti agzavnis amas yovel connectze
			// 2. rogorcki daisubeba notificationze (inter/notifications), clientis sokets gavugzavnot unauthorized
			// 3. clienti miigebs am datas da cherez steam api daitrevs datas da gamomigzavnis ukan (intr/notifications) ze
			// 4. ro miigos clientma notificationebi ragac eventebze,
			//    unda davupostot magis connections, magis connectioni shegvilia avigot steam64 id da magas davusubot
			//      -- scenari, Nika ugzavnis ragacas Giorgis
			//         1. vicit nikasic da giorgis steam id
			//         2. unda davitriot giorgis socket connection id, romelic aris giorgis steam64 id
			//		   3. nikas soketi apablishebs giorgis steam64 ze notificationis datas
			// 		   4. giorgis misdis notificationi (intr/notification, data: ...)

			// bet is scenari
			// shemovida beti ruletkaze, egreve chamovacherit balanci
			// roca chamovacherit, gavugzavnet cherez grpc micro_balances, romelmac chamoachra redisshi da bazashi
			// mere am grpc servisma dauposta channels tavis balanci da experience
			// micro-games shi vicit vinc moigebs winaswar sanam datrialdeba, chavyrit queue shi yvelas balancis updates
			// es queue daigzavneba gRPC balancze mashin roca morcheba raundi
			continue

		case SUBSCRIBE_COINFLIP:
			wsConnection.Subscribe(INTERRACT_COINFLIP)
			wsConnection.Conn.WriteMessage(websocket.TextMessage, []byte(SUBSCRIBE_COINFLIP))

		case UNSUBSCRIBE_COINFLIP:
			wsConnection.Unsubscribe(INTERRACT_COINFLIP)
			wsConnection.Conn.WriteMessage(websocket.TextMessage, []byte(UNSUBSCRIBE_COINFLIP))

		case INTERRACT_COINFLIP:
			switch message.Action {
			case "create_game":
				var data types.CoinflipCreateGameInput
				err := utils.Remarshal(message.Data, &data)
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				err = c.Validate(&data)
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				resp, err := s.gRPC.CoinFlip.CreateGame(context.Background(),
					&pbCoinflip.CreateGameRequest{
						BetAmount: data.BetAmount,
						Side:      data.Side,
						Token:     data.SecurityToken,
					}) // Todo: withdeadline context

				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				fmt.Println(resp) // Check if everything went fine

			case "accept_challenge":
				var data types.CoinflipAcceptChallengeInput
				err := utils.Remarshal(message.Data, &data)
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				err = c.Validate(&data)
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				resp, err := s.gRPC.CoinFlip.AcceptChallenge(context.Background(),
					&pbCoinflip.AcceptChallengeRequest{
						Token:   data.SecurityToken,
						RoundId: data.RoundID,
					})
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				fmt.Println(resp) // check if everything wnet fine

			case "cancel_game":
				var data types.CoinflipCancelGameInput
				err := utils.Remarshal(message.Data, &data)
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				err = c.Validate(&data)
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				resp, err := s.gRPC.CoinFlip.CancelGame(context.Background(),
					&pbCoinflip.CancelGameRequest{
						RoundId: data.RoundID,
						Token:   data.SecurityToken,
					})
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				fmt.Println(resp) // check if everything wnet fine
			default:
				wsConnection.HandleWebsocketError("invalid action for coinflip")
				continue
			}
			// -------- NEW FLOW ------------ intr/coinflip create_game
			// 1. clienti migzavnis intr/coinflip create game
			// 2. me mivdivar microgames shi cherez gRPC
			// 3. vqmni tamashs da vubruneb yvela connections pasuxs ro tamashi shevqmeni

			// intr/coinflip join_game
			// 1. vnaculob tamashs tu arsebobs redis shi
			// 2. tu arsebobs, microgames shi vartyav mag tamashistvis dajoinebas
			// 3. yvelastan vagzavni events : intr/coinflip challenge s vigac rogorcki joindeba
			// 3. am dros tmaahsis resulti ukve cnobilia, timeout unda vqnat 4 wami da mere yvelas davugzavno intr/coinflip result

			// intr/coinflip cancel_game
			// s.Redis.Publish(context.Background(), INTERRACT_COINFLIP, "intr/coinflip, 'create_game'")
			// intr/coinflip accept_challenge
			// tu dafeilda,
			// wsConnection.Conn.WriteMessage(websocket.TextMessage, []byte("moxda erori"))
			// tu araperi moxda da accept challenge success iyo
			// s.Redis.Publish(context.Background(), INTERRACT_COINFLIP, "intr/coinflip, acceptChallenge data")
			//

		case SUBSCRIBE_ROULETTE:
			wsConnection.Subscribe(INTERRACT_ROULETTE)
			wsConnection.Conn.WriteMessage(websocket.TextMessage, []byte(SUBSCRIBE_ROULETTE))
			resp, err := s.gRPC.Roulette.GetState(context.Background(), &pbRoulette.EmptyRequest{})
			if err != nil && resp.Success && resp.Data != nil {
				wsConnection.HandleWebsocketError(err.Error())
				continue
			}
			wsConnection.Conn.WriteMessage(websocket.TextMessage, []byte(*resp.Data)) // TODO Init ze wamovides ruletkis info

		case INTERRACT_ROULETTE:
			// es ari roca klienti gvebazreba imena chven
			// marto place_bet
			// magalitad davde me
			// wavida grpc requesti dadebis da ro daido damibrunda pasuxi
			// da mere davapablishe INTERRACT_ROULETTE channelze
			// round_id, _ := strconv.Atoi(message.Data)
			switch message.Action {
			case "place_bet":
				var data types.PlaceBetRouletteInput
				err := utils.Remarshal(message.Data, &data)
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}

				err = c.Validate(&data)
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}

				resp, err := s.gRPC.Roulette.PlaceBet(context.Background(), &pbRoulette.PlaceBetRequest{
					Token:   data.Token,
					RoundId: data.RoundID,
					Coin:    data.Coin,
					Amount:  data.Amount,
				})
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				} else if resp.Error != "null" && !resp.Success {
					wsConnection.HandleWebsocketError(resp.Error)
					continue
				}
			default:
				wsConnection.HandleWebsocketError("invalid action for roulette")
				continue
			}

		case UNSUBSCRIBE_ROULETTE:
			wsConnection.Unsubscribe(INTERRACT_ROULETTE)
			wsConnection.Conn.WriteMessage(websocket.TextMessage, []byte(UNSUBSCRIBE_ROULETTE))
		case SUBSCRIBE_CHAT:
			// increase number of people in this specific chat and publish it to everyone
			// unsubscribe from other chats and subscribe to this chat only because
			// user can only be in one chat at once
			s.Redis.Set(c.Request().Context(), fmt.Sprintf("chat:%s", conID), "english_room", 0) // Subscribe to english channel by default
			s.Redis.Publish(c.Request().Context(), "monte-server", 1)
			wsConnection.Subscribe(INTERRACT_CHAT)
			wsConnection.Conn.WriteMessage(websocket.TextMessage, []byte(SUBSCRIBE_CHAT))
		case INTERRACT_CHAT:
			switch message.Action {
			case "change_room":
				var data types.ChatChangeRoomInput
				err := utils.Remarshal(message.Data, &data)
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				currentChat, err := s.Redis.Get(c.Request().Context(), fmt.Sprintf("chat:%s", conID)).Result()
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				wsConnection.Unsubscribe(currentChat)
				wsConnection.Subscribe(data.RoomName)
			case "send_message": // User sent a message
				var data types.ChatMessageInput
				err := utils.Remarshal(message.Data, &data)
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				s.Redis.Publish(c.Request().Context(), data.RoomName, data.Message)
				msg := &types.ChatMessageOutput{
					Message:  data.Message,
					RoomName: data.RoomName,
				}
				wso := &types.WebsocketOutputMessage{
					Type: "batch",
					Data: msg,
				}
				outgoingMessage, err := json.Marshal(wso)
				if err != nil {
					wsConnection.HandleWebsocketError(err.Error())
					continue
				}
				wsConnection.Conn.WriteMessage(websocket.TextMessage, outgoingMessage)
			}
		case UNSUBSCRIBE_CHAT:
			// unsubscribe from chat that he was connected to
			currentChat, err := s.Redis.Get(c.Request().Context(), fmt.Sprintf("chat:%s", conID)).Result()
			if err != nil {
				wsConnection.HandleWebsocketError(err.Error())
				continue
			}
			s.Redis.Publish(c.Request().Context(), "monte-server", -1)
			wsConnection.Unsubscribe(currentChat)
		default:
			wsConnection.Conn.WriteMessage(websocket.TextMessage, []byte("requested event does not exist"))
		}

	}
}
