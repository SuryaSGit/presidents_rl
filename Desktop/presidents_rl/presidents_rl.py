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
    def check_valid_action(self, action : int, cur_highest : int, pile_multiplier : int):
        #0-51 = play that card
        #52-65 = play pair with that number
        #66-79 = play three of a kind with that number
        #80-93 = play four of a kind with that number
        cardnum = self.get_num_from_action(action)
        amount = self.get_amount_of_cards(cardnum)
        highest_card = self.get_highest_card_of_num(cardnum)
        if action < 52:
            if(pile_multiplier != -1 and pile_multiplier != 1):
                return False
            if(self.cards[action] != 0):
                return True
        elif action < 66:
            if(pile_multiplier != -1 and pile_multiplier != 2):
                return False
            if(amount > 1):
                if highest_card > cur_highest:
                    return True
        elif action < 79:
            if(pile_multiplier != -1 and pile_multiplier != 3):
                return False
            if(amount > 2):
                if highest_card > cur_highest:
                    return True
        elif action < 93:
            if(pile_multiplier != -1 and pile_multiplier != 4):
                return False
            if(amount > 3):
                if highest_card > cur_highest:
                    return True
        return False

    def play_action(self,action : int, cur_highest : int, pile_multiplier : int):
        cards_played = []
        if not self.check_valid_action(action, cur_highest, pile_multiplier):
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
    def get_best_action(self, cur_highest : int, pile_multiplier : int):
        for i in range(93):
            if self.check_valid_action(i, cur_highest, pile_multiplier):
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
        self.pile_multiplier = -1
        self.players_left = 6
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
        self.board_state.append(self.pile_multiplier)
        self.board_state.append(self.players_left)
    def play_action(self,action:int):
        if(self.current_player != 0):
            print("Not your turn")
            return
        curplayer = self.players[0]
        if not curplayer.check_valid_action(action, self.cur_highest_card, self.pile_multiplier):
            print("Invalid action")
            return
        cards_played = curplayer.play_action(action, self.cur_highest_card, self.pile_multiplier)
        self.cur_highest_card = max(cards_played)
        for card in cards_played:
            self.cards_played[card] = 1
            self.board_state[card] = 1
        self.last_player = self.current_player
        self.current_player = (self.current_player + 1) % 6
        self.board_state[53] = self.cur_highest_card
        self.board_state[54] = self.last_player
        self.board_state[55] = self.pile_multiplier
        self.board_state[56] = self.players_left
    def play_one_ai_turn(self):
        #greedy, plays lowest possible card(s) possible
        curplayer = self.players[self.current_player]
        action = curplayer.get_best_action(self.cur_highest_card, self.pile_multiplier)
        if(action == -1):
            self.current_player = (self.current_player + 1) % 6
            return
        cards_played = curplayer.play_action(action, self.cur_highest_card, self.pile_multiplier)
        self.cur_highest_card = max(cards_played)
        for card in cards_played:
            self.cards_played[card] = 1
            self.board_state[card] = 1
        self.last_player = self.current_player
        self.current_player = (self.current_player + 1) % 6
        self.board_state[53] = self.cur_highest_card
        self.board_state[54] = self.last_player
        self.board_state[55] = self.pile_multiplier
        self.board_state[56] = self.players_left
    def step(self, action: int):
        self.play_action(action)


def create_game():
    #card1,2,3,4,5,6,7,8,9, cur_highest_card, highest_left, current_player, last_player
    cards = [i for i in range(52)]

    state = []