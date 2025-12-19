from copy import deepcopy
import shogi
import shogi.KIF
from typing import List, Any, Dict

from mcts_gen.models.game_state import GameStateBase

class ShogiGameState(GameStateBase):
    """
    Implements the game state for Shogi using the python-shogi library.
    """

    def __init__(self, sfen: str = ""):
        if not sfen:
            self.board = shogi.Board()
        else:
            self.board = shogi.Board(sfen)

    def getCurrentPlayer(self) -> int:
        return 1 if self.board.turn == shogi.BLACK else -1

    def getPossibleActions(self) -> List[str]:
        """Returns a list of legal moves in USI string format."""
        return [move.usi() for move in self.board.legal_moves]

    def takeAction(self, action) -> "ShogiGameState":
        """Takes a shogi.Move object and returns the new state."""
        newState = deepcopy(self)
        newState.board.push_usi(action)
        return newState

    def isTerminal(self) -> bool:
        return self.board.is_game_over()

    def getReward(self) -> float:
        if not self.isTerminal():
            return 0.0

        if self.board.is_checkmate():
            return -1.0 if self.board.turn == shogi.BLACK else 1.0
        elif self.board.is_stalemate() or self.board.is_fourfold_repetition():
            return 0.0
        else:
            return 0.0

    def get_state_summary(self) -> Dict[str, str]:
        """
        Returns a summary of the current game state, including a KIF string with move history.
        """
        # python-shogi's kif_str() only gives the position, not the full move history.
        # We need to build the move list manually.
        kif_moves = []
        # We need a temporary board to correctly generate KIF move strings from the start
        temp_board = shogi.Board()
        for i, move in enumerate(self.board.move_stack):
            move_num = i + 1
            kif_move_str = shogi.KIF.Exporter.kif_move_from(move.usi(), temp_board)
            kif_moves.append(f"{move_num} {kif_move_str}")
            temp_board.push(move)

        return {"kif": "\n".join(kif_moves)}

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the game state to a dictionary for logging."""
        return {"sfen": self.board.sfen()}

    def __str__(self) -> str:
        return self.board.kif_str()
