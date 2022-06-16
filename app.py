"""monopoly-like game simulation."""

import random
from typing import List, Optional
from abc import ABC, abstractmethod


def roll_die() -> int:
    """Return an int between 1 and 6."""
    return random.randint(1, 6)


def coin_toss() -> bool:
    """Return True with 50% chance."""
    return random.random() >= 0.5


class AbstractPlayer(ABC):
    """Player abstract representation."""

    def __init__(self) -> None:
        """Initialize Player object with balance of 300 units."""
        self.balance: int = 300

    def get_balance(self) -> int:
        """Return Player balance."""
        return self.balance

    def increase_balance(self, amount_to_increase: int) -> None:
        """Increase Player balance by a certain amount."""
        self.balance += amount_to_increase

    def decrease_balance(self, amount_to_decrease: int) -> None:
        """Decrease Player balance by a certain amount."""
        self.balance -= amount_to_decrease

    @abstractmethod
    def decide_to_buy(self, property: 'Property') -> bool:
        """Determine Player willingness to buy a certain property."""
        pass


class ImpulsivePlayer(AbstractPlayer):
    """Impulsive player representation."""

    def decide_to_buy(self, property: 'Property') -> bool:
        """Determine Player willingness to buy a certain property."""
        return True


class DemandingPlayer(AbstractPlayer):
    """Demanding player representation."""

    def decide_to_buy(self, property: 'Property') -> bool:
        """Determine Player willingness to buy a certain property."""
        return property.get_rent_cost() > 50


class CautiousPlayer(AbstractPlayer):
    """Cautious player representation."""

    def decide_to_buy(self, property: 'Property') -> bool:
        """Determine Player willingness to buy a certain property."""
        return self.get_balance() >= property.get_sell_cost() + 80


class RandomPlayer(AbstractPlayer):
    """Random player representation."""

    def decide_to_buy(self, property: 'Property') -> bool:
        """Determine Player willingness to buy a certain property."""
        return coin_toss()


def transfer(
        p_from: AbstractPlayer,
        p_to: AbstractPlayer,
        amount: int) -> None:
    """Transfer a certain amount from p_from to p_to."""
    if p_from is not p_to:
        p_to.increase_balance(min(p_from.get_balance(), amount))
        p_from.decrease_balance(amount)


class Property:
    """Property representation."""

    def __init__(self, sell_cost: int, rent_cost: int):
        """Create Property object with sell_cost, rent_cost and no owner."""
        self.sell_cost: int = sell_cost
        self.rent_cost: int = rent_cost
        self.owner: Optional[AbstractPlayer] = None

    def has_owner(self) -> bool:
        """Determine whether a property is owned by someone."""
        return self.owner is not None

    def get_owner(self) -> Optional[AbstractPlayer]:
        """Retrieve this property's owner or None in case it has no owner."""
        return self.owner

    def set_owner(self, new_owner: Optional[AbstractPlayer]) -> None:
        """Set this property's owner."""
        self.owner = new_owner

    def get_rent_cost(self) -> int:
        """Retrieve this property's rent cost."""
        return self.rent_cost

    def get_sell_cost(self) -> int:
        """Retrieve this property's sell cost."""
        return self.sell_cost


def random_property(max_sell_cost: int, max_rent_cost: int) -> Property:
    """Create a random property with max_sell_cost and max_rent_cost."""
    sell_cost: int = random.randint(1, max_sell_cost)
    rent_cost: int = random.randint(1, max_rent_cost)

    return Property(sell_cost, rent_cost)


class Board:
    """Board representation."""

    def __init__(self, properties: List[Property]):
        """Create a Board instance based on a list of properties."""
        self.properties: List[Property] = properties

    def length(self) -> int:
        """Return the board length i.e its number of properties."""
        return len(self.properties)

    def property_at(self, board_position: int) -> Property:
        """Return the property object at a certain board position."""
        return self.properties[board_position]

    def get_properties(self) -> List[Property]:
        """Return the board's list of properties."""
        return self.properties


def random_board(max_sell_cost: int, max_rent_cost: int):
    """Generate a board instance consisting of 20 random properties."""
    properties: List[Property] = list()

    for i in range(0, 20):
        properties.append(random_property(max_sell_cost, max_rent_cost))

    return Board(properties)


class Game():
    """Game representation."""

    def __init__(self, board: Board, players: List[AbstractPlayer]):
        """Create Game instance with a board and a list of players."""
        self.board: Board = board
        self.players: List[AbstractPlayer] = players

        self.current_player: int = 0
        self.current_turn: int = 1
        self.player_position: List[int] = [0 for player in self.players]
        self.active_player: List[bool] = [True for player in self.players]

    def get_current_turn(self):
        """Return current turn number."""
        return self.current_turn

    def has_winner(self) -> Optional[AbstractPlayer]:
        """Return the winner if win condition is met, otherwise return None."""
        num_players: int = len(self.players)
        active_players: List[int] = [id for id in range(0, num_players)
                                     if self.active_player[id]]

        if len(active_players) == 1:
            active_player_id = active_players[0]

            return self.players[active_player_id]
        else:
            return None

    def player_with_highest_balance(self):
        """Return a player with highest balance."""
        max_balance: int = max(player.get_balance() for player in self.players)
        max_balance_players = filter(
            lambda p: p.get_balance() == max_balance,
            self.players
        )

        return list(max_balance_players)[0]

    def __stop_condtion(self) -> bool:
        return self.has_winner() or self.current_turn >= 1000

    def play(self):
        """Run consecutive turns until stop condition is met."""
        while not self.__stop_condtion():
            self.__turn()

    def __next_player_turn(self):
        self.current_player = (self.current_player + 1) % len(self.players)

        if not self.active_player[self.current_player]:
            self.__next_player_turn()

    def __adjust_position_to_length(self, player_id: int) -> bool:
        board_length = self.board.length()

        if self.player_position[player_id] >= board_length:
            self.player_position[player_id] %= board_length

            return True
        else:
            return False

    def __apply_defeat_to(self, player_id: int) -> None:
        self.active_player[player_id] = False

        for property in self.board.get_properties():
            if property.get_owner() is self.players[player_id]:
                property.set_owner(None)

    def __turn(self):
        player_id: int = self.current_player
        player: AbstractPlayer = self.players[player_id]
        die_roll: int = roll_die()

        self.player_position[player_id] += die_roll

        completed_track: bool = self.__adjust_position_to_length(player_id)

        if completed_track:
            player.increase_balance(100)

        property = self.board.property_at(self.player_position[player_id])

        if property.has_owner():
            transfer(
                player,
                property.get_owner(),
                property.get_rent_cost()
            )

            if player.get_balance() < 0:
                self.__apply_defeat_to(player_id)

        else:
            if (player.get_balance() >= property.get_sell_cost()
                    and player.decide_to_buy(property)):
                property.set_owner(player)

                player.decrease_balance(property.get_sell_cost())

        self.current_turn += 1
        self.__next_player_turn()


def random_game(
        max_sell_cost: int,
        max_rent_cost: int,
        players: List[AbstractPlayer]):
    """Generate a game with some players and random properties."""
    board = random_board(max_sell_cost, max_rent_cost)

    return Game(board, players)


class GameRunner:
    """Game runner representation."""

    def __init__(
            self,
            players: List[AbstractPlayer],
            max_sell_cost: int,
            max_rent_cost: int
    ):
        """Initialize GameRunner instance with a set of players."""
        self.players: List[AbstractPlayer] = players
        self.max_sell_cost: int = max_sell_cost
        self.max_rent_cost: int = max_rent_cost
        self.games_simulated: int = 0
        self.timed_out_games: int = 0
        self.num_turns: List[int] = []
        self.winner: List[AbstractPlayer] = []
        self.wins_per_behavior = {behavior: 0
                                  for behavior in [
                                          ImpulsivePlayer,
                                          DemandingPlayer,
                                          CautiousPlayer,
                                          RandomPlayer,
                                          type(None)]}

    def get_average_num_turns(self) -> int:
        """Retrieve average number of turns of a simulated game."""
        return sum(self.num_turns) / len(self.num_turns)

    def get_win_percentage_per_behavior(self):
        """Retrieve percentage of games won by an AbstractPlayer subclass."""
        result = dict()
        for behavior, wins in self.wins_per_behavior.items():
            result[behavior] = wins / self.games_simulated

        result.pop(type(None))

        return result

    def get_timed_out_games(self) -> int:
        """Retrieve number of timed out games."""
        return self.timed_out_games

    def play_game(self):
        """Run a Game instance and register its outcome."""
        game = random_game(
            self.max_sell_cost,
            self.max_rent_cost,
            self.players
        )

        game.play()

        self.games_simulated += 1

        winner = game.has_winner()

        if winner is None:
            self.timed_out_games += 1
            self.winner.append(game.player_with_highest_balance())
        else:
            self.winner.append(winner)

        self.num_turns.append(game.get_current_turn())

        self.wins_per_behavior[type(winner)] += 1


def report(
        max_sell_cost: int,
        max_rent_cost: int,
        num_games_to_play: int) -> None:
    """Generate Report."""
    players = [
        ImpulsivePlayer(),
        DemandingPlayer(),
        CautiousPlayer(),
        RandomPlayer()
    ]

    game_runner = GameRunner(players, max_sell_cost, max_rent_cost)

    for i in range(num_games_to_play):
        game_runner.play_game()

    timed_out_games = game_runner.get_timed_out_games()

    average_num_turns = game_runner.get_average_num_turns()

    win_percentage_per_behavior = game_runner.get_win_percentage_per_behavior()

    most_successful_behavior = max(
        win_percentage_per_behavior,
        key=win_percentage_per_behavior.get
    )

    print("timed out games: ", timed_out_games)
    print("average num turns: ", average_num_turns)

    print("win percentage per behavior:")
    for behavior, percentage in win_percentage_per_behavior.items():
        print("behavior ", behavior, ": ", percentage)

    print("most successful behavior: ", most_successful_behavior)


if __name__ == "__main__":
    report(300, 80, 300)
    # another interesting experiment in which demanding player is
    # dominant
    # report(2000, 80, 300)
