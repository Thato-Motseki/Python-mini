import shutil
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PlannedMove:
    source: Path
    destination: Path


def category_for(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    return suffix[1:] if suffix else "No extension"


def plan_moves(source_dir: Path, destination_dir: Path) -> list[PlannedMove]:
    moves = []
    reserved_destinations = set()

    for source in sorted(source_dir.iterdir(), key=lambda path: path.name.lower()):
        if not source.is_file() or source.is_symlink():
            continue

        target_dir = destination_dir / category_for(source)
        target = target_dir / source.name
        suffix_number = 1

        while target.exists() or target in reserved_destinations:
            target_name = f"{source.stem} ({suffix_number}){source.suffix}"
            target = target_dir / target_name
            suffix_number += 1

        reserved_destinations.add(target)
        moves.append(PlannedMove(source, target))

    return moves


def move_files(moves: list[PlannedMove]) -> None:
    for move in moves:
        move.destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(move.source), str(move.destination))
