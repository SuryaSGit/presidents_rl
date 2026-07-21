from typing import List
import random
from typing import Optional
import numpy as np
import gymnasium as gym
from gymnasium.utils.env_checker import check_env
import torch
class playerstate:
    def __init__(self,cards):
        #52 dim vector storing whether or not hand has a certain card.
        self.cards = [0 for i in range(52)]
        for card in cards:
            self.cards[card] = 1
    def cards_left(self):
        return sum(self.cards)
    def get_state(self):
        return self.cards
    def get_num_from_action(self,action : int):
        if action <= 51:
            return action
        elif action <= 64:
            return action - 52
        elif action <= 77:
            return action - 65
        elif action <= 90:
            return action - 78
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
    def get_all_valid_actions(self, cur_highest : int, pile_multiplier : int):
        valid_actions = []
        for action in range(92):
            if self.check_valid_action(action, cur_highest, pile_multiplier):
                valid_actions.append(action)
        return valid_actions
    def check_valid_action(self, action : int, cur_highest : int, pile_multiplier : int):
        #0-51 = play that card
        #52-64 = play pair with that number
        #65-77 = play three of a kind with that number
        #78-90 = play four of a kind with that number
        #91 = pass
        if(action == 91):
            return True
        if action <= 51:
            if(action < cur_highest):
                return False
            if(pile_multiplier != -1 and pile_multiplier != 1):
                return False
            if(self.cards[action] != 0):
                return True
            return False
        cardnum = self.get_num_from_action(action)
        amount = self.get_amount_of_cards(cardnum)
        highest_card = self.get_highest_card_of_num(cardnum)
        if action <= 64:
            if(pile_multiplier != -1 and pile_multiplier != 2):
                return False
            if(amount > 1):
                if highest_card > cur_highest:
                    return True
        elif action <= 77:
            if(pile_multiplier != -1 and pile_multiplier != 3):
                return False
            if(amount > 2):
                if highest_card > cur_highest:
                    return True
        elif action <= 90:
            if(pile_multiplier != -1 and pile_multiplier != 4):
                return False
            if(amount > 3):
                if highest_card > cur_highest:
                    return True
        return False

    def play_action(self,action : int, cur_highest : int, pile_multiplier : int):
        cards_played = []
        if not self.check_valid_action(action, cur_highest, pile_multiplier):
            #print("Invalid action")
            a=1
        else:
            if action <= 51:
                self.cards[action] = 0
                cards_played.append(action)
            elif action <= 64:
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
            elif action <= 77:
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
            elif action <= 90:
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


def randomize_cards(cards : List[int], seed: Optional[int] = None):
    if seed is not None:
        random.seed(seed)
    result = [[] for _ in range(6)]
    cur = 0
    while cards:
        card = cards.pop(random.randint(0, len(cards) - 1))
        result[cur].append(card)
        cur += 1
        if(cur == 6):
            cur = 0
    if(len(result) != 6):
        print("Error in randomizing")
    return result
def get_string_from_card(index : int):
    suits = ["♦️", "♣️", "♥️", "♠️"]
    ranks = ["3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A", "2"]
    suit = suits[index % 4]
    rank = ranks[index // 4]
    return rank + suit
class stateManager:
    def __init__(self):
        self.reset()
    def reset(self, seed: Optional[int] = None):
        self.players = []
        self.board_state = []
        self.pile_multiplier = -1
        self.players_left = 6
        self.game_over = False
        self.place = -1
        self.cards_played = [0 for i in range(52)]
        cards = [i for i in range(52)]
        player_hands = randomize_cards(cards, seed)
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
        reward = 0
        if(self.current_player != 0):
            print("Not your turn")
            return -1
        curplayer = self.players[0]
        if not curplayer.check_valid_action(action, self.cur_highest_card, self.pile_multiplier):
            #print("Invalid action")
            return -1
        cards_played = curplayer.play_action(action, self.cur_highest_card, self.pile_multiplier)
        if(len(cards_played) == 0):
            #print("No cards played")
            self.current_player = (self.current_player + 1) % 6
            return 0
        if(curplayer.cards_left() == 0):
            self.players_left -= 1
            self.game_over = True
            self.place = self.players_left
        reward = reward + len(cards_played)
        self.update_pile_multiplier(action)
        self.cur_highest_card = max(cards_played)
        for card in cards_played:
            self.cards_played[card] = 1
            self.board_state[card] = 1
        self.last_player = self.current_player
        self.current_player = (self.current_player + 1) % 6
        return reward
    def update_board_state(self):
        for i in range(52):
            self.board_state[i] = self.cards_played[i]
        self.board_state[52] = self.cur_highest_card
        self.board_state[53] = self.last_player
        self.board_state[54] = self.pile_multiplier
        self.board_state[55] = self.players_left
    def get_board_state(self):
        self.update_board_state()
        return self.board_state
    def get_card_state(self):
        return self.players[0].get_state()
    def get_state(self):
        return self.get_card_state() + self.get_board_state()
    def print_cards(self, cards: List[int]):
        print("Player's Cards:")
        for i in range(52):
            if cards[i] == 1:
                print(get_string_from_card(i) + " ")
    def print_board(self):
        print("Cards Played:")
        for i in range(52):
            if self.board_state[i] == 1:
                print(get_string_from_card(i) + " ")
        if self.cur_highest_card != -1:
            print("Current highest card: " + get_string_from_card(self.cur_highest_card))
        else:
            print("Current highest card: None")
        print("Last player: " + str(self.last_player))
        print("Pile multiplier: " + str(self.pile_multiplier))
        print("Players left: " + str(self.players_left))
    def print_state(self):
        self.print_cards(self.get_card_state())
        self.print_board()
    def reset_stack(self):
        self.cur_highest_card = -1
        self.pile_multiplier = -1
        self.last_player = -1
    def update_pile_multiplier(self, action : int):
        if(action <= 51):
            self.pile_multiplier = 1
        elif(action <= 64):
            self.pile_multiplier = 2
        elif(action <= 77):
            self.pile_multiplier = 3
        else:
            self.pile_multiplier = 4
    def get_valid_moves(self):
        return self.players[self.current_player].get_all_valid_actions(self.cur_highest_card, self.pile_multiplier)
    def play_one_ai_turn(self):
        #greedy, plays lowest possible card(s) possible   
        if(self.current_player == self.last_player):
            #one full cycle of passes
            self.reset_stack()
        curplayer = self.players[self.current_player]
        #print("Existing Highest Card: " + get_string_from_card(self.cur_highest_card))
        action = curplayer.get_best_action(self.cur_highest_card, self.pile_multiplier)
        if(action == 91):
            self.current_player = (self.current_player + 1) % 6
            return
        cards_played = curplayer.play_action(action, self.cur_highest_card, self.pile_multiplier)
        if(self.pile_multiplier == -1):
            self.update_pile_multiplier(action)
        if(curplayer.cards_left() == 0):
            self.players_left -= 1
            if(self.players_left == 1):
                self.game_over = True
        if(len(cards_played) == 0):
            #print("No cards played")
            self.current_player = (self.current_player + 1) % 6
            return
        self.cur_highest_card = max(cards_played)
        #print("New Highest Card: " + get_string_from_card(self.cur_highest_card))
        for card in cards_played:
            self.cards_played[card] = 1
            #print("Card Played: " + get_string_from_card(card))
        self.last_player = self.current_player
        self.current_player = (self.current_player + 1) % 6
    def simulate_all_turns(self):
        while self.current_player != 0:
            self.play_one_ai_turn()
            if(self.game_over):
                break

    def step(self, action: int):
        reward = self.play_action(action)
        terminated = False
        if(self.game_over):
            reward = reward + self.place
            terminated = True
        else:
            self.simulate_all_turns()
            if(self.game_over):
                reward = (reward - 5) - self.players[0].cards_left()
                terminated = True
            if(self.last_player == self.current_player):
                reward += 2
                self.reset_stack()
        obs = self.get_state()
        return obs, reward, terminated, False, {}
class CustomEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = gym.spaces.Discrete(92)
        # State layout (108 dims):
        #   [0:52]   hand cards        -> 0/1
        #   [52:104] cards played      -> 0/1
        #   [104]    cur_highest_card  -> -1..51
        #   [105]    last_player       -> -1..5
        #   [106]    pile_multiplier   -> -1..4
        #   [107]    players_left      -> 1..6
        low = np.concatenate([np.zeros(104), np.array([-1, -1, -1, 1])]).astype(np.int64)
        high = np.concatenate([np.ones(104), np.array([51, 5, 4, 6])]).astype(np.int64)
        self.observation_space = gym.spaces.Box(low=low, high=high, dtype=np.int64)
        self.state_manager = stateManager()
    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        self.state_manager.reset(seed)
        #print(len(self.state_manager.get_state()))
        #for i in range(108):
            #print(self.state_manager.get_state()[i])
        return self.state_manager.get_state(), {}
    def step(self, action: int):
        return self.state_manager.step(action)
    def action_space_sample(self):
        possible_actions = self.state_manager.get_valid_moves()
        if(len(possible_actions) == 0):
            return 91
        return np.random.choice(possible_actions)
    def mask(self,tensor):
        valid_actions = self.state_manager.get_valid_moves()
        mask = torch.zeros(len(valid_actions),dtype=torch.bool)
        mask[valid_actions] = True
        flipped_mask = ~mask
        return tensor.masked_fill_(flipped_mask, -float("inf"))
    def getaction(self,tensor):
        new_tensor = self.mask(tensor)
        max_q_index = torch.argmax(new_tensor,dim=1)[0]
        return max_q_index.detach().item()

class GameWrapper:
    def __init__(self):
        self.game = stateManager()
        print("Starting Game State")
        self.game.print_state()
    def reset(self):
        return self.game.reset()
    def get_move(self):
        return int(input("Enter your move: "))
    def start_game(self):
        while not self.game.game_over:
            valid_actions = self.get_valid_moves()
            print(f"Valid actions: {valid_actions}")
            move = self.get_move()
            self.game.step(move)
            self.game.print_state()
        print("Game Over")
    def get_valid_moves(self):
        return self.game.get_valid_moves()


# try:
#     check_env(CustomEnv())
#     print("Environment passes all checks!")
# except Exception as e:
#     print(f"Environment has issues: {e}")

gym.register(
    id="gymnasium_env/presidents-rl",
    entry_point=CustomEnv,
    max_episode_steps=1000,  # Prevent infinite episodes
)