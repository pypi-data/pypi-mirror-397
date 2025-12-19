#!/usr/bin/env python3
"""
SemTag - A tool for managing semantic version tags in git repositories
"""

import argparse
import logging
# import sys
from SemanticVersion import SemanticVersion, semsort
import git
from pathlib import Path

logger = logging.getLogger(__name__)

def main():
  """ Main function """
  ########################
  ### Argument Parsing ###
  ########################
  parser = argparse.ArgumentParser(
    description='SemTag - Manage semantic version tags in git repositories',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  %(prog)s -m              # Increment minor version (1.0.0 -> 1.1.0)
  %(prog)s -M              # Increment major version (1.0.0 -> 2.0.0)
  %(prog)s -p -b 5         # Increment patch version by 5 (1.0.0 -> 1.0.5)
  %(prog)s -p -l rc1       # Increment patch and add label (1.0.0 -> 1.0.1-rc1)
        """
  )
  parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbosity (-v for INFO, -vv for DEBUG)')
  # parser.add_argument('-f', '--force', action='store_true', default=False, help='Force the operation even if not on main/master branch')
  parser.add_argument('-b', '--by', action='store', type=int, default=1, help='Increment by a specific number')
  
  version_group = parser.add_mutually_exclusive_group(required=True)
  version_group.add_argument('-p', '--patch', action='store_true', help='Increment patch version (x.x.PATCH)')
  version_group.add_argument('-m', '--minor', action='store_true', help='Increment minor version (x.MINOR.0)')
  version_group.add_argument('-M', '--major', action='store_true', help='Increment major version (MAJOR.0.0)')
  
  parser.add_argument('-l', '--label', type=str, default=None, help='Add label to the version (e.g., -l rc1 creates 1.0.0-rc1)')
  parser.add_argument('-u', '--push', action='store_true', help='Push the new tag to remote repository', default=False)
  parser.add_argument('-U', '--pushall', action='store_true', help='Push all local tags to remote repository', default=False)
  parser.add_argument('-n', '--no-fetch', action='store_true', help='Do not fetch tags from remote before operation', default=False)
  args = parser.parse_args()
  
  ### Logging based on verbosity ###
  if args.verbose == 0:
    log_level = logging.WARNING
  elif args.verbose == 1:
    log_level = logging.INFO
  else:
    log_level = logging.DEBUG
  
  logging.basicConfig(
    level=log_level,
    format='%(message)s' # Keep it simple (no timestamps, severity etc.)
  )
  
  ##################
  ### Main Logic ###
  ##################
  logger.debug(f"Arguments: {args}")
  pwd = Path('.').resolve()

  ### Check if this is a git workspace ###
  try:
    repo = git.Repo(pwd, search_parent_directories=True)
    logger.debug(f"Found git repository at {repo.working_dir}")
  except git.InvalidGitRepositoryError:
    logger.error(f"{pwd} is not a git repository")
    exit(1)
  except git.GitCommandError as e:
    logger.error(f"Git command failed: {e}")
    exit(99)
  
  reponame = Path(repo.working_dir).name
  logger.info(f"Repository name : {reponame}")
  
  ## Check if on main/master branch (warning only)
  # try:
  #   if repo.active_branch.name not in ['main', 'master']:
  #     logger.warning(f"You are on branch '{repo.active_branch.name}', not on main/master")
  #   logger.debug(f"On {repo.active_branch.name} branch")
  # except TypeError:
  #   logger.warning("HEAD is detached, not on any branch")
  #   exit(2)
  

  # Fetch tags from remote to avoid duplicates
  if not args.no_fetch:
    try:
      logger.debug("Fetching tags from remote...")
      repo.remotes.origin.fetch(tags=True)
      logger.info("Tags fetched successfully")
    except Exception as e:
      logger.warning(f"Error fetching tags: {e}")
    
  logger.debug(f"Tags in repository: {repo.tags}")
  tags = semsort([tag.name for tag in repo.tags])
  logger.debug(f"Sorted semantic tags: {tags}")
  if tags:
    latest_tag = tags[0]
    logger.info(f"Latest semantic version tag: {latest_tag}")
  else:
    # No tags found, start with 0.0.0
    logger.info("No semantic version tags found. Starting with 0.0.0")
    latest_tag = '0.0.0'
    
  # Initialize obj
  current_version = SemanticVersion(latest_tag)
  
  ### Increment version ###
  if args.major:
    logger.debug("Incrementing major version")
    current_version.inc_major(by=args.by)
  elif args.minor:
    logger.debug("Incrementing minor version")
    current_version.inc_minor(by=args.by)
  elif args.patch:
    logger.debug("Incrementing patch version")
    current_version.inc_patch(by=args.by)
  
  ### Label ###
  if args.label:
    logger.debug(f"Adding label: {args.label}")
    current_version.add_label(args.label)
  
  new_tag = str(current_version)
  logger.debug(f"Generated new tag: {new_tag}")
    
  ### Create and push
  try:
    #TODO: add tag message option later
    #repo.create_tag(new_tag, message=f"Release {new_tag}")
    repo.create_tag(new_tag)
    logger.info(f"Successfully created tag: {new_tag}")
    
    # Push if requested
    if args.pushall:
      logger.debug("Pushing all local tags to remote...")
      repo.remote('origin').push(tags=True)
      logger.info("Successfully pushed all tags to remote")
    elif args.push:
      logger.debug(f"Pushing tag '{new_tag}' to remote...")
      repo.remote('origin').push(new_tag) # It only pushes the new tag not all from local repo
      logger.info(f"Successfully pushed new tag: {new_tag}")
    else:
      logger.debug("Not pushing tag to remote")
  except git.GitCommandError as e:
    logger.error(f"Error creating/pushing tag: {e}")
  except Exception as e:
    logger.error(f"Error: {e}")  

  # Print the new tag to stout as confirmation if not verbose
  if args.verbose == 0:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    print(f"{GREEN}{reponame}{RESET} -> {YELLOW}{new_tag}{RESET}")

if __name__ == "__main__":
  main()
