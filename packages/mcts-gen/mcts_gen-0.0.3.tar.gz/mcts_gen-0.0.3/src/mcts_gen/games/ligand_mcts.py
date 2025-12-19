"""
This module implements the GameState for de novo ligand generation, guided
by a protein pocket point cloud. It is designed to be dynamically loaded by the
mcts-gen framework.

**Dependencies:**

*   **Python Libraries:** RDKit, SciPy, NumPy
    -   `uv pip install rdkit scipy numpy` (or `pip install ...`)

*   **External Tool: fpocket:** This program is required to identify the binding
    pocket from a protein structure file (e.g., PDB). The output of fpocket
    (a PDB file of the pocket) is used as the `pocket_path` input for this module.

    **Installation (Ubuntu/Debian):**
    ```bash
    sudo snap install fpocket
    ```

    **Usage Example:**
    1.  Run fpocket on your protein: `fpocket -f your_protein.pdb`
    2.  This creates a results directory, e.g., `your_protein_out/pockets/`.
    3.  Use the largest pocket's PDB file as input for the `pocket_path` argument.
       (e.g., `pocket_path='your_protein_out/pockets/pocket1_atm.pdb'`)

**Fragment Generation:**

This module generates chemical fragments dynamically from a user-provided source
molecule file. Use the `source_molecule_path` argument to specify the path to your
file. Supported formats are:
-   `.smi` / `.smiles`: SMILES format
-   `.sdf`: Structure-Data File format
-   `.csv`: A CSV file with a 'smiles' column

If `source_molecule_path` is not provided, a small default library of fragments
will be used.

**Tool-Specific Behavior:**

*   When used with the `get_principal_variation` tool, the `final_state_summary`
    in the tool's output will contain the SMILES string of the best molecule
    and a `pdb_path` key pointing to a saved PDB file of its 3D structure.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
import os
import numpy as np
import pandas as pd

from mcts_gen.models.game_state import GameStateBase

# Attempt to import RDKit and SciPy, but do not fail if they are not present.
# A runtime check in the GameState constructor will handle their absence.
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, QED, BRICS
except ImportError:
    Chem = None

try:
    from scipy.spatial import cKDTree
except ImportError:
    cKDTree = None


# --- Helper Functions for Molecule and Fragment Handling ---

def _load_molecules_from_file(file_path: str) -> List[Any]:
    """
    (T008) Loads molecules from a file, supporting .smi, .sdf, and .csv formats.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source molecule file not found at: {file_path}")

    ext = os.path.splitext(file_path)[1]
    molecules = []

    try:
        if ext in ['.smi', '.smiles']:
            suppl = Chem.SmilesMolSupplier(file_path, titleLine=False)
            molecules = [mol for mol in suppl if mol is not None]
        elif ext == '.sdf':
            suppl = Chem.SDMolSupplier(file_path)
            molecules = [mol for mol in suppl if mol is not None]
        elif ext == '.csv':
            df = pd.read_csv(file_path)
            smiles_col = next((col for col in df.columns if col.lower() == 'smiles'), None)
            if not smiles_col:
                raise ValueError("CSV file must have a 'smiles' column.")
            molecules = [Chem.MolFromSmiles(smi) for smi in df[smiles_col] if isinstance(smi, str)]
            molecules = [mol for mol in molecules if mol is not None]
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        if not molecules:
            raise ValueError(f"No valid molecules could be loaded from {file_path}.")

    except Exception as e:
        raise ValueError(f"Failed to process file {file_path}: {e}") from e

    return molecules

def _generate_fragments_from_molecules(molecules: List[Any]) -> List[str]:
    """
    (T009) Generates a unique set of chemical fragments from a list of molecules using the BRICS algorithm,
    filters by size, and pre-validates that each fragment can form a 3D conformation.
    """
    if not Chem:
        raise ImportError("RDKit is required for fragmentation.")
    
    all_fragments_smiles = set()
    for mol in molecules:
        fragments = BRICS.BRICSDecompose(mol)
        all_fragments_smiles.update(fragments)
    
    validated_fragments = []
    max_heavy_atoms = 20  # Define a threshold for fragment size
    for smiles in sorted(list(all_fragments_smiles)):
        try:
            frag_mol = Chem.MolFromSmiles(smiles)
            if frag_mol is None:
                continue
            
            # Filter out fragments that are too large
            if frag_mol.GetNumHeavyAtoms() > max_heavy_atoms:
                continue

            # Pre-validate that a 3D conformation can be generated
            frag_mol_with_hs = Chem.AddHs(frag_mol)
            if AllChem.EmbedMolecule(frag_mol_with_hs, AllChem.ETKDGv3()) == -1:
                # EmbedMolecule returns -1 on failure
                continue
            
            validated_fragments.append(smiles)
        except Exception:
            # Ignore fragments that cause any error during validation
            continue
            
    return validated_fragments


# --- Data Classes ---

@dataclass(frozen=True)
class LigandAction:
    """
    Represents a discrete action to modify a molecule, such as adding a chemical
    fragment. This class is immutable.

    Attributes:
        frag_smiles: The SMILES string of the fragment to add.
        attach_idx: The index of the atom on the existing molecule to connect to.
    """
    frag_smiles: str
    attach_idx: Optional[int] = None

    def __repr__(self) -> str:
        """Provides a clear string representation of the action."""
        return f"LigandAction(frag='{self.frag_smiles}', attach_at={self.attach_idx})"


@dataclass
class LigandState:
    """
    Represents the state of a partially or fully constructed molecule within the
    MCTS search.

    Attributes:
        mol: The RDKit molecule object. Can be None for the initial empty state.
        history: A list of LigandActions taken to reach this state.
        max_atoms: The number of heavy atoms at which the state is considered terminal.
        fragment_library: A list of SMILES strings for allowed fragments.
    """
    mol: Optional[Any] = None
    history: List[LigandAction] = field(default_factory=list)
    max_atoms: int = 50
    fragment_library: List[str] = field(default_factory=lambda: ["C", "N", "O", "c1ccccc1", "C(=O)O"])

    def to_smiles(self) -> str:
        """Returns the SMILES representation of the current molecule."""
        if self.mol and Chem:
            return Chem.MolToSmiles(self.mol)
        return ""

    def clone(self) -> "LigandState":
        """Creates a deep copy of the current state for exploration."""
        new_mol = Chem.Mol(self.mol) if self.mol and Chem else None
        return LigandState(
            mol=new_mol, 
            history=list(self.history), 
            max_atoms=self.max_atoms,
            fragment_library=self.fragment_library
        )

    def is_terminal(self) -> bool:
        """Checks if the state is terminal (molecule has reached max size)."""
        if not self.mol or not Chem:
            return False
        return self.mol.GetNumAtoms() >= self.max_atoms

    def legal_actions(self) -> List[LigandAction]:
        """
        (T011, T012) Returns a list of possible actions (fragment additions) from the fragment library.
        """
        if not self.fragment_library:
            return []
            
        actions = []
        if not self.mol or not Chem:
            # If there's no molecule, actions create one from a fragment.
            for frag in self.fragment_library:
                actions.append(LigandAction(frag_smiles=frag))
        else:
            # This prototype attaches to the first few atoms for simplicity.
            num_attach_points = min(4, self.mol.GetNumAtoms())
            for i in range(num_attach_points):
                for frag in self.fragment_library:
                    actions.append(LigandAction(frag_smiles=frag, attach_idx=i))
        return actions

    def apply_action(self, action: LigandAction) -> "LigandState":
        """
        Applies an action to create a new molecular state.

        Returns:
            A new LigandState instance representing the state after the action.
        """
        if not Chem:
            raise RuntimeError("RDKit is not available, cannot apply action.")

        new_state = self.clone()
        frag = Chem.MolFromSmiles(action.frag_smiles)
        if not frag:
            return new_state  # Invalid fragment SMILES, return original state

        if not new_state.mol:
            # First action: the new state's molecule is just the fragment.
            new_state.mol = frag
        else:
            # NOTE: This is a simplified combination that creates a molecule with
            # two disconnected components. A production-level implementation
            # would use RDKit's reaction system to form a proper covalent bond
            # between the existing molecule and the new fragment.
            combo = Chem.CombineMols(new_state.mol, frag)
            new_state.mol = combo
        
        new_state.history.append(action)
        return new_state


# --- Utility Functions ---

def load_pocket_atm_pdb(path: str) -> np.ndarray:
    """
    Loads the 3D coordinates of atoms from a PDB file, targeting lines that
    start with "ATOM" or "HETATM".

    Args:
        path: The file path to the PDB file.

    Returns:
        A NumPy array of shape (N, 3) containing the 3D coordinates.
    """
    if not isinstance(path, str):
        raise TypeError("File path must be a string.")
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Pocket file not found at {path}")
        return np.array([])

    points = []
    for line in lines:
        if line.startswith(("ATOM", "HETATM")):
            try:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                points.append([x, y, z])
            except (ValueError, IndexError):
                continue  # Ignore malformed lines
    return np.array(points)


def mol_to_points(mol: Any) -> np.ndarray:
    """
    Converts an RDKit molecule to a 3D point cloud of its heavy atoms.
    If the molecule lacks a 3D conformation, one is generated.

    Args:
        mol: The RDKit molecule object.

    Returns:
        A NumPy array of shape (N, 3) for the heavy atom coordinates.
    """
    if not Chem or not mol:
        return np.array([])

    if mol.GetNumConformers() == 0:
        try:
            mol_with_hs = Chem.AddHs(mol)
            if AllChem.EmbedMolecule(mol_with_hs, AllChem.ETKDGv3()) == -1:
                return np.array([]) # Failed to embed
            AllChem.UFFOptimizeMolecule(mol_with_hs)
            mol = Chem.RemoveHs(mol_with_hs)
        except Exception:
            # RDKit can throw a variety of errors here, including Invariant Violation
            return np.array([])

    conformer = mol.GetConformer()
    points = [
        [pos.x, pos.y, pos.z]
        for atom in mol.GetAtoms()
        if atom.GetAtomicNum() > 1  # Ignore hydrogen atoms
        for pos in [conformer.GetAtomPosition(atom.GetIdx())]
    ]
    return np.array(points)


# --- Scoring Functions ---

def usr_descriptor(points: np.ndarray) -> np.ndarray:
    """
    Calculates the Ultrafast Shape Recognition (USR) descriptor for a point cloud.
    The descriptor contains the mean and standard deviation of distances from the
    centroid, providing a compact representation of the cloud's shape.

    Args:
        points: A NumPy array of shape (N, 3).

    Returns:
        A 3-element NumPy array containing [mean, std_dev, max_dist].
    """
    if points.ndim != 2 or points.shape[0] == 0:
        return np.zeros(3)
    centroid = points.mean(axis=0)
    distances = np.linalg.norm(points - centroid, axis=1)
    return np.array([distances.mean(), distances.std(), distances.max()])


def gaussian_overlap(points_a: np.ndarray, points_b: np.ndarray, sigma: float = 1.0) -> float:
    """
    Calculates the Gaussian overlap between two point clouds, a measure of
    3D shape similarity.

    Args:
        points_a: The first point cloud.
        points_b: The second point cloud.
        sigma: The width of the Gaussian.

    Returns:
        A float representing the normalized overlap score.
    """
    if points_a.size == 0 or points_b.size == 0:
        return 0.0

    if cKDTree and points_a.shape[0] * points_b.shape[0] > 100_000:
        tree = cKDTree(points_b)
        cutoff = 3.0 * sigma
        total_overlap = 0.0
        for point_a in points_a:
            indices = tree.query_ball_point(point_a, cutoff)
            if not indices:
                continue
            d_sq = np.sum((points_b[indices] - point_a) ** 2, axis=1)
            total_overlap += np.sum(np.exp(-d_sq / (2.0 * sigma**2)))
    else:
        d_sq = np.sum((points_a[:, np.newaxis, :] - points_b[np.newaxis, :, :]) ** 2, axis=2)
        total_overlap = float(np.sum(np.exp(-d_sq / (2.0 * sigma**2))))

    return total_overlap / np.sqrt(points_a.shape[0] * points_b.shape[0])


# --- Core Logic ---

class Evaluator:
    """
    Scores a molecule based on shape complementarity to a protein pocket and
    desirable chemical properties.

    Attributes:
        pocket_points: A NumPy array of the target pocket's 3D coordinates.
        pocket_usr: The USR descriptor of the target pocket.
        sigma: The sigma value for Gaussian overlap calculations.
        weights: A dictionary of weights for combining different score components.
    """

    def __init__(self, pocket_path: str, sigma: float = 1.0):
        if not pocket_path or not isinstance(pocket_path, str):
            raise ValueError("A valid pocket_path string must be provided.")
        
        self.pocket_points = load_pocket_atm_pdb(pocket_path)
        if self.pocket_points.size == 0:
            raise ValueError(f"Could not load pocket points from {pocket_path}.")

        self.pocket_usr = usr_descriptor(self.pocket_points)
        self.sigma = sigma

        self.weights = {
            "shape": 1.0,
            "gaussian": 1.0,
            "logp": -0.2,
            "qed": 2.0,
            "penalty": -1.0,
        }

    def shape_score(self, mol: Any) -> float:
        """Calculates a shape similarity score based on USR descriptors."""
        mol_points = mol_to_points(mol)
        if mol_points.size == 0:
            return 0.0
        
        mol_usr = usr_descriptor(mol_points)
        dist = np.linalg.norm(mol_usr - self.pocket_usr)
        return 1.0 / (1.0 + dist)

    def gaussian_score(self, mol: Any) -> float:
        """Calculates the 3D Gaussian overlap score."""
        mol_points = mol_to_points(mol)
        if mol_points.size == 0:
            return 0.0
        return gaussian_overlap(mol_points, self.pocket_points, self.sigma)

    def _chemical_penalties(self, mol: Any) -> float:
        """
        Calculates scores and penalties based on chemical properties (QED, LogP)
        and basic structural rules.
        """
        if not Chem or not mol:
            return self.weights.get("penalty", -1.0)
        
        try:
            if not (50 < Descriptors.ExactMolWt(mol) < 800):
                return self.weights.get("penalty", -1.0)
            
            qed_score = QED.qed(mol)
            logp_score = Descriptors.MolLogP(mol)
            
            # Penalize deviation from an ideal logP of ~2.5
            logp_penalty = self.weights.get("logp", -0.2) * abs(logp_score - 2.5)
            
            return self.weights.get("qed", 2.0) * qed_score + logp_penalty

        except Exception:
            # Catches errors from RDKit functions (e.g., sanitization)
            return self.weights.get("penalty", -1.0)

    def total_score(self, mol: Any) -> float:
        """
        Calculates the final weighted score for a molecule, combining shape,
        Gaussian overlap, and chemical property scores.
        """
        chem_score = self._chemical_penalties(mol)
        if chem_score < 0:
            return chem_score

        shape = self.shape_score(mol)
        gaussian = self.gaussian_score(mol)

        return (self.weights.get("shape", 1.0) * shape +
                self.weights.get("gaussian", 1.0) * gaussian +
                chem_score)


class LigandMCTSGameState(GameStateBase):
    """
    GameState implementation for ligand generation that fits the mcts-gen framework.
    This class orchestrates the state transitions and reward calculations for the
    ligand generation "game".

    Attributes:
        evaluator: An Evaluator instance used for scoring.
        internal_state: The LigandState object holding the current molecule.
    """
    def __init__(
        self, 
        pocket_path: Optional[str] = None, 
        source_molecule_path: Optional[str] = None, # (T007)
        internal_state: Optional[LigandState] = None, 
        evaluator: Optional[Evaluator] = None
    ):
        if not Chem:
            raise ImportError("RDKit is required for ligand generation but is not installed. Please run 'pip install rdkit-pypi'.")

        if evaluator:
            self.evaluator = evaluator
        else:
            if not pocket_path:
                raise ValueError("A pocket_path must be provided if an evaluator is not given.")
            self.evaluator = Evaluator(pocket_path)
        
        # (T010) Initialize fragment library and internal state
        if internal_state:
            self.internal_state = internal_state
        else:
            fragment_library = None
            if source_molecule_path:
                try:
                    print(f"Attempting to generate fragments from source: {source_molecule_path}")
                    molecules = _load_molecules_from_file(source_molecule_path)
                    fragment_library = _generate_fragments_from_molecules(molecules)
                    print(f"Successfully generated {len(fragment_library)} unique fragments.")
                except Exception as e:
                    print(f"\n[Warning] Failed to generate fragments from '{source_molecule_path}': {e}")
                    print("[Info] Falling back to the default fragment library.\n")
                    fragment_library = None  # Ensure fallback is triggered
            
            if fragment_library:
                self.internal_state = LigandState(fragment_library=fragment_library)
            else:
                # Fallback to default empty state
                self.internal_state = LigandState()


    def getCurrentPlayer(self) -> int:
        """Returns the current player. Always 1 for this single-player 'game'."""
        return 1

    def isTerminal(self) -> bool:
        """Delegates the terminal state check to the internal LigandState."""
        return self.internal_state.is_terminal()

    def getPossibleActions(self) -> List[LigandAction]:
        """Delegates action generation to the internal LigandState."""
        return self.internal_state.legal_actions()

    def takeAction(self, action: LigandAction) -> "LigandMCTSGameState":
        """
        Applies an action and returns a new game state.

        Args:
            action: The LigandAction to apply.

        Returns:
            A new LigandMCTSGameState instance representing the subsequent state.
        """
        if not isinstance(action, LigandAction):
            raise TypeError("Action must be an instance of LigandAction.")

        new_internal_state = self.internal_state.apply_action(action)
        return LigandMCTSGameState(internal_state=new_internal_state, evaluator=self.evaluator)

    def getReward(self) -> float:
        """
        Returns the reward for the current state. The reward is only calculated
        for a terminal state, otherwise it's 0.
        """
        if not self.isTerminal():
            return 0.0
        
        return self.evaluator.total_score(self.internal_state.mol)

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Saves the current molecule to a PDB file and returns a summary.
        """
        summary = {"smiles": self.internal_state.to_smiles()}
        if self.internal_state.mol:
            try:
                # Ensure output directory exists
                os.makedirs("mcts_output", exist_ok=True)
                pdb_path = "mcts_output/best_molecule.pdb"
                Chem.MolToPDBFile(self.internal_state.mol, pdb_path)
                summary["pdb_path"] = pdb_path
            except Exception as e:
                summary["error"] = f"Failed to save PDB file: {e}"
        return summary

    def __repr__(self) -> str:
        """Provides a developer-friendly representation of the game state."""
        smiles = self.internal_state.to_smiles()
        return f'LigandMCTSGameState(smiles="{smiles}")'