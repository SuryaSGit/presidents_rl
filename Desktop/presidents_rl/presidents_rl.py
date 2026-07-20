from typing import List
import random
class playerstate:
    def __init__(self,cards):
        #52 dim vector storing whether or not hand has a certain card.
        self.cards = [0 for i in range(52)]
        for card in cards:
            self.cards[card] = 1
    def get_state(self):
        return self.cards
    def get_num_from_action(action : int):
        if action < 52:
            return action
        elif action < 66:
            return action - 52
        elif action < 79:
            return action - 66
        elif action < 93:
            return action - 80
        return -1
    def get_amount_of_cards(self, cardnum : int):
        count = 0
        startpoint = cardnum * 4
        for i in range(startpoint, startpoint + 4):
            if self.cards[i] != 0:
                count += 1
        return count
    def get_highest_card_of_num(self, cardnum : int):
        curmax = -1
        for i in range(cardnum * 4, cardnum * 4 + 4):
            if self.cards[i] != 0:
                curmax = i
        return curmax
    def check_valid_action(self, action : int, cur_highest : int):
        #0-51 = play that card
        #52-65 = play pair with that number
        #66-79 = play three of a kind with that number
        #80-93 = play four of a kind with that number
        int cardnum = self.get_num_from_action(action)
        if action < 52:
            if(self.cards[action] != 0):
                return True
        elif action < 66:
            if(self.get_amount_of_cards(cardnum) > 1):
                if self.get_highest_card_of_num(cardnum) > cur_highest:
                    return True
        elif action < 79:
            if(self.get_amount_of_cards(cardnum) > 2):
                if self.get_highest_card_of_num(cardnum) > cur_highest:
                    return True
        elif action < 93:
            if(self.get_amount_of_cards(cardnum) > 3):
                if self.get_highest_card_of_num(cardnum) > cur_highest: 
                    return True
        return False

    def play_action(self,action : int):
        cards_played = []
        if not self.check_valid_action(action):
            print("Invalid action")
        else:
            if action < 52:
                self.cards[action] = 0
                cards_played.append(action)
            if action < 66:
                #keep highest
                cardnum = self.get_num_from_action(action)
                to_remove = []
                for i in range(cardnum * 4, cardnum * 4 + 4):
                    if self.cards[i] != 0:
                        to_remove.append(i)
                    if len(to_remove) == 2: 
                        break
                self.cards[to_remove[0]] = 0
                cards_played.append(to_remove[0])
                self.cards[to_remove[1]] = 0
                cards_played.append(to_remove[1])
            if action < 79:
                cardnum = self.get_num_from_action(action)
                to_remove = []
                for i in range(cardnum * 4, cardnum * 4 + 4):
                    if self.cards[i] != 0:
                        to_remove.append(i)
                    if len(to_remove) == 3:
                        break
                self.cards[to_remove[0]] = 0
                self.cards[to_remove[1]] = 0
                self.cards[to_remove[2]] = 0
                cards_played.append(to_remove[0])
                cards_played.append(to_remove[1])
                cards_played.append(to_remove[2])
            if action < 93:
                cardnum = self.get_num_from_action(action)
                for i in range(cardnum * 4, cardnum * 4 + 4):
                    self.cards[i]=0
                    cards_played.append(i)
        return cards_played

    def get_lowest_possible_playable(self, cur_highest : int):
        for i in range(cur_highest + 1, 52):
            if(self.cards[i] != 0):
                return i
        return -1


def randomize_cards(cards : List[int]):
    result = []
    cur = 0
    while cards:
        card = cards.pop(random.randint(0, len(cards) - 1))
        result[cur].append(card)
        cur += 1
        if(cur == 7):
            cur = 0
    if(len(result) != 6):
        print("Error in randomizing")
    return result
class stateManager:
    def __init__(self):
        self.players = []
        self.board_state = []
        self.cards_played = [0 for i in range(52)]
        cards = [i for i in range(52)]
        player_hands = randomize_cards(cards)
        #RL Guy is player 0
        for i in range(6):
            self.players.append(playerstate(player_hands[i]))
        self.current_player = 0
        self.last_player = -1
        self.cur_highest_card = -1
        for card in self.cards_played:
            self.board_state.append(card)
        self.board_state.append(self.cur_highest_card)
        self.board_state.append(self.last_player)
    def play_action(self,action:int):
        if(self.current_player != 0):
            print("Not your turn")
            return
        curplayer = self.players[0]
        if not curplayer.check_valid_action(action):
            print("Invalid action")
            return
        cards_played = curplayer.play_action(action)

        for card in cards_played:
            self.cards_played[card] = 1
            self.board_state[card] = 1
        self.last_player = self.current_player
        self.current_player = (self.current_player + 1) % 6
        self.board_state[53] = 

def create_game():
    #card1,2,3,4,5,6,7,8,9, cur_highest_card, highest_left, current_player, last_player
    cards = [i for i in range(52)]

    state = []