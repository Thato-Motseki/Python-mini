import tempfile
import unittest
from pathlib import Path

from organizer import move_files, plan_moves


class FileOrganizerTests(unittest.TestCase):
    def test_planning_does_not_move_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = root / "Downloads"
            destination_dir = source_dir / "Organized"
            source_dir.mkdir()
            source_file = source_dir / "report.pdf"
            source_file.write_text("report")

            plan_moves(source_dir, destination_dir)

            self.assertTrue(source_file.is_file())
            self.assertFalse(destination_dir.exists())

    def test_plans_extension_folders_and_avoids_overwriting(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = root / "Downloads"
            destination_dir = root / "Organized"
            source_dir.mkdir()
            (source_dir / "notes.txt").write_text("new notes")
            (source_dir / "photo.JPG").write_text("photo")
            (source_dir / "LICENSE").write_text("license")
            existing_file = destination_dir / "txt" / "notes.txt"
            existing_file.parent.mkdir(parents=True)
            existing_file.write_text("keep these notes")

            moves = plan_moves(source_dir, destination_dir)
            destinations = {move.source.name: move.destination for move in moves}

            self.assertEqual(destinations["photo.JPG"], destination_dir / "jpg" / "photo.JPG")
            self.assertEqual(
                destinations["notes.txt"], destination_dir / "txt" / "notes (1).txt"
            )
            self.assertEqual(
                destinations["LICENSE"], destination_dir / "No extension" / "LICENSE"
            )
            self.assertEqual(existing_file.read_text(), "keep these notes")

    def test_move_files_moves_planned_files(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source_dir = root / "Downloads"
            destination_dir = root / "Organized"
            source_dir.mkdir()
            source_file = source_dir / "report.pdf"
            source_file.write_text("report")

            move_files(plan_moves(source_dir, destination_dir))

            self.assertFalse(source_file.exists())
            self.assertEqual((destination_dir / "pdf" / "report.pdf").read_text(), "report")


if __name__ == "__main__":
    unittest.main()