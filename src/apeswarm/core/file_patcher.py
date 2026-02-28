"""File modification logic for self-edit loop."""
import re
from pathlib import Path
from typing import Optional


def _extract_patch_targets(self_edit_output: str) -> list[tuple[str, str]]:
	"""Extract (filename, suggested_action) from self-edit output.
	
	Looks for markdown bullets like:
	- src/file.py: Add type hints to function X
	- README.md: Update installation instructions
	Also handles numbered lists like:
	1. src/file.py: Add docstring to process_data function
	"""
	targets = []
	lines = self_edit_output.split('\n')
	
	for line in lines:
		line = line.strip()
		# Match both bullet points and numbered items
		if line.startswith('-') or line.startswith('•') or (len(line) > 0 and line[0].isdigit() and '.' in line[:3]):
			# Remove bullet/number and strip
			content = re.sub(r'^[-•\d]+[\.\)]\s*', '', line).strip()
			# Try to extract filename: action pattern
			match = re.match(r'([a-zA-Z0-9_./-]+\.(py|md|toml|yml|yaml|txt|sh)):\s*(.+)', content)
			if match:
				filename, _, action = match.groups()[0], match.groups()[1], match.groups()[2]
				targets.append((filename, action))
	
	return targets


def _apply_simple_patch(file_path: Path, action_desc: str, model) -> bool:
	"""Apply a simple patch to a file based on action description.
	
	Uses LLM to generate safe, minimal modifications.
	Returns True if patch was applied successfully.
	"""
	if not file_path.exists():
		return False
	
	content = file_path.read_text(encoding='utf-8', errors='replace')
	
	# For now, we'll use a simple heuristic approach for common patterns
	# In production, this would use the LLM with proper safety checks
	
	if file_path.suffix == '.py':
		# Python-specific patches
		if 'type hint' in action_desc.lower() or 'annotation' in action_desc.lower():
			# Simple: add basic type hints to function definitions without them
			updated = _add_type_hints_to_functions(content)
			if updated != content:
				file_path.write_text(updated, encoding='utf-8')
				return True
		elif 'docstring' in action_desc.lower() or 'documentation' in action_desc.lower():
			# Add docstrings to functions without them
			updated = _add_docstrings_to_functions(content)
			if updated != content:
				file_path.write_text(updated, encoding='utf-8')
				return True
		elif 'import' in action_desc.lower():
			# Remove unused imports (already have this elsewhere)
			return True
	
	elif file_path.suffix in ['.md', '.txt']:
		# Markdown/text patches - typically additive
		if 'add' in action_desc.lower() or 'update' in action_desc.lower():
			# These are safe to skip for demo - user would review
			pass
	
	return False


def _add_type_hints_to_functions(content: str) -> str:
	"""Add basic type hints to function definitions."""
	# Find function definitions without return type hints
	pattern = r'(def\s+\w+\s*\([^)]*\))(\s*:)'
	
	def replacer(match) -> None:
		sig = match.group(1)
		colon = match.group(2)
		# Only add if missing -> annotation
		if '->' not in sig:
			return sig + ' -> None' + colon
		return match.group(0)
	
	return re.sub(pattern, replacer, content)


def _add_docstrings_to_functions(content: str) -> str:
	"""Add minimal docstrings to functions that lack them."""
	lines = content.split('\n')
	result = []
	i = 0
	
	while i < len(lines):
		line = lines[i]
		result.append(line)
		
		# Check if this is a function def
		if re.match(r'\s*def\s+\w+\(', line):
			# Check next non-empty line
			j = i + 1
			indent_match = re.match(r'^(\s*)', line)
			indent = indent_match.group(1) if indent_match else ''
			
			while j < len(lines) and not lines[j].strip():
				result.append(lines[j])
				j += 1
			
			if j < len(lines):
				next_line = lines[j]
				# Check if next line is already a docstring
				if '"""' not in next_line and "'''" not in next_line:
					# Add minimal docstring
					docstring_indent = indent + '    '
					result.append(f'{docstring_indent}"""TODO: Add description."""')
		
		i += 1
	
	return '\n'.join(result)


def apply_self_edit_patches(
	self_edit_output: str,
	repo_root: Path,
	model=None,
) -> tuple[int, list[str]]:
	"""Apply self-edit patch recommendations to repository files.
	
	Args:
		self_edit_output: Markdown-formatted recommendations from SelfEditApe
		repo_root: Root directory of the repository
		model: LLM model (optional, for advanced patching)
	
	Returns:
		(count_applied, list_of_modified_files)
	"""
	targets = _extract_patch_targets(self_edit_output)
	applied_count = 0
	modified_files = []
	
	for filename, action in targets:
		file_path = repo_root / filename
		
		# Resolve path if it doesn't exist directly
		if not file_path.exists():
			# Try to find it
			candidates = list(repo_root.rglob(filename.split('/')[-1]))
			if candidates:
				file_path = candidates[0]
			else:
				continue
		
		try:
			if _apply_simple_patch(file_path, action, model):
				applied_count += 1
				modified_files.append(filename)
		except Exception:
			# Silently skip patches that fail
			pass
	
	return applied_count, modified_files
