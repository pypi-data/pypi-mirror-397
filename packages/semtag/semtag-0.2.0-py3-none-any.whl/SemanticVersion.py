"""
Semantic versioning module for parsing and bumping ver_list numbers
More about semantic versioning: https://semver.org/
"""
import re

class SemanticVersion:
  """Handle semantic versioning parsing and incrementing"""
  def __init__(self, version_string: str):
    self.original = version_string
    self.prefix = ""
    self.major = 0
    self.minor = 0
    self.patch = 0
    self.label = ""
    self._parse(version_string)

  def _parse(self, version_string: str):
    """Parse and validate semantic version string"""
    # 'v' prefix handling
    if version_string.startswith('v'):
      self.prefix = 'v'
      version_string = version_string[1:]

    # regex from semver.org
    pattern = r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    match = re.match(pattern, version_string)
    
    if not match:
      raise ValueError(f"Invalid semantic version format: {self.original}")
    
    self.major = int(match.group('major'))
    self.minor = int(match.group('minor'))
    self.patch = int(match.group('patch'))
    self.label = match.group('prerelease') or ""

  def inc_major(self, by=1) -> 'SemanticVersion':
    """ Increment major version and reset minor & patch"""
    self.major += by
    self.minor = 0
    self.patch = 0
    self.label = ""
    return self
  
  def inc_minor(self, by=1) -> 'SemanticVersion':
    """ Increment minor version and reset patch"""
    self.minor += by
    self.patch = 0
    self.label = ""
    return self
  
  def inc_patch(self, by=1) -> 'SemanticVersion':
    """ Increment patch - preserve major & minor"""
    self.patch += by
    self.label = ""
    return self
  
  def add_label(self, label: str) -> 'SemanticVersion':
    """Add a label to the version"""
    self.label = label
    return self
  
  def __str__(self) -> str:
    """Return concatinated string"""
    version = f"{self.prefix}{self.major}.{self.minor}.{self.patch}"
    if self.label:
      version += f"-{self.label}"
    return version
  
  def __repr__(self) -> str:
    """Return representation of version"""
    return f"SemanticVersion('{str(self)}')"


### This is standalone function (could be @staticmethod as well) ###
def semsort(versions: list[str]) -> list[str]:
  """Sort semantic version tags by major, minor, patch """
  ver_list = []
  for v in versions:
    try:
      version = SemanticVersion(v)
      ver_list.append((v, version))
    except ValueError:
      # Skip invalid semantic version tags
      continue

  ver_list.sort(
    key=lambda x: (x[1].major, x[1].minor, x[1].patch),
    reverse=True
  )
  return [x for x, _ in ver_list]
